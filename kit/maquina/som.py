# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Áudio do episódio: leitura via ffmpeg, filtros, efeitos feitos por código e uma mesa estéreo com ducking.

Tudo a 48 kHz. Fontes mono (float32) são colocadas na mesa com pan (fixo ou andando) em dois barramentos:
"voz" (narração e falas) e "resto" (efeitos, cama, música). Na mixagem o resto abaixa quando a voz fala, um
limitador suave segura os picos e o resultado sai ESTÉREO (mono deixa alguns celulares mudos: lição real).

Efeitos por código não dependem de áudio de terceiros. Trilha baixada do YouTube não tem licença: não use.
"""
import subprocess
from pathlib import Path

import numpy as np
from scipy.ndimage import maximum_filter1d
from scipy.signal import butter, fftconvolve, sosfilt

from config import CFG, ffmpeg

SR = int(CFG["audio"]["taxa"])
RNG = np.random.default_rng(7)


# ---------------------------------------------------------------- leitura e gravação

def ler(caminho, ini=0.0, fim=None, canais=1):
    """Lê qualquer áudio (mp3, wav, ...) como float32 a 48 kHz. `canais=2` devolve (n, 2)."""
    pcm = subprocess.run([ffmpeg(), "-v", "error", "-i", str(caminho), "-f", "f32le", "-ac", str(canais), "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(pcm, dtype=np.float32).copy()
    if canais == 2:
        x = x.reshape(-1, 2)
    return x[int(ini * SR): int(fim * SR) if fim else None]


def gravar_wav(caminho, estereo):
    """Grava (n, 2) float em WAV PCM 24 bits estéreo pelo ffmpeg (sem depender de libsndfile)."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    dados = np.ascontiguousarray(np.clip(estereo, -1, 1).astype(np.float32))
    subprocess.run([ffmpeg(), "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "pcm_s24le", str(caminho)], input=dados.tobytes(), check=True)
    return caminho


def duracao(caminho):
    return len(ler(caminho)) / SR


# ---------------------------------------------------------------- filtros

def filtro(x, tipo, freq, ordem=4):
    return sosfilt(butter(ordem, freq, btype=tipo, fs=SR, output="sos"), x)


def reverb(x, cauda=0.9, mix=0.35):
    n = int(cauda * SR)
    ir = filtro(RNG.standard_normal(n) * np.exp(-np.linspace(0, 6, n)), "lowpass", 4000, 2)
    ir /= np.abs(ir).sum() ** 0.5 * 8
    molhado = np.pad(fftconvolve(x, ir), (0, 1))[: len(x) + n]
    return np.concatenate([x, np.zeros(n)]) * (1 - mix) + molhado * mix * 3


def longe(x, corte=1800, mix=0.55):
    """Som distante: abafado e com eco."""
    return reverb(filtro(x, "lowpass", corte, 2), 1.4, mix)


def telefone(x):
    """Voz de áudio de celular: banda estreita e um pouco saturada."""
    return np.tanh(filtro(x, "bandpass", [300, 3400], 4) * 1.6) * 0.8


def fade(x, ini=0.01, fim=0.05):
    x = x.copy()
    a, b = int(ini * SR), int(fim * SR)
    if a:
        x[:a] *= np.linspace(0, 1, a)
    if b:
        x[-b:] *= np.linspace(1, 0, b)
    return x


# ---------------------------------------------------------------- efeitos por código

def _t(dur):
    return np.arange(int(dur * SR)) / SR


def tom(f, dur, amp=1.0):
    return amp * np.sin(2 * np.pi * f * _t(dur))


def notificacao():
    a, b = _t(0.07), _t(0.16)
    return np.concatenate([tom(1320, 0.07) * np.exp(-a * 30), tom(1760, 0.16) * np.exp(-b * 22)]) * 0.35


def vibra(dur=0.8):
    t = _t(dur)
    return 0.3 * np.sin(2 * np.pi * 165 * t) * ((t % 0.4) < 0.3)


def drone(dur, f=48.0):
    """Cama grave contínua que respira devagar."""
    t = _t(dur)
    x = 0.05 * np.sin(2 * np.pi * f * t) + 0.04 * np.sin(2 * np.pi * f * 1.152 * t) + 0.03 * np.sin(2 * np.pi * f * 2.01 * t)
    x += filtro(RNG.standard_normal(len(t)), "lowpass", 220, 2) * 0.05
    return x * (0.8 + 0.2 * np.sin(2 * np.pi * 0.07 * t))


def vento(dur, forca=1.0):
    """Vento noturno: ruído filtrado com rajadas lentas."""
    t = _t(dur)
    x = filtro(RNG.standard_normal(len(t)), "bandpass", [180, 900], 2)
    raj = 0.55 + 0.45 * np.sin(2 * np.pi * 0.11 * t + 1.3) * np.sin(2 * np.pi * 0.047 * t)
    return x * raj * 0.05 * forca


def estalo():
    """Estalo de interruptor ou lâmpada."""
    t = _t(0.35)
    click = RNG.standard_normal(len(t)) * np.exp(-t * 60) * 0.8
    chiado = filtro(RNG.standard_normal(len(t)), "highpass", 3000, 2) * np.exp(-t * 9) * 0.15
    return click + chiado


def zumbido_lampada(dur):
    """Zumbido de lâmpada fluorescente (60 Hz + harmônicos)."""
    t = _t(dur)
    x = sum(np.sin(2 * np.pi * 60 * k * t) / k for k in (1, 2, 3, 5))
    return filtro(x, "bandpass", [100, 2000], 2) * 0.03


def coracao(dur, bpm0=62, bpm1=96):
    """Batida de coração que acelera."""
    x, n = np.zeros(int(dur * SR)), int(0.12 * SR)
    tt = np.arange(n) / SR
    bate = np.sin(2 * np.pi * 52 * tt) * np.exp(-tt * 28)
    t = 0.0
    while t < dur - 0.4:
        for d, g in ((0.0, 1.0), (0.22, 0.65)):
            i = int((t + d) * SR)
            x[i:i + n] += bate[: len(x) - i] * g
        t += 60 / (bpm0 + (bpm1 - bpm0) * t / dur)
    return filtro(x, "lowpass", 180, 2) * 0.9


def subida(dur, f0=40.0, f1=160.0):
    """Grave subindo para o momento da escolha (tensão)."""
    t = _t(dur)
    f = f0 * (f1 / f0) ** (t / dur)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * filtro(RNG.standard_normal(len(t)), "lowpass", 400, 2)
    return x * (t / dur) ** 2 * 0.18


def impacto():
    """Golpe grave (corte seco)."""
    t = _t(1.6)
    x = np.sin(2 * np.pi * 42 * t * (1 - 0.3 * t / 1.6)) * np.exp(-t * 3.5)
    x += filtro(RNG.standard_normal(len(t)), "lowpass", 900, 2) * np.exp(-t * 14) * 0.6
    return reverb(x * 0.7, 1.2, 0.3)


# ---------------------------------------------------------------- mesa estéreo

def _pan_ganhos(pan, n):
    """Pan de potência constante; `pan` em -1 (esquerda) .. 1 (direita), número ou array (pan que anda)."""
    p = np.asarray(pan, dtype=np.float64)
    if p.ndim and len(p) != n:
        p = np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(p)), p)
    ang = (np.clip(p, -1, 1) + 1) * np.pi / 4
    return np.cos(ang), np.sin(ang)


