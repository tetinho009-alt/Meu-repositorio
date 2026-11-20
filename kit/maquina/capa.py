# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Capa do episódio 1080x1920, layout "cartão e adesivo".

Composição: fundo liso com listras diagonais discretas; um cartão inclinado na cor de destaque (com retícula de
pontos) atrás do elenco; o elenco recortado como adesivo (borda clara e sombra dura) saltando para fora do cartão; o
selo redondo com o número da parte no canto do cartão. Embaixo, alinhado à esquerda: o título do episódio em
versal espaçada, o nome da série em fonte de cartaz (até duas linhas) e as duas opções do voto como etiquetas nas
cores das opções. Fontes: `fontes.capa_titulo` (cartaz) e `fontes.capa_apoio` (apoio) do config.

A pergunta da capa tem de repetir exatamente as opções do voto (regra aprendida): "ENTRAR OU FUGIR?" vira as
etiquetas ENTRAR (cor da opção 1) e FUGIR (cor da opção 2).
O elenco recortado sai de `elenco()`: os bonecos com a luz de cinema, fundo transparente.

Uma versão por rede (`rede`):
- ig: tudo dentro do recorte 3:4 da grade do perfil (y 240 a 1680), menos o @ do rodapé;
- tiktok: o app mostra a capa cortada em 3:4 e cobre a base com a contagem de views, então tudo cabe entre y 240 e
  1480; sem o @ (o app já mostra o perfil);
- youtube: Shorts aparece pequeno na prateleira, então é mais exagerada: o gancho gigante no alto em faixas de marca-
  texto, o elenco maior e mais saturado, o nome da série menor e sem a pergunta.
