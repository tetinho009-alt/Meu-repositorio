# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Áudio das cartelas: uma tomada de voz por bloco, aparada sem comer palavra, juntada com as pausas decididas aqui,
alinhada palavra por palavra e mixada com efeitos e trilha feitos por código (nenhum áudio de terceiros).

Por que uma tomada por bloco: o corte entre blocos cai sempre no silêncio entre dois arquivos, nunca no meio de uma
palavra (o defeito que mais custou episódio refeito). Refazer um bloco = apagar só o mp3 dele e rodar de novo.
"""
import hashlib
import json
import re
from pathlib import Path

import numpy as np

from maquina import som as S
from numeros_pt import por_extenso
from voz import provedor
from voz.pronuncia import aplicar

SR = S.SR
PALAVRAS_POR_S = 2.8      # ritmo médio da narração em pt-BR (para a prévia sem voz)


def sem_tags(texto):
    return re.sub(r"\[[^\]]*\]|<[^>]*>", " ", texto).split()


def estimar(fala):
    n = len(sem_tags(fala))
    return 0.0 if not n else 0.25 + n / PALAVRAS_POR_S


# ---------------------------------------------------------------- voz

def arquivo_bloco(pasta, i, fala, prov, voz):
    h = hashlib.sha1(f"{prov}|{voz}|{fala}".encode("utf-8")).hexdigest()[:8]
    return Path(pasta) / f"b{i:02d}_{h}.mp3"


def gerar_vozes(blocos, prov, voz, pasta, seco=False):
    """Grava só os blocos que faltam. Devolve a lista de arquivos (None para bloco sem fala)."""
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    faltam = [(i, b) for i, b in enumerate(blocos) if b.get("fala") and
              not arquivo_bloco(pasta, i, b["fala"], prov, voz).is_file()]
    chars = sum(len(b["fala"]) for _, b in faltam)
    if faltam:
        print(f"voz: {len(faltam)} bloco(s) para gravar, {chars} caracteres ({prov})", flush=True)
        if prov == "elevenlabs":
            print(f"   custo estimado na ElevenLabs: cerca de {chars} créditos", flush=True)
    if seco:
        return None
    gerador = provedor(prov) if faltam else None
    arqs = []
    for i, b in enumerate(blocos):
        if not b.get("fala"):
            arqs.append(None)
            continue
        arq = arquivo_bloco(pasta, i, b["fala"], prov, voz)
        if not arq.is_file():
            print(f"   bloco {i + 1}/{len(blocos)}: {b['fala'][:60]}", flush=True)
            tmp = arq.with_suffix(".tmp.mp3")
            gerador.sintetizar(aplicar(b["fala"]), voz, tmp)
            tmp.replace(arq)
        arqs.append(arq)
    return arqs


def aparar(x, limiar_db=-50.0, folga_ini=0.12, folga_fim=0.25):
    """Tira o silêncio das pontas sem comer o ataque nem o rabo da palavra (lição da Cobaia: -38 dB comia sílaba)."""
    if not len(x):
        return x
    h = SR // 100
    n = len(x) // h
    if n < 2:
        return x
    rms = np.sqrt(np.mean(x[: n * h].reshape(n, h).astype(np.float64) ** 2, axis=1))
    ref = np.percentile(np.abs(x), 99) + 1e-9
    voz = np.where(20 * np.log10(rms / ref + 1e-12) > limiar_db)[0]
    if not len(voz):
        return x
    i0 = max(0, voz[0] * h - int(folga_ini * SR))
    i1 = min(len(x), (voz[-1] + 1) * h + int(folga_fim * SR))
    y = x[i0:i1].copy()
    ri, rf = int(0.012 * SR), int(0.05 * SR)
    y[:ri] *= np.linspace(0, 1, min(ri, len(y)))[: len(y[:ri])]
    y[-rf:] *= np.linspace(1, 0, min(rf, len(y)))[-len(y[-rf:]):]
    return y


def juntar(blocos, arqs, inicio=0.15):
    """Narração inteira + janela (t0, t1) da fala de cada bloco + o fim de cada bloco (com pausa e contagem)."""
    trechos, janelas, t = [], [], inicio
    for i, b in enumerate(blocos):
        if arqs and arqs[i]:
            x = aparar(S.ler(arqs[i]))
        else:
            x = np.zeros(int(estimar(b.get("fala", "")) * SR), dtype=np.float32)
        t0, t1 = t, t + len(x) / SR
        trechos.append((t0, x))
        extra = float(b.get("contagem", 0) or 0)
        pausa = float(b.get("pausa", 0.35 if i < len(blocos) - 1 else 0.6))
        janelas.append({"t0": round(t0, 3), "t1": round(t1, 3), "fim": round(t1 + extra + pausa, 3)})
        t = t1 + extra + pausa
    total = t + 0.2
    narr = np.zeros(int(total * SR) + 1, dtype=np.float32)
    for t0, x in trechos:
        i = int(t0 * SR)
        narr[i:i + len(x)] += x[: len(narr) - i]
    return narr, janelas, total


# ---------------------------------------------------------------- tempo de cada palavra

def _expande_numeros(ouvidas):
    out = []
    for w, a, b in ouvidas:
        ext = por_extenso(w).split()
        if len(ext) <= 1:
            out.append((ext[0] if ext else w, a, b))
            continue
        passo = (b - a) / len(ext)
        out += [(p, a + k * passo, a + (k + 1) * passo) for k, p in enumerate(ext)]
    return out


def _uniforme(fala, t0, t1):
    ps = sem_tags(fala)
    pesos = np.array([max(2, len(p)) for p in ps], dtype=float)
    cum = np.concatenate([[0], np.cumsum(pesos)]) / max(pesos.sum(), 1)
    return [(t0 + (t1 - t0) * cum[k], p) for k, p in enumerate(ps)]


def palavras(blocos, janelas, wav=None, cpu=False):
    """[(t, palavra)] de cada bloco, na grafia do roteiro. Com Whisper quando há voz; senão, distribuído na janela.

    Devolve (lista por bloco, casadas, total) para a trava de semelhança voz x roteiro.
    """
    falas = [b.get("fala", "") for b in blocos]
    uniforme = [_uniforme(f, j["t0"], j["t1"]) if f else [] for f, j in zip(falas, janelas)]
    if wav is None:
        return uniforme, 0, 0
    try:
        from alinhar import ouvir_whisper
        from maquina.alinhamento import alinhar_palavras
        ouvidas = _expande_numeros(ouvir_whisper(wav, cpu=cpu))
    except ImportError:
        print("aviso: sem o Whisper (pip install faster-whisper), a legenda segue o ritmo médio da fala", flush=True)
        return uniforme, 0, 0
    res, casadas = alinhar_palavras(falas, ouvidas)
    por_bloco = [[] for _ in blocos]
    for w in res:
        por_bloco[w["bloco"]].append((w["ini"], w["palavra"]))
    saida = []
    for i, (j, ws) in enumerate(zip(janelas, por_bloco)):
        dentro = [p for p in ws if j["t0"] - 0.25 <= p[0] <= j["t1"] + 0.25]
        if ws and len(dentro) >= 0.6 * len(ws):
            saida.append([(min(max(tp, j["t0"]), j["t1"]), p) for tp, p in ws])
        else:
            saida.append(uniforme[i])
    return saida, casadas, len(res)


# ---------------------------------------------------------------- efeitos e trilha (feitos por código)

def whoosh(dur=0.45):
    t = np.arange(int(dur * SR)) / SR
    ruido = S.RNG.standard_normal(len(t))
    x = S.filtro(S.filtro(ruido, "lowpass", 2400, 2), "highpass", 300, 2)
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    return (x * env * 0.35).astype(np.float32)


def tique():
    return S.fade(S.tom(1250, 0.05, 0.25), 0.002, 0.03)


def acerto():
    x = S.tom(880, 0.5, 0.25) + S.tom(1320, 0.5, 0.18)
    t = np.arange(len(x)) / SR
    return S.reverb(x * np.exp(-t * 5), 0.7, 0.25)


def trilha_fundo(total, clima="leve"):
    """Cama musical por código: acorde suave com pulso (leve) ou drone grave (tenso)."""
    n = int(total * SR)
    t = np.arange(n) / SR
    if clima == "tenso":
        x = S.drone(total, 46.0)[:n]
        return np.pad(x, (0, max(0, n - len(x))))[:n] * 0.9
    acordes = [(220.0, 277.18, 329.63), (196.0, 246.94, 293.66), (174.61, 220.0, 261.63), (196.0, 246.94, 329.63)]
    x = np.zeros(n)
    dur = 2.4
    for k in range(int(total / dur) + 1):
        i0, i1 = int(k * dur * SR), min(n, int((k + 1) * dur * SR))
        if i0 >= n:
            break
        tt = t[i0:i1] - k * dur
        env = np.minimum(1, tt / 0.4) * np.minimum(1, (dur - tt) / 0.5)
        for f in acordes[k % 4]:
            x[i0:i1] += (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * f * 2.003 * tt)) * env * 0.05
    batida = 60 / 100
    for k in range(int(total / batida)):
        i = int(k * batida * SR)
        m = min(n - i, int(0.12 * SR))
        if m > 0:
            tt = np.arange(m) / SR
            x[i:i + m] += np.sin(2 * np.pi * 60 * tt * (1 - tt * 2)) * np.exp(-tt * 30) * (0.22 if k % 2 == 0 else 0.1)
    return S.filtro(x, "lowpass", 3200, 2)


def _prefs_audio():
    try:
        import prefs
        return prefs.carregar()["audio"]
    except Exception:  # noqa: BLE001
        return {"trilha": True, "volume_trilha": 0.55, "ducking": 0.65, "efeitos": True}


def mixar(narr, linha, saida_wav, clima="leve", musica=True):
    """Voz + trilha + efeitos. Volume da trilha, ducking e efeitos seguem as preferências do canal."""
    pa = _prefs_audio()
    total = len(narr) / SR
    mesa = S.Mesa(total)
    mesa.poe(0.0, narr, voz=True)
    if musica and pa.get("trilha", True):
        mesa.poe(0.0, trilha_fundo(total, clima), ganho=float(pa.get("volume_trilha", 0.55)))
    if not pa.get("efeitos", True):
        return mesa.gravar(saida_wav, duck=float(pa.get("ducking", 0.65)))
    for b in linha["blocos"]:
        if b["i"]:
            mesa.poe(max(0.0, b["seg0"] - 0.22), whoosh(), pan=0.3 if b["i"] % 2 else -0.3, ganho=0.8)
        if b["tipo"] == "item":
            mesa.poe(b["seg0"], S.impacto(), ganho=0.35)
        if b["tipo"] == "quiz" and b["dados"].get("contagem"):
            for k in range(int(b["dados"]["contagem"])):
                mesa.poe(b["t1"] + k, tique(), ganho=0.9)
        if b["tipo"] == "revela":
            mesa.poe(b["seg0"], acerto(), ganho=0.8)
        if b["tipo"] == "voto":
            mesa.poe(b["seg0"], S.notificacao(), ganho=0.5)
    return mesa.gravar(saida_wav, duck=float(pa.get("ducking", 0.65)))


def gravar_linha(arq, linha):
    Path(arq).write_text(json.dumps(linha, ensure_ascii=False, indent=1), encoding="utf-8")
