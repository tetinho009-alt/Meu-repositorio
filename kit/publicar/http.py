# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Cliente HTTP comum da publicação: modo seco (mostra o pedido e não envia), token mascarado no log e erro claro."""
import json
import re

from config import ErroConfig, segredo

_SENSIVEIS = re.compile(r"(access_token|token|key|secret|authorization|xi-api-key|refresh_token|client_secret)", re.I)
AUSENTE = "<TOKEN_AUSENTE_NO_SECO>"


class ErroAPI(RuntimeError):
    pass


def _mascara(d):
    if not isinstance(d, dict):
        return d
    return {k: ("***" if _SENSIVEIS.search(str(k)) and v else _mascara(v)) for k, v in d.items()}


def token(nome, seco):
    """Segredo pelo nome lógico; no modo seco, se faltar, usa um marcador (nada é enviado mesmo)."""
    try:
        return segredo(nome)
    except ErroConfig:
        if seco:
            return AUSENTE
        raise


class Cliente:
    def __init__(self, seco=False):
        self.seco = seco
        self.pedidos = []

    def pedido(self, metodo, url, *, params=None, data=None, json_=None, headers=None, corpo=None, falso=None,
               descricao="", ok=(200, 201)):
        """Envia (ou, no seco, só registra e mostra) um pedido. `corpo` = bytes ou caminho de arquivo a enviar.
        Devolve (resposta JSON ou {}, cabeçalhos)."""
        info = dict(metodo=metodo, url=url, params=_mascara(params), dados=_mascara(data), json=_mascara(json_),
                    cabecalhos=_mascara(headers), corpo=(f"<{len(corpo)} bytes>" if isinstance(corpo, (bytes, bytearray))
                                                         else (f"<arquivo {corpo}>" if corpo else None)))
        info = {k: v for k, v in info.items() if v not in (None, {}, [])}
        self.pedidos.append(info)
        if self.seco:
            print(f"[SECO] {descricao}\n" + json.dumps(info, ensure_ascii=False, indent=1), flush=True)
            return (falso or {}), {"Location": "https://seco.invalid/upload"}
        import requests

        if corpo is not None and not isinstance(corpo, (bytes, bytearray)):
            with open(corpo, "rb") as f:
                corpo = f.read()
        r = requests.request(metodo, url, params=params, data=corpo if corpo is not None else data, json=json_,
                             headers=headers, timeout=600)
        try:
            resp = r.json() if r.content else {}
        except ValueError:
            resp = {"texto": r.text[:500]}
        if r.status_code not in ok:
            raise ErroAPI(f"{descricao}: HTTP {r.status_code} {json.dumps(_mascara(resp), ensure_ascii=False)[:600]}")
        return resp, r.headers
