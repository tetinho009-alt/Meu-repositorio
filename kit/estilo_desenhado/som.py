# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Som do estilo desenhado (opcional): trilha e efeitos sintetizados aqui mesmo (numpy/scipy, nada baixado), o tratamento
da narração e o guia de voz pro ElevenLabs.

Trilha (cada camada é uma função; `trilha()` junta): drone grave, cordas desafinadas, caixinha de música quebrada,
harmônio arrastado, piano fora do tom, contrabaixo em pizzicato lento, serrote tocado com arco e silêncios.
Efeitos: vento uivando, madeira rangendo, graveto quebrando, corvo distante, fogo crepitando, sussurros
ininteligíveis e o "ding" de caixinha nas viradas.

Tudo em 48 kHz estéreo float32 (-1..1). `salva(caminho, sinal)` grava WAV 24 bits.
"""
import math
import subprocess
from pathlib import Path

import numpy as np
from scipy import signal as sg
from scipy.io import wavfile

SR = 48000

# ---------------------------------------------------------------- guia de voz (ElevenLabs)
GUIA_VOZ = {
    "voz": "uma voz grave e cansada de narrador pt-BR (no ElevenLabs, por exemplo NFmEzNOony1UsEJGXLth); configure em voz.elevenlabs.voz",
    "direcao": ("Narrador triste e pesado, que já viu isso acontecer: devagar, grave, quase sussurrado, sem "
                "animação de locutor. Frases curtas, respiração antes da frase importante, pausa longa depois."),
    "texto": ("Escreva as pausas no texto: reticências pra pausa curta, ponto final e frase nova pra pausa longa. "
              "Nada de ponto de exclamação. Palavra-chave isolada no fim da frase ('...pra ela.')."),
    "eleven_v4": {"tags": "[whispers] no começo do bloco quando for segredo; [sighs] antes da revelação; evitar [excited]",
                  "configuracao": "estabilidade alta (Robust) e estilo 0: menos variação, menos 'interpretação'"},
    "eleven_multilingual_v2": {"configuracao": "stability 0.8-0.9, similarity 0.75, style 0.0-0.1, speaker boost ligado, "
                                               "speed 0.8 (mais lento sem esticar a voz)"},
    "pos": "voz_gotica(): EQ leve, compressão suave e uma sala pequena; nunca muda tempo nem tom da voz",
}


# ---------------------------------------------------------------- básicos

def _t(dur):
    return np.arange(int(dur * SR)) / SR


def _env(n, ataque, solta, sustem=1.0):
    e = np.ones(n) * sustem
    a = max(1, int(ataque * SR))
    r = max(1, int(solta * SR))
    e[:a] = np.linspace(0, sustem, a)
    if r < n:
        e[-r:] *= np.linspace(1, 0, r)
    return e


def _passa_baixa(x, fc, ordem=2):
    b, a = sg.butter(ordem, min(0.99, fc / (SR / 2)), "low")
    return sg.lfilter(b, a, x)


def _passa_banda(x, f0, q):
    b, a = sg.iirpeak(min(0.99 * SR / 2, f0) / (SR / 2), q)
    return sg.lfilter(b, a, x)


def _passa_alta(x, fc, ordem=2):
    b, a = sg.butter(ordem, fc / (SR / 2), "high")
    return sg.lfilter(b, a, x)


def reverb(x, dur=2.4, mix=0.35, semente=1, escuro=3000):
    """Reverb por convolução com resposta sintética (ruído com decaimento e cauda escura)."""
    rng = np.random.default_rng(semente)
    n = int(dur * SR)
    ir = rng.standard_normal((n, 2)) * np.exp(-np.arange(n) / (SR * dur / 6.5))[:, None]
    ir = np.stack([_passa_baixa(ir[:, k], escuro) for k in range(2)], axis=1)
    ir /= np.abs(ir).sum(axis=0).max() / 6
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    mol = np.stack([sg.fftconvolve(x[:, k], ir[:, k])[:len(x)] for k in range(2)], axis=1)
    return (1 - mix) * x + mix * mol


def pan(x, p):
    """p em -1..1 (esquerda..direita)."""
    a = (p + 1) * math.pi / 4
    return np.stack([x * math.cos(a), x * math.sin(a)], axis=1)


def _nota(f):
    return 440.0 * 2 ** ((f - 69) / 12)


def mix(*faixas, dur=None):
    n = max(len(f) for f in faixas) if dur is None else int(dur * SR)
    out = np.zeros((n, 2))
    for f in faixas:
        if f.ndim == 1:
            f = np.stack([f, f], axis=1)
        m = min(n, len(f))
        out[:m] += f[:m]
    return out


def coloca(dur, som, t0, ganho=1.0):
    """Põe `som` começando em t0 numa faixa de `dur` segundos."""
    n = int(dur * SR)
    out = np.zeros((n, 2))
    if som.ndim == 1:
        som = np.stack([som, som], axis=1)
    i = int(t0 * SR)
    m = max(0, min(len(som), n - i))
    out[i:i + m] = som[:m] * ganho
    return out


def normaliza(x, pico=0.89):
    m = np.abs(x).max() or 1.0
    return x * (pico / m)


def salva(caminho, x):
    x = np.clip(x, -1, 1)
    wavfile.write(str(caminho), SR, (x * (2 ** 31 - 1)).astype(np.int32))


# ---------------------------------------------------------------- camadas da trilha

def drone(dur, raiz=28, semente=1):
    """Drone grave: raiz e quinta desafinada em serra filtrada, respirando devagar, com ruído escuro por baixo."""
    t = _t(dur)
    rng = np.random.default_rng(semente)
    x = np.zeros_like(t)
    for semi, ganho, desv in ((0, 0.5, 0.0), (0, 0.4, 0.31), (7, 0.22, -0.18), (12, 0.12, 0.42), (13, 0.05, 0.0)):
        f = _nota(raiz + semi + desv / 10)
        x += ganho * sg.sawtooth(2 * math.pi * f * t + rng.uniform(0, 6))
    x = _passa_baixa(x, 220)
    resp = 0.6 + 0.4 * np.sin(2 * math.pi * t / 9.0 + 1) * np.sin(2 * math.pi * t / 23.0)
    ruido = _passa_baixa(rng.standard_normal(len(t)), 90) * 0.6
    return (x * resp + ruido) * _env(len(t), 2.5, 2.0) * 0.5


def cordas(dur, acordes=((40, 41, 47), (38, 44, 45)), semente=2):
    """Cordas desafinadas: pares de serra com vibrato lento, cluster de semitom, crescendo e corte."""
    t = _t(dur)
    rng = np.random.default_rng(semente)
    x = np.zeros_like(t)
    seg = dur / len(acordes)
    for k, ac in enumerate(acordes):
        m = (t >= k * seg) & (t < (k + 1) * seg)
        tt = t[m] - k * seg
        env = np.sin(np.pi * np.clip(tt / seg, 0, 1)) ** 1.5
        for nota in ac:
            for desv in (-0.14, 0.11):
                f = _nota(nota + desv) * (1 + 0.004 * np.sin(2 * math.pi * 4.8 * tt + rng.uniform(0, 6)))
                fase = 2 * math.pi * np.cumsum(f) / SR
                x[m] += 0.12 * sg.sawtooth(fase) * env
    return _passa_baixa(x, 1800) * 0.6


def caixinha(dur, melodia=(76, 75, 72, 71, 72, 79, 76, None, 74, 72, 71, 67), passo=0.42, semente=3, quebrada=True):
    """Caixinha de música quebrada: sino de pente metálico, notas fora do tom, tempo tropeçando e corda acabando."""
    t = _t(dur)
    rng = np.random.default_rng(semente)
    x = np.zeros_like(t)
    pos = 0.3
    k = 0
    while pos < dur - 0.5:
        nota = melodia[k % len(melodia)]
        if nota is not None:
            desafina = rng.uniform(-0.45, 0.45) if quebrada and rng.random() < 0.4 else rng.uniform(-0.08, 0.08)
            f = _nota(nota + desafina)
            i = int(pos * SR)
            n = min(len(t) - i, int(1.8 * SR))
            tt = np.arange(n) / SR
            som = (np.sin(2 * math.pi * f * tt) + 0.4 * np.sin(2 * math.pi * f * 2.76 * tt) * np.exp(-tt * 7)
                   + 0.2 * np.sin(2 * math.pi * f * 5.4 * tt) * np.exp(-tt * 14)) * np.exp(-tt * 2.6)
            som[:40] *= np.linspace(0, 1, 40)
            x[i:i + n] += som * 0.22
        devagar = 1 + (0.6 * pos / dur if quebrada else 0)        # a corda acabando: cada vez mais lenta
        pos += passo * devagar * (1 + (rng.uniform(-0.12, 0.25) if quebrada else 0))
        k += 1
    return pan(_passa_alta(x, 300), 0.25)


def harmonio(dur, notas=(45, 52, 57), semente=4):
    """Sanfona/harmônio arrastado: palhetas desafinadas batendo, fole respirando, entra devagar."""
    t = _t(dur)
    x = np.zeros_like(t)
    for n in notas:
        for desv in (0, 0.12):
            f = _nota(n + desv)
            for h, g in ((1, 1.0), (2, 0.5), (3, 0.33), (4, 0.2), (5, 0.12)):
                x += g * np.sign(np.sin(2 * math.pi * f * h * t)) * 0.03 / h
    fole = 0.5 + 0.5 * np.sin(2 * math.pi * t / 3.7) ** 2
    return pan(_passa_baixa(x, 1400) * fole * _env(len(t), 3.0, 2.5), -0.3)


def piano_torto(dur, notas=((0.5, 33), (2.9, 34), (5.6, 28), (8.2, 33)), semente=5):
    """Piano fora do tom: nota grave solta, parciais esticados (inarmônico) e martelo abafado."""
    t = _t(dur)
    x = np.zeros_like(t)
    rng = np.random.default_rng(semente)
    for t0, nota in notas:
        if t0 >= dur:
            continue
        i = int(t0 * SR)
        n = min(len(t) - i, int(5 * SR))
        tt = np.arange(n) / SR
        f = _nota(nota + rng.uniform(-0.3, 0.3))
        som = sum((1 / h) * np.sin(2 * math.pi * f * h * (1 + 0.0009 * h * h) * tt) * np.exp(-tt * (0.6 + 0.3 * h)) for h in range(1, 9))
        som[:200] *= np.linspace(0, 1, 200)
        x[i:i + n] += som * 0.32
    return _passa_baixa(x, 2400)


def pizzicato(dur, notas=((1.2, 28), (3.4, 31), (4.6, 27), (7.0, 28), (9.0, 26)), semente=6):
    """Contrabaixo em pizzicato lento (Karplus-Strong), cada nota sozinha no silêncio."""
    x = np.zeros(int(dur * SR))
    rng = np.random.default_rng(semente)
    for t0, nota in notas:
        if t0 >= dur:
            continue
        f = _nota(nota)
        p = int(SR / f)
        n = min(len(x) - int(t0 * SR), int(2.5 * SR))
        buf = rng.uniform(-1, 1, p)
        out = np.zeros(n)
        for k in range(n):
            out[k] = buf[k % p]
            buf[k % p] = 0.5 * (buf[k % p] + buf[(k + 1) % p]) * 0.996
        x[int(t0 * SR):int(t0 * SR) + n] += _passa_baixa(out, 600) * 0.6
    return x


def serrote(dur, t0=0.0, nota=67, semente=7):
    """Serrote tocado com arco: senoide com glissando lento e vibrato largo, sopro de arco por cima."""
    t = _t(dur)
    rng = np.random.default_rng(semente)
    glis = nota + 2.5 * np.sin(np.pi * np.clip((t - t0) / max(0.1, dur - t0), 0, 1)) - 1.5
    f = 440 * 2 ** ((glis - 69) / 12) * (1 + 0.012 * np.sin(2 * math.pi * 5.6 * t))
    fase = 2 * math.pi * np.cumsum(f) / SR
    x = np.sin(fase) + 0.08 * np.sin(2 * fase)
    sopro = _passa_banda(rng.standard_normal(len(t)), 2600, 4) * 0.05
    env = np.clip((t - t0) / 1.5, 0, 1) * np.clip((dur - t) / 1.2, 0, 1)
    return pan((x * 0.16 + sopro) * env, -0.15)


def trilha(dur=12.0, semente=1, silencios=((6.6, 7.4),)):
    """Trilha completa: as camadas acima com entradas escalonadas, reverb de sala grande e silêncios de verdade."""
    t = _t(dur)
    base = mix(pan(drone(dur, semente=semente), 0.0), pan(cordas(dur), 0.1) * 0.7, harmonio(dur) * 0.8, pan(piano_torto(dur), -0.2),
               pan(pizzicato(dur), 0.05) * 0.9, serrote(dur, t0=dur * 0.45) * 0.8, caixinha(dur) * 0.9)
    corte = np.ones(len(t))
    for a, b in silencios:   # silêncio de verdade (a trilha some e volta)
        m = (t >= a) & (t < b)
        corte[m] = 0.0
    corte = np.convolve(corte, np.ones(2400) / 2400, "same")
    return reverb(base * corte[:, None], dur=3.2, mix=0.38)


# ---------------------------------------------------------------- efeitos

def vento(dur, forca=1.0, semente=11):
    """Vento uivando: ruído filtrado por ressonâncias que sobem e descem (assobio na fresta) + rajadas."""
    t = _t(dur)
    rng = np.random.default_rng(semente)
    ruido = rng.standard_normal(len(t))
    x = np.zeros_like(t)
    f0 = 380 + 260 * np.sin(2 * math.pi * t / 5.3) + 120 * np.sin(2 * math.pi * t / 1.7)
    # filtro passa-banda variando: aproxima por bancos de 6 frequências misturadas pelo f0 atual
    banco = [220, 330, 470, 620, 780, 950]
    filtrados = [_passa_banda(ruido, f, 18) for f in banco]
    for f, sinal in zip(banco, filtrados):
        peso = np.exp(-((f0 - f) / 110) ** 2)
        x += sinal * peso
    rajada = 0.4 + 0.6 * np.clip(np.sin(2 * math.pi * t / 4.1) + 0.3 * np.sin(2 * math.pi * t / 1.3), 0, 1)
    fundo = _passa_baixa(ruido, 400) * 0.6
    return pan((x * 0.5 + fundo) * rajada * forca * 0.35 * _env(len(t), 1.0, 1.0), -0.4)


def rangido(dur=1.6, semente=12, f_base=95):
    """Madeira rangendo: trem de estalinhos de atrito (stick-slip) com a taxa variando, numa ressonância de tábua."""
    rng = np.random.default_rng(semente)
    n = int(dur * SR)
    x = np.zeros(n)
    tt = 0.0
    while tt < dur:
        taxa = f_base * (1 + 0.5 * math.sin(2 * math.pi * tt / dur * 1.3)) * rng.uniform(0.85, 1.15)
        i = int(tt * SR)
        if i < n:
            x[i] += rng.uniform(0.6, 1.0)
        tt += 1 / taxa
    x = sum(_passa_banda(x, f, 12) * g for f, g in ((420, 1.0), (780, 0.6), (1300, 0.35)))
    env = np.sin(np.pi * np.linspace(0, 1, n)) ** 0.6
    return pan(x * env * 0.5, 0.3)


def graveto(semente=13):
    """Graveto quebrando: 3 ou 4 estalos secos em sequência rápida, com lascas."""
    rng = np.random.default_rng(semente)
    n = int(0.5 * SR)
    x = np.zeros(n)
    tt = 0.0
    for k in range(rng.integers(3, 6)):
        i = int(tt * SR)
        m = int(rng.uniform(0.006, 0.02) * SR)
        x[i:i + m] += rng.standard_normal(m) * np.exp(-np.arange(m) / (m / 4)) * rng.uniform(0.5, 1.0)
        tt += rng.uniform(0.015, 0.07)
    return pan(_passa_alta(x, 700) * 0.9, 0.2)


def corvo(semente=14, longe=True):
    """Corvo distante: "cráá" áspero (serra com formantes e aspereza de AM), duas ou três vezes."""
    rng = np.random.default_rng(semente)
    out = []
    for k in range(rng.integers(2, 4)):
        d = rng.uniform(0.28, 0.4)
        t = _t(d)
        f = 620 * (1 - 0.18 * t / d) * (1 + 0.02 * np.sin(2 * math.pi * 30 * t))
        fase = 2 * math.pi * np.cumsum(f) / SR
        x = sg.sawtooth(fase) * (1 + 0.6 * np.sign(np.sin(2 * math.pi * 75 * t)))
        x = _passa_banda(x, 1200, 3) + 0.6 * _passa_banda(x, 2400, 4)
        x *= _env(len(t), 0.02, 0.12)
        out.append(x)
        out.append(np.zeros(int(rng.uniform(0.18, 0.35) * SR)))
    x = np.concatenate(out)
    if longe:
        x = _passa_baixa(x, 2200)
        x = reverb(pan(x * 0.35, 0.6), dur=2.0, mix=0.55)
        return x
    return pan(x, 0.6)


def fogo(dur, semente=15):
    """Fogo crepitando: ronco grave de chama + estalos aleatórios de lenha."""
    rng = np.random.default_rng(semente)
    n = int(dur * SR)
    ronco = _passa_baixa(rng.standard_normal(n), 300) * 0.25
    x = np.zeros(n)
    for k in range(int(dur * 14)):
        i = rng.integers(0, n - 2000)
        m = int(rng.uniform(0.002, 0.012) * SR)
        x[i:i + m] += rng.standard_normal(m) * np.exp(-np.arange(m) / (m / 3)) * rng.uniform(0.2, 1.0)
    return pan(ronco + _passa_alta(x, 1500) * 0.7, -0.1)


def sussurros(dur, vozes=3, semente=16):
    """Sussurros ininteligíveis: ruído passando por formantes de vogais que trocam em sílabas (sem palavra nenhuma)."""
    rng = np.random.default_rng(semente)
    n = int(dur * SR)
    vogais = [(300, 870, 2240), (400, 2000, 2550), (530, 1840, 2480), (660, 1720, 2410), (520, 920, 2200)]
    saida = np.zeros((n, 2))
    for v in range(vozes):
        ruido = rng.standard_normal(n)
        x = np.zeros(n)
        pos = rng.uniform(0, 0.6)
        while pos < dur - 0.2:
            sil = rng.uniform(0.09, 0.22)
            i, m = int(pos * SR), int(sil * SR)
            f1, f2, f3 = vogais[rng.integers(0, len(vogais))]
            seg = ruido[i:i + m]
            s = _passa_banda(seg, f1, 6) + 0.8 * _passa_banda(seg, f2, 8) + 0.4 * _passa_banda(seg, f3, 10)
            s += 0.5 * _passa_alta(seg, 4000) * (rng.random() < 0.4)   # "s" e "ch"
            x[i:i + len(s)] += s * np.sin(np.pi * np.linspace(0, 1, len(s))) ** 0.8
            pos += sil + (rng.uniform(0.25, 0.7) if rng.random() < 0.25 else rng.uniform(0.01, 0.05))
        saida += pan(x * 0.18, rng.uniform(-0.8, 0.8))
    return reverb(saida, dur=1.6, mix=0.4)


def ding(nota=88, semente=17):
    """O "ding" de caixinha nas viradas: sino metálico agudo, um pouco desafinado, com cauda."""
    t = _t(2.5)
    f = _nota(nota + 0.18)
    x = (np.sin(2 * math.pi * f * t) + 0.5 * np.sin(2 * math.pi * f * 2.76 * t) * np.exp(-t * 4)
         + 0.25 * np.sin(2 * math.pi * f * 5.4 * t) * np.exp(-t * 9)) * np.exp(-t * 1.6)
    x[:30] *= np.linspace(0, 1, 30)
    return reverb(pan(x * 0.35, 0.1), dur=2.2, mix=0.45)


# ---------------------------------------------------------------- narração

def voz_gotica(entrada, saida, lento=1.0, semitons=0.0):
    """Tratamento da narração: EQ leve (tira o embolado, abre a presença), compressão suave e uma sala pequena.

    Nunca muda tempo nem tom da voz: esticar (atempo) e baixar o tom (asetrate) com eco curto deixa a fala "tonta, de
    bêbado". `lento` e `semitons` existem só para recusar quem tentar."""
    if lento != 1.0 or semitons != 0.0:
        raise ValueError("voz_gotica: não muda tempo nem tom da voz (fica com cara de voz bêbada)")
    filtro = ("aresample=48000:resampler=soxr,highpass=f=75,equalizer=f=280:t=q:w=1.0:g=-1.5,equalizer=f=3600:t=q:w=1.4:g=2.0,"
              "acompressor=threshold=0.08:ratio=2:attack=12:release=160:knee=4:makeup=1,"
              "aecho=0.9:0.25:60|95:0.10|0.06")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(entrada), "-af", filtro, "-ar", "48000", "-ac", "2",
                    str(saida)], check=True)


