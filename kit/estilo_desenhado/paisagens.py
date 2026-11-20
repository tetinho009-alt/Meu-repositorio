# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Planos abertos em diorama de papel: primeiro plano (capim de papel recortado em zigue-zague, cerca, lampião),
meio (casas de papel dobrado, cruzes, capela, poço, porteira) e fundo (morros em faixas de papel, árvore de papel, lua
de papel com o halo da luz atrás e nuvens recortadas), com camadas de papel de seda entre os planos.

Tudo 3D de verdade (câmera `CamG`, com paralaxe quando ela anda): cada camada é uma peça que projeta a sombra dura na
de trás. Cenas: cemiterio(), estrada_neblina(), cidadezinha(), quintal(). Cada uma recebe `cam` (ou usa a dela),
`atores=[(X, Z, desenha, altura_m[, Y])]` e `extras(cena)`. Com a câmera andando (grua, travelling), passe também
`ref` = a câmera do primeiro quadro do plano: o mato do primeiro plano vira objeto do mundo (paralaxe de verdade) em
vez de ficar grudado na tela. Câmera que gira declara `cam.ceu_ref = (yaw, pitch)` do céu composto.
"""
import math
import random

import numpy as np
import skia

from . import tinta as T
from .cenario3d import (LAMPADA, LUA, W, H, CamG, Cena, _fixa, arvore_seca, ceu_noite, fio, mato, nuvens, poste, rachadura, tex_parede,
                        tex_tabuas, tex_telhas, torto, janela, _n, lua_do_estilo)

PAPEL_NOITE = ((6, 8, 14), (22, 26, 38), (96, 100, 104))
# Neblina de luar: papel de seda frio, mais claro que as silhuetas de perto; cada camada que se afasta clareia (é o
# que separa os planos do diorama).
NEVOA_LUAR = T.mistura(T.PUXA, T.PAPEL, 0.45)


# ---------------------------------------------------------------- relevo

class Relevo:
    """Morros como soma de lombadas gaussianas: altura(X, Z) em metros."""

    def __init__(self, lombadas):
        self.lomb = lombadas   # [(x0, z0, sx, sz, alt)]

    def __call__(self, X, Z):
        return sum(a * math.exp(-((X - x0) / sx) ** 2 - ((Z - z0) / sz) ** 2) for x0, z0, sx, sz, a in self.lomb)


def morro_fatias(cena, relevo, x0, x1, z0, z1, n=14, cor=(58, 62, 58), passo_x=1.2, rim=0.9, semente=1, zorder=None, curvas=True):
    """Morro em fatias de profundidade (do fundo pra frente), cada fatia uma faixa de papel na mesma cor, então viram
    uma massa só; o perfil de cada fatia aparece só como um fio fino (o corte da faixa de cima)."""
    zs = np.linspace(z1, z0, n)
    xs = np.arange(x0, x1 + passo_x, passo_x)
    alto_max = max(max(relevo(X, Z) for X in xs) for Z in zs) or 1.0
    i_cume = int(np.argmax([max(relevo(X, Z) for X in xs) for Z in zs]))
    for i, Z in enumerate(zs):
        topo = [(X, relevo(X, Z), Z) for X in xs]
        alto = max(p[1] for p in topo)
        if alto < 0.15:
            continue
        pts = topo + [(x1, -0.5, Z), (x0, -0.5, Z)]
        sid = semente * 1000 + i
        cume = i == i_cume

        def desenha(c, pts=pts, topo=topo, Z=Z, sid=sid, alto=alto, cume=cume):
            f = cena.fog(Z)
            scr = cena._projeta_poli(pts)
            if scr is None:
                return
            fill = T.caminho(scr)
            base = T.mistura(T.cenario(cor), cena.nevoa, f)
            y0 = cena.cam.hz - 0.35 * H
            y1 = cena.cam.hz + 0.12 * H
            c.drawPath(fill, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear(
                [skia.Point(0, y0), skia.Point(0, y1)],
                [T.cor_skia(T.escurece(base, 0.55)), T.cor_skia(T.escurece(base, 0.85)), T.cor_skia(T.mistura(base, cena.nevoa, 0.55))],
                [0.0, 0.6, 1.0])))
            st = np.array([cena.p(q) for q in topo])
            if cume:
                c.save()
                c.clipPath(fill, doAntiAlias=True)
                pa = skia.Paint(AntiAlias=True, Color=T.cor_skia(T.TINTA, 90 * (1 - f)), Style=skia.Paint.kStroke_Style, StrokeWidth=1.0)
                c.drawPath(T.hachura(fill, 0.95, 7.0, 1.0, cena.var, sid), pa)
                c.restore()
            if rim and cume:
                c.drawPath(T.traco_tinta(st, 4.0, cena.var, sid + 1, amp=0.6, ponta=(0.0, 0.0)),
                           T.tinta_paint(T.mistura(LUA, cena.nevoa, f * 0.5), 190 * rim * (1 - 0.5 * f)))
            if cume:
                c.drawPath(T.traco_tinta(st, cena.larg(Z, 1.0), cena.var, sid + 2, amp=0.8, ponta=(0.0, 0.0)), cena._tinta_paint(f))
                # capim seco e mato na crista, em silhueta contra o céu
                rnd = random.Random(sid)
                tufo = skia.Path()
                for k in range(0, len(st) - 1):
                    for j in range(rnd.randint(1, 4)):
                        u = rnd.random()
                        x = st[k][0] + (st[k + 1][0] - st[k][0]) * u
                        y = st[k][1] + (st[k + 1][1] - st[k][1]) * u
                        h = rnd.uniform(3, 12) * (1.8 if rnd.random() < 0.08 else 1.0)
                        tufo.moveTo(x, y + 1)
                        tufo.quadTo(x + rnd.uniform(-2, 2), y - h * 0.5, x + rnd.uniform(-5, 5), y - h)
                c.drawPath(tufo, skia.Paint(AntiAlias=True, Color=T.cor_skia(T.mistura(T.TINTA, cena.nevoa, f * 0.6), 230),
                                            Style=skia.Paint.kStroke_Style, StrokeWidth=1.3, StrokeCap=skia.Paint.kRound_Cap))
            elif curvas:
                c.drawPath(T.traco_tinta(st, max(0.8, cena.larg(Z, 0.35)), cena.var, sid + 2, amp=0.8, ponta=(0.0, 0.0)),
                           cena._tinta_paint(f, 70))
        cena.item(Z if zorder is None else zorder + Z * 0.001, desenha, zg=Z, centro=(0.5 * (x0 + x1), alto * 0.5, Z))


# ---------------------------------------------------------------- objetos

def cruz(cena, X, Z, Y=0.0, alt=1.1, inclina=0.0, semente=1, cor=(110, 100, 86)):
    df = torto(lean=inclina, wob=0.01, semente=semente, base=(X, Y, Z), rot=_n(semente) * 0.4)
    cena.caixa(X - 0.05, X + 0.05, Y, Y + alt, Z - 0.05, Z + 0.05, cor, deforma=df)
    cena.caixa(X - 0.32, X + 0.32, Y + alt * 0.62, Y + alt * 0.72, Z - 0.045, Z + 0.045, cor, deforma=df)


def lapide(cena, X, Z, Y=0.0, alt=0.8, larg=0.5, inclina=0.0, semente=1, cor=(124, 120, 110)):
    """Lápide de topo redondo, torta, com uma rachadura e musgo seco."""
    df = torto(lean=inclina, wob=0.012, semente=semente, base=(X, Y, Z), rot=_n(semente + 3) * 0.3)
    arco = [(X + larg / 2 * math.cos(a), Y + alt - larg / 2 + larg / 2 * math.sin(a), Z) for a in np.linspace(0, math.pi, 10)]
    frente = [(X + larg / 2, Y, Z)] + arco + [(X - larg / 2, Y, Z)]
    cena.face([df(p) for p in frente], cor, textura=tex_parede([df(p) for p in ((X - larg / 2, Y, Z), (X + larg / 2, Y, Z),
                                                                                  (X + larg / 2, Y + alt, Z), (X - larg / 2, Y + alt, Z))],
                                                                semente, picho=0.0, umidade=0.9, rachas=1), rim=True)
    lado = [(X + larg / 2, Y, Z), (X + larg / 2, Y, Z + 0.12), (X + larg / 2, Y + alt - larg / 2, Z + 0.12), (X + larg / 2, Y + alt - larg / 2, Z)]
    cena.face([df(p) for p in lado], T.escurece(cor, 0.8), z=Z + 0.06)


def cova_rachada(cena, X, Z, Y=0.0, semente=1):
    """Cova fresca rachada de dentro pra fora: monte de terra aberto em fendas, torrões jogados e a cruz torta."""
    rnd = random.Random(semente)
    monte = [(X + 0.55 * math.cos(a) * rnd.uniform(0.85, 1.1), Y + 0.04 + 0.12 * max(0.0, math.sin(a)), Z + 1.1 * math.sin(a) * rnd.uniform(0.85, 1.1))
             for a in np.linspace(0, 2 * math.pi, 18, endpoint=False)]
    cena.face(monte, (70, 56, 44), z=Z + 0.1, textura=None)
    fenda = [(X - 0.18, Y + 0.05, Z - 0.7), (X + 0.06, Y + 0.05, Z - 0.3), (X - 0.1, Y + 0.05, Z + 0.1), (X + 0.14, Y + 0.05, Z + 0.6),
             (X + 0.02, Y + 0.05, Z + 0.62), (X - 0.2, Y + 0.05, Z + 0.1), (X - 0.04, Y + 0.05, Z - 0.3), (X - 0.3, Y + 0.05, Z - 0.68)]
    cena.face(fenda, (8, 6, 6), contorno=0.8, hach=False, z=Z + 0.05)
    for k in range(7):   # rachaduras saindo da fenda
        a = rnd.uniform(0, 2 * math.pi)
        o = (X + 0.15 * math.cos(a), Y + 0.06, Z + 0.4 * math.sin(a))
        rachadura(cena, o, (math.cos(a), 0, math.sin(a) * 1.5), rnd.uniform(0.4, 0.8), semente * 10 + k, z=Z + 0.04)
    for k in range(9):   # torrões jogados pra fora
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(0.7, 1.3)
        x, z = X + 0.55 * r * math.cos(a), Z + 1.1 * r * math.sin(a)
        w = rnd.uniform(0.06, 0.14)
        cena.caixa(x, x + w, Y, Y + w * 0.6, z, z + w, (78, 62, 48), deforma=torto(rot=rnd.uniform(-1, 1), wob=0.01, semente=semente + k,
                                                                                base=(x, Y, z)))
    cruz(cena, X, Z + 1.25, Y=Y, alt=1.0, inclina=0.18, semente=semente + 50, cor=(96, 86, 72))


def trilha_terra(cena, pontos, larg=0.35, semente=1):
    """Trilha de terra seca (pegadas arrastadas) passando pelos pontos 3D, do cemitério até as casas."""
    rnd = random.Random(semente)
    for i, (a, b) in enumerate(zip(pontos[:-1], pontos[1:])):
        n = max(2, int(math.dist(a, b) / 0.7))
        for k in range(n):
            u = k / n
            x, y, z = (a[j] + (b[j] - a[j]) * u for j in range(3))
            w = larg * rnd.uniform(0.6, 1.2)
            pts = [(x + w * math.cos(q) * rnd.uniform(0.7, 1.1), y + 0.01, z + w * 0.7 * math.sin(q) * rnd.uniform(0.6, 1.1))
                   for q in np.linspace(0, 2 * math.pi, 8, endpoint=False)]
            cena.face(pts, (52, 40, 32), contorno=0.0, hach=False, z=z + 0.02)


def lampiao(cena, X, Z, Y=0.0, alt=2.2, acesa=1.0, semente=1):
    """Poste de madeira torto com lampião pendurado (vidro, armação de ferro e a chama quente)."""
    df = torto(lean=0.05, wob=0.01, semente=semente, base=(X, Y, Z))
    cena.caixa(X - 0.06, X + 0.06, Y, Y + alt, Z - 0.06, Z + 0.06, (84, 70, 56), deforma=df)
    braco = [df((X, Y + alt - 0.1, Z)), df((X + 0.45, Y + alt - 0.05, Z))]
    cena.linha(braco, 1.0)
    lx, ly = X + 0.45, Y + alt - 0.32
    cena.linha([df((lx, Y + alt - 0.05, Z)), df((lx, ly + 0.2, Z))], 0.5)
    vidro = [(lx - 0.1, ly - 0.16, Z), (lx + 0.1, ly - 0.16, Z), (lx + 0.12, ly + 0.14, Z), (lx - 0.12, ly + 0.14, Z)]
    cena.face(vidro, T.mistura((40, 30, 20), LAMPADA, 0.8 * acesa), contorno=1.0, hach=False, luz_extra=acesa, z=Z - 0.02)
    cena.face([(lx - 0.14, ly + 0.14, Z), (lx + 0.14, ly + 0.14, Z), (lx, ly + 0.26, Z)], (40, 34, 30), contorno=0.8, z=Z - 0.03)
    if acesa:
        cena.luz(lx, ly, Z - 0.05, 3.6, (236, 176, 96), acesa, chao=True, pisca=semente)


def cerca_torta(cena, x0, x1, Z, alt=1.1, semente=1, passo=0.22):
    """Cerca de ripas tortas (primeiro plano): ripas de ponta, duas travessas, umas faltando."""
    rnd = random.Random(semente)
    x = x0
    k = 0
    while x < x1:
        if rnd.random() > 0.12:
            inc = rnd.uniform(-0.08, 0.08)
            h = alt * rnd.uniform(0.85, 1.05)
            pts = [(x, 0, Z), (x + 0.12, 0, Z), (x + 0.12 + inc * h, h, Z), (x + 0.06 + inc * h, h + 0.1, Z), (x + inc * h, h, Z)]
            cena.face(pts, (92, 80, 66), contorno=1.0, z=Z, textura=tex_tabuas(pts[:4], 2, ao_longo=1, alfa=80, nos=False))
        x += passo
        k += 1
    for y in (alt * 0.3, alt * 0.75):
        cena.caixa(x0, x1, y, y + 0.08, Z + 0.02, Z + 0.06, (84, 72, 60), deforma=torto(lean=0.0, sag=0.02, wob=0.02, semente=semente + int(y * 10)))


def capela(cena, X, Z, Y=0.0, semente=1, acesa=0.7):
    """Capela branca de cemitério: corpo, telhado de duas águas, torre do sino com a cruz, porta e janela acesa."""
    df = torto(lean=0.03, wob=0.02, semente=semente, base=(X, Y, Z))
    w, d_, h = 3.2, 4.6, 3.4
    cena.caixa(X - w / 2, X + w / 2, Y, Y + h, Z, Z + d_, (176, 168, 150), deforma=df,
               textura_face=lambda pts: tex_parede(pts, semente + 1, picho=0.0, umidade=1.0, rachas=2))
    cume = Y + h + 1.6
    frente_tri = [df((X - w / 2 - 0.2, Y + h - 0.1, Z - 0.15)), df((X + w / 2 + 0.2, Y + h - 0.1, Z - 0.15)), df((X, cume, Z - 0.15))]
    cena.face(frente_tri, (150, 142, 126), z=Z - 0.1)
    tel = [df((X + w / 2 + 0.25, Y + h - 0.15, Z - 0.2)), df((X + w / 2 + 0.25, Y + h - 0.15, Z + d_ + 0.2)), df((X, cume, Z + d_ + 0.2)),
           df((X, cume, Z - 0.2))]
    cena.face(tel, (96, 70, 60), textura=tex_telhas(tel), z=Z + d_ / 2 - 0.05, rim=True)
    porta = [df((X - 0.45, Y, Z - 0.02)), df((X + 0.45, Y, Z - 0.02)), df((X + 0.45, Y + 1.9, Z - 0.02)), df((X, Y + 2.25, Z - 0.02)),
             df((X - 0.45, Y + 1.9, Z - 0.02))]
    cena.face(porta, (56, 42, 34), z=Z - 0.05, textura=tex_tabuas(porta[:4], 4, ao_longo=1, nos=False))
    jan = [df((X - 0.25, Y + 2.5, Z - 0.03)), df((X + 0.25, Y + 2.5, Z - 0.03)), df((X + 0.25, Y + 3.1, Z - 0.03)), df((X - 0.25, Y + 3.1, Z - 0.03))]
    janela(cena, jan, acesa=acesa, grade=False, z=Z - 0.06)
    # torre do sino ao lado
    tx = X + w / 2 + 0.7
    cena.caixa(tx - 0.6, tx + 0.6, Y, Y + h + 2.6, Z + 0.4, Z + 1.6, (170, 162, 146), deforma=df,
               textura_face=lambda pts: tex_parede(pts, semente + 2, picho=0.0, umidade=1.0, rachas=1))
    topo = Y + h + 2.6
    cena.face([df((tx - 0.75, topo, Z + 0.3)), df((tx + 0.75, topo, Z + 0.3)), df((tx, topo + 1.5, Z + 1.0))], (90, 66, 56), z=Z + 0.2, rim=True)
    vao = [df((tx - 0.3, topo - 1.4, Z + 0.38)), df((tx + 0.3, topo - 1.4, Z + 0.38)), df((tx + 0.3, topo - 0.5, Z + 0.38)),
           df((tx - 0.3, topo - 0.5, Z + 0.38))]
    cena.face(vao, (8, 6, 8), z=Z + 0.2, hach=False)
    cena.linha([df((tx, topo + 1.5, Z + 1.0)), df((tx, topo + 2.3, Z + 1.0))], 0.8)
    cena.linha([df((tx - 0.25, topo + 2.0, Z + 1.0)), df((tx + 0.25, topo + 2.0, Z + 1.0))], 0.8)


def casinha(cena, X, Z, Y=0.0, w=4.0, d_=5.0, h=2.8, cor=(150, 138, 118), semente=1, acesa=0.0, frente=True, vira=0.0,
            telha=(104, 76, 62), chamine=False):
    """Casa de cidadezinha: torta, telhado de telha de barro de duas águas, janela (às vezes acesa), porta, beiral,
    chaminé de tijolo (o topo dela fica em cena.chamines, pra fumaça)."""
    df = torto(lean=0.04 * _n(semente), sag=0.06, wob=0.025, semente=semente, base=(X, Y, Z), rot=vira)
    cena.caixa(X - w / 2, X + w / 2, Y, Y + h, Z, Z + d_, cor, deforma=df,
               textura_face=lambda pts: tex_parede(pts, semente, picho=0.0, umidade=0.9, rachas=1))
    cume = Y + h + 1.4 + 0.3 * _n(semente + 1)
    tel = [df((X - w / 2 - 0.3, Y + h - 0.12, Z - 0.3)), df((X + w / 2 + 0.3, Y + h - 0.12, Z - 0.3)), df((X + w / 2 + 0.3, Y + h - 0.12, Z + d_ + 0.3)),
           df((X - w / 2 - 0.3, Y + h - 0.12, Z + d_ + 0.3))]
    cumes = [df((X, cume, Z - 0.3)), df((X, cume, Z + d_ + 0.3))]
    for lado in (-1, 1):   # as duas águas
        pts = [tel[0] if lado < 0 else tel[1], tel[3] if lado < 0 else tel[2], cumes[1], cumes[0]]
        if (lado < 0 and cena.cam.x < X) or (lado > 0 and cena.cam.x >= X) or cena.cam.h > cume:
            cena.face(pts, telha, textura=tex_telhas(pts), z=Z + d_ / 2 - 0.06, rim=True)
    if chamine:
        cxm, czm = X + w * 0.22, Z + d_ * 0.62
        base_y = Y + h + 0.6
        cena.caixa(cxm - 0.3, cxm + 0.3, base_y, cume + 0.9, czm - 0.3, czm + 0.3, (118, 72, 56), deforma=df, rim=True)
        if not hasattr(cena, "chamines"):
            cena.chamines = []
        cena.chamines.append(df((cxm, cume + 0.9, czm)))
    if frente and cena.cam.z < Z:
        cena.face([df((X - w / 2, Y + h - 0.05, Z - 0.02)), df((X + w / 2, Y + h - 0.05, Z - 0.02)), df((X, cume - 0.05, Z - 0.02))],
                  T.escurece(cor, 0.9), z=Z - 0.04)
        jan = [df((X - w * 0.35, Y + 1.0, Z - 0.03)), df((X - w * 0.1, Y + 1.0, Z - 0.03)), df((X - w * 0.1, Y + 1.9, Z - 0.03)),
               df((X - w * 0.35, Y + 1.9, Z - 0.03))]
        janela(cena, jan, acesa=acesa, grade=False, z=Z - 0.05)
        porta = [df((X + w * 0.1, Y, Z - 0.03)), df((X + w * 0.32, Y, Z - 0.03)), df((X + w * 0.32, Y + 2.0, Z - 0.03)), df((X + w * 0.1, Y + 2.0, Z - 0.03))]
        cena.face(porta, (60, 46, 38), z=Z - 0.05, textura=tex_tabuas(porta, 3, ao_longo=1, nos=False))


def poco(cena, X, Z, Y=0.0, semente=1):
    """Poço de tijolo com sarilho de madeira e balde pendurado."""
    from .cenario3d import _cilindro
    _cilindro(cena, X, Y, Z, 0.7, 0.68, 0.8, (128, 100, 84))
    for x in (-0.65, 0.65):
        cena.caixa(X + x - 0.05, X + x + 0.05, Y + 0.8, Y + 1.9, Z - 0.05, Z + 0.05, (90, 74, 60))
    cena.linha([(X - 0.7, Y + 1.8, Z), (X + 0.7, Y + 1.8, Z)], 1.2)
    cena.face([(X - 0.85, Y + 1.9, Z - 0.4), (X + 0.85, Y + 1.9, Z - 0.4), (X, Y + 2.4, Z)], (96, 72, 58), z=Z - 0.1)
    cena.linha([(X + 0.1, Y + 1.8, Z), (X + 0.1, Y + 1.2, Z)], 0.4)
    _cilindro(cena, X + 0.1, Y + 1.0, Z, 0.12, 0.14, 0.2, (90, 80, 70))


def _galhos_frente_cru(c, t, lado=-1, semente=1, escala=1.0, cor=(10, 8, 10)):
    """Galho seco enorme no primeiro plano, entrando pelo canto (desenhado na tela, por cima da cena): moldura de
    pintura, quase silhueta, com um fio de luz da lua na borda e o balanço lento do vento."""
    rnd = random.Random(semente)
    var = T.ferve(t)
    segs = []

    def ramo(x, y, ang, comp, larg, nivel):
        if nivel > 7 or comp < 10:
            return
        pts = [(x, y)]
        a = ang
        for j in range(5):
            a += rnd.uniform(-0.22, 0.22) + 0.012 * math.sin(t * 0.8 + nivel) * nivel
            x, y = x + math.cos(a) * comp / 5, y + math.sin(a) * comp / 5
            pts.append((x, y))
        segs.append((pts, larg))
        for k in range(2 if nivel < 2 else rnd.choice((2, 2, 3))):
            ramo(x, y, a + rnd.uniform(-0.8, 0.8), comp * rnd.uniform(0.55, 0.75), larg * 0.6, nivel + 1)
        if nivel >= 2:   # gravetinhos espetados ao longo do ramo (é o que dá a massa de galhada contra o céu)
            for j in range(1, 4):
                px, py = pts[j]
                aa = a + rnd.choice((-1, 1)) * rnd.uniform(0.6, 1.2)
                cc = comp * rnd.uniform(0.15, 0.3)
                segs.append(([(px, py), (px + math.cos(aa) * cc * 0.5, py + math.sin(aa) * cc * 0.5),
                              (px + math.cos(aa + 0.2) * cc, py + math.sin(aa + 0.2) * cc)], max(1.2, larg * 0.35)))

    x0 = 0 if lado < 0 else W
    ang0 = (0.15 if lado < 0 else math.pi - 0.15) + rnd.uniform(-0.1, 0.1)
    y0 = H * rnd.uniform(0.08, 0.22)
    ramo(x0 - lado * 10, y0, ang0, 600 * escala, 56 * escala, 0)
    ramo(x0 - lado * 10, y0 + 90 * escala, ang0 + 0.35 * (1 if lado < 0 else -1), 360 * escala, 30 * escala, 1)   # o galho de baixo
    for k, (pts, larg) in enumerate(segs):
        q = T.catmull(np.array(pts), False, 5)
        c.drawPath(T.traco_tinta(q, larg, var, semente * 100 + k, amp=0.5, ponta=(0.0, 0.6)), T.tinta_paint(cor))
        if larg > 6:
            off = q + np.array([lado * -1.0, -larg * 0.32])
            c.drawPath(T.traco_tinta(off, max(1.0, larg * 0.07), var, semente * 100 + k + 50, amp=0.3, ponta=(0.2, 0.7)), T.tinta_paint(LUA, 70))


def sombra_frente(c, ini=0.6, k=0.72, lados=0.35):
    """Escurece o chão perto da câmera (o primeiro plano fica na sombra e a luz mora no meio do quadro, como
    em pintura de cenário) e fecha um pouco os lados."""
    c.drawRect(skia.Rect.MakeLTRB(-50, H * ini, W + 50, H + 50), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, H * ini), skia.Point(0, H)], [T.cor_skia((12, 10, 12), 0), T.cor_skia((12, 10, 12), 255 * k * 0.6),
                                                      T.cor_skia((12, 10, 12), 255 * k)], [0.0, 0.55, 1.0])))
    for l in (-1, 1):
        x0 = 0 if l < 0 else W
        c.drawRect(skia.Rect.MakeLTRB(-50, 0, W + 50, H), skia.Paint(Shader=skia.GradientShader.MakeLinear(
            [skia.Point(x0, 0), skia.Point(x0 - l * W * 0.3, 0)], [T.cor_skia((12, 10, 12), 255 * lados), T.cor_skia((12, 10, 12), 0)],
            [0.0, 1.0])))


def _mato_frente_cru(c, t, semente=1, cor=(12, 10, 10), altura=(0.06, 0.14)):
    """Capim do primeiro plano em papel: duas faixas recortadas em zigue-zague (a de trás um tom mais clara), mais
    altas nos cantos e baixas no meio (a estrada leva o olho), cada uma com a sombra dura na de trás. O vento mexe as
    pontas em degraus de stop motion."""
    rnd = random.Random(semente)
    ts = T.passo_stop(t) / 12.0
    escuro = T.mistura(T.TINTA, T.APOIO, 0.25)
    d = T.Desenho()
    for camada, (cor_c, k_alt) in enumerate(((T.mistura(escuro, T.APOIO, 0.35), 1.25), (escuro, 1.0))):
        pts = [(-40, H + 20)]
        x = -40.0
        while x < W + 40:
            canto = 1.0 if (x < 0.18 * W or x > 0.82 * W) else (0.35 if 0.32 * W < x < 0.68 * W else 0.65)
            h = H * rnd.uniform(*altura) * k_alt * canto
            passo = rnd.uniform(18, 34)
            balanco = 6 * math.sin(ts * 1.2 + x * 0.02 + camada)
            pts.append((x + passo * 0.5 + balanco, H - h))
            pts.append((x + passo, H - h * rnd.uniform(0.25, 0.45)))
            x += passo
        pts.append((W + 40, H + 20))
        T.peca(d, pts, cor_c, semente * 10 + camada, sombra=3.0, corte=False)
    d.desenha(c)


_MOLDURAS = {}


def _moldura(c, chave, desenha):
    """Imagem W x H (transparente) da moldura, feita uma vez por chave (inclui o desenho da fervura)."""
    img = _MOLDURAS.get(chave)
    if img is None:
        sup = c.getSurface()
        off = sup.makeSurface(W, H) if sup is not None else None
        if off is None:
            off = skia.Surface(W, H)
        oc = off.getCanvas()
        oc.clear(skia.Color(0, 0, 0, 0))
        desenha(oc)
        img = off.makeImageSnapshot()
        if len(_MOLDURAS) > 60:
            _MOLDURAS.clear()
        _MOLDURAS[chave] = img
    return img


def ancora_frente(cam, ref, x_tela, y_tela, D):
    """Primeiro plano no mundo: o ponto que, na câmera de referência `ref` (a do quadro em que a moldura foi composta),
    cai em (x_tela, y_tela) a D metros, projetado de novo pela câmera atual. Devolve (x, y, escala), ou None se o
    ponto passou para trás da câmera (a grua passou do galho). Sem `ref` (ou ref = cam), fica onde está na tela: só
    serve com a câmera parada."""
    if cam is None or ref is None or ref is cam or not hasattr(cam, "cam_xyz"):
        return x_tela, y_tela, 1.0
    ref = ref.original() if hasattr(ref, "original") else ref
    P = ref.mundo(x_tela, y_tela, D)
    zc = cam.cam_xyz(*P)[2]
    if zc < 0.15:
        return None
    x, y = cam.p(*P)
    return x, y, (cam.F / zc) / (ref.F / D)


def galhos_frente(c, t, lado=-1, semente=1, escala=1.0, cor=(10, 8, 10), cam=None, ref=None, D=3.5):
    """Galho seco enorme no primeiro plano, entrando pelo canto: moldura de pintura em quase silhueta, com o fio de
    luz da lua na borda; o vento balança o galho inteiro em volta do ponto onde ele entra no quadro. Só entra quando
    o estilo do canal pede essa moldura (T.MOLDURA)."""
    if T.MOLDURA != "galho":
        return
    var = T.ferve(t)
    tf = {0: 0.0, 1: 1 / 12, 2: 2 / 12}.get(var, 0.0)   # um t que cai no mesmo desenho da fervura
    img = _moldura(c, ("galhos", lado, semente, escala, cor, var), lambda oc: _galhos_frente_cru(oc, tf, lado, semente, escala, cor))
    x0 = 0 if lado < 0 else W
    y0 = H * 0.15
    an = ancora_frente(cam, ref, x0, y0, D)   # com `ref`, o galho é um objeto a D metros: paralaxe e escala pela câmera
    if an is None:
        return
    xa, ya, k = an
    c.save()
    c.translate(xa, ya)
    c.scale(k, k)
    c.translate(-x0, -y0)
    c.rotate(0.5 * math.sin(t * 0.8 + semente) * (-lado), x0, y0)
    c.drawImage(img, 0, 0)
    c.restore()


def mato_frente(c, t, semente=1, cor=(12, 10, 10), altura=(0.06, 0.14), cam=None, ref=None, D=2.5):
    """Capim, haste com cacho de semente e folha larga enormes na beira de baixo (primeiro plano em quase
    silhueta); o vento entorta o mato todo a partir do chão. Some quando o estilo pede o quadro sem moldura."""
    if T.MOLDURA == "nenhuma":
        return
    var = T.ferve(t)
    tf = {0: 0.0, 1: 1 / 12, 2: 2 / 12}.get(var, 0.0)
    img = _moldura(c, ("mato", semente, cor, altura, var), lambda oc: _mato_frente_cru(oc, tf, semente, cor, altura))
    an = ancora_frente(cam, ref, W / 2, H, D)   # o mato nasce no chão, D metros à frente da câmera de referência
    if an is None:
        return
    xa, ya, k = an
    c.save()
    c.translate(xa, ya)
    c.scale(k, k)
    c.translate(-W / 2, -H)
    c.translate(0, H)
    c.skew(0.018 * math.sin(t * 1.1 + semente), 0)
    c.translate(0, -H)
    c.drawImage(img, 0, 0)
    c.restore()


def corvos_3d(cena, t, n=5, semente=3, volume=(-30, 30, 14, 24, 40, 90), envergadura=0.9, vel=(3.0, 6.0)):
    """Bando de corvos no mundo: cada um com posição (X, Y, Z) dentro do `volume` (x0, x1, y0, y1, z0, z1, em metros),
    voando com velocidade própria (dá a volta no volume) e batendo asa. Projetados pela câmera: paralaxe, escala pela
    distância e neblina, então não ficam parados na tela quando a câmera anda. Só no estilo que sorteou corvos."""
    if not T.CORVOS:
        return
    x0, x1, y0, y1, z0, z1 = volume
    rnd = random.Random(semente)
    for k in range(n):
        X0, Y0, Z0 = rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(z0, z1)
        ang = rnd.uniform(-0.5, 0.5) + (0 if rnd.random() < 0.6 else math.pi)
        v = rnd.uniform(*vel)
        fase, freq = rnd.uniform(0, 6.28), rnd.uniform(7, 10)
        X = x0 + (X0 - x0 + math.cos(ang) * v * t) % (x1 - x0)
        Z = z0 + (Z0 - z0 + math.sin(ang) * v * t * 0.4) % (z1 - z0)
        Y = Y0 + 0.6 * math.sin(t * 0.7 + fase)
        bate = math.sin(t * freq + fase)

        def fn(c, X=X, Y=Y, Z=Z, bate=bate):
            cam = cena.cam
            if hasattr(cam, "cam_xyz"):
                zc = cam.cam_xyz(X, Y, Z)[2]
                if zc < 1.0:
                    return
                s = 0.5 * envergadura * cam.F / zc
            else:
                s = 0.5 * envergadura * cam.escala(Z)
            x, y = cam.p(X, Y, Z)
            if s < 1.2 or x < -50 or x > W + 50 or y < -50 or y > H + 50:
                return
            p = skia.Path()
            p.moveTo(x - s, y - s * 0.4 * bate)
            p.quadTo(x - s * 0.4, y - s * 0.1, x, y + s * 0.15)
            p.quadTo(x + s * 0.4, y - s * 0.1, x + s, y - s * 0.4 * bate)
            c.drawPath(p, skia.Paint(AntiAlias=True, Color=T.cor_skia(T.mistura((12, 10, 12), cena.nevoa, cena.fog(Z) * 0.8)),
                                     Style=skia.Paint.kStroke_Style, StrokeWidth=max(1.0, s * 0.16), StrokeCap=skia.Paint.kRound_Cap))
        cena.item(Z, fn, vivo=True, centro=(X, Y, Z))


def corvos_voando(c, t, n=5, semente=3, area=(0.1, 0.9, 0.06, 0.3), escala=1.0):
    """Bando em coordenada de tela. Só para close parado: com a câmera andando os corvos ficam grudados na tela (use
    corvos_3d). Só no estilo que sorteou corvos (T.CORVOS)."""
    if not T.CORVOS:
        return
    rnd = random.Random(semente)
    for k in range(n):
        x = (rnd.uniform(*area[:2]) * W + t * rnd.uniform(18, 40)) % (W + 100) - 50
        y = rnd.uniform(*area[2:]) * H + 6 * math.sin(t * 1.3 + k)
        s = rnd.uniform(9, 16) * escala
        bate = math.sin(t * rnd.uniform(7, 10) + k)
        p = skia.Path()
        p.moveTo(x - s, y - s * 0.4 * bate)
        p.quadTo(x - s * 0.4, y - s * 0.1, x, y + s * 0.15)
        p.quadTo(x + s * 0.4, y - s * 0.1, x + s, y - s * 0.4 * bate)
        c.drawPath(p, skia.Paint(AntiAlias=True, Color=T.cor_skia((12, 10, 12)), Style=skia.Paint.kStroke_Style, StrokeWidth=2.4 * escala,
                                 StrokeCap=skia.Paint.kRound_Cap))


def lua_grande(c, cena, x, y, r):
    """Lua cheia de papel: disco recortado com as crateras de papel de seda e o halo da luz atrás do papel."""
    c.drawCircle(x, y, r * 3.4, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
        skia.Point(x, y), r * 3.4, [T.cor_skia(LUA, 70), T.cor_skia(LUA, 18), T.cor_skia(LUA, 0)], [0.0, 0.45, 1.0])))
    d = T.Desenho()
    T.peca(d, T.elipse(x, y, r, r, 80), LUA, 991, sombra=2.2)
    rnd = random.Random(5)
    for k in range(6):
        a, rr = rnd.uniform(0, 6.28), rnd.uniform(0, r * 0.62)
        T.mancha(d, T.elipse(x + rr * math.cos(a), y + rr * math.sin(a), rnd.uniform(0.08, 0.18) * r, rnd.uniform(0.07, 0.14) * r, 18),
                 T.escurece(LUA, 0.82), 150, semente=60 + k)
    d.desenha(c)


def nuvem_na_lua(c, cena, x, y, r, semente=61):
    """Faixa de nuvem passando na frente da lua, com a borda acesa (a lua por trás)."""
    from .cenario3d import _nuvem
    d = T.Desenho()
    rnd = random.Random(semente)
    _nuvem(d, x - r * 2.2, y + r * 0.85, r * 3.6, r * 0.75, rnd, cena.var, semente, (40, 44, 54), (20, 22, 30), (226, 222, 196),
           T.mistura(T.TINTA, (40, 44, 54), 0.2))
    _nuvem(d, x + r * 0.2, y + r * 1.5, r * 2.4, r * 0.5, rnd, cena.var, semente + 1, (34, 38, 48), (18, 20, 26), (210, 206, 182),
           T.mistura(T.TINTA, (34, 38, 48), 0.2))
    d.desenha(c)


def _ceu(cc, ce, lua_xy=(0.72, 0.14), r_lua=110, cores=PAPEL_NOITE):
    ceu_noite(cc, ce, lua=lua_xy, r_lua=1, cores=cores, nuvens=False)
    lua_xy, r_lua = lua_do_estilo(lua_xy, r_lua)
    # brilho do ar úmido no horizonte, atrás dos morros (é ele que recorta as silhuetas)
    hz = ce.cam.hz + 140
    cc.drawRect(skia.Rect.MakeLTRB(-200, hz - 700, W + 200, hz + 200), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, hz - 700), skia.Point(0, hz + 200)], [T.cor_skia(NEVOA_LUAR, 0), T.cor_skia(NEVOA_LUAR, 110),
                                                              T.cor_skia(NEVOA_LUAR, 0)], [0.0, 0.75, 1.0])))
    lua_grande(cc, ce, W * lua_xy[0], H * lua_xy[1], r_lua)
    nuvem_na_lua(cc, ce, W * lua_xy[0], H * lua_xy[1], r_lua)


# ---------------------------------------------------------------- cenas

RELEVO_CEMITERIO = Relevo([(-3.0, 30.0, 16.0, 9.0, 9.0), (14.0, 40.0, 14.0, 10.0, 6.0), (-24.0, 44.0, 12.0, 9.0, 7.0)])


def _cemiterio_fixo(cam):
    cena = Cena(cam, 0.0, nevoa=NEVOA_LUAR, alcance=70.0, luz=(0.4, 0.45, 0.8), w_tinta=3.0)
    rel = RELEVO_CEMITERIO
    cena.face([(-80, 0, -12), (80, 0, -12), (80, 0, 160), (-80, 0, 160)], (26, 26, 24), z=400, hach=False)
    # morros de fundo em camadas (silhuetas cada vez mais claras na neblina)
    for k, (zf, alt, cor) in enumerate(((150, 52, (44, 48, 56)), (120, 40, (36, 40, 46)), (90, 26, (28, 30, 34)))):
        r = Relevo([(-70 + 34 * j + 12 * _n(k, j), zf, 18 + 6 * _n(j, k), 6, alt * (0.55 + 0.45 * abs(_n(j + k)))) for j in range(5)])
        morro_fatias(cena, r, -120, 120, zf - 4, zf + 4, n=2, cor=cor, passo_x=3.0, rim=0.8, semente=50 + k)
    morro_fatias(cena, rel, -45, 40, 16, 50, n=30, cor=(34, 36, 32), passo_x=0.8, rim=1.4, semente=3)
    # capela no alto do morro, árvore seca grande do lado
    capela(cena, -4.5, 31.0, Y=rel(-4.5, 31.0) - 0.3, semente=7, acesa=0.75)
    arvore_seca(cena, 4.5, 29.0, alt=11.0, semente=17, galhos=7, inclina=-0.15, grossura=3.0)
    cena.itens[-1] = (cena.itens[-1][0], cena.itens[-1][1], _ancora(cena.itens[-1][2], cena, 4.5, rel(4.5, 29.0), 29.0), *cena.itens[-1][3:])
    rnd = random.Random(11)
    # cruzes e lápides tortas espalhadas pela encosta (mais perto, maiores)
    for k in range(70):
        X = rnd.uniform(-16, 14)
        Z = rnd.uniform(18.5, 30)
        Y = rel(X, Z)
        if Y < 0.6:
            continue
        if rnd.random() < 0.55:
            cruz(cena, X, Z, Y=Y - 0.05, alt=rnd.uniform(0.9, 1.4), inclina=rnd.uniform(-0.25, 0.25), semente=100 + k)
        else:
            lapide(cena, X, Z, Y=Y - 0.05, alt=rnd.uniform(0.6, 1.0), larg=rnd.uniform(0.4, 0.6), inclina=rnd.uniform(-0.2, 0.2), semente=200 + k)
    # a cova rachada, no meio da encosta, e a trilha de terra descendo o morro até a estrada (linha que leva o olho)
    cx_, cz_ = 1.6, 21.0
    cova_rachada(cena, cx_, cz_, Y=rel(cx_, cz_), semente=9)
    trilha = [(cx_, rel(cx_, cz_), cz_ - 1.2)]
    for k in range(1, 9):
        z = cz_ - 1.2 - k * 1.6
        x = cx_ - 0.6 * k + 0.5 * math.sin(k)
        trilha.append((x, rel(x, z) + 0.02, z))
    trilha_terra(cena, trilha, semente=4)
    # muro baixo do cemitério com portão de ferro, no pé do morro
    for x0, x1 in ((-14, -2.2), (0.6, 12)):
        cena.caixa(x0, x1, 0, 1.0, 16.0, 16.4, (120, 114, 104), deforma=torto(lean=0.02, sag=0.04, wob=0.03, semente=int(x0)),
                   textura_face=lambda pts: tex_parede(pts, 33, picho=0.0, umidade=1.0, rachas=2))
    for k in range(12):
        x = -2.1 + k * 0.23
        cena.linha([(x, 0, 16.2), (x + 0.02 * math.sin(k), 1.9 + 0.15 * math.sin(k * 0.8), 16.2)], 0.5, z=16.0)
    cena.linha([(-2.2, 1.75, 16.2), (0.6, 1.85, 16.2)], 0.6, z=16.0)
    # primeiro plano: estrada de terra, cerca torta, mato alto, lampião
    estrada = [(-2.2, 0.002, -12), (2.6, 0.002, -12), (1.2, 0.002, 16.0), (-0.8, 0.002, 16.0)]
    cena.face(estrada, (50, 44, 38), z=399, hach=False)
    cerca_torta(cena, -3.6, -1.0, 6.0, alt=1.2, semente=5)
    cerca_torta(cena, 1.6, 4.2, 7.0, alt=1.1, semente=6)
    lampiao(cena, 1.3, 5.2, alt=2.5, semente=8)
    for k in range(10):
        mato(cena, rnd.uniform(-5, 5), rnd.uniform(1.5, 12), larg=rnd.uniform(0.6, 1.4), alt=rnd.uniform(0.5, 1.1), semente=600 + k)
    mato(cena, -1.2, 1.2, larg=1.0, alt=0.9, semente=71, n=26)
    mato(cena, 1.6, 1.6, larg=0.8, alt=0.8, semente=72, n=22)
    for zn, al, hh in ((17.0, 0.16, 0.9), (36.0, 0.14, 2.5), (80.0, 0.2, 8.0), (110.0, 0.24, 12.0)):
        cena.neblina(zn, altura=hh, alfa=al)
    return cena


def _ancora(fn, cena, X, Y, Z):
    """Desloca um item desenhado no chão (Y=0) pra altura Y do relevo (pra árvore no alto do morro)."""
    def novo(c):
        x0, y0 = cena.cam.p(X, 0.0, Z)
        x1, y1 = cena.cam.p(X, Y, Z)
        c.save()
        c.translate(x1 - x0, y1 - y0)
        fn(c)
        c.restore()
    return novo


def cemiterio(c, t, cam=None, atores=(), extras=None, roll=0.0, ref=None):
    """Cemitério num morro sob a lua: capela com torre do sino e janela acesa, árvore seca, cruzes e lápides tortas
    na encosta, a cova rachada de dentro pra fora e a trilha de terra que desce até a estrada; muro com portão de
    ferro, cerca torta, lampião e mato no primeiro plano; morros de fundo em camadas na neblina."""
    cam = cam or CamG(x=0.6, h=1.6, F=1150, hz=1180, cx=W / 2, z=0.5, pitch=-5.0)
    cena = _fixa("cemiterio", cam, t, _cemiterio_fixo)
    for a in atores:
        X, Z, desenha, alt = a[:4]
        cena.ator(X, Z, desenha, alt, Y=(a[4] if len(a) > 4 else RELEVO_CEMITERIO(X, Z)))
    corvos_3d(cena, t, n=6, semente=3)
    if extras:
        extras(cena)
    c.save()
    c.rotate(roll, W / 2, H / 2)
    cena.desenha(c, ceu=lambda cc, ce: _ceu(cc, ce, (0.7, 0.12), 120), nuvens=lambda cc, ce: nuvens(cc, ce, semente=41, faixa=(0.02, 0.3)))
    sombra_frente(c, ini=0.6, k=0.7)
    mato_frente(c, t, semente=5, altura=(0.08, 0.17), cam=cam, ref=ref)
    galhos_frente(c, t, lado=-1, semente=4, escala=1.2, cam=cam, ref=ref)
    c.restore()
    return cena



# ---------------------------------------------------------------- estrada de terra na neblina

RELEVO_ESTRADA = Relevo([(-30.0, 90.0, 26.0, 14.0, 22.0), (26.0, 80.0, 22.0, 12.0, 16.0), (6.0, 120.0, 30.0, 12.0, 30.0)])


def _curva(Z):
    """Eixo da estrada: um S que leva o olho até o morro."""
    return 1.6 * math.sin(Z / 9.0) + 0.06 * Z


def _capim_campo(area=(-30, 30, 0.5, 70), n=1400):
    def tex(c, cena, f):
        rnd = random.Random(12)
        p = skia.Path()
        for k in range(n):
            X, Z = rnd.uniform(area[0], area[1]), rnd.uniform(area[2], area[3])
            if hasattr(cena.cam, "cam_xyz") and cena.cam.cam_xyz(X, 0, Z)[2] < 0.5:
                continue
            x, y = cena.p((X, 0, Z))
            x2, y2 = cena.p((X, 1.0, Z))
            s = abs(y2 - y)
            h = s * rnd.uniform(0.12, 0.35)
            p.moveTo(x, y)
            p.lineTo(x + rnd.uniform(-0.3, 0.3) * h, y - h)
        c.drawPath(p, skia.Paint(AntiAlias=True, Color=T.cor_skia(T.TINTA, 110), Style=skia.Paint.kStroke_Style, StrokeWidth=1.0))
    return tex


def _sulcos_s():
    def tex(c, cena, f):
        pa = skia.Paint(AntiAlias=True, Color=T.cor_skia(T.TINTA, 150), Style=skia.Paint.kStroke_Style, StrokeWidth=1.3)
        p = skia.Path()
        for off in (-1.0, -0.7, 0.7, 1.0):
            pts = [cena.p((_curva(z) + off * (1 - z / 140), 0.005, z)) for z in np.linspace(-3, 70, 60)]
            p.moveTo(*pts[0])
            for q in pts[1:]:
                p.lineTo(*q)
        rnd = random.Random(3)
        for k in range(160):
            z = rnd.uniform(-2, 30)
            x, y = cena.p((_curva(z) + rnd.uniform(-1.6, 1.6), 0.005, z))
            s = cena.cam.escala(z) * 0.03
            p.addOval(skia.Rect.MakeXYWH(x - s, y - s * 0.5, 2 * s, s))
        c.drawPath(p, pa)
    return tex


def _estrada_fixa(cam):
    cena = Cena(cam, 0.0, nevoa=NEVOA_LUAR, alcance=42.0, luz=(0.4, 0.5, 0.75), w_tinta=3.0)
    cena.face([(-90, 0, -10), (90, 0, -10), (90, 0, 200), (-90, 0, 200)], (34, 34, 30), z=500, hach=False, textura=_capim_campo())
    zs = np.linspace(-6, 80, 60)
    esq = [(_curva(z) - 2.0 * (1 - z / 140), 0.004, z) for z in zs]
    dir_ = [(_curva(z) + 2.0 * (1 - z / 140), 0.004, z) for z in zs[::-1]]
    cena.face(esq + dir_, (70, 60, 50), z=499, hach=False, textura=_sulcos_s())
    morro_fatias(cena, RELEVO_ESTRADA, -110, 110, 70, 140, n=16, cor=(34, 38, 42), passo_x=2.0, rim=1.1, semente=7)
    for k in range(16):
        X = -14 + k * 1.6 + _n(k) * 0.6
        Z = 116.0
        cruz(cena, X, Z, Y=RELEVO_ESTRADA(X, Z) - 0.1, alt=1.6, inclina=_n(k + 3) * 0.2, semente=700 + k, cor=(60, 60, 64))
    capela(cena, 6.0, 118.0, Y=RELEVO_ESTRADA(6.0, 118.0) - 0.4, semente=19, acesa=0.6)
    tops = []
    for k, z in enumerate((6.0, 18.0, 30.0, 44.0, 60.0)):
        x = _curva(z) + 3.2
        tops.append(poste(cena, x, z, alt=6.5, inclina=0.06 * _n(k), lado=1, acesa=(1.0 if k in (1, 3) else 0.0), semente=k + 30))
    for a_, b_ in zip(tops[:-1], tops[1:]):
        fio(cena, a_, b_, barriga=0.7)
    rnd = random.Random(8)
    for l in (-1, 1):
        topo_prev = None
        for k in range(20):
            z = 2.0 + k * 3.4
            x = _curva(z) + l * (2.9 + 0.01 * z)
            inc = rnd.uniform(-0.12, 0.12)
            h = rnd.uniform(1.0, 1.35)
            cena.face([(x - 0.07, 0, z), (x + 0.07, 0, z), (x + 0.07 + inc * h, h, z), (x - 0.07 + inc * h, h + 0.05, z)], (70, 60, 50),
                      contorno=0.9, rim=True)
            topo = (x + inc * h, h * 0.8, z)
            if topo_prev:
                fio(cena, topo_prev, topo, barriga=0.05, k=0.3, n=5)
                fio(cena, (topo_prev[0], topo_prev[1] * 0.5, topo_prev[2]), (topo[0], topo[1] * 0.5, topo[2]), barriga=0.05, k=0.3, n=5)
            topo_prev = topo
    for X, Z, alt_, s_, inc in ((-6.5, 10.0, 8.0, 3, 0.2), (7.0, 16.0, 7.0, 5, -0.15), (-9.0, 34.0, 9.0, 9, 0.1), (10.0, 48.0, 6.0, 14, -0.1),
                                (-6.0, 62.0, 6.0, 21, 0.15)):
        arvore_seca(cena, X, Z, alt=alt_, semente=s_, galhos=7, inclina=inc, grossura=2.2)
    casinha(cena, _curva(38) - 7.5, 38.0, w=4.5, d_=4.5, h=2.8, cor=(132, 122, 104), semente=41, acesa=1.0, vira=0.25)
    poco(cena, _curva(36) - 3.6, 35.0, semente=4)
    for k in range(40):
        l = rnd.choice((-1, 1))
        z = rnd.uniform(2, 70)
        mato(cena, _curva(z) + l * rnd.uniform(2.4, 9), z, larg=rnd.uniform(0.6, 1.6), alt=rnd.uniform(0.4, 1.0), semente=800 + k)
    px, pz = _curva(4) - 2.9, 4.0
    a, b = (px, 0.1, pz), (px - 2.4, 0.1, pz + 1.2)
    for k in range(5):
        y = 0.15 + k * 0.28
        cena.linha([(a[0], y, a[2]), (b[0], y + 0.04 * k, b[2])], 1.2, z=pz)
    cena.linha([(a[0], 0.1, a[2]), (b[0], 1.3, b[2])], 1.0, z=pz)
    cena.caixa(px - 0.12, px + 0.12, 0, 1.8, pz - 0.12, pz + 0.12, (76, 62, 50), rim=True)
    lampiao(cena, _curva(5) + 2.4, 5.0, alt=2.4, semente=12)
    for k, (zp, dxp, rx, rz) in enumerate(((2.6, -0.7, 0.55, 0.35), (6.5, 0.6, 0.7, 0.4), (14.0, -0.4, 0.8, 0.5))):
        xp = _curva(zp) + dxp
        borda = [(xp + rx * math.cos(a) * (1 + 0.3 * _n(k * 9 + j)), 0.006, zp + rz * math.sin(a) * (1 + 0.3 * _n(k * 7 + j)))
                 for j, a in enumerate(np.linspace(0, 2 * math.pi, 14, endpoint=False))]
        cena.face(borda, (44, 46, 50), z=498 - k * 0.01, hach=False, contorno=0.4)
        # o reflexo da lua e do poste na água: um risco claro
        cena.linha([(xp - rx * 0.45, 0.007, zp - rz * 0.05), (xp + rx * 0.35, 0.007, zp + rz * 0.1)], 1.4, z=zp, cor=(214, 210, 190))
        cena.linha([(xp - rx * 0.2, 0.007, zp + rz * 0.3), (xp + rx * 0.1, 0.007, zp + rz * 0.35)], 0.8, z=zp, cor=(190, 186, 170))
    for zn, al, hh in ((8.0, 0.14, 0.8), (16.0, 0.2, 1.0), (26.0, 0.26, 1.2), (40.0, 0.3, 1.6), (62.0, 0.36, 2.4), (90.0, 0.4, 6.0)):
        cena.neblina(zn, altura=hh, alfa=al)
    return cena


def estrada_neblina(c, t, cam=None, atores=(), extras=None, roll=0.0, ref=None):
    """Estrada de terra em S na neblina, levando até o morro do cemitério (cruzes e capela na crista, lá longe);
    postes tortos com fio e luz quente, cerca de mourão dos dois lados, árvores secas, casinha com janela acesa e
    poço no caminho; porteira e lampião no primeiro plano; neblina em seis camadas."""
    cam = cam or CamG(x=_curva(0) + 0.3, h=1.5, F=1000, hz=1080, cx=W / 2, z=-4.0, pitch=-2.0)
    cena = _fixa("estrada_neblina", cam, t, _estrada_fixa)
    for a in atores:
        X, Z, desenha, alt = a[:4]
        cena.ator(X, Z, desenha, alt, Y=(a[4] if len(a) > 4 else 0.0))
    corvos_3d(cena, t, n=4, semente=9)
    if extras:
        extras(cena)
    c.save()
    c.rotate(roll, W / 2, H / 2)
    cena.desenha(c, ceu=lambda cc, ce: _ceu(cc, ce, (0.3, 0.16), 96), nuvens=lambda cc, ce: nuvens(cc, ce, semente=53, faixa=(0.02, 0.3)))
    sombra_frente(c, ini=0.62, k=0.7)
    mato_frente(c, t, semente=8, altura=(0.08, 0.17), cam=cam, ref=ref)
    galhos_frente(c, t, lado=1, semente=6, escala=1.1, cam=cam, ref=ref)
    c.restore()
    return cena


# ---------------------------------------------------------------- a cidadezinha vista de cima

RELEVO_CIDADE = Relevo([(-60.0, 150.0, 40.0, 24.0, 30.0), (70.0, 170.0, 40.0, 22.0, 34.0), (0.0, 220.0, 80.0, 20.0, 46.0),
                        (36.0, 118.0, 12.0, 9.0, 9.0)])


RUAS_CIDADE = [   # (x, z) saindo da praça da igreja; tortas como rua de cidade velha
    [(2, 44), (-6, 34), (-14, 24), (-26, 14), (-40, 4), (-56, -6)],
    [(2, 44), (10, 33), (16, 22), (26, 12), (40, 2), (56, -8)],
    [(2, 44), (-3, 58), (4, 72), (0, 88), (6, 104)],
    [(2, 44), (14, 48), (26, 54), (38, 58), (54, 66)],
    [(2, 44), (-12, 48), (-24, 54), (-38, 52), (-54, 58)],
    [(-14, 24), (-6, 14), (-2, 2), (-4, -10)],
    [(26, 54), (30, 70), (26, 86)],
]


def _rua_pts(r, n=40):
    return T.catmull(np.array(r, float), False, max(2, n // max(1, len(r) - 1)))


def _cidade_fixa(cam):
    cena = Cena(cam, 0.0, nevoa=NEVOA_LUAR, alcance=170.0, luz=(0.4, 0.6, 0.7), w_tinta=2.6)
    cena.face([(-200, 0, -100), (200, 0, -100), (200, 0, 320), (-200, 0, 320)], (30, 32, 28), z=900, hach=False,
              textura=_capim_campo(area=(-80, 80, 0, 160), n=2600))
    rnd = random.Random(31)
    igreja_x, igreja_z = 2.0, 44.0
    # praça de terra batida em volta da igreja
    cena.face([(igreja_x + 11 * math.cos(a), 0.011, igreja_z + 9 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 20, endpoint=False)],
              (74, 66, 56), z=889, hach=False, contorno=0.0)
    lotes = [(igreja_x, igreja_z, 10.0)]
    casas = []
    for i, r in enumerate(RUAS_CIDADE):
        p = _rua_pts(r)
        larg = 1.5 if i < 5 else 1.0
        esq, dir_ = [], []
        for j in range(len(p)):
            a = p[min(j + 1, len(p) - 1)] - p[max(j - 1, 0)]
            n = math.hypot(*a) or 1.0
            nx, nz = -a[1] / n, a[0] / n
            esq.append((p[j][0] + nx * larg, 0.012, p[j][1] + nz * larg))
            dir_.append((p[j][0] - nx * larg, 0.012, p[j][1] - nz * larg))
        cena.face(esq + dir_[::-1], (76, 66, 54), z=888 - i * 0.1, hach=False, contorno=0.0)
        # casas dos dois lados, viradas pra rua, com espaço de quintal entre elas
        dist = 0.0
        for j in range(1, len(p)):
            seg = math.hypot(*(p[j] - p[j - 1]))
            dist += seg
            if dist < rnd.uniform(6.0, 8.0):
                continue
            dist = 0.0
            a = p[min(j + 1, len(p) - 1)] - p[j - 1]
            n = math.hypot(*a) or 1.0
            tx, tz = a[0] / n, a[1] / n
            for lado in (-1, 1):
                if rnd.random() < 0.18:
                    continue   # terreno vazio
                off = larg + rnd.uniform(3.2, 4.4)
                x = p[j][0] - tz * off * lado
                z = p[j][1] + tx * off * lado
                if any(math.hypot(x - a_, z - b_) < r_ + 3.2 for a_, b_, r_ in lotes):
                    continue
                if z < 12:
                    continue   # perto demais da grua: viraria um telhado gigante cortado
                lotes.append((x, z, 2.6))
                casas.append((x, z, 0.12 * math.atan2(tx, tz)))   # só um tanto virada (a caixa torta não gira muito)
    for k in range(40):   # sítios espalhados fora das ruas
        x, z = rnd.uniform(-60, 60), rnd.uniform(14, 110)
        if any(math.hypot(x - a_, z - b_) < r_ + 6 for a_, b_, r_ in lotes):
            continue
        lotes.append((x, z, 3.0))
        casas.append((x, z, rnd.uniform(-0.15, 0.15)))
    TELHAS = ((150, 84, 58), (136, 76, 56), (160, 98, 66), (118, 68, 52), (142, 90, 70))
    PAREDES = ((150, 138, 118), (132, 126, 116), (146, 128, 112), (120, 120, 118), (156, 146, 128), (138, 120, 100), (164, 150, 124))
    for k, (x, z, vira) in enumerate(casas):
        tipo = rnd.random()
        if tipo < 0.15:      # sobrado
            w, d_, h = rnd.uniform(4.2, 5.4), rnd.uniform(4.5, 6.0), rnd.uniform(4.6, 5.6)
        elif tipo < 0.35:    # casa comprida de fundo
            w, d_, h = rnd.uniform(3.0, 3.8), rnd.uniform(7.0, 9.0), rnd.uniform(2.5, 3.0)
        elif tipo < 0.5:     # casinha miúda
            w, d_, h = rnd.uniform(2.6, 3.2), rnd.uniform(3.0, 3.8), rnd.uniform(2.2, 2.6)
        else:                # térrea comum
            w, d_, h = rnd.uniform(3.6, 5.6), rnd.uniform(4.0, 6.0), rnd.uniform(2.5, 3.3)
        casinha(cena, x, z, w=w, d_=d_, h=h, cor=rnd.choice(PAREDES), semente=900 + k, acesa=(0.95 if rnd.random() < 0.22 else 0.0),
                vira=vira + rnd.uniform(-0.08, 0.08), telha=rnd.choice(TELHAS), chamine=rnd.random() < 0.3)
        if rnd.random() < 0.3:   # puxadinho do lado, mais baixo
            casinha(cena, x + (w / 2 + 1.2) * rnd.choice((-1, 1)), z + rnd.uniform(0, d_ * 0.4), w=2.2, d_=rnd.uniform(2.4, 3.2), h=h * 0.72,
                    cor=rnd.choice(PAREDES), semente=1900 + k, vira=vira, telha=rnd.choice(TELHAS), frente=False)
        if rnd.random() < 0.4:   # árvore seca no quintal de trás
            arvore_seca(cena, x + rnd.uniform(-4, 4), z + d_ + rnd.uniform(1, 3), alt=rnd.uniform(4, 7.5), semente=1000 + k, galhos=5,
                        inclina=rnd.uniform(-0.2, 0.2), grossura=1.6)
    # postes de madeira nas ruas principais, com o fio passando de um pro outro por cima das casas
    for i, r in enumerate(RUAS_CIDADE[:5]):
        p = _rua_pts(r)
        topos = []
        for j in range(4, len(p), 9):
            a_ = p[min(j + 1, len(p) - 1)] - p[j - 1]
            n_ = math.hypot(*a_) or 1.0
            px, pz = p[j][0] + a_[1] / n_ * 2.4, p[j][1] - a_[0] / n_ * 2.4
            if pz < 8:
                continue
            topos.append(poste(cena, px, pz, alt=7.0, inclina=0.05 * _n(i * 10 + j), lado=1, acesa=(1.0 if (i + j) % 3 == 0 else 0.0),
                               semente=300 + i * 20 + j))
        for a_, b_ in zip(topos[:-1], topos[1:]):
            fio(cena, a_, b_, barriga=0.5)
            fio(cena, (a_[0] + 0.3, a_[1] - 0.25, a_[2]), (b_[0] + 0.3, b_[1] - 0.25, b_[2]), barriga=0.55)
    capela(cena, igreja_x, igreja_z, semente=81, acesa=0.9)
    for k in range(9):   # poste nas esquinas, poça de luz no chão
        r = RUAS_CIDADE[k % 5]
        x, z = r[1 + k // 5 % (len(r) - 1)]
        cena.luz(x + 1.8, 5.0, z, 7.0, (236, 176, 96), 0.8, chao=True)
    for k in range(5):   # mato de árvore seca em tufos na borda da cidade (massa escura)
        cx_, cz_ = rnd.choice(((-52, 30), (50, 30), (-46, 80), (48, 86), (-20, 96), (30, 100)))
        for j in range(6):
            arvore_seca(cena, cx_ + rnd.uniform(-6, 6), cz_ + rnd.uniform(-5, 5), alt=rnd.uniform(5, 9), semente=1400 + 10 * k + j, galhos=6,
                        inclina=rnd.uniform(-0.15, 0.15), grossura=1.8)
    morro_fatias(cena, RELEVO_CIDADE, -200, 200, 90, 250, n=26, cor=(30, 32, 34), passo_x=3.0, rim=1.0, semente=91)
    for k in range(26):
        X = 30 + rnd.uniform(-8, 8)
        Z = 118 + rnd.uniform(-5, 5)
        cruz(cena, X, Z, Y=RELEVO_CIDADE(X, Z) - 0.1, alt=1.5, inclina=rnd.uniform(-0.2, 0.2), semente=1200 + k, cor=(96, 92, 86))
    trilha = []
    for k in range(18):
        u = k / 17
        x = 30 + (26 - 30) * u + 3 * math.sin(u * 7)
        z = 116 + (86 - 116) * u
        trilha.append((x, max(RELEVO_CIDADE(x, z), 0.0) + 0.05, z))
    trilha_terra(cena, trilha, larg=1.2, semente=12)
    for zn, al, hh in ((28.0, 0.07, 1.6), (50.0, 0.1, 2.4), (72.0, 0.14, 3.5), (96.0, 0.2, 5.0), (140.0, 0.28, 12.0), (200.0, 0.4, 22.0)):
        cena.neblina(zn, altura=hh, alfa=al)
    return cena


def fumaca(t, semente=1):
    """Fumaça de chaminé: bolotas claras que sobem, crescem, entortam com o vento e somem (desenho de ator)."""
    def fn(c, x, y, alt):
        rnd = random.Random(semente)
        tq = math.floor(t * 12) / 12
        for k in range(9):
            u = ((tq * 0.35 + k / 9.0 + rnd.random() * 0.05) % 1.0)
            px = x + (u ** 1.5) * alt * 2.2 + math.sin(tq * 1.3 + k) * alt * 0.06
            py = y - u * alt * 3.2
            r = alt * (0.16 + 0.5 * u)
            a = 165 * (1 - u) ** 1.2
            c.drawCircle(px, py, r, skia.Paint(AntiAlias=True, Color=T.cor_skia((150, 150, 146), a),
                                               MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, r * 0.45 + 0.5)))
    return fn


def cidadezinha(c, t, cam=None, atores=(), extras=None, roll=0.0, ref=None):
    """A cidadezinha toda vista de cima, sob a lua: telhados tortos, ruas de terra, a igreja na praça, poucas
    janelas acesas e luz de poste nas esquinas; o cemitério no morrinho da borda e a trilha de terra escura descendo
    dele até uma das casas; serras em camadas na neblina. Câmera de grua (alta e olhando pra baixo)."""
    cam = cam or CamG(x=2.0, h=34.0, F=900, hz=600, cx=W / 2, z=0.0, pitch=24.0)
    cena = _fixa("cidadezinha", cam, t, _cidade_fixa)
    for k, (X, Y, Z) in enumerate(getattr(cena, "chamines", ())):
        cena.ator(X, Z, fumaca(t, semente=k), 2.4, Y=Y, rim=0.0)
    for a in atores:
        X, Z, desenha, alt = a[:4]
        cena.ator(X, Z, desenha, alt, Y=(a[4] if len(a) > 4 else 0.0))
    corvos_3d(cena, t, n=7, semente=13, volume=(-30, 30, 30, 42, 40, 90))
    if extras:
        extras(cena)
    c.save()
    c.rotate(roll, W / 2, H / 2)
    cena.desenha(c, ceu=lambda cc, ce: _ceu(cc, ce, (0.76, 0.06), 80), nuvens=lambda cc, ce: nuvens(cc, ce, semente=59, faixa=(0.0, 0.12)))
    sombra_frente(c, ini=0.66, k=0.7, lados=0.3)
    mato_frente(c, t, semente=14, altura=(0.1, 0.2), cam=cam, ref=ref)      # o mato do alto do morro de onde a gente olha
    galhos_frente(c, t, lado=-1, semente=15, escala=1.15, cam=cam, ref=ref)
    c.restore()
    return cena


# ---------------------------------------------------------------- o quintal com portão

RELEVO_QUINTAL = Relevo([(4.0, 92.0, 22.0, 10.0, 16.0), (-34.0, 110.0, 20.0, 10.0, 14.0)])


def _quintal_fixo(cam):
    cena = Cena(cam, 0.0, nevoa=NEVOA_LUAR, alcance=48.0, luz=(0.35, 0.55, 0.75), w_tinta=3.0)
    cena.face([(-60, 0, -10), (60, 0, -10), (60, 0, 200), (-60, 0, 200)], (36, 34, 30), z=600, hach=False)
    cena.face([(-6, 0.003, -6), (6, 0.003, -6), (6, 0.003, 8), (-6, 0.003, 8)], (70, 62, 52), z=599, hach=False)
    for x0, x1 in ((-9, -1.3), (1.3, 9)):
        cena.caixa(x0, x1, 0, 1.9, 8.0, 8.3, (126, 118, 104), deforma=torto(lean=0.02, sag=0.03, wob=0.03, semente=int(x0 * 3)),
                   textura_face=lambda pts: tex_parede(pts, 51, picho=0.0, umidade=1.0, rachas=2))
    for k in range(9):
        u = k / 8
        x = -1.3 + 1.2 * u
        z = 8.0 - 1.1 * u
        cena.linha([(x, 0.05, z), (x, 1.85 + 0.15 * math.sin(u * 3), z)], 0.6, z=7.0)
    cena.linha([(-1.3, 0.3, 8.0), (-0.1, 0.3, 6.9)], 0.6, z=7.0)
    cena.linha([(-1.3, 1.5, 8.0), (-0.1, 1.5, 6.9)], 0.6, z=7.0)
    for k in range(9):
        x = 0.1 + k * 0.15
        cena.linha([(x, 0.05, 8.1), (x, 1.85 + 0.12 * math.sin(k), 8.1)], 0.6, z=8.0)
    cena.linha([(0.1, 0.3, 8.1), (1.3, 0.3, 8.1)], 0.6, z=8.0)
    cena.face([(-1.0, 0.004, 8.0), (1.0, 0.004, 8.0), (4.8, 0.004, 80), (3.2, 0.004, 80)], (66, 58, 48), z=598, hach=False)
    trilha_terra(cena, [(0.2, 0.01, 2.0), (0.0, 0.01, 6.0), (0.3, 0.01, 9.0), (1.6, 0.01, 30.0), (3.4, 0.01, 60.0)], larg=0.4, semente=17)
    morro_fatias(cena, RELEVO_QUINTAL, -80, 80, 80, 120, n=18, cor=(32, 34, 34), passo_x=1.5, rim=1.2, semente=21)
    for k in range(18):
        X = -4 + k * 0.9 + _n(k) * 0.4
        cruz(cena, X, 90.0, Y=RELEVO_QUINTAL(X, 90.0) - 0.1, alt=1.4, inclina=_n(k + 7) * 0.2, semente=1300 + k, cor=(70, 68, 66))
    capela(cena, 9.0, 92.0, Y=RELEVO_QUINTAL(9.0, 92.0) - 0.5, semente=23, acesa=0.5)
    cena.caixa(-4.6, -3.2, 0, 1.0, 4.6, 5.8, (96, 76, 60), textura_face=lambda pts: tex_tabuas(pts, 4, ao_longo=1))
    cena.face([(-4.8, 1.0, 4.5), (-3.0, 1.0, 4.5), (-3.9, 1.6, 4.5)], (84, 66, 52), z=4.4)
    cena.face([(-4.25, 0.0, 4.58), (-3.55, 0.0, 4.58), (-3.55, 0.65, 4.58), (-3.9, 0.8, 4.58), (-4.25, 0.65, 4.58)], (8, 6, 6), z=4.39, hach=False)
    poco(cena, 4.2, 5.5, semente=7)
    arvore_seca(cena, -6.5, 7.0, alt=7.5, semente=33, galhos=7, inclina=0.12, grossura=2.6)
    for x in (-5.5, 2.5):
        cena.linha([(x, 0, 2.5), (x, 2.0, 2.5)], 1.0)
    fio(cena, (-5.5, 1.95, 2.5), (2.5, 1.95, 2.5), barriga=0.25, k=0.4)
    for k, (u, larg, alt, cor) in enumerate(((0.2, 0.5, 0.7, (120, 116, 112)), (0.45, 0.4, 0.9, (90, 86, 96)), (0.75, 0.5, 0.6, (130, 120, 104)))):
        x = -5.5 + 8 * u
        y = 1.95 - 0.25 * 4 * u * (1 - u)
        cena.face([(x - larg / 2, y, 2.5), (x + larg / 2, y, 2.5), (x + larg / 2, y - alt, 2.55), (x - larg / 2, y - alt, 2.55)], cor, z=2.45)
    lampiao(cena, 2.2, 8.4, Y=0.0, alt=2.6, semente=14)
    cena.luz(-3.9, 2.0, -3.0, 4.0, (236, 176, 96), 0.7, chao=True)
    for zn, al, hh in ((10.0, 0.12, 0.8), (24.0, 0.2, 1.2), (50.0, 0.3, 2.4), (80.0, 0.36, 5.0)):
        cena.neblina(zn, altura=hh, alfa=al)
    return cena


def quintal(c, t, cam=None, atores=(), extras=None, roll=0.0, ref=None):
    """Quintal à noite: terreiro, muro com reboco e umidade, portão de ferro aberto, casinha do cachorro, varal,
    poço, árvore seca, lampião; a trilha de terra sai pelo portão e segue pela estrada até o morro do cemitério lá
    longe, sob a lua. Use com a grua (`cam` subindo) nos planos 5 e 6 do roteiro."""
    cam = cam or CamG(x=0.0, h=1.4, F=950, hz=1040, cx=W / 2, z=-4.5, pitch=-3.0)
    cena = _fixa("quintal", cam, t, _quintal_fixo)
    for a in atores:
        X, Z, desenha, alt = a[:4]
        cena.ator(X, Z, desenha, alt, Y=(a[4] if len(a) > 4 else 0.0))
    corvos_3d(cena, t, n=4, semente=19)
    if extras:
        extras(cena)
    c.save()
    c.rotate(roll, W / 2, H / 2)
    cena.desenha(c, ceu=lambda cc, ce: _ceu(cc, ce, (0.62, 0.12), 104), nuvens=lambda cc, ce: nuvens(cc, ce, semente=61, faixa=(0.02, 0.3)))
    sombra_frente(c, ini=0.62, k=0.7)
    mato_frente(c, t, semente=12, altura=(0.08, 0.16), cam=cam, ref=ref)
    c.restore()
    return cena
