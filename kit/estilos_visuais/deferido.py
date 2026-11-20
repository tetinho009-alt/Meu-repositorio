# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Luz por pixel para o motor dos estilos visuais: desenha o número de cada triângulo (sem antialias), e daí tira, para cada
pixel, a profundidade, a posição no mundo e a normal (pelo plano do triângulo). Com isso dá para iluminar com lanterna,
fogo e céu, pôr textura presa no mundo e névoa de verdade, tudo em numpy."""
import math

import numpy as np
import skia

import motor as M


def recortar_perto(tri, perto):
    """Sutherland-Hodgman contra o plano z = perto (coordenadas de câmera). Devolve 0, 3 ou 4 vértices."""
    saida = []
    for k in range(3):
        a, b = tri[k], tri[(k + 1) % 3]
        da, db = a[2] - perto, b[2] - perto
        if da >= 0:
            saida.append(a)
        if (da >= 0) != (db >= 0):
            saida.append(a + (b - a) * (da / (da - db)))
    return saida


class Quadro3D:
    """Resultado da passada de ids: por pixel, face (-1 = céu), profundidade, posição, normal."""

    def __init__(self, m, cam, w, h, perto=0.12):
        V = m.v[m.f]
        n = np.cross(V[:, 1] - V[:, 0], V[:, 2] - V[:, 0])
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        cen = V.mean(axis=1)
        frente = np.einsum("ij,ij->i", n, cam.pos - cen) > 0
        pc = cam.para_camera(V)
        vis = frente & (pc[..., 2] > perto).any(axis=1)
        idx = np.nonzero(vis)[0]
        z = pc[idx, :, 2].mean(axis=1)
        ordem = idx[np.argsort(-z)]
        s = skia.Surface(w, h)
        cv = s.getCanvas()
        cv.clear(skia.Color(0, 0, 0))
        paint = skia.Paint(AntiAlias=False)
        for k in ordem:
            tri = pc[k]
            if (tri[:, 2] < perto).any():
                poli = recortar_perto(tri, perto)
                if len(poli) < 3:
                    continue
                tela = cam.projetar(np.array(poli))
            else:
                tela = cam.projetar(tri)
            pa = skia.Path()
            pa.moveTo(*tela[0])
            for p in tela[1:]:
                pa.lineTo(*p)
            pa.close()
            i = int(k) + 1
            paint.setColor(skia.Color((i >> 16) & 255, (i >> 8) & 255, i & 255))
            cv.drawPath(pa, paint)
        rgb = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3].astype(np.int64)
        self.face = (rgb[..., 0] << 16 | rgb[..., 1] << 8 | rgb[..., 2]) - 1
        self.ceu = self.face < 0
        fc = np.where(self.ceu, 0, self.face)
        ys, xs = np.mgrid[:h, :w].astype(np.float32)
        dirs = (cam.fw[None, None, :] + ((xs - w / 2) / cam.f)[..., None] * cam.rt[None, None, :]
                - ((ys - h / 2) / cam.f)[..., None] * cam.up[None, None, :]).astype(np.float32)
        self.dir = dirs / np.linalg.norm(dirs, axis=2, keepdims=True)
        self.n = n[fc].astype(np.float32)
        d_plano = np.einsum("ij,ij->i", n, V[:, 0])
        denom = np.einsum("hwc,hwc->hw", self.n, self.dir)
        denom = np.where(np.abs(denom) < 1e-5, 1e-5, denom)
        t = (d_plano[fc] - self.n @ cam.pos) / denom
        t = np.where(self.ceu | (t < 0), 400.0, np.minimum(t, 400.0))
        self.t = t.astype(np.float32)
        self.pos = (cam.pos[None, None, :] + self.dir * self.t[..., None]).astype(np.float32)
        self.prof = (self.t * (self.dir @ cam.fw)).astype(np.float32)
        self.fc = fc
        self.w, self.h = w, h


# ---------------------------------------------------------------- ruído (textura procedural presa no mundo)

_PERM = np.random.default_rng(1234).permutation(512).astype(np.int64)
_PERM = np.concatenate([_PERM, _PERM])


def _hash(ix, iy):
    return _PERM[(_PERM[ix & 511] + iy) & 511] / 511.0


def ruido2(x, y):
    xi, yi = np.floor(x).astype(np.int64), np.floor(y).astype(np.int64)
    xf, yf = x - xi, y - yi
    u, v = xf * xf * (3 - 2 * xf), yf * yf * (3 - 2 * yf)
    a, b = _hash(xi, yi), _hash(xi + 1, yi)
    c, d = _hash(xi, yi + 1), _hash(xi + 1, yi + 1)
    return (a + (b - a) * u) * (1 - v) + (c + (d - c) * u) * v


def fbm(x, y, oit=3):
    total, amp, s = 0.0, 0.5, 0.0
    for _ in range(oit):
        total = total + amp * ruido2(x, y)
        s += amp
        x, y, amp = x * 2.03 + 17.1, y * 2.03 + 3.7, amp * 0.5
    return total / s


def coords_parede(pos, n):
    """Coordenadas (u, v) da superfície: chão usa x/z; parede usa a horizontal da parede e a altura."""
    ax = np.abs(n)
    chao = ax[..., 1] > 0.7
    u = np.where(chao, pos[..., 0], np.where(ax[..., 0] > ax[..., 2], pos[..., 2], pos[..., 0]))
    v = np.where(chao, pos[..., 2], pos[..., 1])
    return u, v, chao


def suave(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def reinhard(x, exp=1.0):
    x = x * exp
    return x / (1 + x)


def de_linear(x):
    return np.clip(np.power(np.clip(x, 0, 1), 1 / 2.2) * 255, 0, 255).astype(np.uint8)