def le_audio(caminho):
    """Lê qualquer áudio (via ffmpeg) como float estéreo 48 kHz."""
    out = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(caminho), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(out, dtype=np.float32).reshape(-1, 2).astype(np.float64)



# ---------------------------------------------------------------- vozes e efeitos da casa

GUIA_VOZ["narradora"] = {
    "papel": "narradora em primeira pessoa: triste, lenta, cansada, quase sussurrando.",
    "candidatas no ElevenLabs (ouça antes de escolher)": {
        "MA970ZNagubdplnfHEiJ": "Melodie: jovem, delicada e calma",
        "hDHD10Ms9Fhra3KMKKkc": "Aline: fim dos 20, timbre quente, ritmo medido, boa para mistério",
        "MPDBOuBk4rkLBByX9RF4": "Keren: jovem, suave, cadência lenta",
    },
    "direcao_v4": "[whispers] nas falas de dentro da casa; [sighs] antes da revelação; nada de [excited].",
    "voz do outro lado da porta": "uma voz grave qualquer + voz_seca() (rouca, sem grave, abafada pela madeira)",
}


def voz_seca(entrada, saida):
    """Uma voz do outro lado da porta: rouca, seca, sem corpo (corta grave), abafada pela madeira, com um eco curto
    de corredor e chiado. Só ffmpeg, nada de sample."""
    filtro = ("aresample=48000,asetrate=48000*0.94,aresample=48000,atempo=1.0,highpass=f=260,lowpass=f=3200,"
              "equalizer=f=1200:t=q:w=1:g=5,acrusher=bits=10:mode=log:aa=1:mix=0.25,"
              "aecho=0.7:0.5:22:0.35,volume=1.4")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(entrada), "-af", filtro, "-ar", "48000", "-ac", "2",
                    str(saida)], check=True)


