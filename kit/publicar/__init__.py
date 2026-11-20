# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Publicação só pela API oficial de cada rede (Instagram Graph API, YouTube Data API, TikTok Content Posting API)
e resposta a comentários de voto no Instagram com limites conservadores.

Nada aqui curte, segue ou manda DM: isso não existe nas APIs oficiais para esse uso e robô fazendo isso derruba conta.
Todo comando aceita --seco: monta e mostra os pedidos (com o token mascarado) sem enviar nada.
"""
import sys
from pathlib import Path

_KIT = str(Path(__file__).resolve().parent.parent)
if _KIT not in sys.path:
    sys.path.insert(0, _KIT)
