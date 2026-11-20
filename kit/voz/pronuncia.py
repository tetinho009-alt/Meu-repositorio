# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Troca de pronúncia para qualquer voz: os termos em inglês viram a grafia que a voz em português fala certo.

A tabela é `voz/pronuncia.json`, sincronizada a cada versão do kit. A troca vale só para o texto enviado à voz: a
legenda e a tela usam a grafia normal. Termo em inglês que não está na tabela não vai para a voz: reescreva a frase
(ex.: "aplicativo" em vez de "app") e mostre o nome só na tela.
"""
import json
import re
from functools import lru_cache
from pathlib import Path

ARQ = Path(__file__).with_name("pronuncia.json")
# Trocas do próprio canal (editadas pelo painel ou pela IA): valem antes das da base e sobrevivem às atualizações
ARQ_CANAL = Path(__file__).resolve().parents[2] / "canal" / "pronuncia.json"


def _le(arq):
    try:
        return json.loads(arq.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


@lru_cache(maxsize=1)
def _tabela():
    canal, base = _le(ARQ_CANAL), _le(ARQ)
    pares = list(canal.get("trocas", [])) + list(base.get("trocas", []))
    trocas = []
    for p, novo in pares:
        try:
            trocas.append((re.compile(p), novo))
        except re.error:
            trocas.append((re.compile(rf"\b{re.escape(p)}\b"), novo))
    fora = tuple(canal.get("fora_da_fala", [])) + tuple(base.get("fora_da_fala", []))
    return tuple(trocas), fora


def aplicar(texto):
    """Texto pronto para a voz (idempotente: aplicar duas vezes dá o mesmo resultado)."""
    trocas, _ = _tabela()
    for padrao, novo in trocas:
        texto = padrao.sub(novo, texto)
    return texto


def fora_da_fala(texto):
    """Termos que a tabela manda tirar da narração e que ainda aparecem no texto."""
    _, fora = _tabela()
    return [t for t in fora if re.search(rf"\b{re.escape(t)}\b", texto, re.I)]