def tique_taque(dur, bpm=60, para_em=None, semente=21):
    """Tique-taque alto e seco de despertador de corda (tique agudo, taque mais grave). `para_em` = segundo em que para."""
    n = int(dur * SR)
    x = np.zeros(n)
    rng = np.random.default_rng(semente)
    passo = 60.0 / bpm / 2
    tt, k = 0.05, 0
    while tt < dur and (para_em is None or tt < para_em):
        i = int(tt * SR)
        m = int(0.012 * SR)
        clique = rng.standard_normal(m) * np.exp(-np.arange(m) / (m / 5))
        f = 3400 if k % 2 == 0 else 2300
        clique = _passa_banda(clique, f, 6) * 2.5
        x[i:i + m] += clique[:max(0, min(m, n - i))]
        tt += passo
        k += 1
    return pan(x * 0.6, 0.15)


def batidas(ritmo=(0.0, 0.85, 1.12), semente=22):
    """Batidas na porta de madeira: toc... toc-toc (nó do dedo na madeira oca)."""
    n = int((ritmo[-1] + 0.8) * SR)
    x = np.zeros(n)
    rng = np.random.default_rng(semente)
    for t0 in ritmo:
        i = int(t0 * SR)
        m = int(0.25 * SR)
        tt = np.arange(m) / SR
        ataque = rng.standard_normal(m) * np.exp(-tt * 140)
        corpo = (np.sin(2 * math.pi * 110 * tt) + 0.6 * np.sin(2 * math.pi * 187 * tt) + 0.3 * np.sin(2 * math.pi * 291 * tt)) * np.exp(-tt * 26)
        s = _passa_baixa(ataque * 0.6, 2400) + corpo * 0.8
        x[i:i + m] += s[:max(0, min(m, n - i))]
    return reverb(pan(x * 0.7, 0.0), dur=0.9, mix=0.25)


