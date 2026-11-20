# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Vídeo longo horizontal (opcional) para o YouTube: emenda as partes já decididas de uma série num "filme" de 5 a
15 min, em 1920x1080, com abertura própria, um único fim (o CTA da rede) e capítulos na descrição.

As partes entram já renderizadas em 16:9, sem a tela de voto nem o CTA (ver `metodo/video-longo.md`). Vídeo vertical
é recusado: o longo é a mesma cena com a câmera recomposta, não o vertical recortado.

Uso:
    python filme_longo.py --serie "A Casa da Estrada" --saida trabalho/longo \\
        --parte trabalho/p1_16x9.mp4 "Noite 1" --parte trabalho/p2_16x9.mp4 "Noite 2" --parte trabalho/p3_16x9.mp4 "Noite 3" \\
        [--abertura auto|<abertura.mp4>] [--subtitulo "As três primeiras noites"] [--fim <cta_e_cauda.mp4>] \\
        [--capa-em 95.0] [--capa-texto "ELE VOLTOU"] [--link https://seu.site/?utm_source=youtube&utm_medium=descricao]

--abertura auto  cartão de 5 s sem voz (título da série e subtítulo), a mesma regra da abertura do formato sério.
--fim            o único fim do filme: o CTA da rede, já em 1920x1080 (sem cauda de produto: a Meta rebaixa).
--capa-em        segundo do filme de onde sai a imagem da capa 1280x720 (padrão: meio da primeira parte).
Saída: <saida>/<serie>_longo.mp4, capa_youtube.jpg e descricao.md (título, descrição com capítulos e link).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(KIT))

from PIL import Image, ImageDraw, ImageFilter, ImageFont  # noqa: E402

from config import CFG, cor, ffmpeg, ffprobe, fonte_arquivo  # noqa: E402
from maquina import slug  # noqa: E402
from maquina.motor import args_encoder, escolher_encoder  # noqa: E402

W, H = 1920, 1080
FPS = int(CFG["render"]["fps"])
A = CFG["audio"]


def info(video):
    out = subprocess.run([ffprobe(), "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                          "-show_entries", "format=duration", "-of", "json", str(video)],
                         capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    s = j["streams"][0]
    return int(s["width"]), int(s["height"]), float(j["format"]["duration"])


def abertura_auto(serie, subtitulo, destino, dur=5.0):
    """Cartão de abertura sem voz: papel escuro, título grande e subtítulo, com fade de entrada e de saída."""
    img = Image.new("RGB", (W, H), (14, 12, 12))
    vinheta = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vinheta).ellipse((-200, -260, W + 200, H + 260), fill=255)
    img = Image.composite(Image.new("RGB", (W, H), (38, 32, 28)), img, vinheta.filter(ImageFilter.GaussianBlur(220)))
    d = ImageDraw.Draw(img)
    titulo = serie.upper()
    tam = 170
    while tam > 60 and ImageFont.truetype(str(fonte_arquivo("titulo")), tam).getlength(titulo) > W - 300:
        tam -= 6
    ft = ImageFont.truetype(str(fonte_arquivo("titulo")), tam)
    d.text(((W - ft.getlength(titulo)) / 2, H / 2 - tam * 0.75), titulo, font=ft, fill=(232, 222, 198))
    if subtitulo:
        fs = ImageFont.truetype(str(fonte_arquivo("texto")), 46)
        d.text(((W - fs.getlength(subtitulo)) / 2, H / 2 + tam * 0.45), subtitulo, font=fs, fill=(176, 164, 140))
    png = destino.with_suffix(".png")
    img.save(png)
    subprocess.run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-i", str(png),
                    "-f", "lavfi", "-i", f"anullsrc=r={A['taxa']}:cl=stereo", "-t", f"{dur}",
                    "-vf", f"fade=in:st=0:d=0.6,fade=out:st={dur - 0.6}:d=0.6,format=yuv420p",
                    "-c:v", "libx264", "-crf", "18", "-c:a", "aac", "-shortest", str(destino)], check=True)
    png.unlink()
    return destino


def emendar(trechos, saida, encoder):
    """Concatena tudo num arquivo só, normalizando tamanho, taxa de quadros e áudio de cada trecho."""
    cmd = [ffmpeg(), "-hide_banner", "-loglevel", "error", "-y"]
    for t in trechos:
        cmd += ["-i", str(t)]
    filtros = []
    for i in range(len(trechos)):
        filtros.append(f"[{i}:v]scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,"
                       f"setsar=1,fps={FPS},format=yuv420p[v{i}]")
        filtros.append(f"[{i}:a]aresample={A['taxa']},aformat=channel_layouts=stereo[a{i}]")
    pares = "".join(f"[v{i}][a{i}]" for i in range(len(trechos)))
    filtros.append(f"{pares}concat=n={len(trechos)}:v=1:a=1[v][a0]")
    filtros.append(f"[a0]loudnorm=I={A['lufs']}:TP={A['pico_dbtp']}:LRA={A['lra']}[a]")
    cmd += ["-filter_complex", ";".join(filtros), "-map", "[v]", "-map", "[a]", *args_encoder(encoder),
            "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", str(A["bitrate_aac"]),
            "-movflags", "+faststart", str(saida)]
    subprocess.run(cmd, check=True)


