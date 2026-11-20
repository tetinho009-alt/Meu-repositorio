# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Confere, por estimativa, se um @ parece livre no .com, no Instagram, no YouTube e no TikTok.

É uma heurística: faz uma consulta leve a cada site (sem login, sem navegador, sem cookie de conta) e lê a
resposta. Os sites mudam e às vezes bloqueiam a consulta; aí o resultado é "não deu para saber". A confirmação
de verdade é criar a conta no app de cada rede.

Uso, a partir de kit/:  python painel/arroba.py nome_do_canal
"""
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

FORMATO = re.compile(r"^[a-z0-9._]{1,30}$")
TEMPO_LIMITE_S = 8
UA_PREVIA = "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)"
UAS_TIKTOK = ["Twitterbot/1.0", "TelegramBot (like TwitterBot)", "WhatsApp/2.23.20.0", UA_PREVIA]
LIVRE, OCUPADO, INCERTO = "livre", "ocupado", "incerto"


def formato(nome):
    """(ok, mensagem) do formato do @: o mesmo nas quatro redes."""
    n = str(nome or "").strip().lstrip("@").lower()
    if not n:
        return False, "Escreva o @ primeiro."
    if not FORMATO.match(n):
        return False, "Use só letras sem acento, números, ponto e sublinhado, até 30, sem espaço."
    if n.startswith(".") or n.endswith(".") or ".." in n:
        return False, "O Instagram não aceita ponto no começo, no fim ou dois pontos seguidos."
    if len(n) > 24:
        return True, "O TikTok aceita até 24 letras: com mais que isso, o @ não fica igual em todas."
    return True, ""


def _get(url, ua=UA_PREVIA):
    cab = {"User-Agent": ua, "Accept-Language": "pt-BR,pt;q=0.9", "Cookie": "CONSENT=YES+1; SOCS=CAI"}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=cab), timeout=TEMPO_LIMITE_S) as r:
            return r.status, r.read(600_000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:  # noqa: BLE001
        return -1, ""


def dominio_com(n):
    st, _ = _get(f"https://rdap.verisign.com/com/v1/domain/{n}.com")
    return {404: LIVRE, 200: OCUPADO}.get(st, INCERTO)


def instagram(n):
    st, pagina = _get(f"https://www.instagram.com/{n}/")
    if st == 404:
        return LIVRE
    if st != 200:
        return INCERTO
    return OCUPADO if re.search(r'property="og:image"', pagina) else LIVRE


def youtube(n):
    st, _ = _get(f"https://www.youtube.com/@{n}", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130.0")
    return {404: LIVRE, 200: OCUPADO}.get(st, INCERTO)


def tiktok(n):
    for tentativa in range(2):
        st, pagina = _get(f"https://www.tiktok.com/@{n}", UAS_TIKTOK[tentativa % len(UAS_TIKTOK)])
        if st in (200, 404):
            if re.search(r'og:description" content="@%s ' % re.escape(n), pagina, re.I):
                return OCUPADO
            if "Visit TikTok to discover profiles" in pagina or "Visite o TikTok para descobrir perfis" in pagina:
                return LIVRE
        time.sleep(2)
    return INCERTO


CONFERE = {"com": dominio_com, "instagram": instagram, "youtube": youtube, "tiktok": tiktok}


def conferir(nome):
    """{"nome", "formato", "aviso", "redes": {rede: livre|ocupado|incerto}}. Nunca levanta exceção."""
    n = str(nome or "").strip().lstrip("@").lower()
    ok, msg = formato(n)
    if not ok:
        return {"nome": n, "formato": False, "aviso": msg, "redes": {}}
    with ThreadPoolExecutor(max_workers=len(CONFERE)) as ex:
        futuros = {r: ex.submit(f, n) for r, f in CONFERE.items()}
        redes = {}
        for r, fut in futuros.items():
            try:
                redes[r] = fut.result(timeout=TEMPO_LIMITE_S * 3)
            except Exception:  # noqa: BLE001
                redes[r] = INCERTO
    return {"nome": n, "formato": True, "aviso": msg, "redes": redes}


if __name__ == "__main__":
    for fluxo in (sys.stdout,):
        try:
            fluxo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    for alvo in sys.argv[1:]:
        r = conferir(alvo)
        print(r["nome"], r["aviso"] or "", " ".join(f"{k}={v}" for k, v in r["redes"].items()))
