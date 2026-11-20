# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Kit 3D do explicativo: materiais toon, contorno de nanquim, cenário orgânico (metaball), peixes CC0 e o bloco
cortado do mundo ("o mundo em corte"). Importado pelos scripts que rodam dentro do Blender
(`blender -b --factory-startup -P cena.py`).

Antes de montar qualquer coisa, chame `iniciar()`: ela limpa a cena e cria a coleção e o material de contorno.
"""
import math
import random
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

import base3d as G

MODELOS = Path(__file__).resolve().parent.parent / "modelos"

PALETA = {
    "tinta": "#1B1530",
    "agua": "#3CC8C8",
    "agua_clara": "#9FF3E8",
    "areia": "#F6D38C",
    "areia_meio": "#E2AE62",
    "areia_funda": "#B9774A",
    "seixo": "#8A5A3C",
    "rocha": "#6B7BA4",
    "rocha_escura": "#4E5A82",
    "coral": "#FF6F59",
    "coral_ponta": "#FFC07A",
    "coral2": "#C77DFF",
    "coral2_ponta": "#FF9FD0",
    "alga": "#3DBE7A",
    "alga_ponta": "#B5E86A",
    "anemona": "#FF8FAB",
    "anemona_ponta": "#FFE3EC",
    "estrela": "#FFB23E",
    "branco": "#FFF8EC",
}

random.seed(7)


# ------------------------------------------------------------------------------------------------ materiais

def mat_gradiente(nome, cor_a, cor_b, z0, z1, tom="padrao"):
    """Toon de 3 tons com a cor variando na altura do objeto (base -> ponta)."""
    mat = bpy.data.materials.new(nome)
    s = G.Nos(mat)
    sombra, brilho, limiar = G.TOM[tom]
    fator = s.fator_toon(sombra, brilho, limiar)
    tc = s.n("ShaderNodeTexCoord")
    sep = s.n("ShaderNodeSeparateXYZ")
    s.ligar(tc.outputs["Object"], sep.inputs[0])
    mr = s.n("ShaderNodeMapRange")
    s.ligar(sep.outputs["Z"], mr.inputs["Value"])
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = z0, z1
    cor = s.mix(mr.outputs[0], G.lin(cor_a), G.lin(cor_b))
    s.emitir(s.vm("MULTIPLY", cor, fator))
    return mat


def mat_textura(nome, imagem):
    mat = bpy.data.materials.new(nome)
    s = G.Nos(mat)
    fator = s.fator_toon(*G.TOM["padrao"][:2], G.TOM["padrao"][2])
    tex = s.n("ShaderNodeTexImage", image=imagem)
    s.emitir(s.vm("MULTIPLY", tex.outputs["Color"], fator))
    return mat


def mat_areia_topo():
    """Areia com cáustica toon (linhas claras de Voronoi) só nas faces viradas para cima."""
    mat = bpy.data.materials.new("areia_topo")
    s = G.Nos(mat)
    fator = s.fator_toon(*G.TOM["padrao"][:2], G.TOM["padrao"][2])
    tc = s.n("ShaderNodeTexCoord")
    vor = s.n("ShaderNodeTexVoronoi", feature="DISTANCE_TO_EDGE")
    vor.inputs["Scale"].default_value = 5.0
    s.ligar(tc.outputs["Object"], vor.inputs["Vector"])
    linha = s.m("LESS_THAN", vor.outputs["Distance"], 0.035)
    geo = s.n("ShaderNodeNewGeometry")
    sep = s.n("ShaderNodeSeparateXYZ")
    s.ligar(geo.outputs["Normal"], sep.inputs[0])
    cima = s.m("GREATER_THAN", sep.outputs["Z"], 0.6)
    k = s.m("MULTIPLY", s.m("MULTIPLY", linha, cima), 0.55)
    cor = s.mix(k, G.lin(PALETA["areia"]), G.lin("#FFF4D2"))
    s.emitir(s.vm("MULTIPLY", cor, fator))
    return mat


def mat_transparente(nome, cor, alfa, cor_borda=None, borda=0.0):
    """Emissão translúcida (água, bolha, feixe de luz). `borda` clareia onde a superfície fica de lado."""
    mat = bpy.data.materials.new(nome)
    s = G.Nos(mat)
    c = G.lin(cor)
    if cor_borda:
        lw = s.n("ShaderNodeLayerWeight")
        lw.inputs["Blend"].default_value = 0.35
        fac = s.m("MULTIPLY", lw.outputs["Facing"], borda)
        c = s.mix(fac, c, G.lin(cor_borda))
        a = s.m("ADD", s.m("MULTIPLY", lw.outputs["Facing"], borda * 0.5), alfa)
    else:
        a = alfa
    em = s.n("ShaderNodeEmission")
    s.ligar(c, em.inputs["Color"])
    tr = s.n("ShaderNodeBsdfTransparent")
    mx = s.n("ShaderNodeMixShader")
    s.ligar(a, mx.inputs[0])
    s.ligar(tr.outputs[0], mx.inputs[1])
    s.ligar(em.outputs[0], mx.inputs[2])
    out = s.n("ShaderNodeOutputMaterial")
    s.ligar(mx.outputs[0], out.inputs["Surface"])
    mat.surface_render_method = "BLENDED"
    mat.use_backface_culling = True
    return mat


def mat_agua_fundo(cor, alfa):
    """Tinge só as faces de trás da caixa (vistas por dentro): a frente fica aberta e os objetos não desbotam."""
    mat = bpy.data.materials.new("agua")
    s = G.Nos(mat)
    geo = s.n("ShaderNodeNewGeometry")
    tc = s.n("ShaderNodeTexCoord")
    sep = s.n("ShaderNodeSeparateXYZ")
    s.ligar(tc.outputs["Generated"], sep.inputs[0])
    cor_v = s.mix(sep.outputs["Z"], G.lin("#0E5A6E"), G.lin(cor))
    a = s.m("MULTIPLY", geo.outputs["Backfacing"], alfa)
    em = s.n("ShaderNodeEmission")
    s.ligar(cor_v, em.inputs["Color"])
    tr = s.n("ShaderNodeBsdfTransparent")
    mx = s.n("ShaderNodeMixShader")
    s.ligar(a, mx.inputs[0])
    s.ligar(tr.outputs[0], mx.inputs[1])
    s.ligar(em.outputs[0], mx.inputs[2])
    out = s.n("ShaderNodeOutputMaterial")
    s.ligar(mx.outputs[0], out.inputs["Surface"])
    mat.surface_render_method = "BLENDED"
    return mat


def mat_vidro_borda(cor, alfa, potencia=5.0):
    """Vidro curvo: só a silhueta acende (facing elevado a uma potência), o miolo fica limpo."""
    mat = bpy.data.materials.new("vidro")
    s = G.Nos(mat)
    lw = s.n("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.5
    a = s.m("MULTIPLY", s.m("POWER", lw.outputs["Facing"], potencia), alfa)
    em = s.n("ShaderNodeEmission")
    em.inputs["Color"].default_value = G.lin(cor)
    tr = s.n("ShaderNodeBsdfTransparent")
    mx = s.n("ShaderNodeMixShader")
    s.ligar(a, mx.inputs[0])
    s.ligar(tr.outputs[0], mx.inputs[1])
    s.ligar(em.outputs[0], mx.inputs[2])
    out = s.n("ShaderNodeOutputMaterial")
    s.ligar(mx.outputs[0], out.inputs["Surface"])
    mat.surface_render_method = "BLENDED"
    mat.use_backface_culling = True
    return mat


def mat_feixe(nome, alfa):
    """Feixe de luz que some para baixo (coordenada Z do objeto: 0 embaixo, 1 em cima)."""
    mat = bpy.data.materials.new(nome)
    s = G.Nos(mat)
    tc = s.n("ShaderNodeTexCoord")
    sep = s.n("ShaderNodeSeparateXYZ")
    s.ligar(tc.outputs["Generated"], sep.inputs[0])
    a = s.m("MULTIPLY", s.m("POWER", sep.outputs["Z"], 1.6), alfa)
    em = s.n("ShaderNodeEmission")
    em.inputs["Color"].default_value = G.lin("#E8FFF8")
    tr = s.n("ShaderNodeBsdfTransparent")
    mx = s.n("ShaderNodeMixShader")
    s.ligar(a, mx.inputs[0])
    s.ligar(tr.outputs[0], mx.inputs[1])
    s.ligar(em.outputs[0], mx.inputs[2])
    out = s.n("ShaderNodeOutputMaterial")
    s.ligar(mx.outputs[0], out.inputs["Surface"])
    mat.surface_render_method = "BLENDED"
    return mat


CONTORNO = None
COL = None


def iniciar():
    """Cena vazia, coleção "cena" e o material de contorno da paleta."""
    global COL, CONTORNO
    G.limpar()
    COL = bpy.data.collections.new("cena")
    bpy.context.scene.collection.children.link(COL)
    CONTORNO = G.mat_contorno(PALETA["tinta"])
    return COL


def contorno(ob, espessura):
    """Casca invertida de nanquim; a espessura é em metros do mundo (compensa a escala do objeto)."""
    if espessura <= 0:
        return
    bpy.context.view_layer.update()
    escala = ob.matrix_world.to_scale()
    k = (abs(escala.x) + abs(escala.y) + abs(escala.z)) / 3
    n = max(1, len(ob.data.materials))
    for _ in range(n):
        ob.data.materials.append(CONTORNO)
    sc = ob.modifiers.new("contorno", "SOLIDIFY")
    sc.thickness, sc.offset = espessura / k, 1.0
    sc.use_flip_normals, sc.use_rim, sc.material_offset = True, False, n
    sc.use_quality_normals = True


# ------------------------------------------------------------------------------------------------ geometria


def objeto(nome, me, mat, linha=0.006, suave=True, pai=None):
    if suave:
        for p in me.polygons:
            p.use_smooth = True
    if mat is not None:
        me.materials.append(mat)
    ob = bpy.data.objects.new(nome, me)
    COL.objects.link(ob)
    if pai is not None:
        ob.parent = pai
    contorno(ob, linha)
    return ob


def malha_bm(nome, bm):
    me = bpy.data.meshes.new(nome)
    bm.to_mesh(me)
    bm.free()
    return me


def caixa(nome, x0, x1, y0, y1, z0, z1):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((x0 if v.co.x < 0 else x1, y0 if v.co.y < 0 else y1, z0 if v.co.z < 0 else z1))
    return malha_bm(nome, bm)


def blob(nome, elementos, resolucao=0.012, limiar=0.6):
    """Metaball -> malha. elementos: (centro, raio) ou (centro, raio, (sx, sy, sz)) para elipsoide."""
    mb = bpy.data.metaballs.new(nome)
    mb.resolution = mb.render_resolution = resolucao
    mb.threshold = limiar
    for el in elementos:
        e = mb.elements.new()
        e.co, e.radius = Vector(el[0]), el[1]
        if len(el) > 2:
            e.type = "ELLIPSOID"
            e.size_x, e.size_y, e.size_z = el[2]
    ob = bpy.data.objects.new(nome, mb)
    COL.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob)
    bpy.data.metaballs.remove(mb)
    return me


def cadeia(p0, p1, r0, r1, passo=0.45, curva=None):
    """Elementos de metaball ao longo de um segmento (com desvio opcional), raio afinando de r0 a r1."""
    p0, p1 = Vector(p0), Vector(p1)
    n = max(2, int((p1 - p0).length / (passo * min(r0, r1))) + 1)
    out = []
    for i in range(n):
        u = i / (n - 1)
        p = p0.lerp(p1, u)
        if curva:
            p = p + Vector(curva(u))
        out.append((tuple(p), r0 + (r1 - r0) * u))
    return out


def coral(nome, base, altura, cor_a, cor_b, linha):
    """Coral de galhos: ramos que sobem abrindo, ponta mais grossa e mais clara."""
    els = [(base, altura * 0.16, (1.4, 1.4, 0.6))]
    rnd = random.Random(nome)

    def galho(p, d, comp, r, nivel):
        fim = Vector(p) + d * comp
        els.extend(cadeia(p, fim, r, r * 0.8))
        els.append((tuple(fim), r * 1.25))
        if nivel < 3:
            for _ in range(2 if nivel else 3):
                nd = (d + Vector((rnd.uniform(-0.7, 0.7), rnd.uniform(-0.5, 0.5), 0.35))).normalized()
                galho(fim, nd, comp * rnd.uniform(0.6, 0.8), r * 0.78, nivel + 1)

    galho(Vector(base), Vector((0, 0, 1)), altura * 0.36, altura * 0.1, 0)
    me = blob(nome, els, resolucao=altura * 0.018)
    z0, z1 = base[2], base[2] + altura
    return objeto(nome, me, mat_gradiente(nome, cor_a, cor_b, z0, z1), linha)


def alga(nome, base, altura, n_fitas, linha, fase=0.0):
    """Tufo de fitas achatadas e onduladas."""
    els = []
    rnd = random.Random(nome)
    for i in range(n_fitas):
        ang = 2 * math.pi * i / n_fitas + rnd.uniform(-0.3, 0.3)
        alt = altura * rnd.uniform(0.6, 1.0)
        lado = Vector((math.cos(ang), math.sin(ang), 0))
        n = 40
        for j in range(n):
            u = j / (n - 1)
            onda = 0.07 * altura * math.sin(5.5 * u + fase + i) * u
            p = Vector(base) + lado * (0.05 * altura * u + onda) + Vector((0, 0, alt * u))
            larg = altura * 0.075 * (1 - 0.55 * u) * (0.7 + 0.3 * math.sin(math.pi * min(1, u * 1.3)))
            els.append((tuple(p), larg, (1.0, 0.4, 1.3)))
    me = blob(nome, els, resolucao=altura * 0.01)
    return objeto(nome, me, mat_gradiente(nome, PALETA["alga"], PALETA["alga_ponta"], base[2], base[2] + altura), linha)


def anemona(nome, base, raio, linha, n=26):
    els = [(base, raio * 0.75, (1.3, 1.3, 0.8))]
    rnd = random.Random(nome)
    for i in range(n):
        ang = 2 * math.pi * i / n + rnd.uniform(-0.12, 0.12)
        anel = 0.55 if i % 2 else 0.85
        p0 = Vector(base) + Vector((math.cos(ang) * raio * anel * 0.6, math.sin(ang) * raio * anel * 0.6, raio * 0.25))
        comp = raio * rnd.uniform(1.0, 1.4)
        aberto = 0.55 + 0.35 * anel

        def curva(u, ang=ang, comp=comp, aberto=aberto):
            return (math.cos(ang) * comp * aberto * u * u, math.sin(ang) * comp * aberto * u * u, 0.0)

        els.extend(cadeia(p0, p0 + Vector((0, 0, comp)), raio * 0.16, raio * 0.11, passo=0.4, curva=curva))
    me = blob(nome, els, resolucao=raio * 0.05)
    z0 = base[2]
    return objeto(nome, me, mat_gradiente(nome, PALETA["anemona"], PALETA["anemona_ponta"], z0, z0 + raio * 1.5), linha)


def estrela(nome, centro, raio, linha, giro=0.0):
    els = [(centro, raio * 0.42, (1.0, 1.0, 0.5))]
    for i in range(5):
        a = giro + 2 * math.pi * i / 5
        d = Vector((math.cos(a), math.sin(a), 0))
        els.extend(cadeia(centro, Vector(centro) + d * raio, raio * 0.3, raio * 0.12, passo=0.35))
    me = blob(nome, [(p, r, (1.0, 1.0, 0.55)) for p, r, *_ in els], resolucao=raio * 0.06)
    return objeto(nome, me, G.mat_toon(nome, PALETA["estrela"]), linha)


def pedra(nome, centro, tam, cor, linha, achatar=0.6):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)
    rnd = random.Random(nome)
    fases = [rnd.uniform(0, 6.28) for _ in range(3)]
    for v in bm.verts:
        n = v.co.normalized()
        k = 1 + 0.12 * math.sin(3 * n.x + fases[0]) + 0.1 * math.sin(4 * n.y + fases[1]) + 0.08 * math.sin(5 * n.z + fases[2])
        v.co = Vector((n.x * tam[0] * k, n.y * tam[1] * k, n.z * tam[2] * k * achatar)) + Vector(centro)
    return objeto(nome, malha_bm(nome, bm), G.mat_toon(nome, cor), linha)


def bolha(nome, centro, raio, linha):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=16, radius=raio)
    bmesh.ops.translate(bm, verts=bm.verts, vec=Vector(centro))
    ob = objeto(nome, malha_bm(nome, bm), mat_transparente(nome, PALETA["agua_clara"], 0.25, "#FFFFFF", 1.0), 0)
    bm = bmesh.new()  # brilho da bolha
    bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=raio * 0.22)
    bmesh.ops.translate(bm, verts=bm.verts, vec=Vector(centro) + Vector((-0.4, -0.6, 0.45)) * raio)
    objeto(nome + "_brilho", malha_bm(nome + "_brilho", bm), G.mat_chapado(nome + "_b", "#FFFFFF"), 0, pai=ob)
    return ob


def areia_topo(nome, x0, x1, y0, y1, z_base, altura, linha):
    """Superfície de areia ondulada, fechada até z_base (as laterais viram o corte da fatia)."""
    nx, ny = 48, 36
    bm = bmesh.new()
    vs = {}
    for i in range(nx + 1):
        for j in range(ny + 1):
            x = x0 + (x1 - x0) * i / nx
            y = y0 + (y1 - y0) * j / ny
            h = altura * (0.55 + 0.25 * math.sin(4.0 * x + 1.3) * math.cos(3.2 * y) + 0.2 * math.sin(9 * x + 5 * y))
            vs[i, j] = bm.verts.new((x, y, z_base + h))
    for i in range(nx):
        for j in range(ny):
            bm.faces.new((vs[i, j], vs[i + 1, j], vs[i + 1, j + 1], vs[i, j + 1]))
    borda = [e for e in bm.edges if e.is_boundary]
    ext = bmesh.ops.extrude_edge_only(bm, edges=borda)
    novos = [v for v in ext["geom"] if isinstance(v, bmesh.types.BMVert)]
    for v in novos:
        v.co.z = z_base
    bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = malha_bm(nome, bm)
    ob = objeto(nome, me, mat_areia_topo(), linha, suave=False)
    return ob


def seixos(nome, plano, faixa_z, n, cor, linha, tam=0.035):
    """Seixos embutidos no corte da areia. plano: ("y", valor, x0, x1) ou ("x", valor, y0, y1)."""
    rnd = random.Random(nome)
    eixo, v, a0, a1 = plano
    for i in range(n):
        a = rnd.uniform(a0 + 0.05, a1 - 0.05)
        z = rnd.uniform(*faixa_z)
        t = tam * rnd.uniform(0.6, 1.3)
        c = (a, v, z) if eixo == "y" else (v, a, z)
        pedra(f"{nome}_{i}", c, (t * 1.3, t * 1.3, t), cor, linha, achatar=0.75)


def feixe(nome, topo, base_z, raio_topo, raio_base, alfa):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=False, segments=24, radius1=raio_base, radius2=raio_topo, depth=topo[2] - base_z)
    bmesh.ops.translate(bm, verts=bm.verts, vec=Vector((topo[0], topo[1], (topo[2] + base_z) / 2)))
    me = malha_bm(nome, bm)
    ob = objeto(nome, me, mat_feixe(nome, alfa), 0)
    return ob


# ------------------------------------------------------------------------------------------------ peixes (CC0)

CORES_PEIXE = {
    "palhaco": {"Clownfish_Main": "#FF7B2C", "Clownfish_Light": "#FFF6EA", "Clownfish_Dark": "#1B1530",
                "Eyes": "#120E1E"},
    "baiacu": {"Pufferfish_Main": "#F2C14E", "Pufferfish_Light": "#FFF1C9", "Puffefish_Black": "#7A5A3A",
               "Eyes": "#120E1E"},
    "peixe": {"Bottom": "#DDF4F0", "Top": "#3E7FD0", "Fins": "#FFB23E"},
}


def peixe(nome, arquivo, comprimento, local, direcao, acao="Swimming_Normal", quadro=12, linha=0.005, brilho=True,
          tinta=None):
    """Importa um peixe GLB, troca os materiais pelo toon da paleta, põe a pose da animação e o brilho no olho.
    direcao: ângulo (graus, em torno de Z) para onde a cabeça aponta; 0 = +X, -90 = para a câmera."""
    antes_o, antes_a = set(bpy.data.objects), set(bpy.data.actions)
    bpy.ops.import_scene.gltf(filepath=str(MODELOS / f"{arquivo}.glb"))
    novos = [o for o in bpy.data.objects if o not in antes_o]
    acoes = [a for a in bpy.data.actions if a not in antes_a]
    for o in list(novos):  # forma de osso que o GLB traz como objeto solto
        if o.type == "MESH" and o.name.startswith("Icosphere"):
            novos.remove(o)
            bpy.data.objects.remove(o)
    for o in novos:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        COL.objects.link(o)
    raiz = bpy.data.objects.new(nome, None)
    COL.objects.link(raiz)
    for o in novos:
        if o.parent is None:
            o.parent = raiz
    malhas = [o for o in novos if o.type == "MESH"]
    arm = next((o for o in novos if o.type == "ARMATURE"), None)

    if arm and acoes:
        ad = arm.animation_data or arm.animation_data_create()
        for t in list(ad.nla_tracks):
            ad.nla_tracks.remove(t)
        act = next((a for a in acoes if acao in a.name), acoes[0])
        ad.action = act
        if hasattr(ad, "action_slot") and getattr(act, "slots", None):
            ad.action_slot = act.slots[0]
    bpy.context.scene.frame_set(quadro)
    bpy.context.view_layer.update()

    # medidas no espaço da raiz: comprimento em Y; a cabeça é o lado dos olhos
    dg = bpy.context.evaluated_depsgraph_get()
    pts, olhos = [], []
    for o in malhas:
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        mats = [m.name if m else "" for m in o.data.materials]
        for p in me.polygons:
            for vi in p.vertices:
                w = o.matrix_world @ me.vertices[vi].co
                pts.append(w)
                if mats and mats[p.material_index].startswith("Eyes"):
                    olhos.append(w)
        ev.to_mesh_clear()
    ys = [p.y for p in pts]
    comp_orig = max(ys) - min(ys)
    centro = sum(pts, Vector()) / len(pts)
    sinal = 1.0
    if olhos:
        sinal = 1.0 if (sum(olhos, Vector()) / len(olhos)).y > centro.y else -1.0
    base = 90.0 if sinal > 0 else -90.0

    # materiais
    cores = CORES_PEIXE.get(arquivo, {})
    for o in malhas:
        for i, m in enumerate(o.data.materials):
            if m is None:
                continue
            chave = next((k for k in cores if m.name.startswith(k)), None)
            if chave:
                cor = cores[chave]
                o.data.materials[i] = G.mat_toon(f"{nome}_{chave}", tinta or cor if chave != "Eyes" else cor)
            else:
                img = next((n.image for n in m.node_tree.nodes if n.type == "TEX_IMAGE"), None) if m.node_tree else None
                o.data.materials[i] = mat_textura(f"{nome}_{m.name}", img) if img else G.mat_toon(f"{nome}_{i}", "#8899AA")

    k = comprimento / comp_orig
    raiz["direcao"] = direcao  # para onde a cabeça aponta (graus em Z), usado para animar o nado
    raiz.scale = (k, k, k)
    raiz.rotation_euler = (0, 0, math.radians(direcao - base))
    raiz.location = Vector(local) - (Matrix.Rotation(math.radians(direcao - base), 3, "Z") @ (centro * k))
    for o in malhas:
        contorno(o, linha)

    if brilho and olhos:  # pontinho branco no olho: o modelo vem com olho todo preto
        loc = olhos  # capturados antes de escalar/girar a raiz: já estão no espaço local dela
        for lado in (-1, 1):
            grupo = [p for p in loc if (p.x > centro.x) == (lado > 0)]
            if not grupo:
                continue
            c = sum(grupo, Vector()) / len(grupo)
            r = max((p - c).length for p in grupo)
            pos = c + Vector((lado * r * 0.62, sinal * r * 0.3, r * 0.42))
            bm = bmesh.new()
            bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=r * 0.3)
            bmesh.ops.translate(bm, verts=bm.verts, vec=pos)
            objeto(f"{nome}_brilho_{lado}", malha_bm(f"{nome}_brilho_{lado}", bm),
                   G.mat_chapado(f"{nome}_brilho_{lado}", "#FFFFFF"), 0, pai=raiz)
    return raiz


# ------------------------------------------------------------------------------------------------ cena

def camera(alvo, distancia, lente, pitch, largura=1080, altura=1920, amostras=8, escala=100):
    """Câmera vertical olhando o alvo de frente (pitch em graus) e a luz toon presa nela (a luz anda com a câmera,
    então o sombreado não muda quando o plano muda). Também configura o EEVEE (ver base3d.config_render)."""
    sc = bpy.context.scene
    cd = bpy.data.cameras.new("camera")
    cd.lens, cd.sensor_fit, cd.sensor_height = lente, "VERTICAL", 36
    cam = bpy.data.objects.new("camera", cd)
    sc.collection.objects.link(cam)
    p = math.radians(pitch)
    cam.location = Vector(alvo) + Vector((0, -distancia * math.cos(p), distancia * math.sin(p)))
    cam.rotation_euler = (math.radians(90) - p, 0, 0)
    sc.camera = cam
    sol = bpy.data.lights.new("luz_toon", "SUN")
    sol.energy = math.pi
    sol.use_shadow = False
    so = bpy.data.objects.new("luz_toon", sol)
    sc.collection.objects.link(so)
    so.parent = cam
    d = Vector((0.55, -0.6, -1.0)).normalized()
    so.rotation_mode = "QUATERNION"
    so.rotation_quaternion = d.to_track_quat("-Z", "Y")
    G.config_render(largura, altura, amostras, escala)
    sc.world = bpy.data.worlds.new("mundo")
    return cam


def bloco_oceano(L, P, H, BASE, linha):
    """A fatia: três estratos de areia no corte, areia ondulada em cima, água em caixa de vidro, superfície."""
    x0, x1, y0, y1 = -L / 2, L / 2, -P / 2, P / 2
    camadas = [("estrato_fundo", -BASE, -BASE * 0.62, PALETA["areia_funda"]),
               ("estrato_meio", -BASE * 0.62, -BASE * 0.28, PALETA["areia_meio"])]
    for nome, za, zb, cor in camadas:
        objeto(nome, caixa(nome, x0, x1, y0, y1, za, zb), G.mat_toon(nome, cor), linha, suave=False)
    areia_topo("areia", x0, x1, y0, y1, -BASE * 0.28, BASE * 0.28 + 0.06, linha)
    seixos("seixo_f", ("y", y0, x0, x1), (-BASE * 0.95, -BASE * 0.35), 16, PALETA["seixo"], linha * 0.7)
    seixos("seixo_l", ("x", x1, y0, y1), (-BASE * 0.95, -BASE * 0.35), 10, PALETA["seixo"], linha * 0.7)
    seixos("concha_f", ("y", y0, x0, x1), (-BASE * 0.25, -0.02), 6, "#F7E7CE", linha * 0.7, tam=0.022)

    agua = objeto("agua", caixa("agua", x0, x1, y0, y1, -BASE - 0.01, H),
                  mat_agua_fundo(PALETA["agua"], 0.55), 0, suave=False)
    vidro = objeto("vidro", caixa("vidro", x0, x1, y0, y1, -BASE, H), G.mat_chapado("vidro", "#D9FFFA"), 0, suave=False)
    w = vidro.modifiers.new("arestas", "WIREFRAME")
    w.thickness, w.use_relative_offset, w.use_even_offset = 0.012, False, True

    bm = bmesh.new()  # superfície com ondinhas, vista por baixo
    bmesh.ops.create_grid(bm, x_segments=60, y_segments=40, size=1.0)
    for v in bm.verts:
        x, y = v.co.x * L / 2, v.co.y * P / 2
        v.co = Vector((x, y, H + 0.025 * math.sin(7 * x + 2 * y) + 0.015 * math.sin(11 * y - 3 * x)))
    objeto("superficie", malha_bm("superficie", bm), mat_transparente("superficie", "#7FE6DC", 0.55), 0, suave=True)
    bpy.data.materials["superficie"].use_backface_culling = False
    return agua


# ------------------------------------------------------------------------------------------------ cenários gerais
# O fundo do mar é só um dos cenários. Para qualquer outro assunto, monte o lugar do assunto com estas peças (ou com
# caixa, blob e G.tubo) e escolha o "fundo" do episodio.json que combina (casa, tempestade, ceu...).

def bloco_comodo(L, P, H, BASE, linha, parede="#F4D9B0", parede2="#E6BF8E", piso="#C98B55", piso2="#A86A3E",
                 rodape="#FFF8EC", ceu="#5B6E9A", janela=True):
    """Cômodo de casa em corte: piso de tábuas, parede do fundo com janela, parede da esquerda e rodapé.
    Volta {"base", "fundo", "lado"} e, com janela, "vidro"."""
    x0, x1, y0, y1 = -L / 2, L / 2, -P / 2, P / 2
    e = 0.06  # espessura das paredes (m)

    def peca(nome, lim, mat, esp):
        return objeto(nome, caixa(nome, *lim), mat, esp, suave=False)

    partes = {"base": peca("comodo_base", (x0, x1, y0, y1, -BASE, 0), G.mat_toon("comodo_base", piso2), linha)}
    tabuas = (G.mat_toon("comodo_tabua_a", piso2, "suave"), G.mat_toon("comodo_tabua_b", piso, "suave"))
    n_tabuas = 7
    for i in range(n_tabuas):
        ya, yb = y0 + P * i / n_tabuas, y0 + P * (i + 1) / n_tabuas - 0.006
        peca(f"comodo_tabua_{i}", (x0, x1, ya, yb, 0, 0.018), tabuas[i % 2], linha * 0.5)
    partes["fundo"] = peca("comodo_parede_fundo", (x0, x1, y1 - e, y1, 0, H),
                           G.mat_toon("comodo_parede_fundo", parede, "suave"), linha)
    partes["lado"] = peca("comodo_parede_lado", (x0, x0 + e, y0, y1, 0, H),
                          G.mat_toon("comodo_parede_lado", parede2, "suave"), linha)
    mat_rod = G.mat_toon("comodo_rodape", rodape, "suave")
    peca("comodo_rodape_fundo", (x0 + e, x1, y1 - e - 0.012, y1 - e, 0.018, 0.09), mat_rod, linha * 0.6)
    peca("comodo_rodape_lado", (x0 + e, x0 + e + 0.012, y0, y1 - e, 0.018, 0.09), mat_rod, linha * 0.6)
    if janela:
        jx0, jx1, jz0, jz1 = L * 0.08, L * 0.38, H * 0.42, H * 0.82
        yv, f = y1 - e - 0.004, 0.035
        partes["vidro"] = peca("comodo_janela_vidro", (jx0, jx1, yv - 0.004, yv, jz0, jz1),
                               G.mat_chapado("comodo_janela_vidro", ceu), 0)
        meio = (jx0 + jx1) / 2
        molduras = (("b", jx0 - f, jx1 + f, jz0 - f, jz0), ("c", jx0 - f, jx1 + f, jz1, jz1 + f),
                    ("e", jx0 - f, jx0, jz0, jz1), ("d", jx1, jx1 + f, jz0, jz1),
                    ("m", meio - f / 3, meio + f / 3, jz0, jz1))
        for n, a, b, c, d in molduras:
            peca(f"comodo_janela_{n}", (a, b, yv - 0.03, yv, c, d), mat_rod, linha * 0.6)
    return partes


def chao(nome, L, P, BASE, linha, topo="#7BCB5A", terra="#8A5A3C"):
    """Chão de grama (ou de outra cor) em bloco, com terra no corte. Volta a camada de cima."""
    x0, x1, y0, y1 = -L / 2, L / 2, -P / 2, P / 2
    objeto(f"{nome}_terra", caixa(f"{nome}_terra", x0, x1, y0, y1, -BASE, -0.04), G.mat_toon(f"{nome}_terra", terra),
           linha, suave=False)
    return objeto(f"{nome}_topo", caixa(f"{nome}_topo", x0, x1, y0, y1, -0.04, 0),
                  G.mat_toon(f"{nome}_topo", topo, "suave"), linha, suave=False)


def casinha(nome, local, escala=1.0, cor="#FFE3B0", telhado="#E5484D", porta="#8A5A3C", linha=0.005, pai=None):
    """Casinha cartoon (corpo com oitão, telhado de duas águas, porta, janela e chaminé), base em `local`, frente
    para -Y. Volta {"raiz", "corpo"}; a raiz é um vazio (girar e escalar nas chaves de animação)."""
    raiz = bpy.data.objects.new(nome, None)
    COL.objects.link(raiz)
    raiz.parent = pai
    raiz.location = local
    raiz.scale = (escala, escala, escala)
    l, p, h = 0.5, 0.4, 0.36
    cume = 0.17  # o oitão fica logo abaixo da face de baixo do telhado

    # corpo: prisma de cinco lados (paredes + oitão), para não abrir um vão triangular embaixo do telhado
    perfil = [(-l / 2, 0), (l / 2, 0), (l / 2, h), (0, h + cume), (-l / 2, h)]
    bm = bmesh.new()
    frente = [bm.verts.new((x, -p / 2, z)) for x, z in perfil]
    tras = [bm.verts.new((x, p / 2, z)) for x, z in perfil]
    bm.faces.new(frente)
    bm.faces.new(tras[::-1])
    for i in range(5):
        j = (i + 1) % 5
        bm.faces.new((frente[i], tras[i], tras[j], frente[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    corpo = objeto(f"{nome}_corpo", malha_bm(f"{nome}_corpo", bm), G.mat_toon(f"{nome}_corpo", cor), linha,
                   suave=False, pai=raiz)

    aba = math.hypot(l / 2 + 0.04, 0.2)
    ang = math.atan2(0.2, l / 2 + 0.04)
    mat_t = G.mat_toon(f"{nome}_telhado", telhado)
    for s in (-1, 1):
        n = f"{nome}_telhado_{s}"
        m = objeto(n, caixa(n, -aba / 2, aba / 2, -p / 2 - 0.04, p / 2 + 0.04, -0.015, 0.015), mat_t, linha,
                   suave=False, pai=raiz)
        m.location = (s * (l / 4 + 0.01), 0, h + 0.1)
        m.rotation_euler = (0, s * ang, 0)  # beiral para fora e para baixo, cume no meio
    n = f"{nome}_chamine"
    objeto(n, caixa(n, 0.1, 0.17, -0.05, 0.02, h + 0.05, h + 0.3), G.mat_toon(n, "#B9774A"), linha, suave=False,
           pai=raiz)
    n = f"{nome}_porta"
    objeto(n, caixa(n, -0.06, 0.06, -p / 2 - 0.012, -p / 2, 0, 0.2), G.mat_toon(n, porta), linha * 0.7, suave=False,
           pai=raiz)
    n = f"{nome}_janela"
    objeto(n, caixa(n, 0.1, 0.2, -p / 2 - 0.012, -p / 2, 0.16, 0.26), G.mat_chapado(n, "#FFE45E"), linha * 0.7,
           suave=False, pai=raiz)
    return {"raiz": raiz, "corpo": corpo}


def nuvem(nome, centro, tam=0.3, cor="#FFFFFF", cor2=None, semente=1, linha=0.004, pai=None):
    """Nuvem fofa de bolhas (clara no céu, escura na tempestade). `cor2`: cor de baixo, em degradê até `cor`."""
    rnd = random.Random(semente)
    cx, cy, cz = centro
    els = []
    for i in range(7):
        u = i / 6 - 0.5
        p = (cx + u * tam * 1.6, cy + (rnd.random() - 0.5) * tam * 0.3,
             cz + (0.25 - abs(u)) * tam * 0.8 + rnd.random() * tam * 0.15)
        els.append((p, tam * (0.38 + 0.18 * rnd.random())))
    me = blob(nome, els, resolucao=max(0.006, tam * 0.03))
    if cor2:
        mat = mat_gradiente(nome, cor2, cor, cz - tam * 0.3, cz + tam * 0.4, "suave")
    else:
        mat = G.mat_toon(nome, cor, "suave")
    return objeto(nome, me, mat, linha, pai=pai)
