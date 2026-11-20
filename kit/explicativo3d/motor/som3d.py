# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Som do explicativo, todo sintetizado aqui (sem crédito e sem direito de terceiros): só a narração vem de fora,
do provedor de voz do usuário. Saída sempre estéreo 48 kHz (mono já deixou prévia muda no celular).

Peças: marimba(), blup(), tlec(), plim(), chua(), trilha() e mixar() (abaixa a cama sob a voz).
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # raiz do kit (config.py)
from config import ffmpeg  # noqa: E402

SR = 48000
RND = np.random.default_rng(7)


def media_movel(x, n):
    """Média móvel centrada em O(len) (soma acumulada), em vez de np.convolve, que é O(len*n)."""
    c = np.cumsum(np.concatenate([np.zeros(1), x]))
    m = (c[n:] - c[:-n]) / n
    pad = len(x) - len(m)
    return np.pad(m, (pad // 2, pad - pad // 2), mode="edge")


def t_(dur):
    return np.arange(int(dur * SR)) / SR


def filtro(x, tipo, freq, ordem=4):
    return sosfilt(butter(ordem, freq, btype=tipo, fs=SR, output="sos"), x)


def nota(nome):
    """'C4', 'A#3' -> Hz."""
    idx = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
    n, o = nome[:-1], int(nome[-1])
    return 440.0 * 2 ** ((idx[n] + 12 * (o + 1) - 69) / 12)


def marimba(f, dur=0.6, amp=1.0):
    """Marimba: fundamental + parcial em 4x (característico da madeira), ataque de baqueta e decaimento rápido."""
    t = t_(dur)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t * 6) + 0.35 * np.sin(2 * np.pi * f * 4.0 * t) * np.exp(-t * 18)
    x += 0.12 * np.sin(2 * np.pi * f * 9.9 * t) * np.exp(-t * 40)
    ataque = np.minimum(1, t / 0.002)
    return amp * x * ataque


def blup(f0=380, f1=900, dur=0.14, amp=0.8):
    """Bolha: seno com a frequência subindo rápido e um decaimento curto."""
    t = t_(dur)
    f = f0 + (f1 - f0) * (t / dur) ** 0.6
    fase = 2 * np.pi * np.cumsum(f) / SR
    return amp * np.sin(fase) * np.sin(np.pi * t / dur) ** 0.7


def tlec(amp=0.9, tom_hz=2600):
    """Peça de encaixe: estalo de ruído filtrado + um "tic" agudo curto. É a marca da desmontagem."""
    t = t_(0.09)
    ruido = filtro(RND.standard_normal(len(t)), "bandpass", [1500, 6000]) * np.exp(-t * 90)
    tic = np.sin(2 * np.pi * tom_hz * t) * np.exp(-t * 70)
    corpo = np.sin(2 * np.pi * 420 * t) * np.exp(-t * 45) * 0.6
    x = 0.6 * ruido / (np.abs(ruido).max() + 1e-9) + 0.5 * tic + corpo
    return amp * x / np.abs(x).max()


def plim(amp=0.6):
    """Brilho curto (duas notas agudas de marimba)."""
    a = marimba(nota("E6"), 0.4)
    b = marimba(nota("B6"), 0.4)
    x = np.zeros(int(0.5 * SR))
    x[: len(a)] += a
    x[int(0.07 * SR): int(0.07 * SR) + len(b)] += b
    return amp * x / np.abs(x).max()


def chua(dur=2.0, amp=0.5, sobe=False):
    """Água escorrendo (ruído rosado filtrado com envelope em arco). `sobe` inverte o filtro (água enchendo)."""
    t = t_(dur)
    r = np.cumsum(RND.standard_normal(len(t)))
    r = r - media_movel(r, 400)
    env = np.sin(np.pi * t / dur) ** 1.5
    x = filtro(r, "bandpass", [300, 3500] if sobe else [150, 2200]) * env
    return amp * x / (np.abs(x).max() + 1e-9)


def abertura():
    """Assinatura de abertura: blup-blup + 3 notas de marimba subindo (menos de 0,8 s)."""
    x = np.zeros(int(0.9 * SR))
    for t0, f0, f1 in ((0.0, 320, 760), (0.11, 420, 980)):
        b = blup(f0, f1)
        i = int(t0 * SR)
        x[i: i + len(b)] += b
    for k, n in enumerate(("C5", "E5", "G5")):
        m = marimba(nota(n), 0.5, 0.55)
        i = int((0.26 + 0.12 * k) * SR)
        x[i: i + len(m)] += m[: len(x) - i]
    return x / np.abs(x).max()


def trilha(dur, bpm=100, amp=0.32):
    """Cama: marimba em arpejo (C - Am - F - G), baixo seno e chocalho leve. Loop sem fim marcado."""
    batida = 60 / bpm
    acordes = [("C4", "E4", "G4", "C5"), ("A3", "C4", "E4", "A4"), ("F3", "A3", "C4", "F4"), ("G3", "B3", "D4", "G4")]
    baixos = ["C2", "A1", "F1", "G1"]
    x = np.zeros(int((dur + 1) * SR))
    n_comp = int(dur / (4 * batida)) + 1
    for c in range(n_comp):
        ac = acordes[c % 4]
        t_c = c * 4 * batida
        for k in range(8):  # colcheias
            i = int((t_c + k * batida / 2) * SR)
            m = marimba(nota(ac[[0, 2, 1, 3, 2, 1, 3, 2][k]]), 0.45, 0.5 if k % 2 == 0 else 0.35)
            x[i: i + len(m)] += m[: max(0, len(x) - i)]
        tb = t_(4 * batida)
        bx = 0.5 * np.sin(2 * np.pi * nota(baixos[c % 4]) * tb) * np.exp(-tb * 0.8)
        i = int(t_c * SR)
        x[i: i + len(bx)] += bx[: max(0, len(x) - i)]
        for k in range(8):  # chocalho nas colcheias do contratempo
            if k % 2:
                ch = filtro(RND.standard_normal(int(0.05 * SR)), "highpass", 6000) * np.exp(-t_(0.05) * 80) * 0.15
                i = int((t_c + k * batida / 2) * SR)
                x[i: i + len(ch)] += ch[: max(0, len(x) - i)]
    x = x[: int(dur * SR)]
    fade = np.minimum(1, np.minimum(t_(dur) / 0.5, (dur - t_(dur)) / 1.0))
    return amp * x / np.abs(x).max() * fade


def ler(caminho):
    pcm = subprocess.run([ffmpeg(), "-v", "error", "-i", str(caminho), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(pcm, dtype=np.float32).copy()


def por(alvo, t0, x, ganho=1.0, pan=0.0):
    """Soma `x` (mono) em `alvo` (estéreo, shape (n, 2)) a partir de t0 segundos, com pan -1..1."""
    i = int(t0 * SR)
    if i >= len(alvo):
        return
    n = min(len(x), len(alvo) - i)
    esq, dir_ = np.sqrt((1 - pan) / 2), np.sqrt((1 + pan) / 2)
    alvo[i: i + n, 0] += x[:n] * ganho * esq * 1.414
    alvo[i: i + n, 1] += x[:n] * ganho * dir_ * 1.414


def mixar(voz, cama, efeitos, duck=0.35):
    """Voz no centro; a cama abaixa para `duck` onde há voz (envelope suavizado); efeitos por cima. Normaliza a -1 dBFS."""
    n = max(len(voz), len(cama), len(efeitos))
    v = np.zeros(n)
    v[: len(voz)] = voz
    env = media_movel(np.abs(v), int(0.25 * SR))
    env = np.clip(env / (env.max() + 1e-9) * 6, 0, 1)
    ganho = 1 - (1 - duck) * env
    out = np.zeros((n, 2))
    out[:, 0] += v
    out[:, 1] += v
    c = np.zeros((n, 2))
    c[: len(cama)] = cama
    out += c * ganho[:, None]
    e = np.zeros((n, 2))
    e[: len(efeitos)] = efeitos
    out += e
    return out / np.abs(out).max() * 0.89


def gravar(caminho, estereo):
    pcm = (np.clip(estereo, -1, 1) * 32767).astype(np.int16).tobytes()
    subprocess.run([ffmpeg(), "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-", str(caminho)],
                   input=pcm, check=True)
