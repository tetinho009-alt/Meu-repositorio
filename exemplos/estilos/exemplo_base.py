# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Base dos exemplos de 10 s com personagem (série, POV, novela e terror): voz grátis por fala, tempo de cada palavra,
trilha e efeitos por código, masterização e render. Cada exemplo só escreve as falas e o desenho de cada quadro.

Fala = {"quem": "narrador" | nome do personagem, "fala": "...", "tela": "TEXTO GRANDE" (opcional), "pausa": s}.
As vozes saem do Kokoro (grátis, no computador): narrador pm_alex, Lola pf_dora, Nico pm_santa.
"""
import argparse
import json
import os
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
KIT = AQUI.parents[1] / "kit"
sys.path.insert(0, str(KIT))

from config import CFG, pasta  # noqa: E402

VOZES = {"narrador": "pm_alex", "lola": "pf_dora", "nico": "pm_santa", "narradora": "pf_dora"}


def argumentos():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", action="store_true", help="só os quadros-marco (conferência rápida)")
    ap.add_argument("--cpu", action="store_true", help="força render na CPU")
    return ap.parse_args()


class Linha:
    """Falas com o tempo real de cada uma e de cada palavra."""

    def __init__(self, d):
        self.d = d
        self.total = d["total"]
        self.falas = d["falas"]

    def fala(self, k):
        return self.falas[k]

    def janelas(self, k):
        """[(ini, fim, palavra)] da fala k, para a boca (visema) e a legenda."""
        ps = self.falas[k]["palavras"]
        out = []
        for i, (tp, p) in enumerate(ps):
            prox = ps[i + 1][0] if i + 1 < len(ps) else self.falas[k]["t1"]
            out.append((tp, min(prox, tp + 0.5), p))
        return out

    def de(self, quem):
        """Todas as janelas de palavra de um personagem (para a boca só mexer quando ele fala)."""
        out = []
        for k, f in enumerate(self.falas):
            if f["quem"] == quem:
                out += self.janelas(k)
        return out

    def atual(self, t):
        for k, f in enumerate(self.falas):
            if f["seg0"] <= t < f["seg1"]:
                return k
        return len(self.falas) - 1

    def legenda(self, t):
        """(palavras já ditas da fala da vez, quem fala)."""
        k = self.atual(t)
        f = self.falas[k]
        if t > f["t1"] + 0.35:
            return [], f["quem"]
        return [(tp, p) for tp, p in f["palavras"] if tp <= t + 0.03], f["quem"]


def preparar(nome, falas, clima="leve", efeitos=(), stills=False, cauda=1.9):
    """Grava as vozes que faltam, junta, alinha as palavras e mixa. Devolve (Linha, pasta de trabalho, áudio)."""
    trab = pasta("trabalho") / nome
    arq_linha = trab / "linha.json"
    if os.environ.get("MAQUINA_FATIA"):            # processo filho do render na CPU: só desenha
        return Linha(json.loads(arq_linha.read_text(encoding="utf-8"))), trab, None
    from cartelas import audio as AU
    from maquina import som as S
    import numpy as np

    trab.mkdir(parents=True, exist_ok=True)
    aud = trab / "audio"
    blocos = [{"fala": f["fala"], "pausa": f.get("pausa", 0.3)} for f in falas]
    blocos[-1]["pausa"] = cauda
    arqs = [None] * len(blocos)
    if not stills:
        for voz in {VOZES.get(f["quem"], "pm_alex") for f in falas}:
            so = [b if VOZES.get(f["quem"], "pm_alex") == voz else {**b, "fala": ""} for b, f in zip(blocos, falas)]
            for i, a in enumerate(AU.gerar_vozes(so, "kokoro", voz, aud)):
                arqs[i] = a or arqs[i]
    narr, janelas, total = AU.juntar(blocos, arqs if not stills else None)
    wav = None
    if not stills:
        wav = aud / "narracao.wav"
        S.gravar_wav(wav, np.stack([narr, narr], axis=1))
    por_fala, _, _ = AU.palavras(blocos, janelas, wav)
    out = []
    for i, (f, j, ws) in enumerate(zip(falas, janelas, por_fala)):
        seg0 = 0.0 if i == 0 else max(0.0, j["t0"] - 0.1)
        out.append({**f, "t0": j["t0"], "t1": j["t1"], "seg0": round(seg0, 3), "palavras": [[round(a, 3), p] for a, p in ws]})
    for a, b in zip(out, out[1:]):
        a["seg1"] = b["seg0"]
    out[-1]["seg1"] = round(total, 3)
    linha = Linha({"total": round(total, 3), "falas": out})
    arq_linha.write_text(json.dumps(linha.d, ensure_ascii=False, indent=1), encoding="utf-8")
    if stills:
        return linha, trab, None
    mesa = S.Mesa(total)
    mesa.poe(0.0, narr, voz=True)
    mesa.poe(0.0, AU.trilha_fundo(total, clima), ganho=0.55)
    for t0, som, ganho in efeitos(linha) if callable(efeitos) else efeitos:
        mesa.poe(max(0.0, t0), som, ganho=ganho)
    mesa.gravar(aud / "mix.wav", duck=0.65)
    from masterizar import masterizar
    A = CFG["audio"]
    final = aud / "mix_norm.wav"
    masterizar([aud / "mix.wav"], final, A["lufs"], A["pico_dbtp"], A["lra"], A["taxa"])
    return linha, trab, final


def pose_viva(t, quem, linha, pisca, extra=None, olhar=(0.0, 0.0)):
    """Pose de apoio do rig 2D: boca só na fala do próprio personagem, piscada irregular, respiração e cabeça viva."""
    import math
    from maquina.rig import piscar, respira, visema
    janelas = linha.de(quem)
    falando = any(a <= t < b for a, b, _ in janelas)
    pose = {"piscar": piscar(t, pisca), "tronco": respira(t), "visema": visema(t, janelas), "olhar": olhar,
            "cabeca": {"rot": (3.5 if falando else 1.5) * math.sin(t * (2.3 if falando else 0.9))}}
    for k, v in (extra or {}).items():
        pose[k] = {**pose.get(k, {}), **v} if isinstance(v, dict) and isinstance(pose.get(k), dict) else v
    return pose


def gancho(c, t, linhas, ate, cor_destaque=(255, 210, 63), y=560):
    """Texto grande já no quadro 0 (sem fade de entrada: o quadro 0 vira a miniatura) e some no fim do gancho."""
    from maquina.desenho import CX_SEGURO, LARG_SEGURA, caber, texto_c
    if t >= ate:
        return
    a = 255 * min(1.0, (ate - t) / 0.3)
    for i, (txt, destaque) in enumerate(linhas):
        f = caber("titulo", txt, 132, LARG_SEGURA, minimo=60)
        texto_c(c, txt, CX_SEGURO, y, f, cor_destaque if destaque else (255, 255, 255), a, contorno=12)
        y += f.getSize() * 1.05


def legenda(c, t, linha, chaves=(), ate=None, desde=None):
    from maquina.legenda import legenda as L
    if (ate is not None and t >= ate) or (desde is not None and t < desde):   # no gancho, o texto grande já diz
        return
    ps, _ = linha.legenda(t)
    if ps:
        L(c, t, [tuple(p) for p in ps], list(chaves))


def renderizar(quadro, linha, trab, audio, nome, args, marcos=None):
    from maquina.motor import renderizar as R
    marcos = marcos or [round(f["seg0"] + 0.6 * (f["seg1"] - f["seg0"]), 2) for f in linha.falas]
    saida = trab / f"{nome}.mp4"
    R(quadro, linha.total, saida, audio=audio, cpu=args.cpu, marcos=marcos, pasta_quadros=trab / "quadros",
      so_marcos=args.stills)
    print(("STILLS_OK " + str(trab / "folha.jpg")) if args.stills else ("VIDEO_OK " + str(saida)))
    return saida
