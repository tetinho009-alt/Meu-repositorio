# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Mão direita de luva segurando a lanterna, vista por trás (POV). A lanterna aponta para a frente: a lente não aparece,
só o aro de trás, com a luz vazando pela borda. Couro e metal com degradê; volume do dorso, nós, polegar e costuras."""
import math

import numpy as np
import skia

import motor as M
from motor import W, H


def _lin(p0, p1, cores, pos=None):
    return skia.GradientShader.MakeLinear([tuple(p0), tuple(p1)], [M.cor(c) for c in cores], pos)


def mao_lanterna(cv, bob, alvo_luz, brilho_fogo):
    dx, dy = 14 * math.sin(bob), 20 * abs(math.cos(bob))
    tras = np.array([W * 0.90 + dx, H * 1.07 + dy])
    frente = np.array([W * 0.705 + dx * 0.6, H * 0.785 + dy * 0.6])
    d = (frente - tras) / np.linalg.norm(frente - tras)
    nrm = np.array([-d[1], d[0]])
    r_tras, r_frente = 104.0, 62.0

    def pt(u, v):
        """u: 0 atrás -> 1 frente; v em múltiplos do raio local (-1 lado esquerdo, +1 lado direito)."""
        r = r_tras + (r_frente - r_tras) * u
        return tras + (frente - tras) * u + nrm * v * r

    def P(*pts):
        return M.caminho([tuple(p) for p in pts])

    # facho para a frente (aditivo)
    facho = skia.Paint(AntiAlias=True, Color=M.cor((255, 238, 205), 42),
                       MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 80))
    facho.setBlendMode(skia.BlendMode.kPlus)
    ax, ay = alvo_luz
    cv.drawPath(P(pt(1.02, -1.1), pt(1.02, 1.1), (ax + 380, ay + 80), (ax - 380, ay - 80)), facho)
    # corpo de alumínio (cônico pela perspectiva), com recartilhado
    corpo = P(pt(0, -1), pt(0, 1), pt(0.97, 1), pt(0.97, -1))
    cv.drawPath(corpo, skia.Paint(AntiAlias=True, Shader=_lin(pt(0.5, -1), pt(0.5, 1),
                [(10, 10, 12), (34, 35, 40), (128, 132, 142), (58, 60, 66), (14, 14, 16)], [0, 0.3, 0.58, 0.76, 1])))
    for k in range(30):
        u = 0.62 + k * 0.009
        cv.drawLine(*pt(u, -0.92), *pt(u, 0.92), M.tinta((8, 8, 10), 110, traco=2.2))
    # cabeça: cone que alarga para a frente (a lente está do outro lado); só um fio de luz vaza na borda
    cab = P(pt(0.82, -1.0), pt(0.82, 1.0), pt(1.0, 1.42), pt(1.0, -1.42))
    cv.drawPath(cab, skia.Paint(AntiAlias=True, Shader=_lin(pt(0.9, -1.4), pt(0.9, 1.4),
                [(12, 12, 14), (46, 47, 52), (150, 154, 164), (60, 62, 68), (14, 14, 16)], [0, 0.3, 0.6, 0.78, 1])))
    cv.drawLine(*pt(0.82, -1.0), *pt(0.82, 1.0), M.tinta((8, 8, 10), traco=4))
    vaza = skia.Paint(AntiAlias=True, Color=M.cor((255, 236, 196), 210), StrokeWidth=7, Style=skia.Paint.kStroke_Style,
                      MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 6))
    vaza.setBlendMode(skia.BlendMode.kPlus)
    cv.drawLine(*pt(1.0, -1.42), *pt(1.0, 1.42), vaza)
    halo = skia.Paint(AntiAlias=True, Color=M.cor((255, 230, 180), 90),
                      MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 30))
    halo.setBlendMode(skia.BlendMode.kPlus)
    cv.drawPath(P(pt(1.0, -1.6), pt(1.0, 1.6), pt(1.12, 1.9), pt(1.12, -1.9)), halo)
    # manga da jaqueta (cobre o fundo da lanterna), com dobras e punho de malha
    manga = P(pt(-0.35, -2.2), pt(-0.35, 2.4), pt(0.20, 2.1), pt(0.28, -1.5))
    cv.drawPath(manga, skia.Paint(AntiAlias=True, Shader=_lin(pt(0, -2), pt(0, 2.2),
                [(10, 11, 9), (30, 34, 27), (22, 24, 19), (8, 9, 7)], [0, 0.42, 0.75, 1])))
    for u0, v0, u1, v1 in ((-0.1, -1.4, 0.12, -0.5), (0.0, 0.6, 0.16, 1.6), (-0.2, 0.0, 0.05, 0.8)):
        cv.drawLine(*pt(u0, v0), *pt(u1, v1), M.tinta((12, 13, 10), 150, traco=8))
    for k in range(9):
        a, b = pt(0.20 + 0.008 * k, 2.1 - 0.4 * k), pt(0.235 + 0.008 * k, 2.0 - 0.4 * k)
        cv.drawLine(*a, *b, M.tinta((26, 28, 22), traco=5))
    # dedos: as pontas aparecem curvadas no lado esquerdo do corpo (por baixo)
    for k in range(4):
        u = 0.40 + 0.085 * k
        base, ponta = pt(u, -0.55), pt(u + 0.02, -1.18)
        cv.drawLine(*base, *ponta, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=40,
                                               StrokeCap=skia.Paint.kRound_Cap,
                                               Shader=_lin(pt(u, -0.4), pt(u, -1.3), [(46, 36, 30), (18, 14, 12)])))
    # dorso da mão (couro), arredondado, cobrindo o corpo por cima e à direita
    dorso = skia.Path()
    a0, a1, a2, a3 = pt(0.26, -0.9), pt(0.30, 1.75), pt(0.72, 1.2), pt(0.74, -0.7)
    dorso.moveTo(*a0)
    dorso.quadTo(*pt(0.22, 0.5), *a1)
    dorso.quadTo(*pt(0.55, 1.9), *a2)
    dorso.quadTo(*pt(0.80, 0.2), *a3)
    dorso.quadTo(*pt(0.5, -1.15), *a0)
    dorso.close()
    cv.drawPath(dorso, skia.Paint(AntiAlias=True, Shader=_lin(pt(0.3, 1.6), pt(0.7, -0.8),
                [(14, 11, 9), (34, 26, 21), (58, 45, 35), (30, 23, 18)], [0, 0.4, 0.75, 1])))
    # nós dos dedos (quatro calombos na borda da frente) e costuras do dorso
    for k in range(4):
        v = -0.45 + 0.52 * k
        no = pt(0.715 - 0.02 * abs(k - 1.5), v)
        cv.drawCircle(*no, 19, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
            (no[0] - 8, no[1] - 10), 34, [M.cor((84, 66, 52)), M.cor((42, 32, 25)), M.cor((22, 17, 14))], [0, 0.5, 1])))
        cost = skia.Paint(AntiAlias=True, Color=M.cor((120, 96, 72), 90), Style=skia.Paint.kStroke_Style,
                          StrokeWidth=2.6, PathEffect=skia.DashPathEffect.Make([10, 8], 0))
        if k < 3:
            cv.drawLine(*pt(0.34, v * 0.8 + 0.25), *pt(0.66, v + 0.25), cost)
    # polegar: por cima, ao longo da lanterna, do lado esquerdo
    pol0, pol1 = pt(0.40, -0.6), pt(0.80, -0.55)
    cv.drawLine(*pol0, *pol1, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=42,
                                         StrokeCap=skia.Paint.kRound_Cap,
                                         Shader=_lin(pt(0.6, -1.0), pt(0.6, -0.1), [(18, 14, 11), (56, 43, 33), (26, 20, 16)])))
    unha = pt(0.84, -0.55)
    cv.drawCircle(*unha, 14, M.tinta((80, 62, 48), 120, borrao=5))
    # luz de borda do fogo (laranja) no lado esquerdo e reflexo da luz no aro
    borda = skia.Paint(AntiAlias=True, Color=M.cor((255, 128, 48), int(60 + 70 * brilho_fogo)),
                       MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 9), StrokeWidth=6,
                       Style=skia.Paint.kStroke_Style)
    borda.setBlendMode(skia.BlendMode.kPlus)
    cv.drawLine(*pt(0.42, -0.95), *pt(0.82, -0.9), borda)
    cv.drawLine(*pt(0.05, -1.0), *pt(0.95, -1.0), borda)
