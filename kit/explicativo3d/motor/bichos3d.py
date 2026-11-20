# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Bichos e objetos procedurais (os que não existem prontos em CC0). Cada bicho volta separado em partes,
cada parte com o seu vazio de controle, para a desmontagem animar uma por uma.

Uso (dentro do Blender, depois de kit3d.iniciar()):
    cv = caravela("caravela_1", local=(0, 0, 2.2), escala=1.0)
    cv["raiz"], cv["boia"], cv["cacadores"], cv["digestao"], cv["filhotes"]
"""
import math
import random

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

import kit3d as K
from kit3d import G

CORES_CARAVELA = {
    "boia": ("#86CFFF", "#C9A2FF"),       # base -> topo
    "crista": ("#B79BFF", "#FF8FD0"),
    "tentaculo": "#4D6CFF",
    "conta": "#2F45C9",
    "digestao": ("#FF9F6B", "#FFD0A8"),
    "filhotes": ("#B07CFF", "#FFB3E0"),
}


def _vazio(nome, pai, local=(0, 0, 0)):
    ob = bpy.data.objects.new(nome, None)
    K.COL.objects.link(ob)
    ob.parent = pai
    ob.location = local
    return ob


def olhos(nome, centro, raio, olhar=(0, -1, 0), afastar=1.15, pai=None, linha=0.002):
    """Par de olhos cartoon (esclera, pupila e brilho) virados para `olhar`, lado a lado no eixo X."""
    olhar = Vector(olhar).normalized()
    lado = Vector((1, 0, 0))
    obs = []
    for s in (-1, 1):
        c = Vector(centro) + lado * s * raio * afastar
        for parte, r, desloc, cor in (("esclera", raio, 0.0, "#FFFFFF"), ("pupila", raio * 0.55, raio * 0.62, "#120E1E"),
                                      ("brilho", raio * 0.2, raio * 1.02, "#FFFFFF")):
            bm = bmesh.new()
            bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=14, radius=r)
            p = c + olhar * desloc
            if parte == "brilho":
                p += Vector((-0.35, 0, 0.4)) * raio
            bmesh.ops.translate(bm, verts=bm.verts, vec=p)
            obs.append(K.objeto(f"{nome}_{parte}_{s}", K.malha_bm(f"{nome}_{parte}_{s}", bm),
                                G.mat_chapado(f"{nome}_{parte}_{s}", cor), linha if parte == "esclera" else 0, pai=pai))
    return obs


def caravela(nome, local, escala=1.0, espelho=False, linha=0.005, semente=3):
    """Caravela-portuguesa cartoon. Medidas na escala 1: boia de ~0,5 m, tentáculos de ~1,5 m.
    `espelho` troca o lado em que as partes de baixo penduram (caravela canhota x destra)."""
    rnd = random.Random(semente)
    raiz = bpy.data.objects.new(nome, None)
    K.COL.objects.link(raiz)
    raiz.location = local
    raiz.scale = (-escala if espelho else escala, escala, escala)
    partes = {"raiz": raiz}

    # boia: corpo alongado no eixo X, mais grosso na frente (+X), com a ponta de trás arrebitada
    boia = _vazio(f"{nome}_boia", raiz)
    els = []
    for i in range(14):
        u = i / 13
        x = 0.26 - 0.52 * u
        r = 0.095 * (1.0 - 0.45 * u) + 0.02
        z = 0.05 + 0.06 * u * u
        els.append(((x, 0, z), r * 1.35, (1.0, 0.85, 0.9)))
    me = K.blob(f"{nome}_boia_m", els, resolucao=0.01)
    K.objeto(f"{nome}_boia_m", me, K.mat_gradiente(f"{nome}_boia", *CORES_CARAVELA["boia"], -0.05, 0.2), linha, pai=boia)
    cr = []  # crista (a "vela"): barbatana fina, rosa, com a borda de cima ondulada, separada do corpo
    for i in range(40):
        u = i / 39
        x = 0.2 - 0.4 * u
        topo = 0.2 + 0.03 * math.sin(u * math.pi * 3.5) + 0.06 * math.sin(u * math.pi)
        for k in range(4):
            z = 0.09 + (topo - 0.09) * k / 3
            cr.append(((x, 0, z), 0.04, (1.0, 0.22, 1.0)))
    me = K.blob(f"{nome}_crista_m", cr, resolucao=0.006)
    K.objeto(f"{nome}_crista_m", me, K.mat_gradiente(f"{nome}_crista", *CORES_CARAVELA["crista"], 0.1, 0.27), linha,
             pai=boia)
    bm = bmesh.new()  # brilho de balão
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=1.0)
    bmesh.ops.scale(bm, vec=(0.07, 0.012, 0.022), verts=bm.verts)
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(-12), 3, "Y"))
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0.02, -0.112, 0.11))
    K.objeto(f"{nome}_boia_brilho", K.malha_bm(f"{nome}_boia_brilho", bm), G.mat_chapado(f"{nome}_boia_brilho", "#F4FBFF"),
             0, pai=boia)
    olhos(f"{nome}_olho", (0.16, -0.105, 0.07), 0.034, pai=boia)
    partes["boia"] = boia

    # caçadores: tentáculos pendurados do lado (offset em +Y), com contas de veneno
    cac = _vazio(f"{nome}_cacadores", raiz, (0.0, 0.0, 0.0))
    bm = bmesh.new()
    contas = bmesh.new()
    for k in range(7):
        x0 = 0.12 - 0.04 * k + rnd.uniform(-0.01, 0.01)
        y0 = 0.03 + 0.015 * (k % 2)
        comp = 1.5 * rnd.uniform(0.7, 1.0)
        fase = rnd.uniform(0, 6.28)
        pts = []
        for j in range(40):
            u = j / 39
            pts.append((x0 + 0.03 * math.sin(fase + u * 9) * u, y0 + 0.02 * math.cos(fase + u * 7) * u, -0.02 - comp * u))
        v, f = G.tubo(pts, 0.011, nu=8, afinar="fim")
        tmp = G.bm_de(v, f)
        tmp_me = bpy.data.meshes.new("tmp")
        tmp.to_mesh(tmp_me)
        tmp.free()
        bm.from_mesh(tmp_me)
        bpy.data.meshes.remove(tmp_me)
        for j in range(3, 40, 4):  # contas (baterias de nematocistos)
            c = Vector(pts[j])
            bmesh.ops.create_uvsphere(contas, u_segments=10, v_segments=7, radius=0.016 * (1 - 0.5 * j / 39),
                                      matrix=Matrix.Translation(c))
    K.objeto(f"{nome}_tentaculos", K.malha_bm(f"{nome}_tentaculos", bm),
             G.mat_toon(f"{nome}_tentaculos", CORES_CARAVELA["tentaculo"]), linha * 0.7, pai=cac)
    K.objeto(f"{nome}_contas", K.malha_bm(f"{nome}_contas", contas),
             G.mat_toon(f"{nome}_contas", CORES_CARAVELA["conta"]), linha * 0.5, pai=cac)
    olhos(f"{nome}_olho_cac", (0.0, -0.02, -0.06), 0.016, pai=cac, linha=0.0012)
    partes["cacadores"] = cac

    # digestão: tubinhos curtos e caídos embaixo do meio da boia
    dig = _vazio(f"{nome}_digestao", raiz)
    els = []
    for k in range(9):
        a = 2 * math.pi * k / 9
        p0 = Vector((-0.02 + 0.06 * math.cos(a), 0.04 * math.sin(a), -0.02))
        p1 = p0 + Vector((0.03 * math.cos(a), 0.02 * math.sin(a), -0.13 - 0.04 * (k % 3)))
        els.extend(K.cadeia(p0, p1, 0.026, 0.018, passo=0.4))
    me = K.blob(f"{nome}_digestao_m", els, resolucao=0.008)
    K.objeto(f"{nome}_digestao_m", me, K.mat_gradiente(f"{nome}_digestao", *CORES_CARAVELA["digestao"], -0.2, 0.0),
             linha * 0.8, pai=dig)
    olhos(f"{nome}_olho_dig", (-0.02, -0.07, -0.08), 0.016, pai=dig, linha=0.0012)
    partes["digestao"] = dig

    # filhotes: cachos de bolinhas (gonozooides) atrás
    fil = _vazio(f"{nome}_filhotes", raiz)
    els = []
    for k in range(3):
        c = Vector((-0.13 - 0.05 * k, 0.02 * (k - 1), -0.06 - 0.02 * k))
        for _ in range(9):
            els.append((tuple(c + Vector((rnd.uniform(-0.04, 0.04), rnd.uniform(-0.035, 0.035),
                                          rnd.uniform(-0.05, 0.02)))), 0.028))
    me = K.blob(f"{nome}_filhotes_m", els, resolucao=0.007)
    K.objeto(f"{nome}_filhotes_m", me, K.mat_gradiente(f"{nome}_filhotes", *CORES_CARAVELA["filhotes"], -0.13, 0.0),
             linha * 0.8, pai=fil)
    olhos(f"{nome}_olho_fil", (-0.18, -0.06, -0.06), 0.016, pai=fil, linha=0.0012)
    partes["filhotes"] = fil
    return partes


def chinelo(nome, local, giro=0.0, linha=0.004):
    """Chinelo de dedo genérico (sem marca): sola amarela e tira turquesa, para o "achado no corte"."""
    raiz = bpy.data.objects.new(nome, None)
    K.COL.objects.link(raiz)
    raiz.location = local
    raiz.rotation_euler = (0, 0, giro)
    els = []
    for i in range(12):
        u = i / 11
        x = -0.12 + 0.24 * u
        larg = 0.045 + 0.012 * math.sin(math.pi * u) + (0.008 if u > 0.7 else 0)
        els.append(((x, 0, 0), larg, (1.0, 1.0, 0.22)))
    K.objeto(f"{nome}_sola", K.blob(f"{nome}_sola", els, resolucao=0.006), G.mat_toon(f"{nome}_sola", "#FFD23F"),
             linha, pai=raiz)
    tira = []
    for s in (-1, 1):
        pts = [(0.07, 0, 0.012)] + [(0.07 - 0.11 * t, s * 0.045 * math.sin(math.pi * t * 0.9), 0.012 + 0.03 *
                                     math.sin(math.pi * t)) for t in (0.25, 0.5, 0.75, 1.0)]
        v, f = G.tubo(pts, 0.008, nu=8, afinar="uniforme")
        tira.append(G.bm_de(v, f))
    bm = bmesh.new()
    for t in tira:
        me = bpy.data.meshes.new("tmp")
        t.to_mesh(me)
        t.free()
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    K.objeto(f"{nome}_tira", K.malha_bm(f"{nome}_tira", bm), G.mat_toon(f"{nome}_tira", "#3CC8C8"), linha, pai=raiz)
    return raiz


def _esfera(nome, raio, centro, escala=(1, 1, 1), seg=(16, 10)):
    """Malha de esfera em `centro`; `escala` age depois de posicionar (igual ao esfera().scale() do motor3d.js)."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg[0], v_segments=seg[1], radius=raio, matrix=Matrix.Translation(centro))
    bmesh.ops.scale(bm, vec=escala, verts=bm.verts)
    return K.malha_bm(nome, bm)


