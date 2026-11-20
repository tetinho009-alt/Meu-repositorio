# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Gerador procedural de boneco 3D a partir do boneco 2D do kit, sem IA de 3D. Roda dentro do Blender (o jeito
fácil é o `boneco3d/rodar.py`, que acha o Blender e chama este arquivo):

    blender -b --factory-startup -P boneco3d/gerar.py -- <nome> [--previa] [--saida PASTA]

Lê o boneco 2D (molde `maquina/molde.py`, cores de `personagens/<nome>/personagem.json`, retângulos de
`personagens/<nome>/partes.json` e os PNGs de `personagens/<nome>/partes`) e monta: corpo em peças lisas com shading toon (Shader to RGB + rampa de 3 tons), contorno
de nanquim por casca invertida, rosto pintado com as próprias partes 2D (olho, íris, pálpebra, sobrancelha e um
atlas das bocas por visema) e um esqueleto com pesos por grupo de vértices.

Controle da animação: propriedades no objeto do esqueleto ("visema", "piscar_e", "piscar_d", "olhar_x",
"olhar_y", "sobrancelha_dy"), lidas pelo material do rosto por driver. Poses e gags: `aplicar_pose`, `animar`, `gag`.
Unidade: 1 m = 1000 px do molde 2D (pés em z = 0, frente do boneco para -Y, lado "e" do 2D em -X).
"""
import json
import math
import os
import sys
import warnings
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Quaternion, Vector

warnings.filterwarnings("ignore", category=DeprecationWarning)

AQUI = Path(__file__).resolve().parent
KIT = AQUI.parent
FUNDO = (210, 210, 212)
VISEMAS = ["R", "A", "E", "I", "O", "U", "M", "F", "feliz"]
PROPS_ROSTO = {"visema": 0.0, "piscar_e": 0.0, "piscar_d": 0.0, "olhar_x": 0.0, "olhar_y": 0.0, "sobrancelha_dy": 0.0}

# Contorno 2D do cabelo (frações do raio da cabeça, y para baixo), o mesmo de maquina/molde._cabelo_longo.
CABELO_2D = {
    "longo": dict(topo=(1.12, 1.1, 168, 372, -0.06, 0.05),
                  lado_d=[(1.06, 0.2), (1.02, 0.5), (0.9, 0.62), (0.8, 0.3), (0.82, -0.1)],
                  franja=[(0.72, -0.32), (0.4, -0.5), (0.0, -0.56), (-0.36, -0.46), (-0.62, -0.26), (-0.8, -0.04)],
                  lado_e=[(-0.84, 0.3), (-0.92, 0.62), (-1.04, 0.5), (-1.08, 0.2)],
                  linhas=[((0.32, -0.56), (0.38, -0.86), (0.3, -1.06)), ((0.6, -0.5), (0.1, -0.62), (-0.46, -0.4)),
                          ((0.9, 0.0), (0.98, 0.3), (0.9, 0.56)), ((-0.92, 0.0), (-0.98, 0.3), (-0.94, 0.56))]),
}


# ------------------------------------------------------------------------------------------------ leitura do 2D

class Boneco2D:
    """Tudo o que o 3D precisa do boneco 2D: molde, cores e retângulos das partes."""

    def __init__(self, nome):
        if str(KIT) not in sys.path:
            sys.path.insert(0, str(KIT))
        from maquina import molde as pb
        if getattr(pb, "ESTILO", "") == "capsula":
            raise SystemExit("ERRO: o 3D do personagem ainda não suporta o estilo cápsula (o molde de personagem do "
                             "kit).\nO QUE FAZER: faça a cena no rig 2D (kit/maquina), que tem todas as poses.")
        pasta = Path(os.environ.get("BONECO3D_PERSONAGENS") or KIT / "personagens") / nome
        if not (pasta / "partes.json").is_file():
            raise SystemExit(f"personagem {nome} sem partes: rode antes `python construir_boneco.py {nome}`")
        cfg = json.loads((pasta / "personagem.json").read_text(encoding="utf-8"))
        pb.montar(cfg["molde"])  # deixa pb.C com as cores e as escolhas deste personagem
        self.nome, self.pb = nome, pb
        self.C = dict(pb.C)
        dados = json.loads((pasta / "partes.json").read_text(encoding="utf-8"))
        self.partes = dados["partes"]
        self.dir_partes = pasta / "partes"
        self.pose_base = dados.get("pose_base") or cfg.get("pose_base") or {}
        self.R = pb.R / 1000
        self.ZH = (1000 - pb.CAB_Y) / 1000

    def png(self, parte):
        return self.dir_partes / f"{parte}.png"


def P(x2d, y2d, prof=0.0):
    """Ponto do molde 2D (px) em metros no Blender."""
    return Vector(((x2d - 500) / 1000, prof, (1000 - y2d) / 1000))


def lin(hexa):
    """#RRGGBB (sRGB) para RGBA linear."""
    hexa = hexa.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(hexa[i:i + 2], 16) / 255
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (*out, 1.0)


def suave(a, b, x):
    if b == a:
        return 1.0 if x >= b else 0.0
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


# ------------------------------------------------------------------------------------------------ malhas

def grade(f, nu, nv, fechar_u=False):
    """Superfície paramétrica f(u, v) com u, v em 0..1."""
    cols = nu if fechar_u else nu + 1
    verts = [f(i / nu, j / nv) for j in range(nv + 1) for i in range(cols)]
    faces = []
    for j in range(nv):
        for i in range(nu):
            i2 = (i + 1) % cols if fechar_u else i + 1
            faces.append((j * cols + i, j * cols + i2, (j + 1) * cols + i2, (j + 1) * cols + i))
    return verts, faces


def elipsoide(c, rx, ry, rz, nu=48, nv=32, z_min=None):
    c = Vector(c)

    def f(u, v):
        th, ph = 2 * math.pi * u, math.pi * v
        p = Vector((rx * math.sin(ph) * math.cos(th), ry * math.sin(ph) * math.sin(th), rz * math.cos(ph)))
        if z_min is not None:
            p.z = max(p.z, z_min)
        return c + p

    return grade(f, nu, nv, fechar_u=True)


def _base_eixo(d):
    d = d.normalized()
    ref = Vector((0, 1, 0)) if abs(d.y) < 0.9 else Vector((1, 0, 0))
    u = d.cross(ref).normalized()
    return d, u, d.cross(u).normalized()


def revolucao(p0, p1, perfil, nu=24, achatar=1.0):
    """Sólido de revolução no eixo p0 -> p1. perfil: [(t, raio)], t em metros ao longo do eixo a partir de p0,
    do polo de cima (t maior) ao de baixo. `achatar` encolhe o raio na direção da câmera (Y)."""
    p0, p1 = Vector(p0), Vector(p1)
    d, u, w = _base_eixo(p1 - p0)
    verts, faces = [], []
    for t, r in perfil:
        for i in range(nu):
            th = 2 * math.pi * i / nu
            off = u * (r * math.cos(th)) + w * (r * math.sin(th))
            off.y *= achatar
            verts.append(p0 + d * t + off)
    for j in range(len(perfil) - 1):
        for i in range(nu):
            a, b = j * nu + i, j * nu + (i + 1) % nu
            faces.append((a, b, b + nu, a + nu))
    return verts, faces


def capsula(p0, p1, r0, r1, nu=24, n_hemi=6, n_meio=8, achatar=1.0):
    L = (Vector(p1) - Vector(p0)).length
    perfil = []
    for k in range(n_hemi + 1):  # hemisfério de cima (p1)
        ph = (math.pi / 2) * k / n_hemi
        perfil.append((L + r1 * math.cos(ph), r1 * math.sin(ph)))
    for k in range(1, n_meio):
        s = k / n_meio
        perfil.append((L * (1 - s), r1 + (r0 - r1) * s))
    for k in range(n_hemi + 1):  # hemisfério de baixo (p0)
        ph = (math.pi / 2) * (1 + k / n_hemi)
        perfil.append((r0 * math.cos(ph), r0 * math.sin(ph)))
    return revolucao(p0, p1, perfil, nu, achatar)


