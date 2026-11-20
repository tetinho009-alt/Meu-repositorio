# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Interiores em diorama de papel (caixa de papel com a parede da frente aberta): quarto com vela e relógios parados, corredor com fotos tortas e a trilha
de terra, cozinha com a mesa, a carta e a foto da família, sala com a porta da frente e a fechadura, e a janela da
sala vista de dentro pra estrada. Mais os objetos de close: o despertador antigo de corda e a vela.

Mesma construção dos outros cenários (cenario3d.Cena, câmera CamG que pode girar), com a casa montada uma vez e
guardada em cache; `atores=[(X, Z, desenha, altura_m)]`, `extras(cena)` pra itens vivos (use `vivo=True`).
"""
import math
import random

import numpy as np
import skia

from . import tinta as T
from .interface import FONTES, TEXTO
from .cenario3d import (LAMPADA, LUA, W, H, CamG, Cena, _fixa, _quarto_fixo, _tex_listras, _tex_retrato, _cilindro, rachadura,
                        tex_parede, tex_tabuas, torto)
from .paisagens import trilha_terra

LUZ_VELA = (240, 170, 90)


# ---------------------------------------------------------------- objetos de close (2D)

def despertador(c, cx, cy, r, hora=10, minuto=10, segundo=0.0, t=0.0, reflexo=None, deita=0.0):
    """Despertador antigo de corda (duas campainhas, martelo, pezinhos): mostrador de números, ponteiros, vidro com
    brilho. `reflexo(c)` desenha algo dentro do vidro (a figura atrás da cama), já recortado e apagado."""
    var = T.ferve(t)
    d = T.Desenho()
    for l in (-1, 1):   # campainhas e martelo
        bx, by = cx + l * r * 0.62, cy - r * 0.92
        T.forma(d, T.catmull([(bx - r * 0.34, by + r * 0.12), (bx - r * 0.28, by - r * 0.2), (bx, by - r * 0.32), (bx + r * 0.28, by - r * 0.2),
                              (bx + r * 0.34, by + r * 0.12)], True, 8), (150, 132, 96), var, 10 + l, contorno=r * 0.03, sombra=0.9,
                passo_h=max(3.0, r * 0.04))
        T.linha(d, [(bx - l * r * 0.12, by + r * 0.12), (cx + l * r * 0.16, cy - r * 0.9)], r * 0.035, var, 14 + l)
    T.linha(d, [(cx, cy - r * 1.02), (cx, cy - r * 1.28)], r * 0.035, var, 16)
    T.forma(d, T.elipse(cx, cy - r * 1.3, r * 0.07, r * 0.05, 12), (150, 132, 96), var, 17, contorno=r * 0.02, sombra=0.5, hach=False)
    for l in (-1, 1):   # pezinhos
        T.forma(d, T.quina([(cx + l * r * 0.5, cy + r * 0.82), (cx + l * r * 0.72, cy + r * 1.12), (cx + l * r * 0.58, cy + r * 1.14),
                            (cx + l * r * 0.38, cy + r * 0.86)], True, 4), (120, 104, 76), var, 18 + l, contorno=r * 0.025, sombra=0.6, hach=False)
    T.forma(d, T.elipse(cx, cy, r, r, 64), (150, 132, 96), var, 1, contorno=r * 0.045, sombra=1.0, passo_h=max(3.0, r * 0.04))
    mostrador = T.elipse(cx, cy, r * 0.84, r * 0.84, 64)
    T.forma(d, mostrador, (218, 206, 176), var, 2, contorno=r * 0.02, sombra=0.4, hach=False)
    d.desenha(c)
    f = skia.Font(skia.Typeface.MakeFromFile(str(FONTES / TEXTO)), r * 0.17)   # números na fonte de texto do estilo
    for k in range(60):
        a = math.radians(k * 6 - 90)
        r0 = r * (0.72 if k % 5 else 0.66)
        c.drawLine(cx + math.cos(a) * r0, cy + math.sin(a) * r0, cx + math.cos(a) * r * 0.78, cy + math.sin(a) * r * 0.78,
                   skia.Paint(AntiAlias=True, Color=T.cor_skia(T.TINTA, 220), StrokeWidth=r * (0.012 if k % 5 else 0.025)))
    for n in range(1, 13):
        a = math.radians(n * 30 - 90)
        s = str(n)
        w = f.measureText(s)
        c.drawString(s, cx + math.cos(a) * r * 0.54 - w / 2, cy + math.sin(a) * r * 0.54 + r * 0.06, f,
                     skia.Paint(AntiAlias=True, Color=T.cor_skia((40, 30, 24))))
    if reflexo:   # a figura no vidro, por baixo do brilho
        c.save()
        c.clipPath(T.caminho(mostrador), doAntiAlias=True)
        c.saveLayer(None, skia.Paint(Alphaf=0.55))
        reflexo(c)
        c.restore()
        c.restore()
    for ang, comp, larg, cor in ((((hora % 12) + minuto / 60) * 30 - 90, 0.42, 0.05, T.TINTA), (minuto * 6 + segundo * 0.1 - 90, 0.66, 0.035, T.TINTA),
                                 (segundo * 6 - 90, 0.72, 0.012, (120, 30, 24))):
        a = math.radians(ang)
        pts = np.array([(cx - math.cos(a) * r * 0.1, cy - math.sin(a) * r * 0.1), (cx + math.cos(a) * r * comp, cy + math.sin(a) * r * comp)])
        c.drawPath(T.traco_tinta(pts, r * larg, var, int(ang) + 99, amp=0.3, ponta=(0.0, 0.6)), T.tinta_paint(cor))
    c.drawCircle(cx, cy, r * 0.04, T.tinta_paint(T.TINTA))
    brilho = skia.Path()
    brilho.addArc(skia.Rect.MakeXYWH(cx - r * 0.7, cy - r * 0.7, r * 1.4, r * 1.4), 200, 60)
    c.drawPath(brilho, skia.Paint(AntiAlias=True, Color=T.cor_skia((255, 240, 210), 90), Style=skia.Paint.kStroke_Style,
                                  StrokeWidth=r * 0.08, StrokeCap=skia.Paint.kRound_Cap))


def vela(c, x, y, s, t, deita=0.0, acesa=1.0, altura=1.0):
    """Vela num castiçal de lata (2D, pra close e pra cena): cera escorrida, pavio, chama que dança e deita pro lado
    `deita` (-1..1: o vento da porta) e halo quente. (x, y) = base; `s` = px por unidade (vela de ~170 unidades)."""
    var = T.ferve(t)
    d = T.Desenho()
    T.forma(d, T.elipse(x, y, 60 * s, 16 * s, 28), (110, 98, 80), var, 1, contorno=3 * s, sombra=0.8, hach=False)
    T.forma(d, T.quina([(x - 16 * s, y - 4 * s), (x + 16 * s, y - 4 * s), (x + 14 * s, y - 20 * s), (x - 14 * s, y - 20 * s)], True, 4),
            (110, 98, 80), var, 2, contorno=2.4 * s, sombra=0.6, hach=False)
    h = 150 * s * altura
    corpo = [(x - 13 * s, y - 18 * s), (x + 13 * s, y - 18 * s), (x + 12 * s, y - 18 * s - h), (x + 4 * s, y - 14 * s - h), (x - 12 * s, y - 18 * s - h)]
    T.forma(d, T.quina(corpo, True, 6), (220, 208, 180), var, 3, contorno=2.6 * s, sombra=0.7, passo_h=max(3.0, 4 * s))
    for k, (dx, comp) in enumerate(((-12, 40), (8, 70), (12, 26))):   # cera escorrida
        T.linha(d, [(x + dx * s, y - 18 * s - h + 4 * s), (x + dx * s * 1.05, y - 18 * s - h + comp * s)], 5 * s, var, 10 + k, cor=(220, 208, 180),
                ponta=(0.0, 0.2))
    d.desenha(c)
    topo = y - 18 * s - h
    c.drawLine(x, topo, x, topo - 12 * s, skia.Paint(AntiAlias=True, Color=T.cor_skia(T.TINTA), StrokeWidth=2.4 * s))
    if acesa > 0:
        osc = 0.12 * math.sin(t * 17) + 0.06 * math.sin(t * 31)
        dx = (deita + osc) * 34 * s
        alt = 46 * s * (1 + 0.08 * math.sin(t * 23))
        chama = T.catmull([(x, topo - 8 * s), (x + 9 * s, topo - 20 * s), (x + dx * 0.6 + 4 * s, topo - alt * 0.7), (x + dx, topo - alt),
                           (x + dx * 0.6 - 4 * s, topo - alt * 0.7), (x - 9 * s, topo - 20 * s)], True, 6)
        c.drawCircle(x + dx * 0.4, topo - alt * 0.5, 260 * s * acesa, skia.Paint(AntiAlias=True, BlendMode=skia.BlendMode.kScreen,
                     Shader=skia.GradientShader.MakeRadial(skia.Point(x + dx * 0.4, topo - alt * 0.5), 260 * s,
                                                           [T.cor_skia(LUZ_VELA, 110 * acesa), T.cor_skia(LUZ_VELA, 30 * acesa), T.cor_skia(LUZ_VELA, 0)],
                                                           [0.0, 0.35, 1.0])))
        c.drawPath(T.caminho(chama), T.tinta_paint((250, 220, 150), 255 * acesa))
        c.drawPath(T.caminho(T.elipse(x + dx * 0.25, topo - alt * 0.32, 4 * s, 9 * s, 12)), T.tinta_paint((90, 70, 110), 180 * acesa))
        c.drawPath(T.traco_tinta(chama, 1.6 * s, var, 33, fechado=True, amp=0.4), T.tinta_paint((70, 34, 12), 200 * acesa))


# ---------------------------------------------------------------- peças da casa (3D)

def comodo(cena, x0, x1, y1, z0, zf, parede=(132, 120, 100), papel2=(118, 108, 92), piso=(80, 64, 50), teto=(66, 60, 56), semente=1, listras=14):
    """Caixa do cômodo (piso de tábua, paredes de papel listrado com umidade, teto rachado), torta de leve."""
    df = torto(lean=0.015, wob=0.03, semente=semente)
    pis = [df((x0, 0, z0)), df((x1, 0, z0)), df((x1, 0, zf)), df((x0, 0, zf))]
    cena.face(pis, piso, z=100, hach=False, textura=tex_tabuas(pis, 9, ao_longo=1))
    cena.face([df((x0, y1, z0)), df((x1, y1, z0)), df((x1, y1 + 0.08, zf)), df((x0, y1, zf))], teto, z=100)
    fundo = [df((x0, 0, zf)), df((x1, 0, zf)), df((x1, y1 + 0.08, zf)), df((x0, y1, zf))]
    cena.face(fundo, parede, z=99, hach=False, textura=_dupla(_tex_listras(fundo, listras), tex_parede(fundo, semente, picho=0.0, umidade=1.0,
                                                                                                         rachas=2, reboco=False)))
    for x in (x0, x1):
        lado = [df((x, 0, z0)), df((x, 0, zf)), df((x, y1, zf)), df((x, y1, z0))]
        cena.face(lado, papel2, z=98, textura=_dupla(_tex_listras(lado, int(listras * 1.5), eixo=1),
                                                    tex_parede(lado, semente + int(x * 10), picho=0.0, umidade=1.0, rachas=1, reboco=False)))
    cena.linha([df((x0, 0.12, zf)), df((x1, 0.12, zf))], 0.6, z=97)
    rachadura(cena, df((0.3 * (x0 + x1), y1, (z0 + zf) / 2)), (0.4, 0, 1), 2.0, semente + 5, z=97)
    return df


def _dupla(a, b):
    return lambda c, cena, f: (a(c, cena, f), b(c, cena, f))


def quadro_parede(cena, pts, riscado=False, foto=True, z=95.5, semente=1):
    """Porta-retrato torto na parede (pontos 3D, já no plano da parede). `riscado` = o rosto do pai riscado à unha."""
    def tex(c, cena_, f):
        r = c.getLocalClipBounds()
        _tex_retrato()(c, cena_, f)
        if riscado:
            rnd = random.Random(semente)
            cx, cy = r.centerX(), r.centerY() - r.height() * 0.1
            p = skia.Path()
            for k in range(7):
                p.moveTo(cx - r.width() * 0.2 + rnd.uniform(-3, 3), cy - r.height() * 0.15 + k * 3)
                p.lineTo(cx + r.width() * 0.2 + rnd.uniform(-3, 3), cy + r.height() * 0.1 + k * 3)
            c.drawPath(p, skia.Paint(AntiAlias=True, Color=T.cor_skia((230, 222, 200), 220), Style=skia.Paint.kStroke_Style,
                                     StrokeWidth=max(1.0, r.width() * 0.015)))
    cena.face(pts, (66, 54, 44), contorno=1.0, z=z, textura=tex if foto else None)


def porta_frente(cena, x0, x1, Z, y1=2.15, abre=0.0, fechadura=True, df=None):
    """Porta da frente de madeira (na parede do fundo, plano Z): almofadas, maçaneta, espelho da fechadura com o
    buraco (onde o olho aparece), fresta de baixo com a terra entrando."""
    df = df or (lambda p: p)
    folha = [df((x0, 0.02, Z - 0.02)), df((x1, 0.02, Z - 0.02)), df((x1, y1, Z - 0.02)), df((x0, y1, Z - 0.02))]
    cena.face(folha, (84, 64, 50), z=96.8, textura=tex_tabuas(folha, 5, ao_longo=1))
    for yy in (0.25, 1.15):   # almofadas
        a = [df((x0 + 0.12, yy, Z - 0.03)), df((x1 - 0.12, yy, Z - 0.03)), df((x1 - 0.12, yy + 0.75, Z - 0.03)), df((x0 + 0.12, yy + 0.75, Z - 0.03))]
        cena.face(a, (74, 56, 44), z=96.75, contorno=0.7)
    cena.linha([df((x0 - 0.08, 0, Z - 0.02)), df((x0 - 0.08, y1 + 0.08, Z - 0.02)), df((x1 + 0.08, y1 + 0.08, Z - 0.02)),
                df((x1 + 0.08, 0, Z - 0.02))], 1.4, z=96.7)
    mx = x1 - 0.14
    if fechadura:
        cena.face([df((mx - 0.04, 0.92, Z - 0.04)), df((mx + 0.04, 0.92, Z - 0.04)), df((mx + 0.04, 1.12, Z - 0.04)), df((mx - 0.04, 1.12, Z - 0.04))],
                  (60, 54, 48), z=96.7, contorno=0.6)
        cena.face([df((mx - 0.012, 0.96, Z - 0.05)), df((mx + 0.012, 0.96, Z - 0.05)), df((mx + 0.012, 1.0, Z - 0.05)), df((mx - 0.012, 1.0, Z - 0.05))],
                  (4, 2, 2), z=96.69, contorno=0.0, hach=False)
    _cilindro(cena, mx, 1.04, Z - 0.08, 0.035, 0.035, 0.0, (150, 130, 96), n=10)
    cena.face([df((x0, 0.0, Z - 0.03)), df((x1, 0.0, Z - 0.03)), df((x1, 0.025, Z - 0.03)), df((x0, 0.025, Z - 0.03))], (4, 2, 2), z=96.68,
              contorno=0.0, hach=False)   # a fresta de baixo


def mesa(cena, X, Z, w=1.6, d_=1.0, h=0.78, cor=(96, 74, 56), semente=1):
    df = torto(wob=0.01, semente=semente)
    tampo = [df((X - w / 2, h, Z - d_ / 2)), df((X + w / 2, h, Z - d_ / 2)), df((X + w / 2, h, Z + d_ / 2)), df((X - w / 2, h, Z + d_ / 2))]
    cena.face(tampo, cor, textura=tex_tabuas(tampo, 5, ao_longo=0))
    cena.caixa(X - w / 2, X + w / 2, h - 0.06, h, Z - d_ / 2, Z + d_ / 2, T.escurece(cor, 0.85), deforma=df, topo=False)
    for sx in (-1, 1):
        for sz in (-1, 1):
            cena.caixa(X + sx * (w / 2 - 0.08) - 0.04, X + sx * (w / 2 - 0.08) + 0.04, 0, h - 0.06, Z + sz * (d_ / 2 - 0.08) - 0.04,
                       Z + sz * (d_ / 2 - 0.08) + 0.04, T.escurece(cor, 0.8), deforma=df)


def cadeira(cena, X, Z, rot=0.0, cor=(88, 68, 52), semente=1):
    """Cadeira de madeira de espaldar alto (a do pai), virada `rot` rad."""
    df = torto(rot=rot, wob=0.01, semente=semente, base=(X, 0, Z))
    cena.caixa(X - 0.22, X + 0.22, 0.42, 0.47, Z - 0.22, Z + 0.22, cor, deforma=df)
    for sx in (-1, 1):
        for sz in (-1, 1):
            cena.caixa(X + sx * 0.18 - 0.025, X + sx * 0.18 + 0.025, 0, 0.42, Z + sz * 0.18 - 0.025, Z + sz * 0.18 + 0.025, T.escurece(cor, 0.8), deforma=df)
    for sx in (-1, 1):
        cena.caixa(X + sx * 0.18 - 0.025, X + sx * 0.18 + 0.025, 0.47, 1.15, Z + 0.18, Z + 0.23, cor, deforma=df)
    for yy in (0.7, 0.92, 1.1):
        cena.caixa(X - 0.2, X + 0.2, yy, yy + 0.05, Z + 0.19, Z + 0.22, cor, deforma=df)


def carta(cena, X, Y, Z, rot=0.2, aberta=0.0):
    """A carta velha suja de terra em cima da mesa ("Pra Clarinha"), com torrões em volta."""
    ca, sa = math.cos(rot), math.sin(rot)

    def P(x, z):
        return (X + x * ca - z * sa, Y + 0.004, Z + x * sa + z * ca)
    pts = [P(-0.16, -0.11), P(0.16, -0.11), P(0.16, 0.11), P(-0.16, 0.11)]

    def tex(c, cena_, f):
        r = c.getLocalClipBounds()
        rnd = random.Random(4)
        for k in range(6):
            c.drawCircle(rnd.uniform(r.left(), r.right()), rnd.uniform(r.top(), r.bottom()), r.width() * rnd.uniform(0.05, 0.14),
                         skia.Paint(AntiAlias=True, Color=T.cor_skia((70, 54, 40), 150), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle,
                                                                                                                    max(1.0, r.width() * 0.03))))
        p = skia.Path()
        p.moveTo(r.left(), r.top())
        p.lineTo(r.centerX(), r.centerY())
        p.lineTo(r.right(), r.top())
        c.drawPath(p, skia.Paint(AntiAlias=True, Color=T.cor_skia(T.TINTA, 150), Style=skia.Paint.kStroke_Style, StrokeWidth=1.2))
    cena.face(pts, (196, 180, 146), contorno=0.7, hach=False, textura=tex)
    if aberta > 0:
        folha = [P(-0.15, -0.11), P(0.15, -0.11), P(0.15, -0.11 - 0.32 * aberta), P(-0.15, -0.11 - 0.32 * aberta)]
        cena.face([(p[0], p[1] + 0.02 * aberta, p[2]) for p in folha], (210, 196, 162), contorno=0.7, hach=False)


def relogio_parede(cena, X, Y, Z, r=0.22, plano="z", hora=10, minuto=10):
    """Relógio redondo de parede parado (o mostrador desenhado no plano da parede)."""
    pts = []
    for a in np.linspace(0, 2 * math.pi, 24, endpoint=False):
        if plano == "z":
            pts.append((X + r * math.cos(a), Y + r * math.sin(a), Z))
        else:
            pts.append((X, Y + r * math.sin(a), Z + r * math.cos(a)))

    def tex(c, cena_, f):
        rr = c.getLocalClipBounds()
        cx, cy = rr.centerX(), rr.centerY()
        rad = min(rr.width(), rr.height()) / 2
        c.drawCircle(cx, cy, rad * 0.86, T.tinta_paint((214, 202, 172)))
        for k in range(12):
            a = math.radians(k * 30)
            c.drawLine(cx + math.cos(a) * rad * 0.68, cy + math.sin(a) * rad * 0.68, cx + math.cos(a) * rad * 0.82, cy + math.sin(a) * rad * 0.82,
                       skia.Paint(AntiAlias=True, Color=T.cor_skia(T.TINTA), StrokeWidth=max(1.0, rad * 0.05)))
        for ang, comp in (((hora + minuto / 60) * 30 - 90, 0.45), (minuto * 6 - 90, 0.7)):
            a = math.radians(ang)
            c.drawLine(cx, cy, cx + math.cos(a) * rad * comp, cy + math.sin(a) * rad * comp,
                       skia.Paint(AntiAlias=True, Color=T.cor_skia(T.TINTA), StrokeWidth=max(1.2, rad * 0.06), StrokeCap=skia.Paint.kRound_Cap))
    cena.face(pts, (110, 90, 66), contorno=1.0, hach=False, textura=tex, z=95.4)


def vela3d(cena, X, Y, Z, forca=1.0):
    """Vela num pires (3D) com a luz quente que treme e um halo."""
    _cilindro(cena, X, Y, Z, 0.09, 0.09, 0.012, (110, 98, 80), n=12)
    _cilindro(cena, X, Y + 0.012, Z, 0.022, 0.022, 0.16, (222, 210, 180), n=10)
    cena.face([(X - 0.012, Y + 0.18, Z), (X + 0.012, Y + 0.18, Z), (X + 0.004, Y + 0.24, Z)], (250, 220, 150), contorno=0.4, hach=False,
              luz_extra=1.0, z=Z - 0.05)
    cena.luz(X, Y + 0.22, Z, 2.6, LUZ_VELA, forca, chao=False, pisca=7)


# ---------------------------------------------------------------- luz, sombra e textura dos cômodos

LUAR = (150, 170, 205)          # luar azul que entra pela janela
LAMPIAO = (244, 176, 92)


def _P(face_pts):
    A, B, C_, D = [np.array(p, float) for p in face_pts]
    return lambda u, v: (A + (B - A) * u) * (1 - v) + (D + (C_ - D) * u) * v


def tex_descasca(face_pts, semente=1, n=4, mofo=0.8, rachas=2):
    """Papel de parede descascando (o reboco aparecendo, a ponta do papel enrolada com sombra), mofo esverdeado
    nos cantos de cima e de baixo, rachadura de nanquim. Tudo no plano da face."""
    P = _P(face_pts)

    def tex(c, cena, f):
        k = 1 - f
        if k < 0.08:
            return
        rnd = random.Random(semente)
        for i in range(n):
            u0, v0 = rnd.uniform(0.08, 0.9), rnd.uniform(0.25, 0.9)
            ru, rv = rnd.uniform(0.04, 0.1), rnd.uniform(0.06, 0.14)
            borda = [P(u0 + ru * math.cos(a) * rnd.uniform(0.6, 1.2), v0 + rv * math.sin(a) * rnd.uniform(0.6, 1.2))
                     for a in np.linspace(0, 2 * math.pi, 11, endpoint=False)]
            scr = np.array([cena.p(q) for q in borda])
            c.drawPath(T.caminho(scr, True), T.tinta_paint((176, 166, 146), 225 * k))
            c.drawPath(T.traco_tinta(scr, 1.3, cena.var, semente * 13 + i, fechado=True, amp=0.5), T.tinta_paint(T.TINTA, 200 * k))
            # a ponta do papel que soltou e enrolou pra fora, com a sombra embaixo
            a, b = borda[1], borda[3]
            ponta = P(u0 + ru * 0.3, v0 + rv * 1.6)
            tri = np.array([cena.p(a), cena.p(b), cena.p(ponta)])
            p = T.tinta_paint((10, 8, 8), 110 * k)
            p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 3))
            c.drawPath(T.caminho(tri + np.array([3, 5]), True), p)
            c.drawPath(T.caminho(tri, True), T.tinta_paint((150, 136, 112), 235 * k))
            c.drawPath(T.traco_tinta(tri, 1.2, cena.var, semente * 17 + i, fechado=True, amp=0.4), T.tinta_paint(T.TINTA, 210 * k))
        if mofo:
            for i in range(int(7 * mofo)):
                u = rnd.random()
                v = rnd.choice((rnd.uniform(0.85, 1.0), rnd.uniform(0.0, 0.18)))
                x, y = cena.p(P(u, v))
                s_ = cena.cam.escala(P(u, v)[2])
                r = s_ * rnd.uniform(0.12, 0.3)
                c.drawOval(skia.Rect.MakeXYWH(x - r, y - r * 0.7, 2 * r, 1.4 * r), skia.Paint(
                    AntiAlias=True, Color=T.cor_skia((40, 50, 34), 120 * k), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, r * 0.5 + 1)))
                pts = skia.Path()
                for j in range(14):
                    pts.addCircle(x + rnd.uniform(-r, r), y + rnd.uniform(-r * 0.6, r * 0.6), rnd.uniform(0.6, 1.6))
                c.drawPath(pts, T.tinta_paint((26, 30, 20), 150 * k))
        for i in range(rachas):
            u, v = rnd.uniform(0.1, 0.9), rnd.uniform(0.75, 0.99)
            pts = [P(u, v)]
            for j in range(7):
                u += rnd.uniform(-0.035, 0.035)
                v -= rnd.uniform(0.03, 0.08)
                pts.append(P(u, max(0.0, v)))
            scr = np.array([cena.p(q) for q in pts])
            c.drawPath(T.traco_tinta(scr, 1.4, cena.var, semente * 43 + i, amp=0.3, ponta=(0.3, 0.6)), T.tinta_paint(T.TINTA, 210 * k))
    return tex


def textura_solta(cena, pts, tex, z):
    """Só o desenho de uma textura no plano (por cima da parede já pintada), sem preencher a face."""
    zc = float(np.mean([p[2] for p in pts]))
    cena.item(z, lambda c: tex(c, cena, cena.fog(zc)), zg=zc)


def luz_poca(cena, pts3, cor, alfa=90, borra=0.18, z=None, vivo=False):
    """Mancha de luz translúcida num plano (o luar no assoalho, a poça quente da vela na parede): soma por cima do
    que já está pintado (screen), com a borda amaciada conforme a distância."""
    pts3 = [tuple(p) for p in pts3]
    zc = float(np.mean([p[2] for p in pts3]))

    def fn(c):
        scr = np.array([cena.p(p) for p in pts3])
        s_ = cena.cam.escala(zc)
        paint = T.tinta_paint(cor, alfa)
        paint.setBlendMode(skia.BlendMode.kScreen)
        paint.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, max(1.0, borra * s_)))
        c.drawPath(T.caminho(scr, True), paint)
    cena.item(max(p[2] for p in pts3) + 0.02 if z is None else z, fn, vivo=vivo, zg=zc)


def _casco(pts):
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts

    def cruz(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cruz(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cruz(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def sombra_chao(cena, x0, x1, z0, z1, h, luz, alfa=150, borra=0.12, z=None):
    """Sombra projetada no assoalho de uma caixa (móvel) por uma luz pontual: o pé da caixa mais o topo projetado
    a partir da luz. Legível e com a borda mais mole longe do móvel."""
    Lx, Ly, Lz = luz
    base = [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]
    proj = []
    for x, zz in base:
        if h >= Ly - 0.05:
            s_ = 6.0
        else:
            s_ = min(6.0, Ly / (Ly - h))
        proj.append((Lx + (x - Lx) * s_, Lz + (zz - Lz) * s_))
    casco = _casco([(round(a, 4), round(b, 4)) for a, b in base + proj])
    pts3 = [(a, 0.004, b) for a, b in casco]
    zc = float(np.mean([p[2] for p in pts3]))

    def fn(c):
        scr = np.array([cena.p(p) for p in pts3])
        p = T.tinta_paint((8, 6, 8), alfa)
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, max(1.0, borra * cena.cam.escala(zc))))
        c.drawPath(T.caminho(scr, True), p)
    cena.item(max(p[2] for p in pts3) + 0.03 if z is None else z, fn, zg=zc)


def janela_luar(cena, x, z0, z1, y0, y1, lado=1, dir_luz=(-0.75, -0.62, 0.2), cortina=True, df=None, plano="x"):
    """Janela com o luar azul entrando: vidro com a lua, caixilho em cruz, cortina, a mancha da janela projetada no
    assoalho e o feixe de luz no ar. plano "x": parede lateral em x (vão de z0 a z1); plano "z": parede do fundo
    em z = x (vão de z0 a z1 no eixo x)."""
    df = df or (lambda p: p)
    if plano == "z":
        Zp = x
        vid = [df((z0, y0, Zp)), df((z1, y0, Zp)), df((z1, y1, Zp)), df((z0, y1, Zp))]
        cena.face(vid, (58, 70, 92), contorno=1.4, hach=False, z=97.0, luz_extra=0.6)
        a, b, c_, d = [np.array(p) for p in vid]
        cena.linha([(a + b) / 2, (d + c_) / 2], 1.6, z=96.9)
        cena.linha([(a + d) / 2, (b + c_) / 2], 1.6, z=96.9)
        cena.caixa(z0 - 0.08, z1 + 0.08, y0 - 0.06, y0, Zp - 0.12, Zp, (96, 76, 58), deforma=df)
        if cortina:
            for xx, ww in ((z0 - 0.05, 0.28), (z1 + 0.05, -0.28)):
                pano = [df((xx, y1 + 0.12, Zp - 0.04)), df((xx + ww * 0.8, y1 + 0.12, Zp - 0.04)), df((xx + ww * 0.5, y0 - 0.3, Zp - 0.08)),
                        df((xx - ww * 0.15, y0 - 0.3, Zp - 0.06))]
                cena.face(pano, (112, 96, 104), contorno=1.0, z=96.5, textura=_tex_listras(pano, 5, eixo=0, alfa=70))
        dx, dy, dz = dir_luz
        chao = [(p[0] + dx * (p[1] / -dy), 0.003, p[2] + dz * (p[1] / -dy)) for p in vid]
        luz_poca(cena, chao, LUAR, alfa=95, borra=0.08)
        luz_poca(cena, [vid[3], vid[2], chao[2], chao[3]], LUAR, alfa=26, borra=0.3, z=Zp - 0.3)
        luz_poca(cena, [vid[0], vid[1], chao[1], chao[0]], LUAR, alfa=18, borra=0.3, z=Zp - 0.31)
        return chao
    vid = [df((x, y0, z0)), df((x, y0, z1)), df((x, y1, z1)), df((x, y1, z0))]
    cena.face(vid, (58, 70, 92), contorno=1.4, hach=False, z=97.0, luz_extra=0.6)
    a, b, c_, d = [np.array(p) for p in vid]
    cena.linha([(a + b) / 2, (d + c_) / 2], 1.6, z=96.9)
    cena.linha([(a + d) / 2, (b + c_) / 2], 1.6, z=96.9)
    cena.caixa(min(x, x - lado * 0.12), max(x, x - lado * 0.12), y0 - 0.06, y0, z0 - 0.08, z1 + 0.08, (96, 76, 58), deforma=df)  # peitoril
    if cortina:
        for zz, ww in ((z0 - 0.05, 0.28), (z1 + 0.05, -0.28)):
            pano = [df((x - lado * 0.04, y1 + 0.12, zz)), df((x - lado * 0.04, y1 + 0.12, zz + ww * 0.8)),
                    df((x - lado * 0.08, y0 - 0.3, zz + ww * 0.5)), df((x - lado * 0.06, y0 - 0.3, zz - ww * 0.15))]
            cena.face(pano, (112, 96, 104), contorno=1.0, z=96.5, textura=_tex_listras(pano, 5, eixo=1, alfa=70))
    dx, dy, dz = dir_luz
    chao = []
    for p in (vid[0], vid[1], vid[2], vid[3]):
        s_ = p[1] / -dy
        chao.append((p[0] + dx * s_, 0.003, p[2] + dz * s_))
    luz_poca(cena, chao, LUAR, alfa=95, borra=0.08)
    # o feixe no ar: do vidro até a mancha do chão, bem fraco
    ar = [vid[3], vid[2], chao[2], chao[3]]
    luz_poca(cena, ar, LUAR, alfa=26, borra=0.3, z=min(z0, z1) - 0.2)
    luz_poca(cena, [vid[0], vid[1], chao[1], chao[0]], LUAR, alfa=18, borra=0.3, z=min(z0, z1) - 0.21)
    return chao


def rodape(cena, x0, x1, z0, z1, plano="x", cor=(70, 54, 42), semente=1):
    """Rodapé de madeira gasto: a tábua com lascas claras faltando e a junta escura com o piso."""
    if plano == "x":
        pts = [(x0, 0.0, z0 + 0.001), (x0, 0.0, z1), (x0, 0.14, z1), (x0, 0.14, z0 + 0.001)]
    else:
        pts = [(x0, 0.0, z0), (x1, 0.0, z0), (x1, 0.14, z0), (x0, 0.14, z0)]
    P = _P(pts)

    def tex(c, cena_, f):
        rnd = random.Random(semente)
        for i in range(6):
            u = rnd.random()
            q = [P(u, 1.0), P(u + 0.03, 1.0), P(u + 0.02, 0.55)]
            c.drawPath(T.caminho(np.array([cena_.p(p) for p in q]), True), T.tinta_paint((150, 128, 100), 200 * (1 - f)))
    cena.face(pts, cor, contorno=1.0, z=96.0, textura=tex)


# ---------------------------------------------------------------- móveis

def cama_ferro(cena, X, Z0, w=1.2, comp=2.0, semente=1, luz=None):
    """Cama de ferro de cabeceira alta (barras e bolinhas de latão), colchão fino e a colcha de crochê de quadradinhos
    caindo dos lados, travesseiro amassado."""
    Z1 = Z0 + comp
    xl, xr = X - w / 2, X + w / 2
    ferro = (34, 30, 32)
    for zz, alt_ in ((Z1, 1.2), (Z0, 0.86)):
        for xx in (xl, xr):
            cena.linha([(xx, 0.0, zz), (xx, alt_, zz)], 2.6, z=zz - 0.01, cor=ferro)
            cena.face([(xx - 0.05, alt_ + 0.02, zz), (xx + 0.05, alt_ + 0.02, zz), (xx + 0.05, alt_ + 0.1, zz), (xx - 0.05, alt_ + 0.1, zz)],
                      (176, 140, 70), contorno=0.8, hach=False, z=zz - 0.02)
        arco = [(xl + (xr - xl) * u, alt_ - 0.04 + 0.12 * math.sin(math.pi * u), zz) for u in np.linspace(0, 1, 9)]
        cena.linha(arco, 2.0, z=zz - 0.01, cor=ferro)
        cena.linha([(xl, 0.5, zz), (xr, 0.5, zz)], 1.6, z=zz - 0.01, cor=ferro)
        for j in range(1, 6):
            xx = xl + (xr - xl) * j / 6
            cena.linha([(xx, 0.5, zz), (xx, alt_ - 0.04 + 0.12 * math.sin(math.pi * j / 6), zz)], 1.1, z=zz - 0.012, cor=ferro)
    cena.caixa(xl + 0.03, xr - 0.03, 0.34, 0.5, Z0 + 0.03, Z1 - 0.03, (150, 140, 120))
    # travesseiro amassado
    cena.caixa(xl + 0.12, xr - 0.12, 0.5, 0.64, Z1 - 0.5, Z1 - 0.08, (190, 182, 162), deforma=torto(wob=0.03, sag=0.05, semente=semente))
    # colcha de crochê: em cima e caindo na frente e no lado
    topo = [(xl - 0.04, 0.53, Z0 - 0.02), (xr + 0.04, 0.53, Z0 - 0.02), (xr + 0.04, 0.53, Z1 - 0.55), (xl - 0.04, 0.53, Z1 - 0.55)]
    frente = [(xl - 0.04, 0.53, Z0 - 0.04), (xr + 0.04, 0.53, Z0 - 0.04), (xr + 0.08, 0.18, Z0 - 0.08), (xl - 0.08, 0.18, Z0 - 0.08)]
    lado_x = xr + 0.04 if cena.cam.x > X else xl - 0.04
    lado = [(lado_x, 0.53, Z0 - 0.02), (lado_x, 0.53, Z1 - 0.55), (lado_x + (0.05 if lado_x > X else -0.05), 0.16, Z1 - 0.55),
            (lado_x + (0.05 if lado_x > X else -0.05), 0.16, Z0 - 0.02)]
    for pts, n_u, n_v, zz in ((lado, 8, 3, Z0 + 0.4), (topo, 6, 7, Z0 + 0.3), (frente, 6, 2, Z0 - 0.05)):
        cena.face(pts, (176, 150, 120), contorno=1.2, hach=False, z=zz, textura=_tex_croche(pts, n_u, n_v, semente))
    if luz:
        sombra_chao(cena, xl - 0.08, xr + 0.08, Z0 - 0.1, Z1, 0.6, luz, alfa=140)


def _tex_croche(face_pts, n_u=6, n_v=6, semente=1):
    """Colcha de crochê de quadradinhos (granny square): cada quadrado com aro e miolo de cor, ponto de cruz em volta."""
    P = _P(face_pts)
    cores = ((150, 64, 56), (176, 140, 76), (92, 112, 88), (204, 192, 160), (120, 80, 96))

    def tex(c, cena, f):
        rnd = random.Random(semente)
        k = 1 - f
        for i in range(n_u):
            for j in range(n_v):
                u0, u1, v0, v1 = i / n_u, (i + 1) / n_u, j / n_v, (j + 1) / n_v
                q = np.array([cena.p(P(u0, v0)), cena.p(P(u1, v0)), cena.p(P(u1, v1)), cena.p(P(u0, v1))])
                c.drawPath(T.caminho(q, True), T.tinta_paint(rnd.choice(cores), 170 * k))
                m = q.mean(axis=0)
                miolo = m + (q - m) * 0.45
                c.drawPath(T.caminho(miolo, True), T.tinta_paint(rnd.choice(cores), 210 * k))
                c.drawPath(T.caminho(q, True), skia.Paint(AntiAlias=True, Color=T.cor_skia(T.TINTA, 150 * k), Style=skia.Paint.kStroke_Style,
                                                          StrokeWidth=1.0))
        # babado de bolinhas na beira de baixo
        for i in range(n_u * 3):
            x, y = cena.p(P((i + 0.5) / (n_u * 3), 0.0))
            c.drawCircle(x, y + 2, 2.6, T.tinta_paint((204, 192, 160), 200 * k))
    return tex


def guarda_roupa(cena, x0, x1, z0, z1, h=2.05, cor=(88, 64, 48), luz=None, espelho=True):
    """Guarda-roupa de madeira escura de duas portas (de frente pra câmera, no plano z0): tábuas, cornija em cima,
    pezinhos, puxadores, espelho manchado numa porta e a fresta preta da outra entreaberta."""
    cena.caixa(x0, x1, 0.1, h, z0, z1, cor, textura=tex_tabuas([(x0, 0.1, z0), (x1, 0.1, z0), (x1, h, z0), (x0, h, z0)], 6, ao_longo=1))
    cena.caixa(x0 - 0.05, x1 + 0.05, h, h + 0.1, z0 - 0.05, z1 + 0.03, T.escurece(cor, 0.85))
    for xx in (x0 + 0.06, x1 - 0.1):
        cena.caixa(xx, xx + 0.04, 0.0, 0.1, z0 + 0.05, z0 + 0.09, T.escurece(cor, 0.7))
    xm = (x0 + x1) / 2
    cena.linha([(xm, 0.12, z0 - 0.005), (xm, h - 0.02, z0 - 0.005)], 1.2, z=z0 - 0.01)
    cena.face([(xm + 0.005, 0.14, z0 - 0.006), (xm + 0.03, 0.14, z0 - 0.006), (xm + 0.03, h - 0.04, z0 - 0.006), (xm + 0.005, h - 0.04, z0 - 0.006)],
              (6, 4, 6), contorno=0.0, hach=False, z=z0 - 0.012)   # fresta preta da porta entreaberta
    if espelho:
        esp = [(x0 + 0.1, 0.5, z0 - 0.008), (xm - 0.08, 0.5, z0 - 0.008), (xm - 0.08, 1.75, z0 - 0.008), (x0 + 0.1, 1.75, z0 - 0.008)]

        def tex(c, cena_, f):
            q = np.array([cena_.p(p) for p in esp])
            r = skia.Rect.MakeLTRB(q[:, 0].min(), q[:, 1].min(), q[:, 0].max(), q[:, 1].max())
            c.drawRect(r, skia.Paint(Shader=skia.GradientShader.MakeLinear(
                [skia.Point(r.left(), r.top()), skia.Point(r.right(), r.bottom())],
                [T.cor_skia((70, 80, 92)), T.cor_skia((118, 126, 132)), T.cor_skia((54, 60, 70))], [0.0, 0.45, 1.0])))
            rnd = random.Random(3)
            for i in range(5):   # o aço do espelho manchado nas bordas
                c.drawCircle(rnd.choice((r.left(), r.right())) + rnd.uniform(-6, 6), rnd.uniform(r.top(), r.bottom()), rnd.uniform(6, 16),
                             skia.Paint(AntiAlias=True, Color=T.cor_skia((40, 36, 30), 150),
                                        MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 5)))
        cena.face(esp, (90, 100, 110), contorno=1.4, hach=False, z=z0 - 0.015, textura=tex)
    for xx in (xm - 0.05, xm + 0.05):
        cena.face([(xx - 0.012, 1.0, z0 - 0.02), (xx + 0.012, 1.0, z0 - 0.02), (xx + 0.012, 1.14, z0 - 0.02), (xx - 0.012, 1.14, z0 - 0.02)],
                  (176, 140, 70), contorno=0.6, hach=False, z=z0 - 0.02)
    if luz:
        sombra_chao(cena, x0, x1, z0, z1, h, luz, alfa=150)


def santinho(cena, X, Y, Z, w=0.32, h=0.44, semente=1):
    """Santinho emoldurado na parede (plano z): moldura dourada de topo em arco, a santa de manto azul com a auréola
    e o ramo bento seco atrás da moldura. Imagem genérica, desenhada aqui."""
    pts = [(X - w / 2, Y, Z), (X + w / 2, Y, Z)] + [(X + w / 2 * math.cos(a), Y + h - w / 2 + w / 2 * math.sin(a), Z) for a in np.linspace(0, math.pi, 9)]
    for k in range(3):   # o ramo bento seco atravessado atrás
        cena.linha([(X - w * 0.9, Y + h * 0.9 - 0.05 * k, Z + 0.01), (X + w * 0.8, Y + h * 1.1 + 0.04 * k, Z + 0.01)], 0.8, z=95.6, cor=(96, 84, 54))

    def tex(c, cena_, f):
        q = np.array([cena_.p(p) for p in pts])
        r = skia.Rect.MakeLTRB(q[:, 0].min(), q[:, 1].min(), q[:, 0].max(), q[:, 1].max())
        c.drawRect(r, T.tinta_paint((196, 170, 110)))
        cx, cy, s_ = r.centerX(), r.top() + r.height() * 0.32, r.width()
        c.drawCircle(cx, cy, s_ * 0.2, skia.Paint(AntiAlias=True, Color=T.cor_skia((250, 230, 160), 230), Style=skia.Paint.kStroke_Style,
                                                  StrokeWidth=max(1.0, s_ * 0.03)))
        manto = skia.Path()
        manto.moveTo(cx, cy - s_ * 0.12)
        manto.lineTo(cx + s_ * 0.3, r.bottom() - s_ * 0.06)
        manto.lineTo(cx - s_ * 0.3, r.bottom() - s_ * 0.06)
        manto.close()
        c.drawPath(manto, T.tinta_paint((60, 80, 128)))
        c.drawCircle(cx, cy, s_ * 0.1, T.tinta_paint((214, 182, 150)))
        c.drawPath(manto, skia.Paint(AntiAlias=True, Color=T.cor_skia(T.TINTA, 200), Style=skia.Paint.kStroke_Style, StrokeWidth=1.0))
    cena.face(pts, (150, 116, 56), contorno=1.6, hach=False, z=95.5, textura=tex)


def tapete(cena, X, Z, rx=0.6, rz=0.4, semente=1):
    """Tapete oval de retalho trançado (anéis de cor) no assoalho."""
    pts = [(X + rx * math.cos(a), 0.006, Z + rz * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 24, endpoint=False)]

    def tex(c, cena_, f):
        q = np.array([cena_.p(p) for p in pts])
        r = skia.Rect.MakeLTRB(q[:, 0].min(), q[:, 1].min(), q[:, 0].max(), q[:, 1].max())
        rnd = random.Random(semente)
        for i in range(7, 0, -1):
            k = i / 7
            c.drawOval(skia.Rect.MakeXYWH(r.centerX() - r.width() / 2 * k, r.centerY() - r.height() / 2 * k, r.width() * k, r.height() * k),
                       skia.Paint(AntiAlias=True, Color=T.cor_skia(T.mistura(rnd.choice(((130, 60, 52), (150, 120, 70), (80, 96, 80), (170, 156, 130),
                                                                                         (96, 70, 90))), (70, 60, 52), 0.45), 220), Style=skia.Paint.kStroke_Style,
                                  StrokeWidth=r.height() / 14))
    cena.face(pts, (140, 110, 80), contorno=1.0, hach=False, z=99.5, textura=tex)


def criado_mudo(cena, X, Z, cor=(84, 62, 46), luz=None):
    cena.caixa(X - 0.25, X + 0.25, 0.0, 0.6, Z - 0.22, Z + 0.22, cor, textura=tex_tabuas([(X - 0.25, 0, Z - 0.22), (X + 0.25, 0, Z - 0.22),
                                                                                          (X + 0.25, 0.6, Z - 0.22), (X - 0.25, 0.6, Z - 0.22)], 2))
    cena.face([(X - 0.03, 0.4, Z - 0.225), (X + 0.03, 0.4, Z - 0.225), (X + 0.03, 0.45, Z - 0.225), (X - 0.03, 0.45, Z - 0.225)], (176, 140, 70),
              contorno=0.6, hach=False, z=Z - 0.23)


def cabideiro(cena, X, Z, luz=None):
    """Cabideiro de pé com o chapéu de feltro do pai pendurado e o paletó escuro."""
    cena.linha([(X, 0.0, Z), (X, 1.75, Z)], 2.4, z=Z, cor=(60, 44, 34))
    for a in (0.0, 2.1, 4.2):   # pés
        cena.linha([(X, 0.12, Z), (X + 0.28 * math.cos(a), 0.0, Z + 0.28 * math.sin(a))], 1.8, z=Z, cor=(60, 44, 34))
    for a in (0.6, 2.6):   # ganchos
        cena.linha([(X, 1.66, Z), (X + 0.16 * math.cos(a), 1.74, Z - 0.1)], 1.2, z=Z - 0.02, cor=(40, 30, 26))
    # paletó pendurado
    pal = [(X - 0.04, 1.68, Z - 0.06), (X + 0.04, 1.68, Z - 0.06), (X + 0.2, 1.56, Z - 0.08), (X + 0.23, 1.2, Z - 0.1), (X + 0.21, 0.86, Z - 0.1),
           (X + 0.05, 0.82, Z - 0.1), (X - 0.06, 0.86, Z - 0.1), (X - 0.2, 0.84, Z - 0.1), (X - 0.22, 1.2, Z - 0.1), (X - 0.19, 1.56, Z - 0.08)]
    cena.face(pal, (30, 28, 32), contorno=1.4, z=Z - 0.05, sombra=0.6)
    for l in (-1, 1):   # gola, lapela e a manga caída
        cena.linha([(X + l * 0.03, 1.66, Z - 0.11), (X + l * 0.09, 1.42, Z - 0.12), (X + l * 0.02, 1.2, Z - 0.12)], 0.8, z=Z - 0.06)
        cena.linha([(X + l * 0.19, 1.55, Z - 0.11), (X + l * 0.17, 1.15, Z - 0.12), (X + l * 0.18, 0.92, Z - 0.12)], 0.7, z=Z - 0.06)
    cena.linha([(X - 0.02, 1.2, Z - 0.12), (X - 0.01, 0.84, Z - 0.12)], 0.8, z=Z - 0.06)
    # chapéu de feltro (aba e copa com a fita)
    aba = [(X + 0.18 + 0.2 * math.cos(a), 1.82 + 0.035 * math.sin(a), Z - 0.1 + 0.2 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 16, endpoint=False)]
    cena.face(aba, (70, 58, 48), contorno=1.2, hach=False, z=Z - 0.12)
    _cilindro(cena, X + 0.18, 1.83, Z - 0.1, 0.11, 0.09, 0.12, (76, 62, 50), n=12)
    cena.linha([(X + 0.07, 1.86, Z - 0.21), (X + 0.29, 1.86, Z - 0.21)], 1.4, z=Z - 0.25, cor=(30, 24, 22))
    if luz:
        sombra_chao(cena, X - 0.25, X + 0.25, Z - 0.15, Z + 0.15, 1.8, luz, alfa=120)


def lampiao_mesa(cena, X, Y, Z, forca=1.0, pisca=11):
    """Lampião de querosene em cima de um móvel: base de lata, a manga de vidro com a chama e a luz quente."""
    _cilindro(cena, X, Y, Z, 0.08, 0.06, 0.1, (120, 104, 76), n=12)
    _cilindro(cena, X, Y + 0.1, Z, 0.05, 0.065, 0.2, (226, 210, 160), n=12)
    cena.face([(X - 0.015, Y + 0.14, Z - 0.07), (X + 0.015, Y + 0.14, Z - 0.07), (X, Y + 0.24, Z - 0.07)], (255, 220, 150), contorno=0.0,
              hach=False, luz_extra=1.0, z=Z - 0.08)
    cena.linha([(X - 0.05, Y + 0.3, Z), (X, Y + 0.38, Z), (X + 0.05, Y + 0.3, Z)], 0.9, z=Z - 0.02)
    cena.luz(X, Y + 0.2, Z, 3.2, LAMPIAO, forca, chao=True, pisca=pisca)


def teto_vigas(cena, x0, x1, y1, z0, zf, zs_vigas, lampada=None, teia=None, semente=1, prateleira=None):
    """O alto do cômodo deixa de ser um buraco preto: forro de tábua, vigas de madeira atravessadas
    (frente e barriga), a lâmpada pendurada APAGADA no fio torcido, teia de aranha num canto e, se pedir, uma
    prateleira alta com potes. `lampada=(X, Z)`, `teia=(X, Z)` (canto), `prateleira=(x0, x1, Z, Y)`."""
    forro = [(x0, y1 - 0.004, z0), (x1, y1 - 0.004, z0), (x1, y1 - 0.004, zf), (x0, y1 - 0.004, zf)]
    cena.face(forro, (96, 78, 60), contorno=0.0, hach=False, z=99.95, textura=tex_tabuas(forro, 14, ao_longo=1, alfa=150))
    rnd = random.Random(semente)
    for k, z in enumerate(zs_vigas):
        h, e = 0.17 + rnd.uniform(-0.02, 0.02), 0.13
        frente = [(x0, y1 - h, z), (x1, y1 - h + rnd.uniform(-0.03, 0.03), z), (x1, y1, z), (x0, y1, z)]
        cena.face(frente, (74, 56, 42), contorno=1.0, z=z - 0.01, textura=tex_tabuas(frente, 2, ao_longo=0, alfa=110))
        barriga = [(x0, y1 - h, z), (x1, y1 - h, z), (x1, y1 - h, z + e), (x0, y1 - h, z + e)]
        cena.face(barriga, (58, 44, 34), contorno=0.9, hach=True, z=z - 0.005)
    if lampada:
        X, Z = lampada
        y_b = y1 - 0.62
        pts = [(X, y1, Z)] + [(X + 0.012 * math.sin(k * 1.7), y1 - (y1 - y_b - 0.08) * k / 6, Z) for k in range(1, 7)]
        cena.linha(pts, 0.9, z=Z - 0.02, cor=(40, 34, 30))                                           # fio torcido
        cena.caixa(X - 0.035, X + 0.035, y_b + 0.02, y_b + 0.1, Z - 0.035, Z + 0.035, (60, 54, 46))   # bocal
        bulbo = [(X + 0.065 * math.cos(a), y_b - 0.03 + 0.075 * math.sin(a), Z - 0.04) for a in np.linspace(0, 2 * math.pi, 16, endpoint=False)]
        cena.face(bulbo, (150, 146, 132), contorno=1.0, hach=False, z=Z - 0.05)                      # vidro apagado
        cena.linha([(X - 0.02, y_b + 0.0, Z - 0.045), (X - 0.035, y_b - 0.05, Z - 0.045)], 0.5, z=Z - 0.06, cor=(214, 210, 196))
    if teia:
        X, Z = teia
        sx = -1 if X > (x0 + x1) / 2 else 1
        raios = [(X + sx * 0.55 * math.cos(a), y1 - 0.55 * math.sin(a), Z - 0.02) for a in np.linspace(0.0, math.pi / 2, 6)]
        for q in raios:
            cena.linha([(X, y1, Z - 0.02), q], 0.45, z=Z - 0.1, cor=(200, 196, 184), alfa=150)
        for r in (0.14, 0.26, 0.38, 0.5):
            arco = [(X + sx * r * math.cos(a), y1 - r * math.sin(a) + 0.02 * math.sin(a * 6), Z - 0.02) for a in np.linspace(0.0, math.pi / 2, 7)]
            cena.linha(arco, 0.35, z=Z - 0.1, cor=(200, 196, 184), alfa=120)
    if prateleira:
        px0, px1, Z, Y = prateleira
        cena.caixa(px0, px1, Y, Y + 0.04, Z - 0.26, Z, (86, 66, 50))
        for k in range(int((px1 - px0) / 0.22)):
            x = px0 + 0.12 + k * 0.22
            hh = rnd.uniform(0.14, 0.26)
            r = rnd.uniform(0.05, 0.08)
            _cilindro(cena, x, Y + 0.04, Z - 0.13, r, r * 0.9, hh, rnd.choice(((150, 120, 90), (110, 120, 110), (170, 150, 120), (90, 70, 60))), n=10)


# ---------------------------------------------------------------- cômodos

QUARTO_VELA = (0.45, 0.82, 4.45)       # onde está a chama da vela do criado-mudo


def _quarto_vela_fixo(cam):
    """O quarto, de verdade: cama de ferro com colcha de crochê, criado-mudo com a vela e o despertador,
    guarda-roupa de espelho, santinho e ramo bento em cima da cama, tapete de retalho, janela com cortina e o luar
    azul no assoalho; papel descascando, mofo e rachadura."""
    cena = Cena(cam, 0.0, nevoa=(30, 28, 34), alcance=40.0, luz=(0.35, 0.5, -0.8), w_tinta=2.6)
    df = comodo(cena, -2.3, 2.3, 2.75, -1.2, 5.0, parede=(138, 124, 102), papel2=(124, 112, 94), semente=4, listras=14)
    fundo = [(-2.3, 0, 4.99), (2.3, 0, 4.99), (2.3, 2.75, 4.99), (-2.3, 2.75, 4.99)]
    textura_solta(cena, fundo, tex_descasca(fundo, 5, n=5), 98.9)
    lado_d = [(2.29, 0, -1.2), (2.29, 0, 5.0), (2.29, 2.75, 5.0), (2.29, 2.75, -1.2)]
    textura_solta(cena, lado_d, tex_descasca(lado_d, 6, n=3), 97.9)
    rodape(cena, -2.3, 2.3, 4.98, 4.98, plano="z", semente=1)
    rodape(cena, 2.28, 2.28, -1.2, 5.0, plano="x", semente=2)
    L = QUARTO_VELA
    tapete(cena, 1.0, 2.9, rx=0.6, rz=0.4, semente=3)
    cama_ferro(cena, -0.55, 2.85, w=1.25, comp=2.05, semente=5, luz=L)
    santinho(cena, -0.55, 1.62, 4.97, semente=6)
    criado_mudo(cena, 0.45, 4.45)
    vela3d(cena, 0.45, 0.6, 4.4, forca=1.1)
    cena.face([(0.62, 0.6, 4.36), (0.8, 0.6, 4.36), (0.8, 0.78, 4.36), (0.62, 0.78, 4.36)], (150, 132, 96), contorno=0.8, hach=False, z=4.3)
    guarda_roupa(cena, -2.25, -1.35, 4.35, 4.95, luz=L)
    relogio_parede(cena, 1.4, 2.0, 4.98, r=0.19, plano="z")
    quadro_parede(cena, [(1.0, 1.25, 4.975), (1.5, 1.22, 4.975), (1.52, 1.62, 4.975), (1.02, 1.65, 4.975)], semente=12)
    janela_luar(cena, 2.29, 3.0, 4.2, 0.95, 2.05, lado=1, dir_luz=(-0.7, -0.62, -0.25))
    sombra_chao(cena, 0.2, 0.7, 4.23, 4.67, 0.6, (1.8, 2.2, 2.0), alfa=90)   # o criado-mudo no luar
    teto_vigas(cena, -2.3, 2.3, 2.75, -1.2, 5.0, (0.7, 2.1, 3.5, 4.75), lampada=(0.35, 2.3), teia=(2.3, 4.98), semente=7,
               prateleira=(-1.25, -0.3, 4.99, 2.1))
    return cena


def quarto_vela(c, t, cam=None, atores=(), extras=None, roll=1.0, escuro=0.42):
    """O quarto à luz de vela (cama de ferro, colcha de crochê, guarda-roupa de espelho, santinho, tapete,
    janela com luar). Gire a câmera em volta da cama com CamG(yaw=...)."""
    cam = cam or CamG(x=0.5, h=1.35, F=980, hz=860, cx=W / 2, z=0.5, pitch=4.0)
    cena = _fixa("quarto_vela", cam, t, _quarto_vela_fixo)
    for X, Z, desenha, alt in atores:
        cena.ator(X, Z, desenha, alt, rim=0.3)
    cena.escuro(escuro, [(*QUARTO_VELA, 3.4, 0.95), (1.2, 0.4, 3.6, 2.2, 0.6), (2.2, 1.5, 3.6, 1.4, 0.75), (0.4, 2.55, 4.2, 2.6, 0.55),
                         (0.35, 2.3, 2.3, 1.4, 0.4)], tom=(6, 4, 8))
    if extras:
        extras(cena)
    c.save()
    c.rotate(roll, W / 2, H / 2)
    c.drawPaint(T.tinta_paint((8, 6, 8)))
    cena.desenha(c)
    c.restore()
    return cena


CORREDOR_LAMPIAO = (0.7, 0.95, 2.9)


def _corredor_fixo(cam):
    cena = Cena(cam, 0.0, nevoa=(24, 22, 26), alcance=30.0, luz=(0.3, 0.5, -0.8), w_tinta=2.6)
    df = comodo(cena, -1.0, 1.0, 2.6, -1.5, 6.4, parede=(124, 112, 94), papel2=(112, 102, 88), semente=21, listras=6)
    for x, s_ in ((-0.99, 31), (0.99, 32)):
        lado = [(x, 0, -1.5), (x, 0, 6.4), (x, 2.6, 6.4), (x, 2.6, -1.5)]
        textura_solta(cena, lado, tex_descasca(lado, s_, n=6), 97.9)
        rodape(cena, x, x, -1.5, 6.4, plano="x", semente=s_)
    porta_frente(cena, -0.45, 0.45, 6.39, df=df)
    # bandeira de vidro em cima da porta: o luar entra azul
    band = [(-0.45, 2.24, 6.38), (0.45, 2.24, 6.38), (0.45, 2.5, 6.38), (-0.45, 2.5, 6.38)]
    cena.face(band, (70, 86, 112), contorno=1.0, hach=False, z=96.6, luz_extra=0.7)
    luz_poca(cena, [(-0.6, 0.003, 6.3), (0.6, 0.003, 6.3), (0.8, 0.003, 4.6), (-0.8, 0.003, 4.6)], LUAR, alfa=55, borra=0.25)
    luz_poca(cena, [(-0.45, 0.003, 6.37), (0.45, 0.003, 6.37), (0.5, 0.003, 6.1), (-0.5, 0.003, 6.1)], LUAR, alfa=120, borra=0.06)   # a fresta
    # passadeira comprida no assoalho
    pas = [(-0.42, 0.006, -0.8), (0.42, 0.006, -0.8), (0.42, 0.006, 5.6), (-0.42, 0.006, 5.6)]
    cena.face(pas, (110, 64, 56), contorno=1.0, hach=False, z=99.4, textura=_tex_listras(pas, 7, eixo=0, alfa=80))
    rnd = random.Random(5)
    for k, z in enumerate((0.6, 1.9, 3.9, 5.1)):   # fotos tortas nas duas paredes
        for x in (-0.985, 0.985):
            if x > 0 and k == 1:
                continue
            yy = 1.35 + rnd.uniform(-0.1, 0.2)
            w, h = rnd.uniform(0.25, 0.4), rnd.uniform(0.3, 0.45)
            inc = rnd.uniform(-0.12, 0.12)
            pts = [(x, yy, z), (x, yy + inc, z + w), (x, yy + h + inc, z + w), (x, yy + h, z)]
            quadro_parede(cena, [df(p) for p in pts], riscado=(k == 2 and x > 0), z=95.4, semente=k)
    for k, z in enumerate((3.2,)):   # porta de quarto entreaberta pro escuro
        cena.face([df((-1.0, 0, z)), df((-1.0, 0, z + 0.85)), df((-1.0, 2.05, z + 0.85)), df((-1.0, 2.05, z))], (8, 6, 8), z=97.2)
        cena.linha([df((-0.99, 0, z - 0.06)), df((-0.99, 2.12, z - 0.06)), df((-0.99, 2.12, z + 0.91)), df((-0.99, 0, z + 0.91))], 1.6, z=97.1)
    L = CORREDOR_LAMPIAO
    cabideiro(cena, -0.68, 1.3, luz=L)
    # aparador com o lampião
    cena.caixa(0.55, 0.98, 0.0, 0.82, 2.6, 3.2, (80, 60, 46), textura=tex_tabuas([(0.55, 0, 2.6), (0.98, 0, 2.6), (0.98, 0.82, 2.6), (0.55, 0.82, 2.6)], 2))
    sombra_chao(cena, 0.55, 0.98, 2.6, 3.2, 0.82, (0.7, 1.3, 2.9), alfa=60)
    lampiao_mesa(cena, *L[:1], 0.82, L[2], forca=1.0)
    trilha_terra(cena, [(0.0, 0.01, 6.3), (0.15, 0.01, 4.4), (-0.1, 0.01, 2.2), (0.1, 0.01, -1.2)], larg=0.2, semente=33)
    teto_vigas(cena, -1.0, 1.0, 2.6, -1.5, 6.4, (0.2, 1.6, 3.0, 4.4, 5.8), lampada=(0.0, 1.5), teia=(-1.0, 6.38), semente=23)
    return cena


def corredor(c, t, cam=None, atores=(), extras=None, roll=0.0, escuro=0.5, luz_vela=None):
    """Corredor da casa: papel listrado descascando, rodapé gasto, fotos tortas (uma com o rosto riscado),
    cabideiro com o chapéu e o paletó do pai, aparador com o lampião aceso, passadeira, porta de quarto entreaberta
    pro escuro, a porta da frente no fim com o luar entrando pela bandeira e pela fresta, e a trilha de terra.
    `luz_vela=(X, Y, Z)` abre a escuridão em volta da vela que a personagem carrega."""
    cam = cam or CamG(x=0.05, h=1.5, F=1040, hz=880, cx=W / 2, z=-1.2, pitch=2.0)
    cena = _fixa("corredor", cam, t, _corredor_fixo)
    for X, Z, desenha, alt in atores:
        cena.ator(X, Z, desenha, alt, rim=0.2)
    buracos = [(0.0, 1.0, 6.3, 1.6, 0.55), (CORREDOR_LAMPIAO[0], 1.1, CORREDOR_LAMPIAO[2], 2.8, 0.95),
               (CORREDOR_LAMPIAO[0] - 0.3, 2.45, CORREDOR_LAMPIAO[2], 2.4, 0.5)]
    if luz_vela:
        buracos.append((*luz_vela, 2.6, 0.95))
        cena.luz(*luz_vela, 2.0, LUZ_VELA, 0.9, chao=False, vivo=True, pisca=5)
    cena.escuro(escuro, buracos, tom=(6, 4, 6))
    if extras:
        extras(cena)
    c.save()
    c.rotate(roll, W / 2, H / 2)
    c.drawPaint(T.tinta_paint((6, 4, 6)))
    cena.desenha(c)
    c.restore()
    return cena


def _tex_xadrez(face_pts, n_u=10, n_v=6):
    P = _P(face_pts)

    def tex(c, cena, f):
        k = 1 - f
        for i in range(n_u):
            for j in range(n_v):
                if (i + j) % 2:
                    continue
                q = np.array([cena.p(P(i / n_u, j / n_v)), cena.p(P((i + 1) / n_u, j / n_v)), cena.p(P((i + 1) / n_u, (j + 1) / n_v)),
                              cena.p(P(i / n_u, (j + 1) / n_v))])
                c.drawPath(T.caminho(q, True), T.tinta_paint((150, 54, 48), 200 * k))
    return tex


COZINHA_VELA = (-0.45, 0.98, 2.3)


def _cozinha_fixa(cam):
    cena = Cena(cam, 0.0, nevoa=(30, 28, 32), alcance=30.0, luz=(0.4, 0.5, -0.7), w_tinta=2.6)
    df = comodo(cena, -2.6, 2.6, 2.7, -1.2, 4.6, parede=(150, 140, 116), papel2=(132, 122, 102), piso=(96, 88, 76), semente=31, listras=6)
    fundo = [(-2.6, 0, 4.59), (2.6, 0, 4.59), (2.6, 2.7, 4.59), (-2.6, 2.7, 4.59)]
    textura_solta(cena, fundo, tex_descasca(fundo, 33, n=4, mofo=1.0), 98.9)
    rodape(cena, -2.6, 2.6, 4.58, 4.58, plano="z", semente=3)
    L = COZINHA_VELA
    # mesa com a toalha xadrez caindo dos lados
    mesa(cena, 0.0, 2.2, w=1.8, d_=1.0)
    tampo = [(-0.95, 0.785, 1.65), (0.95, 0.785, 1.65), (0.95, 0.785, 2.75), (-0.95, 0.785, 2.75)]
    cena.face(tampo, (214, 204, 184), contorno=1.0, hach=False, z=2.2, textura=_tex_xadrez(tampo, 12, 7))
    cai = [(-0.95, 0.785, 1.64), (0.95, 0.785, 1.64), (0.97, 0.5, 1.62), (-0.97, 0.5, 1.62)]
    cena.face(cai, (214, 204, 184), contorno=1.0, hach=False, z=1.6, textura=_tex_xadrez(cai, 12, 2))
    sombra_chao(cena, -0.95, 0.95, 1.65, 2.75, 0.78, (L[0], L[1] + 0.6, L[2]), alfa=150)
    for k, (x, z, rot) in enumerate(((-0.6, 1.35, 0.1), (0.6, 1.4, -0.15), (-1.2, 2.25, 1.5), (1.2, 2.2, -1.4), (0.0, 3.05, 3.1))):
        cadeira(cena, x, z, rot=rot, semente=40 + k)
    carta(cena, 0.1, 0.79, 2.15, rot=0.3)
    for k in range(5):   # torrões de terra em volta da carta
        cena.caixa(0.3 + 0.05 * k, 0.33 + 0.05 * k, 0.79, 0.81, 2.0 + 0.04 * k, 2.03 + 0.04 * k, (70, 54, 40))
    vela3d(cena, L[0], 0.79, L[2], forca=0.95)
    quadro_parede(cena, [(-0.5, 1.45, 4.575), (0.3, 1.41, 4.575), (0.32, 2.0, 4.575), (-0.48, 2.04, 4.575)], riscado=True, semente=9)
    # fogão a lenha caiado: chapa de ferro com as bocas, a portinhola com a brasa, a chaminé até o teto e a lenha
    cena.caixa(1.25, 2.5, 0, 0.82, 3.55, 4.5, (176, 168, 150), textura_face=lambda pts: tex_parede(pts, 61, picho=0.0, umidade=0.9, rachas=2))
    chapa = [(1.25, 0.825, 3.55), (2.5, 0.825, 3.55), (2.5, 0.825, 4.5), (1.25, 0.825, 4.5)]
    cena.face(chapa, (30, 28, 30), contorno=1.2, hach=False, z=3.9)
    for xx in (1.6, 2.1):
        cena.face([(xx + 0.16 * math.cos(a), 0.83, 3.9 + 0.13 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 14, endpoint=False)],
                  (18, 16, 18), contorno=1.0, hach=False, z=3.85)
    brasa = [(1.45, 0.25, 3.545), (1.85, 0.25, 3.545), (1.85, 0.5, 3.545), (1.45, 0.5, 3.545)]
    cena.face(brasa, (30, 22, 20), contorno=1.4, hach=False, z=3.5)
    cena.face([(1.5, 0.28, 3.54), (1.8, 0.28, 3.54), (1.8, 0.33, 3.54), (1.5, 0.33, 3.54)], (250, 140, 60), contorno=0.0, hach=False,
              luz_extra=1.0, z=3.49)
    cena.luz(1.65, 0.3, 3.4, 1.6, (250, 130, 60), 0.8, chao=True, pisca=17)
    cena.caixa(2.1, 2.3, 0.82, 2.7, 4.2, 4.4, (40, 36, 34))
    for k in range(9):   # lenha empilhada do lado do fogão
        x = 0.95 + 0.11 * (k % 3) + (0.05 if k // 3 == 1 else 0)
        y = 0.06 + 0.11 * (k // 3)
        cena.face([(x + 0.055 * math.cos(a), y + 0.055 * math.sin(a), 3.6) for a in np.linspace(0, 2 * math.pi, 10, endpoint=False)],
                  (150, 116, 80), contorno=1.0, hach=False, z=3.58)
        cena.caixa(x - 0.05, x + 0.05, y - 0.05, y + 0.05, 3.6, 4.3, (96, 72, 52))
    # panelas de alumínio penduradas no varão da parede
    cena.linha([(0.6, 2.05, 4.55), (2.4, 2.05, 4.55)], 1.6, z=4.5, cor=(60, 50, 44))
    for k, (x, r, hh) in enumerate(((0.8, 0.14, 0.16), (1.15, 0.18, 0.2), (1.55, 0.12, 0.14), (1.9, 0.2, 0.12), (2.25, 0.1, 0.12))):
        y0 = 2.05 - 0.12 - hh
        cena.linha([(x, 2.05, 4.54), (x, y0 + hh + 0.04, 4.54)], 0.8, z=4.52)
        pan = [(x - r, y0, 4.5), (x + r, y0, 4.5), (x + r, y0 + hh, 4.5), (x - r, y0 + hh, 4.5)]
        cena.face(pan, (150, 150, 146), contorno=1.2, z=4.48, textura=_tex_listras(pan, 3, eixo=1, alfa=40))
        cena.face([(x + r * math.cos(a), y0 + hh + 0.025 * math.sin(a), 4.49) for a in np.linspace(0, 2 * math.pi, 12, endpoint=False)],
                  (120, 120, 118), contorno=0.8, hach=False, z=4.47)
    # filtro de barro em cima da mesinha do canto
    cena.caixa(-2.5, -1.8, 0.0, 0.9, 3.9, 4.5, (86, 66, 52), textura=tex_tabuas([(-2.5, 0, 3.9), (-1.8, 0, 3.9), (-1.8, 0.9, 3.9), (-2.5, 0.9, 3.9)], 3))
    _cilindro(cena, -2.15, 0.9, 4.2, 0.17, 0.19, 0.32, (176, 96, 64), n=14)
    _cilindro(cena, -2.15, 1.22, 4.2, 0.19, 0.17, 0.3, (168, 90, 60), n=14)
    _cilindro(cena, -2.15, 1.52, 4.2, 0.12, 0.05, 0.06, (150, 80, 54), n=12)
    cena.linha([(-2.05, 0.98, 4.02), (-2.0, 0.95, 3.98), (-2.0, 0.9, 3.98)], 1.2, z=3.97, cor=(150, 150, 146))   # a torneirinha
    # janela com o luar sobre a pia
    janela_luar(cena, -2.59, 1.2, 2.2, 1.05, 2.0, lado=-1, dir_luz=(0.75, -0.62, 0.15))
    teto_vigas(cena, -2.6, 2.6, 2.7, -1.2, 4.6, (0.5, 1.8, 3.1, 4.35), lampada=(0.0, 2.2), teia=(-2.6, 4.58), semente=37,
               prateleira=(-2.45, -0.95, 4.59, 2.05))
    return cena


def cozinha(c, t, cam=None, atores=(), extras=None, roll=0.0, escuro=0.4):
    """Cozinha da roça: mesa com toalha xadrez, as cadeiras (a do pai na cabeceira), a carta suja de terra e a vela,
    foto da família com o rosto do pai riscado, fogão a lenha com a brasa, lenha empilhada, panelas penduradas,
    filtro de barro, janela com luar; papel descascando e mofo."""
    cam = cam or CamG(x=0.55, h=1.6, F=900, hz=760, cx=W / 2, z=-0.1, pitch=10.0)
    cena = _fixa("cozinha", cam, t, _cozinha_fixa)
    for X, Z, desenha, alt in atores:
        cena.ator(X, Z, desenha, alt, rim=0.3)
    cena.escuro(escuro, [(COZINHA_VELA[0], 1.0, COZINHA_VELA[2], 3.4, 0.95), (1.65, 0.4, 3.5, 1.8, 0.7), (-1.6, 0.5, 1.8, 2.0, 0.55),
                         (COZINHA_VELA[0], 2.5, COZINHA_VELA[2], 2.6, 0.5)],
                tom=(6, 4, 6))
    if extras:
        extras(cena)
    c.save()
    c.rotate(roll, W / 2, H / 2)
    c.drawPaint(T.tinta_paint((6, 4, 6)))
    cena.desenha(c)
    c.restore()
    return cena


SALA_LAMPIAO = (-0.75, 0.95, 3.4)


def sofa_capa(cena, x0, x1, z0, z1, luz=None):
    """Sofá velho coberto com a capa de pano claro (dobras, franja caindo), almofada amassada."""
    pano = (176, 166, 144)
    cena.caixa(x0, x1, 0.0, 0.45, z0, z1, pano)
    cena.caixa(x0, x1, 0.45, 0.95, z1 - 0.22, z1, T.escurece(pano, 0.92))
    for xx in (x0, x1 - 0.18):
        cena.caixa(xx, xx + 0.18, 0.45, 0.66, z0, z1, T.escurece(pano, 0.95))
    rnd = random.Random(8)
    for k in range(7):   # dobras do pano
        x = x0 + (x1 - x0) * (k + 0.5) / 7
        cena.linha([(x + rnd.uniform(-0.05, 0.05), 0.44, z0 - 0.005), (x + rnd.uniform(-0.08, 0.08), 0.05, z0 - 0.01)], 0.7, z=z0 - 0.02)
        cena.linha([(x + rnd.uniform(-0.05, 0.05), 0.94, z1 - 0.225), (x + rnd.uniform(-0.05, 0.05), 0.5, z1 - 0.225)], 0.6, z=z1 - 0.23)
    for k in range(int((x1 - x0) / 0.05)):   # franja
        x = x0 + 0.025 + 0.05 * k
        cena.linha([(x, 0.06, z0 - 0.01), (x + 0.005, 0.0, z0 - 0.015)], 0.5, z=z0 - 0.03)
    cena.caixa(x0 + 0.3, x0 + 0.75, 0.45, 0.72, z1 - 0.35, z1 - 0.2, (120, 70, 64), deforma=torto(wob=0.03, sag=0.05, semente=4))
    if luz:
        sombra_chao(cena, x0, x1, z0, z1, 0.95, luz, alfa=140)


def tv_tubo(cena, X, Z, luz=None):
    """Televisão de tubo desligada em cima do rack: caixa de madeira, a tela abaulada escura com o reflexo da janela,
    botões e a antena de orelha de coelho."""
    cena.caixa(X - 0.4, X + 0.4, 0.0, 0.55, Z - 0.25, Z + 0.25, (76, 58, 46), textura=tex_tabuas([(X - 0.4, 0, Z - 0.25), (X + 0.4, 0, Z - 0.25),
                                                                                             (X + 0.4, 0.55, Z - 0.25), (X - 0.4, 0.55, Z - 0.25)], 2))
    cena.caixa(X - 0.34, X + 0.34, 0.55, 1.08, Z - 0.22, Z + 0.25, (96, 80, 66))
    tela = [(X - 0.28, 0.62, Z - 0.225), (X + 0.14, 0.62, Z - 0.225), (X + 0.14, 1.0, Z - 0.225), (X - 0.28, 1.0, Z - 0.225)]

    def tex(c, cena_, f):
        q = np.array([cena_.p(p) for p in tela])
        r = skia.Rect.MakeLTRB(q[:, 0].min(), q[:, 1].min(), q[:, 0].max(), q[:, 1].max())
        c.drawRoundRect(r, r.width() * 0.12, r.width() * 0.12, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
            skia.Point(r.centerX() - r.width() * 0.15, r.centerY() - r.height() * 0.2), r.width() * 0.8,
            [T.cor_skia((70, 78, 82)), T.cor_skia((30, 34, 36)), T.cor_skia((14, 16, 18))], [0.0, 0.5, 1.0])))
        c.drawRect(skia.Rect.MakeXYWH(r.left() + r.width() * 0.62, r.top() + r.height() * 0.12, r.width() * 0.12, r.height() * 0.32),
                   T.tinta_paint((150, 166, 196), 60))   # o reflexo da janela no vidro
    cena.face(tela, (24, 28, 30), contorno=1.4, hach=False, z=Z - 0.24, textura=tex)
    for k in range(3):
        y = 0.95 - 0.1 * k
        cena.face([(X + 0.22 + 0.04 * math.cos(a), y + 0.04 * math.sin(a), Z - 0.226) for a in np.linspace(0, 2 * math.pi, 10, endpoint=False)],
                  (40, 34, 30), contorno=0.6, hach=False, z=Z - 0.245)
    for l in (-1, 1):
        cena.linha([(X, 1.08, Z), (X + l * 0.3, 1.5, Z + 0.1)], 0.8, z=Z - 0.01, cor=(150, 150, 146))
    if luz:
        sombra_chao(cena, X - 0.4, X + 0.4, Z - 0.25, Z + 0.25, 1.08, luz, alfa=130)


def porta_tranca(cena, x0, x1, Z, df=None):
    """A porta da frente trancada: a tranca de madeira atravessada nos dois suportes e o ferrolho."""
    porta_frente(cena, x0, x1, Z, df=df)
    for xx in (x0 - 0.06, x1 + 0.02):
        cena.caixa(xx, xx + 0.06, 1.0, 1.16, Z - 0.12, Z - 0.02, (60, 44, 34))
    cena.caixa(x0 - 0.16, x1 + 0.16, 1.06, 1.16, Z - 0.16, Z - 0.08, (104, 80, 58),
               textura=tex_tabuas([(x0 - 0.16, 1.06, Z - 0.16), (x1 + 0.16, 1.06, Z - 0.16), (x1 + 0.16, 1.16, Z - 0.16), (x0 - 0.16, 1.16, Z - 0.16)], 1))
    cena.caixa(x1 - 0.2, x1 - 0.04, 1.6, 1.64, Z - 0.06, Z - 0.03, (110, 104, 96))   # ferrolho


def _sala_fixa(cam):
    cena = Cena(cam, 0.0, nevoa=(28, 26, 30), alcance=30.0, luz=(0.35, 0.5, -0.8), w_tinta=2.6)
    df = comodo(cena, -2.8, 2.8, 2.7, -1.2, 4.8, parede=(130, 118, 98), papel2=(116, 106, 90), semente=41, listras=12)
    fundo = [(-2.8, 0, 4.79), (2.8, 0, 4.79), (2.8, 2.7, 4.79), (-2.8, 2.7, 4.79)]
    textura_solta(cena, fundo, tex_descasca(fundo, 43, n=5), 98.9)
    lado_e = [(-2.79, 0, -1.2), (-2.79, 0, 4.8), (-2.79, 2.7, 4.8), (-2.79, 2.7, -1.2)]
    textura_solta(cena, lado_e, tex_descasca(lado_e, 44, n=3), 97.9)
    rodape(cena, -2.8, 2.8, 4.78, 4.78, plano="z", semente=5)
    rodape(cena, -2.78, -2.78, -1.2, 4.8, plano="x", semente=6)
    L = SALA_LAMPIAO
    porta_tranca(cena, -0.5, 0.45, 4.79, df=df)
    trilha_terra(cena, [(0.0, 0.01, 4.7), (0.15, 0.01, 4.0), (-0.1, 0.01, 3.3)], larg=0.22, semente=43)
    tapete(cena, 0.0, 2.6, rx=0.8, rz=0.5, semente=9)
    janela_luar(cena, 4.78, 1.45, 2.4, 1.05, 2.05, plano="z", dir_luz=(-0.25, -0.62, -0.75))
    sofa_capa(cena, -2.6, -1.1, 3.4, 4.3, luz=(L[0], L[1] + 0.25, L[2]))
    # mesinha com o lampião entre o sofá e a porta
    cena.caixa(-1.0, -0.55, 0.0, 0.7, 3.2, 3.6, (80, 60, 46))
    lampiao_mesa(cena, L[0], 0.7, L[2], forca=1.0, pisca=13)
    tv_tubo(cena, 1.95, 4.2, luz=(L[0], L[1] + 0.25, L[2]))
    for k, x in enumerate((-2.2, -1.6)):
        quadro_parede(cena, [df((x, 1.5, 4.78)), df((x + 0.4, 1.47, 4.78)), df((x + 0.42, 1.98, 4.78)), df((x + 0.02, 2.0, 4.78))], riscado=(k == 1),
                      semente=20 + k)
    santinho(cena, 0.95, 1.55, 4.78, w=0.26, h=0.36, semente=7)
    relogio_parede(cena, -0.03, 2.35, 4.78, r=0.16, plano="z")
    teto_vigas(cena, -2.8, 2.8, 2.7, -1.2, 4.8, (0.4, 1.7, 3.0, 4.25), lampada=(0.6, 1.9), teia=(2.8, 4.78), semente=47)
    return cena


def sala(c, t, cam=None, atores=(), extras=None, roll=0.0, escuro=0.42):
    """Sala: a porta da frente trancada (tranca de madeira, ferrolho, fechadura, fresta) com a trilha de terra entrando,
    sofá com capa de pano, lampião aceso na mesinha, TV de tubo desligada com a antena, relógio parado em cima da
    porta, santinho e fotos tortas, tapete de retalho, janela com luar; papel descascando e mofo."""
    cam = cam or CamG(x=0.2, h=1.35, F=940, hz=860, cx=W / 2, z=0.5, pitch=3.0)
    cena = _fixa("sala", cam, t, _sala_fixa)
    for X, Z, desenha, alt in atores:
        cena.ator(X, Z, desenha, alt, rim=0.3)
    cena.escuro(escuro, [(SALA_LAMPIAO[0], 1.1, SALA_LAMPIAO[2], 3.4, 0.95), (1.6, 0.4, 3.4, 2.2, 0.65), (0.0, 1.0, 4.6, 1.6, 0.45),
                         (SALA_LAMPIAO[0] + 0.3, 2.5, SALA_LAMPIAO[2], 2.6, 0.5)],
                tom=(6, 4, 6))
    if extras:
        extras(cena)
    c.save()
    c.rotate(roll, W / 2, H / 2)
    c.drawPaint(T.tinta_paint((6, 4, 6)))
    cena.desenha(c)
    c.restore()
    return cena


def janela_sala(c, t, figura=None, roll=0.0):
    """Janela da sala vista de dentro pra fora: a estrada de terra na neblina lá fora (o cenário inteiro, com
    paralaxe) e, por cima, a parede de dentro com o vão da janela, o caixilho em cruz, a cortina rasgada e o
    parapeito. `figura(cena)` põe alguém na estrada (uma silhueta andando aos trancos)."""
    from .paisagens import _curva, estrada_neblina
    cam = CamG(x=_curva(0) - 0.4, h=1.7, F=1300, hz=1040, cx=W / 2, z=-6.0, pitch=-1.0)
    estrada_neblina(c, t, cam=cam, extras=figura, roll=roll)
    var = T.ferve(t)
    jx0, jx1, jy0, jy1 = 150, W - 150, 360, 1340
    parede = skia.Path()
    parede.setFillType(skia.PathFillType.kEvenOdd)
    parede.addRect(skia.Rect.MakeLTRB(-50, -50, W + 50, H + 50))
    parede.addRect(skia.Rect.MakeLTRB(jx0, jy0, jx1, jy1))
    c.drawPath(parede, T.tinta_paint((58, 50, 44)))
    c.save()
    c.clipPath(parede, doAntiAlias=True)
    for k in range(9):   # listras do papel de parede, à luz da lua que entra
        x = k * W / 8
        c.drawRect(skia.Rect.MakeXYWH(x - 14, 0, 28, H), T.tinta_paint((40, 34, 30), 120))
    c.drawPath(T.hachura(parede, 0.9, 6.0, 1.0, var, 7), skia.Paint(AntiAlias=True, Color=T.cor_skia(T.TINTA, 110), Style=skia.Paint.kStroke_Style,
                                                                    StrokeWidth=1.0))
    c.drawRect(skia.Rect.MakeLTRB(jx0 - 60, jy1, jx1 + 60, jy1 + 40), T.tinta_paint((84, 66, 52)))   # parapeito
    c.restore()
    c.drawRect(skia.Rect.MakeLTRB(jx0, jy0, jx1, jy1), skia.Paint(AntiAlias=True, Color=T.cor_skia((60, 46, 36)), Style=skia.Paint.kStroke_Style,
                                                                  StrokeWidth=26))
    for pts in (np.array([((jx0 + jx1) / 2, jy0), ((jx0 + jx1) / 2, jy1)]), np.array([(jx0, (jy0 + jy1) / 2), (jx1, (jy0 + jy1) / 2)])):
        c.drawPath(T.traco_tinta(pts, 18, var, 9, amp=0.5, ponta=(0.0, 0.0)), T.tinta_paint((52, 40, 32)))
        c.drawPath(T.traco_tinta(pts, 3, var, 10, amp=0.8, ponta=(0.0, 0.0)), T.tinta_paint(T.TINTA))
    c.drawPath(T.traco_tinta(np.array([(jx0, jy0), (jx1, jy0), (jx1, jy1), (jx0, jy1)]), 4, var, 11, fechado=True, amp=1.2),
               T.tinta_paint(T.TINTA))
    for l, x in ((-1, jx0), (1, jx1)):   # cortina rasgada
        bal = 12 * math.sin(t * 1.1 + l)
        pts = np.array([(x - l * 130, jy0 - 120), (x + l * 70, jy0 - 120), (x + l * 40 + bal, jy0 + 400), (x + l * 90 + bal, jy0 + 640),
                        (x + l * 20 + bal, jy1 + 60), (x - l * 130, jy1 + 60)])
        q = T.catmull(pts, True, 6)
        c.drawPath(T.caminho(q), T.tinta_paint((70, 60, 66)))
        c.drawPath(T.traco_tinta(q, 3.2, var, 20 + l, fechado=True, amp=1.0), T.tinta_paint(T.TINTA))
        for k in range(4):
            xx = x + l * (k * 18 - 60)
            c.drawPath(T.traco_tinta(np.array([(xx, jy0 - 100), (xx + bal * 0.5, jy0 + 500), (xx + bal, jy1 + 40)]), 1.6, var, 30 + k + l * 5,
                                     amp=0.6), T.tinta_paint(T.TINTA, 150))
