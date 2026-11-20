# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Cena do exemplo "Isso não é uma água-viva": plano contínuo dentro de uma fatia de oceano, animado pela narração.

Roda dentro do Blender (o rodar.py chama sozinho):

    blender -b --factory-startup --python-exit-code 1 -P cena.py -- --tempos T.json --saida PASTA
            [--stills 0.5,5.0] [--leve] [--amostras 8] [--ate SEGUNDOS]

Lê o tempos.json (palavra a palavra, do alinhar.py do kit) e o episodio.json. Grava em PASTA:
- quadros/q_0001.png ... (RGBA, fundo transparente; o compor.py põe o fundo, o texto e o CTA);
- etiquetas.json (posição na tela de cada rótulo, quadro a quadro);
- render.json (tempo de render medido) e cena.blend (para abrir e mexer no Blender).
Com --stills renderiza só os instantes pedidos, em stills/still_<t>.png, para conferir antes do render longo.

Não há personagem humano: o "boneco" é o próprio objeto. Cada parte da caravela tem olhos e quica na palavra
dela (gag de "objeto vivo"), e o peixe-palhaço dá meia-volta quando chega perto dos tentáculos.
"""
import json
import math
import sys
import time
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "motor"))
import bichos3d as B  # noqa: E402
import kit3d as K  # noqa: E402
from kit3d import G, PALETA  # noqa: E402
from tempos import Tempos  # noqa: E402

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def arg(nome, padrao=None):
    return ARGS[ARGS.index(nome) + 1] if nome in ARGS else padrao


EP = json.loads((AQUI / "episodio.json").read_text(encoding="utf-8"))
TEMPOS = Tempos(arg("--tempos", AQUI / "audio" / "tempos.json"))
SAIDA = Path(arg("--saida", AQUI / "saida"))
FPS = int(arg("--fps", 30))  # vem do config (render.fps): 60 na GPU, 30 na CPU
L, P, H, BASE = 1.7, 1.2, 2.2, 0.55   # largura, profundidade, altura da água e espessura da areia da fatia (m)
LN = 0.0075                           # espessura do contorno (m)
FALA_FIM = TEMPOS.fim
DURACAO = FALA_FIM + 0.4 + EP["cta_segundos"]

q = TEMPOS.quando
T = {  # marcos da narração
    "caravela": q("caravela"),
    "condominio": q("condomínio"),
    "boia": q("boia"),
    "caca": q("caça"),
    "come": q("come"),
    "namora": q("namora"),
    "sozinho": q("sozinho"),
    "sobrevive": q("sobrevive"),
}

# Câmera: (marco, alvo_x, alvo_z, distância, pitch). Em cada marco ela sai do plano anterior e chega ao novo em
# 1,6 s. O último plano repete o primeiro: o fim do vídeo emenda no começo quando a rede repete (replay).
CAMERA = [
    (0.0, 0.0, 1.7, 5.2, 11),
    (T["caravela"], 0.0, 1.85, 3.3, 8),
    (T["condominio"], 0.0, 2.1, 2.5, 7),
    (T["sozinho"], 0.0, 1.85, 3.3, 8),
    (FALA_FIM, 0.0, 1.7, 5.2, 11),
]


def camera_em(t):
    k = max(i for i, m in enumerate(CAMERA) if m[0] <= t)
    if k == 0:
        return CAMERA[0][1:]
    u = G.suave(CAMERA[k][0], CAMERA[k][0] + 1.6, t)
    return [a + (b - a) * u for a, b in zip(CAMERA[k - 1][1:], CAMERA[k][1:])]


def volta(u, s=1.7):
    """Ease com passada (back-out): a peça passa um pouco do ponto e volta."""
    u = max(0.0, min(1.0, u)) - 1
    return 1 + u * u * ((s + 1) * u + s)


def pulo(t, t0, dur=0.32, alto=1.0):
    """0 -> pico -> 0 em `dur` segundos: o quique de uma parte no ritmo da fala."""
    if t < t0 or t > t0 + dur:
        return 0.0
    return alto * math.sin(math.pi * (t - t0) / dur)


def chave(ob, f, **props):
    for k, v in props.items():
        setattr(ob, k, v)
        ob.keyframe_insert(k, frame=f)


def coracao(nome, linha=0.004):
    els = [((-0.03, 0, 0.02), 0.045), ((0.03, 0, 0.02), 0.045)]
    els += K.cadeia((0, 0, -0.01), (0, 0, -0.07), 0.04, 0.012, passo=0.3)
    me = K.blob(nome, [(p, r, (1.0, 0.55, 1.0)) for p, r, *_ in els], resolucao=0.006)
    return K.objeto(nome, me, G.mat_toon(nome, "#FF5C8A"), linha)


# ------------------------------------------------------------------------------------------------ montagem

def montar(amostras, escala):
    K.bloco_oceano(L, P, H, BASE, LN)
    mundo = bpy.data.objects.new("mundo", None)
    K.COL.objects.link(mundo)
    K.feixe("feixe_1", (-0.35, 0.25, H), 0.0, 0.16, 0.34, 0.12)
    K.feixe("feixe_2", (0.35, 0.1, H), 0.4, 0.1, 0.22, 0.09)
    algas = []
    for nome, b, alt, n, fase in (("alga_1", (-0.62, 0.38, 0.03), 1.2, 6, 0.0), ("alga_2", (0.68, 0.45, 0.03), 0.8, 4, 0.6)):
        ob = K.alga(nome, b, alt, n, LN, fase=fase)
        ob.data.transform(Matrix.Translation(-Vector(b)))  # pivô na base, para balançar a partir do chão
        ob.location = b
        algas.append(ob)
    K.coral("coral_1", (0.6, -0.3, 0.04), 0.52, PALETA["coral"], PALETA["coral_ponta"], LN)
    K.coral("coral_2", (0.3, 0.38, 0.04), 0.4, PALETA["coral2"], PALETA["coral2_ponta"], LN)
    K.pedra("pedra_1", (0.55, 0.18, 0.05), (0.2, 0.16, 0.16), PALETA["rocha"], LN)
    K.estrela("estrela_1", (-0.25, -0.42, 0.09), 0.08, LN, giro=0.4)
    K.anemona("anemona_1", (-0.55, -0.2, 0.05), 0.1, LN)
    ch = B.chinelo("chinelo_1", (0.38, -P / 2 + 0.012, -BASE * 0.45), linha=0.004)  # achado no corte da areia
    ch.rotation_euler = (math.radians(90), math.radians(-18), 0)
    ch.scale = (0.9, 0.9, 0.9)

    cv = B.caravela("caravela_1", (0.0, -0.05, H - 0.03), escala=1.35)
    peixe = K.peixe("palhaco_1", "palhaco", 0.3, (0.62, -0.25, 1.35), 180, linha=0.005)
    baiacu = K.peixe("baiacu_1", "baiacu", 0.24, (-0.5, 0.3, 0.9), 15, linha=0.004)
    cardume = [K.peixe(f"cardume_{i}", "peixe", 0.11, (-0.55 + 0.08 * i, 0.4, 1.45 + 0.07 * (i % 2)), 10,
                       linha=0.003, brilho=False) for i in range(3)]
    cor = coracao("coracao_1")
    for o in list(bpy.context.scene.objects):
        if o.parent is None and o is not mundo:
            o.parent = mundo
    cam = K.camera((0.0, 0.0, 1.7), 5.2, 40, 11, amostras=amostras, escala=escala)
    return dict(mundo=mundo, algas=algas, cv=cv, peixe=peixe, baiacu=baiacu, cardume=cardume, coracao=cor, cam=cam)


# ------------------------------------------------------------------------------------------------ animação

def animar(c):
    sc = bpy.context.scene
    sc.render.fps = FPS
    n = int(round(DURACAO * FPS))
    sc.frame_start, sc.frame_end = 1, n
    for a in bpy.data.actions:  # o nado dos peixes CC0 em loop
        for fc in G.fcurves(a):
            if not any(m.type == "CYCLES" for m in fc.modifiers):
                fc.modifiers.new("CYCLES")
    sup = bpy.data.objects["superficie"]
    cv = c["cv"]
    crista = bpy.data.objects["caravela_1_crista_m"]
    p0 = c["peixe"].location.copy()
    rz0 = c["peixe"].rotation_euler.z
    b0 = c["baiacu"].location.copy()
    card0 = [o.location.copy() for o in c["cardume"]]

    for f in range(1, n + 1):
        t = (f - 1) / FPS
        ax, az, dist, pitch = camera_em(t)
        p = math.radians(pitch)
        chave(c["cam"], f, location=(ax, -dist * math.cos(p), az + dist * math.sin(p)),
              rotation_euler=(math.radians(90) - p, 0, 0))
        chave(c["mundo"], f, rotation_euler=(0, 0, math.radians(-24 + 4 * math.sin(t / 9))))
        chave(sup, f, location=(0, 0, 0.004 * math.sin(2.1 * t)))
        for i, a in enumerate(c["algas"]):
            chave(a, f, rotation_euler=(math.radians(3.5 * math.sin(1.3 * t + i)),
                                        math.radians(4.5 * math.sin(0.9 * t + 1.7 * i)), 0))

        # desmonta em "condomínio"; em "sozinho" a digestão se afasta e murcha; em "sobrevive" tudo encaixa de volta
        abre = volta((t - T["condominio"]) / 0.6) * (1 - G.suave(T["sobrevive"] - 0.1, T["sobrevive"] + 0.35, t))
        sozinho = G.suave(T["sozinho"], T["sozinho"] + 0.5, t) * (1 - G.suave(T["sobrevive"] - 0.1, T["sobrevive"] + 0.35, t))
        boia_z = H - 0.03 + 0.02 * math.sin(1.6 * t)
        chave(cv["raiz"], f, location=(0.0, -0.05, boia_z), rotation_euler=(0, math.radians(2 * math.sin(1.1 * t)), 0))
        ritmo = {k: pulo(t, T[k]) for k in ("boia", "caca", "come", "namora")}
        chave(cv["boia"], f, location=(0, 0, 0.16 * abre + 0.06 * ritmo["boia"]),
              rotation_euler=(0, 0, math.radians(8 * abre)))
        chave(cv["cacadores"], f, location=(0, 0, -0.08 * abre - 0.04 * ritmo["caca"]), scale=(1, 1, 0.6))
        chave(cv["digestao"], f, location=(0.34 * abre + 0.08 * sozinho, 0, -0.04 * abre + 0.05 * ritmo["come"] - 0.05 * sozinho),
              rotation_euler=(0, math.radians(-20 * sozinho), math.radians(25 * abre)),
              scale=(1 - 0.25 * sozinho,) * 3)
        chave(cv["filhotes"], f, location=(-0.36 * abre, 0, -0.04 * abre + 0.05 * ritmo["namora"]),
              rotation_euler=(0, 0, math.radians(-25 * abre)))
        chave(crista, f, scale=(1, 1, 1 + 0.25 * ritmo["boia"]))

        # coração no "namora"
        u = (t - T["namora"]) / 1.2
        vis = 0 < u < 1
        chave(c["coracao"], f, location=(-0.5, -0.12, (boia_z - 0.05 + 0.3 * u) if vis else -5.0),
              scale=(1.6 * volta(u * 3),) * 3 if vis else (0.001,) * 3)

        # micro-gag: o peixe-palhaço chega perto dos tentáculos e, no "caça", dá meia-volta e foge
        ida = G.suave(T["condominio"], T["caca"], t)
        if t < T["caca"]:
            pos, rot = p0 + Vector((-0.38 * ida, 0, 0.02 * math.sin(2 * t))), 0.0
        else:
            k = G.suave(T["caca"], T["caca"] + 0.25, t)
            pos = p0 + Vector((-0.38 + 0.9 * G.suave(T["caca"] + 0.15, T["caca"] + 1.4, t), 0, 0.02 * math.sin(2 * t)))
            rot = math.pi * k
        chave(c["peixe"], f, location=pos, rotation_euler=(0, 0, rz0 + rot))
        chave(c["baiacu"], f, location=b0 + Vector((0.12 * math.sin(0.4 * t), 0, 0.03 * math.sin(1.3 * t))))
        for i, o in enumerate(c["cardume"]):
            chave(o, f, location=card0[i] + Vector((0.25 * math.sin(0.3 * t + i * 0.3), 0, 0.02 * math.sin(2 * t + i))))


def ancoras(cam, c):
    """Posição na tela (0..1, y para baixo) de cada rótulo, quadro a quadro."""
    sc = bpy.context.scene
    alvos = {
        "BOIA": (c["cv"]["boia"], (0.0, 0.0, 0.2)),
        "CAÇADORES": (c["cv"]["cacadores"], (0.0, 0.0, -0.7)),
        "DIGESTÃO": (c["cv"]["digestao"], (0.0, 0.0, -0.12)),
        "FILHOTES": (c["cv"]["filhotes"], (-0.15, 0.0, -0.1)),
    }
    out = {}
    for f in range(sc.frame_start, sc.frame_end + 1):
        sc.frame_set(f)
        out[f] = {}
        for rotulo, (ob, ponto) in alvos.items():
            v = world_to_camera_view(sc, cam, ob.matrix_world @ Vector(ponto))
            out[f][rotulo] = (round(v.x, 4), round(1 - v.y, 4))
    return out


def main():
    leve = "--leve" in ARGS
    amostras = int(arg("--amostras", 4 if leve else 8))
    escala = 50 if leve else 100
    SAIDA.mkdir(parents=True, exist_ok=True)
    K.iniciar()
    t0 = time.time()
    c = montar(amostras, escala)
    animar(c)
    sc = bpy.context.scene
    print(f"montagem {time.time() - t0:.1f} s, duração {DURACAO:.2f} s, {sc.frame_end} quadros", flush=True)

    if "--stills" in ARGS:
        (SAIDA / "stills").mkdir(exist_ok=True)
        for ts in arg("--stills").split(","):
            sc.frame_set(int(float(ts) * FPS) + 1)
            sc.render.filepath = str(SAIDA / "stills" / f"still_{float(ts):05.2f}.png")
            bpy.ops.render.render(write_still=True)
        return

    (SAIDA / "etiquetas.json").write_text(json.dumps(ancoras(c["cam"], c)), encoding="utf-8")
    if "--ate" in ARGS:  # só os primeiros segundos (teste de velocidade da placa)
        sc.frame_end = min(sc.frame_end, int(float(arg("--ate")) * FPS))
    pasta = SAIDA / "quadros"
    pasta.mkdir(exist_ok=True)
    for velho in pasta.glob("q_*.png"):  # render anterior mais longo deixaria quadros sobrando no fim
        velho.unlink()
    sc.render.filepath = str(pasta / "q_")
    t0 = time.time()
    bpy.ops.render.render(animation=True)
    dt = time.time() - t0
    info = {"quadros": sc.frame_end, "segundos": round(dt, 1), "s_por_quadro": round(dt / sc.frame_end, 3),
            "duracao_video": round(DURACAO, 2), "amostras": amostras, "escala": escala,
            "blender": bpy.app.version_string}
    try:
        import gpu
        info["placa"] = gpu.platform.renderer_get()
    except Exception:
        pass
    (SAIDA / "render.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"RENDER_OK {dt:.1f} s = {dt / sc.frame_end:.2f} s/quadro ({info.get('placa', '?')})", flush=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(SAIDA / "cena.blend"), compress=True)


main()
