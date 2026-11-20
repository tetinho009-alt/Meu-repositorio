# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Som do exemplo: narração + cama de marimba + efeitos nos marcos da fala, tudo por código (som3d).

    python explicativo3d/exemplo/trilha.py --audio PASTA

Lê PASTA/narrador.mp3 e PASTA/tempos.json; grava PASTA/mix.wav (estéreo 48 kHz). O volume final (-14 LUFS) é
acertado depois pelo masterizar.py do kit.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[1] / "motor"))
import som3d as S  # noqa: E402
from tempos import Tempos  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--audio", required=True)
    a = ap.parse_args()
    pasta = Path(a.audio)
    ep = json.loads((AQUI / "episodio.json").read_text(encoding="utf-8"))
    tp = Tempos(pasta / "tempos.json")
    q = tp.quando

    voz = S.ler(pasta / "narrador.mp3")
    dur = tp.fim + 0.4 + ep["cta_segundos"]
    tr = S.trilha(dur)
    cama = np.stack([tr, tr], axis=1)
    fx = np.zeros_like(cama)

    S.por(fx, 0.0, S.abertura(), 0.4)
    S.por(fx, q("entrar"), S.blup(900, 300, amp=0.6), 0.35)   # o raio cai
    S.por(fx, q("casa"), S.tlec(0.9), 0.45)                     # pousa no chão
    S.por(fx, q("casa") + 0.15, S.tlec(0.6, 3600), 0.3, -0.5)   # susto da tomada
    S.por(fx, q("fiação"), S.plim(), 0.45)                      # faísca no fio
    S.por(fx, tp.fim + 0.35, S.plim(), 0.4)  # entra o cartão do CTA

    mix = S.mixar(voz, cama, fx)
    S.gravar(pasta / "mix.wav", mix)
    print(f"TRILHA_OK {pasta / 'mix.wav'} ({len(mix) / S.SR:.2f} s)")


if __name__ == "__main__":
    main()
