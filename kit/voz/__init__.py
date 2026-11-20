# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Adaptadores de voz com a mesma interface: texto + voz -> mp3 + tempos de palavra (quando o provedor dá).

    from voz import provedor
    res = provedor("kokoro").sintetizar("texto", "pm_alex", "audio/narrador.mp3")
    res.audio      # Path do mp3
    res.palavras   # [(palavra, ini, fim)] ou None (aí rode alinhar.py com Whisper)

Provedores:
- gemini (API do Google AI Studio, plano grátis, chave GEMINI_API_KEY): a voz grátis recomendada;
- elevenlabs (API, chave ELEVENLABS_API_KEY): a voz paga recomendada;
- azure (API, chave AZURE_SPEECH_KEY);
- kokoro e piper (locais, sem custo e sem internet);
- edge (SÓ TESTE: serviço sem licença comercial; bloqueado por padrão).
"""
import importlib
import sys
from pathlib import Path

_KIT = str(Path(__file__).resolve().parent.parent)
if _KIT not in sys.path:
    sys.path.insert(0, _KIT)

from .base import ErroVoz, ResultadoVoz, Voz  # noqa: E402

PROVEDORES = {
    "gemini": "voz.gemini:Gemini",
    "elevenlabs": "voz.elevenlabs:ElevenLabs",
    "azure": "voz.azure:Azure",
    "kokoro": "voz.kokoro_local:Kokoro",
    "piper": "voz.piper_local:Piper",
    "edge": "voz.edge_teste:EdgeTeste",
}


def provedor(nome):
    if nome not in PROVEDORES:
        raise ErroVoz(f"provedor de voz desconhecido: {nome}. Opções: {', '.join(PROVEDORES)}")
    mod, cls = PROVEDORES[nome].split(":")
    return getattr(importlib.import_module(mod), cls)()


__all__ = ["ErroVoz", "PROVEDORES", "ResultadoVoz", "Voz", "provedor"]
