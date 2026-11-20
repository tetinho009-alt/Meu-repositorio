# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Estilos extras do kit (registrados no ESTILOS de estilos.py)."""
import math

import numpy as np
import skia

import motor as M
from motor import W, H
from estilos import _corpo2d, _pose2d_caminhada

RNG = np.random.default_rng


def _img_skia(rgb):
    rgb = np.ascontiguousarray(rgb, dtype=np.uint8)
    return skia.Image.fromarray(np.dstack([rgb, np.full(rgb.shape[:2], 255, np.uint8)]),
                                colorType=skia.kRGBA_8888_ColorType)


# ================================================================ 5) STICKER

def _palito_sticker(cv, pts, esc, cor=(22, 22, 26)):
    pares = (("q", "pesc"), ("q", "joelho_e"), ("joelho_e", "pe_e"), ("q", "joelho_d"), ("joelho_d", "pe_d"),
             ("ombro_e", "cot_e"), ("cot_e", "mao_e"), ("ombro_d", "cot_d"), ("cot_d", "mao_d"))
    for camada, c, larg, off, a, borrao in (("sombra", (0, 0, 0), 60, 14, 70, 10), ("borda", (255, 255, 255), 58, 0, 255, 0),
                                            ("traco", cor, 16, 0, 255, 0)):
        p = M.tinta(c, a, traco=larg * esc / 1.0, borrao=borrao)
        for a_, b_ in pares:
            cv.drawLine(pts[a_][0] + off, pts[a_][1] + off, pts[b_][0] + off, pts[b_][1] + off, p)
        r = 40 * esc + (larg - 16) * esc / 2
        if camada == "traco":
            cv.drawCircle(*pts["cab"], 40 * esc, M.tinta(cor, traco=16 * esc))
            cv.drawCircle(*pts["cab"], 40 * esc - 8 * esc, M.tinta((255, 214, 90)))
        else:
            cv.drawCircle(pts["cab"][0] + off, pts["cab"][1] + off, r, M.tinta(c, a, borrao=borrao))


def _estrela(cx, cy, r1, r2, n=5, rot=0.0):
    pts = []
    for k in range(2 * n):
        r = r1 if k % 2 == 0 else r2
        a = rot + k * math.pi / n - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return M.caminho(pts)


def _com_borda(cv, desenho_path, cor, borda=34):
    sombra = M.tinta((0, 0, 0), 70, borrao=10)
    cv.save()
    cv.translate(12, 16)
    cv.drawPath(desenho_path, sombra)
    cv.restore()
    p = M.tinta((255, 255, 255), traco=borda)
    cv.drawPath(desenho_path, p)
    cv.drawPath(desenho_path, M.tinta((255, 255, 255)))
    cv.drawPath(desenho_path, M.tinta(cor))


def _batida(t, t0, dur=0.45):
    """Escala do adesivo batendo na tela: entra grande, passa do ponto e assenta."""
    if t < t0:
        return 0.0
    u = (t - t0) / dur
    if u >= 1:
        return 1.0
    return 1.0 + 0.6 * (1 - u) ** 2 * math.cos(u * math.pi * 2.2)