def terra_caindo(dur, densidade=1.0, semente=23):
    """Terra seca escorrendo e caindo no chão (grãos miúdos e uns torrões)."""
    rng = np.random.default_rng(semente)
    n = int(dur * SR)
    x = np.zeros(n)
    for k in range(int(dur * 90 * densidade)):
        i = rng.integers(0, n - 400)
        m = rng.integers(40, 300)
        x[i:i + m] += rng.standard_normal(m) * np.exp(-np.arange(m) / (m / 4)) * rng.uniform(0.1, 0.6)
    for k in range(int(dur * 3 * densidade)):
        i = rng.integers(0, n - 4000)
        m = 3000
        tt = np.arange(m) / SR
        x[i:i + m] += _passa_baixa(rng.standard_normal(m), 700) * np.exp(-tt * 40) * 0.8
    return pan(_passa_alta(x, 120) * 0.5, -0.1)


def papel(dur=1.2, semente=24):
    """Papel velho arrastando na mesa / carta abrindo (farfalhar seco)."""
    rng = np.random.default_rng(semente)
    n = int(dur * SR)
    ruido = rng.standard_normal(n)
    env = np.abs(np.convolve(rng.standard_normal(n), np.ones(1500) / 1500, "same")) * 6
    env *= np.sin(np.pi * np.linspace(0, 1, n)) ** 0.5
    x = _passa_banda(ruido, 3000, 1.2) * env
    return pan(x * 0.5, 0.1)


