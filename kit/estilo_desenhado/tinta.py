# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Motor do recorte de papel colorido: cada forma vira uma peça de papel com a borda cortada à mão (tesoura, rasgo,
picote ou estilete, conforme o estilo), a fibra do papel assada na peça, um fio claro onde o papel foi cortado e a
sombra projetada dura, deslocada, da peça sobre o que está atrás. Também a caixa de papéis do canal (`estilo.json`)
e o acabamento do quadro (fibra leve, vinheta fria, grão quase nenhum).

Papel não ferve: o corte é o mesmo em todo quadro (a peça é recortada uma vez e guardada em cache). O que dá a cara
de animação de recorte é o stop motion de 12 poses por segundo e o leve "recolocar" de cada peça a cada pose
(`recoloca`). A API é a do motor de antes (forma, linha, mancha, Desenho, Cache, quadro, NOITE), então cenários,
bichos e interface continuam chamando as mesmas funções.

Convenções: pontos são np.ndarray (N, 2) em unidades do mundo do desenho; `var` é mantido por compatibilidade (o
papel não usa); `semente` separa uma peça da outra.
"""
import colorsys
import math
import random
import zlib

import numpy as np
import skia

# ---------------------------------------------------------------- caixa de papéis (do estilo do canal)

from .estilo import carregar as _carregar  # noqa: E402

ESTILO = _carregar()
_P, _A, _G = ESTILO["paleta"], ESTILO["acabamento"], ESTILO["gradacao"]
_R = ESTILO.get("recorte", {})
TINTA = tuple(_P["tinta"])        # o papel escuro (o "preto" do recorte)
PAPEL = tuple(_P["papel"])        # o papel claro das etiquetas
PUXA = tuple(_P["puxa"])          # tom da noite
APOIO = tuple(_P["apoio"])        # o papel mais escuro da caixa (mato, parede do fundo)
SOMBRA = tuple(_P["sombra"])      # cor da sombra projetada
DESTAQUE = tuple(_P["destaque"])
PAPEIS = [tuple(p) for p in _P.get("papeis", [APOIO, DESTAQUE])]
# corte: quanto a borda foge da linha e o tamanho de cada trecho reto (unidades de uma peça de 1000)
BORDA, PASSO, CORTE = float(_R.get("borda", 1.5)), float(_R.get("passo", 13.0)), _R.get("tipo", "tesoura")
# sombra projetada: deslocamento em px de uma peça de 1000 px de altura e a força
SOMBRA_DX, SOMBRA_DY, SOMBRA_ALFA = float(_R.get("sombra_dx", 5.0)), float(_R.get("sombra_dy", 7.0)), float(_R.get("sombra_alfa", 0.5))
FIBRA = float(_A.get("fibras", 0.8))
SEDA = float(_A.get("seda", 0.55))        # quanto as camadas de neblina (papel de seda) deixam passar
# compatibilidade com quem lia o traço de nanquim
K_LARG, K_FERVE, PENA, K_HACH, ANG_HACH, ALFA_TRACO = 1.0, 0.0, 1.0, 1.0, 0.0, 255
ACABAMENTO = dict(papel=_A["papel"], vinheta=_A["vinheta"], grao=_A["grao"], tom=tuple(_G.get("tom", (1, 1, 1))),
                  saturacao=_G.get("saturacao", 1.0))
# plano aberto noturno: um pouco mais de vinheta e o quadro puxado pro frio
NOITE = dict(ACABAMENTO, vinheta=min(1.0, _A["vinheta"] + 0.12), tom=(0.94, 0.97, 1.05))
FERVE_HZ = 12.0
DESENHOS = 1


def rgb(cor):
    if isinstance(cor, str):
        cor = cor.lstrip("#")
        return tuple(int(cor[k:k + 2], 16) for k in (0, 2, 4))
    return tuple(int(v) for v in cor[:3])


def mistura(a, b, k):
    return tuple(int(round(a[i] + (b[i] - a[i]) * k)) for i in range(3))


def escurece(cor, k):
    return tuple(int(v * k) for v in cor)


def _hls(c):
    return colorsys.rgb_to_hls(*(v / 255 for v in rgb(c)))


def _de_hls(h, l, s):
    return tuple(int(round(v * 255)) for v in colorsys.hls_to_rgb(h % 1.0, max(0, min(1, l)), max(0, min(1, s))))


def _papel_mais_perto(h):
    """O papel da caixa de matiz mais perto de h (0..1)."""
    def dist(p):
        hp = _hls(p)[0]
        d = abs(hp - h)
        return min(d, 1 - d)
    return min(PAPEIS, key=dist)


def papel_cor(cor, sat=0.42, puxa=PUXA, k_puxa=0.24, luz=(0.10, 0.80), matiz=True):
    """Cor do molde -> papel colorido: mais saturada que o original, brilho comprimido em `luz` e o matiz puxado um
    pouco para o papel da caixa mais próximo (as roupas conversam com o cenário). `sat` 0,42 é o normal; menos que
    isso é papel mais fechado (cabelo). `matiz=False`: não puxa o matiz (cabelo e olho ficam da cor de gente)."""
    h, l, s = _hls(cor)
    l = luz[0] + l * (luz[1] - luz[0])
    s = min(0.92, s * max(0.5, sat / 0.42) * 1.15 + (0.06 if s > 0.05 else 0.0))
    if s > 0.15 and matiz:
        hp = _hls(_papel_mais_perto(h))[0]
        d = (hp - h + 0.5) % 1.0 - 0.5
        h = h + d * 0.3
    return _de_hls(h, l, s)


gotica = papel_cor   # nome antigo


def pele_papel(cor):
    """Pele: o tom de verdade do personagem, um pouco mais vivo (papel colorido de pele, sem puxar pra sépia)."""
    h, l, s = _hls(cor)
    return _de_hls(h, min(0.86, l * 1.02), min(0.75, s * 1.08))


pele_gotica = pele_papel


_CEN = ESTILO.get("cenario", {})
K_CENA = float(_CEN.get("puxa", 0.85))   # quanto as cores do cenário viram papel da caixa
TORTO = float(_CEN.get("torto", 0.5))     # quanto a arquitetura entorta (0 reta, 1 casa torta de papel dobrado)
MOLDURA = _CEN.get("moldura", "mato")     # primeiro plano do plano aberto: mato | nenhuma
if MOLDURA == "galho":
    MOLDURA = "mato"
LUA_LADO = int(_CEN.get("lua_lado", 1))
LUA_TAM = float(_CEN.get("lua_tam", 1.0))
CORVOS = False


def cenario(cor):
    """Cor de cenário -> papel da caixa do canal, mantendo o claro e o escuro do original. Cor viva vai pro papel de
    matiz mais perto; cor apagada (parede, chão, móvel) ganha um papel da caixa sorteado pela própria cor, então cada
    coisa do cenário sai num papel diferente, como numa colagem, e a mesma coisa sai sempre igual."""
    r, g, b = rgb(cor)
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    if s >= 0.3:
        alvo = _papel_mais_perto(h)
    else:
        alvo = PAPEIS[zlib.crc32(bytes((r, g, b))) % len(PAPEIS)]
    ha, la, sa = _hls(alvo)
    lum = (0.3 * r + 0.59 * g + 0.11 * b) / 255
    l2 = 0.05 + lum * 0.8
    s2 = sa * (0.5 + 0.4 * min(1.0, l2 / 0.42))
    novo = _de_hls(ha, l2, s2)
    return mistura((r, g, b), novo, K_CENA)


def _sem(*a):
    """Semente estável entre execuções (o hash() de str muda a cada processo)."""
    return zlib.crc32(repr(a).encode())


def cor_skia(c, a=255):
    return skia.Color(int(c[0]), int(c[1]), int(c[2]), int(max(0, min(255, a))))


def tinta_paint(cor=TINTA, a=255):
    return skia.Paint(AntiAlias=True, Color=cor_skia(cor, a))


def ferve(t):
    """O papel não ferve: sempre o mesmo corte (índice 0). Mantido pela API."""
    return 0


def passo_stop(t, qps=12.0):
    return int(math.floor((t or 0.0) * qps + 1e-6))


def recoloca(t, chave, amp=0.6, giro=0.35):
    """O tremidinho de quem recoloca a peça de papel a cada pose do stop motion: (dx, dy, graus), igual dentro da
    mesma pose (12 por segundo) e diferente na seguinte."""
    if t is None:
        return 0.0, 0.0, 0.0
    rnd = random.Random(_sem(chave, passo_stop(t)))
    return rnd.uniform(-amp, amp), rnd.uniform(-amp, amp), rnd.uniform(-giro, giro)


# ---------------------------------------------------------------- curvas

def catmull(pts, fechado=True, n=10):
    """Curva suave (Catmull-Rom) passando pelos pontos de controle."""
    p = np.asarray(pts, dtype=float)
    if len(p) < 3:
        return p
    if fechado:
        ext = np.vstack([p[-1:], p, p[:2]])
    else:
        ext = np.vstack([2 * p[0] - p[1], p, 2 * p[-1] - p[-2]])
    segs = len(ext) - 3
    t = np.linspace(0, 1, n, endpoint=False)[:, None]
    out = []
    for i in range(segs):
        p0, p1, p2, p3 = ext[i], ext[i + 1], ext[i + 2], ext[i + 3]
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t ** 2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out = np.vstack(out)
    if not fechado:
        out = np.vstack([out, p[-1:]])
    return out


def quina(pts, fechado=True, n=6):
    """Polígono com quinas vivas (segmentos retos levemente amostrados): pra coisas angulosas."""
    p = np.asarray(pts, dtype=float)
    if fechado:
        p = np.vstack([p, p[:1]])
    t = np.linspace(0, 1, n, endpoint=False)[:, None]
    out = np.vstack([p[i] + (p[i + 1] - p[i]) * t for i in range(len(p) - 1)])
    return out if fechado else np.vstack([out, p[-1:]])


def elipse(cx, cy, rx, ry, n=48, rot=0.0):
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    x, y = rx * np.cos(a), ry * np.sin(a)
    cr, sr = math.cos(rot), math.sin(rot)
    return np.stack([cx + x * cr - y * sr, cy + x * sr + y * cr], axis=1)


def reamostra(p, passo=3.0, fechado=True):
    p = np.asarray(p, dtype=float)
    q = np.vstack([p, p[:1]]) if fechado else p
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(q, axis=0).T))]
    L = d[-1]
    if L < 1e-6:
        return p.copy(), 0.0
    n = max(4, int(L / passo))
    s = np.linspace(0, L, n, endpoint=not fechado)
    return np.stack([np.interp(s, d, q[:, 0]), np.interp(s, d, q[:, 1])], axis=1), L


def _normais(p, fechado):
    if fechado:
        tg = np.roll(p, -1, axis=0) - np.roll(p, 1, axis=0)
    else:
        tg = np.gradient(p, axis=0)
    n = np.hypot(tg[:, 0], tg[:, 1])[:, None] + 1e-9
    tg = tg / n
    return np.stack([-tg[:, 1], tg[:, 0]], axis=1), tg


def _ruido(s, L, fechado, rnd, comp=(70.0, 24.0), pesos=(1.0, 0.35)):
    """Ruído suave ao longo da curva (soma de senos); periódico nas curvas fechadas."""
    out = np.zeros_like(s)
    for lam, w in zip(comp, pesos):
        if fechado:
            m = max(1, round(L / lam))
            f = 2 * np.pi * m / max(L, 1e-6)
        else:
            f = 2 * np.pi / lam
        out += w * np.sin(f * s + rnd.uniform(0, 2 * np.pi))
    return out / sum(pesos)


def tremido(p, var, semente, amp=1.6, fechado=True, passo=3.0):
    """Curva reamostrada e deslocada de leve pela normal (sempre igual: o papel não ferve)."""
    q, L = reamostra(p, passo, fechado)
    if amp <= 0:
        return q, L
    rnd = random.Random(_sem((semente, 0)))
    s = np.linspace(0, L, len(q), endpoint=not fechado)
    nrm, _ = _normais(q, fechado)
    d = amp * 0.5 * _ruido(s, L, fechado, rnd)
    return q + nrm * d[:, None], L


def tesoura(p, semente, amp=None, passo=None, fechado=True, tipo=None):
    """A borda de uma peça recortada: o contorno refeito em trechos retos (cada tesourada) com as quinas fugindo um
    pouco da linha. `tipo`: tesoura | rasgado (borda miúda e irregular) | picote (zigue-zague) | estilete (quase reto).
    Peça pequena corta mais fino (a borda nunca come mais que ~4% da peça)."""
    p = np.asarray(p, dtype=float)
    if len(p) < 3:
        return p
    tipo = tipo or CORTE
    amp = BORDA if amp is None else amp
    passo = PASSO if passo is None else passo
    lo, hi = p.min(axis=0), p.max(axis=0)
    menor = max(1e-3, float(min(hi - lo)))
    amp = min(amp, 0.045 * menor)
    q0 = np.vstack([p, p[:1]]) if fechado else p
    L = float(np.hypot(*np.diff(q0, axis=0).T).sum())
    passo = max(1.5, min(passo, L / 14))
    q, L = reamostra(p, passo, fechado)
    if amp <= 0.01:
        return q
    rnd = np.random.default_rng(_sem("tesoura", semente) % (2 ** 32))
    n = len(q)
    nrm, _ = _normais(q, fechado)
    if tipo == "picote":
        d = amp * np.where(np.arange(n) % 2 == 0, 1.0, -1.0)
    elif tipo == "rasgado":
        s = np.linspace(0, L, n, endpoint=not fechado)
        d = amp * (0.7 * _ruido(s, L, fechado, random.Random(semente), comp=(40.0, 11.0), pesos=(1.0, 0.6))
                   + 0.5 * rnd.uniform(-1, 1, n))
        d = np.where(d > 0, d * 0.6, d)   # o rasgo come mais pra dentro do que pra fora
    else:
        d = amp * (0.75 * rnd.uniform(-1, 1, n) + 0.25 * np.sin(np.linspace(0, 2 * np.pi * rnd.uniform(1, 3), n) + rnd.uniform(0, 6)))
    out = q + nrm * d[:, None]
    if not fechado:
        out[0], out[-1] = q[0], q[-1]
    return out


def caminho(p, fechado=True):
    path = skia.Path()
    if len(p) < 2:
        return path
    lista = np.asarray(p, dtype=float).tolist()   # lineTo em laço é ~3x mais rápido que montar skia.Point um a um
    path.moveTo(*lista[0])
    for x, y in lista[1:]:
        path.lineTo(x, y)
    if fechado:
        path.close()
    return path


def traco_tinta(p, larg, var=None, semente=0, fechado=False, amp=1.4, ponta=(0.18, 0.18), passo=2.5, sobra=0.05):
    """Tira de papel ao longo da curva (largura quase constante, pontas cortadas retas): é o "traço" do papel.
    Curva fechada vira um anel."""
    q, L = reamostra(p, max(2.0, passo * 1.6), fechado)
    if len(q) < 2:
        return skia.Path()
    rnd = np.random.default_rng(_sem("tira", semente) % (2 ** 32))
    nrm, _ = _normais(q, fechado)
    n = len(q)
    w = larg * (1 + 0.12 * rnd.uniform(-1, 1, n))
    if not fechado:
        s = np.linspace(0, 1, n)
        a, b = (min(0.06, ponta[0]), min(0.06, ponta[1]))
        if a > 0:
            w *= np.clip(0.55 + s / a * 0.45, 0, 1)
        if b > 0:
            w *= np.clip(0.55 + (1 - s) / b * 0.45, 0, 1)
    w = np.maximum(w, 0.6)
    esq = q + nrm * (w / 2)[:, None]
    dir_ = q - nrm * (w / 2)[:, None]
    if fechado:
        path = caminho(esq, True)
        path.addPath(caminho(dir_[::-1], True))
        path.setFillType(skia.PathFillType.kEvenOdd)
        return path
    return caminho(np.vstack([esq, dir_[::-1]]), True)


def hachura(regiao, angulo, passo, larg, var=None, semente=0, amp=0.8):
    """Papel não tem hachura: devolve um caminho vazio (quem chamava continua funcionando, sem desenhar nada)."""
    return skia.Path()


def deslocado(path, dx, dy):
    q = skia.Path(path)
    q.offset(dx, dy)
    return q


def sombra_regioes(fill, luz=(-0.62, -0.78), prof=(0.30, 0.13)):
    """Regiões do lado oposto à luz (forma menos ela mesma empurrada pra luz). Devolve (meia-sombra, sombra funda)."""
    r = fill.computeTightBounds()
    tam = min(r.width(), r.height())
    out = []
    for k in prof:
        d = tam * k
        out.append(skia.Op(fill, deslocado(fill, luz[0] * d, luz[1] * d), skia.PathOp.kDifference_PathOp))
    return out


def dir_sombra():
    """Direção unitária da sombra projetada (pra baixo e pro lado do estilo)."""
    n = math.hypot(SOMBRA_DX, SOMBRA_DY) or 1.0
    return SOMBRA_DX / n, SOMBRA_DY / n


def sombra_px(altura_px):
    """Deslocamento da sombra projetada de uma peça de `altura_px` de altura na tela."""
    k = altura_px / 1000.0
    return SOMBRA_DX * k, SOMBRA_DY * k


def cor_sombra(a=1.0):
    return cor_skia(SOMBRA, 255 * SOMBRA_ALFA * a)


_SEM_SOMBRA = [False]


class sem_sombra:
    """Desliga a sombra projetada enquanto dura (a trava de contato mede a base do objeto, não a sombra dele)."""

    def __enter__(self):
        self._antes = _SEM_SOMBRA[0]
        _SEM_SOMBRA[0] = True

    def __exit__(self, *exc):
        _SEM_SOMBRA[0] = self._antes
        return False


def com_sombra():
    return not _SEM_SOMBRA[0]


# ---------------------------------------------------------------- fibra do papel (assada uma vez)

_FIBRA = {}


def _fibra_img(semente=3, tam=256):
    """Ladrilho de fibra de papel (cinza em volta do branco): fibras curtas em todas as direções e uma ondulação
    larga. Gerado uma vez por processo (numpy) e repetido como shader: nada é alocado por quadro."""
    if semente in _FIBRA:
        return _FIBRA[semente]
    rng = np.random.default_rng(semente)
    base = rng.random((tam // 16, tam // 16))
    base = np.kron(base, np.ones((16, 16)))
    k = np.ones(9) / 9
    for eixo in (0, 1):
        base = np.apply_along_axis(lambda v: np.convolve(np.r_[v[-8:], v, v[:8]], k, "same")[8:-8], eixo, base)
    fib = np.zeros((tam, tam))
    for _ in range(int(900 * max(0.3, FIBRA))):
        x, y = rng.integers(0, tam, 2)
        ang = rng.uniform(0, math.pi)
        comp = rng.integers(4, 14)
        for j in range(comp):
            xx, yy = int(x + j * math.cos(ang)) % tam, int(y + j * math.sin(ang)) % tam
            fib[yy, xx] += rng.uniform(0.5, 1.0)
    pontos = rng.random((tam, tam)) < 0.004 * float(_A.get("manchas", 0.2))
    v = 1.0 - 0.10 * (base - 0.5) - 0.12 * np.clip(fib, 0, 1) * min(1.2, FIBRA) - 0.35 * pontos
    claro = rng.random((tam, tam)) < 0.003
    v = np.where(claro, 1.0, v)
    img = np.empty((tam, tam, 4), np.uint8)
    g = np.clip(255 * v, 0, 255).astype(np.uint8)
    img[:, :, 0] = img[:, :, 1] = img[:, :, 2] = g
    img[:, :, 3] = 255
    im = skia.Image.fromarray(img, colorType=skia.ColorType.kRGBA_8888_ColorType)
    _FIBRA[semente] = im
    return im


def fibra_paint(semente=0, alfa=0.5, escala=1.0):
    """Tinta que multiplica a fibra por cima de uma peça (cada peça com o ladrilho num ponto diferente)."""
    rnd = random.Random(semente)
    m = skia.Matrix()
    m.setScale(escala, escala)
    m.postTranslate(rnd.uniform(0, 256), rnd.uniform(0, 256))
    sh = _fibra_img().makeShader(skia.TileMode.kRepeat, skia.TileMode.kRepeat, skia.SamplingOptions(skia.FilterMode.kLinear), m)
    p = skia.Paint(AntiAlias=True, Shader=sh, BlendMode=skia.BlendMode.kMultiply)
    p.setAlphaf(max(0.0, min(1.0, alfa)))
    return p


# ---------------------------------------------------------------- operações de desenho compiladas

_AMOSTRA = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)


def _vetor_local(c, dx, dy):
    """Vetor da tela (dx, dy) no espaço local do canvas (pra sombra cair sempre pro mesmo lado da tela)."""
    inv = skia.Matrix()
    if not c.getTotalMatrix().invert(inv):
        return dx, dy
    a = inv.mapXY(0, 0)
    b = inv.mapXY(dx, dy)
    return b.x() - a.x(), b.y() - a.y()


class Desenho:
    """Lista de operações prontas pra pintar (caminhos + tintas), montada uma vez por peça."""

    __slots__ = ("ops", "_img", "_somb")
    ESCALAS = (1.0, 1.5, 2.0, 3.0, 4.0, 6.0)   # px por unidade do mundo em que a parte vira textura

    def __init__(self):
        self.ops = []
        self._img = {}
        self._somb = None

    def limites(self, folga=14.0):
        r = None
        for op in self.ops:
            b = op[1].computeTightBounds()
            if r is None:
                r = skia.Rect(b.left(), b.top(), b.right(), b.bottom())
            else:
                r.join(b)
        if r is None:
            return None
        r.outset(folga, folga)
        return r

    def imagem(self, escala):
        """A parte rasterizada (uma vez) na escala: desenhar vira um drawImage."""
        k = next((e for e in self.ESCALAS if e >= escala), self.ESCALAS[-1])
        if k not in self._img:
            r = self.limites()
            if r is None:
                self._img[k] = None
            else:
                w, h = max(1, int(math.ceil(r.width() * k))), max(1, int(math.ceil(r.height() * k)))
                sup = skia.Surface(w, h)
                cc = sup.getCanvas()
                cc.clear(skia.Color(0, 0, 0, 0))
                cc.scale(k, k)
                cc.translate(-r.left(), -r.top())
                self.desenha(cc)
                self._img[k] = (sup.makeImageSnapshot(), r)
        return self._img[k]

    def pinta_em(self, c, escala=None, sombra=None):
        """Pinta no canvas: vetor (escala None) ou textura em cache na escala pedida. `sombra` = (dx, dy) em px da
        tela: antes da peça, a silhueta dela na cor da sombra, deslocada pro mesmo lado em qualquer giro."""
        if _SEM_SOMBRA[0]:   # medindo contato: vetor, sem as sombras
            self.desenha(c)
            return
        if sombra:
            dx, dy = _vetor_local(c, *sombra)
            if self._somb is None:
                self._somb = skia.Paint(AntiAlias=True, ColorFilter=skia.ColorFilters.Blend(cor_sombra(), skia.BlendMode.kSrcIn))
            c.save()
            c.translate(dx, dy)
            if not escala:
                c.saveLayer(None, self._somb)
                self.desenha(c)
                c.restore()
            else:
                im = self.imagem(escala)
                if im is not None:
                    c.drawImageRect(im[0], im[1], _AMOSTRA, self._somb)
            c.restore()
        if not escala:
            self.desenha(c)
            return
        im = self.imagem(escala)
        if im is not None:
            c.drawImageRect(im[0], im[1], _AMOSTRA)

    def pinta(self, path, paint):
        self.ops.append(("p", path, paint))

    def sombra(self, path, paint):
        self.ops.append(("s", path, paint))

    def recorte(self, regiao, sub):
        self.ops.append(("c", regiao, sub))

    def desenha(self, c):
        for op in self.ops:
            if op[0] == "p" or (op[0] == "s" and not _SEM_SOMBRA[0]):
                c.drawPath(op[1], op[2])
            elif op[0] == "s":
                continue
            else:
                c.save()
                c.clipPath(op[1], doAntiAlias=True)
                op[2].desenha(c)
                c.restore()


def borda_paint(cor, larg, a=1.0):
    """O fio claro do corte (o miolo branco do papel colorido aparecendo na borda)."""
    return skia.Paint(AntiAlias=True, Color=cor_skia(mistura(cor, (255, 255, 255), 0.42), 105 * a), Style=skia.Paint.kStroke_Style,
                      StrokeWidth=larg, StrokeJoin=skia.Paint.kRound_Join)


def peca(d, pts, cor, semente, sombra=1.0, alfa=255, borda=None, corte=True, fibra=1.0, fio=None, tipo=None):
    """Peça de papel: borda cortada, sombra projetada dura (`sombra` 0 desliga; 1 = a de uma peça grossa), papel
    da cor pedida com a fibra assada e o fio claro do corte. Devolve o caminho da peça."""
    q = tesoura(pts, semente, amp=borda, tipo=tipo) if corte else np.asarray(pts, float)
    fill = caminho(q, True)
    a = alfa / 255
    if sombra > 0:
        ux, uy = dir_sombra()
        k = 3.2 * sombra
        p = skia.Paint(AntiAlias=True, Color=cor_sombra(a * 0.85))
        d.sombra(deslocado(fill, ux * k, uy * k), p)
    d.pinta(fill, tinta_paint(cor, alfa))
    if fibra > 0:
        d.pinta(fill, fibra_paint(semente, 0.55 * fibra * a))
    if fio is None:
        r = fill.computeTightBounds()
        fio = max(0.7, min(2.0, 0.012 * min(r.width(), r.height()) + 0.7))
    if fio:
        d.pinta(fill, borda_paint(cor, fio, a))
    return fill


def forma(d, pts, cor, var, semente, contorno=5.0, sombra=1.0, hach=True, luz=(-0.62, -0.78), amp=1.5, passo_h=6.5,
          larg_h=1.1, angulo_h=0.85, tinta=TINTA, alfa=255, prof=(0.30, 0.13), fechado=True, borda_luz=None):
    """API antiga, no papel: a forma vira uma peça recortada. Peça com contorno (> 0) é peça solta e projeta sombra;
    `sombra` (que era o tom da sombra interna) vira a força da sombra projetada."""
    s = (min(1.6, contorno / 4.0) * max(0.4, min(1.0, sombra))) if contorno else 0.0
    return peca(d, pts, cor, semente, sombra=s, alfa=alfa)


def linha(d, pts, larg, var, semente, cor=TINTA, alfa=255, amp=1.0, ponta=(0.22, 0.3), suave=True, fechado=False):
    """Tira fina de papel ao longo dos pontos (fio, risco, costura)."""
    p = catmull(pts, fechado, 10) if suave and len(pts) >= 3 else np.asarray(pts, float)
    path = traco_tinta(p, larg, var, semente, fechado=fechado, ponta=ponta)
    if larg >= 2.4:
        ux, uy = dir_sombra()
        d.sombra(deslocado(path, ux * larg * 0.5, uy * larg * 0.5), skia.Paint(AntiAlias=True, Color=cor_sombra(alfa / 255 * 0.7)))
    d.pinta(path, tinta_paint(cor, alfa))


def mancha(d, pts, cor, alfa, borra=6.0, var=None, semente=0):
    """Mancha de tom: um pedaço de papel de seda (translúcido) colado por cima, com a borda cortada."""
    q = tesoura(pts, semente, amp=BORDA * 0.8)
    d.pinta(caminho(q, True), tinta_paint(cor, alfa * 0.8))


def rabiscos(d, centro, raio, n, larg, var, semente, cor=TINTA, alfa=200):
    """Tirinhas curtas soltas (pelo, palha, folha seca)."""
    rnd = random.Random(semente)
    cx, cy = centro
    for k in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        r = raio * math.sqrt(rnd.random())
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        b = rnd.uniform(0, 2 * math.pi)
        L = rnd.uniform(0.3, 1.0) * raio * 0.35
        linha(d, [(x, y), (x + math.cos(b) * L * 0.5, y + math.sin(b) * L * 0.5 + 2), (x + math.cos(b) * L, y + math.sin(b) * L)],
              larg, var, semente * 31 + k, cor, alfa)


class Cache:
    """Cache de desenhos: chave -> Desenho. Uma função `monta(d)` por chave."""

    def __init__(self, limite=1500):
        self.m = {}
        self.limite = limite

    def pega(self, chave, monta):
        d = self.m.get(chave)
        if d is None:
            if len(self.m) > self.limite:
                self.m.clear()
            d = Desenho()
            monta(d)
            self.m[chave] = d
        return d


# ---------------------------------------------------------------- acabamento do quadro

_PAPEL = {}


def _textura_quadro(W, H, semente=5):
    """A fibra leve do quadro inteiro (o "papel por trás de tudo"), gerada uma vez: o ladrilho de fibra repetido."""
    k = (W, H, semente)
    if k not in _PAPEL:
        _PAPEL[k] = _fibra_img(semente + 11)
    return _PAPEL[k]


def gradacao(tom=(1.0, 1.0, 1.0), s=1.0):
    """Matriz de cor do quadro: tom (multiplica cada canal) e saturação (1 = igual)."""
    lr, lg, lb = 0.30, 0.59, 0.11
    m = []
    for i, t in enumerate(tom):
        linha_ = [lr * (1 - s), lg * (1 - s), lb * (1 - s)]
        linha_[i] += s
        m += [v * t for v in linha_] + [0, 0]
    m += [0, 0, 0, 1, 0]
    return skia.ColorFilters.Matrix(m)


class quadro:
    """Contexto do quadro: o que for pintado dentro sai no tom do estilo (quase neutro: o papel já tem a cor); na
    saída entram a fibra leve, a vinheta fria e um grão quase invisível.

        with quadro(c, t, W, H):
            ... cena ...
    """

    def __init__(self, c, t, W=1080, H=1920, papel=ACABAMENTO["papel"], vinheta=ACABAMENTO["vinheta"], grao=ACABAMENTO["grao"],
                 gradua=True, tom=ACABAMENTO["tom"], saturacao=ACABAMENTO["saturacao"]):
        self.c, self.t, self.W, self.H = c, t, W, H
        self.tom, self.sat = tom, saturacao
        neutro = all(abs(v - 1.0) < 1e-3 for v in tom) and abs(saturacao - 1.0) < 1e-3
        self.papel, self.vin, self.grao, self.gradua = papel, vinheta, grao, gradua and not neutro

    def __enter__(self):
        if self.gradua:
            self.n = self.c.saveLayer(None, skia.Paint(ColorFilter=gradacao(self.tom, self.sat)))
        return self.c

    def __exit__(self, *exc):
        c, W, H = self.c, self.W, self.H
        if self.gradua:
            c.restore()
        c.save()
        c.resetMatrix()
        if self.papel:
            p = fibra_paint(5, self.papel, escala=1.6)
            c.drawRect(skia.Rect.MakeWH(W, H), p)
        if self.vin:
            c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=skia.GradientShader.MakeRadial(
                skia.Point(W / 2, H * 0.46), max(W, H) * 0.62,
                [cor_skia((0, 0, 0), 0), cor_skia((0, 0, 0), 0), cor_skia(SOMBRA, 120 * self.vin), cor_skia(SOMBRA, 210 * self.vin)],
                [0.0, 0.5, 0.82, 1.0])))
        if self.grao:
            p = skia.Paint(Shader=skia.PerlinNoiseShader.MakeTurbulence(0.9, 0.9, 2, passo_stop(self.t) % 997))
            p.setColorFilter(skia.ColorFilters.Matrix([0.33, 0.33, 0.33, 0, 0] * 3 + [0, 0, 0, 1, 0]))
            p.setAlphaf(self.grao)
            p.setBlendMode(skia.BlendMode.kOverlay)
            c.drawRect(skia.Rect.MakeWH(W, H), p)
        c.restore()
        return False