def toro(c, R_, r, nu=40, nv=12, normal=(0, 1, 0)):
    c = Vector(c)
    rot = Vector((0, 0, 1)).rotation_difference(Vector(normal)).to_matrix()

    def f(u, v):
        a, b = 2 * math.pi * u, 2 * math.pi * v
        p = Vector(((R_ + r * math.cos(b)) * math.cos(a), (R_ + r * math.cos(b)) * math.sin(a), r * math.sin(b)))
        return c + rot @ p

    cols = nu
    verts = [f(i / nu, j / nv) for j in range(nv) for i in range(nu)]
    faces = [(j * cols + i, j * cols + (i + 1) % nu, ((j + 1) % nv) * cols + (i + 1) % nu, ((j + 1) % nv) * cols + i)
             for j in range(nv) for i in range(nu)]
    return verts, faces


def tubo(pontos, raio, nu=8, afinar="lens"):
    """Tubo por uma lista de pontos; `afinar`: lens (fino nas pontas), fim (fino no fim) ou uniforme."""
    pts = [Vector(p) for p in pontos]
    n = len(pts)
    verts, faces = [], []
    ref = Vector((0, 0, 1))
    for k, p in enumerate(pts):
        t = (pts[min(k + 1, n - 1)] - pts[max(k - 1, 0)]).normalized()
        if abs(t.dot(ref)) > 0.95:
            ref = Vector((1, 0, 0))
        u = t.cross(ref).normalized()
        w = t.cross(u).normalized()
        s = k / (n - 1)
        f = {"lens": 0.35 + 0.65 * math.sin(math.pi * s), "fim": 1.0 - 0.75 * s}.get(afinar, 1.0)
        for i in range(nu):
            th = 2 * math.pi * i / nu
            verts.append(p + (u * math.cos(th) + w * math.sin(th)) * raio * f)
    for j in range(n - 1):
        for i in range(nu):
            a, b = j * nu + i, j * nu + (i + 1) % nu
            faces.append((a, b, b + nu, a + nu))
    i0, i1 = len(verts), len(verts) + 1
    verts += [pts[0], pts[-1]]
    for i in range(nu):
        faces.append((i0, (i + 1) % nu, i))
        faces.append((i1, (n - 1) * nu + i, (n - 1) * nu + (i + 1) % nu))
    return verts, faces


def loft(aneis, topo, fundo):
    """Sólido por anéis (mesmo número de pontos), fechado por um ponto em cima e outro embaixo."""
    nu = len(aneis[0])
    verts = [Vector(p) for anel in aneis for p in anel]
    faces = []
    for j in range(len(aneis) - 1):
        for i in range(nu):
            a, b = j * nu + i, j * nu + (i + 1) % nu
            faces.append((a, b, b + nu, a + nu))
    it, ib = len(verts), len(verts) + 1
    verts += [Vector(topo), Vector(fundo)]
    last = (len(aneis) - 1) * nu
    for i in range(nu):
        faces.append((it, (i + 1) % nu, i))
        faces.append((ib, last + i, last + (i + 1) % nu))
    return verts, faces


def _bm_de(verts, faces):
    bm = bmesh.new()
    vs = [bm.verts.new(v) for v in verts]
    for f in faces:
        ids = list(dict.fromkeys(f))
        if len(ids) >= 3:
            try:
                bm.faces.new([vs[i] for i in ids])
            except ValueError:
                pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    return bm


# ------------------------------------------------------------------------------------------------ materiais

class Nos:
    """Atalhos para montar árvore de nós de material."""

    def __init__(self, mat):
        if hasattr(mat, "use_nodes"):
            mat.use_nodes = True
        self.nt = mat.node_tree
        self.nt.nodes.clear()

    def n(self, tipo, **kw):
        no = self.nt.nodes.new(tipo)
        for k, v in kw.items():
            setattr(no, k, v)
        return no

    def ligar(self, saida, entrada):
        if isinstance(saida, bpy.types.NodeSocket):
            self.nt.links.new(saida, entrada)
        else:
            entrada.default_value = saida

    def m(self, op, a, b=None, c=None):
        no = self.n("ShaderNodeMath", operation=op)
        for i, x in enumerate((a, b, c)):
            if x is not None:
                self.ligar(x, no.inputs[i])
        return no.outputs[0]

    def vm(self, op, a, b=None):
        no = self.n("ShaderNodeVectorMath", operation=op)
        for i, x in enumerate((a, b)):
            if x is not None:
                self.ligar(x, no.inputs[i])
        return no.outputs[0]

    def mix(self, fator, a, b):
        no = self.n("ShaderNodeMix", data_type="RGBA", blend_type="MIX")
        ins = {s.identifier: s for s in no.inputs}
        self.ligar(fator, ins["Factor_Float"])
        self.ligar(a, ins["A_Color"])
        self.ligar(b, ins["B_Color"])
        return {s.identifier: s for s in no.outputs}["Result_Color"]

    def xyz(self, x, y, z=0.0):
        no = self.n("ShaderNodeCombineXYZ")
        for i, v in enumerate((x, y, z)):
            self.ligar(v, no.inputs[i])
        return no.outputs[0]

    def fator_toon(self, sombra, brilho, limiar=(0.30, 0.95)):
        """Shader to RGB de um difuso branco -> rampa constante de 3 tons (sombra, luz, brilho)."""
        d = self.n("ShaderNodeBsdfDiffuse")
        d.inputs["Color"].default_value = (1, 1, 1, 1)
        rgb = self.n("ShaderNodeShaderToRGB")
        self.ligar(d.outputs[0], rgb.inputs[0])
        bw = self.n("ShaderNodeRGBToBW")
        self.ligar(rgb.outputs["Color"], bw.inputs[0])
        cr = self.n("ShaderNodeValToRGB")
        cr.color_ramp.interpolation = "CONSTANT"
        topo = max(1.0, brilho)
        e = cr.color_ramp.elements
        e[0].position, e[0].color = 0.0, (sombra / topo,) * 3 + (1,)
        e[1].position, e[1].color = limiar[0], (1 / topo,) * 3 + (1,)
        e.new(limiar[1]).color = (brilho / topo,) * 3 + (1,)
        self.ligar(bw.outputs[0], cr.inputs[0])
        return self._escala(cr.outputs["Color"], topo)

    def _escala(self, cor, k):
        no = self.n("ShaderNodeVectorMath", operation="SCALE")
        self.ligar(cor, no.inputs[0])
        no.inputs["Scale"].default_value = k
        return no.outputs[0]

    def emitir(self, cor):
        em = self.n("ShaderNodeEmission")
        self.ligar(cor, em.inputs["Color"])
        out = self.n("ShaderNodeOutputMaterial")
        self.ligar(em.outputs[0], out.inputs["Surface"])


TOM = {  # sombra, brilho, limiares da rampa
    "pele": (0.86, 1.04, (0.16, 0.97)),
    "cabelo": (0.64, 1.45, (0.26, 0.985)),
    "roupa": (0.68, 1.10, (0.30, 0.95)),
    "calca": (0.70, 1.12, (0.30, 0.95)),
    "sapato": (0.82, 1.0, (0.25, 0.99)),
    "chapado": (1.0, 1.0, (0.0, 0.99)),
}


def mat_toon(nome, cor, tom="roupa"):
    mat = bpy.data.materials.new(nome)
    s = Nos(mat)
    sombra, brilho, limiar = TOM[tom]
    fator = s.fator_toon(sombra, brilho, limiar)
    s.emitir(s.vm("MULTIPLY", lin(cor)[:3], fator))
    return mat


def mat_chapado(nome, cor):
    mat = bpy.data.materials.new(nome)
    s = Nos(mat)
    s.emitir(lin(cor))
    return mat