def terco(dur=1.5, semente=25):
    """Contas de terço batendo umas nas outras (cliques de madeira pequenos, em cachos)."""
    rng = np.random.default_rng(semente)
    n = int(dur * SR)
    x = np.zeros(n)
    tt = 0.05
    while tt < dur - 0.05:
        for j in range(rng.integers(2, 5)):
            i = int((tt + j * rng.uniform(0.01, 0.03)) * SR)
            m = 300
            x[i:i + m] += _passa_banda(rng.standard_normal(m) * np.exp(-np.arange(m) / 40), rng.uniform(2200, 3600), 10)[:max(0, min(m, n - i))]
        tt += rng.uniform(0.18, 0.4)
    return pan(x * 0.5, -0.3)


def ganido(dur=1.4, semente=26):
    """Ganido baixo de cachorro com medo (choro nasal que sobe e cai)."""
    t = _t(dur)
    rng = np.random.default_rng(semente)
    f = 680 + 260 * np.sin(np.pi * t / dur) - 120 * t / dur + 12 * np.sin(2 * math.pi * 7 * t)
    fase = 2 * math.pi * np.cumsum(f) / SR
    x = np.sin(fase) + 0.4 * np.sin(2 * fase) + 0.15 * np.sin(3 * fase)
    x = _passa_banda(x, 900, 2) + 0.3 * _passa_banda(rng.standard_normal(len(t)), 1800, 3)
    return reverb(pan(x * _env(len(t), 0.08, 0.4) * 0.25, 0.4), dur=1.2, mix=0.3)