"""
import math
import re
from pathlib import Path

import skia
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from config import CFG, cor as cor_cfg, fonte_arquivo

from .cinema import boneco_iluminado
from .motor import Superficie
from .rig import Boneco

W, H = 1080, 1920
X0, LARG = 88, 904            # coluna de texto, alinhada à esquerda
BORDA_ADESIVO = 14            # px da borda clara em volta do elenco
SOMBRA_DURA = (14, 18)        # deslocamento da sombra sem desfoque (adesivo, cartão, etiquetas)

# Por rede: cartão (x0, y0, x1, y1), base do elenco, topo mínimo do elenco e limite de baixo do texto.
LAYOUT = {
    "ig": dict(cartao=(64, 330, 1016, 1060), base=1085, topo=250, texto=1112, limite=1664),
    "tiktok": dict(cartao=(64, 300, 1016, 900), base=925, topo=255, texto=950, limite=1470),
    "youtube": dict(cartao=(40, 560, 1040, 1470), base=1500, topo=470, texto=1525, limite=1840),
}


def elenco(atores, saida, cpu=False, chave=((255, 205, 150), (1.0, -0.6)), aro=None):
    """PNG com alfa do elenco, recortado no conteúdo. `atores` = [dict(nome, x, pe, altura, pose)].

    `aro` = (cor, direção, força) da luz de recorte; sem ele, a cor de destaque do canal clareada."""
    if aro is None:
        aro = (_misturar(cor_cfg("destaque"), (255, 255, 255), 0.55), (-1.0, -0.4), 0.7)
    sup = Superficie(W, H, cpu=cpu, transparente=True)
    c = sup.canvas
    c.clear(skia.Color(0, 0, 0, 0))
    for a in atores:
        b = Boneco(a["nome"])
        boneco_iluminado(c, b, a.get("x", W / 2), a.get("pe", 1500), a.get("altura", 1000), a.get("pose", {}),
                         chave=a.get("chave", chave), aro=a.get("aro", aro), exposicao=1.0, escuro_lado=0.35)
    buf = sup.ler()
    sup.fechar()
    im = Image.fromarray(buf[:, :, [2, 1, 0, 3]].copy(), "RGBA")
    caixa = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    Path(saida).parent.mkdir(parents=True, exist_ok=True)
    (im.crop(caixa) if caixa else im).save(saida)
    return saida


# ---------------------------------------------------------------- cor

def _misturar(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def _luminancia(c):
    def canal(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (canal(v) for v in c[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contraste(a, b):
    la, lb = sorted((_luminancia(a), _luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def _tinta_sobre(fundo_cor, escuro, claro):
    """A cor de texto (escura ou clara) que dá mais contraste sobre `fundo_cor`."""
    return escuro if _contraste(fundo_cor, escuro) >= _contraste(fundo_cor, claro) else claro


def _paleta():
    fundo = cor_cfg("fundo") if "fundo" in CFG["cores"] else (15, 20, 36)
    texto = cor_cfg("texto")
    return dict(fundo=fundo, texto=texto, destaque=cor_cfg("destaque"), op1=cor_cfg("opcao1"), op2=cor_cfg("opcao2"),
                suave=_misturar(texto, fundo, 0.32), sombra=_misturar(fundo, (0, 0, 0), 0.55))


# ---------------------------------------------------------------- texto

def _fonte(arq, tam):
    return ImageFont.truetype(str(arq), max(12, int(tam)))


def _caber(texto, arq, tam, larg, minimo=20):
    while tam > minimo:
        f = _fonte(arq, tam)
        if f.getlength(texto) <= larg:
            return f
        tam -= 2
    return _fonte(arq, minimo)


def _largura(texto, f, tracking=0.0):
    return f.getlength(texto) + tracking * f.size * max(0, len(texto) - 1)


def _escreve(img, x, y, texto, f, cor, tracking=0.0, sombra=None, contorno=0, cor_contorno=(0, 0, 0)):
    """Texto com o topo da caixa em y. `tracking` em fração do corpo; `sombra` = (cor, dx, dy) sem desfoque."""
    d = ImageDraw.Draw(img)
    passos = [(x, texto)] if not tracking else []
    if tracking:
        cx = x
        for ch in texto:
            passos.append((cx, ch))
            cx += f.getlength(ch) + tracking * f.size
    if sombra:
        cs, dx, dy = sombra
        for px, s in passos:
            d.text((px + dx, y + dy), s, font=f, fill=cs, stroke_width=contorno, stroke_fill=cs)
    for px, s in passos:
        d.text((px, y), s, font=f, fill=cor, stroke_width=contorno, stroke_fill=cor_contorno)


def _altura(f, texto="ÁG"):
    caixa = f.getbbox(texto)
    return caixa[3] - caixa[1], caixa[1]


def _quebra(texto, arq, tam_max, larg, alt_max, max_linhas=3):
    """Uma linha se couber grande; senão 2 ou 3, quebradas onde as linhas ficam mais parecidas. Devolve (linhas, fonte).
    Mais uma linha só entra se o corpo crescer de verdade (12%)."""
    palavras = texto.split()
    ref = _fonte(arq, 100)

    def equilibrada(n):
        melhor, pior_melhor = None, None
        cortes = [()]
        for _ in range(n - 1):
            cortes = [c + (k,) for c in cortes for k in range((c[-1] if c else 0) + 1, len(palavras))]
        for c in cortes:
            lim = (0, *c, len(palavras))
            linhas = [" ".join(palavras[lim[i]:lim[i + 1]]) for i in range(n)]
            pior = max(ref.getlength(l) for l in linhas)
            if pior_melhor is None or pior < pior_melhor:
                melhor, pior_melhor = linhas, pior
        return melhor

    opcoes = [[texto]] + [equilibrada(n) for n in range(2, min(max_linhas, len(palavras)) + 1)]
    escolha = None
    for linhas in opcoes:
        tam = tam_max
        while tam > 40:
            f = _fonte(arq, tam)
            if all(f.getlength(l) <= larg for l in linhas) and len(linhas) * tam * 1.0 <= alt_max:
                break
            tam -= 2
        if escolha is None or tam > escolha[1].size * 1.12:
            escolha = (linhas, _fonte(arq, tam))
    return escolha


def _opcoes_do_voto(pergunta):
    """'ENTRAR OU FUGIR?' -> ('ENTRAR', 'FUGIR'); None se a pergunta não tiver esse formato."""
    m = re.match(r"^\s*(.+?)\s+OU\s+(.+?)\s*\??\s*$", pergunta, re.I)
    return (m.group(1).strip(), m.group(2).strip()) if m else None


def _parte(pilula):
    """'PARTE 1 · ALGUÉM ACENOU' -> ('1', 'ALGUÉM ACENOU'); sem número, (None, texto)."""
    m = re.match(r"^\s*(?:PARTE|EP\.?|EPIS[OÓ]DIO)\s*(\d+)\s*(?:[·\-:|]\s*(.*))?$", pilula, re.I)
    if m:
        return m.group(1), (m.group(2) or "").strip()
    return None, pilula.strip()


# ---------------------------------------------------------------- peças

def _fundo(p):
    img = Image.new("RGB", (W, H), p["fundo"])
    d = ImageDraw.Draw(img)
    listra = _misturar(p["fundo"], p["destaque"], 0.07)
    passo, grossura = 64, 20
    for k in range(-H // passo, (W + H) // passo + 1):
        x = k * passo
        d.polygon([(x, 0), (x + grossura, 0), (x + grossura - H * 0.55, H), (x - H * 0.55, H)], fill=listra)
    # o pé da capa escurece para a área da legenda do app
    grad = Image.linear_gradient("L").resize((W, H)).point(lambda v: int(max(0, min(200, (v / 255 * H - 1400) / 520 * 200))))
    return Image.composite(Image.new("RGB", (W, H), p["sombra"]), img, grad)


def _camada_girada(desenho, caixa, angulo, escala=2):
    """Desenha numa camada 2x (antisserrilhado), gira em torno do centro da caixa e devolve (camada RGBA, x, y)."""
    x0, y0, x1, y1 = caixa
    folga = int(max(x1 - x0, y1 - y0) * 0.12) + 40
    lw, lh = int(x1 - x0) + 2 * folga, int(y1 - y0) + 2 * folga
    cam = Image.new("RGBA", (lw * escala, lh * escala), (0, 0, 0, 0))
    desenho(cam, (folga * escala, folga * escala, (lw - folga) * escala, (lh - folga) * escala), escala)
    cam = cam.rotate(angulo, resample=Image.BICUBIC).resize((lw, lh), Image.LANCZOS)
    return cam, int(x0) - folga, int(y0) - folga


def _cartao(img, caixa, p, angulo=-3.0):
    topo, base = _misturar(p["fundo"], p["destaque"], 0.55), _misturar(p["fundo"], p["destaque"], 0.30)
    ponto = _misturar(p["fundo"], p["destaque"], 0.72)

    def desenho(cam, r, e):
        x0, y0, x1, y1 = r
        mascara = Image.new("L", cam.size, 0)
        ImageDraw.Draw(mascara).rounded_rectangle(r, radius=56 * e, fill=255)
        grad = Image.linear_gradient("L").resize((int(x1 - x0), int(y1 - y0)))
        cor = Image.composite(Image.new("RGB", grad.size, base), Image.new("RGB", grad.size, topo), grad)
        cheio = Image.new("RGBA", cam.size, (0, 0, 0, 0))
        cheio.paste(cor, (int(x0), int(y0)))
        d = ImageDraw.Draw(cheio)
        passo = 30 * e   # retícula: os pontos crescem para o canto de baixo à direita
        for gy in range(int(y0), int(y1), int(passo)):
            for gx in range(int(x0), int(x1), int(passo)):
                t = ((gx - x0) / (x1 - x0) + (gy - y0) / (y1 - y0)) / 2
                raio = (1.0 + 6.5 * max(0.0, t - 0.35) / 0.65) * e
                if t > 0.35:
                    d.ellipse((gx - raio, gy - raio, gx + raio, gy + raio), fill=ponto)
        sombra = Image.new("RGBA", cam.size, (*p["sombra"], 0))
        sm = Image.new("L", cam.size, 0)
        ImageDraw.Draw(sm).rounded_rectangle([v + o * e for v, o in zip(r, (*SOMBRA_DURA, *SOMBRA_DURA))],
                                             radius=56 * e, fill=230)
        sombra.putalpha(sm)
        cam.alpha_composite(sombra)
        cheio.putalpha(mascara)
        cam.alpha_composite(cheio)

    cam, x, y = _camada_girada(desenho, caixa, angulo)
    img.paste(cam, (x, y), cam)


def _dilata(alfa, raio):
    for _ in range(raio // 2):
        alfa = alfa.filter(ImageFilter.MaxFilter(5))
    if raio % 2:
        alfa = alfa.filter(ImageFilter.MaxFilter(3))
    return alfa.filter(ImageFilter.GaussianBlur(1.2))


def _adesivo(img, arte, p, alt_max, larg_max, cx, base, tamanho, saturar=1.0, sangra=(), dissolve=()):
    """Cola o elenco como adesivo: borda clara, sombra dura, pés em `base`. Respeita as regras de recorte_elenco."""
    from recorte_elenco import destino, dissolve_lados, limpa, posicao_x
    st = Image.open(arte).convert("RGBA")
    if saturar != 1.0:
        alfa = st.getchannel("A")
        st = ImageEnhance.Color(st.convert("RGB")).enhance(saturar).convert("RGBA")
        st.putalpha(alfa)
    k = min(tamanho / max(st.size), alt_max / st.height, larg_max / st.width)
    st = st.resize((max(1, int(st.width * k)), max(1, int(st.height * k))), Image.LANCZOS)
    st = limpa(st)                                  # sem pontas finas (fio de cabelo vira espeto no contorno)
    diss, sang = destino(st, sangra, dissolve)      # lado cortado reto só com destino; a base dissolve sozinha
    st = dissolve_lados(st, diss)
    B = BORDA_ADESIVO
    M = B + max(SOMBRA_DURA) + 4
    alfa = Image.new("L", (st.width + 2 * M, st.height + 2 * M), 0)
    alfa.paste(st.getchannel("A"), (M, M))
    borda = _dilata(alfa, B)
    pos = (posicao_x(st.width, W, cx, sang) - M, int(base - st.height) - M)
    sombra = Image.new("RGBA", alfa.size, (*p["sombra"], 0))
    sombra.putalpha(borda.point(lambda v: int(v * 0.85)))
    img.paste(sombra, (pos[0] + SOMBRA_DURA[0], pos[1] + SOMBRA_DURA[1]), sombra)
    clara = Image.new("RGBA", alfa.size, (*p["texto"], 0))
    clara.putalpha(borda)
    img.paste(clara, pos, clara)
    img.paste(st, (pos[0] + M, pos[1] + M), st)


def _selo(img, cx, cy, numero, p, fapoio, ftitulo, raio=96, angulo=-8.0):
    """Selo redondo com 'PARTE' e o número grande."""
    tinta = p["fundo"]

    def desenho(cam, r, e):
        x0, y0, x1, y1 = r
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        d = ImageDraw.Draw(cam)
        sx, sy = SOMBRA_DURA[0] * 0.7 * e, SOMBRA_DURA[1] * 0.7 * e
        d.ellipse((mx - raio * e + sx, my - raio * e + sy, mx + raio * e + sx, my + raio * e + sy), fill=(*p["sombra"], 235))
        d.ellipse((mx - raio * e, my - raio * e, mx + raio * e, my + raio * e), fill=(*p["texto"], 255))
        fa = _fonte(fapoio, 26 * e)
        rot = "PARTE"
        larg = _largura(rot, fa, 0.18)
        _escreve(cam, mx - larg / 2, my - raio * e * 0.62, rot, fa, (*tinta, 255), tracking=0.18)
        fn = _caber(numero, ftitulo, 104 * e, raio * e * 1.5)
        h, topo = _altura(fn, numero)
        d.text((mx - fn.getlength(numero) / 2, my - raio * e * 0.22 - topo), numero, font=fn, fill=(*tinta, 255))

    caixa = (cx - raio, cy - raio, cx + raio, cy + raio)
    cam, x, y = _camada_girada(desenho, caixa, angulo)
    img.paste(cam, (x, y), cam)


def _etiquetas(img, x, y, op1, op2, p, ftitulo, fapoio, larg_max, alt=112, medir=False):
    """As duas opções do voto como etiquetas coloridas, com 'ou' entre elas: numa linha se couberem com corpo legível
    (>= 44 px), senão uma embaixo da outra. Devolve a altura usada; com `medir`, só mede."""
    fo = _fonte(fapoio, 40)
    meio = "ou"
    w_meio = fo.getlength(meio) + 36
    pad = 34

    def corpo(textos, larg):
        tam = 64
        while tam > 30 and sum(_fonte(ftitulo, tam).getlength(t) + 2 * pad for t in textos) > larg:
            tam -= 2
        return tam

    tam = corpo((op1, op2), larg_max - w_meio)
    linhas = [[(op1, p["op1"]), (op2, p["op2"])]]
    if tam < 44:   # duas linhas: cada etiqueta com a largura toda
        tam = min(corpo((op1,), larg_max), corpo((op2,), larg_max - w_meio))
        linhas = [[(op1, p["op1"])], [(op2, p["op2"])]]
    f = _fonte(ftitulo, tam)
    alt = min(alt, int(tam * 1.75))
    total = len(linhas) * (alt + 10) + (len(linhas) - 1) * 12
    if medir:
        return total
    d = ImageDraw.Draw(img)
    yy = y
    for k, linha in enumerate(linhas):
        cx = x
        if k == 1:   # na segunda linha, o "ou" abre a linha
            h, topo = _altura(fo, meio)
            d.text((cx, yy + (alt - h) / 2 - topo), meio, font=fo, fill=p["texto"])
            cx += w_meio - 18
        for i, (texto, cor) in enumerate(linha):
            w = f.getlength(texto) + 2 * pad
            d.rounded_rectangle((cx + 8, yy + 10, cx + w + 8, yy + alt + 10), radius=20, fill=p["sombra"])
            d.rounded_rectangle((cx, yy, cx + w, yy + alt), radius=20, fill=cor)
            h, topo = _altura(f, texto)
            d.text((cx + pad, yy + (alt - h) / 2 - topo), texto, font=f,
                   fill=_tinta_sobre(cor, p["fundo"], (255, 255, 255)))
            cx += w
            if i == 0 and len(linha) == 2:
                h, topo = _altura(fo, meio)
                d.text((cx + 18, yy + (alt - h) / 2 - topo), meio, font=fo, fill=p["texto"])
                cx += w_meio
        yy += alt + 10 + 12
    return total


# ---------------------------------------------------------------- capa

def capa(arte, pilula, serie, pergunta, linha_mono, saida, tamanho_arte=1000, perfil=None, rede="ig", gancho=None,
         sangra=(), dissolve=()):
    """Monta a capa. `arte` = PNG com alfa (elenco recortado ou outra arte própria). `pilula` = "PARTE N · título";
    `linha_mono` = a linha de apoio do rodapé (o nome ficou pela compatibilidade: a fonte é a de apoio, não mono).
    `rede` = ig, tiktok ou youtube; `gancho` = frase curta do topo na versão do YouTube (sem ela, o nome da série)."""
    p = _paleta()
    rede = "youtube" if rede == "shorts" else rede
    L = LAYOUT.get(rede, LAYOUT["ig"])
    ftitulo, fapoio = fonte_arquivo("capa_titulo"), fonte_arquivo("capa_apoio")
    numero, titulo_ep = _parte(pilula)
    img = _fundo(p)
    shorts = rede == "youtube"

    if not shorts:
        op = _opcoes_do_voto(pergunta)
        fk = _caber(titulo_ep.upper(), fapoio, 40, LARG)
        fl = _caber(linha_mono, fapoio, 32, LARG, minimo=22)
        alt_et = 112 if rede == "ig" else 100
        alt_op = _etiquetas(img, X0, 0, op[0], op[1], p, ftitulo, fapoio, LARG, alt=alt_et, medir=True) if op else 96
        # o que vem depois do nome da série: folga, etiquetas (ou a pergunta em texto), folga e a linha de apoio
        depois = 26 + alt_op + 28 + int(fl.size * 1.3)
        tam_max = 190 if rede == "ig" else 170

        def titulo(sobe):
            y0 = L["texto"] - sobe + (52 if titulo_ep else 0)
            return _quebra(serie, ftitulo, tam_max, LARG, L["limite"] - y0 - depois)

        # nome longo (ou opções longas) espremendo o título: o cartão e o elenco cedem até 220 px de altura
        sobe = 0
        linhas, ft = titulo(0)
        while ft.size < 100 and sobe < 220:
            sobe += 20
            linhas, ft = titulo(sobe)
        L = dict(L, cartao=(*L["cartao"][:3], L["cartao"][3] - sobe), base=L["base"] - sobe, texto=L["texto"] - sobe)

    cart = L["cartao"]
    _cartao(img, cart, p, angulo=-2.0 if shorts else -3.0)
    _adesivo(img, arte, p, L["base"] - L["topo"], 960 if shorts else 900, W / 2, L["base"],
             1080 if shorts else tamanho_arte, saturar=1.25 if shorts else 1.0, sangra=sangra, dissolve=dissolve)
    if numero:
        _selo(img, cart[0] + 92, cart[1] + 70, numero, p, fapoio, ftitulo, raio=84 if rede == "tiktok" else 96)

    y = L["texto"]
    if shorts:
        _gancho(img, (gancho or serie).upper(), p, ftitulo)
        fk = _caber(titulo_ep.upper(), fapoio, 36, LARG)
        _escreve(img, X0, y, titulo_ep.upper(), fk, _misturar(p["destaque"], (255, 255, 255), 0.45), tracking=0.08)
        y += 52
        linhas, ft = _quebra(serie, ftitulo, 110, LARG, L["limite"] - y)
        for ln in linhas:
            _escreve(img, X0, y, ln, ft, p["texto"], sombra=(p["sombra"], 0, 8))
            y += int(ft.size * 1.0)
    else:
        if titulo_ep:
            _escreve(img, X0, y, titulo_ep.upper(), fk, _misturar(p["destaque"], (255, 255, 255), 0.45), tracking=0.08)
            y += 52
        for ln in linhas:
            _escreve(img, X0, y, ln, ft, p["texto"], sombra=(p["sombra"], 0, 8))
            y += int(ft.size * 1.0)
        y += 26
        if op:
            y += _etiquetas(img, X0, y, op[0], op[1], p, ftitulo, fapoio, LARG, alt=alt_et)
        else:
            fq = _caber(pergunta, ftitulo, 80, LARG)
            _escreve(img, X0, y, pergunta, fq, p["op1"])
            y += int(fq.size * 1.2)
        y += 28
        _escreve(img, X0, y, linha_mono, fl, p["suave"], tracking=0.06 if fl.getlength(linha_mono) < LARG * 0.85 else 0)
        if rede == "ig":
            fp = _fonte(fapoio, 34)
            _escreve(img, X0, 1752, perfil or CFG["perfil"], fp, _misturar(p["suave"], p["fundo"], 0.2))
    Path(saida).parent.mkdir(parents=True, exist_ok=True)
    img.save(saida, quality=92)
    return saida


def _gancho(img, texto, p, ftitulo):
    """Gancho gigante do Shorts: uma ou duas linhas, cada uma numa faixa de marca-texto inclinada."""
    palavras = texto.split()
    if len(texto) <= 14 or len(palavras) < 2:
        linhas = [texto]
    else:
        meio = min(range(1, len(palavras)),
                   key=lambda k: abs(len(" ".join(palavras[:k])) - len(" ".join(palavras[k:]))))
        linhas = [" ".join(palavras[:meio]), " ".join(palavras[meio:])]
    tam = min(_caber(l, ftitulo, 180, LARG - 40, minimo=60).size for l in linhas)
    f = _fonte(ftitulo, tam)
    faixa = p["destaque"]
    tinta = _tinta_sobre(faixa, p["fundo"], (255, 255, 255))
    y = 110
    for i, ln in enumerate(linhas):
        h, topo = _altura(f, ln)
        w = f.getlength(ln)
        x = (W - w) / 2
        caixa = (x - 28, y - 18, x + w + 28, y + h + 22)
        ang = 2.0 if i % 2 == 0 else -1.5

        def desenho(cam, r, e, ln=ln, h=h, topo=topo):
            d = ImageDraw.Draw(cam)
            x0, y0, x1, y1 = r
            dx, dy = SOMBRA_DURA[0] * e * 0.8, SOMBRA_DURA[1] * e * 0.8
            d.rectangle((x0 + dx, y0 + dy, x1 + dx, y1 + dy), fill=(*p["sombra"], 235))
            d.rectangle(r, fill=(*faixa, 255))
            fe = _fonte(ftitulo, tam * e)
            d.text((x0 + 28 * e, y0 + 18 * e - topo * e), ln, font=fe, fill=(*tinta, 255))

        cam, cx, cy = _camada_girada(desenho, caixa, ang)
        img.paste(cam, (cx, cy), cam)
        y += int(h + 54)