def mat_contorno(cor):
    mat = bpy.data.materials.new("contorno")
    s = Nos(mat)
    s.emitir(lin(cor))
    mat.use_backface_culling = True
    if hasattr(mat, "use_backface_culling_shadow"):
        mat.use_backface_culling_shadow = True
    return mat


def atlas_bocas(b2d, destino):
    """Junta as bocas de todos os visemas numa tira (uma célula por visema, no retângulo que contém todas)."""
    import numpy as np
    rects = [b2d.partes[f"boca_{v}"] for v in VISEMAS]
    x0 = min(r["x"] for r in rects)
    y0 = min(r["y"] for r in rects)
    x1 = max(r["x"] + r["w"] for r in rects)
    y1 = max(r["y"] + r["h"] for r in rects)
    esc = 2.0
    cw, ch = int(math.ceil((x1 - x0) * esc)), int(math.ceil((y1 - y0) * esc))
    tira = np.zeros((ch, cw * len(VISEMAS), 4), np.float32)
    for k, v in enumerate(VISEMAS):
        r = b2d.partes[f"boca_{v}"]
        im = bpy.data.images.load(str(b2d.png(f"boca_{v}")))
        w, h = im.size
        px = np.array(im.pixels[:], np.float32).reshape(h, w, 4)[::-1]  # linha 0 = topo
        ox, oy = int(round((r["x"] - x0) * esc)), int(round((r["y"] - y0) * esc))
        tira[oy:oy + h, k * cw + ox:k * cw + ox + w] = px[:ch - oy, :cw - ox]
        bpy.data.images.remove(im)
    img = bpy.data.images.new(f"{b2d.nome}_bocas", cw * len(VISEMAS), ch, alpha=True)
    img.pixels.foreach_set(tira[::-1].ravel())
    destino.parent.mkdir(parents=True, exist_ok=True)
    img.filepath_raw = str(destino)
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)
    return (x0, y0, x1 - x0, y1 - y0)


def mat_rosto(b2d, rig, atlas_png, atlas_rect):
    """Pele toon com nariz e blush do molde; por cima, as partes 2D do rosto projetadas de frente (UV 'frontal')."""
    C, pb = b2d.C, b2d.pb
    mat = bpy.data.materials.new("rosto")
    s = Nos(mat)
    uv = s.n("ShaderNodeUVMap", uv_map="frontal")
    sep = s.n("ShaderNodeSeparateXYZ")
    s.ligar(uv.outputs[0], sep.inputs[0])
    px = s.m("MULTIPLY", sep.outputs[0], 1000.0)
    py = s.m("MULTIPLY", s.m("SUBTRACT", 1.0, sep.outputs[1]), 1000.0)
    frente = s.n("ShaderNodeAttribute", attribute_type="GEOMETRY", attribute_name="frente").outputs["Fac"]

    # valores animáveis, ligados por driver às propriedades do esqueleto
    val = {}
    for k in PROPS_ROSTO:
        no = s.n("ShaderNodeValue", label=k, name=k)
        fc = no.outputs[0].driver_add("default_value")
        fc.driver.type = "SUM"
        var = fc.driver.variables.new()
        var.targets[0].id = rig
        var.targets[0].data_path = f'["{k}"]'
        val[k] = no.outputs[0]

    def elipse(cx, cy, rx, ry, borda=0.15):
        dx = s.m("DIVIDE", s.m("SUBTRACT", px, cx), rx)
        dy = s.m("DIVIDE", s.m("SUBTRACT", py, cy), ry)
        d = s.m("ADD", s.m("MULTIPLY", dx, dx), s.m("MULTIPLY", dy, dy))
        mr = s.n("ShaderNodeMapRange", interpolation_type="SMOOTHSTEP")
        s.ligar(d, mr.inputs["Value"])
        mr.inputs["From Min"].default_value = 1 - borda
        mr.inputs["From Max"].default_value = 1.0
        mr.inputs["To Min"].default_value = 1.0
        mr.inputs["To Max"].default_value = 0.0
        return mr.outputs["Result"]

    CX, CY, R = pb.CX, pb.CAB_Y, pb.R
    cor = lin(C["pele"])
    for lado in (-1, 1):  # blush
        cor = s.mix(s.m("MULTIPLY", elipse(CX + lado * R * 0.62, CY + 100, 42, 16, 0.5), 0.35), cor, lin("#F08A96"))
    cor = s.mix(elipse(CX, CY + 96, 20, 15, 0.2), cor, lin(C["pele_sombra"]))
    cor = s.mix(elipse(CX - 6, CY + 90, 6, 4, 0.3), cor, lin("#F6D6BC"))
    sombra, brilho, limiar = TOM["pele"]
    cor = s.vm("MULTIPLY", cor, s.fator_toon(sombra, brilho, limiar))

    def decal(parte, dx=None, dy=None, k=None, mascara=None, imagem=None, rect=None):
        nonlocal cor
        r = rect or b2d.partes[parte]
        x = s.m("SUBTRACT", px, r["x"]) if dx is None else s.m("SUBTRACT", s.m("SUBTRACT", px, r["x"]), dx)
        y = s.m("SUBTRACT", py, r["y"]) if dy is None else s.m("SUBTRACT", s.m("SUBTRACT", py, r["y"]), dy)
        if k is not None:  # pálpebra: desce a partir do topo do olho (igual ao rig 2D)
            topo = 20.0
            y = s.m("ADD", s.m("DIVIDE", s.m("SUBTRACT", y, topo), s.m("MAXIMUM", k, 0.05)), topo)
        u = s.m("DIVIDE", x, r["w"])
        v = s.m("SUBTRACT", 1.0, s.m("DIVIDE", y, r["h"]))
        tex = s.n("ShaderNodeTexImage", extension="CLIP", interpolation="Linear")
        tex.image = imagem or bpy.data.images.load(str(b2d.png(parte)), check_existing=True)
        s.ligar(s.xyz(u, v), tex.inputs["Vector"])
        alfa = s.m("MULTIPLY", tex.outputs["Alpha"], frente)
        if mascara is not None:
            alfa = s.m("MULTIPLY", alfa, mascara)
        cor = s.mix(alfa, cor, tex.outputs["Color"])
        return tex

    olhar_dx = s.m("MULTIPLY", val["olhar_x"], 13.0)
    olhar_dy = s.m("MULTIPLY", val["olhar_y"], 10.0)
    for lado in ("e", "d"):
        decal(f"olho_{lado}")
        decal(f"iris_{lado}", dx=olhar_dx, dy=olhar_dy)
        pis = val[f"piscar_{lado}"]
        decal(f"palpebra_{lado}", k=pis, mascara=s.m("GREATER_THAN", pis, 0.05))
        decal(f"sobrancelha_{lado}", dy=val["sobrancelha_dy"])

    # boca: célula do atlas escolhida pelo visema
    bx, by, bw, bh = atlas_rect
    su = s.m("DIVIDE", s.m("SUBTRACT", px, bx), bw)
    sv = s.m("DIVIDE", s.m("SUBTRACT", py, by), bh)
    dentro = s.m("MULTIPLY", s.m("MULTIPLY", s.m("GREATER_THAN", su, 0.0), s.m("LESS_THAN", su, 1.0)),
                 s.m("MULTIPLY", s.m("GREATER_THAN", sv, 0.0), s.m("LESS_THAN", sv, 1.0)))
    idx = s.m("ROUND", val["visema"])
    u = s.m("DIVIDE", s.m("ADD", idx, su), float(len(VISEMAS)))
    tex = s.n("ShaderNodeTexImage", extension="CLIP", interpolation="Linear")
    tex.image = bpy.data.images.load(str(atlas_png), check_existing=True)
    s.ligar(s.xyz(u, s.m("SUBTRACT", 1.0, sv)), tex.inputs["Vector"])
    cor = s.mix(s.m("MULTIPLY", s.m("MULTIPLY", tex.outputs["Alpha"], frente), dentro), cor, tex.outputs["Color"])
    s.emitir(cor)
    return mat


