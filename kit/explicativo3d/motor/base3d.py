# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Base do motor 3D: cor, malha de tubo, árvore de nós do material toon, contorno de nanquim e ajuste do EEVEE.

Roda dentro do Blender (bpy, bmesh e mathutils). Não depende de personagem nenhum: o boneco do vídeo é o próprio
objeto (com olhos, quique e reação), montado pelos módulos `kit3d` e `bichos3d`.
"""
import math

import bmesh
import bpy
from mathutils import Vector


def lin(hexa):
    """#RRGGBB (sRGB) para RGBA linear."""
    hexa = hexa.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(hexa[i:i + 2], 16) / 255
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (*out, 1.0)


def suave(a, b, x):
    """Rampa suave (smoothstep) de 0 em `a` a 1 em `b`."""
    if b == a:
        return 1.0 if x >= b else 0.0
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


# ------------------------------------------------------------------------------------------------ malhas

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


def bm_de(verts, faces):
    """bmesh a partir de vértices e faces (ignora face degenerada e funde vértices repetidos)."""
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
    """Atalhos para montar a árvore de nós de um material."""

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

    def fator_toon(self, sombra, brilho, limiar=(0.30, 0.95)):
        """Shader to RGB de um difuso branco -> rampa constante de 3 tons (sombra, luz, brilho). Só existe no EEVEE."""
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
        no = self.n("ShaderNodeVectorMath", operation="SCALE")
        self.ligar(cr.outputs["Color"], no.inputs[0])
        no.inputs["Scale"].default_value = topo
        return no.outputs[0]

    def emitir(self, cor):
        em = self.n("ShaderNodeEmission")
        self.ligar(cor, em.inputs["Color"])
        out = self.n("ShaderNodeOutputMaterial")
        self.ligar(em.outputs[0], out.inputs["Surface"])


TOM = {  # sombra, brilho, limiares da rampa
    "padrao": (0.68, 1.10, (0.30, 0.95)),
    "suave": (0.86, 1.04, (0.16, 0.97)),
    "chapado": (1.0, 1.0, (0.0, 0.99)),
}


def mat_toon(nome, cor, tom="padrao"):
    mat = bpy.data.materials.new(nome)
    s = Nos(mat)
    sombra, brilho, limiar = TOM[tom]
    fator = s.fator_toon(sombra, brilho, limiar)
    s.emitir(s.vm("MULTIPLY", lin(cor)[:3], fator))
    return mat


def mat_chapado(nome, cor):
    mat = bpy.data.materials.new(nome)
    Nos(mat).emitir(lin(cor))
    return mat


def mat_contorno(cor):
    """Cor da casca invertida do contorno: só a face de trás aparece, e vira o traço de nanquim."""
    mat = bpy.data.materials.new("contorno")
    Nos(mat).emitir(lin(cor))
    mat.use_backface_culling = True
    if hasattr(mat, "use_backface_culling_shadow"):
        mat.use_backface_culling_shadow = True
    return mat


# ------------------------------------------------------------------------------------------------ render e cena

def config_render(largura=1080, altura=1920, amostras=8, escala=100):
    """EEVEE enxuto: sem sombra, sem raytracing, sem AO. O visual toon vem dos materiais, não da luz."""
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = largura, altura
    sc.render.resolution_percentage = escala
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    ee = sc.eevee
    ee.taa_render_samples = amostras
    for attr, v in (("use_raytracing", False), ("use_shadows", False), ("use_gtao", False), ("use_bloom", False),
                    ("use_volumetric_shadows", False), ("use_fast_gi", False)):
        if hasattr(ee, attr):
            setattr(ee, attr, v)
    if hasattr(ee, "shadow_ray_count"):
        ee.shadow_ray_count, ee.shadow_step_count = 1, 1
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.image_settings.compression = 15
    sc.render.film_transparent = True


def fcurves(acao):
    """Curvas de uma ação, no formato antigo (acao.fcurves) ou no de camadas (Blender 4.4+)."""
    if hasattr(acao, "fcurves") and len(getattr(acao, "fcurves", [])):
        return list(acao.fcurves)
    out = []
    for camada in getattr(acao, "layers", []):
        for faixa in camada.strips:
            for bag in faixa.channelbags:
                out += list(bag.fcurves)
    return out


def limpar():
    bpy.ops.wm.read_factory_settings(use_empty=True)
