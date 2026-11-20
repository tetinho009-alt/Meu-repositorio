# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Grade de revisão: um quadro a cada N segundos do vídeo inteiro, em folhas de 9 colunas com o tempo escrito.

Uso:
    python qa_grade.py <video.mp4> [--passo 2] [--saida PASTA] [--zona]

`--zona` desenha a zona segura da configuração (texto importante tem de ficar dentro) e o limite de baixo da
legenda. O que procurar (regra 14 do estúdio): objeto flutuando, coisa atravessando parede, objeto do lado errado
do muro, personagem cortado, legenda fora da zona, tela de voto parada tempo demais.
Saída: <pasta>/qa_grade_0.jpg, qa_grade_1.jpg ... (36 quadros por folha).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(KIT))

from config import CFG, ffmpeg, ffprobe, pasta  # noqa: E402

LW, LH = 270, 480
COLUNAS, POR_FOLHA = 9, 36


def _fonte(tam):
    try:
        return ImageFont.truetype(str(pasta("fontes") / CFG["fontes"]["mono"]), tam)
    except OSError:
        return ImageFont.load_default()


def tamanho(video):
    r = subprocess.run([ffprobe(), "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                        "-of", "json", str(video)], capture_output=True, text=True)
    st = json.loads(r.stdout)["streams"][0]
    return int(st["width"]), int(st["height"])


def quadros(video, passo):
    """Quadros reduzidos (LWxLH) a cada `passo` s, lidos por pipe (sem arquivos temporários)."""
    r = subprocess.run([ffmpeg(), "-v", "error", "-i", str(video), "-vf", f"fps=1/{passo},scale={LW}:{LH}",
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True)
    n = len(r.stdout) // (LW * LH * 3)
    return np.frombuffer(r.stdout[: n * LW * LH * 3], dtype=np.uint8).reshape(n, LH, LW, 3)


def grade(video, passo=2.0, saida=None, zona=False):
    video = Path(video)
    saida = Path(saida) if saida else video.parent / "qa"
    saida.mkdir(parents=True, exist_ok=True)
    w, h = tamanho(video)
    sx, sy = LW / w, LH / h
    zs = CFG["zona_segura"]
    f = _fonte(16)
    fs = quadros(video, passo)
    folhas = []
    for k0 in range(0, len(fs), POR_FOLHA):
        lote = fs[k0:k0 + POR_FOLHA]
        linhas = (len(lote) + COLUNAS - 1) // COLUNAS
        folha = Image.new("RGB", (LW * COLUNAS, LH * linhas), (20, 20, 24))
        for j, arr in enumerate(lote):
            im = Image.fromarray(arr)
            d = ImageDraw.Draw(im)
            if zona:
                d.rectangle([zs["x0"] * sx, zs["y0"] * sy, zs["x1"] * sx, zs["y1"] * sy], outline=(0, 255, 120))
                d.line([0, zs["legenda_y_max"] * sy, LW, zs["legenda_y_max"] * sy], fill=(255, 80, 80))
            t = (k0 + j) * passo
            d.rectangle([0, 0, 74, 22], fill=(0, 0, 0))
            d.text((4, 2), f"{int(t // 60)}:{t % 60:04.1f}", font=f, fill=(255, 220, 90))
            folha.paste(im, ((j % COLUNAS) * LW, (j // COLUNAS) * LH))
        arq = saida / f"qa_grade_{k0 // POR_FOLHA}.jpg"
        folha.save(arq, quality=86)
        folhas.append(arq)
    print(f"QA_OK {len(fs)} quadros em {len(folhas)} folha(s): " + ", ".join(str(p) for p in folhas))
    return folhas


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--passo", type=float, default=2.0)
    ap.add_argument("--saida")
    ap.add_argument("--zona", action="store_true")
    a = ap.parse_args()
    grade(a.video, a.passo, a.saida, a.zona)


if __name__ == "__main__":
    main()