def sticker():
    def quadro(i, t):
        s, cv = M.superficie()
        cv.clear(M.cor((255, 120, 150)))
        for y in range(0, H, 64):
            for x in range((y // 64 % 2) * 32, W, 64):
                cv.drawCircle(x, y, 7, M.tinta((255, 160, 185)))
        # 1) adesivo do boneco acenando
        k = _batida(t, 0.2)
        if k:
            cv.save()
            cv.translate(W * 0.5, H * 0.56)
            cv.rotate(-6 + 3 * math.sin(t * 2))
            cv.scale(k, k)
            pul = max(0.0, math.sin((t - 7.5) * math.pi * 1.6)) if t > 7.5 else 0.0
            onda = 0.5 + 0.5 * math.sin(t * 7)
            a = {"tronco": 0.0, "coxa_e": 0.12, "coxa_d": -0.12, "joelho_e": 0.08 + 0.6 * pul, "joelho_d": 0.08 + 0.6 * pul,
                 "ombro_e": -0.35, "ombro_d": 2.5, "cot_e": 0.3, "cot_d": 0.2 + 0.7 * onda}
            pts = _corpo2d((0, 120 - 160 * pul), a, esc=1.5)
            _palito_sticker(cv, pts, 1.5)
            cv.restore()
        # 2) estrela
        k = _batida(t, 1.6)
        if k:
            cv.save()
            cv.translate(W * 0.22, H * 0.22)
            cv.rotate(14 + 4 * math.sin(t * 1.5))
            cv.scale(k, k)
            _com_borda(cv, _estrela(0, 0, 150, 66), (255, 206, 60))
            cv.restore()
        # 3) balão com texto
        k = _batida(t, 3.0)
        if k:
            cv.save()
            cv.translate(W * 0.68, H * 0.2)
            cv.rotate(8)
            cv.scale(k, k)
            pa = skia.Path()
            pa.addRRect(skia.RRect.MakeRectXY(skia.Rect(-250, -120, 250, 120), 60, 60))
            pa.moveTo(-90, 110)
            pa.lineTo(-160, 220)
            pa.lineTo(-10, 115)
            pa.close()
            _com_borda(cv, pa, (255, 255, 255))
            cv.drawPath(pa, M.tinta((30, 30, 34), traco=8))
            M.texto(cv, "BORA?", 0, 45, 130, (30, 30, 34), fonte="Impact", alinhar="centro")
            cv.restore()
        # 4) coração e raio
        k = _batida(t, 4.6)
        if k:
            cv.save()
            cv.translate(W * 0.2, H * 0.83)
            cv.rotate(-12)
            cv.scale(k, k)
            pa = skia.Path()
            pa.moveTo(0, 120)
            pa.cubicTo(-260, -40, -120, -200, 0, -70)
            pa.cubicTo(120, -200, 260, -40, 0, 120)
            pa.close()
            _com_borda(cv, pa, (235, 50, 80))
            cv.restore()
        k = _batida(t, 5.8)
        if k:
            cv.save()
            cv.translate(W * 0.8, H * 0.82)
            cv.rotate(10)
            cv.scale(k, k)
            _com_borda(cv, M.caminho([(-40, -190), (110, -190), (30, -30), (120, -30), (-70, 200), (-10, 20),
                                      (-100, 20)]), (120, 200, 255))
            cv.restore()
        return M.pixels(s)

    return quadro


# ================================================================ 6) PIXEL ART 16 BITS

PW, PH = 180, 320


def _quadro_pixel(t):
    s, cv = M.superficie(PW, PH)
    for k, c in enumerate([(40, 40, 92), (60, 56, 124), (92, 74, 150), (140, 96, 166), (206, 124, 150), (246, 170, 130)]):
        cv.drawRect(skia.Rect(0, k * 30, PW, k * 30 + 30), M.tinta(c, aa=False))
    cv.drawCircle(130, 120, 16, M.tinta((255, 226, 150), aa=False))
    vel = 34.0
    rng = RNG(3)

    def faixa(par, y_base, amp, cor, semente, passo=12):
        r = RNG(semente)
        alturas = r.uniform(0, amp, 400)
        off = (t * vel * par) % passo
        k0 = int(t * vel * par // passo)
        pts = [(-passo, PH)]
        for k in range(PW // passo + 3):
            pts.append((k * passo - off, y_base - alturas[(k + k0) % 400]))
        pts.append((PW + passo, PH))
        cv.drawPath(M.caminho(pts), M.tinta(cor, aa=False))

    faixa(0.15, 190, 50, (70, 60, 120), 1, 18)
    faixa(0.35, 215, 30, (52, 96, 110), 2, 10)
    # árvores
    for k in range(-1, 8):
        x = int(k * 34 - (t * vel * 0.7) % 34)
        cv.drawRect(skia.Rect(x + 6, 218, x + 9, 236), M.tinta((90, 56, 40), aa=False))
        for j, (w_, y_) in enumerate([(14, 200), (11, 192), (7, 186)]):
            cv.drawRect(skia.Rect(x + 7.5 - w_ / 2, y_, x + 7.5 + w_ / 2, y_ + 12), M.tinta((40 + 20 * j, 140 + 14 * j, 70), aa=False))
    # chão de tijolo
    off = int(t * vel) % 16
    cv.drawRect(skia.Rect(0, 236, PW, PH), M.tinta((150, 90, 60), aa=False))
    cv.drawRect(skia.Rect(0, 236, PW, 240), M.tinta((90, 190, 80), aa=False))
    for y in range(244, PH, 8):
        d = 8 if (y // 8) % 2 else 0
        for x in range(-off - 16 + d, PW + 16, 16):
            cv.drawRect(skia.Rect(x, y, x + 15, y + 7), M.tinta((176, 108, 72), aa=False))
    # moedas
    for k in range(6):
        mx = (k * 70 + 160 - t * vel) % 420 - 20
        if mx < 66 and k <= int((t * vel + 30) / 70):
            continue
        larg = abs(math.cos(t * 6 + k)) * 5 + 1
        cv.drawOval(skia.Rect(mx - larg, 200, mx + larg, 212), M.tinta((255, 210, 60), aa=False))
    # personagem (sprite de 16x24 feito de retângulos), 4 quadros de caminhada
    qd = int(t * 8) % 4
    x0, y0 = 54, 236 - (1 if qd in (1, 3) else 0)
    R = lambda a, b, c, d, cor: cv.drawRect(skia.Rect(x0 + a, y0 - d, x0 + c, y0 - b), M.tinta(cor, aa=False))
    pernas = {0: [(4, 0, 7, 7), (9, 0, 12, 7)], 1: [(2, 0, 5, 7), (11, 1, 14, 7)], 2: [(5, 0, 8, 7), (8, 0, 11, 7)],
              3: [(11, 0, 14, 7), (2, 1, 5, 7)]}[qd]
    for a, b, c, d in pernas:
        R(a, b, c, d, (50, 60, 140))
        R(a, b, c, b + 2, (40, 30, 30))
    R(3, 7, 13, 15, (220, 60, 60))
    braco = 2 if qd in (1, 3) else 0
    R(1, 8 + braco, 3, 14, (240, 190, 150))
    R(13, 10 - braco, 15, 14, (240, 190, 150))
    R(4, 15, 12, 22, (240, 190, 150))
    R(3, 20, 13, 24, (120, 70, 40))
    R(9, 17, 11, 19, (30, 30, 30))
    pontos = 1200 + int(t * vel / 70) * 100
    M.texto(cv, f"PONTOS {pontos:06d}", 6, 16, 11, (255, 255, 255), fonte="Consolas", negrito=True)
    M.texto(cv, "FASE 1-1", PW - 6, 16, 11, (255, 255, 255), fonte="Consolas", negrito=True, alinhar="dir")
    return M.pixels(s)


def pixel_16bit():
    return lambda i, t: M.ampliar(_quadro_pixel(t), 6)


# ================================================================ 13) TV DE TUBO

def crt_retro():
    def quadro(i, t):
        img = M.ampliar(_quadro_pixel(t), 6)
        s, cv = M.superficie()
        cv.drawImage(_img_skia(img), 0, 0)
        if t < 2.5:
            M.texto(cv, "CANAL 03", W - 70, 150, 80, (80, 255, 120), fonte="Consolas", negrito=True, alinhar="dir")
        if 0.0 < t < 0.35:
            ruido = RNG(i).integers(0, 255, (H // 8, W // 8, 1)).repeat(3, axis=2)
            return M.crt(M.ampliar(ruido.astype(np.uint8), 8))
        return M.crt(M.pixels(s))

    return quadro


# ================================================================ 7) VOXEL

DIRS = [((1, 0, 0), 0.82), ((-1, 0, 0), 0.82), ((0, 1, 0), 1.0), ((0, -1, 0), 0.5), ((0, 0, 1), 0.68), ((0, 0, -1), 0.68)]


def voxels_para_malha(cel):
    v, f, c = [], [], []
    for (x, y, z), cor in cel.items():
        for (dx, dy, dz), _ in DIRS:
            if (x + dx, y + dy, z + dz) in cel:
                continue
            n = np.array([dx, dy, dz], float)
            cen = np.array([x, y, z], float) + n * 0.5
            a = np.array([dy, dz, dx], float) if dx == 0 else np.array([0, 1, 0], float)
            if dy != 0:
                a = np.array([1, 0, 0], float)
            b = np.cross(n, a)
            q = [cen + (-a - b) * 0.5, cen + (a - b) * 0.5, cen + (a + b) * 0.5, cen + (-a + b) * 0.5]
            base = len(v)
            v += q
            for tri in ([0, 1, 2], [0, 2, 3]):
                p0, p1, p2 = (q[k] for k in tri)
                if np.dot(np.cross(p1 - p0, p2 - p0), n) < 0:
                    tri = [tri[0], tri[2], tri[1]]
                f.append([base + k for k in tri])
                c.append(cor)
    return M.Malha(np.array(v), np.array(f), np.array(c, float))


def voxel():
    rng = RNG(8)
    cel = {}
    N = 22
    for x in range(-N // 2, N // 2):
        for z in range(-N // 2, N // 2):
            d = math.hypot(x, z) / (N / 2)
            h = int(round(4.5 * (1 - d * d) + 1.2 * math.sin(x * 0.6) * math.cos(z * 0.5)))
            if d > 1.05:
                continue
            for y in range(-2, max(h, 0) + 1):
                if y == h:
                    cor = (240, 222, 160) if h <= 1 else (96, 178, 82)
                elif y >= h - 1:
                    cor = (140, 96, 64)
                else:
                    cor = (128, 128, 136)
                cel[(x, y, z)] = cor
            if h < 1:
                cel[(x, 1, z)] = (70, 140, 220)
    for _ in range(9):
        x, z = int(rng.integers(-7, 7)), int(rng.integers(-7, 7))
        topo = max(y for (xx, y, zz) in cel if xx == x and zz == z)
        if cel[(x, topo, z)] != (96, 178, 82):
            continue
        for y in range(topo + 1, topo + 4):
            cel[(x, y, z)] = (110, 74, 48)
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                for dy in (0, 1):
                    cel[(x + dx, topo + 4 + dy, z + dz)] = (50, 140, 70) if (dx + dz + dy) % 2 else (64, 160, 80)
        cel[(x, topo + 6, z)] = (64, 160, 80)
    ilha = voxels_para_malha(cel)

    def personagem(t):
        pulo = abs(math.sin(t * math.pi * 1.2)) * 1.2
        c2 = {}
        for y in range(0, 2):
            c2[(0, y, 0)] = (50, 70, 160)
            c2[(1, y, 0)] = (50, 70, 160)
        for y in range(2, 4):
            for x in (0, 1):
                c2[(x, y, 0)] = (230, 80, 70)
        c2[(-1, 3, 0)] = (240, 190, 150)
        c2[(2, 3, 0)] = (240, 190, 150)
        for y in range(4, 6):
            for x in (0, 1):
                c2[(x, y, 0)] = (240, 190, 150)
        c2[(0, 6, 0)] = (90, 60, 40)
        c2[(1, 6, 0)] = (90, 60, 40)
        m = voxels_para_malha(c2)
        m = M.Malha(m.v * 0.45, m.f, m.c)
        return m.mover(M.ry(t * 1.2), (0.0, 5.3 + pulo, 0.0))

    def quadro(i, t):
        s, cv = M.superficie()
        M.gradiente_vertical(cv, W, H, (150, 210, 250), (230, 244, 255))
        a = t * 2 * math.pi / 10 * 0.6 + 0.5
        cam = M.Camera((40 * math.sin(a), 24, 40 * math.cos(a)), (0, 1.5, 0), fov=38)
        M.desenhar(cv, M.juntar([ilha, personagem(t)]), cam, amb=0.5, variacao=0.05, luz=(-0.4, -0.85, -0.3))
        return M.pixels(s)

    return quadro


# ================================================================ 8) DIORAMA ISOMÉTRICO

def _telhado(sx, sz, h, cor, t):
    x, z = sx / 2, sz / 2
    v = np.array([[-x, 0, -z], [x, 0, -z], [x, 0, z], [-x, 0, z], [-x, h, 0], [x, h, 0]], float)
    f = [[0, 1, 5], [0, 5, 4], [3, 4, 5], [3, 5, 2], [0, 4, 3], [1, 2, 5], [0, 3, 2], [0, 2, 1]]
    f = M._orienta(v, f, np.array([0, h / 3, 0]))
    return M.Malha(v, f, cor).mover(None, t)


def diorama_iso():
    rng = RNG(21)
    objs = [M.caixa(10, 1.2, 10, (120, 84, 58), t=(0, -0.6, 0)), M.caixa(10.02, 0.12, 10.02, (110, 186, 92), t=(0, 0.02, 0))]
    objs.append(M.caixa(1.4, 0.13, 10.04, (80, 150, 220), t=(2.6, 0.03, 0)))
    objs.append(M.caixa(10.04, 0.14, 1.0, (90, 90, 96), t=(0, 0.04, -1.5)))
    objs.append(M.caixa(1.8, 0.3, 1.2, (150, 110, 76), t=(2.6, 0.12, -1.5)))
    for k, (x, z, cor, tel) in enumerate([(-3, -3.4, (240, 230, 210), (200, 70, 60)), (-0.8, -3.4, (250, 214, 160), (70, 90, 160)),
                                         (-3.2, 1.0, (230, 236, 240), (80, 150, 100)), (-0.4, 1.2, (245, 200, 200), (190, 90, 70))]):
        objs.append(M.caixa(1.6, 1.2, 1.4, cor, t=(x, 0, z), base=True))
        objs.append(_telhado(1.8, 1.6, 0.8, tel, (x, 1.2, z)))
        objs.append(M.caixa(0.3, 0.5, 0.05, (90, 60, 40), t=(x, 0.25, z + 0.71)))
        objs.append(M.caixa(0.3, 0.3, 0.05, (160, 210, 240), t=(x + 0.5, 0.75, z + 0.71)))
    for _ in range(16):
        x, z = rng.uniform(-4.6, 4.6), rng.uniform(-4.6, 4.6)
        if abs(x - 2.6) < 1.0 or abs(z + 1.5) < 0.8 or (x < 0.5 and (abs(z + 3.4) < 1.2 or abs(z - 1.1) < 1.2)):
            continue
        objs.append(M.cilindro(0.08, 0.4, 5, (110, 76, 50), t=(x, 0, z)))
        objs.append(M.cilindro(0.42, 1.0, 6, (60, 140, 80), r_topo=0, t=(x, 0.3, z)))
    base = M.juntar(objs)

    def quadro(i, t):
        s, cv = M.superficie()
        M.gradiente_vertical(cv, W, H, (250, 236, 214), (214, 226, 246))
        u = (t * 0.9) % 10 - 5
        carro = M.juntar([M.caixa(0.7, 0.25, 0.4, (230, 80, 70), t=(u, 0.25, -1.3)),
                          M.caixa(0.4, 0.2, 0.36, (250, 240, 230), t=(u - 0.05, 0.46, -1.3))])
        pessoas = M.juntar([M.caixa(0.12, 0.3, 0.12, (60, 80, 180), t=(-2 + 0.6 * math.sin(t), 0.15, -0.6)),
                            M.icosfera(0.08, (240, 190, 150), t=(-2 + 0.6 * math.sin(t), 0.38, -0.6))])
        a = math.radians(45 + 25 * math.sin(t * 0.4))
        alvo = np.array([0, 0.4, 0])
        cam = M.Camera(alvo + [14 * math.sin(a), 11, 14 * math.cos(a)], alvo, orto=19)
        M.desenhar(cv, M.juntar([base, carro, pessoas]), cam, amb=0.55, luz=(-0.5, -0.8, -0.2))
        img = M.pixels(s).astype(float)
        lum = img.mean(axis=2, keepdims=True)
        img = np.clip(lum + (img - lum) * 1.25, 0, 255)
        bor = M.borrar(img, 12)
        yy = np.linspace(-1, 1, H)[:, None, None]
        m = np.clip((np.abs(yy) - 0.28) / 0.45, 0, 1)
        return np.clip(img * (1 - m) + bor * m, 0, 255).astype(np.uint8)

    return quadro


# ================================================================ 9) BACKROOMS EM FITA VHS

def backrooms_vhs():
    rng = RNG(13)
    parede, chao, teto = (232, 214, 128), (176, 152, 88), (236, 230, 196)
    objs = []
    for x in np.arange(-6, 18, 1.2):
        for z in np.arange(-4, 22, 1.2):
            objs.append(M.caixa(1.2, 0.05, 1.2, chao, t=(x, -0.025, z)))
            luz = (round(x / 1.2) % 3 == 0) and (round(z / 1.2) % 3 == 0)
            objs.append(M.caixa(1.18, 0.05, 1.18, (255, 252, 230) if luz else teto, t=(x, 2.8, z), emi=luz))
    paredes = [((-1.4, 0), (-1.4, 16)), ((1.4, 0), (1.4, 5)), ((1.4, 7.5), (1.4, 12.6)), ((-1.4, 16), (14, 16)),
               ((1.4, 12.6), (14, 12.6)), ((1.4, 5), (5, 5)), ((1.4, 7.5), (5, 7.5)), ((5, 5), (5, 7.5)),
               ((-1.4, -1), (1.4, -1))]
    for (x0, z0), (x1, z1) in paredes:
        cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
        objs.append(M.caixa(max(abs(x1 - x0), 0.2), 2.8, max(abs(z1 - z0), 0.2), parede, t=(cx, 0, cz), base=True))
    mundo = M.juntar(objs)

    def quadro(i, t):
        s, cv = M.superficie()
        cv.clear(M.cor((214, 200, 130)))
        if t < 7:
            pos, yaw = np.array([0.0, 1.55, 1.0 + 1.6 * t]), 0.0
        else:
            k = float(M.suave(t, 7, 8.6))
            pos, yaw = np.array([0.0 + 1.4 * max(0, t - 8), 1.55, 12.2 + 1.6 * min(t - 7, 1.0) * 0.4]), k * math.pi / 2
        bob = math.sin(t * 2 * math.pi * 0.9)
        pos = pos + [0.03 * bob, 0.03 * abs(bob), 0]
        alvo = pos + [math.sin(yaw) * 5, -0.15, math.cos(yaw) * 5]
        cam = M.Camera(pos, alvo, fov=68)
        M.desenhar(cv, mundo, cam, nevoa=((214, 200, 130), 6, 30), amb=0.74, luz=(0.2, -1, 0.3), variacao=0.04)
        img = M.pixels(s).astype(float)
        if RNG(int(t * 4)).random() < 0.12:
            img *= 0.82
        img = M.vhs(np.clip(img, 0, 255).astype(np.uint8), t, semente=i)
        s2, cv2 = M.superficie()
        cv2.drawImage(_img_skia(img), 0, 0)
        if int(t * 2) % 2 == 0:
            cv2.drawCircle(96, 128, 22, M.tinta((230, 40, 40)))
        M.texto(cv2, "REC", 132, 146, 54, (240, 240, 240), fonte="Consolas", negrito=True)
        seg = int(t) + 3 * 60 + 12
        M.texto(cv2, f"00:{seg // 60:02d}:{seg % 60:02d}", W - 60, 146, 50, (240, 240, 240), fonte="Consolas",
                negrito=True, alinhar="dir")
        M.texto(cv2, "NOV 08 1996   03:14 AM", 70, H - 110, 46, (240, 240, 240), fonte="Consolas", negrito=True)
        M.texto(cv2, "PLAY", W - 120, H - 110, 46, (240, 240, 240), fonte="Consolas", negrito=True, alinhar="dir")
        cv2.drawPath(M.caminho([(W - 104, H - 146), (W - 70, H - 128), (W - 104, H - 110)]), M.tinta((240, 240, 240)))
        return M.pixels(s2)

    return quadro


# ================================================================ 10) MANGÁ A NANQUIM

CORES_ANIME = {"pele": (250, 214, 190), "camisa": (40, 50, 90), "calca": (30, 30, 40), "sapato": (240, 240, 240),
               "cabelo": (40, 40, 60)}


def _cabelo_espetado(pos, yaw, quique, cor, esc=1.0):
    cab = np.array(pos) + M.ry(yaw) @ (np.array([0, 0.95 + quique + 0.80, -0.02]) * esc)
    pecas = [M.icosfera(0.165 * esc, cor, nivel=1, t=cab, achatar=(1, 0.8, 1))]
    for k in range(8):
        a = k / 8 * 2 * math.pi
        d = M.ry(yaw) @ np.array([math.sin(a) * 0.12, 0.05, math.cos(a) * 0.12 - 0.04]) * esc
        R = M.ry(yaw + a) @ M.rx(-1.1 + 0.2 * (k % 2))
        pecas.append(M.cilindro(0.06 * esc, 0.2 * esc, 4, cor, r_topo=0, R=R, t=cab + d))
    for k in range(3):
        R = M.ry(yaw) @ M.rx(1.9) @ M.rz(-0.5 + 0.5 * k)
        pecas.append(M.cilindro(0.05 * esc, 0.17 * esc, 4, cor, r_topo=0, R=R,
                                t=cab + M.ry(yaw) @ np.array([-0.07 + 0.07 * k, 0.07, 0.12]) * esc))
    return [M.com_casca(p, 0.02, (18, 14, 24)) for p in pecas]


def _boneco_anime(t, yaw, pos=(0, 0, 0), passo=1.0, cores=CORES_ANIME):
    pose = M.pose_caminhada(t * 2 * math.pi * 1.1, passo)
    corpo = M.boneco(pose, cores, yaw=yaw, pos=pos, casca=0.022, cabelo=False)
    return M.juntar([corpo] + _cabelo_espetado(pos, yaw, pose["quique"], cores["cabelo"]))


def manga():
    paineis = [(40, 40, 1040, 640), (40, 670, 1040, 1250), (40, 1280, 1040, 1880)]

    def painel_img(k, t, w, h):
        s, cv = M.superficie(w, h)
        cv.clear(M.cor((255, 255, 255)))
        if k == 0:
            rng = RNG(4)
            x = 0
            while x < w:
                bw, bh = rng.uniform(60, 140), rng.uniform(120, 360)
                cv.drawRect(skia.Rect(x, h * 0.62 - bh, x + bw, h * 0.62), M.tinta((150, 150, 150)))
                x += bw + 6
            m = _boneco_anime(t, math.pi, pos=(0, 0, 0))
            cam = M.Camera((0.4, 1.5, -3.6 + 0.1 * t), (0, 1.15, 0), fov=40, w=w, h=h)
        elif k == 1:
            for j in range(26):
                y = (j * 37 + 13) % h
                cv.drawLine(0, y, w, y, M.tinta((20, 20, 20), traco=2 + (j % 3) * 2))
            m = _boneco_anime(t * 1.8, math.pi / 2, passo=1.5)
            cam = M.Camera((3.0, 1.3, 0.2), (0, 1.1, 0), fov=38, w=w, h=h)
        else:
            cx, cy = w / 2, h * 0.45
            for j in range(60):
                a = j / 60 * 2 * math.pi
                r0 = 260 + 40 * (j % 3)
                cv.drawLine(cx + math.cos(a) * r0, cy + math.sin(a) * r0, cx + math.cos(a) * 1400,
                            cy + math.sin(a) * 1400, M.tinta((20, 20, 20), traco=3 + (j % 4)))
            m = _boneco_anime(0.25, math.pi * 1.05, passo=0.2)
            cam = M.Camera((0.5, 0.35, -2.7 + 0.25 * min(t, 3)), (0, 1.35, 0), fov=50, w=w, h=h)
        sm, cvm = M.superficie(w, h)
        cvm.clear(M.cor((255, 0, 255)))
        cinza = M.Malha(m.v, m.f, np.repeat(m.c.mean(axis=1, keepdims=True), 3, axis=1) * 1.25, m.emi, m.casca)
        M.desenhar(cvm, cinza, cam, tons=3, amb=0.45)
        fig = M.pixels(sm).astype(float)
        fundo = M.pixels(s).astype(float)
        mascara = ~((fig[..., 0] > 240) & (fig[..., 1] < 20) & (fig[..., 2] > 240))
        lum = fig.mean(axis=2) / 255
        tom = np.where(lum < 0.18, 0.0, np.where(lum > 0.8, 1.0, M.meio_tom(lum * 1.15, passo=9)))
        out = fundo.mean(axis=2) / 255
        out[mascara] = tom[mascara]
        return np.repeat((out * 255)[..., None], 3, axis=2).astype(np.uint8)

    def quadro(i, t):
        s, cv = M.superficie()
        cv.clear(M.cor((250, 248, 242)))
        for k, (x0, y0, x1, y1) in enumerate(paineis):
            t0 = k * 3.0
            if t < t0:
                continue
            ap = float(M.suave(t, t0, t0 + 0.35))
            w, h = x1 - x0, y1 - y0
            img = painel_img(k, t - t0, w, h)
            cv.save()
            cv.translate(0, (1 - ap) * 60)
            cv.drawImage(_img_skia(img), x0, y0, skia.SamplingOptions(), skia.Paint(Alphaf=ap))
            cv.drawRect(skia.Rect(x0, y0, x1, y1), M.tinta((15, 15, 15), traco=10))
            cv.restore()
        if t > 3.4:
            M.texto(cv, "ZUM!", 900, 860, 170, (255, 255, 255), fonte="Impact", alinhar="dir", contorno=((10, 10, 10), 22))
        if t > 7.0:
            pa = skia.Path()
            pa.addOval(skia.Rect(560, 1320, 1010, 1500))
            _ = pa
            cv.drawOval(skia.Rect(560, 1320, 1010, 1500), M.tinta((255, 255, 255)))
            cv.drawOval(skia.Rect(560, 1320, 1010, 1500), M.tinta((10, 10, 10), traco=6))
            M.texto(cv, "Agora vai.", 785, 1428, 64, (10, 10, 10), negrito=True, alinhar="centro")
        return M.pixels(s)

    return quadro


# ================================================================ 14) ANIME CEL-SHADING

def anime_cel():
    rng = RNG(9)
    petalas = rng.uniform(0, 1, (70, 4))
    cores = {"pele": (255, 222, 200), "camisa": (250, 250, 252), "calca": (40, 60, 120), "sapato": (200, 60, 60),
             "cabelo": (230, 120, 60)}
    chao = M.terreno(30, 16, lambda x, z: -0.04 * (x * x + z * z) * 0.15, lambda x, y, z: (110, 200, 110))

    def quadro(i, t):
        s, cv = M.superficie()
        M.gradiente_vertical(cv, W, H, (70, 140, 240), (190, 226, 255), 0, H * 0.7)
        for cx, cy, r in ((220, 520, 170), (380, 470, 210), (560, 540, 160), (800, 380, 140), (940, 430, 120)):
            x = cx + 12 * t
            cv.drawCircle(x, cy + 30, r, M.tinta((210, 222, 245)))
            cv.drawCircle(x, cy, r, M.tinta((255, 255, 255)))
        m = M.juntar([chao, _boneco_anime(t, math.pi * 0.85, pos=(0, 0.0, 0), cores=cores)])
        cam = M.Camera((1.2 - 0.3 * t / 10, 0.45, -3.6 + 0.9 * M.suave(t, 0, 10)), (0, 1.3, 0), fov=46)
        M.desenhar(cv, m, cam, tons=2, amb=0.62, sombra_cor=(120, 90, 190), luz=(0.4, -0.7, 0.55))
        for px, py, pv, pr in petalas:
            x = (px * W + 120 * math.sin(t * 1.3 + pv * 7) - t * 60 * (0.5 + pv)) % W
            y = (py * H + t * (90 + 120 * pv)) % H
            cv.save()
            cv.translate(x, y)
            cv.rotate(t * 90 * (pv - 0.5) + pr * 360)
            cv.drawOval(skia.Rect(-14, -7, 14, 7), M.tinta((255, 190, 210)))
            cv.restore()
        for k in range(6):
            y = (k * 210 + t * 500) % H
            cv.drawLine(W * 0.05, y, W * 0.3, y + 6, M.tinta((255, 255, 255), 120, traco=4))
        flare = skia.Paint(AntiAlias=True, Color=M.cor((255, 250, 220), 120), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 60))
        flare.setBlendMode(skia.BlendMode.kPlus)
        cv.drawCircle(W * 0.85, H * 0.12, 160, flare)
        return M.pixels(s)

    return quadro


# ================================================================ 11) RECORTE DE PAPEL

def _papel_borda(pts, semente, amp=4):
    r = RNG(semente)
    return [(x + r.uniform(-amp, amp), y + r.uniform(-amp, amp)) for x, y in pts]


def recorte_papel():
    rng = RNG(31)
    textura = rng.normal(0, 7, (H // 4, W // 4))
    textura = np.repeat(np.repeat(textura, 4, axis=0), 4, axis=1)[..., None]

    def camada(cv, path, cor, tq, sem, sombra=True):
        r = RNG(sem + int(tq * 12))
        dx, dy, rot = r.uniform(-1.5, 1.5), r.uniform(-1.5, 1.5), r.uniform(-0.4, 0.4)
        cv.save()
        cv.translate(dx, dy)
        cv.rotate(rot)
        if sombra:
            cv.save()
            cv.translate(8, 10)
            cv.drawPath(path, M.tinta((0, 0, 0), 80, borrao=9))
            cv.restore()
        cv.drawPath(path, M.tinta(cor))
        cv.restore()

    def morro(y, amp, freq, fase, sem):
        pts = [(-20, H + 20)] + [(x, y - amp * (0.6 + 0.4 * math.sin(x * freq + fase))) for x in range(-20, W + 60, 40)] + [(W + 40, H + 20)]
        return M.caminho(_papel_borda(pts, sem))

    def quadro(i, t):
        tq = math.floor(t * 12) / 12
        s, cv = M.superficie()
        cv.clear(M.cor((168, 214, 236)))
        sol = skia.Path()
        for k in range(24):
            a = k / 24 * 2 * math.pi + tq * 0.3
            r = 170 if k % 2 == 0 else 125
            (sol.moveTo if k == 0 else sol.lineTo)(W * 0.74 + r * math.cos(a), H * 0.17 + r * math.sin(a))
        sol.close()
        camada(cv, sol, (255, 196, 70), tq, 1)
        for k, (cx, cy) in enumerate([(200, 380), (650, 300), (1000, 470)]):
            x = (cx + tq * 40) % (W + 300) - 150
            nuvem = skia.Path()
            for dx, dy, r in ((0, 0, 70), (70, -30, 85), (150, 0, 70), (75, 25, 75)):
                nuvem.addCircle(x + dx, cy + dy, r)
            camada(cv, nuvem, (252, 252, 248), tq, 10 + k)
        camada(cv, morro(H * 0.55, 140, 0.004, 1.0, 3), (96, 160, 110), tq, 20)
        camada(cv, morro(H * 0.66, 110, 0.006, 2.5, 4), (126, 190, 106), tq, 21)
        for k, x in enumerate((140, 880)):
            camada(cv, M.caminho(_papel_borda([(x - 90, H * 0.66), (x, H * 0.48), (x + 90, H * 0.66)], 40 + k)),
                   (60, 130, 80), tq, 30 + k)
            camada(cv, M.caminho([(x - 14, H * 0.66), (x + 14, H * 0.66), (x + 14, H * 0.7), (x - 14, H * 0.7)]),
                   (120, 84, 56), tq, 32 + k)
        camada(cv, morro(H * 0.78, 60, 0.008, 0.3, 5), (160, 210, 120), tq, 22)
        # boneco de papel com colchetes (articulado só no ombro e no quadril: nada de cotovelo dobrado errado)
        x = W * 0.2 + tq * 62
        y = H * 0.74 + 8 * abs(math.sin(tq * 6))
        balanco = 0.5 * math.sin(tq * 6)
        partes = []

        def membro(px, py, ang, comp, larg, cor):
            pa = skia.Path()
            pa.addRRect(skia.RRect.MakeRectXY(skia.Rect(-larg / 2, -larg / 2, larg / 2, comp), larg / 2, larg / 2))
            m = skia.Matrix()
            m.setRotate(math.degrees(ang))
            m.postTranslate(px, py)
            pa.transform(m)
            partes.append((pa, cor))

        membro(x - 22, y - 10, balanco, 150, 46, (60, 70, 140))
        membro(x - 30, y - 200, -balanco * 0.9, 140, 38, (230, 180, 140))
        tronco = skia.Path()
        tronco.addRRect(skia.RRect.MakeRectXY(skia.Rect(x - 70, y - 230, x + 40, y), 30, 30))
        partes.append((tronco, (230, 90, 80)))
        membro(x + 14, y - 10, -balanco, 150, 46, (70, 80, 150))
        cabeca = skia.Path()
        cabeca.addCircle(x - 15, y - 290, 64)
        partes.append((cabeca, (240, 196, 160)))
        membro(x - 6, y - 200, balanco * 0.9, 140, 38, (240, 190, 150))
        for k, (pa, cor) in enumerate(partes):
            camada(cv, pa, cor, tq, 50 + k)
        cv.drawCircle(x + 8, y - 300, 8, M.tinta((40, 30, 30)))
        for px, py in ((x - 22, y - 10), (x + 14, y - 10), (x - 30, y - 200), (x - 6, y - 200)):
            cv.drawCircle(px, py, 7, M.tinta((200, 170, 70)))
        M.texto(cv, "um passo de cada vez", W / 2, H * 0.92, 66, (60, 60, 70), negrito=True, alinhar="centro")
        img = M.pixels(s).astype(float) + textura
        return np.clip(img, 0, 255).astype(np.uint8)

    return quadro


# ================================================================ 12) MASSINHA

def massinha():
    rng = RNG(77)
    digitais = rng.normal(0, 1, (H // 2, W // 2))
    digitais = M.borrar(np.repeat(digitais[..., None], 1, axis=2), 2)[..., 0] * 6
    digitais = np.repeat(np.repeat(digitais, 2, axis=0), 2, axis=1)[..., None]

    def bolota(cv, cx, cy, rx, ry, cor, sem, tq, brilho=True):
        r = RNG(sem + int(tq * 12) * 7)
        pts = []
        for k in range(28):
            a = k / 28 * 2 * math.pi
            j = 1 + r.uniform(-0.025, 0.025)
            pts.append((cx + rx * j * math.cos(a), cy + ry * j * math.sin(a)))
        pa = skia.Path()
        pa.moveTo(*pts[0])
        for k in range(len(pts)):
            p1, p2 = pts[(k + 1) % len(pts)], pts[(k + 2) % len(pts)]
            pa.quadTo(p1[0], p1[1], (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
        pa.close()
        cv.save()
        cv.translate(10, 14)
        cv.drawPath(pa, M.tinta((0, 0, 0), 60, borrao=14))
        cv.restore()
        claro = tuple(min(255, c * 1.25 + 20) for c in cor)
        escuro = tuple(c * 0.62 for c in cor)
        sh = skia.GradientShader.MakeRadial((cx - rx * 0.35, cy - ry * 0.4), max(rx, ry) * 1.4,
                                            [M.cor(claro), M.cor(cor), M.cor(escuro)], [0, 0.45, 1])
        cv.drawPath(pa, skia.Paint(AntiAlias=True, Shader=sh))
        if brilho:
            cv.drawOval(skia.Rect(cx - rx * 0.55, cy - ry * 0.7, cx - rx * 0.15, cy - ry * 0.45),
                        M.tinta((255, 255, 255), 110, borrao=6))

    def quadro(i, t):
        tq = math.floor(t * 12) / 12
        s, cv = M.superficie()
        M.gradiente_vertical(cv, W, H, (250, 210, 170), (255, 236, 200))
        bolota(cv, W * 0.5, H * 0.95, W * 0.9, H * 0.25, (196, 120, 70), 1, tq, brilho=False)
        for k, (x, h_, c) in enumerate([(150, 260, (240, 90, 110)), (330, 180, (250, 200, 70)), (860, 230, (140, 110, 230)),
                                       (980, 160, (240, 140, 60))]):
            cv.drawLine(x, H * 0.76, x, H * 0.76 - h_, M.tinta((80, 160, 80), traco=22))
            for p in range(5):
                a = p / 5 * 2 * math.pi + tq
                bolota(cv, x + 34 * math.cos(a), H * 0.76 - h_ + 34 * math.sin(a), 30, 30, c, 100 + k * 10 + p, tq, False)
            bolota(cv, x, H * 0.76 - h_, 24, 24, (255, 230, 120), 200 + k, tq, False)
        pulo = abs(math.sin(tq * math.pi * 0.9))
        espreme = 1 - 0.25 * (1 - pulo) ** 3
        cx, cy = W * 0.5, H * 0.66 - 380 * pulo
        rx, ry = 230 / espreme ** 0.5, 260 * espreme
        for lado in (-1, 1):
            bolota(cv, cx + lado * 230, cy + 30 - 60 * pulo, 60, 44, (90, 170, 220), 300 + lado, tq)
        bolota(cv, cx, cy, rx, ry, (100, 190, 240), 400, tq)
        for lado in (-1, 1):
            ex, ey = cx + lado * 80, cy - 60 * espreme
            fechado = (tq % 3.0) < 0.12
            if fechado:
                cv.drawLine(ex - 40, ey, ex + 40, ey, M.tinta((30, 30, 40), traco=14))
            else:
                bolota(cv, ex, ey, 52, 60, (250, 250, 250), 500 + lado, tq, False)
                bolota(cv, ex + 10, ey + 10, 24, 28, (30, 30, 40), 510 + lado, tq, False)
        boca = skia.Path()
        boca.moveTo(cx - 60, cy + 70 * espreme)
        boca.quadTo(cx, cy + (130 + 30 * pulo) * espreme, cx + 60, cy + 70 * espreme)
        cv.drawPath(boca, M.tinta((60, 30, 40), traco=16))
        img = M.pixels(s).astype(float) + digitais
        return np.clip(img, 0, 255).astype(np.uint8)

    return quadro


EXTRAS = {"sticker": sticker, "pixel_16bit": pixel_16bit, "crt_retro": crt_retro, "voxel": voxel,
          "diorama_iso": diorama_iso, "backrooms_vhs": backrooms_vhs, "manga": manga, "anime_cel": anime_cel,
          "recorte_papel": recorte_papel, "massinha": massinha}
