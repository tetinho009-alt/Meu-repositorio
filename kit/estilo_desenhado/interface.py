# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Interface do recorte de papel: tudo na tela é papel colado, nas cores e nas fontes do estilo do canal
(estilo.json): etiquetas cortadas na tesoura e presas com fita, letra recortada colada em papel escuro com a sombra
dura, selos de papel, confete.
Funções prontas para a série (legenda, abertura, intertítulo, voto, apuração, CTA):

    from estilo_desenhado import interface as UI
    UI.voto_cartao(c, t, t0, "O que a Lola faz?", [("Abrir", "...", "olho_aberto"), ("Fechar", "...", "olho_fechado")], ...)

O que NÃO muda por aqui: o CTA de cada rede e a cauda opcional do seu produto (cta_redes.py) e a chamada falada
pro comentário fixado (é do roteiro).

Texto: a fonte de título do estilo virada em caminho, colada num papel escuro um pouco maior, com a sombra dura e um
giro mínimo por palavra. Cor: o papel claro do estilo; palavra-chave na cor de destaque.
"""
import math
import random
from pathlib import Path

import numpy as np
import skia

from . import tinta as T

KIT = Path(__file__).resolve().parents[1]


def _pasta_fontes():
    try:
        from config import pasta
        return pasta("fontes")
    except Exception:  # fora do kit (teste isolado): a pasta padrão
        return KIT / "fontes"


FONTES = _pasta_fontes()
_PAL = T.ESTILO["paleta"]
TITULO, TEXTO = T.ESTILO["fontes"]["titulo"], T.ESTILO["fontes"]["texto"]
OSSO = T.mistura(T.PAPEL, (255, 255, 255), 0.25)            # texto claro sobre a cena
CREME = T.mistura(T.PAPEL, (255, 255, 255), 0.4)
FERRUGEM = T.DESTAQUE                                         # palavra-chave
TINTA_UI = T.TINTA
PAPEL_UI = T.mistura(T.PAPEL, (255, 255, 255), 0.15)           # etiqueta do voto e da regra
PERGAMINHO = (PAPEL_UI, PAPEL_UI)                              # nome antigo
OPCAO = tuple(tuple(c) for c in _PAL["opcoes"])                # as duas cores do voto
_F = {}


def fonte(nome, tam):
    k = (nome, tam)
    if k not in _F:
        _F[k] = skia.Font(skia.Typeface.MakeFromFile(str(FONTES / nome)), tam)
    return _F[k]


def cabe(s, tam, larg, nome=TITULO):
    """O maior corpo até `tam` em que o texto cabe em `larg` px: a fonte de título muda com o estilo e as largas
    (de cartaz, de faroeste) estouravam a moldura com o mesmo corpo."""
    while tam > 24 and fonte(nome, tam).measureText(s) > larg:
        tam -= 4
    return tam


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def _texto_caminho(s, tam, nome=TITULO):
    f = fonte(nome, tam)
    gl = f.textToGlyphs(s)
    pos = f.getPos(gl, skia.Point(0, 0))
    p = skia.Path()
    for g, q in zip(gl, pos):
        gp = f.getPath(g)
        if gp is not None:
            p.addPath(gp, q.x(), q.y())
    return p, f.measureText(s)


def texto_tinta(c, s, x, y, tam, cor=OSSO, t=0.0, centro=True, nome=TITULO, borda=None, a=255, rugoso=1.0, sombra=True,
                rot=0.0):
    """Texto de letra recortada: as letras na cor pedida, coladas num papel escuro um pouco maior (a borda), com a
    sombra dura deslocada e um giro mínimo por palavra (cada palavra é um recorte). Devolve a largura."""
    p, w = _texto_caminho(s, tam, nome)
    rnd = random.Random(T._sem(s, round(tam)))
    c.save()
    c.translate(x - (w / 2 if centro else 0), y)
    giro = rot + (rnd.uniform(-1.1, 1.1) * rugoso if rugoso else 0.0)
    if giro:
        c.rotate(giro, w / 2, -tam * 0.35)
    borda = borda if borda is not None else max(3.0, tam * 0.09)
    contorno = skia.Paint(AntiAlias=True, Color=T.cor_skia(TINTA_UI, a), Style=skia.Paint.kStrokeAndFill_Style, StrokeWidth=borda,
                          StrokeJoin=skia.Paint.kRound_Join)
    if sombra:   # sombra dura do recorte
        sx, sy = T.sombra_px(max(140.0, tam * 2.2))
        q = T.deslocado(p, sx, sy)
        ps = skia.Paint(contorno)
        ps.setColor(T.cor_sombra(a / 255))
        c.drawPath(q, ps)
    if borda > 0:
        c.drawPath(p, contorno)
    c.drawPath(p, skia.Paint(AntiAlias=True, Color=T.cor_skia(cor, a)))
    if tam >= 56:
        c.drawPath(p, T.fibra_paint(T._sem(s) % 997, 0.45 * a / 255))
    c.restore()
    return w


def texto_c(c, s, x, y, f, rgb=OSSO, a=255, contorno=0):
    """Compatível com maquina.desenho.texto_c (fonte já pronta): vira texto recortado no tamanho da fonte."""
    return texto_tinta(c, s, x, y, f.getSize(), rgb, a=a)


# ---------------------------------------------------------------- papel colado

def _ret(r):
    return np.array([(r.left(), r.top()), (r.right(), r.top()), (r.right(), r.bottom()), (r.left(), r.bottom())])


def fita(c, x, y, ang=0.0, larg=120.0, alt=36.0, a=255, semente=1):
    """Pedaço de fita adesiva transparente: a ponta rasgada em zigue-zague, um brilho fosco e a fibra por baixo."""
    rnd = random.Random(semente)
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    pts = [(-larg / 2, -alt / 2), (larg / 2, -alt / 2)]
    for k in range(5):   # ponta direita rasgada
        pts.append((larg / 2 + (4 if k % 2 else -2) + rnd.uniform(-1, 1), -alt / 2 + alt * (k + 1) / 6))
    pts += [(larg / 2, alt / 2), (-larg / 2, alt / 2)]
    for k in range(5):   # ponta esquerda rasgada
        pts.append((-larg / 2 + (-4 if k % 2 else 2) + rnd.uniform(-1, 1), alt / 2 - alt * (k + 1) / 6))
    path = T.caminho(np.array(pts))
    c.drawPath(path, T.tinta_paint((250, 252, 255), 110 * a / 255))
    c.drawPath(path, T.fibra_paint(semente, 0.25 * a / 255))
    c.drawPath(path, skia.Paint(AntiAlias=True, Color=T.cor_skia((255, 255, 255), 70 * a / 255), Style=skia.Paint.kStroke_Style,
                                StrokeWidth=1.2))
    c.restore()


def etiqueta(c, r, semente=1, t=0.0, a=255, escuro=False, borda_tinta=True, cor=None, fitas=2):
    """Etiqueta de papel colada com fita: retângulo cortado na tesoura, papel com fibra, o fio claro do corte, a
    sombra dura embaixo e dois pedaços de fita nos cantos de cima. `escuro`: papel escuro (intertítulo)."""
    cor = cor or (T.mistura(T.TINTA, T.PUXA, 0.4) if escuro else PAPEL_UI)
    if isinstance(cor, tuple) and len(cor) == 2 and isinstance(cor[0], (tuple, list)):
        cor = tuple(cor[0])
    q = T.tesoura(T.quina(_ret(r), True, 10), semente, amp=2.4, passo=16.0)
    forma = T.caminho(q)
    sx, sy = T.sombra_px(1000.0 * 0.95)
    c.drawPath(T.deslocado(forma, sx, sy), skia.Paint(AntiAlias=True, Color=T.cor_sombra(a / 255)))
    c.drawPath(forma, T.tinta_paint(cor, a))
    c.drawPath(forma, T.fibra_paint(semente, 0.4 * a / 255))
    c.drawPath(forma, T.borda_paint(cor, 1.6, a / 255))
    rnd = random.Random(semente)
    if fitas >= 1:
        fita(c, r.left() + 18, r.top() + 10, -38 + rnd.uniform(-6, 6), a=a, semente=semente + 1)
    if fitas >= 2:
        fita(c, r.right() - 18, r.top() + 10, 38 + rnd.uniform(-6, 6), a=a, semente=semente + 2)
    return forma


pergaminho = etiqueta   # nome antigo


def respingos(c, x, y, r, semente=1, a=255, cor=None):
    """Confete de papel: bolinhas e triângulos recortados nas cores do canal, com a sombra dura."""
    rnd = random.Random(semente)
    cores = [T.DESTAQUE] + list(T.PAPEIS)
    for k in range(7):
        ang = rnd.uniform(0, 2 * math.pi)
        dd = r * rnd.uniform(0.0, 3.0)
        px, py = x + math.cos(ang) * dd, y + math.sin(ang) * dd
        rr = r * rnd.uniform(0.35, 0.8)
        if k % 2:
            pts = T.elipse(px, py, rr, rr, 14)
        else:
            g = rnd.uniform(0, 6.28)
            pts = np.array([(px + rr * 1.3 * math.cos(g + j * 2.094), py + rr * 1.3 * math.sin(g + j * 2.094)) for j in range(3)])
        d = T.Desenho()
        T.peca(d, pts, cor or rnd.choice(cores), semente * 10 + k, sombra=0.8, alfa=a)
        d.desenha(c)


def moldura(c, r, t=0.0, a=255, cor=OSSO, semente=3):
    """Moldura de tiras de papel coladas por dentro da etiqueta (quatro tiras, cada uma levemente torta)."""
    rnd = random.Random(semente)
    d = T.Desenho()
    e = 9.0
    lados = [(r.left(), r.top(), r.right(), r.top()), (r.right(), r.top(), r.right(), r.bottom()),
             (r.right(), r.bottom(), r.left(), r.bottom()), (r.left(), r.bottom(), r.left(), r.top())]
    for k, (x0, y0, x1, y1) in enumerate(lados):
        dx, dy = x1 - x0, y1 - y0
        n = math.hypot(dx, dy) or 1
        nx, ny = -dy / n * e / 2, dx / n * e / 2
        j = rnd.uniform(-2, 2)
        pts = [(x0 - dx / n * 6 + nx + j, y0 - dy / n * 6 + ny), (x1 + dx / n * 6 + nx, y1 + dy / n * 6 + ny + j),
               (x1 + dx / n * 6 - nx, y1 + dy / n * 6 - ny + j), (x0 - dx / n * 6 - nx + j, y0 - dy / n * 6 - ny)]
        T.peca(d, T.quina(pts, True, 8), cor, semente * 7 + k, sombra=0.6, alfa=a)
    d.desenha(c)


def carimbo(c, texto, x, y, larg=None, tam=44, cor=FERRUGEM, rot=-6.0, a=255, t=0.0, semente=7, circular=False):
    """Selo de papel: uma tira da cor de destaque, recortada, colada torta com um pedaço de fita, e o texto em papel
    escuro por cima (nome antigo: carimbo)."""
    p, w = _texto_caminho(texto, tam, TITULO)
    larg = larg or w + tam * 1.1
    alt = tam * 1.6
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    r = skia.Rect.MakeLTRB(-larg / 2, -alt / 2, larg / 2, alt / 2)
    etiqueta(c, r, semente=semente, a=a, cor=cor, fitas=0)
    c.translate(-w / 2, tam * 0.36)
    c.drawPath(p, T.tinta_paint(TINTA_UI, a))
    c.restore()
    fita(c, x + math.cos(math.radians(rot)) * (larg / 2 - 10), y - alt / 2 + math.sin(math.radians(rot)) * (larg / 2), rot + 55,
         larg=80, alt=28, a=a, semente=semente + 5)


# ---------------------------------------------------------------- ícones desenhados à mão

def _ci(cor):
    """Cor de ícone -> papel colorido do canal (nada de creme)."""
    return T.papel_cor(cor, luz=(0.14, 0.9))


def icone(c, nome, cx, cy, r, rgb=TINTA_UI, a=255, w=None, t=0.0):
    """Ícone em peças de papel: vela, chave, olho (aberto/fechado), porta, mão, caveirinha de pássaro.
    Os nomes do kit de sempre caem no mais próximo (olho_aberto, olho_fechado, porta...)."""
    var = T.ferve(t)
    nome = {"olho_aberto": "olho", "abrir": "olho", "olho_fechado": "olho_fechado", "fechar": "olho_fechado", "fugir": "porta",
            "ler": "carta", "queimar": "vela", "vo": "terco", "vó": "terco", "rezar": "terco", "proteger": "vela_mao",
            "correr": "porta", "ficar": "vela", "esconder": "porta", "ligar": "mao", "chamar": "mao"}.get(nome, nome)
    d = T.Desenho()
    k = r / 60.0

    def P(pts):
        return [(cx + x * k, cy + y * k) for x, y in pts]
    if nome == "vela":
        T.forma(d, T.quina(P([(-14, -10), (14, -10), (16, 50), (-16, 50)]), True, 6), _ci((214, 200, 168)), var, 1, contorno=3.6 * k, sombra=0.7,
                passo_h=4 * k)
        T.linha(d, P([(-14, -6), (-18, 10), (-12, 22)]), 3 * k, var, 2)   # cera escorrendo
        T.forma(d, T.catmull(P([(0, -52), (8, -28), (4, -14), (-4, -14), (-8, -28)]), True, 6), _ci((226, 168, 80)), var, 3, contorno=2.6 * k,
                sombra=0.3, hach=False)
        T.linha(d, P([(0, -14), (0, -8)]), 2.4 * k, var, 4)
        T.forma(d, T.elipse(cx, cy + 52 * k, 34 * k, 8 * k, 20), _ci((110, 90, 70)), var, 5, contorno=3 * k, sombra=0.4, hach=False)
    elif nome == "chave":
        T.forma(d, T.elipse(cx - 26 * k, cy, 20 * k, 20 * k, 24), _ci((190, 170, 120)), var, 1, contorno=3.4 * k, sombra=0.6, passo_h=4 * k)
        d.pinta(T.caminho(T.elipse(cx - 26 * k, cy, 8 * k, 8 * k, 16)), T.tinta_paint(TINTA_UI))
        T.forma(d, T.quina(P([(-8, -5), (50, -5), (50, 5), (-8, 5)]), True, 6), _ci((190, 170, 120)), var, 2, contorno=3 * k, sombra=0.5, hach=False)
        for x in (34, 46):
            T.forma(d, T.quina(P([(x - 4, 5), (x + 4, 5), (x + 4, 20), (x - 4, 18)]), True, 4), _ci((190, 170, 120)), var, 3 + x, contorno=2.6 * k,
                    sombra=0.4, hach=False)
    elif nome in ("olho", "olho_fechado"):
        if nome == "olho":
            amd = T.catmull(P([(-50, 0), (-20, -24), (20, -24), (50, 0), (20, 22), (-20, 22)]), True, 8)
            T.forma(d, amd, _ci((226, 214, 188)), var, 1, contorno=3.6 * k, sombra=0.3, hach=False)
            T.forma(d, T.elipse(cx, cy, 15 * k, 15 * k, 20), _ci((110, 80, 50)), var, 2, contorno=2.6 * k, sombra=0.4, hach=False)
            d.pinta(T.caminho(T.elipse(cx, cy, 6 * k, 6 * k, 12)), T.tinta_paint(TINTA_UI))
            for j in range(5):
                T.linha(d, P([(-36 + 18 * j, -26), (-40 + 20 * j, -38)]), 2.2 * k, var, 10 + j, ponta=(0.0, 0.7))
        else:
            T.linha(d, P([(-50, 0), (0, 18), (50, 0)]), 4 * k, var, 1)
            for j in range(5):
                T.linha(d, P([(-34 + 17 * j, 12 + 4 * math.sin(j)), (-38 + 19 * j, 30)]), 2.4 * k, var, 10 + j, ponta=(0.0, 0.7))
            T.linha(d, P([(-12, 34), (-14, 48)]), 2.0 * k, var, 20, cor=(110, 120, 140))   # lágrima
    elif nome == "porta":
        T.forma(d, T.quina(P([(-30, 50), (-30, -40), (0, -56), (30, -40), (30, 50)]), True, 6), _ci((96, 72, 52)), var, 1, contorno=3.6 * k,
                sombra=0.8, passo_h=4 * k)
        T.forma(d, T.quina(P([(-6, 50), (-6, -30), (22, -40), (22, 50)]), True, 6), _ci((12, 8, 8)), var, 2, contorno=2.4 * k, sombra=0, hach=False)
        T.linha(d, P([(16, 0), (18, 4)]), 3 * k, var, 3)
    elif nome == "mao":
        palma = T.catmull(P([(-22, 50), (-26, 0), (-18, -6), (18, -6), (24, 4), (20, 50)]), True, 6)
        for j, x in enumerate((-18, -6, 6, 17)):
            comp = (46, 56, 54, 42)[j]
            T.forma(d, T.catmull(P([(x - 5, -2), (x - 4, -comp), (x, -comp - 6), (x + 4, -comp), (x + 5, -2)]), True, 4), _ci((214, 196, 160)), var,
                    3 + j, contorno=2.6 * k, sombra=0.4, hach=False)
        T.forma(d, palma, _ci((214, 196, 160)), var, 1, contorno=3.4 * k, sombra=0.6, passo_h=4 * k)
        T.forma(d, T.catmull(P([(-24, 22), (-42, 4), (-44, -10), (-36, -8), (-20, 6)]), True, 4), _ci((214, 196, 160)), var, 9, contorno=2.6 * k,
                sombra=0.4, hach=False)
    elif nome == "carta":   # carta velha suja de terra, com o lacre
        env = T.quina(P([(-48, -30), (48, -30), (48, 32), (-48, 32)]), True, 8)
        T.forma(d, env, _ci((214, 198, 160)), var, 1, contorno=3.2 * k, sombra=0.5, passo_h=4 * k)
        T.linha(d, P([(-46, -28), (0, 6), (46, -28)]), 2.6 * k, var, 2)
        T.forma(d, T.elipse(cx, cy + 4 * k, 9 * k, 9 * k, 16), _ci((130, 40, 34)), var, 3, contorno=2 * k, sombra=0.3, hach=False)
        for j in range(5):
            T.mancha(d, T.elipse(cx + (-30 + 14 * j) * k, cy + (20 - 6 * (j % 2)) * k, 8 * k, 5 * k, 12), _ci((90, 70, 50)), 150, borra=2 * k)
    elif nome == "terco":   # terço da vó: volta de contas, a medalhinha e a cruz pendurada
        for j in range(26):
            ang = math.pi * 2 * j / 26
            x, y = 34 * math.cos(ang), -12 + 28 * math.sin(ang)
            if 0.35 * math.pi < ang < 0.65 * math.pi:
                continue   # abre embaixo, onde desce a cauda
            T.forma(d, T.elipse(cx + x * k, cy + y * k, 4.6 * k, 4.6 * k, 10), _ci((150, 112, 74)), var, 10 + j, contorno=1.6 * k, sombra=0.3,
                    hach=False, amp=0.2)
        T.forma(d, T.elipse(cx, cy + 18 * k, 6.5 * k, 8 * k, 14), _ci((196, 184, 150)), var, 3, contorno=2 * k, sombra=0.3, hach=False)
        for j in range(3):
            T.forma(d, T.elipse(cx, cy + (30 + 8 * j) * k, 4 * k, 4 * k, 10), _ci((150, 112, 74)), var, 40 + j, contorno=1.4 * k, sombra=0.3, hach=False)
        T.forma(d, T.quina(P([(-3, 54), (3, 54), (3, 62), (11, 62), (11, 67), (3, 67), (3, 82), (-3, 82), (-3, 67), (-11, 67), (-11, 62),
                             (-3, 62)]), True, 3), _ci((190, 172, 132)), var, 4, contorno=2.2 * k, sombra=0.4, hach=False, amp=0.2)
    elif nome == "vela_mao":   # mão segurando a vela acesa
        T.forma(d, T.catmull(P([(0, -60), (9, -36), (4, -22), (-4, -22), (-9, -36)]), True, 6), _ci((226, 168, 80)), var, 3, contorno=2.6 * k,
                sombra=0.3, hach=False)
        T.linha(d, P([(0, -22), (0, -16)]), 2.4 * k, var, 4)
        T.forma(d, T.quina(P([(-12, -16), (12, -16), (13, 40), (-13, 40)]), True, 5), _ci((214, 200, 168)), var, 1, contorno=3.4 * k, sombra=0.6,
                passo_h=4 * k)
        T.linha(d, P([(-11, -12), (-15, 2), (-10, 12)]), 2.6 * k, var, 2)   # cera escorrendo
        palma = T.catmull(P([(-30, 18), (26, 14), (32, 32), (28, 52), (-24, 56), (-34, 38)]), True, 6)
        T.forma(d, palma, _ci((222, 190, 158)), var, 5, contorno=3.2 * k, sombra=0.5, hach=False)
        for j in range(4):   # os dedos fechados em volta da vela
            y = 22 + 9 * j
            T.linha(d, P([(-20, y), (2, y - 2), (20, y + 1)]), 1.8 * k, var, 20 + j, alfa=200)
        T.forma(d, T.catmull(P([(-30, 20), (-18, 8), (-6, 10), (-10, 22)]), True, 4), _ci((222, 190, 158)), var, 6, contorno=2.4 * k, sombra=0.3,
                hach=False)   # polegar por cima
        T.linha(d, P([(-24, 56), (-26, 70)]), 3 * k, var, 7)
        T.linha(d, P([(28, 52), (30, 70)]), 3 * k, var, 8)
    else:  # caveirinha de pássaro
        cranio = T.catmull(P([(-40, 0), (-34, -26), (-6, -34), (14, -22), (18, 0), (4, 14), (-24, 16)]), True, 8)
        T.forma(d, cranio, _ci((222, 210, 182)), var, 1, contorno=3.4 * k, sombra=0.7, passo_h=4 * k)
        T.forma(d, T.quina(P([(14, -16), (58, 6), (14, 4)]), True, 5), _ci((222, 210, 182)), var, 2, contorno=3 * k, sombra=0.5, hach=False)
        d.pinta(T.caminho(T.elipse(cx - 12 * k, cy - 10 * k, 10 * k, 10 * k, 14)), T.tinta_paint(TINTA_UI))
        T.linha(d, P([(-30, 6), (-20, 10), (-8, 8)]), 2 * k, var, 5)
    c.saveLayer(None, skia.Paint(Alphaf=a / 255))
    d.desenha(c)
    c.restore()


# ---------------------------------------------------------------- telas

def legenda(c, palavras, chave=(), y=1430, tema=None, fala=False, W=1080, a=255, t=None, larg=0.84):
    """Legenda: cada palavra é um recorte de letra clara colada em papel escuro, com a sombra dura; a palavra-chave
    vem na cor de destaque. `palavras` = [(t, p)] ou lista de strings. Quebra em linhas de até 84% da tela."""
    if t is None:
        t = 0.0
    vis = [(tp, p.upper()) for tp, p in palavras if tp <= t + 0.03] if palavras and isinstance(palavras[0], tuple) else \
        [(0.0, p.upper()) for p in palavras]
    if not vis:
        return
    tam = 84
    f = fonte(TITULO, tam)
    linhas, atual, lw_ = [], [], 0.0
    for tp, p in vis:
        w = f.measureText(p + " ")
        if lw_ + w > W * larg and atual:
            linhas.append((atual, lw_))
            atual, lw_ = [], 0.0
        atual.append((tp, p, w))
        lw_ += w
    if atual:
        linhas.append((atual, lw_))
    chaves = {k.upper() for k in chave}
    for i, (ln, lw) in enumerate(linhas[-2:]):
        x = (W - lw) / 2
        yy = y + i * (tam * 1.1)
        for tp, p, w in ln:
            u = ease((t - tp) / 0.12) if tp > 0 else 1.0
            cor = FERRUGEM if p.strip(".,!?") in chaves else OSSO
            # a palavra "cai" colada: entra um tico grande e assenta (em degraus de stop motion)
            texto_tinta(c, p, x, yy + (1 - u) * 10, tam, cor, t=t, centro=False, a=a * u, rugoso=1.0)
            x += w


def intertitulo(c, t, t0, texto, sub=None, dur=2.4, W=1080, H=1920):
    """Intertítulo: a tela cobre de papel escuro e uma etiqueta clara é colada no meio, com fita."""
    u = t - t0
    if not (0 <= u < dur):
        return
    k = ease(u / 0.25) * (1 - ease((u - dur + 0.3) / 0.3))
    c.drawRect(skia.Rect.MakeWH(W, H), T.tinta_paint(T.mistura(T.TINTA, T.SOMBRA, 0.4), 235 * k))
    c.drawRect(skia.Rect.MakeWH(W, H), T.fibra_paint(31, 0.5 * k, 1.8))
    r = skia.Rect.MakeXYWH(90, H * 0.36, W - 180, H * 0.26)
    etiqueta(c, r, semente=31, t=t, a=255 * k)
    texto_tinta(c, texto, W / 2, r.centerY() + (14 if not sub else -6), cabe(texto, 92, r.width() - 90), FERRUGEM, t=t, a=255 * k)
    if sub:
        texto_tinta(c, sub, W / 2, r.centerY() + 78, 40, TINTA_UI, t=t, a=255 * k, nome=TEXTO, borda=0, sombra=False, rugoso=0)


def cartao_regra(c, t, t0, n, texto, dur=3.4, W=1080, H=1920):
    """REGRA N: selo de papel + texto numa etiqueta clara colada com fita."""
    u = t - t0
    if not (0 <= u < dur):
        return
    k = ease(u / 0.25) * (1 - ease((u - dur + 0.3) / 0.3))
    r = skia.Rect.MakeXYWH(70, 300, W - 140, 330)
    etiqueta(c, r, semente=41 + n, t=t, a=245 * k)
    carimbo(c, f"REGRA {n}", W / 2, r.top() + 84, tam=46, a=255 * k, t=t, semente=n)
    texto_tinta(c, texto.upper(), W / 2, r.top() + 236, cabe(texto.upper(), 64, r.width() - 80), TINTA_UI, t=t, a=255 * k, borda=0,
                sombra=False)


def abertura(c, t, t0, serie, sub, W=1080, dur=2.6):
    """Selo da série: o nome em letra recortada, a parte num selo de papel colado com fita e um punhado de confete."""
    u = t - t0
    if not (0 <= u < dur):
        return
    k = ease(u / 0.3) * (1 - ease((u - dur + 0.35) / 0.35))
    y = 820
    texto_tinta(c, serie.upper(), W / 2, y, cabe(serie.upper(), 128, W - 120), OSSO, t=t, a=255 * k, rugoso=1.4)
    carimbo(c, sub.upper(), W / 2, y + 110, tam=48, a=255 * k * ease((u - 0.3) / 0.15), t=t, rot=-5)
    if u > 0.25:
        respingos(c, W - 130, y + 250, 12, semente=5, a=230 * k)


def selos_ficcao(c, topo, rodape, W=1080, H=1920, a=255):
    texto_tinta(c, topo, W / 2, 70, 30, T.mistura(T.PAPEL, (255, 255, 255), 0.3), a=a, nome=TEXTO, borda=3.0, sombra=False, rugoso=0)
    texto_tinta(c, rodape, W / 2, H - 52, 26, T.mistura(T.PAPEL, (255, 255, 255), 0.3), a=a, nome=TEXTO, borda=2.6, sombra=False,
                rugoso=0)


def voto_cartao(c, t, t0, pergunta, opcoes, duracao=5.0, W=1080, H=1920, rotulo="PARTE", numero=1, fundo=190, margem=90, topo=760, a=255):
    """Tela de voto em papel: duas etiquetas coladas tortas com fita, cada uma com o ícone num disco de papel da cor
    da opção, a palavra em letra recortada e o custo embaixo; selo "PARTE N · VOCÊ DECIDE" no alto."""
    u = t - t0
    if u < 0 or u > duracao:
        return
    k = ease(u / 0.3) * (1 - ease((u - duracao + 0.3) / 0.3))
    c.drawRect(skia.Rect.MakeWH(W, H), T.tinta_paint(T.SOMBRA, fundo * k))
    carimbo(c, f"{rotulo} {numero} · VOCÊ DECIDE", W / 2, topo - 250, tam=40, a=255 * k, t=t, rot=-3)
    texto_tinta(c, pergunta.upper(), W / 2, topo - 110, cabe(pergunta.upper(), 78, W - 80), OSSO, t=t, a=255 * k)
    alt_c = 250
    for i, (palavra, custo, ico) in enumerate(opcoes[:2]):
        ent = ease((u - 0.15 - 0.12 * i) / 0.35)
        y0 = topo + i * (alt_c + 50) + (1 - ent) * 80
        r = skia.Rect.MakeXYWH(margem, y0, W - 2 * margem, alt_c)
        c.save()
        balanco = 0.15 * math.sin(T.passo_stop(t) / 12.0 * 1.3 + i)
        c.rotate((-1.4 if i == 0 else 1.1) * (1 + balanco), r.centerX(), r.centerY())
        etiqueta(c, r, semente=60 + i, t=t, a=255 * k * ent)
        mx, my = r.left() + 130, r.centerY()
        disco = T.Desenho()   # disco de papel da cor da opção, com o ícone por cima
        T.peca(disco, T.elipse(mx, my, 86, 86, 48), OPCAO[i], 90 + i, sombra=1.4, alfa=255 * k * ent)
        T.peca(disco, T.elipse(mx, my, 70, 70, 40), T.mistura(OPCAO[i], (255, 255, 255), 0.55), 95 + i, sombra=0.6, alfa=255 * k * ent)
        disco.desenha(c)
        icone(c, ico, mx, my, 52, a=255 * k * ent, t=t)
        texto_tinta(c, palavra.upper(), r.left() + 250, r.centerY() + 14, cabe(palavra.upper(), 96, r.width() - 270), OPCAO[i], t=t,
                    centro=False, a=255 * k * ent, borda=5.0, rugoso=0.6)
        texto_tinta(c, custo, r.left() + 252, r.centerY() + 72, 32, TINTA_UI, t=t, centro=False, a=255 * k * ent,
                    nome=TEXTO, borda=0, sombra=False, rugoso=0)
        c.restore()
    # sem isca ("comenta 1 ou 2" é proibido) e sem número nos cartões: só a pergunta aberta
    texto_tinta(c, f"O QUE VOCÊS ESCOLHEREM VIRA A {rotulo} {numero + 1}", W / 2, topo + 2 * (alt_c + 50) + 70, 30,
                T.mistura(T.PAPEL, (255, 255, 255), 0.3), t=t, a=255 * k, nome=TEXTO, borda=3.0, sombra=False, rugoso=0)


def apuracao(c, t, t0, pergunta, opcoes, votos, parte=1, W=1080, H=1920, cores=OPCAO, aviso=None):
    """Contagem dos votos: duas barras de tiras de papel colorido coladas uma depois da outra numa etiqueta; o número
    sobe e a vencedora leva o selo. `votos` tem que ser a contagem real."""
    u = t - t0
    if u < 0:
        return
    total = max(1, sum(votos))
    c.drawRect(skia.Rect.MakeWH(W, H), T.tinta_paint(T.mistura(T.TINTA, T.SOMBRA, 0.4)))
    r = skia.Rect.MakeXYWH(70, 420, W - 140, 980)
    etiqueta(c, r, semente=77, t=t)
    texto_tinta(c, "A APURAÇÃO", W / 2, r.top() + 130, 86, FERRUGEM, t=t)
    texto_tinta(c, pergunta.upper(), W / 2, r.top() + 200, cabe(pergunta.upper(), 38, r.width() - 80, TEXTO), TINTA_UI, t=t, nome=TEXTO,
                borda=0, sombra=False, rugoso=0)
    vence = 0 if votos[0] >= votos[1] else 1
    for i, (nome, v) in enumerate(zip(opcoes, votos)):
        enche = ease((u - 0.5 - 0.2 * i) / 2.2) * v / total
        y = r.top() + 330 + i * 270
        texto_tinta(c, nome.upper(), r.left() + 70, y, 64, cores[i], t=t, centro=False, borda=4.0, rugoso=0.5)
        bx, by, bw, bh = r.left() + 70, y + 40, r.width() - 140, 90
        d = T.Desenho()
        T.peca(d, _ret(skia.Rect.MakeXYWH(bx, by, bw, bh)), T.mistura(T.PAPEL, T.TINTA, 0.18), 300 + i, sombra=0.5)
        if enche > 0.002:   # tiras de papel coladas lado a lado: a barra cresce em pedaços
            x1 = bx + 6 + (bw - 12) * enche
            n = max(1, int((x1 - bx) / 70) + 1)
            for j in range(n):
                xa = bx + 6 + j * 70
                xb = min(x1, xa + 76)
                if xb - xa < 6:
                    continue
                T.peca(d, _ret(skia.Rect.MakeLTRB(xa, by + 8 + (j % 2) * 2, xb, by + bh - 8 - (j % 2))), cores[i], 400 + 10 * i + j, sombra=0.6)
        d.desenha(c)
        pct = round(100 * ease((u - 0.5 - 0.2 * i) / 2.2) * v / total)
        texto_tinta(c, f"{pct}%", bx + bw - 140, y, 64, TINTA_UI, t=t, centro=False, borda=0, sombra=False, rugoso=0)
    if u > 3.0:
        y = r.top() + 330 + vence * 270 + 40
        carimbo(c, "VENCEU", r.right() - 170, y + 45, tam=50, rot=-12, a=255 * ease((u - 3.0) / 0.12), t=t)
    if aviso:
        texto_tinta(c, aviso, W / 2, r.bottom() - 70, 30, TINTA_UI, t=t, nome=TEXTO, borda=0, sombra=False, rugoso=0)


def cta(c, t, t0, linhas, W=1080, H=1920, y=1240, dur=3.0):
    """CTA da rede no mesmo universo: etiqueta colada com fita e a chamada em letra recortada."""
    u = t - t0
    if not (0 <= u < dur):
        return
    k = ease(u / 0.3)
    r = skia.Rect.MakeXYWH(80, y - 80, W - 160, 100 + 82 * len(linhas))
    c.drawRect(skia.Rect.MakeWH(W, H), T.tinta_paint((0, 0, 0), 150 * k))
    etiqueta(c, r, semente=88, t=t, a=255 * k)
    for j, ln in enumerate(linhas):
        texto_tinta(c, ln.upper(), W / 2, r.top() + 108 + j * 82, cabe(ln.upper(), 66, r.width() - 60), TINTA_UI, t=t, a=255 * k,
                    borda=0, sombra=False)
    respingos(c, r.right() - 30, r.top() + 20, 12, semente=9, a=220 * k)


def use_fone(c, t, t0=0.0, dur=3.0, W=1080):
    """Selinho "USE FONE" no alto: etiquetinha clara com o fone recortado."""
    u = t - t0
    if not (0 <= u < dur):
        return
    k = ease(u / 0.25) * (1 - ease((u - dur + 0.3) / 0.3))
    r = skia.Rect.MakeXYWH(W / 2 - 170, 124, 340, 66)
    etiqueta(c, r, semente=12, a=255 * k, fitas=1)
    texto_tinta(c, "USE FONE", W / 2 + 26, 170, 34, TINTA_UI, t=t, a=255 * k, nome=TEXTO, borda=0, sombra=False, rugoso=0)
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(W / 2 - 128, 136, 34, 34), 180, 180)
    c.drawPath(p, skia.Paint(AntiAlias=True, Color=T.cor_skia(TINTA_UI, 255 * k), Style=skia.Paint.kStroke_Style, StrokeWidth=4))
    for x in (W / 2 - 130, W / 2 - 96):
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 2, 148, 9, 15), 3, 3, T.tinta_paint(FERRUGEM, 255 * k))


def linha_misterio(c, t, texto, t0=0.0, dur=3.0, y=1500, W=1080):
    """A linha-mistério da abertura ("ela ainda está lá fora."), em minúscula, letra recortada clara, surgindo devagar."""
    u = t - t0
    if not (0 <= u < dur):
        return
    k = ease(u / 0.6) * (1 - ease((u - dur + 0.4) / 0.4))
    texto_tinta(c, texto, W / 2, y, 64, OSSO, t=t, a=255 * k, rugoso=1.3)