def capa(video, em, serie, texto, destino):
    """Capa 1280x720: o quadro escolhido do filme, escurecido embaixo, com o texto curto e o nome da série."""
    quadro = destino.with_name("_quadro_capa.png")
    subprocess.run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{em:.2f}", "-i", str(video),
                    "-frames:v", "1", str(quadro)], check=True)
    img = Image.open(quadro).convert("RGB").resize((1280, 720), Image.LANCZOS)
    quadro.unlink()
    grad = Image.linear_gradient("L").resize((1280, 720)).point(lambda v: int(max(0, (v - 110) * 1.4)))
    img = Image.composite(Image.new("RGB", (1280, 720), (8, 6, 6)), img, grad)
    d = ImageDraw.Draw(img)
    arq = str(fonte_arquivo("titulo"))
    grande = (texto or serie).upper()
    tam = 150
    while tam > 50 and ImageFont.truetype(arq, tam).getlength(grande) > 1180:
        tam -= 6
    fg = ImageFont.truetype(arq, tam)
    d.text((50, 720 - tam - 110), grande, font=fg, fill=(255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0))
    if texto:
        fs = ImageFont.truetype(arq, 54)
        d.text((54, 720 - 92), serie.upper(), font=fs, fill=cor("opcao1"), stroke_width=3, stroke_fill=(0, 0, 0))
    img.save(destino, quality=92)
    return destino


def hhmmss(s):
    s = int(round(s))
    h, m = divmod(s, 3600)
    m, s = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--serie", required=True)
    ap.add_argument("--parte", nargs=2, action="append", metavar=("VIDEO", "TITULO"), required=True)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--abertura", default="auto")
    ap.add_argument("--subtitulo", default="")
    ap.add_argument("--fim")
    ap.add_argument("--capa-em", type=float)
    ap.add_argument("--capa-texto", default="")
    ap.add_argument("--link", default="")
    ap.add_argument("--cpu", action="store_true")
    a = ap.parse_args()

    saida = Path(a.saida)
    saida.mkdir(parents=True, exist_ok=True)
    partes = [(Path(v), t) for v, t in a.parte]
    for v, _t in partes + ([(Path(a.fim), "fim")] if a.fim else []):
        w, h, _d = info(v)
        if h > w:
            raise SystemExit(f"{v.name} é vertical ({w}x{h}): renderize a parte em 16:9 (metodo/video-longo.md), "
                             "não recorte o vertical")

    abertura = None
    if a.abertura == "auto":
        abertura = abertura_auto(a.serie, a.subtitulo, saida / "_abertura.mp4")
    elif a.abertura:
        abertura = Path(a.abertura)
    trechos = ([abertura] if abertura else []) + [v for v, _t in partes] + ([Path(a.fim)] if a.fim else [])

    # O YouTube só mostra capítulos com o primeiro em 00:00 e cada um com 10 s ou mais: a abertura (5 s) entra no
    # primeiro capítulo, e o fim (o CTA) entra no último.
    capitulos, t = [], 0.0
    if abertura:
        t += info(abertura)[2]
    inicio_1 = t
    for k, (v, titulo) in enumerate(partes):
        capitulos.append((0.0 if k == 0 else t, titulo))
        t += info(v)[2]
    if a.fim:
        t += info(Path(a.fim))[2]
    if not 300 <= t <= 900:
        print(f"AVISO o filme tem {t / 60:.1f} min; o formato pede de 5 a 15 min (junte ou separe partes)")

    nome = slug(a.serie)
    filme = saida / f"{nome}_longo.mp4"
    encoder = escolher_encoder(a.cpu)
    print(f"EMENDANDO {len(trechos)} trechos ({hhmmss(t)}) com {encoder}", flush=True)
    emendar(trechos, filme, encoder)
    if abertura and abertura.name == "_abertura.mp4":
        abertura.unlink()

    em = a.capa_em if a.capa_em is not None else inicio_1 + info(partes[0][0])[2] / 2
    capa(filme, em, a.serie, a.capa_texto, saida / "capa_youtube.jpg")

    linhas = [f"# {a.serie} · o filme ({len(partes)} partes)", "",
              "## Título", f"{a.serie}: {partes[0][1]} a {partes[-1][1]} (a história completa) | Ficção", "",
              "## Descrição", f"As partes de {a.serie} que vocês decidiram, juntas e sem interrupção. Ficção.", ""]
    linhas += [f"{hhmmss(s)} {titulo}" for s, titulo in capitulos]
    if a.link:
        linhas += ["", a.link]
    linhas += ["", "## Conferir antes de subir",
               "- Capítulos: o primeiro em 00:00, pelo menos 3 e cada um com 10 s ou mais (senão o YouTube não mostra).",
               "- Rótulo de conteúdo alterado ou sintético, se a voz for sintética realista (metodo/seguranca.md).",
               "- Capa 1280x720 com rosto grande e texto curto (capa_youtube.jpg)."]
    (saida / "descricao.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"LONGO_OK {filme} ({hhmmss(t)})")


if __name__ == "__main__":
    main()
