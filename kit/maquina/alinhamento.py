# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Tempo de cada palavra DO ROTEIRO a partir das palavras ouvidas (Whisper) ou devolvidas pelo provedor de voz.

O alinhamento é por sequência (difflib) entre a grafia do roteiro e a ouvida: a legenda usa a grafia do roteiro,
nunca a do reconhecedor. Palavra não encontrada é interpolada pelas vizinhas.
Saída: [{"bloco", "palavra", "ini", "fim"}, ...]
"""
import difflib
import re
import unicodedata

TAG = re.compile(r"\[[^\]]*\]")


def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(ch for ch in s if ch.isalnum())


def sem_tags(texto):
    """Remove tags de direção de voz ([whispers], [pause]...) e espaços duplicados."""
    return " ".join(TAG.sub(" ", texto).split())


def palavras_de_caracteres(chars, ini, fim):
    """Converte o alinhamento por caractere (ElevenLabs) em [(palavra, ini, fim)], ignorando tags entre colchetes."""
    out, atual, t0, t1, dentro_tag = [], "", None, None, False
    for ch, a, b in zip(chars, ini, fim):
        if ch == "[":
            dentro_tag = True
        if dentro_tag:
            if ch == "]":
                dentro_tag = False
            continue
        if ch.isspace():
            if atual:
                out.append((atual, t0, t1))
            atual, t0 = "", None
            continue
        if t0 is None:
            t0 = a
        atual += ch
        t1 = b
    if atual:
        out.append((atual, t0, t1))
    return out


def alinhar_palavras(blocos, ouvidas):
    """`blocos` = textos do roteiro (um por bloco); `ouvidas` = [(palavra, ini, fim)]. Devolve (tempos, casadas)."""
    roteiro = [(b, p) for b, txt in enumerate(blocos) for p in sem_tags(txt).split()]
    a, b = [norm(p) for _, p in roteiro], [norm(w) for w, _, _ in ouvidas]
    tempos = [None] * len(roteiro)
    for bloco in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(bloco.size):
            tempos[bloco.a + k] = tuple(ouvidas[bloco.b + k][1:])
    conhecidos = [i for i, t in enumerate(tempos) if t]
    for i, t in enumerate(tempos):
        if t:
            continue
        ant = max((j for j in conhecidos if j < i), default=None)
        dep = min((j for j in conhecidos if j > i), default=None)
        t0 = tempos[ant][1] if ant is not None else 0.0
        t1 = tempos[dep][0] if dep is not None else t0 + 0.4
        n = (dep if dep is not None else i + 1) - (ant if ant is not None else -1)
        k = i - (ant if ant is not None else -1)
        tempos[i] = (t0 + (t1 - t0) * (k - 1) / n, t0 + (t1 - t0) * k / n)
    res = [{"bloco": bl, "palavra": p, "ini": round(float(t[0]), 3), "fim": round(float(t[1]), 3)}
           for (bl, p), t in zip(roteiro, tempos)]
    return res, len(conhecidos)


def resumo(res, blocos):
    linhas = []
    for bl in range(len(blocos)):
        ps = [s for s in res if s["bloco"] == bl]
        if ps:
            linhas.append(f"{bl}  {ps[0]['ini']:6.2f} {ps[-1]['fim']:6.2f}  " + " ".join(s["palavra"] for s in ps)[:60])
    return "\n".join(linhas)