def _tubo(nome, pontos, raio, afinar="nenhum"):
    v, f = G.tubo(pontos, raio, nu=8, afinar=afinar)
    return K.malha_bm(nome, G.bm_de(v, f))


def mascote(nome, local, cor="#FFD23F", cor2=None, forma="gota", escala=1.0, linha=0.005, pai=None):
    """Personagem de qualquer coisa (mascote): corpo com olhos, boca, bracinhos e perninhas. É o jeito de pôr um
    personagem em qualquer assunto, mesmo sem modelo pronto: o raio, a casa, a tomada, a gota, o átomo...
    Base nos pés, em `local`; ~0,32 m de altura na escala 1; frente para -Y (a câmera).

        r = mascote("raio", (0.3, -0.2, 0), forma="raio", cor="#FFE45E", cor2="#FFB23E")
        r["raiz"], r["corpo"], r["braco_e"], r["braco_d"] (vazios para girar), r["boca"] (escala Z para falar),
        r["olhos"]

    Formas: "gota", "bola", "caixa" (bloco arredondado) e "raio" (zigue-zague). Olhos, boca, ombros e pernas são
    encostados na superfície real do corpo (a malha do metaball fica menor que o raio dos elementos)."""
    raiz = _vazio(nome, pai, local)
    raiz.scale = (escala, escala, escala)
    z_corpo = 0.07
    corpo = _vazio(f"{nome}_corpo", raiz, (0, 0, z_corpo))
    olho_z, largura = 0.17, 0.09
    if forma == "bola":
        els = [((0, 0, 0.11), 0.11)]
    elif forma == "caixa":
        # grade 3 x 2 x 3: com só os oito cantos (raio 0,06) as bolas não se fundem e viram caroços soltos
        els = [((x, y, z), 0.075) for x in (-0.06, 0, 0.06) for y in (-0.04, 0.04) for z in (0.05, 0.11, 0.17)]
        olho_z, largura = 0.16, 0.1
    elif forma == "raio":
        els = [(p, r, (1, 0.6, 1)) for p, r in K.cadeia((0.05, 0, 0.26), (-0.04, 0, 0.14), 0.055, 0.05, 0.3)
               + K.cadeia((-0.04, 0, 0.14), (0.04, 0, 0.11), 0.05, 0.05, 0.3)
               + K.cadeia((0.04, 0, 0.11), (-0.03, 0, -0.02), 0.05, 0.02, 0.3)]
        largura = 0.06
    else:  # gota
        els = [((0, 0, 0.08), 0.1), ((0, 0, 0.17), 0.07), ((0, 0, 0.24), 0.035)]
    me = K.blob(f"{nome}_corpo_m", els, resolucao=0.007)
    mat = K.mat_gradiente(f"{nome}_corpo", cor2, cor, 0, 0.26) if cor2 else G.mat_toon(f"{nome}_corpo", cor)
    K.objeto(f"{nome}_corpo_m", me, mat, linha, pai=corpo)

    # superfície real do corpo (espaço do vazio "corpo"), por raio contra a malha
    arvore = BVHTree.FromPolygons([v.co.copy() for v in me.vertices], [tuple(p.vertices) for p in me.polygons])

    def toque(origem, direcao):
        return arvore.ray_cast(Vector(origem), Vector(direcao))[0]

    def meio_x(z):
        e, d = toque((-1, 0, z), (1, 0, 0)), toque((1, 0, z), (-1, 0, 0))
        return (e.x + d.x) / 2 if e and d else 0.0

    # olhos no máximo a 55% da meia-altura acima do meio do corpo (na bola, 0,17 já fica fora da malha)
    zs = [v.co.z for v in me.vertices]
    z_meio, meia = (max(zs) + min(zs)) / 2, (max(zs) - min(zs)) / 2
    olho_z = min(olho_z, z_meio + 0.55 * meia)
    raio_olho, afastar = 0.022, 1.05
    ox = meio_x(olho_z)
    frentes = [toque((ox + s * raio_olho * afastar, -1, olho_z), (0, 1, 0)) for s in (-1, 1)]
    frentes = [p.y for p in frentes if p]
    frente = max(frentes) if frentes else -0.08  # centro do olho na face mais recuada: nenhum olho solto no ar
    ol = olhos(f"{nome}_olho", (ox, frente, olho_z), raio_olho, afastar=afastar, pai=corpo, linha=linha * 0.5)

    boca_z = olho_z - 0.05
    bx = meio_x(boca_z)
    pb = toque((bx, -1, boca_z), (0, 1, 0))
    boca = _vazio(f"{nome}_boca", corpo, (bx, pb.y + 0.003 if pb else frente - 0.004, boca_z))
    K.objeto(f"{nome}_boca_m", _esfera(f"{nome}_boca_m", 0.02, (0, 0, 0), (1.2, 0.5, 0.6)),
             G.mat_chapado(f"{nome}_boca_m", "#3A1020"), 0, pai=boca)

    membros = G.mat_toon(f"{nome}_membros", "#1B1530")
    mao = G.mat_toon(f"{nome}_mao", "#FFFFFF")

    def braco(s):
        lado = "d" if s > 0 else "e"
        pt = toque((s, 0, 0.11), (-s, 0, 0))
        ombro = pt.x - s * 0.006 if pt else s * largura  # começa um pouco dentro do corpo
        g = _vazio(f"{nome}_braco_{lado}", corpo, (ombro, 0, 0.11))
        K.objeto(f"{g.name}_m", _tubo(f"{g.name}_m", [(0, 0, 0), (s * 0.05, -0.01, -0.03), (s * 0.09, -0.01, -0.02)],
                                      0.009), membros, 0, pai=g)
        K.objeto(f"{g.name}_mao", _esfera(f"{g.name}_mao", 0.016, (s * 0.095, -0.01, -0.02), seg=(12, 8)), mao,
                 linha * 0.5, pai=g)
        return g

    braco_e, braco_d = braco(-1), braco(1)

    # pernas: do fundo do corpo até o pé; onde o corpo não passa sobre a perna (raio), sai da ponta de baixo
    fundo = min(me.vertices, key=lambda v: v.co.z).co
    for s in (-1, 1):
        pt = toque((s * 0.035, 0, -1), (0, 0, 1))
        if pt and pt.z < fundo.z + 0.05:
            topo = (s * 0.035, 0, z_corpo + pt.z + 0.01)
        else:
            topo = (fundo.x + s * 0.012, 0, z_corpo + fundo.z + 0.01)
        K.objeto(f"{nome}_perna_{s}", _tubo(f"{nome}_perna_{s}", [topo, (s * 0.04, 0, 0.012)], 0.01), membros, 0,
                 pai=raiz)
        K.objeto(f"{nome}_pe_{s}", _esfera(f"{nome}_pe_{s}", 0.022, (s * 0.042, -0.012, 0.012), (1, 1.4, 0.55),
                                           seg=(14, 10)), membros, 0, pai=raiz)
    return {"raiz": raiz, "corpo": corpo, "braco_e": braco_e, "braco_d": braco_d, "boca": boca, "olhos": ol}
