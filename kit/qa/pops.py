# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Trava de persistência: acha objeto que SOME ou APARECE de um quadro pro outro sem corte de plano (o "pop").

Lê o vídeo em baixa resolução (cinza, 270x480) e, em cada quadro, compara a diferença para o anterior com a dos
vizinhos. Pop é uma mancha compacta que muda forte de t-1 pra t e fica parada antes e depois. Movimento de câmera e
stop motion mudam em ritmo (a mesma região de novo em até 15 quadros), e a fervura do traço é fina demais para
passar no limiar. Ficam fora os quadros em volta dos cortes e mudanças marcadas e as faixas de interface (selos do
topo, legenda), que mudam de propósito.

Uso (da pasta kit/):
    python qa/pops.py <video.mp4> [--cortes cortes.json] [--fps 60] [--limiar 28] [--min-blocos 6]
cortes.json: lista de segundos em que há corte ou mudança de propósito ([3.2, 7.85, ...]) ou o tempos.json da
montagem (qualquer dict: entram todos os valores numéricos das chaves que começam com "t_").
Sai com código 1 se achar pop.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

W, H = 270, 480
B = 6                   # bloco de 6x6 (24x24 no quadro cheio)
UI_TOPO = 140           # px do quadro cheio: selos do topo
LEGENDA = (1290, 1600)  # px do quadro cheio: faixa da legenda


def _cortes(arq):
    if not arq:
        return []
    d = json.loads(Path(arq).read_text(encoding="utf-8"))
    if isinstance(d, list):
        return [float(v) for v in d]
    return [float(v) for k, v in d.items() if k.startswith("t_") and isinstance(v, (int, float))]


def _bloco(d):
    h, w = d.shape[0] // B, d.shape[1] // B
    return d[: h * B, : w * B].reshape(h, B, w, B).mean(axis=(1, 3))


def _sobrepoe(a, b):
    ix = max(0, min(a[5], b[5]) - max(a[3], b[3]))
    iy = max(0, min(a[6], b[6]) - max(a[4], b[4]))
    menor = min((a[5] - a[3]) * (a[6] - a[4]), (b[5] - b[3]) * (b[6] - b[4])) or 1
    return ix * iy / menor > 0.3


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--cortes")
    ap.add_argument("--fps", type=float, default=60.0)
    ap.add_argument("--limiar", type=float, default=28.0)
    ap.add_argument("--min-blocos", type=int, default=6)
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.video, "-vf", f"scale={W}:{H}:flags=area,format=gray", "-f", "rawvideo", "-"],
                            stdout=subprocess.PIPE)
    fr = []
    while True:
        b = proc.stdout.read(W * H)
        if len(b) < W * H:
            break
        fr.append(np.frombuffer(b, dtype=np.uint8).reshape(H, W).astype(np.float32))
    proc.wait()
    n = len(fr)
    perto_corte = np.zeros(n, bool)
    for tc in _cortes(a.cortes):
        k = int(round(tc * a.fps))
        perto_corte[max(0, k - 3): min(n, k + 16)] = True   # o que muda no corte anima até ~0,25 s
    D = [None] + [_bloco(np.abs(fr[i] - fr[i - 1])) for i in range(1, n)]
    achados = []
    for i in range(3, n - 2):
        if perto_corte[i]:
            continue
        viz = np.maximum(np.maximum(D[i - 1], D[i + 1]), np.maximum(D[i - 2] if D[i - 2] is not None else 0, D[i + 2]))
        mask = (D[i] > a.limiar) & (D[i] > 4 * viz + 4)
        mask[: UI_TOPO // 4 // B, :] = False
        mask[LEGENDA[0] // 4 // B: LEGENDA[1] // 4 // B, :] = False
        if mask.sum() < a.min_blocos:
            continue
        lab, nl = ndimage.label(mask)
        tam = ndimage.sum(mask, lab, range(1, nl + 1))
        k = int(np.argmax(tam))
        if tam[k] < a.min_blocos:
            continue
        ys, xs = np.where(lab == k + 1)
        achados.append((i, i / a.fps, int(tam[k]), xs.min() * B * 4, ys.min() * B * 4, (xs.max() + 1) * B * 4, (ys.max() + 1) * B * 4))
    # stop motion muda a pose a cada poucos quadros no mesmo lugar; pop de verdade acontece uma vez na região
    achados = [x for x in achados if not any(y is not x and abs(y[0] - x[0]) <= 15 and _sobrepoe(x, y) for y in achados)]
    print(f"{Path(a.video).name}: {n} quadros, {len(achados)} pop(s)")
    for i, t, tam, x0, y0, x1, y1 in achados:
        print(f"  quadro {i:5d}  t={t:6.2f}s  {tam:3d} blocos  caixa x{x0}-{x1} y{y0}-{y1}: confira se é corte ou objeto sumindo")
    if achados:
        sys.exit(1)
    print("POPS_OK")


if __name__ == "__main__":
    main()
