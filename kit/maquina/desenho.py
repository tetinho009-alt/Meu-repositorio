# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Utilitários de desenho comuns: cores, tintas Skia, fontes da configuração, curvas de tempo e texto."""
import math

import skia

from config import CFG, fonte_arquivo

W = int(CFG["render"]["largura"])
H = int(CFG["render"]["altura"])
FPS = int(CFG["render"]["fps"])
ZS = CFG["zona_segura"]
CX_SEGURO = (ZS["x0"] + ZS["x1"]) / 2          # centro horizontal da zona segura (fora dos botões laterais)
LARG_SEGURA = ZS["x1"] - ZS["x0"]


def cor(rgb, a=255):
    return skia.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]), int(max(0, min(255, a))))


def mix(a, b, k):
    return tuple(a[i] + (b[i] - a[i]) * k for i in range(3))


def cheio(rgb, a=255, blur=0.0):
    p = skia.Paint(AntiAlias=True, Color=cor(rgb, a))
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def traco(rgb, w, a=255, blur=0.0):
    p = cheio(rgb, a, blur)
    p.setStyle(skia.Paint.kStroke_Style)
    p.setStrokeWidth(w)
    p.setStrokeCap(skia.Paint.kRound_Cap)
    p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def _cores(cores):
    out = []
    for c in cores:
        out.append(cor(*c) if isinstance(c[0], (tuple, list)) else cor(c))
    return out


def degrade(p0, p1, cores, pos=None):
    """Degradê linear; cada cor é (r, g, b) ou ((r, g, b), alfa)."""
    return skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear(
        [skia.Point(*p0), skia.Point(*p1)], _cores(cores), pos))


def radial(x, y, r, cores, pos=None):
    return skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(skia.Point(x, y), r, _cores(cores), pos))


_FONTES = {}


def fonte(papel, tam):
    """Fonte por papel da configuração: titulo, legenda, texto ou mono."""
    k = (papel, int(tam))
    if k not in _FONTES:
        _FONTES[k] = skia.Font(skia.Typeface.MakeFromFile(str(fonte_arquivo(papel))), int(tam))
    return _FONTES[k]


def ease(x):
    """Saída suave (desacelera no fim)."""
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def suave(x):
    """Entrada e saída suaves."""
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, k):
    return a + (b - a) * k


def janela(t, t0, t1, entra=0.3, sai=0.3):
    """0..1: aparece em `entra` s a partir de t0 e some em `sai` s até t1."""
    if t < t0 or t > t1:
        return 0.0
    return ease((t - t0) / max(entra, 1e-6)) * (1 - ease((t - (t1 - sai)) / max(sai, 1e-6)))


def texto_c(c, s, x, y, f, rgb=(255, 255, 255), a=255, contorno=0):
    w = f.measureText(s)
    if contorno:
        c.drawString(s, x - w / 2, y, f, traco((0, 0, 0), contorno, a))
    c.drawString(s, x - w / 2, y, f, cheio(rgb, a))


def texto_espacado(c, s, cx, y, f, rgb, a=255, espaco=0.0, blur=0.0):
    """Texto centralizado com espaço extra entre letras (o Skia não tem letter-spacing)."""
    larg = largura_espacada(s, f, espaco)
    x = cx - larg / 2
    p = cheio(rgb, a, blur=blur)
    for ch in s:
        c.drawString(ch, x, y, f, p)
        x += f.measureText(ch) + espaco


def largura_espacada(s, f, espaco=0.0):
    return sum(f.measureText(ch) for ch in s) + espaco * max(0, len(s) - 1)


def caber(papel, texto, tam, larg, minimo=20, espaco=0.0):
    """Maior fonte (até `tam`) em que `texto` cabe em `larg` px."""
    while tam > minimo:
        f = fonte(papel, tam)
        if largura_espacada(texto, f, espaco) <= larg:
            return f
        tam -= 2
    return fonte(papel, minimo)


def quebrar(texto, f, larg):
    """Quebra em linhas que cabem em `larg` px."""
    linhas, atual = [], ""
    for p in texto.split():
        teste = (atual + " " + p).strip()
        if atual and f.measureText(teste) > larg:
            linhas.append(atual)
            atual = p
        else:
            atual = teste
    if atual:
        linhas.append(atual)
    return linhas


def tremida(t, forca, freq=37.0):
    return math.sin(t * freq) * forca, math.cos(t * freq * 1.3) * forca