# ------------------------------------------------------------------------------------------------ construção

class Montador:
    def __init__(self, b2d, colecao):
        self.b = b2d
        self.col = colecao
        self.rig = None
        self.contorno = mat_contorno(b2d.pb.TINTA)
        self.mats = {}

    def mat(self, chave, cor, tom):
        if chave not in self.mats:
            self.mats[chave] = mat_toon(chave, cor, tom)
        return self.mats[chave]

    def objeto(self, nome, geo, mat, pesos, contorno=0.0055, volume=None, fechado=True, orientar=None, uv_frontal=False,
               frente=None):
        """Cria a malha com material, casca de contorno e pesos. `pesos`: nome do osso ou função(co) -> {osso: peso}."""
        bm = geo if isinstance(geo, bmesh.types.BMesh) else _bm_de(*geo)
        if fechado:
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        elif orientar is not None:  # superfície aberta: normal para fora segundo a função
            bm.faces.ensure_lookup_table()
            soma = sum((f.normal.dot(orientar(f.calc_center_median())) for f in bm.faces), 0.0)
            if soma < 0:
                bmesh.ops.reverse_faces(bm, faces=bm.faces)
        me = bpy.data.meshes.new(nome)
        bm.to_mesh(me)
        bm.free()
        for p in me.polygons:
            p.use_smooth = True
        me.materials.append(mat)
        me.materials.append(self.contorno)
        if uv_frontal:
            uvl = me.uv_layers.new(name="frontal")
            for lp in me.loops:
                co = me.vertices[lp.vertex_index].co
                uvl.data[lp.index].uv = (co.x + 0.5, co.z)
        if frente is not None:
            at = me.attributes.new("frente", "FLOAT", "POINT")
            for v in me.vertices:
                at.data[v.index].value = frente(v.co)
        ob = bpy.data.objects.new(nome, me)
        self.col.objects.link(ob)
        ob.parent = self.rig
        if callable(pesos):
            grupos = {}
            for v in me.vertices:
                for osso, w in pesos(v.co).items():
                    if w > 1e-4:
                        g = grupos.get(osso) or ob.vertex_groups.new(name=osso)
                        grupos[osso] = g
                        g.add([v.index], w, "REPLACE")
        else:
            ob.vertex_groups.new(name=pesos).add(list(range(len(me.vertices))), 1.0, "REPLACE")
        arm = ob.modifiers.new("esqueleto", "ARMATURE")
        arm.object = self.rig
        if volume:
            sv = ob.modifiers.new("volume", "SOLIDIFY")
            sv.thickness, sv.offset = volume, -1.0
            sv.use_quality_normals = True
        if contorno:
            sc = ob.modifiers.new("contorno", "SOLIDIFY")
            sc.thickness, sc.offset = contorno * ESCALA_CONTORNO, 1.0
            sc.use_flip_normals, sc.use_rim, sc.material_offset = True, False, 1
            sc.use_quality_normals = True
        return ob


OSSOS = [  # nome, cabeça, cauda, pai (metros; "e" = esquerda da tela = -X)
    ("raiz", (0, 0, 0), (0, 0, 0.10), None),
    ("quadril", (0, 0, 0.233), (0, 0, 0.30), "raiz"),
    ("coluna", (0, 0, 0.30), (0, 0, 0.50), "quadril"),
    ("pescoco", (0, 0, 0.50), (0, 0, 0.546), "coluna"),
    ("cabeca", (0, 0, 0.546), (0, 0, 0.95), "pescoco"),
]
for _l, _s in (("e", -1), ("d", 1)):
    OSSOS += [
        (f"ombro_{_l}", (_s * 0.03, 0, 0.50), (_s * 0.118, 0, 0.52), "coluna"),
        (f"braco_{_l}", (_s * 0.118, 0, 0.52), (_s * 0.182, 0, 0.372), f"ombro_{_l}"),
        (f"antebraco_{_l}", (_s * 0.182, 0, 0.372), (_s * 0.186, 0, 0.248), f"braco_{_l}"),
        (f"mao_{_l}", (_s * 0.186, 0, 0.248), (_s * 0.188, 0, 0.18), f"antebraco_{_l}"),
        (f"coxa_{_l}", (_s * 0.068, 0, 0.245), (_s * 0.068, 0, 0.15), "quadril"),
        (f"canela_{_l}", (_s * 0.068, 0, 0.15), (_s * 0.068, 0, 0.05), f"coxa_{_l}"),
        (f"pe_{_l}", (_s * 0.068, 0, 0.05), (_s * 0.075, -0.10, 0.03), f"canela_{_l}"),
    ]


def criar_esqueleto(nome, col):
    arm = bpy.data.armatures.new(f"{nome}_esqueleto")
    rig = bpy.data.objects.new(f"{nome}_rig", arm)
    col.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    eb = {}
    for n, h, t, pai in OSSOS:
        b = arm.edit_bones.new(n)
        b.head, b.tail = h, t
        b.use_deform = n != "raiz"
        if pai:
            b.parent = eb[pai]
        eb[n] = b
    bpy.ops.object.mode_set(mode="OBJECT")
    for pbn in rig.pose.bones:
        pbn.rotation_mode = "QUATERNION"
    for k, v in PROPS_ROSTO.items():
        rig[k] = v
    arm.display_type = "STICK"
    return rig


def _perfil(tabela, x):
    """Interpolação suave (cosseno) numa tabela [(x, a, b, ...)]."""
    if x <= tabela[0][0]:
        return tabela[0][1:]
    for p, q in zip(tabela[:-1], tabela[1:]):
        if x <= q[0]:
            t = (x - p[0]) / (q[0] - p[0])
            t = (1 - math.cos(math.pi * t)) / 2
            return tuple(a + (b - a) * t for a, b in zip(p[1:], q[1:]))
    return tabela[-1][1:]


SUPER = 2.6
ESCALA_CONTORNO = 1.9  # casca de contorno: espessura relativa ao traço do 2D
TRONCO = [  # y2d, meia-largura, meia-profundidade (px)
    (446, 74, 60), (454, 104, 80), (472, 124, 94), (520, 137, 104), (600, 142, 108), (690, 144, 108),
    (760, 140, 104), (792, 133, 98), (808, 118, 88), (816, 92, 68)]


def _superelipse(W, D, th, n=SUPER):
    c, s = math.cos(th), math.sin(th)
    return (W * math.copysign(abs(c) ** (2 / n), c), D * math.copysign(abs(s) ** (2 / n), s))


def frente_tronco(x, z):
    """Profundidade (y, metros) da frente do moletom no ponto (x, z)."""
    W, D = _perfil(TRONCO, 1000 - z * 1000)
    W, D = W / 1000, D / 1000
    f = max(0.0, 1 - abs(x / W) ** SUPER)
    return -D * f ** (1 / SUPER)


def _amostrar_suave(pts, n=8):
    out, cur = [pts[0]], pts[0]
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        e = ((x0 + x1) / 2, (y0 + y1) / 2)
        for k in range(1, n + 1):
            t = k / n
            out.append(((1 - t) ** 2 * cur[0] + 2 * (1 - t) * t * x0 + t * t * e[0],
                        (1 - t) ** 2 * cur[1] + 2 * (1 - t) * t * y0 + t * t * e[1]))
        cur = e
    out.append(pts[-1])
    return out


