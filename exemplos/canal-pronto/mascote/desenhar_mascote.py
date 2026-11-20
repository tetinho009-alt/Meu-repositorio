# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Mascote do canal de exemplo: Bubi, um axolote no estilo cápsula do kit, desenhado só por código (Skia).

Mesmas regras do molde cápsula (`kit/maquina/molde.py`): corpo de feijão, olhos grandes ovais com brilho, braços e
pernas de mangueira com ponta redonda, cor chapada com uma sombra dura no lado direito e contorno fino num tom mais
escuro da própria cor, nunca preto. O que faz dele um axolote: as três brânquias de cada lado da cabeça, a barriga
clara, o sorriso largo e o rabo de nadadeira.

Uso (com o Python do kit, que já tem o skia-python):
    python desenhar_mascote.py              -> uma PNG transparente por pose nesta pasta + rosto.png (para o ícone)

Para fazer o mascote do seu canal, peça à IA: "desenha o mascote do meu canal por código, igual ao Bubi". Ela troca
as cores em CORES e as partes que caracterizam o bicho (brânquias, rabo) e mantém o resto.
"""
import colorsys
import math
from pathlib import Path

import numpy as np
import skia

AQUI = Path(__file__).resolve().parent
W, H = 1000, 1100
CX = 500.0
TOPO_Y, BASE_Y = 190.0, 830.0
MEIO_Y, ALT_2 = (TOPO_Y + BASE_Y) / 2, (BASE_Y - TOPO_Y) / 2
LARG, LARG_DELTA, EXPOENTE = 232.0, 26.0, 2.3
EYE_Y, EYE_SEP, OLHO_RX, OLHO_RY = 352.0, 96.0, 44.0, 54.0
BOCA_Y = 468.0
CONTORNO = 7.0

CORES = dict(pele="#F59BB5", barriga="#FDD3DF", branquia="#E0517C", iris="#2A1420", bochecha="#FF7A98",
             lupa="#3D8EF0", cabo="#7A4A36")


def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _hex(rgb):
    return "#%02X%02X%02X" % tuple(int(round(max(0.0, min(1.0, v)) * 255)) for v in rgb)


def tom(cor, k):
    """Mesma cor, mais escura e um pouco mais saturada (igual ao molde): sombra e contorno saem daqui."""
    h, s, v = colorsys.rgb_to_hsv(*_rgb(cor))
    s = min(1.0, s * (1 + (1 - k) * 0.7) + (1 - k) * 0.08)
    return _hex(colorsys.hsv_to_rgb(h, s, v * k))


def tinta(c, a=255, traco=None, cap=True):
    r, g, b = (int(round(v * 255)) for v in _rgb(c))
    p = skia.Paint(AntiAlias=True, Color=skia.ColorSetARGB(a, r, g, b))
    if traco:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(traco)
        p.setStrokeJoin(skia.Paint.kRound_Join)
        p.setStrokeCap(skia.Paint.kRound_Cap if cap else skia.Paint.kButt_Cap)
    return p


def linha(c):
    return tom(c, 0.52)


# ---------------------------------------------------------------- formas


def feijao():
    p = skia.Path()
    for i in range(361):
        t = math.radians(i)
        c, s = math.cos(t), math.sin(t)
        y = MEIO_Y + ALT_2 * math.copysign(abs(s) ** (2 / EXPOENTE), s)
        meia = LARG + LARG_DELTA * (y - MEIO_Y) / ALT_2
        x = CX + meia * math.copysign(abs(c) ** (2 / EXPOENTE), c)
        p.moveTo(x, y) if i == 0 else p.lineTo(x, y)
    p.close()
    return p


def com_sombra(cv, forma, cor, desloc=38.0):
    """Cor chapada com a sombra dura no lado direito: a forma inteira no tom escuro, a mesma forma deslocada para a
    esquerda (recortada pela original) na cor base, e o contorno fino por cima."""
    cv.drawPath(forma, tinta(tom(cor, 0.82)))
    luz = skia.Path(forma)
    luz.offset(-desloc, 0)
    cv.drawPath(skia.Op(forma, luz, skia.PathOp.kIntersect_PathOp), tinta(cor))
    cv.drawPath(forma, tinta(linha(cor), traco=CONTORNO))


def tubo(cv, pts, r, cor):
    """Mangueira (braço, perna, brânquia): traço grosso com ponta redonda, contorno no tom escuro."""
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    cv.drawPath(p, tinta(linha(cor), traco=2 * r + 2 * CONTORNO))
    cv.drawPath(p, tinta(cor, traco=2 * r))


def bola(cv, x, y, r, cor):
    cv.drawCircle(x, y, r + CONTORNO / 2, tinta(linha(cor)))
    cv.drawCircle(x, y, r - CONTORNO / 2, tinta(cor))


def membro(ombro, a1, l1, a2, l2):
    """Pontos de um braço em dois segmentos; ângulos em graus a partir do eixo x (y cresce para baixo)."""
    x0, y0 = ombro
    x1, y1 = x0 + l1 * math.cos(math.radians(a1)), y0 + l1 * math.sin(math.radians(a1))
    x2, y2 = x1 + l2 * math.cos(math.radians(a2)), y1 + l2 * math.sin(math.radians(a2))
    return [(x0, y0), (x1, y1), (x2, y2)]


# ---------------------------------------------------------------- partes


def branquias(cv):
    """Três de cada lado da cabeça, em leque, com uma bolinha na ponta (a franja simplificada)."""
    cor = CORES["branquia"]
    for lado in (-1, 1):
        for k, (ang, comp) in enumerate(((-58, 120), (-28, 128), (2, 112))):
            a = math.radians(ang)
            base = (CX + lado * 170, 300 + k * 52)
            ponta = (base[0] + lado * comp * math.cos(a), base[1] + comp * math.sin(a))
            tubo(cv, [base, ponta], 22, cor)
            bola(cv, ponta[0], ponta[1], 27, cor)


def rabo(cv):
    cor = CORES["pele"]
    p = skia.Path()
    p.moveTo(640, 760)
    p.cubicTo(760, 760, 850, 720, 880, 600)
    p.cubicTo(900, 680, 860, 800, 730, 840)
    p.cubicTo(690, 852, 650, 845, 630, 830)
    p.close()
    cv.drawPath(p, tinta(tom(cor, 0.86)))
    cv.drawPath(p, tinta(linha(cor), traco=CONTORNO))
    # nadadeira: faixa clara ao longo do dorso do rabo
    f = skia.Path()
    f.moveTo(700, 770)
    f.cubicTo(790, 760, 860, 700, 878, 616)
    cv.drawPath(f, tinta(CORES["barriga"], traco=12))


def pernas(cv, pulando=False):
    cor = CORES["pele"]
    for lado in (-1, 1):
        x = CX + lado * 92
        y_pe = 960 if pulando else 1000
        tubo(cv, [(x, 800), (x + lado * (14 if pulando else 4), y_pe - 30)], 30, cor)
        pe = skia.Path()
        pe.addOval(skia.Rect(x - 52 + lado * 18, y_pe - 46, x + 52 + lado * 18, y_pe + 6))
        com_sombra(cv, pe, tom(cor, 0.92), 14)


def corpo(cv):
    f = feijao()
    com_sombra(cv, f, CORES["pele"])
    barriga = skia.Path()
    barriga.addOval(skia.Rect(CX - 165, 560, CX + 165, 860))
    barriga = skia.Op(barriga, f, skia.PathOp.kIntersect_PathOp)
    cv.drawPath(barriga, tinta(CORES["barriga"]))
    # risquinhos da barriga (dobras), no tom da própria barriga
    for k, y in enumerate((640, 690, 740)):
        meia = 70 - 8 * abs(k - 1)
        p = skia.Path()
        p.moveTo(CX - meia, y)
        p.quadTo(CX, y + 14, CX + meia, y)
        cv.drawPath(p, tinta(tom(CORES["barriga"], 0.72), traco=6))
    cv.drawPath(f, tinta(linha(CORES["pele"]), traco=CONTORNO))


def olhos(cv, olhar=(0.0, 0.0), arregalado=False, piscando=False):
    rx, ry = (OLHO_RX * 1.08, OLHO_RY * 1.12) if arregalado else (OLHO_RX, OLHO_RY)
    for lado in (-1, 1):
        ox = CX + lado * EYE_SEP
        if piscando:
            p = skia.Path()
            p.moveTo(ox - 38, EYE_Y + 4)
            p.quadTo(ox, EYE_Y + 34, ox + 38, EYE_Y + 4)
            cv.drawPath(p, tinta(linha(CORES["pele"]), traco=9))
            continue
        r = skia.Rect(ox - rx, EYE_Y - ry, ox + rx, EYE_Y + ry)
        cv.drawOval(r, tinta("#FFFFFF"))
        cv.drawOval(r, tinta(linha(CORES["pele"]), traco=6))
        px, py = ox + olhar[0] * 12, EYE_Y + 6 + olhar[1] * 12
        cv.drawOval(skia.Rect(px - 25, py - 33, px + 25, py + 33), tinta(CORES["iris"]))
        cv.drawOval(skia.Rect(px - 18, py - 24, px, py - 4), tinta("#FFFFFF"))


def sobrancelhas(cv, jeito="normal"):
    """normal, alta (surpresa) ou duvida (uma sobe, outra desce)."""
    c = linha(CORES["pele"])
    for lado in (-1, 1):
        ox = CX + lado * EYE_SEP
        sobe = {"normal": 0, "alta": 22, "duvida": 22 if lado < 0 else -4}[jeito]
        y = EYE_Y - OLHO_RY - 26 - sobe
        incl = {"normal": 6, "alta": 4, "duvida": -8 if lado < 0 else 10}[jeito]
        p = skia.Path()
        p.moveTo(ox - 30, y + incl * (1 if lado < 0 else -1) * 0.5)
        p.lineTo(ox + 30, y - incl * (1 if lado < 0 else -1) * 0.5)
        cv.drawPath(p, tinta(c, traco=11))


def bochechas(cv):
    for lado in (-1, 1):
        cv.drawOval(skia.Rect(CX + lado * 160 - 34, 432, CX + lado * 160 + 34, 470), tinta(CORES["bochecha"], 120))


def boca(cv, jeito):
    """sorriso (o sorriso largo do axolote), aberta (riso), O (surpresa) ou hum (pensando)."""
    c = linha(CORES["pele"])
    if jeito == "sorriso":
        p = skia.Path()
        p.moveTo(CX - 92, BOCA_Y - 10)
        p.cubicTo(CX - 50, BOCA_Y + 36, CX + 50, BOCA_Y + 36, CX + 92, BOCA_Y - 10)
        cv.drawPath(p, tinta(c, traco=9))
    elif jeito == "aberta":
        p = skia.Path()
        p.moveTo(CX - 70, BOCA_Y - 12)
        p.cubicTo(CX - 60, BOCA_Y + 72, CX + 60, BOCA_Y + 72, CX + 70, BOCA_Y - 12)
        p.close()
        cv.drawPath(p, tinta("#7A1F3D"))
        lingua = skia.Path()
        lingua.addOval(skia.Rect(CX - 34, BOCA_Y + 22, CX + 34, BOCA_Y + 66))
        cv.drawPath(skia.Op(lingua, p, skia.PathOp.kIntersect_PathOp), tinta("#FF8AA3"))
        cv.drawPath(p, tinta(c, traco=8))
    elif jeito == "O":
        r = skia.Rect(CX - 26, BOCA_Y - 10, CX + 26, BOCA_Y + 54)
        cv.drawOval(r, tinta("#7A1F3D"))
        cv.drawOval(r, tinta(c, traco=8))
    else:  # hum
        p = skia.Path()
        p.moveTo(CX - 40, BOCA_Y + 10)
        p.quadTo(CX + 10, BOCA_Y + 2, CX + 46, BOCA_Y - 8)
        cv.drawPath(p, tinta(c, traco=9))


def braco(cv, lado, pts):
    tubo(cv, pts, 25, CORES["pele"])
    bola(cv, pts[-1][0], pts[-1][1], 34, CORES["pele"])


def lupa(cv, mao):
    x, y = mao
    cx, cy = x - 70, y - 118
    tubo(cv, [(x - 10, y - 14), (cx + 28, cy + 46)], 13, CORES["cabo"])
    cv.drawCircle(cx, cy, 70, tinta("#DDF0FF", 150))
    cv.drawCircle(cx, cy, 70, tinta(linha(CORES["lupa"]), traco=30))
    cv.drawCircle(cx, cy, 70, tinta(CORES["lupa"], traco=18))
    brilho = skia.Path()
    brilho.addArc(skia.Rect(cx - 46, cy - 46, cx + 46, cy + 46), 200, 60)
    cv.drawPath(brilho, tinta("#FFFFFF", 220, traco=10))


# ---------------------------------------------------------------- poses

OMBRO = {-1: (CX - 214, 600.0), 1: (CX + 214, 600.0)}
BAIXO = {-1: (110, 110, 100, 120), 1: (70, 110, 80, 120)}   # braço caído junto do corpo (a1, l1, a2, l2)


def caido(lado):
    a1, l1, a2, l2 = BAIXO[lado]
    return membro(OMBRO[lado], a1, l1, a2, l2)


POSES = {
    "acenando": dict(boca="aberta", sobr="normal", olhar=(0.2, -0.2),
                     bracos={-1: caido(-1), 1: membro(OMBRO[1], -20, 110, -80, 120)}),
    "surpreso": dict(boca="O", sobr="alta", arregalado=True, olhar=(0, -0.3),
                     bracos={-1: membro(OMBRO[-1], 210, 105, 250, 115), 1: membro(OMBRO[1], -30, 105, -70, 115)}),
    "apontando": dict(boca="sorriso", sobr="normal", olhar=(0.8, -0.1),
                      bracos={-1: caido(-1), 1: membro(OMBRO[1], -18, 130, -22, 130)}),
    "lupa": dict(boca="hum", sobr="duvida", olhar=(-0.6, -0.2), lupa=True,
                 bracos={-1: membro(OMBRO[-1], 200, 105, 268, 110), 1: caido(1)}),
    "feliz": dict(boca="aberta", sobr="alta", piscando=True, pulando=True,
                  bracos={-1: membro(OMBRO[-1], 225, 110, 260, 115), 1: membro(OMBRO[1], -45, 110, -80, 115)}),
    "rosto": dict(boca="sorriso", sobr="normal", olhar=(0, 0), bracos={}, sem_rabo=True),
}


def desenhar(cv, pose):
    p = POSES[pose]
    if not p.get("sem_rabo"):
        rabo(cv)
    branquias(cv)
    pernas(cv, p.get("pulando", False))
    corpo(cv)
    bochechas(cv)
    olhos(cv, p.get("olhar", (0, 0)), p.get("arregalado", False), p.get("piscando", False))
    sobrancelhas(cv, p.get("sobr", "normal"))
    boca(cv, p["boca"])
    for lado, pts in p["bracos"].items():
        braco(cv, lado, pts)
    if p.get("lupa"):
        lupa(cv, p["bracos"][-1][-1])


def salvar(pose, recorte=None, margem=16):
    s = skia.Surface(W, H)
    cv = s.getCanvas()
    cv.clear(skia.ColorTRANSPARENT)
    desenhar(cv, pose)
    a = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType)
    if recorte:
        a = a[recorte[0]:recorte[1]]
    ys, xs = np.nonzero(a[..., 3] > 8)
    # Busto (recorte): a base fica cortada reta, sem margem, para o gerador encostar a arte no pé do quadro.
    y0, y1 = max(0, ys.min() - margem), (a.shape[0] if recorte else min(a.shape[0], ys.max() + margem + 1))
    x0, x1 = max(0, xs.min() - margem), min(a.shape[1], xs.max() + margem + 1)
    a = np.ascontiguousarray(a[y0:y1, x0:x1])
    img = skia.Image.fromarray(a, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType)
    destino = AQUI / f"{pose}.png"
    img.save(str(destino), skia.kPNG)
    print(f"{destino.name}  {a.shape[1]}x{a.shape[0]}")


if __name__ == "__main__":
    for nome in POSES:
        if nome != "rosto":
            salvar(nome)
    # Busto para o ícone e a foto de perfil: cabeça, brânquias e barriga, sem braços nem pernas.
    salvar("rosto", recorte=(150, 690))
