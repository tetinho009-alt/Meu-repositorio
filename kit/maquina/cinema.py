# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Camada de cinema: câmera 2D (enquadramento, zoom, foco), luz no personagem e acabamento de imagem
(correção de cor, vinheta, grão). É o que dá volume ao boneco chapado e cara de produção ao quadro."""
import math
from contextlib import contextmanager

import numpy as np
import skia

from .desenho import H, W, cheio, cor, degrade, radial


class Camera:
    """Enquadra um mundo do tamanho da tela: centro (x, y), zoom e leve inclinação."""

    def __init__(self, x=W / 2, y=H / 2, zoom=1.0, rot=0.0):
        self.x, self.y, self.zoom, self.rot = x, y, zoom, rot

    @contextmanager
    def em(self, c):
        c.save()
        c.translate(W / 2, H / 2)
        c.rotate(self.rot)
        c.scale(self.zoom, self.zoom)
        c.translate(-self.x, -self.y)
        try:
            yield
        finally:
            c.restore()

    def mistura(self, outra, k):
        return Camera(*(a + (b - a) * k for a, b in ((self.x, outra.x), (self.y, outra.y),
                                                     (self.zoom, outra.zoom), (self.rot, outra.rot))))


@contextmanager
def foco(c, raio):
    """Tudo que for desenhado dentro sai desfocado (profundidade de campo: close com o fundo borrado)."""
    if raio <= 0.2:
        yield
        return
    c.saveLayer(None, skia.Paint(ImageFilter=skia.ImageFilters.Blur(raio, raio)))
    try:
        yield
    finally:
        c.restore()


# ---------------------------------------------------------------- acabamento

def vinheta(c, forca=0.8, cx=W / 2, cy=H * 0.5):
    c.drawRect(skia.Rect.MakeWH(W, H), radial(cx, cy, H * 0.66, [((0, 0, 0), 0), ((0, 0, 0), 0), ((0, 0, 0), 255 * forca)],
                                              [0.0, 0.5, 1.0]))


_GRAO = []


def _prepara_grao():
    rnd = np.random.default_rng(7)
    for _ in range(8):
        g = rnd.integers(0, 255, (H // 2, W // 2), dtype=np.uint8)
        rgba = np.dstack([g, g, g, np.full_like(g, 255)])
        _GRAO.append(skia.Image.fromarray(np.ascontiguousarray(rgba), colorType=skia.kRGBA_8888_ColorType))


def grao(c, t, forca=0.08, fps=30):
    """Grão de filme que muda a cada quadro (texturas prontas: barato na GPU e na CPU)."""
    if not _GRAO:
        _prepara_grao()
    p = skia.Paint(Alphaf=forca)
    p.setBlendMode(skia.BlendMode.kOverlay)
    c.drawImageRect(_GRAO[int(t * fps) % len(_GRAO)], skia.Rect.MakeWH(W, H), skia.SamplingOptions(), p)


def correcao(c, sombra=(20, 26, 60), forca=0.25):
    """Puxa as sombras para uma cor (azul-noite por padrão) sem sujar as luzes."""
    p = cheio(sombra, 255 * forca)
    p.setBlendMode(skia.BlendMode.kScreen)
    c.drawRect(skia.Rect.MakeWH(W, H), p)


def escuro(c, luzes, nivel=0.86, tom=(2, 2, 6)):
    """Apaga a cena e só deixa ver onde há luz. Cada luz é (x, y, alcance, força) em coordenadas do desenho."""
    c.saveLayer(None, None)
    c.drawRect(skia.Rect.MakeLTRB(-3000, -3000, 4000, 5000), cheio(tom, 255 * nivel))
    for x, y, r, f in luzes:
        p = radial(x, y, r, [((0, 0, 0), 255 * f), ((0, 0, 0), 160 * f), ((0, 0, 0), 0)], [0.0, 0.35, 1.0])
        p.setBlendMode(skia.BlendMode.kDstOut)
        c.drawCircle(x, y, r, p)
    c.restore()


def sombra_contato(c, x, chao_y, larg, forca=1.0):
    c.drawOval(skia.Rect.MakeLTRB(x - larg / 2, chao_y - larg * 0.05, x + larg / 2, chao_y + larg * 0.08),
               cheio((0, 0, 0), 200 * forca, blur=larg * 0.06))


# ---------------------------------------------------------------- luz no personagem

_APOIO = {}


def iluminado(c, desenha, caixa, pe, chave=((255, 210, 150), (-1.0, -0.4)), aro=None, sombra=0.75, escuro_lado=0.7,
              exposicao=0.8, projeta=True):
    """Desenha um personagem chapado e aplica a luz da cena como se ele tivesse volume.

    `desenha(canvas)` pinta o personagem em coordenadas do mundo; `caixa` (Rect do mundo) envolve ele; `pe` é o
    ponto do mundo onde ele toca o chão. `chave` = (cor, direção de onde vem a luz principal); `aro` = (cor,
    direção, força) da luz secundária que acende a borda (só do lado da fonte: regra de luz coerente).
    """
    m = c.getTotalMatrix()
    sup = c.getSurface()
    if id(sup) not in _APOIO:  # superfície de apoio reaproveitada entre quadros (GPU ou CPU, igual à principal)
        _APOIO[id(sup)] = sup.makeSurface(sup.width(), sup.height())
    tela = _APOIO[id(sup)]
    r = r_tela = m.mapRect(caixa)
    # Só a região do personagem (com folga para o aro e o desfoque): na CPU isso é a diferença entre segundos e
    # milissegundos por quadro.
    folga = r.width() * 0.12 + 24
    ir = r.makeOutset(folga, folga).roundOut()
    if not ir.intersect(skia.IRect.MakeWH(tela.width(), tela.height())):
        return r_tela
    oc = tela.getCanvas()
    oc.save()
    oc.resetMatrix()
    oc.clipRect(skia.Rect.Make(ir))
    oc.clear(skia.Color(0, 0, 0, 0))
    oc.setMatrix(m)
    desenha(oc)
    oc.restore()
    img = tela.makeImageSnapshot(ir)
    ox, oy = float(ir.left()), float(ir.top())
    fx, fy = m.mapXY(*pe)
    escala = r.height() / 1000.0
    crgb, (kx, _ky) = chave
    c.save()
    c.resetMatrix()
    c.translate(ox, oy)            # a imagem recortada é desenhada no lugar dela; r e o pé passam para esse sistema
    r = r.makeOffset(-ox, -oy)
    fx, fy = fx - ox, fy - oy
    limite = skia.Rect.MakeWH(img.width(), img.height()).makeOutset(folga, folga)
    if projeta:  # sombra projetada no chão, para o lado oposto à luz principal
        proj = skia.Matrix()
        proj.setTranslate(fx, fy)
        proj.preSkew(-kx * 1.6, 0)
        proj.preScale(1.0, -0.2)
        proj.preTranslate(-fx, -fy)
        c.save()
        c.concat(proj)
        c.drawImage(img, 0, 0, skia.SamplingOptions(), skia.Paint(
            ColorFilter=skia.ColorFilters.Blend(cor((0, 0, 0), 255 * sombra * 0.6), skia.BlendMode.kSrcIn),
            ImageFilter=skia.ImageFilters.Blur(8 * escala + 2, 8 * escala + 2)))
        c.restore()
        c.drawOval(skia.Rect.MakeLTRB(fx - r.width() * 0.42, fy - r.height() * 0.015, fx + r.width() * 0.42,
                                      fy + r.height() * 0.03), cheio((0, 0, 0), 200 * sombra, blur=max(0.5, r.height() * 0.015)))
    # corpo + sombreado pelo lado da luz + borda acesa, tudo preso dentro da silhueta
    c.saveLayer(limite, None)
    c.drawImage(img, 0, 0)
    x_luz = r.left() if kx < 0 else r.right()
    x_sombra = r.right() if kx < 0 else r.left()
    p = degrade((x_luz, 0), (x_sombra, 0), [(crgb, 60), (crgb, 0), ((4, 4, 10), 150 * escuro_lado), ((4, 4, 10), 235 * escuro_lado)],
                [0.0, 0.3, 0.65, 1.0])
    p.setBlendMode(skia.BlendMode.kSrcATop)
    c.drawRect(r, p)
    p = degrade((0, r.bottom()), (0, r.top()), [((4, 4, 10), 160), ((4, 4, 10), 0)], [0.0, 0.5])
    p.setBlendMode(skia.BlendMode.kSrcATop)
    c.drawRect(r, p)
    p = cheio((4, 4, 10), 255 * (1 - exposicao))
    p.setBlendMode(skia.BlendMode.kSrcATop)
    c.drawRect(r, p)
    if aro:
        argb, (ax, ay), forca = aro
        for desloc, alfa, borra in ((r.width() * 0.012, 230, 1.2), (r.width() * 0.07, 70, 8 * escala + 3)):
            c.saveLayer(limite, skia.Paint(BlendMode=skia.BlendMode.kSrcATop, ImageFilter=skia.ImageFilters.Blur(borra, borra)))
            c.drawImage(img, 0, 0, skia.SamplingOptions(),
                        skia.Paint(ColorFilter=skia.ColorFilters.Blend(cor(argb, alfa * forca), skia.BlendMode.kSrcIn)))
            c.drawImage(img, -ax * desloc, -ay * desloc, skia.SamplingOptions(), skia.Paint(BlendMode=skia.BlendMode.kDstOut))
            c.restore()
    c.restore()
    c.restore()
    return r_tela


def boneco_iluminado(c, boneco, x, pe, alt, pose, chave=((190, 200, 255), (1.0, -0.6)), aro=None, exposicao=0.8,
                     escuro_lado=0.65, projeta=False, extra=None):
    """Atalho: desenha `boneco` com `iluminado` (o padrão de qualidade do estúdio para personagem em cena)."""
    def desenha(oc):
        boneco.desenhar(oc, x, pe, alt, pose)
        if extra:
            extra(oc)
    return iluminado(c, desenha, boneco.caixa(x, pe, alt), (x, pe), chave=chave, aro=aro, exposicao=exposicao,
                     escuro_lado=escuro_lado, projeta=projeta)


def chicote(c, t, cortes, desenha, dur=0.18):
    """Chicote de câmera nos cortes: o quadro entra borrado na horizontal e deslizando nos primeiros `dur` s."""
    u = min((t - tc for tc in cortes if 0 <= t - tc < dur), default=None)
    if u is None:
        desenha(c)
        return
    k = ease_corte(u / dur)
    c.saveLayer(None, skia.Paint(ImageFilter=skia.ImageFilters.Blur(80 * (1 - k) + 0.1, 0.1)))
    c.translate(-260 * (1 - k), 0)
    desenha(c)
    c.restore()


def ease_corte(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def lampada(c, x, y, r, rgb=(255, 214, 150), forca=1.0, t=0.0):
    """Ponto de luz com halo (poste, janela, abajur)."""
    pisca = 0.92 + 0.08 * math.sin(t * 37 + x)
    c.drawCircle(x, y, r * 6, cheio(rgb, 40 * forca * pisca, blur=r * 3))
    c.drawCircle(x, y, r, cheio(rgb, 255 * forca * pisca))
