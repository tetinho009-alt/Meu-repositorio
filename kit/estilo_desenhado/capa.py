# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Capa do recorte de papel, no visual do estilo do canal (estilo.json): fundo de papel escuro com fibra, faixas de
papel rasgado, a caixa de papéis, a cor de destaque, as fontes e um de três layouts sorteados com o estilo
(etiqueta, colagem ou faixa); o elenco entra recortado, com a borda branca do papel e a sombra dura. Mesmo contrato da capa padrão: elenco recortado,
PARTE, série, gancho, pergunta e uma versão por rede (ig, tiktok, youtube), com as áreas seguras de sempre (recorte
3:4 de y 240 a 1680; no TikTok tudo sobe 200; no Shorts o gancho gigante no alto, elenco maior e sem a pergunta).
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from config import CFG, pasta
from recorte_elenco import posicao_x, prepara

from . import tinta as T
from .estilo import luminancia

W, H = 1080, 1920
E = T.ESTILO
PAPEL, TINTA, DESTAQUE = tuple(E["capa"]["fundo"]), tuple(E["capa"]["titulo"]), tuple(E["paleta"]["destaque"])
SOMBRA = tuple(E["paleta"]["sombra"])
TITULO_COR = tuple(E["capa"]["titulo"])
FIBRA = T.mistura(T.PAPEL, (255, 255, 255), 0.6)       # a borda branca do papel recortado
SDX, SDY = T.SOMBRA_DX * 1.4, T.SOMBRA_DY * 1.4        # sombra dura da capa (px)
TEXTURA = {"papel_velho": "fibra", "vhs": "reciclado", "pelicula": "fibra", "limpo": "cartolina"}.get(
    E["respostas"].get("textura"), E["respostas"].get("textura", "fibra"))
LAYOUT = {"moldura": "etiqueta", "diagonal": "colagem"}.get(E["capa"]["layout"], E["capa"]["layout"])


def _fonte(papel):
    return str(pasta("fontes") / E["fontes"][papel])


TITULO, TEXTO = _fonte("titulo"), _fonte("texto")


