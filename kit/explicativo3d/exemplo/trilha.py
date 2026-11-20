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
sys.path.insert(0, str(AQUI.parent / "motor"))
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
    t = q("condomínio")
    for k, pan in enumerate((0.0, -0.5, 0.5, -0.2)):  # as 4 partes se soltando
        S.por(fx, t + 0.05 + 0.09 * k, S.tlec(0.8), 0.45, pan)
    for palavra in ("boia", "caça", "come"):  # cada parte quica na sua palavra
        S.por(fx, q(palavra), S.tlec(0.5, 3200), 0.35)
    S.por(fx, q("namora"), S.plim(), 0.45)
    S.por(fx, q("sozinho"), S.blup(520, 260, amp=0.5), 0.35, 0.5)  # a digestão murcha, sozinha
    t = q("sobrevive", fim=True) - 0.35
    for k, pan in enumerate((0.5, -0.5, 0.0)):  # encaixam de volta
        S.por(fx, t + 0.1 * k, S.tlec(0.9), 0.35, pan)
    S.por(fx, tp.fim + 0.35, S.plim(), 0.4)  # entra o cartão do CTA

    mix = S.mixar(voz, cama, fx)
    S.gravar(pasta / "mix.wav", mix)
    print(f"TRILHA_OK {pasta / 'mix.wav'} ({len(mix) / S.SR:.2f} s)")


if __name__ == "__main__":
    main()
