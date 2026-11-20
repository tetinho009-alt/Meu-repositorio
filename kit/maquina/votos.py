# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Leitura de voto num comentário e apuração com um voto por perfil. Mesma regra do placar, da apuração do vídeo e
do robô de respostas (é o único lugar onde ela existe; `placar/preparar.py` copia este arquivo para o site).

Vale como voto:
- o NÚMERO da opção no começo ("2", "2 com certeza", "2222" conta como 2);
- a PALAVRA da opção entre as 3 primeiras palavras (sem acento, letra estilizada normalizada; forma curta ou longa
  com 4+ letras vale: PUXA = PUXAR = PUXARIA).
Não vale: citar as duas opções; negação ("não entra") sem regra `nega` da série. Com `nega = {"1": "2"}`, "não entra"
vira voto na opção 2. Sem a regra, o comentário fica de fora: melhor perder um voto do que contar errado.
"""
import re
import unicodedata

NEGA = {"NAO", "NUNCA", "JAMAIS", "NEM"}
_INICIO = re.compile(r"^[^\w]+", re.UNICODE)
_NUMERO = re.compile(r"^([0-9])\1*(?![^\W_])")


def sem_acento(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    return "".join(ch for ch in s if not unicodedata.combining(ch)).upper()


def _bate(w, p):
    return w == p or (len(w) >= 4 and (p.startswith(w) or w.startswith(p)))


def voto_do(texto, opcoes, nega=None, palavras_max=3):
    """`opcoes` = {"1": ["ENTRAR", "ENTRA"], "2": ["FUGIR", "CORRE"]}. Devolve "1", "2" ou None."""
    t = sem_acento(_INICIO.sub("", (texto or "").strip()))
    m = _NUMERO.match(t)
    if m and m.group(1) in opcoes:
        return m.group(1)
    ws = [w for w in re.split(r"[^\w]+", t) if w][:palavras_max]
    achou = set()
    for k, palavras in opcoes.items():
        ps = [sem_acento(p) for p in palavras]
        i = next((j for j, w in enumerate(ws) if any(_bate(w, p) for p in ps)), -1)
        if i < 0:
            continue
        if i > 0 and ws[i - 1] in NEGA:
            if not nega or k not in nega:
                return None
            achou.add(nega[k])
        else:
            achou.add(k)
    return achou.pop() if len(achou) == 1 else None


def apurar(comentarios, opcoes, nega=None):
    """`comentarios` = [{"quem", "texto", "data"}]. Um voto por perfil (o primeiro que valeu, em ordem de data).

    Devolve (contagem {"1": n, "2": n}, lista dos comentários que viraram voto, cada um com "opcao")."""
    contagem = {k: 0 for k in opcoes}
    vistos, validos = set(), []
    for c in sorted(comentarios, key=lambda x: str(x.get("data") or "")):
        v = voto_do(c.get("texto"), opcoes, nega)
        quem = c.get("quem") or f"{c.get('data')}|{c.get('texto')}"
        if v is None or quem in vistos:
            continue
        vistos.add(quem)
        contagem[v] += 1
        validos.append({**c, "opcao": v})
    return contagem, validos