def _ruido(w, h, celula, semente):
    rng = np.random.default_rng(semente)
    g = Image.fromarray((rng.random((max(2, h // celula + 2), max(2, w // celula + 2))) * 255).astype(np.uint8), "L")
    return np.asarray(g.resize((w, h), Image.BICUBIC), dtype=np.float32) / 255.0


def _fibra(w, h, semente):
    """Fibra de papel (numpy, uma vez por capa): ondulação larga, fibra miúda e pintinhas no reciclado."""
    rng = np.random.default_rng(semente)
    n = 0.5 * _ruido(w, h, 160, semente) + 0.5 * _ruido(w, h, 6, semente + 1)
    v = 1.0 + 0.10 * (n - 0.5) * {"fibra": 1.4, "reciclado": 1.6, "seda": 1.0}.get(TEXTURA, 0.6)
    if TEXTURA == "reciclado":
        v = v - 0.25 * (rng.random((h, w)) < 0.0015)
    return v[..., None]


def _rasgo_y(w, y0, amp, semente, passo=6):
    """Borda de cima de uma faixa de papel rasgada (lista de pontos)."""
    rng = np.random.default_rng(semente)
    xs = np.arange(-10, w + 16, passo)
    ys = y0 + amp * np.sin(xs / 140 + semente) + rng.uniform(-amp * 0.25, amp * 0.25, len(xs))
    return list(zip(xs.tolist(), ys.tolist()))


def _fundo(cx, cy, semente=7):
    """Papel escuro do estilo com fibra, uma claridade atrás do elenco (luz por trás do papel) e duas faixas de papel
    rasgado da caixa de papéis no pé da capa (diorama)."""
    base = np.array(PAPEL, np.float32)[None, None, :] * _fibra(W, H, semente)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    luz = np.clip(1 - np.sqrt(((xx - cx) / 560) ** 2 + ((yy - cy) / 700) ** 2), 0, 1) ** 1.4
    base = base * (1 + 0.45 * luz[..., None]) + np.array(DESTAQUE, np.float32) * 0.10 * luz[..., None]
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB")
    papeis = sorted([tuple(p) for p in E["paleta"]["papeis"]], key=sum)
    for k, (y0, cor) in enumerate(((1500, papeis[1]), (1660, papeis[0]))):
        borda = _rasgo_y(W, y0, 22, semente + k)
        _peca(img, borda + [(W + 20, H + 20), (-20, H + 20)], cor)
    return img


def _peca(img, pts, cor, sombra=True, fibra=True):
    """Peça de papel colada na capa: sombra dura, a borda branca do papel e a peça por cima."""
    d = ImageDraw.Draw(img, "RGBA")
    if sombra:
        d.polygon([(x + SDX, y + SDY) for x, y in pts], fill=(*SOMBRA, 160))
    if fibra:
        d.polygon(pts, fill=(*FIBRA, 255))
        cx = sum(x for x, _ in pts) / len(pts)
        cy = sum(y for _, y in pts) / len(pts)
        pts = [(cx + (x - cx) * 0.99, cy + (y - cy) * 0.985 + 2) for x, y in pts]
    d.polygon(pts, fill=(*cor, 255))


def _ret(x0, y0, x1, y1, semente, amp=3.0):
    """Retângulo cortado na tesoura (as quinas e os lados fogem um pouco da linha)."""
    rng = np.random.default_rng(semente)
    out = []
    for (a, b, c_, e) in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)):
        n = max(2, int(math.hypot(c_ - a, e - b) / 40))
        for k in range(n):
            u = k / n
            out.append((a + (c_ - a) * u + rng.uniform(-amp, amp), b + (e - b) * u + rng.uniform(-amp, amp)))
    return out


def _fita(img, x, y, ang, larg=130, alt=40):
    """Pedaço de fita adesiva transparente com as pontas rasgadas."""
    s = Image.new("RGBA", (larg + 20, alt + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    pts = [(10, 10), (larg + 10, 10)] + [(larg + 10 + (4 if k % 2 else -2), 10 + alt * (k + 1) / 6) for k in range(5)]
    pts += [(larg + 10, alt + 10), (10, alt + 10)] + [(10 + (-4 if k % 2 else 2), alt + 10 - alt * (k + 1) / 6) for k in range(5)]
    d.polygon(pts, fill=(250, 252, 255, 120), outline=(255, 255, 255, 90))
    s = s.rotate(ang, resample=Image.BICUBIC, expand=True)
    img.paste(s, (int(x - s.width / 2), int(y - s.height / 2)), s)


def _layout(img, rede, sobe):
    """O desenho de papel que muda de estilo para estilo, atrás do texto."""
    if LAYOUT == "etiqueta":   # uma etiqueta clara grande, colada com fita, atrás do nome da série
        y0 = 1270 - sobe
        _peca(img, _ret(60, y0, W - 60, y0 + 400, 3), TITULO_COR)
        _fita(img, 110, y0 + 8, -35)
        _fita(img, W - 110, y0 + 8, 35)
    elif LAYOUT == "colagem":   # três tiras da caixa de papéis, tortas, uma sobre a outra
        papeis = [tuple(p) for p in E["paleta"]["papeis"]]
        for k, (y, g) in enumerate(((1260, -3.0), (1400, 2.0), (1530, -1.5))):
            y0 = y - sobe
            pts = [(40, y0 + g * 6), (W - 40, y0 - g * 6), (W - 46, y0 + 150 - g * 6), (46, y0 + 150 + g * 6)]
            _peca(img, pts, papeis[k % len(papeis)])
    else:   # faixa larga da cor de destaque, rasgada em cima e embaixo
        y0 = 1390 - sobe
        topo = _rasgo_y(W, y0 - 40, 14, 5)
        base = [(x, y + 430) for x, y in _rasgo_y(W, y0 - 40, 14, 9)][::-1]   # cobre até o rodapé
        _peca(img, topo + base, DESTAQUE)


def _elenco(img, caminho, recorte, cx, pe, alt_max, sangra=(), dissolve=()):
    """Cola o elenco como recorte: borda branca de papel em volta e a sombra dura deslocada. Antes,
    `recorte_elenco.prepara` tira as pontas finas e decide o destino de cada lado cortado reto (base dissolve; topo e
    laterais pedem `sangra` ou `dissolve`, senão a capa é recusada)."""
    st = Image.open(caminho).convert("RGBA")
    if recorte:
        st = st.crop((int(recorte[0] * st.width), int(recorte[1] * st.height), int(recorte[2] * st.width), int(recorte[3] * st.height)))
    k = min(1060 / st.width, alt_max / st.height)
    st = st.resize((int(st.width * k), int(st.height * k)), Image.LANCZOS)
    st, sang = prepara(st, sangra, dissolve)
    a = st.getchannel("A").point(lambda v: 255 if v > 170 else 0)
    M = 40
    grande = Image.new("L", (st.width + 2 * M, st.height + 2 * M), 0)
    grande.paste(a, (M, M))
    contorno = grande.filter(ImageFilter.MaxFilter(15))
    x0, y0 = posicao_x(st.width, W, cx, sang), int(pe - st.height)
    img.paste(SOMBRA, (x0 - M + int(SDX * 2.4), y0 - M + int(SDY * 2.4)), contorno.point(lambda v: int(v * 0.7)))
    img.paste(FIBRA, (x0 - M, y0 - M), contorno)
    img.paste(st, (x0, y0), st)


def _caber(texto, fonte, tam, larg):
    while tam > 20:
        f = ImageFont.truetype(fonte, tam)
        if f.getlength(texto) <= larg:
            return f
        tam -= 4
    return ImageFont.truetype(fonte, tam)


def _texto(img, texto, y, f, cor, borda, contorno=6, x=None):
    w = f.getlength(texto)
    x = (W - w) / 2 if x is None else x
    ImageDraw.Draw(img).text((x, y), texto, font=f, fill=cor, stroke_width=contorno, stroke_fill=borda)


def _selo(img, texto, x, y, tam, gira):
    """A PARTE num selo de papel da cor de destaque, cortado torto e preso com fita."""
    f = ImageFont.truetype(TEXTO, tam)
    tw = int(f.getlength(texto))
    larg, alt = tw + tam + 40, int(tam * 1.9) + 40
    s = Image.new("RGBA", (larg + 40, alt + 40), (0, 0, 0, 0))
    _peca(s, _ret(20, 20, larg, alt, 11, amp=2.0), DESTAQUE)
    ImageDraw.Draw(s).text((20 + tam / 2 + 10, 20 + tam * 0.45), texto, font=f, fill=T.TINTA)
    s = s.rotate(gira, resample=Image.BICUBIC, expand=True)
    img.paste(s, (int(x), int(y)), s)
    _fita(img, x + s.width - 30, y + 26, 40, larg=90, alt=30)
    return s.width


def gera(elenco, parte, serie, gancho, pergunta, saida, rede="ig", recorte=None, perfil=None, sangra=(), dissolve=()):
    """`rede`: ig, tiktok ou youtube (Shorts: gancho gigante no alto, elenco maior e sem a pergunta). `sangra` e
    `dissolve`: o destino dos lados em que o elenco está cortado reto (ver recorte_elenco)."""
    perfil = perfil or CFG["perfil"]
    shorts = rede in ("youtube", "shorts")
    sobe = 200 if rede == "tiktok" else 0
    cx, cy = W / 2, 820 - sobe
    img = _fundo(cx, cy)
    _layout(img, rede, sobe)
    # texto claro onde o fundo é escuro (diagonal) e escuro onde é claro
    claro, escuro = T.mistura(T.PAPEL, (255, 255, 255), 0.4), T.TINTA
    fundo_texto = DESTAQUE if LAYOUT == "faixa" else (TITULO_COR if LAYOUT == "etiqueta" else PAPEL)
    sobre_escuro = luminancia(fundo_texto) < 0.3
    cor, borda = (claro, escuro) if sobre_escuro else (escuro, claro)
    alt_max = 1240 if shorts else (900 if rede == "tiktok" else 1080)
    pe = (1460 if shorts else 1380) - sobe
    _elenco(img, elenco, recorte, cx, pe, alt_max, sangra, dissolve)
    if shorts:
        palavras = gancho.split()
        meio = len(palavras) // 2 + len(palavras) % 2
        linhas = [gancho] if len(gancho) <= 14 else [" ".join(palavras[:meio]), " ".join(palavras[meio:])]
        tam = min(_caber(l, TITULO, 210, 1000).size for l in linhas)
        fgg = ImageFont.truetype(TITULO, tam)
        y = 150
        for l in linhas:
            _texto(img, l, y, fgg, DESTAQUE, T.TINTA, contorno=12)
            y += int(tam * 1.05)
        larg = _selo(img, parte, 24, 1420, 60, 5)
        _texto(img, serie, 1450, _caber(serie, TITULO, 150, 1000 - larg), cor, borda, x=larg + 40)
        fm = ImageFont.truetype(TEXTO, 30)
        ImageDraw.Draw(img).text(((W - fm.getlength(perfil)) / 2, 1700), perfil, font=fm, fill=cor)
    else:
        _selo(img, parte, 50 if rede == "ig" else W - 360, 262 if rede == "ig" else 1240 - sobe, 56, 6 if rede == "ig" else -5)
        fg = _caber(gancho, TITULO, 92, 940)
        _texto(img, gancho, 1290 - sobe, fg, DESTAQUE, T.TINTA, contorno=8)
        y = 1300 - sobe + fg.size + 20
        ft = _caber(serie, TITULO, 180, 1000)
        _texto(img, serie, y, ft, cor, borda, contorno=7)
        fq = _caber(pergunta, TITULO, 90, 960)
        _texto(img, pergunta, y + ft.size + 30, fq, cor, borda, contorno=5)
        fm = ImageFont.truetype(TEXTO, 30)
        rodape = f"{perfil} · ficção"
        ImageDraw.Draw(img).text(((W - fm.getlength(rodape)) / 2, y + ft.size + fq.size + 80), rodape, font=fm, fill=cor)
    Path(saida).parent.mkdir(parents=True, exist_ok=True)
    img.save(saida, quality=92)
    return saida


def elenco(nomes, saida, altura=1150):
    """PNG transparente com o elenco em papel recortado e com medo (o primeiro nome maior, à frente). Aceita nome ou
    papel do elenco do estilo ("protagonista", "adulto", "idoso")."""
    import skia
    from .elenco import pessoa
    from .personagem import pose_medo
    n = len(nomes)
    sup = skia.Surface.MakeRaster(skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kUnpremul_AlphaType))
    c = sup.getCanvas()
    c.clear(skia.Color4f(0, 0, 0, 0))
    for k in reversed(range(n)):
        b = pessoa(nomes[k])
        x = W / 2 + (k - (n - 1) / 2) * 380
        b.desenhar(c, x, 1800, altura if k == 0 else altura * 0.88, pose_medo(1.0, t=0.0, olhar=(0.5 if k == 0 else -0.5, -0.2)))
    img = Image.fromarray(sup.toarray(colorType=skia.kRGBA_8888_ColorType), "RGBA")
    caixa = img.getbbox()
    if caixa:
        img = img.crop(caixa)
    Path(saida).parent.mkdir(parents=True, exist_ok=True)
    img.save(saida)
    return saida
