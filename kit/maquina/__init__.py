# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Núcleo do kit: motor de render (GPU com queda para CPU), rig de boneco, perspectiva 3D, som, legenda, telas e capa.

Os módulos leem a configuração de `config.py` na raiz do kit.
"""
import sys
from pathlib import Path

_KIT = str(Path(__file__).resolve().parent.parent)
if _KIT not in sys.path:
    sys.path.insert(0, _KIT)


def slug(texto):
    """Nome de arquivo seguro em qualquer sistema: sem acento, minúsculo, com _ ("A Luz da Casa 7" -> a_luz_da_casa_7)."""
    import re
    import unicodedata

    s = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_") or "episodio"
