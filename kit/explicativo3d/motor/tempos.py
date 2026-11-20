# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Linha do tempo da narração: o tempos.json do `alinhar.py` do kit ([{"bloco", "palavra", "ini", "fim"}, ...]).

Python puro, sem dependência: roda tanto no Python do kit quanto dentro do Blender. Tudo no vídeo (câmera,
desmontagem, efeito sonoro, rótulo, legenda) é marcado por palavra da fala, nunca por segundo fixo: trocou a voz,
o vídeo inteiro se reajusta sozinho.
"""
import json
import re
import unicodedata
from pathlib import Path


def norm(s):
    """Minúsculo, sem acento e sem pontuação ("Água-viva," -> "aguaviva")."""
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if c.isalnum())


class Tempos:
    def __init__(self, caminho):
        self.palavras = json.loads(Path(caminho).read_text(encoding="utf-8"))
        if not self.palavras:
            raise ValueError(f"{caminho} está vazio")
        self.fim = self.palavras[-1]["fim"]

    def quando(self, palavra, depois=0.0, fim=False):
        """Início (ou fim) da 1ª palavra que começa com `palavra` a partir de `depois` segundos."""
        alvo = norm(palavra)
        for w in self.palavras:
            if w["ini"] >= depois and norm(w["palavra"]).startswith(alvo):
                return w["fim"] if fim else w["ini"]
        raise KeyError(f"a palavra '{palavra}' não está na narração (confira o narrador.txt e o tempos.json)")

    def legenda(self, destaques=()):
        """Legenda palavra a palavra: [[ini, fim, "TEXTO", destaque], ...].

        Palavras de até 2 letras grudam na seguinte para a tela não piscar, e cada palavra fica até a próxima entrar
        quando o intervalo é curto. `destaques`: palavras (sem acento, maiúsculas ou não) pintadas na cor de destaque.
        """
        alvo = {norm(d) for d in destaques}
        out, pend = [], None
        for w in self.palavras:
            txt = re.sub(r"[.,:;!…]+$", "", w["palavra"].upper()).replace("...", "")
            if not txt:
                continue
            if pend:
                txt, ini = pend[0] + " " + txt, pend[1]
                pend = None
            else:
                ini = w["ini"]
            if len(norm(txt)) <= 2 and not re.search(r"[.,:;!?…]$", w["palavra"]):
                pend = (txt, ini)
                continue
            out.append([round(ini, 3), round(w["fim"], 3), txt, any(norm(p) in alvo for p in txt.split())])
        for i in range(len(out) - 1):
            if out[i + 1][0] - out[i][1] < 0.35:
                out[i][1] = out[i + 1][0]
        return out
