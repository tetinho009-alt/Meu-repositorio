# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""O Rasgado: a ameaça do recorte de papel. Uma silhueta alta arrancada de uma folha escura, com a borda rasgada à
mão (o miolo branco da fibra aparecendo em volta), sem rosto: só dois buracos recortados no lugar dos olhos, com
luz atrás do papel, e, quando "sorri", um rasgo torto que também deixa a luz passar. Nada gráfico: assusta pela
silhueta, pela altura e pelos buracos acesos.

`Vulto` continua como nome (as cenas antigas chamam `Vulto()`).

Mundo: pés em y=1000, centro x=500; 1000 unidades = a altura dele. Pra ficar alto perto de gente, desenhe com
`altura` ~1,45x a do personagem.

Pose ({"parte": {...}} como no rig) e chaves próprias:
  olhos: "acesos" (ou "brancos") | "apagados" (ou "negros")   brilho: 0..1 (luz dos buracos)
  sorriso: 0 (sem rasgo) .. 1.2 (rasgo aberto de lado a lado)
  dedos: 0 (pontas abertas) .. 1 (fechadas, agarrando)        t: segundos (stop motion)
"""
import math
import random

import numpy as np
import skia

from . import tinta as T
from .rig_simples import RigSimples

CX = 500.0
CAB = (CX, 104.0)          # centro da cabeça
CAB_RX, CAB_RY = 60.0, 86.0
BOCA = (CX, 150.0)
CORPO = T.mistura(T.TINTA, T.PUXA, 0.22)                      # a folha escura de onde ele foi arrancado
CORPO_2 = T.mistura(CORPO, T.PUXA, 0.35)                      # um pedaço mais claro colado por cima (o peito)
FIBRA = T.mistura(T.PAPEL, (255, 255, 255), 0.55)             # o miolo branco do papel na borda rasgada
LUZ = T.mistura(T.DESTAQUE, (255, 244, 200), 0.45)            # a luz atrás dos buracos


def _ombro(l):
    return (CX + l * 76, 256.0)


def _cotovelo(l):
    return (CX + l * 96, 488.0)


def _punho(l):
    return (CX + l * 102, 700.0)


def rasgada(d, pts, cor, sid, amp=6.0, sombra=1.0):
    """Peça de papel rasgada: por baixo, a mesma forma um pouco maior na cor da fibra (o branco que aparece no rasgo);
    por cima, a peça escura com o rasgo miúdo. Devolve o caminho da peça escura."""
    fora = T.tesoura(pts, sid, amp=amp * 1.25, passo=4.0, tipo="rasgado")
    centro = np.asarray(pts, float).mean(axis=0)
    fora = centro + (fora - centro) * 1.015
    T.peca(d, fora, FIBRA, sid + 1, sombra=sombra, corte=False, fio=0, fibra=0.6)
    return T.peca(d, T.tesoura(pts, sid + 2, amp=amp, passo=3.5, tipo="rasgado"), cor, sid + 2, sombra=0, corte=False, fio=0)


class Rasgado(RigSimples):
    PARTES = [
        ("perna_e", "corpo", (CX - 24, 820.0)), ("perna_d", "corpo", (CX + 24, 820.0)),
        ("braco_e", "tronco", _ombro(-1)), ("antebraco_e", "braco_e", _cotovelo(-1)), ("mao_e", "antebraco_e", _punho(-1)),
        ("tronco", "corpo", (CX, 820.0)),
        ("pescoco", "tronco", (CX, 236.0)), ("cabeca", "pescoco", (CX, 186.0)),
        ("braco_d", "tronco", _ombro(1)), ("antebraco_d", "braco_d", _cotovelo(1)), ("mao_d", "antebraco_d", _punho(1)),
    ]

    def __init__(self, semente=13):
        super().__init__(semente)

    def expr(self, parte, pose):
        if parte.startswith("mao"):
            return (round(pose.get("dedos", 0.2) * 10) / 10,)
        return ()

    def monta(self, parte, d, var, e):
        sid = T._sem(self.semente, parte) % 100000
        l = -1 if parte.endswith("_e") else 1
        if parte.startswith("perna"):   # tocos escuros que somem debaixo da barra rasgada
            x0 = CX + l * 24
            pts = [(x0 - 12, 790), (x0 + 12, 790), (x0 + 10, 994), (x0 + l * 30, 1000), (x0 - 14, 1000)]
            rasgada(d, pts, T.escurece(CORPO, 0.8), sid, amp=3.0, sombra=0.4)
        elif parte.startswith("braco"):
            (sx, sy), (ex, ey) = _ombro(l), _cotovelo(l)
            pts = [(sx - l * 16, sy - 8), (sx + l * 18, sy - 12), (sx + l * 22, sy + 40), (ex + l * 16, ey - 4), (ex + l * 14, ey + 18),
                   (ex - l * 14, ey + 18), (ex - l * 15, ey - 16), (sx - l * 14, sy + 44)]
            rasgada(d, T.catmull(pts, True, 5), CORPO, sid, amp=5.0)
        elif parte.startswith("antebraco"):
            (ex, ey), (wx, wy) = _cotovelo(l), _punho(l)
            pts = [(ex - l * 15, ey - 14), (ex + l * 15, ey - 12), (ex + l * 13, ey + 80), (wx + l * 11, wy - 4), (wx - l * 11, wy - 4),
                   (ex - l * 13, ey + 80)]
            rasgada(d, T.catmull(pts, True, 5), CORPO, sid, amp=4.5)
        elif parte.startswith("mao"):
            self._mao(d, l, sid, e[0])
        elif parte == "tronco":
            self._manto(d, sid)
        elif parte == "pescoco":
            pts = [(CX - 16, 170), (CX + 16, 170), (CX + 20, 258), (CX - 20, 258)]
            rasgada(d, pts, CORPO, sid, amp=3.0, sombra=0.4)
        elif parte == "cabeca":
            cx, cy = CAB
            pts = []
            for a in np.linspace(0, 2 * np.pi, 48, endpoint=False):
                x, y = math.cos(a), math.sin(a)
                k = 1.0 + 0.10 * max(0.0, -y)          # alto da cabeça um pouco mais largo
                pts.append((cx + CAB_RX * k * x, cy + CAB_RY * y + (10 * x * x if y > 0 else 0)))
            rasgada(d, np.array(pts), CORPO, sid, amp=6.5)

    def _mao(self, d, l, sid, dobra):
        """Mão de papel arrancado: um toco largo com três pontas rasgadas curtas (nada de dedo comprido)."""
        wx, wy = _punho(l)
        pts = [(wx - 16, wy - 6), (wx + 16, wy - 6), (wx + 22, wy + 30)]
        for k in range(3):
            u = k / 2
            x = wx + 20 - 40 * u
            comp = (34 - 6 * abs(k - 1)) * (1 - 0.45 * dobra)
            pts += [(x + l * 6 * dobra, wy + 36 + comp), (x - 7, wy + 40)]
        pts += [(wx - 22, wy + 30)]
        rasgada(d, np.array(pts), CORPO, sid, amp=3.5, sombra=0.6)

    def _manto(self, d, sid):
        """O corpo: uma folha comprida que alarga pra baixo, a barra arrancada em tiras, e um pedaço mais claro
        colado no peito (dá volume sem traço)."""
        rnd = random.Random(self.semente)
        meia = [(CX + 18, 236), (CX + 52, 242), (CX + 78, 256), (CX + 74, 300), (CX + 62, 400), (CX + 70, 540), (CX + 94, 720),
                (CX + 120, 860)]
        barra = []
        x = CX + 120
        while x > CX - 120:   # barra rasgada em tiras de tamanhos diferentes
            barra.append((x, 880 + rnd.uniform(0, 30)))
            x -= rnd.uniform(14, 26)
            barra.append((x, 950 + rnd.uniform(-14, 34)))
            x -= rnd.uniform(8, 16)
        pts = meia + barra + [(2 * CX - px, py) for px, py in reversed(meia)]
        fill = rasgada(d, T.quina(pts, True, 4), CORPO, sid, amp=7.0, sombra=1.2)
        sub = T.Desenho()
        peito = [(CX - 52, 262), (CX + 46, 258), (CX + 40, 420), (CX + 8, 520), (CX - 30, 470), (CX - 48, 380)]
        rasgada(sub, T.catmull(peito, True, 4), CORPO_2, sid + 9, amp=5.0, sombra=0.8)
        d.recorte(fill, sub)

    def antes(self, c, parte, pose, var):
        if parte == "cabeca" and _acesos(pose) and pose.get("brilho", 0.6) > 0:
            k = pose.get("brilho", 0.6)
            for l in (-1, 1):   # luz que vaza pelos buracos e pinta o papel em volta
                c.drawCircle(CAB[0] + l * 24, CAB[1] - 8, 46, skia.Paint(AntiAlias=True, BlendMode=skia.BlendMode.kScreen,
                                                                       Color=T.cor_skia(LUZ, 70 * k),
                                                                       MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 16)))

    def depois(self, c, parte, pose, var):
        if parte != "cabeca":
            return
        acesos = _acesos(pose)
        cor = LUZ if acesos else T.escurece(CORPO, 0.4)
        olhos = self.cache.pega(("olhos", acesos), lambda d: _buracos(d, cor))
        olhos.pinta_em(c)
        k = pose.get("sorriso", 0.0)
        if k > 0:
            q = round(k * 5) / 5
            self.cache.pega(("rasgo", acesos, q), lambda d: _rasgo(d, cor, q)).pinta_em(c)


def _acesos(pose):
    return pose.get("olhos", "acesos") in ("acesos", "brancos")


def _buracos(d, cor):
    """Dois buracos recortados tortos (um maior que o outro) com a luz atrás."""
    cx, cy = CAB
    for l, (rx, ry, inc) in ((-1, (17, 11, 0.25)), (1, (15, 13, -0.2))):
        pts = T.elipse(cx + l * 26, cy - 10, rx, ry, 18, rot=inc)
        pts[:, 1] += np.where(pts[:, 0] * l > (cx + l * 26) * l, -4, 0)   # canto de fora puxado pra cima
        T.peca(d, T.tesoura(pts, 700 + l, amp=1.6, passo=4.0, tipo="rasgado"), cor, 710 + l, sombra=0, corte=False, fio=0, fibra=0.3)
    return d


def _rasgo(d, cor, k):
    """A boca: um rasgo torto de lado a lado, mais aberto com `k`."""
    cx, by = BOCA
    w = 30 + 14 * k
    h = 3 + 9 * k
    rnd = random.Random(7)
    cima = [(cx - w + 2 * w * u, by - h * math.sin(math.pi * u) * 0.4 + rnd.uniform(-2, 2) - 6 * u) for u in np.linspace(0, 1, 9)]
    baixo = [(cx - w + 2 * w * u, by + h * math.sin(math.pi * u) + rnd.uniform(-2, 3) - 6 * u) for u in np.linspace(1, 0, 9)]
    T.peca(d, np.array(cima + baixo), cor, 720, sombra=0, corte=False, fio=0, fibra=0.3)
    return d


Vulto = Rasgado   # nome antigo


def pose_espreita(t=0.0, entra=1.0, dedos=0.8, sorriso=0.9, inclina=-22.0):
    """Pose de quem espia pela porta: cabeça tombada, braço da frente agarrando o batente."""
    resp = math.sin(t * 2 * math.pi / 3.2)
    return {"t": t, "olhos": "acesos", "brilho": 0.8, "sorriso": sorriso * entra, "dedos": dedos,
            "cabeca": {"rot": inclina * entra + 2 * resp}, "pescoco": {"rot": inclina * 0.5 * entra},
            "tronco": {"rot": -6 * entra, "sy": 1 + 0.006 * resp},
            "braco_d": {"rot": -62 * entra}, "antebraco_d": {"rot": -38 * entra}, "mao_d": {"rot": 30 * entra},
            "braco_e": {"rot": 6}, "antebraco_e": {"rot": 4}}
