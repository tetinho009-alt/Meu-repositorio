# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Clipes do boneco 3D (1080x1920, 30 fps, EEVEE na GPU). Roda dentro do Blender (o jeito fácil é o
`boneco3d/rodar.py`):

    blender -b --factory-startup -P boneco3d/clipe.py -- <nome> <teste|gag|pose_gag|fala> [--rapido] [--saida v.mp4]
                                                        [--tempos tempos.json --audio voz.mp3 --ate 8]

teste    : 3 s, plano médio: olha para a câmera, vira a cabeça, fala (visemas A, E, O, M, I) e pisca.
gag      : 6 s, corpo inteiro: mexe no celular, sério; no meio, uma gag discreta de 1,6 s.
pose_gag : um quadro só da pose do celular (para conferência).
fala     : o boneco fala a narração ou a fala dele: boca pelo tempo de cada palavra (tempos.json do alinhar.py ou o
           .tempos.json do falas.py), piscada irregular, cabeça viva; o áudio entra no mp4.
--rapido : 8 amostras de antialias em vez de 32 (o toon não usa sombra, então não há sombra suave a cortar).
Encoder: h264_nvenc (NVIDIA) e, se não houver, libx264. Imprime o tempo de render por segundo de vídeo.
"""
import json
import math
import shutil
import subprocess
import sys
import time
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent))
import gerar as G  # noqa: E402
from config import ffmpeg  # noqa: E402


def piscada(t, t0, dur=0.16):
    """0 -> 1 -> 0 em `dur` segundos a partir de t0."""
    if t < t0 or t > t0 + dur:
        return 0.0
    u = (t - t0) / dur
    return min(1.0, 2.2 * (1 - abs(2 * u - 1)))


def janela(t, a, b, c, d):
    """Sobe de a a b, fica em 1 até c, desce até d (suave)."""
    return G.suave(a, b, t) * (1 - G.suave(c, d, t))


# ------------------------------------------------------------------ clipe de teste (rosto)

FALA = [(1.60, "A"), (1.74, "E"), (1.88, "O"), (2.03, "M"), (2.12, "A"), (2.26, "I"), (2.40, "O"), (2.52, "R")]


def base_teste(t):
    vira = janela(t, 0.70, 1.00, 1.25, 1.55)
    pose = {
        "cabeca": {"rz": 32 * vira, "rx": -3 * vira + 2.5 * math.sin(2 * math.pi * 3.0 * t) * janela(t, 1.6, 1.7, 2.45, 2.6),
                   "ry": 6 * G.suave(2.6, 2.85, t)},
        "coluna": {"rx": 1.0 * math.sin(2 * math.pi * 0.35 * t)},
        "olhar_x": 0.85 * janela(t, 0.62, 0.80, 1.25, 1.42),
        "piscar_e": max(piscada(t, 0.42), piscada(t, 2.20)),
        "piscar_d": max(piscada(t, 0.42), piscada(t, 2.20)),
        "sobrancelha_dy": -6 * janela(t, 1.55, 1.65, 2.45, 2.6),
        "visema": "R",
    }
    for t0, v in FALA:
        if t >= t0:
            pose["visema"] = v
    if t >= 2.62:
        pose["visema"] = "feliz"
    return pose


# ------------------------------------------------------------------ clipe da gag (celular)

POSE_CELULAR = {
    "braco_d": {"rx": -32, "rz": -14},
    "antebraco_d": {"rx": -92, "rz": -40},
    "mao_d": {"rx": -10, "rz": -10},
    "braco_e": {"ry": 3},
    "cabeca": {"rx": 17, "ry": -3},
}


def base_gag(t):
    pose = {k: dict(v) for k, v in POSE_CELULAR.items()}
    rola = math.sin(2 * math.pi * 1.4 * t) * (1 - janela(t, 2.0, 2.3, 3.8, 4.1) * 0.6)  # polegar rolando a tela
    pose["mao_d"]["rx"] += 5 * rola
    pose["antebraco_d"]["rx"] += 1.5 * rola
    pose["coluna"] = {"rx": 1.2 * math.sin(2 * math.pi * 0.3 * t)}
    pose["cabeca"]["rx"] += 1.0 * math.sin(2 * math.pi * 0.3 * t + 0.6)
    pose["olhar_y"] = 0.9
    pose["olhar_x"] = 0.2
    p = max(piscada(t, 1.10), piscada(t, 4.70))
    pose["piscar_e"] = pose["piscar_d"] = p
    pose["visema"] = "M"
    return pose


def celular(rig, col, mt_contorno):
    """Celular preso ao osso da mão direita (da tela), com a tela virada para o rosto."""
    aneis = []
    for k, y in ((0.86, -0.005), (1.0, -0.004), (1.0, 0.004), (0.86, 0.005)):
        aneis.append([Vector((0.036 * k * a, y, 0.068 * k * b)) for a, b in
                      (G._superelipse(1, 1, 2 * math.pi * i / 40, 6.0) for i in range(40))])
    corpo = G._bm_de(*G.loft(aneis, (0, -0.005, 0), (0, 0.005, 0)))
    import bmesh
    bmesh.ops.recalc_face_normals(corpo, faces=corpo.faces)
    me = bpy.data.meshes.new("celular")
    corpo.to_mesh(me)
    corpo.free()
    me.materials.append(G.mat_toon("celular", "#25242C", "roupa"))
    me.materials.append(mt_contorno)
    ob = bpy.data.objects.new("celular", me)
    col.objects.link(ob)
    sc = ob.modifiers.new("contorno", "SOLIDIFY")
    sc.thickness, sc.offset, sc.use_flip_normals, sc.use_rim, sc.material_offset = 0.007, 1.0, True, False, 1
    # tela (lado +Y local = virado para o rosto)
    tv, tf = G.grade(lambda u, v: Vector((0.031 * (2 * u - 1), 0.0056, 0.061 * (2 * v - 1))), 1, 1)
    mt = bpy.data.meshes.new("tela")
    mt.from_pydata([tuple(v) for v in tv], [], tf)
    mt.materials.append(G.mat_chapado("tela", "#CFE2FF"))
    tela = bpy.data.objects.new("tela", mt)
    col.objects.link(tela)
    tela.parent = ob

    bpy.context.view_layer.update()
    pb = rig.pose.bones["mao_d"]
    mao = rig.matrix_world @ pb.matrix
    pos = mao @ Vector((0, 0.045, 0))  # um pouco além do punho, na palma
    cabeca = rig.matrix_world @ rig.pose.bones["cabeca"].matrix @ Vector((0, 0.2, 0))
    n = (cabeca - pos).normalized()
    cima = (Vector((0, 0, 1)) - n * n.z).normalized()
    x = n.cross(cima).normalized()
    m = Matrix((x, n, cima)).transposed().to_4x4()
    m.translation = pos + n * 0.0 - x * 0.006
    ob.parent = rig
    ob.parent_type = "BONE"
    ob.parent_bone = "mao_d"
    bpy.context.view_layer.update()
    ob.matrix_world = m
    return ob


# ------------------------------------------------------------------ clipe de fala (tempo de palavra)

# Mesma regra da boca do 2D (maquina/rig.visema): a letra da palavra no instante decide o visema; fecha entre palavras.
VISEMA_POR_LETRA = {"a": "A", "á": "A", "ã": "A", "â": "A", "e": "E", "é": "E", "ê": "E", "i": "I", "í": "I",
                    "o": "O", "ó": "O", "ô": "O", "õ": "O", "u": "U", "ú": "U", "m": "M", "b": "M", "p": "M",
                    "f": "F", "v": "F"}


def visema(t, palavras):
    for ini, fim, p in palavras:
        if ini <= t < fim:
            letras = [ch for ch in p.lower() if ch.isalpha()] or ["a"]
            k = min(len(letras) - 1, int((t - ini) / max(fim - ini, 1e-3) * len(letras)))
            return VISEMA_POR_LETRA.get(letras[k], "E")
    return "R"


def base_fala(palavras, duracao, semente=7):
    """Pose por instante: boca pela fala, piscada irregular (2 a 5 s), cabeça que acompanha a fala, respiração."""
    import random
    rnd, t, piscas = random.Random(semente), 0.8, []
    while t < duracao:
        piscas.append(t)
        t += rnd.uniform(2.0, 5.0)
    falando = [(ini, fim) for ini, fim, _ in palavras]

    def pose(t):
        fala = any(a - 0.1 <= t < b + 0.15 for a, b in falando)
        pergunta = any(a <= t < b + 0.6 and p.endswith("?") for a, b, p in palavras)
        p = max((piscada(t, b) for b in piscas), default=0.0)
        return {
            "cabeca": {"rx": (1.6 * math.sin(2 * math.pi * 2.3 * t) if fala else 0.0) - 2.0 * pergunta,
                       "rz": 6 * math.sin(2 * math.pi * 0.21 * t), "ry": 3 * pergunta},
            "coluna": {"rx": 1.0 * math.sin(2 * math.pi * 0.3 * t)},
            "olhar_x": 0.15 * math.sin(2 * math.pi * 0.13 * t), "olhar_y": 0.0,
            "piscar_e": p, "piscar_d": p,
            "sobrancelha_dy": -5 * pergunta,
            "visema": visema(t, palavras),
        }
    return pose


def ler_palavras(arq):
    dados = json.loads(Path(arq).read_text(encoding="utf-8"))
    return [(float(w["ini"]), float(w["fim"]), w["palavra"]) for w in dados]


# ------------------------------------------------------------------ render

def renderizar(pasta, saida_mp4, fps=30, audio=None):
    sc = bpy.context.scene
    if pasta.exists():
        shutil.rmtree(pasta)
    pasta.mkdir(parents=True)
    sc.render.filepath = str(pasta) + "/"
    sc.render.image_settings.file_format = "PNG"
    t = time.time()
    bpy.ops.render.render(animation=True)
    dt = time.time() - t
    n = sc.frame_end - sc.frame_start + 1
    base = [ffmpeg(), "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(pasta / "%04d.png")]
    if audio:
        base += ["-i", str(audio), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-shortest"]
    fim = ["-pix_fmt", "yuv420p", "-movflags", "+faststart", str(saida_mp4)]
    t2 = time.time()
    if subprocess.run(base + ["-c:v", "h264_nvenc", "-preset", "p5", "-cq", "19"] + fim).returncode:
        print("sem NVENC: usando libx264", flush=True)  # sem placa NVIDIA o encoder de CPU resolve
        subprocess.run(base + ["-c:v", "libx264", "-crf", "18", "-preset", "medium"] + fim, check=True)
    dt2 = time.time() - t2
    seg = n / fps
    print(f"RENDER {n} quadros em {dt:.1f} s ({dt / n:.3f} s/quadro) = {dt / seg:.2f} s de render por s de vídeo; "
          f"ffmpeg nvenc {dt2:.1f} s -> {saida_mp4}")
    return dt, n


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    nome, modo = args[0], args[1]
    rapido = "--rapido" in args

    def opcao(chave):
        return args[args.index(chave) + 1] if chave in args else None

    dest = G.pasta_saida(nome, opcao("--pasta"))
    dest.mkdir(parents=True, exist_ok=True)
    saida = Path(opcao("--saida")) if opcao("--saida") else dest / f"{nome}3d_{modo}.mp4"
    t0 = time.time()
    G.limpar()
    rig = G.construir(nome, dest)
    audio = None
    if modo == "teste":
        G.cena(alvo_z=0.66, meia_altura=0.40, rapido=rapido)
        G.animar(rig, base_teste, 3.0)
    elif modo in ("gag", "pose_gag"):
        G.cena(alvo_z=0.53, meia_altura=0.64, rapido=rapido)
        G.aplicar_pose(rig, base_gag(0.0))
        celular(rig, rig.users_collection[0], bpy.data.materials["contorno"])
        if modo == "gag":
            G.animar(rig, base_gag, 6.0, camadas=[G.gag("rebolado", 2.2, 1.6, 1.0)])
    elif modo == "fala":
        if not opcao("--tempos"):
            raise SystemExit("modo fala precisa de --tempos (e --audio para o som)")
        palavras = ler_palavras(opcao("--tempos"))
        duracao = palavras[-1][1] + 0.6
        if opcao("--ate"):
            duracao = min(duracao, float(opcao("--ate")))
        audio = opcao("--audio")
        G.cena(alvo_z=0.66, meia_altura=0.40, rapido=rapido)
        G.animar(rig, base_fala(palavras, duracao), duracao)
    else:
        raise SystemExit(f"modo desconhecido: {modo} (teste, gag, pose_gag, fala)")
    print(f"MONTAGEM {time.time() - t0:.1f} s")
    if modo == "pose_gag":
        sc = bpy.context.scene
        sc.render.filepath = str(dest / "pose_gag.png")
        bpy.ops.render.render(write_still=True)
        return
    bpy.ops.wm.save_as_mainfile(filepath=str(dest / f"{nome}_{modo}.blend"), compress=True)
    renderizar(dest / "quadros" / (modo + ("_rapido" if rapido else "")), saida, audio=audio)


if __name__ == "__main__":
    main()