def _quad(a, c, b, n=16):
    return [((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * c[0] + t * t * b[0],
             (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * c[1] + t * t * b[1]) for t in (k / n for k in range(n + 1))]


def _dentro(poly, x, y):
    ok = False
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            ok = not ok
    return ok


def _mais_proximo(poly, x, y):
    melhor, bd = None, 1e9
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        dx, dy = x1 - x0, y1 - y0
        t = max(0.0, min(1.0, ((x - x0) * dx + (y - y0) * dy) / (dx * dx + dy * dy + 1e-12)))
        qx, qy = x0 + t * dx, y0 + t * dy
        d = (qx - x) ** 2 + (qy - y) ** 2
        if d < bd:
            melhor, bd = (qx, qy), d
    return melhor, math.sqrt(bd)


def pasta_saida(nome, saida=None):
    """Onde o 3D grava (blend, texturas, quadros): fora de personagens/, em <kit>/trabalho/boneco3d/<nome>."""
    return Path(saida) if saida else KIT / "trabalho" / "boneco3d" / nome


def construir(nome="nico", saida=None):
    """Monta o boneco na cena atual. Devolve o objeto do esqueleto."""
    b2d = Boneco2D(nome)
    C, pb = b2d.C, b2d.pb
    if C.get("cabelo_estilo") not in CABELO_2D:
        raise SystemExit(f"cabelo '{C.get('cabelo_estilo')}' ainda não tem versão 3D (só: {list(CABELO_2D)}); "
                         "esse personagem fica no 2D")
    if C.get("roupa_tipo", "moletom") != "moletom":
        raise SystemExit(f"roupa '{C.get('roupa_tipo')}' ainda não tem versão 3D (só: moletom); esse personagem fica no 2D")
    col = bpy.data.collections.new(nome)
    bpy.context.scene.collection.children.link(col)
    rig = criar_esqueleto(nome, col)
    mt = Montador(b2d, col)
    mt.rig = rig
    R, ZH = b2d.R, b2d.ZH
    tinta_cabelo = "#140A07"

    # ---- cabeça (rosto projetado de frente)
    atlas_png = pasta_saida(nome, saida) / "texturas" / "bocas.png"
    atlas_rect = atlas_bocas(b2d, atlas_png)
    HX, HY, HZ = R, 0.925 * R, 0.96 * R
    cab = elipsoide((0, 0, ZH), HX, HY, HZ, 96, 64)
    mt.objeto("cabeca", cab, mat_rosto(b2d, rig, atlas_png, atlas_rect), "cabeca", contorno=0.006, uv_frontal=True,
              frente=lambda co: suave(0.15, 0.45, -co.y / HY))
    mt.objeto("pescoco", capsula((0, 0, 0.50), (0, 0, 0.62), 0.05, 0.05), mt.mat("pele", C["pele"], "pele"),
              "pescoco", contorno=0.004)

    # ---- tronco (moletom)
    aneis = []
    for y2d, W, D in TRONCO:
        aneis.append([P(500 + w, y2d, d / 1000) for w, d in (_superelipse(W, D, 2 * math.pi * i / 64) for i in range(64))])
    tronco = loft(aneis, P(500, 440), P(500, 818))

    def pesos_tronco(co):
        w = suave(0.27, 0.40, co.z)
        return {"quadril": 1 - w, "coluna": w}

    roupa = mt.mat("roupa", C["roupa"], "roupa")
    roupa_esc = mt.mat("roupa_esc", C["roupa_esc"], "roupa")
    mt.objeto("tronco", tronco, roupa, pesos_tronco)

    gola = toro((0, 0.004, 0.551), 0.068, 0.015, normal=(0, 0, 1))
    mt.objeto("gola", gola, roupa_esc, "coluna", contorno=0.004)

    # bolso canguru: retângulo arredondado colado na frente do moletom
    def bolso_pt(px_, pz_, recuo):
        x, z = (px_ - 500) / 1000, (1000 - pz_) / 1000
        return Vector((x, frente_tronco(x, z) - recuo, z))

    borda = []
    bx0, by0, bw, bh, br = 412, 640, 176, 92, 26
    for cx_, cy_, a0 in ((bx0 + bw - br, by0 + br, -90), (bx0 + bw - br, by0 + bh - br, 0), (bx0 + br, by0 + bh - br, 90),
                         (bx0 + br, by0 + br, 180)):
        for k in range(9):
            a = math.radians(a0 + 90 * k / 8)
            borda.append((cx_ + br * math.cos(a), cy_ + br * math.sin(a)))
    aneis_b = []
    for s_ in (1.0, 0.75, 0.5, 0.25):
        aneis_b.append([bolso_pt(500 + (x - 500) * s_, 686 + (y - 686) * s_, 0.0035) for x, y in borda])
    verts = [v for a in aneis_b for v in a]
    nb = len(borda)
    faces = [(j * nb + i, j * nb + (i + 1) % nb, (j + 1) * nb + (i + 1) % nb, (j + 1) * nb + i)
             for j in range(len(aneis_b) - 1) for i in range(nb)]
    verts.append(bolso_pt(500, 686, 0.0035))
    c_ = len(verts) - 1
    faces += [((len(aneis_b) - 1) * nb + i, (len(aneis_b) - 1) * nb + (i + 1) % nb, c_) for i in range(nb)]
    mt.objeto("bolso", (verts, faces), roupa_esc, pesos_tronco, contorno=0.0035, volume=0.006, fechado=False,
              orientar=lambda c: Vector((0, -1, 0)))

    # cordões do capuz
    branco = mt.mat("cordao", "#F2EEFA", "sapato")
    y_ini, y_fim = pb.OMBRO_Y + 26, 568
    for lado in (-1, 1):
        pts = []
        for k in range(12):
            t = k / 11
            x = (lado * 30 + lado * 5 * t) / 1000
            z = (1000 - (y_ini + (y_fim - y_ini) * t)) / 1000
            pts.append(Vector((x, frente_tronco(x, z) - 0.006, z)))
        mt.objeto(f"cordao_{'e' if lado < 0 else 'd'}", tubo(pts, 0.0042, afinar="uniforme"), branco, "coluna",
                  contorno=0.0022)
        fim = pts[-1] + Vector((0, 0, -0.008))
        mt.objeto(f"ponteira_{'e' if lado < 0 else 'd'}", elipsoide(fim, 0.0065, 0.0055, 0.0095, 16, 10), branco,
                  "coluna", contorno=0.0025)

    # ---- braços
    for lado, s in (("e", -1), ("d", 1)):
        o, cot, pun = Vector((s * 0.118, 0, 0.52)), Vector((s * 0.182, 0, 0.372)), Vector((s * 0.186, 0, 0.248))

        def pesos_braco(co, o=o, cot=cot, lado=lado):
            eixo = cot - o
            t = (co - o).dot(eixo) / eixo.length_squared
            w = suave(0.82, 1.05, t)
            return {f"braco_{lado}": 1 - w, f"antebraco_{lado}": w}

        mt.objeto(f"braco_{lado}", capsula(o, cot, 0.036, 0.035), roupa, pesos_braco)
        mt.objeto(f"antebraco_{lado}", capsula(cot, pun, 0.035, 0.032), roupa,
                  lambda co, cot=cot, lado=lado: {f"antebraco_{lado}": 1 - 0.5 * suave(0.03, 0.0, cot.z - co.z),
                                                  f"braco_{lado}": 0.5 * suave(0.03, 0.0, cot.z - co.z)})
        punho = revolucao(pun + Vector((0, 0, 0.012)), pun + Vector((0, 0, -0.016)),
                          [(0.028, 0), (0.028, 0.03), (0.025, 0.037), (0.003, 0.037), (0.0, 0.03), (0.0, 0)])
        mt.objeto(f"punho_{lado}", punho, roupa_esc, f"antebraco_{lado}", contorno=0.004)
        pele = mt.mat("pele", C["pele"], "pele")
        mao_c = pun + Vector((s * 0.002, 0, -0.036))
        mt.objeto(f"mao_{lado}", elipsoide(mao_c, 0.034, 0.03, 0.033, 32, 20), pele, f"mao_{lado}", contorno=0.0045)
        mt.objeto(f"polegar_{lado}", elipsoide(mao_c + Vector((-s * 0.026, -0.016, 0.012)), 0.012, 0.012, 0.018, 16, 10),
                  pele, f"mao_{lado}", contorno=0.0035)

    # ---- quadril, pernas, tênis
    calca = mt.mat("calca", C["calca"], "calca")
    calca_esc = mt.mat("calca_esc", C["calca_esc"], "calca")
    mt.objeto("quadril", elipsoide((0, 0, 0.245), 0.132, 0.092, 0.06), calca, "quadril", contorno=0.004)
    sapato = mt.mat("sapato", C["sapato"], "sapato")
    sola = mt.mat("sola", C["sola"], "sapato")
    cadarco = mt.mat("cadarco", "#8A8AA0", "chapado")
    for lado, s in (("e", -1), ("d", 1)):
        hx = s * 0.068

        def pesos_perna(co, lado=lado):
            w = suave(0.17, 0.13, co.z)
            return {f"coxa_{lado}": 1 - w, f"canela_{lado}": w}

        mt.objeto(f"perna_{lado}", capsula((hx, 0, 0.05), (hx, 0, 0.27), 0.040, 0.041), calca, pesos_perna)
        barra = revolucao((hx, 0, 0.034), (hx, 0, 0.07), [(0.036, 0), (0.036, 0.040), (0.033, 0.045), (0.003, 0.045),
                                                           (0.0, 0.040), (0.0, 0)])
        mt.objeto(f"barra_{lado}", barra, calca_esc, f"canela_{lado}", contorno=0.004)

        px_, giro = s * 0.084, math.radians(s * 7)
        rot = Matrix.Rotation(giro, 3, "Z")
        cen = Vector((px_, -0.032, 0))

        def no_pe(v, cen=cen, rot=rot):
            return cen + rot @ (Vector(v) - Vector((0, -0.032, 0)) - Vector((0, 0, 0)))

        aneis_s = []
        for z, k in ((0.0, 0.86), (0.004, 0.97), (0.030, 1.0), (0.040, 0.9)):
            aneis_s.append([no_pe(Vector((0.066 * k * a, -0.034 + 0.118 * k * b, z)))
                            for a, b in (_superelipse(1, 1, 2 * math.pi * i / 48, 3.0) for i in range(48))])
        mt.objeto(f"sola_{lado}", loft(aneis_s, no_pe((0, -0.032, 0.042)), no_pe((0, -0.032, 0))), sola,
                  f"pe_{lado}", contorno=0.004)
        CC, RX, RY, RZ = Vector((0, -0.036, 0.030)), 0.064, 0.114, 0.094
        cab_ = elipsoide(CC, RX, RY, RZ, 48, 32, z_min=0.030)
        cab_ = ([no_pe(v) for v in cab_[0]], cab_[1])
        mt.objeto(f"tenis_{lado}", cab_, sapato, f"pe_{lado}", contorno=0.005)

        def no_cabedal(x, z, recuo=0.0015):
            f = max(0.0, 1 - (x / RX) ** 2 - ((z - CC.z) / RZ) ** 2)
            return no_pe(Vector((x, CC.y - RY * math.sqrt(f) - recuo, z)))

        for k, z2d in enumerate((898, 912, 926)):
            z = (1000 - z2d) / 1000
            pts = [no_cabedal(x / 1000, z) for x in range(-24, 25, 6)]
            mt.objeto(f"cadarco_{lado}{k}", tubo(pts, 0.0028, afinar="uniforme"), cadarco, f"pe_{lado}", contorno=0)

    # ---- cabelo
    cfg = CABELO_2D[C["cabelo_estilo"]]
    mat_cab = mt.mat("cabelo", C["cabelo"], "cabelo")
    mat_linha = mat_chapado("linha_cabelo", tinta_cabelo)
    rx_t, ry_t, rz_t = 1.12 * R, 0.98 * R, 1.10 * R
    cz_t, cy_t = ZH + 0.06 * R, 0.004

    def touca_y(x, z, recuo=0.0):
        f = max(0.0, 1 - (x / rx_t) ** 2 - ((z - cz_t) / rz_t) ** 2)
        return cy_t - (ry_t + recuo) * math.sqrt(f)

    rx2, ry2, a0, a1, cy2, amp = cfg["topo"]
    topo = []
    for k in range(25):
        ang = a0 + (a1 - a0) * k / 24
        f = 1.0 + amp * abs(math.sin(math.radians(ang) * 6.5))
        topo.append((math.cos(math.radians(ang)) * rx2 * f, cy2 + math.sin(math.radians(ang)) * ry2 * f))
    poly = _amostrar_suave(topo + cfg["lado_d"] + cfg["franja"] + cfg["lado_e"] + [topo[0]])

    bm = _bm_de(*elipsoide((0, cy_t, cz_t), rx_t, ry_t, rz_t, 160, 112))
    apagar = []
    for v in bm.verts:
        fx, fy = v.co.x / R, (ZH - v.co.z) / R
        if fy > 0.85 or (v.co.y < 0.01 and not _dentro(poly, fx, fy)):
            apagar.append(v)
    bmesh.ops.delete(bm, geom=apagar, context="VERTS")
    for v in bm.verts:  # borda da franja exatamente na curva do 2D
        if v.is_boundary and v.co.y < 0.01:
            fx, fy = v.co.x / R, (ZH - v.co.z) / R
            (qx, qy), d = _mais_proximo(poly, fx, fy)
            if d < 0.12:
                x, z = qx * R, ZH - qy * R
                v.co = Vector((x, touca_y(x, z), z))
    mt.objeto("cabelo_touca", bm, mat_cab, "cabeca", contorno=0.006, volume=0.02, fechado=False,
              orientar=lambda c: c - Vector((0, cy_t, cz_t)))

    for k, (a, c, b) in enumerate(cfg["linhas"]):
        pts = []
        for fx, fy in _quad(a, c, b, 20):
            x, z = fx * R, ZH - fy * R
            pts.append(Vector((x, touca_y(x, z, 0.0022), z)))
        mt.objeto(f"mecha_{k}", tubo(pts, 0.0026), mat_linha, "cabeca", contorno=0)

    # cortina de trás: cai das costas da cabeça até o peito e abre nas laterais
    PERFIL = [  # fy, Rx, Ry, Yc (frações de R); começa por dentro da touca e sai dela na nuca
        (-0.40, 0.95, 0.84, 0.02), (0.00, 1.09, 1.02, 0.02), (0.26, 1.10, 1.04, 0.02), (0.62, 1.29, 0.88, 0.05),
        (0.90, 1.25, 0.70, 0.07), (1.18, 1.30, 0.64, 0.08), (1.42, 1.18, 0.62, 0.09), (1.58, 1.04, 0.60, 0.09)]
    A_MAX = math.radians(100)

    def cortina(u, v, extra=0.0):
        a = -A_MAX + 2 * A_MAX * u
        fy_b = 1.50 + 0.07 * math.cos(5 * a) - 0.04 * (abs(a) / A_MAX) ** 2
        fy = -0.40 + (fy_b + 0.40) * v
        rx, ry, yc = _perfil(PERFIL, fy)
        m = 1.0 + 0.022 * math.cos(9 * a) + 0.06 * suave(0.82, 1.0, v) ** 2 + extra / (R * ry)
        return Vector((R * rx * m * math.sin(a), R * (yc + ry * m * math.cos(a)), ZH - R * fy))

    def pesos_cortina(co):
        fy = (ZH - co.z) / R
        w = 1.0 - 0.6 * suave(0.85, 1.35, fy)
        return {"cabeca": w, "coluna": 1 - w}

    mt.objeto("cabelo_cortina", grade(cortina, 96, 48), mat_cab, pesos_cortina, contorno=0.006, volume=0.022,
              fechado=False, orientar=lambda c: Vector((c.x, c.y - 0.02 * R, 0)))
    # fios: descem do cocuruto pela touca e seguem pela cortina (escondem a emenda das duas peças)
    for k, a_ in enumerate((-0.62, -0.38, -0.12, 0.14, 0.4, 0.64)):
        pts = []
        for j in range(14):
            fy = -1.0 + 0.86 * j / 13
            z = ZH - fy * R
            f = math.sqrt(max(0.0, 1 - ((z - cz_t) / rz_t) ** 2))
            a = A_MAX * a_ * (0.35 + 0.65 * j / 13)
            pts.append(Vector(((rx_t + 0.0022) * f * math.sin(a), cy_t + (ry_t + 0.0022) * f * math.cos(a), z)))
        mt.objeto(f"fio_touca_{k}", tubo(pts, 0.0019, afinar="fim"), mat_linha, "cabeca", contorno=0)
        pts = []
        for j in range(26):
            v = 0.16 + 0.72 * j / 25
            pts.append(cortina(0.5 + 0.5 * (a_ + 0.05 * math.sin(3 * math.pi * v)), v, extra=0.0022))
        mt.objeto(f"fio_{k}", tubo(pts, 0.0022), mat_linha, pesos_cortina, contorno=0)

    # argolas
    ouro = mt.mat("ouro", "#E8B840", "sapato")
    for lado, s in (("e", -1), ("d", 1)):
        mt.objeto(f"argola_{lado}", toro((s * 0.214, -0.04, 0.594), 0.017, 0.0034, 32, 10), ouro, "cabeca", contorno=0.002)

    # sombra no chão
    sombra_chao(col)
    rig["boneco3d"] = nome
    return rig


def sombra_chao(col):
    verts, faces = [], []
    n, aneis = 48, 8
    for j in range(aneis + 1):
        r = j / aneis
        for i in range(n):
            a = 2 * math.pi * i / n
            verts.append(Vector((0.23 * r * math.cos(a), 0.14 * r * math.sin(a) - 0.01, 0.0015)))
    faces = [(j * n + i, j * n + (i + 1) % n, (j + 1) * n + (i + 1) % n, (j + 1) * n + i)
             for j in range(aneis) for i in range(n)]
    me = bpy.data.meshes.new("sombra")
    me.from_pydata([tuple(v) for v in verts], [], faces)
    at = me.attributes.new("alfa", "FLOAT", "POINT")
    for i in range(len(verts)):
        r = (i // n) / aneis
        at.data[i].value = 0.32 * (1 - suave(0.35, 1.0, r))
    mat = bpy.data.materials.new("sombra_chao")
    s = Nos(mat)
    alfa = s.n("ShaderNodeAttribute", attribute_type="GEOMETRY", attribute_name="alfa").outputs["Fac"]
    tr = s.n("ShaderNodeBsdfTransparent")
    em = s.n("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0, 0, 0, 1)
    mx = s.n("ShaderNodeMixShader")
    s.ligar(alfa, mx.inputs[0])
    s.ligar(tr.outputs[0], mx.inputs[1])
    s.ligar(em.outputs[0], mx.inputs[2])
    out = s.n("ShaderNodeOutputMaterial")
    s.ligar(mx.outputs[0], out.inputs["Surface"])
    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = "BLENDED"
    me.materials.append(mat)
    ob = bpy.data.objects.new("sombra_chao", me)
    col.objects.link(ob)
    return ob


# ------------------------------------------------------------------------------------------------ cena e render

def cena(alvo_z=0.53, meia_altura=0.62, lente=85, largura=1080, altura=1920, rapido=False):
    """Câmera de frente, luz toon presa à câmera (de cima, à esquerda), fundo neutro do 2D só para a câmera."""
    sc = bpy.context.scene
    cam_d = bpy.data.cameras.new("camera")
    cam_d.lens, cam_d.sensor_fit, cam_d.sensor_height = lente, "VERTICAL", 36
    cam = bpy.data.objects.new("camera", cam_d)
    sc.collection.objects.link(cam)
    dist = meia_altura / math.tan(math.atan(18 / lente))
    cam.location = (0, -dist, alvo_z)
    cam.rotation_euler = (math.radians(90), 0, 0)
    sc.camera = cam

    sol = bpy.data.lights.new("luz_toon", "SUN")
    sol.energy = math.pi  # Shader to RGB de um difuso branco vale 1.0 de frente para a luz
    sol.use_shadow = False
    sol_o = bpy.data.objects.new("luz_toon", sol)
    sc.collection.objects.link(sol_o)
    sol_o.parent = cam
    d = Vector((0.55, -0.6, -1.0)).normalized()  # direção da luz no espaço da câmera
    sol_o.rotation_mode = "QUATERNION"
    sol_o.rotation_quaternion = d.to_track_quat("-Z", "Y")

    mundo = bpy.data.worlds.new("mundo")
    sc.world = mundo
    if hasattr(mundo, "use_nodes"):
        mundo.use_nodes = True
    wn = mundo.node_tree
    wn.nodes.clear()
    lp = wn.nodes.new("ShaderNodeLightPath")
    fundo = wn.nodes.new("ShaderNodeBackground")
    fundo.inputs[0].default_value = lin("#%02X%02X%02X" % FUNDO)
    preto = wn.nodes.new("ShaderNodeBackground")
    preto.inputs[0].default_value = (0, 0, 0, 1)
    mx = wn.nodes.new("ShaderNodeMixShader")
    out = wn.nodes.new("ShaderNodeOutputWorld")
    wn.links.new(lp.outputs["Is Camera Ray"], mx.inputs[0])
    wn.links.new(preto.outputs[0], mx.inputs[1])
    wn.links.new(fundo.outputs[0], mx.inputs[2])
    wn.links.new(mx.outputs[0], out.inputs["Surface"])
    config_render(largura, altura, rapido)
    return cam


def config_render(largura=1080, altura=1920, rapido=False):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = largura, altura, 100
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.render.film_transparent = False
    ee = sc.eevee
    ee.taa_render_samples = 8 if rapido else 32
    for attr, v in (("use_raytracing", False), ("use_shadows", False), ("use_gtao", False), ("use_bloom", False),
                    ("use_volumetric_shadows", False), ("use_fast_gi", False)):
        if hasattr(ee, attr):
            setattr(ee, attr, v)
    if hasattr(ee, "shadow_ray_count"):
        ee.shadow_ray_count, ee.shadow_step_count = 1, 1
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.compression = 15


# ------------------------------------------------------------------------------------------------ pose e animação

EIXOS = {"rx": Vector((1, 0, 0)), "ry": Vector((0, 1, 0)), "rz": Vector((0, 0, 1))}


def aplicar_pose(rig, pose):
    """pose: {osso: {"rx", "ry", "rz" (graus, eixos do mundo), "loc": (x, y, z) m}} + chaves do rosto.
    ry = giro no plano da tela, igual ao "rot" do rig 2D (positivo = horário); rx positivo inclina para a câmera;
    rz positivo vira a frente para +X (direita da tela)."""
    for pbn in rig.pose.bones:
        d = pose.get(pbn.name, {})
        Ri = pbn.bone.matrix_local.to_3x3().inverted()
        q = Quaternion()
        for k in ("rz", "ry", "rx"):
            if d.get(k):
                q = q @ Quaternion((Ri @ EIXOS[k]).normalized(), math.radians(d[k]))
        pbn.rotation_quaternion = q
        pbn.location = Ri @ Vector(d.get("loc", (0, 0, 0)))
    for k, padrao in PROPS_ROSTO.items():
        v = pose.get(k, padrao)
        if k == "visema" and isinstance(v, str):
            v = VISEMAS.index(v)
        rig[k] = float(v)


PARTES_2D = {"braco_e": "braco_e", "antebraco_e": "antebraco_e", "braco_d": "braco_d", "antebraco_d": "antebraco_d",
             "cabeca": "cabeca", "tronco": "coluna", "perna_e": "coxa_e", "perna_d": "coxa_d", "tenis_e": "pe_e",
             "tenis_d": "pe_d"}


def de_pose_2d(p2d):
    """Converte uma pose do rig 2D (rot em graus no plano da tela, dx/dy em px, corpo_rot, pulo, visema, piscar,
    olhar) para a pose 3D."""
    out = {}
    for parte, osso in PARTES_2D.items():
        q = p2d.get(parte)
        if isinstance(q, dict):
            out[osso] = {"ry": q.get("rot", 0.0), "loc": (q.get("dx", 0.0) / 1000, 0.0, -q.get("dy", 0.0) / 1000)}
    raiz = out.setdefault("raiz", {})
    raiz["ry"] = p2d.get("corpo_rot", 0.0)
    raiz["loc"] = (0.0, 0.0, p2d.get("pulo", 0.0) / 1000)
    if "visema" in p2d:
        out["visema"] = p2d["visema"]
    if "piscar" in p2d:
        out["piscar_e"] = out["piscar_d"] = p2d["piscar"]
    if "olhar" in p2d:
        out["olhar_x"], out["olhar_y"] = p2d["olhar"]
    return out


def somar(pose, osso, chave, v):
    d = pose.setdefault(osso, {})
    if chave == "loc":
        d["loc"] = tuple(a + b for a, b in zip(d.get("loc", (0.0, 0.0, 0.0)), v))
    else:
        d[chave] = d.get(chave, 0.0) + v


def envelope(t, t0, dur, borda=0.25):
    if t <= t0 or t >= t0 + dur:
        return 0.0
    a = min(1.0, (t - t0) / borda, (t0 + dur - t) / borda)
    return a * a * (3 - 2 * a)


def _vis(pose):
    v = pose.get("visema", 0)
    return VISEMAS.index(v) if isinstance(v, str) else v


def gag(nome, t0, dur, intensidade=1.0):
    """Camada de gag por cima da animação: devolve f(t, pose) -> pose. Gags: rebolado, cabeca_beat, piscadinha,
    dancinha, disfarca. Todas entram e saem suaves (envelope de 0,25 s) e escalam com a intensidade."""

    def camada(t, pose):
        e = envelope(t, t0, dur, min(0.25, dur / 4)) * intensidade
        if e <= 0:
            return pose
        tau, u = t - t0, (t - t0) / dur
        if nome == "rebolado":
            # quadril balança de lado no ritmo (2,2 Hz) e a coluna compensa: o tronco e a cabeça ficam no lugar
            ph = 2 * math.pi * 2.2 * tau
            a = 7.0 * e * math.sin(ph)
            torce = 5.0 * e * math.sin(ph + math.pi / 2)
            somar(pose, "quadril", "ry", a)
            somar(pose, "quadril", "rz", torce)
            somar(pose, "quadril", "loc", (0.009 * e * math.sin(ph), 0.0, 0.0))
            somar(pose, "coluna", "ry", -a)
            somar(pose, "coluna", "rz", -torce)
            for lado in ("e", "d"):
                somar(pose, f"coxa_{lado}", "ry", -a)
                somar(pose, f"coxa_{lado}", "rz", -torce)
        elif nome == "cabeca_beat":
            ph = 2 * math.pi * 2.0 * tau
            somar(pose, "cabeca", "ry", 9.0 * e * math.sin(ph))
            somar(pose, "cabeca", "rx", 3.0 * e * abs(math.sin(ph)))
        elif nome == "piscadinha":
            _olhar_camera(pose, e)
            pis = suave(0.3, 0.42, u) * (1 - suave(0.62, 0.74, u))
            pose["piscar_d"] = max(pose.get("piscar_d", 0.0), pis * min(1.0, intensidade))
            somar(pose, "cabeca", "ry", 7.0 * e)
            if 0.28 < u < 0.8 and e > 0.5:
                pose["visema"] = "feliz"
        elif nome == "dancinha":
            ph = 2 * math.pi * 2.0 * tau
            somar(pose, "braco_e", "ry", 40.0 * e * (0.5 + 0.5 * math.sin(ph)))
            somar(pose, "braco_d", "ry", -40.0 * e * (0.5 + 0.5 * math.sin(ph + math.pi)))
            somar(pose, "antebraco_e", "ry", 30.0 * e)
            somar(pose, "antebraco_d", "ry", -30.0 * e)
            somar(pose, "raiz", "loc", (0.0, 0.0, 0.014 * e * abs(math.sin(ph))))
            somar(pose, "quadril", "ry", 6.0 * e * math.sin(ph))
            somar(pose, "cabeca", "ry", 6.0 * e * math.sin(ph + math.pi / 3))
            if e > 0.5:
                pose["visema"] = "feliz"
        elif nome == "disfarca":
            olha = suave(0.0, 0.2, u) * (1 - suave(0.5, 0.58, u))
            _olhar_camera(pose, olha * e)
            if u > 0.56:
                pose["olhar_x"] = pose.get("olhar_x", 0.0) + 0.9 * e
                pose["sobrancelha_dy"] = pose.get("sobrancelha_dy", 0.0) - 8.0 * e
                if 0.6 < u < 0.95 and e > 0.5:
                    pose["visema"] = "U"
        else:
            raise ValueError(f"gag desconhecida: {nome}")
        return pose

    return camada


def _olhar_camera(pose, k):
    """Puxa cabeça e olhos para a câmera com peso k (0..1)."""
    d = pose.setdefault("cabeca", {})
    for ch in ("rx", "rz"):
        d[ch] = d.get(ch, 0.0) * (1 - k)
    pose["olhar_x"] = pose.get("olhar_x", 0.0) * (1 - k)
    pose["olhar_y"] = pose.get("olhar_y", 0.0) * (1 - k)


def animar(rig, base, duracao, camadas=(), fps=30):
    """Grava keyframes quadro a quadro: pose = base(t) e cada camada por cima."""
    sc = bpy.context.scene
    sc.render.fps = fps
    n = int(round(duracao * fps))
    sc.frame_start, sc.frame_end = 1, n
    for f in range(1, n + 1):
        t = (f - 1) / fps
        pose = base(t)
        for c in camadas:
            pose = c(t, pose)
        aplicar_pose(rig, pose)
        for pbn in rig.pose.bones:
            pbn.keyframe_insert("rotation_quaternion", frame=f)
            pbn.keyframe_insert("location", frame=f)
        for k in PROPS_ROSTO:
            rig.keyframe_insert(f'["{k}"]', frame=f)
    acao = rig.animation_data.action
    for fc in _fcurves(acao):
        modo = "CONSTANT" if fc.data_path == '["visema"]' else "LINEAR"
        for kp in fc.keyframe_points:
            kp.interpolation = modo


def _fcurves(acao):
    if hasattr(acao, "fcurves") and len(getattr(acao, "fcurves", [])):
        return list(acao.fcurves)
    out = []  # ações em camadas (Blender 4.4+)
    for camada in getattr(acao, "layers", []):
        for faixa in camada.strips:
            for bag in faixa.channelbags:
                out += list(bag.fcurves)
    return out


# ------------------------------------------------------------------------------------------------ principal

def limpar():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    nome = args[0] if args else "nico"
    dest = pasta_saida(nome, args[args.index("--saida") + 1] if "--saida" in args else None)
    limpar()
    rig = construir(nome, dest)
    aplicar_pose(rig, de_pose_2d(Boneco2D(nome).pose_base))
    cena()
    dest.mkdir(parents=True, exist_ok=True)
    bpy.context.scene["boneco3d"] = nome
    bpy.ops.wm.save_as_mainfile(filepath=str(dest / f"{nome}.blend"), compress=True)
    print("blend ok", dest / f"{nome}.blend")
    if "--previa" in args:
        sc = bpy.context.scene
        sc.render.filepath = str(dest / "previa.png")
        bpy.ops.render.render(write_still=True)
        print("previa ok", dest / "previa.png")


if __name__ == "__main__":
    main()