def estalo_seco(semente=27):
    """Estalo de pele seca (galho fino partindo devagar, com rangido)."""
    return mix(graveto(semente) * 0.7, rangido(0.5, semente, f_base=240) * 0.5)


def passos_madeira(dur, passo=0.62, peso=1.0, semente=28):
    """Passos no assoalho velho: o pé batendo e a tábua rangendo de vez em quando."""
    rng = np.random.default_rng(semente)
    n = int(dur * SR)
    x = np.zeros((n, 2))
    tt = 0.1
    k = 0
    while tt < dur - 0.3:
        m = int(0.18 * SR)
        s = _passa_baixa(rng.standard_normal(m) * np.exp(-np.arange(m) / (SR * 0.02)), 500) * peso
        x += coloca(dur, pan(s * 0.7, -0.2 if k % 2 else 0.2), tt)
        if rng.random() < 0.35:
            x += coloca(dur, rangido(0.5, semente + k, f_base=rng.uniform(70, 140)) * 0.6, tt + 0.05)
        tt += passo * rng.uniform(0.92, 1.08)
        k += 1
    return x


def respiracao(dur, ofegante=True, semente=29):
    """Respiração (ofegante de corrida, ou presa de medo): ruído soprado em ciclos, inspira mais agudo."""
    rng = np.random.default_rng(semente)
    n = int(dur * SR)
    ciclo = 0.42 if ofegante else 1.6
    t = _t(dur)
    fase = (t % ciclo) / ciclo
    env = np.where(fase < 0.45, np.sin(np.pi * fase / 0.45), 0.7 * np.sin(np.pi * (fase - 0.45) / 0.55)) ** 1.5
    ar = rng.standard_normal(n)
    insp = _passa_banda(ar, 1600, 1.5)
    exp_ = _passa_banda(ar, 700, 1.2)
    x = np.where(fase < 0.45, insp, exp_) * env
    return pan(x * (0.35 if ofegante else 0.2), 0.0)


def porta_batendo(semente=30):
    """Porta de madeira batendo com o vento (pancada grave e a moldura chacoalhando)."""
    m = int(1.2 * SR)
    t = np.arange(m) / SR
    rng = np.random.default_rng(semente)
    golpe = _passa_baixa(rng.standard_normal(m), 400) * np.exp(-t * 18) * 1.4 + np.sin(2 * math.pi * 62 * t) * np.exp(-t * 9) * 0.8
    chacoalha = _passa_banda(rng.standard_normal(m), 2400, 4) * np.exp(-t * 7) * (np.sin(2 * math.pi * 23 * t) > 0) * 0.3
    return reverb(pan(golpe + chacoalha, 0.0), dur=1.2, mix=0.3)
