# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Prepara o elenco recortado (PNG transparente) para a capa e barra o recorte malfeito.

Dois erros que vão ao ar fácil:
- a figura cortada pela borda do quadro de onde ela saiu vira uma linha reta no meio da capa, com contorno em volta;
- fio de cabelo solto e farpa do recorte viram espetos no contorno.

Regras:
- `limpa`: tira o semitransparente (brilho, sombra) e as pontas finas antes do contorno.
- Lado em que a figura encosta na borda da imagem é corte reto, e cada um precisa de destino:
  - a base (pé, corpo) se dissolve sozinha no escuro de baixo;
  - topo, esquerda e direita precisam de `--sangra <lado>` (o lado sai pra fora da capa; só esquerda e direita) ou
    `--dissolve <lado>` (o lado some em degradê). Sem isso, a capa é recusada.
"""
from PIL import Image, ImageChops, ImageDraw, ImageFilter

LIMIAR = 170   # abaixo disso é brilho ou sombra do recorte, não corpo
PONTA = 5      # some o que for mais fino que isso, em px na escala da capa (fio de cabelo)
MINIMO = 12    # px opacos encostados numa borda para contar como corte
SANGRIA = 24   # quanto o lado sangrado passa da beira da capa
FAIXA = 0.16   # fração do lado que se dissolve


class CapaRecusada(SystemExit):
    pass


def limpa(st):
    """Alfa só do corpo opaco, sem as pontas finas. Devolve uma cópia."""
    corpo = st.getchannel("A").point(lambda v: 255 if v > LIMIAR else 0)
    corpo = corpo.filter(ImageFilter.MinFilter(PONTA)).filter(ImageFilter.MaxFilter(PONTA))
    st = st.copy()
    st.putalpha(ImageChops.multiply(st.getchannel("A").point(lambda v: v if v > LIMIAR else 0), corpo))
    return st


def cortes(st):
    """Lados em que o corpo encosta na borda da imagem, com quantos px."""
    a = st.getchannel("A")
    w, h = a.size
    px = a.load()
    n = {"topo": sum(px[x, 0] > LIMIAR for x in range(w)), "base": sum(px[x, h - 1] > LIMIAR for x in range(w)),
         "esq": sum(px[0, y] > LIMIAR for y in range(h)), "dir": sum(px[w - 1, y] > LIMIAR for y in range(h))}
    return {k: v for k, v in n.items() if v >= MINIMO}


def destino(st, sangra=(), dissolve=(), nome="elenco"):
    """Decide o destino de cada lado cortado: devolve (lados a dissolver, lados a sangrar) ou recusa a capa."""
    c = cortes(st)
    sangra = [s for s in sangra if s in ("esq", "dir")]
    sem = [f"{lado} ({n} px)" for lado, n in c.items() if lado != "base" and lado not in sangra and lado not in dissolve]
    if sem:
        raise CapaRecusada(f"CAPA RECUSADA: o {nome} está cortado reto na borda {', '.join(sem)}. Esse corte ficaria no meio "
                           "da capa, com contorno. Refaça o recorte com a figura inteira, ou passe --sangra <lado> (encosta "
                           "na beira da capa) ou --dissolve <lado> (some em degradê).")
    diss = [lado for lado in c if lado == "base" or lado in dissolve]
    if c:
        print("elenco: corte reto em", ", ".join(f"{k} {v} px" for k, v in c.items()), "| dissolve:", diss or "-",
              "| sangra:", [s for s in sangra if s in c] or "-")
    return diss, [s for s in sangra if s in c]


def dissolve_lados(st, lados):
    """Leva o alfa a 0 em degradê nos lados pedidos (FAIXA do tamanho do lado)."""
    if not lados:
        return st
    w, h = st.size
    m = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(m)
    for lado in lados:
        n = max(1, int((h if lado in ("topo", "base") else w) * FAIXA))
        for i in range(n):
            v = int(255 * i / n)
            if lado == "base":
                d.line([(0, h - 1 - i), (w, h - 1 - i)], fill=v)
            elif lado == "topo":
                d.line([(0, i), (w, i)], fill=v)
            elif lado == "esq":
                d.line([(i, 0), (i, h)], fill=v)
            else:
                d.line([(w - 1 - i, 0), (w - 1 - i, h)], fill=v)
    st = st.copy()
    st.putalpha(ImageChops.multiply(st.getchannel("A"), m))
    return st


def posicao_x(largura, W, cx, sangra):
    """x do canto do elenco: centrado em cx, ou com o lado sangrado passando SANGRIA da beira da capa."""
    if "esq" in sangra and "dir" in sangra:
        if largura < W + 2 * SANGRIA:
            raise CapaRecusada("CAPA RECUSADA: esquerda e direita sangradas, mas o elenco não cobre a largura da capa.")
        return int((W - largura) / 2)
    if "esq" in sangra:
        return -SANGRIA
    if "dir" in sangra:
        return W - largura + SANGRIA
    return int(cx - largura / 2)


def prepara(st, sangra=(), dissolve=(), nome="elenco"):
    """limpa + destino + degradê: devolve (elenco pronto, lados sangrados)."""
    st = limpa(st)
    diss, sang = destino(st, sangra, dissolve, nome)
    return dissolve_lados(st, diss), sang
