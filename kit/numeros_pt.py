# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Números em algarismo de volta para extenso ("368" -> "trezentos e sessenta e oito", "55%" -> "cinquenta e cinco
por cento").

O Whisper escreve número em algarismo, e o roteiro tem o número por extenso (é assim que a voz fala). Sem esta troca,
o alinhamento não casa a palavra, e a fala com número escorrega para o bloco vizinho.
"""
import re

_U = "zero um dois três quatro cinco seis sete oito nove dez onze doze treze catorze quinze dezesseis dezessete " \
     "dezoito dezenove".split()
_D = "_ _ vinte trinta quarenta cinquenta sessenta setenta oitenta noventa".split()
_C = "_ cento duzentos trezentos quatrocentos quinhentos seiscentos setecentos oitocentos novecentos".split()


def _ate_mil(n):
    if n < 20:
        return _U[n]
    if n < 100:
        d, u = divmod(n, 10)
        return _D[d] + (f" e {_U[u]}" if u else "")
    if n == 100:
        return "cem"
    c, r = divmod(n, 100)
    return _C[c] + (f" e {_ate_mil(r)}" if r else "")


def extenso(n):
    """Inteiro de 0 a 999.999 por extenso."""
    n = int(n)
    if n < 1000:
        return _ate_mil(n)
    m, r = divmod(n, 1000)
    mil = "mil" if m == 1 else f"{_ate_mil(m)} mil"
    if not r:
        return mil
    liga = " e " if r < 100 or r % 100 == 0 else " "
    return mil + liga + _ate_mil(r)


def por_extenso(texto):
    """Troca cada número inteiro (com ou sem %) de até 6 dígitos pelo extenso."""
    def troca(m):
        num = int(m.group(1).replace(".", ""))
        return extenso(num) + (" por cento" if m.group(2) else "")
    return re.sub(r"\b(\d{1,3}(?:\.\d{3})?|\d{1,6})\b(\s?%)?", troca, texto)


if __name__ == "__main__":
    for t in ("368 flexões", "55%", "1.200 caracteres", "2015 views", "100", "101"):
        print(t, "->", por_extenso(t))
