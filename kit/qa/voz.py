# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Trava de voz: nenhuma fala termina num corte seco.

O fim da fala é o fim do SOM, não o fim da última palavra: a consoante surda ("s", "f", "x") e a respiração colada
vêm depois do que o alinhamento marca como fim da palavra, e cortar ali faz a fala parar seco. Tomada que o gerador
truncou com a voz soando ganha a cauda de soltura de 180 ms no `falas.py --juntar`.

Confere no narrador.mp3 juntado: na passagem de cada fala para a pausa, a voz cai até o silêncio sem degrau (a janela
de 10 ms antes do silêncio já está 25 dB abaixo do pico). Degrau = corte seco: reprova.

Uso (da pasta kit/):
    python qa/voz.py <pasta do --juntar>      # lê narrador.mp3 e tempos.json
Sai com código 1 se achar corte seco.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

SR = 48000


def _le(arq):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(arq), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True,
                         check=True).stdout
    return np.frombuffer(raw, np.float32)


def _db10(x):
    h = SR // 100
    n = len(x) // h
    return 20 * np.log10(np.sqrt(np.mean(x[: n * h].reshape(n, h).astype(np.float64) ** 2, axis=1)) + 1e-9)


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    pasta = Path(sys.argv[1])
    db = _db10(_le(pasta / "narrador.mp3"))
    pico = db.max()
    lim = pico - 40
    tempos = json.loads((pasta / "tempos.json").read_text(encoding="utf-8"))
    fins = {}
    for w in tempos:
        fins[w["bloco"]] = max(fins.get(w["bloco"], 0.0), w["fim"])
    falhas = []
    for bloco, fw in sorted(fins.items()):
        i = int(fw * 100)
        k = i   # o primeiro silêncio de verdade (>= 120 ms abaixo do limite) depois da última palavra
        while k < len(db):
            if db[k] < lim:
                m = k
                while m < len(db) and db[m] < lim:
                    m += 1
                if m - k >= 12 or m >= len(db):
                    break
                k = m
            else:
                k += 1
        if k >= len(db):
            continue   # a última fala vai até o fim do arquivo
        degrau = db[k - 1] - pico
        ok = degrau <= -25
        som = (k - i) * 10
        print(f"  {'ok   ' if ok else 'FALHA'} fala {bloco:2d}: som até {k / 100:6.2f}s ({som:+4d} ms depois da última palavra), "
              f"última janela antes do silêncio a {degrau:.0f} dB do pico")
        if not ok:
            falhas.append(bloco)
    if falhas:
        print(f"corte seco nas falas {falhas}: grave a fala de novo ou junte com o falas.py (que põe a cauda de soltura)")
        sys.exit(1)
    print("VOZ_OK")


if __name__ == "__main__":
    main()