class Mesa:
    """Linha do tempo estéreo com barramentos de voz e de resto, ducking e máscara de silêncio."""

    def __init__(self, total):
        self.total = float(total)
        n = int(self.total * SR) + SR
        self.voz = np.zeros((n, 2))
        self.resto = np.zeros((n, 2))
        self.mascara = np.ones(n)

    def poe(self, t0, x, pan=0.0, voz=False, ganho=1.0):
        """Coloca o som mono `x` no instante t0 (s) com pan e ganho."""
        alvo = self.voz if voz else self.resto
        i = max(0, int(t0 * SR))
        n = min(len(x), len(alvo) - i)
        if n <= 0:
            return
        gl, gr = _pan_ganhos(pan, len(x))
        gl = gl[:n] if np.ndim(gl) else gl
        gr = gr[:n] if np.ndim(gr) else gr
        alvo[i:i + n, 0] += x[:n] * gl * ganho
        alvo[i:i + n, 1] += x[:n] * gr * ganho

    def silencio(self, a, b, rampa=0.04):
        """Zera TUDO entre a e b (silêncio como golpe)."""
        tt = np.arange(len(self.mascara)) / SR
        self.mascara *= 1 - np.interp(tt, [a - rampa, a, b, b + rampa * 2], [0, 1, 1, 0])

    def mixar(self, duck=0.6, voz_ganho=1.1):
        """Resto abaixa até (1 - duck) quando a voz fala; limitador suave; corta no total."""
        voz_m = np.abs(self.voz).mean(axis=1)
        env = np.clip(np.convolve(voz_m, np.ones(SR // 10) / (SR // 10), mode="same") * 12, 0, 1)
        fala = maximum_filter1d(env, int(0.6 * SR))
        fala = np.convolve(fala, np.ones(SR // 10) / (SR // 10), mode="same")
        dk = (1 - duck * fala)[:, None]
        final = np.tanh((self.resto * dk + self.voz * voz_ganho) * self.mascara[:, None] * 1.1) * 0.95
        return final[: int(self.total * SR)]

    def gravar(self, caminho, **kw):
        return gravar_wav(caminho, self.mixar(**kw))
