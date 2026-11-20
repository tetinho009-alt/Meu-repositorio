# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Cenários 3D em diorama de papel: câmera pinhole (Cam3D), e cada face vira uma peça de papel colorido da caixa
do canal, com a borda cortada, a fibra assada, o fio claro do corte e a sombra dura da peça sobre a de trás. A luz
troca o papel em 3 tons (não há degradê nem hachura); a distância entra como camadas de papel de seda (neblina em
degraus e tiras translúcidas rente ao chão); lâmpadas com halo, como luz atrás do papel. A arquitetura pode entortar
(casa de papel dobrado), conforme o estilo.

Unidades em metros: X lateral, Y altura, Z profundidade. Nada vem de fora: tudo é gerado por código.

Uso:
    cena = Cena(cam, t)                     # t em segundos (vento e stop motion)
    ... cena.face(...), cena.caixa(...), cena.ator(X, Z, desenha) ...
    cena.desenha(c)
Ou as cenas prontas: rua(c, t, ...), quarto(c, t, ...), laje(c, t, ...), estrada(c, t, ...).
"""
import math
import random

import numpy as np
import skia

from . import tinta as T

class Cam3D:
    """Câmera pinhole: x lateral, h altura do olho, F distância focal em px, hz linha do horizonte, z = dolly."""

    def __init__(self, x=0.0, h=1.6, F=1000.0, hz=1000.0, cx=540, z=0.0):
        self.x, self.h, self.F, self.hz, self.cx, self.z = x, h, F, hz, cx, z

    def p(self, X, Y, Z):
        Z = max(Z - self.z, 0.35)
        return (self.cx + (X - self.x) * self.F / Z, self.hz + (self.h - Y) * self.F / Z)

    def escala(self, Z):
        return self.F / max(Z - self.z, 0.35)


W, H = 1080, 1920
NEVOA = T.mistura(T.PUXA, T.PAPEL, 0.42)   # papel de seda frio da distância


def _lua():
    """A lua é o papel mais amarelo da caixa, clareado (mostarda vira lua); sem amarelo, o papel claro."""
    import colorsys
    amarelos = [p for p in T.PAPEIS if 30 <= colorsys.rgb_to_hls(*(v / 255 for v in p))[0] * 360 <= 70]
    if amarelos:
        return T.mistura(max(amarelos, key=sum), (255, 246, 214), 0.35)
    return T.mistura(T.PAPEL, (255, 255, 255), 0.2)


LUA = _lua()
LAMPADA = (226, 200, 140)


def _n(*a):
    """Ruído determinístico em -1..1."""
    return (math.sin(sum(v * (k + 1) * 12.9898 for k, v in enumerate(a)) + 1.7) * 43758.5453) % 1.0 * 2 - 1


_BANDAS = {}   # cache das camadas de fundo: (cena, var, camada) -> (textura, câmera de referência)


PERTURBA = None   # (dx, dh, dz, dyaw, dpitch): só na trava de espaço (qa/espaco.py)


class CamG(Cam3D):
    """Câmera pinhole com giro e inclinação: `yaw` (graus, positivo vira pra direita), `pitch` (graus, positivo olha
    pra baixo). Com yaw=pitch=0 é idêntica à Cam3D. `p()` projeta, `cam_xyz()` dá o ponto no espaço da câmera."""

    def __init__(self, x=0.0, h=1.6, F=1000.0, hz=1000.0, cx=W / 2, z=0.0, yaw=0.0, pitch=0.0):
        self._orig = (x, h, F, hz, cx, z, yaw, pitch)
        if PERTURBA:   # trava de espaço: a câmera inteira mexe um tico; o que não mexer junto está grudado na tela
            dx, dh, dz, dyaw, dpitch = PERTURBA
            x, h, z, yaw, pitch = x + dx, h + dh, z + dz, yaw + dyaw, pitch + dpitch
        super().__init__(x=x, h=h, F=F, hz=hz, cx=cx, z=z)
        self.yaw, self.pitch = yaw, pitch
        a, b = math.radians(yaw), math.radians(pitch)
        self._cy, self._sy, self._cp, self._sp = math.cos(a), math.sin(a), math.cos(b), math.sin(b)

    def cam_xyz(self, X, Y, Z):
        dx, dy, dz = X - self.x, Y - self.h, Z - self.z
        xr = dx * self._cy - dz * self._sy
        zr = dx * self._sy + dz * self._cy
        yc = dy * self._cp + zr * self._sp
        zc = -dy * self._sp + zr * self._cp
        return xr, yc, zc

    def p(self, X, Y, Z):
        xc, yc, zc = self.cam_xyz(X, Y, Z)
        zc = max(zc, 0.05)
        return (self.cx + xc * self.F / zc, self.hz - yc * self.F / zc)

    def de_cam(self, xc, yc, zc):
        return (self.cx + xc * self.F / max(zc, 0.05), self.hz - yc * self.F / max(zc, 0.05))

    def prof(self, X, Y, Z):
        return self.cam_xyz(X, Y, Z)[2]

    def escala(self, Z):
        return self.F / max(Z - self.z, 0.35)

    def original(self):
        """A mesma câmera sem a perturbação da trava (a câmera de referência de uma composição não mexe no teste)."""
        global PERTURBA
        guarda, PERTURBA = PERTURBA, None
        try:
            x, h, F, hz, cx, z, yaw, pitch = self._orig
            return CamG(x=x, h=h, F=F, hz=hz, cx=cx, z=z, yaw=yaw, pitch=pitch)
        finally:
            PERTURBA = guarda

    def mundo(self, x, y, D):
        """O ponto do mundo que cai no pixel (x, y) a D metros de profundidade (o inverso de p())."""
        xc, yc, zc = (x - self.cx) * D / self.F, (self.hz - y) * D / self.F, D
        zr = yc * self._sp + zc * self._cp            # desfaz o pitch
        dy = yc * self._cp - zc * self._sp
        dx = xc * self._cy + zr * self._sy            # desfaz o yaw
        dz = -xc * self._sy + zr * self._cy
        return (self.x + dx, self.h + dy, self.z + dz)

    def desloc_ceu(self):
        """Quanto o céu (gradiente, lua, nuvens: tudo no infinito) anda na tela pelo GIRO da câmera em relação a
        `ceu_ref` = (yaw, pitch) em que o céu foi composto. Translação não mexe no infinito. Câmera que gira dentro do
        plano declara `ceu_ref`; sem ele, a referência é o giro dela mesma sem a perturbação da trava."""
        yaw0, pitch0 = getattr(self, "ceu_ref", (self._orig[6], self._orig[7]))
        tg = lambda g: math.tan(math.radians(g))  # noqa: E731
        c0, c1 = math.cos(math.radians(pitch0)), math.cos(math.radians(self.pitch))
        return -self.F * (tg(self.yaw) / c1 - tg(yaw0) / c0), -self.F * (tg(self.pitch) - tg(pitch0))


def _cam_tupla(cam):
    return (cam.x, cam.h, cam.F, cam.hz, cam.cx, cam.z, getattr(cam, "yaw", 0.0), getattr(cam, "pitch", 0.0))


def _reprojeta(ref, cam, faixa, tol=1.5):
    """Matriz 2D que leva a camada pintada na câmera `ref` pra câmera atual, válida pra faixa de profundidade
    [z0, z1]; None se o erro na faixa passa de `tol` px (aí a camada é refeita)."""
    x0c, h0, F0, hz0, cx0, z0c, yw0, pt0 = ref
    x1c, h1, F1, hz1, cx1, z1c, yw1, pt1 = _cam_tupla(cam)
    if (x0c, h0, F0, hz0, cx0, z0c, yw0, pt0) == (x1c, h1, F1, hz1, cx1, z1c, yw1, pt1):
        return skia.Matrix()
    if (yw0, pt0) != (yw1, pt1) or yw1 or pt1:   # câmera girando: refaz a camada
        return None
    zs = [max(z, z1c + 0.5, z0c + 0.5) for z in faixa]
    mats = []
    for Z in zs:
        if Z > 1e5:   # céu: só desloca com a câmera girando (aqui não gira): fica parado
            mats.append((1.0, 0.0, 0.0))
            continue
        s = F1 * (Z - z0c) / (F0 * (Z - z1c))
        tx = (x0c - x1c) * F1 / (Z - z1c)
        ty = (h1 - h0) * F1 / (Z - z1c)
        mats.append((s, tx, ty))
    (sa, txa, tya), (sb, txb, tyb) = mats[0], mats[-1]
    if abs(sa - sb) * 1100 > tol or abs(txa - txb) > tol or abs(tya - tyb) > tol:
        return None
    s, tx, ty = (sa + sb) / 2, (txa + txb) / 2, (tya + tyb) / 2
    m = skia.Matrix()
    m.setAll(s, 0, cx1 - s * cx0 + tx, 0, s, hz1 - s * hz0 + ty, 0, 0, 1)
    return m


def torto(lean=0.0, sag=0.0, wob=0.03, semente=0, base=(0.0, 0.0, 0.0), rot=0.0):
    """Deformação de arquitetura torta: inclina (cisalha X por Y), embarriga e treme cada vértice. O quanto entorta
    vem do estilo (T.TORTO): o mesmo cenário sai reto num canal e caricato noutro."""
    bx, by, bz = base
    lean, sag, wob = lean * T.TORTO, sag * T.TORTO, wob * T.TORTO

    def f(p):
        X, Y, Z = p
        dx = lean * (Y - by)
        dy = -sag * math.sin(math.pi * max(0.0, min(1.0, (X - bx) / 6 + 0.5))) * max(0.0, (Y - by)) / 4
        if rot:
            ox, oz = X - bx, Z - bz
            X, Z = bx + ox * math.cos(rot) - oz * math.sin(rot), bz + ox * math.sin(rot) + oz * math.cos(rot)
        k = wob
        return (X + dx + k * _n(semente, round(X, 2), round(Y, 2), round(Z, 2)),
                Y + dy + k * _n(semente + 1, round(Z, 2), round(X, 2)),
                Z + k * _n(semente + 2, round(Y, 2), round(X, 2)))
    return f


class Cena:
    def __init__(self, cam, t=0.0, nevoa=NEVOA, alcance=38.0, luz=(0.55, 0.55, 0.62), tinta=T.TINTA, w_tinta=3.0):
        self.cam, self.t = cam, t
        self.var = T.ferve(t)
        self.nevoa, self.alcance = nevoa, alcance
        n = math.sqrt(sum(v * v for v in luz))
        self.L = tuple(v / n for v in luz)       # direção de onde vem a luz da lua
        self.tinta, self.w_tinta = tinta, w_tinta
        self.itens = []
        self.luzes = []
        self.k = 0
        self.cache_id = None
        self._escuro = None

    # ------------------------------------------------------------ utilidades
    def dist(self, Z):
        return max(0.4, Z - self.cam.z)

    def fog(self, Z):
        return 1 - math.exp(-self.dist(Z) / self.alcance)

    def p(self, P):
        return self.cam.p(*P)

    def _seed(self):
        self.k += 1
        return self.k * 7919

    def item(self, z, fn, vivo=False, zg=None, centro=None):
        """Item de pintura. `z` = ordem (mais longe primeiro); `vivo` = muda a cada quadro (ator, roupa no varal) e não
        entra no cache de fundo; `zg` = profundidade geométrica (pra reprojetar a camada quando a câmera anda)."""
        self.itens.append((z, len(self.itens), fn, vivo, z if zg is None else zg, centro))

    def prepara(self, cam, t):
        """Reaproveita a cena montada noutro quadro: troca câmera e tempo e tira os itens vivos do quadro anterior."""
        self.cam, self.t = cam, t
        self.var = T.ferve(t)
        self.itens = [it for it in self.itens if not it[3]]
        self.luzes = [l for l in self.luzes if not l[7]]
        self._escuro = None
        return self

    def _projeta_poli(self, pts):
        cam = self.cam
        if not hasattr(cam, "cam_xyz"):
            return np.array([cam.p(*q) for q in pts])
        cs = [cam.cam_xyz(*q) for q in pts]
        perto = 0.08
        if all(c_[2] > perto for c_ in cs):
            return np.array([cam.de_cam(*c_) for c_ in cs])
        out = []
        for i in range(len(cs)):
            a, b = cs[i], cs[(i + 1) % len(cs)]
            ina, inb = a[2] > perto, b[2] > perto
            if ina:
                out.append(a)
            if ina != inb:
                u = (perto - a[2]) / (b[2] - a[2])
                out.append(tuple(a[k] + (b[k] - a[k]) * u for k in range(3)))
        if len(out) < 3:
            return None
        return np.array([cam.de_cam(*c_) for c_ in out])

    def _tinta_paint(self, f, a=255):
        return T.tinta_paint(T.mistura(self.tinta, self.nevoa, f * 0.6), a * (1 - 0.6 * f))

    def larg(self, Z, k=1.0):
        return max(0.6, min(5.0, self.w_tinta * k * math.sqrt(6.0 / self.dist(Z))))

    # ------------------------------------------------------------ primitivas
    def face(self, pts, cor, contorno=1.0, hach=True, z=None, textura=None, luz_extra=0.0, sombra=1.0, rim=False, vivo=False):
        """Polígono 3D. `z` só muda a ordem de pintura (a neblina vem da geometria). `textura(c, cena, f)` desenha
        detalhe por cima (tijolo, telha), recortado pela face. Face funda (chão, rua) ganha neblina em degradê."""
        pts = [tuple(p) for p in pts]
        P = np.array(pts)
        zg = float(P[:, 2].mean())
        zc = zg if z is None else z
        sid = self._seed()
        a, b, cc = P[0], P[1], P[2]
        nrm = np.cross(b - a, cc - a)
        nn = np.linalg.norm(nrm) or 1.0
        nrm = nrm / nn
        cam_pos = np.array([self.cam.x, self.cam.h, self.cam.z])
        if np.dot(nrm, cam_pos - P.mean(axis=0)) < 0:
            nrm = -nrm
        lam = float(np.dot(nrm, self.L))
        i_perto, i_longe = int(np.argmin(P[:, 2])), int(np.argmax(P[:, 2]))
        cor_est = T.cenario(cor)
        if abs(nrm[1]) > 0.9:   # chão: papel mais apagado (não vira tapete vermelho)
            g_ = sum(cor_est) / 3
            cor_est = tuple(g_ + (v - g_) * 0.55 for v in cor_est)

        def desenha(c):
            fp, fl = self.fog(P[i_perto, 2]), self.fog(P[i_longe, 2])
            fundo = fl - fp > 0.12
            f = fp if fundo else self.fog(zg)
            scr = self._projeta_poli(pts)
            if scr is None:
                return
            # papel: a luz não degradê, troca de papel em 3 tons (lado da lua, lado de lado, lado de trás)
            k = max(0.0, lam)
            k = 1.0 if k > 0.55 else (0.72 if k > 0.15 else 0.5)
            tom = tuple(min(255, v * (0.42 + 0.58 * k) + 30 * luz_extra) for v in cor_est)
            esc = math.sqrt(6.0 / self.dist(zg))
            if corta:   # borda de tesoura só no que não é chão/parede inteira (ali a borda é a de outra peça)
                scr = T.tesoura(scr, sid, amp=min(2.2, 1.4 * esc), passo=max(6.0, 14.0 * esc))
            fill = T.caminho(scr)
            if contorno and sombra > 0 and T.com_sombra():   # sombra projetada dura da peça sobre o que está atrás
                sx, sy = T.sombra_px(1000.0 * min(1.4, 0.55 * esc))
                c.drawPath(T.deslocado(fill, sx, sy), skia.Paint(AntiAlias=True, Color=T.cor_sombra((1 - f) * min(1.0, sombra))))
            cor_f = T.mistura(tom, self.nevoa, f)
            c.drawPath(fill, T.tinta_paint(cor_f))
            c.drawPath(fill, T.fibra_paint(sid, 0.5 * (1 - 0.6 * f)))
            if textura or fundo:
                c.save()
                c.clipPath(fill, doAntiAlias=True)
                if textura:
                    textura(c, self, f)
                if fundo:  # camadas de papel de seda na distância: a neblina sobe em degraus, não em degradê
                    A, B = P[i_perto], P[i_longe]
                    s0, s1 = np.array(self.p(A)), np.array(self.p(B))
                    eixo = s1 - s0
                    L2 = float(np.dot(eixo, eixo)) or 1.0
                    cores, pos = [], []
                    ant = None
                    for u in (0.0, 0.04, 0.1, 0.2, 0.35, 0.55, 0.8, 1.0):
                        Q = A + (B - A) * u
                        sq = np.array(self.p(Q))
                        pq = min(1.0, max(0.0, float(np.dot(sq - s0, eixo)) / L2))
                        fq = self.fog(Q[2])
                        cq = T.cor_skia(self.nevoa, 255 * max(0.0, (fq - fp) / max(1e-3, 1 - fp)))
                        if ant is not None:   # degrau: a cor de antes vai até aqui e troca de uma vez
                            cores.append(ant)
                            pos.append(pq)
                        cores.append(cq)
                        pos.append(pq)
                        ant = cq
                    ordem = sorted(range(len(pos)), key=lambda i: (pos[i], i))
                    c.drawPaint(skia.Paint(Shader=skia.GradientShader.MakeLinear(
                        [skia.Point(*s0), skia.Point(*s1)], [cores[i] for i in ordem], [pos[i] for i in ordem])))
                c.restore()
            if contorno:   # o fio claro do corte
                c.drawPath(fill, T.borda_paint(cor_f, max(0.6, min(1.6, 0.9 * esc)), 1 - f))
        corta = not (contorno and abs(nrm[1]) > 0.9 and len(pts) == 4 and (np.ptp(P[:, 0]) > 20 or np.ptp(P[:, 2]) > 20))
        self.item(zc, desenha, vivo=vivo, zg=zg, centro=tuple(P.mean(axis=0)))

    def linha(self, pts3, k=1.0, z=None, cor=None, alfa=255, n=1, vivo=False):
        """Tira fina de papel por pontos 3D (fio, galho, rachadura)."""
        pts3 = [tuple(p) for p in pts3]
        zg = float(np.mean([p[2] for p in pts3]))
        zc = zg if z is None else z
        sid = self._seed()

        def desenha(c):
            f = self.fog(zg)
            if hasattr(self.cam, "cam_xyz") and min(self.cam.cam_xyz(*q)[2] for q in pts3) < 0.08:
                return   # traço que passa por trás da câmera: some
            scr = np.array([self.p(q) for q in pts3])
            w = self.larg(zg, k)
            pa = self._tinta_paint(f, alfa) if cor is None else T.tinta_paint(T.mistura(cor, self.nevoa, f), alfa * (1 - 0.7 * f))
            c.drawPath(T.traco_tinta(T.catmull(scr, False, 6) if len(scr) > 2 else scr, w, self.var, sid, amp=0.8), pa)
        self.item(zc, desenha, vivo=vivo, zg=zg, centro=tuple(np.mean(np.array(pts3, float), axis=0)))

    def caixa(self, x0, x1, y0, y1, z0, z1, cor, deforma=None, topo=True, frente=True, lados=True, fundo=False, textura=None,
              cor_topo=None, rim=True, textura_face=None, vivo=False):
        f = deforma or (lambda p: p)
        if textura_face is not None:   # textura que depende da face (parede: reboco, pichação, umidade)
            _face = self.face

            def face_tex(pts, cor_, **kw):
                ys = [p[1] for p in pts]
                if kw.get("textura") is None and len(pts) == 4 and max(ys) - min(ys) > 0.05:   # só parede (face em pé)
                    kw["textura"] = textura_face(pts)
                return _face(pts, cor_, vivo=vivo, **kw)
            self.face = face_tex
            try:
                return Cena.caixa(self, x0, x1, y0, y1, z0, z1, cor, deforma, topo, frente, lados, fundo, textura, cor_topo, rim)
            finally:
                del self.face
        V = {k: f(v) for k, v in {
            "a": (x0, y0, z0), "b": (x1, y0, z0), "c": (x1, y1, z0), "d": (x0, y1, z0),
            "e": (x0, y0, z1), "f": (x1, y0, z1), "g": (x1, y1, z1), "h": (x0, y1, z1)}.items()}
        zs = (z0 + z1) / 2
        if fundo:
            self.face([V["e"], V["f"], V["g"], V["h"]], cor, textura=textura, z=z1)
        if lados:
            # só os lados que a câmera vê
            if self.cam.x < x0:
                self.face([V["a"], V["e"], V["h"], V["d"]], cor, textura=textura, z=zs)
            if self.cam.x > x1:
                self.face([V["b"], V["f"], V["g"], V["c"]], cor, textura=textura, z=zs)
        if topo and self.cam.h > y1 - 0.01:
            self.face([V["d"], V["c"], V["g"], V["h"]], cor_topo or cor, z=zs, rim=rim)
        if frente and self.cam.z < z0:
            self.face([V["a"], V["b"], V["c"], V["d"]], cor, textura=textura, z=z0, rim=rim)
        return V

    def ator(self, X, Z, desenha, altura_m=1.7, Y=0.0, rim=0.6):
        """Personagem/bicho 2D na cena: `desenha(c, x, y, altura_px)` com os pés em (X, Y, Z); entra na ordem de
        profundidade, ganha neblina e luz de recorte da lua."""
        def fn(c):
            x, y = self.cam.p(X, Y, Z)
            if hasattr(self.cam, "cam_xyz"):
                if self.cam.cam_xyz(X, Y, Z)[2] < 0.2:
                    return
                x2, y2 = self.cam.p(X, Y + 1.0, Z)
                alt = altura_m * math.hypot(x2 - x, y2 - y)
            else:
                alt = altura_m * self.cam.escala(Z)
            f = self.fog(Z)
            c.saveLayer(None, None)
            desenha(c, x, y, alt)
            if f > 0.02:   # longe: uma folha de papel de seda na frente (tinge a figura, sem borrar)
                p = T.tinta_paint(self.nevoa, 255 * f)
                p.setBlendMode(skia.BlendMode.kSrcATop)
                c.drawRect(skia.Rect.MakeLTRB(-W, -H, 2 * W, 2 * H), p)
            c.restore()
        self.item(Z, fn, vivo=True, centro=(X, Y + altura_m / 2, Z))

    def neblina(self, Z, altura=1.4, alfa=0.55, x0=-60, x1=60):
        """Faixa de neblina rente ao chão numa profundidade, com a borda de cima ondulada e andando devagar: as
        camadas em profundidades diferentes é que dão a distância."""
        sem = self._seed()

        def fn(c):
            a, b = self.cam.p(0, 0, Z), self.cam.p(0, altura, Z)
            base, topo = a[1], b[1]
            h = max(8.0, base - topo)
            rnd = random.Random(sem)
            fases = [rnd.uniform(0, 6.28) for _ in range(3)]
            path = skia.Path()
            path.moveTo(-200, base + h * 0.4)
            ts = T.passo_stop(self.t) / 12.0   # a tira anda em degraus, como peça empurrada no stop motion
            for x in np.linspace(-200, W + 200, 28):
                y = topo + h * 0.35 * (math.sin(x / 140 + fases[0] + ts * 0.15) + 0.5 * math.sin(x / 57 + fases[1] - ts * 0.25))
                path.lineTo(x, y)
            path.lineTo(W + 200, base + h * 0.4)
            path.close()
            # tira de papel de seda: borda de cima recortada em ondas, translúcida, com o fio claro do corte
            cor = T.mistura(self.nevoa, LUA, 0.3)
            a = min(0.85, alfa * (0.55 + 0.5 * T.SEDA))
            c.drawPath(T.deslocado(path, 0, -max(2.0, h * 0.05)), T.tinta_paint(T.mistura(cor, (255, 255, 255), 0.35), 255 * a * 0.35))
            c.drawPath(path, T.tinta_paint(cor, 255 * a))
            c.drawPath(path, T.fibra_paint(sem, 0.35 * a))
        self.item(Z + 0.01, fn)

    def luz(self, X, Y, Z, raio_m, cor=LAMPADA, forca=1.0, chao=True, pisca=None, vivo=False):
        """Ponto de luz quente com halo e halação. `pisca` = semente: a lâmpada falha de vez em quando."""
        self.luzes.append((X, Y, Z, raio_m, cor, forca, chao, vivo, pisca))

    def escuro(self, nivel=0.6, buracos=(), tom=(4, 3, 6)):
        """Apaga a cena depois de pintada, menos onde há luz: buracos = [(X, Y, Z, raio_m, força)]."""
        self._escuro = (nivel, buracos, tom)

    def desenha(self, c, ceu=None, nuvens=None):
        """Pinta tudo. Com `self.cache_id` (as cenas prontas ligam), o fundo vai pra cache em camadas: cada grupo de
        itens parados entre dois itens vivos vira uma textura; com a câmera parada o quadro só
        cola as texturas, e com a câmera andando cada camada é reprojetada (escala + deslocamento na profundidade dela)
        e só é refeita quando o erro passa de ~1,5 px."""
        if getattr(self.cam, "yaw", 0.0) or getattr(self.cam, "pitch", 0.0):
            def chave(it):
                if it[5] is None:
                    return (-it[0], it[1])
                return (-(self.cam.prof(*it[5]) + (it[0] - it[4])), it[1])
            itens = sorted(self.itens, key=chave)
        else:
            itens = sorted(self.itens, key=lambda it: (-it[0], it[1]))
        if hasattr(self.cam, "desloc_ceu") and (ceu or nuvens):
            dxc, dyc = self.cam.desloc_ceu()
            if abs(dxc) > 0.01 or abs(dyc) > 0.01:   # o céu anda com o GIRO da câmera, não com a translação

                def _desloca(fn):
                    def g(cc, ce):
                        cc.save()
                        cc.translate(dxc, dyc)
                        fn(cc, ce)
                        cc.restore()
                    return g
                ceu = _desloca(ceu) if ceu else None
                nuvens = _desloca(nuvens) if nuvens else None
        sup = c.getSurface() if getattr(self, "cache_id", None) else None
        if sup is None:
            if ceu:
                ceu(c, self)
            if nuvens:
                nuvens(c, self)
            for it in itens:
                it[2](c)
        else:
            if ceu:
                self._banda(c, sup, ("ceu",), lambda cc: ceu(cc, self), (1e6, 1e6))
            if nuvens:
                nuvens(c, self)
            grupo = []
            for it in itens + [None]:
                if it is None or it[3]:
                    if grupo:
                        zs = [g[4] for g in grupo]
                        self._banda(c, sup, ("b", grupo[0][1], grupo[-1][1], len(grupo)),
                                    lambda cc, g=grupo: [x[2](cc) for x in g], (min(zs), max(zs)))
                        grupo = []
                    if it is not None:
                        it[2](c)
                else:
                    grupo.append(it)
        if getattr(self, "_escuro", None):
            nivel, buracos, tom = self._escuro
            c.saveLayer(None, None)
            c.drawPaint(T.tinta_paint(tom, 255 * nivel))
            for X, Y, Z, r, forca in buracos:
                x, y = self.cam.p(X, Y, Z)
                R = r * self.cam.escala(Z)
                p = skia.Paint(AntiAlias=True, BlendMode=skia.BlendMode.kDstOut, Shader=skia.GradientShader.MakeRadial(
                    skia.Point(x, y), R, [T.cor_skia((0, 0, 0), 255 * forca), T.cor_skia((0, 0, 0), 150 * forca), T.cor_skia((0, 0, 0), 0)],
                    [0.0, 0.4, 1.0]))
                c.drawCircle(x, y, R, p)
            c.restore()
        self._luzes(c)

    def _banda(self, c, sup, chave, fn, faixa):
        cam = self.cam
        k = (self.cache_id, self.var, chave)
        ent = _BANDAS.get(k)
        if ent is not None:
            img, ref = ent
            m = _reprojeta(ref, cam, faixa)
            if m is not None:
                c.save()
                c.concat(m)
                c.drawImage(img, 0, 0)
                c.restore()
                return
        off = sup.makeSurface(W, H)
        if off is None:
            fn(c)
            return
        oc = off.getCanvas()
        oc.clear(skia.Color(0, 0, 0, 0))
        fn(oc)
        img = off.makeImageSnapshot()
        if len(_BANDAS) > 160:
            _BANDAS.clear()
        _BANDAS[k] = (img, _cam_tupla(cam))
        c.drawImage(img, 0, 0)

    def _luzes(self, c):
        for X, Y, Z, r, cor, forca, chao, _vivo, pisca in self.luzes:
            if pisca is not None:  # lâmpada de rua falhando: quase sempre acesa, às vezes dá umas piscadas
                janela_ = int(self.t * 8)
                falha = _n(pisca, janela_ // 6) > 0.72 and (janela_ % 3 == 0)
                forca = forca * (0.25 if falha else 0.92 + 0.08 * math.sin(self.t * 23 + pisca))
            x, y = self.cam.p(X, Y, Z)
            s = self.cam.escala(Z)
            f = self.fog(Z) * 0.5
            # halo quente + halação (franja avermelhada de filme em volta do ponto forte) + miolo quase branco
            c.drawCircle(x, y, r * s * 1.5, skia.Paint(AntiAlias=True, BlendMode=skia.BlendMode.kScreen, Shader=skia.GradientShader.MakeRadial(
                skia.Point(x, y), r * s * 1.5, [T.cor_skia((150, 54, 30), 0), T.cor_skia((150, 54, 30), 46 * forca), T.cor_skia((150, 54, 30), 0)],
                [0.0, 0.35, 1.0])))
            p = skia.Paint(AntiAlias=True, BlendMode=skia.BlendMode.kScreen, Shader=skia.GradientShader.MakeRadial(
                skia.Point(x, y), r * s, [T.cor_skia(cor, 170 * forca * (1 - f)), T.cor_skia(cor, 50 * forca), T.cor_skia(cor, 0)],
                [0.0, 0.25, 1.0]))
            c.drawCircle(x, y, r * s, p)
            c.drawCircle(x, y, max(2.0, r * s * 0.06), skia.Paint(AntiAlias=True, BlendMode=skia.BlendMode.kScreen, Color=T.cor_skia(
                (255, 236, 196), 220 * forca), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, max(1.0, r * s * 0.03))))
            if chao:
                gx, gy = self.cam.p(X, 0, Z)
                c.save()
                c.translate(gx, gy)
                c.scale(1.0, 0.22)
                c.drawCircle(0, 0, r * s * 0.8, skia.Paint(AntiAlias=True, BlendMode=skia.BlendMode.kScreen,
                                                           Shader=skia.GradientShader.MakeRadial(skia.Point(0, 0), r * s * 0.8,
                                                                                                 [T.cor_skia(cor, 70 * forca), T.cor_skia(cor, 0)])))
                c.restore()


# ---------------------------------------------------------------- céu, lua, nuvens, árvores

def lua_do_estilo(lua, r_lua):
    """Posição (frações da tela) e raio da lua no estilo do canal: espelhada para o outro lado e maior ou menor."""
    return (0.5 + T.LUA_LADO * (lua[0] - 0.5), lua[1]), r_lua * T.LUA_TAM


def _cor_ceu(cor):
    """Cor de céu -> papel da noite do canal pela claridade: escuro vira o papel escuro, meio vira o tom da noite,
    claro (horizonte) vira o papel de seda da distância."""
    r, g, b = T.rgb(cor)
    l = (0.3 * r + 0.59 * g + 0.11 * b) / 255
    if l < 0.16:
        return T.mistura(T.TINTA, T.PUXA, l / 0.16)
    return T.mistura(T.PUXA, NEVOA, min(1.0, (l - 0.16) / 0.3))


def ceu_noite(c, cena, lua=(0.78, 0.2), r_lua=70, cores=((18, 16, 24), (44, 40, 50), (92, 86, 84)), nuvens=True, horizonte=None):
    """Céu de papel: faixas de papel coladas uma sobre a outra (a de baixo mais clara), cada uma com a borda de cima
    cortada em ondas e a sombra dura na de trás; a lua é um disco de papel com as crateras de papel de seda."""
    cam = cena.cam
    hz = cam.hz if horizonte is None else horizonte
    cores = [_cor_ceu(k) for k in cores]
    lua, r_lua = lua_do_estilo(lua, r_lua)
    c.drawRect(skia.Rect.MakeLTRB(-400, -400, W + 400, hz + 400), T.tinta_paint(cores[0]))
    d = T.Desenho()
    n = 4
    for k in range(1, n + 1):
        u = k / n
        cor = T.mistura(cores[0], cores[1], min(1.0, u * 1.4)) if u < 0.75 else T.mistura(cores[1], cores[2], (u - 0.6) * 1.2)
        y0 = -200 + (hz + 200) * (0.18 + 0.82 * u ** 1.15)
        xs = np.linspace(-420, W + 420, 22)
        rnd = random.Random(300 + k)
        topo = [(x_, y0 - 40 * math.sin(x_ / (170 + 40 * k) + k * 1.7) - rnd.uniform(-6, 6)) for x_ in xs]
        pts = topo + [(W + 420, hz + 420), (-420, hz + 420)]
        T.peca(d, quina_ceu(pts), cor, 310 + k, sombra=1.6, fio=1.2)
    d.desenha(c)
    lx, ly = W * lua[0], H * lua[1]
    c.drawCircle(lx, ly, r_lua * 3.2, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
        skia.Point(lx, ly), r_lua * 3.2, [T.cor_skia(LUA, 70), T.cor_skia(LUA, 14), T.cor_skia(LUA, 0)], [0.0, 0.4, 1.0])))
    dl = T.Desenho()
    T.peca(dl, T.elipse(lx, ly, r_lua, r_lua, 64), LUA, 991, sombra=2.0)
    rnd = random.Random(5)
    for k in range(5):
        a, rr = rnd.uniform(0, 6.28), rnd.uniform(0, r_lua * 0.6)
        T.mancha(dl, T.elipse(lx + rr * math.cos(a), ly + rr * math.sin(a), rnd.uniform(7, 18), rnd.uniform(6, 14), 18),
                 T.escurece(LUA, 0.82), 150, semente=40 + k)
    dl.desenha(c)
    if nuvens:
        rnd = random.Random(17)
        dn = T.Desenho()
        for k in range(5):
            y = rnd.uniform(H * 0.05, hz * 0.7)
            x = (rnd.uniform(-300, W + 300) + (T.passo_stop(cena.t) / 12.0) * rnd.uniform(4, 10)) % (W + 600) - 300
            larg, alt = rnd.uniform(260, 480), rnd.uniform(60, 110)
            _nuvem(dn, x, y, larg, alt, rnd, 0, 2000 + k, T.mistura(cores[1], LUA, 0.22), cores[0], LUA, T.TINTA)
        dn.desenha(c)


def quina_ceu(pts):
    return np.asarray(pts, float)


def arvore_seca(cena, X, Z, alt=5.0, semente=1, galhos=5, inclina=0.0, grossura=1.0):
    """Árvore de papel: tronco e poucos galhos grossos em tiras recortadas (no máximo 3 níveis, nada de galhada fina),
    tudo numa peça só com a sombra dura; o vento mexe em degraus de stop motion."""
    rnd = random.Random(semente)
    t = T.passo_stop(cena.t) / 12.0
    segs = []
    galhos = min(galhos, 3)

    def ramo(x, y, ang, comp, larg, nivel):
        if nivel > galhos or comp < 0.25:
            return
        vento = 0.03 * math.sin(t * 0.9 + nivel + semente) * nivel
        pts = [(x, y)]
        a = ang
        for j in range(3):
            a += rnd.uniform(-0.22, 0.22) + vento * 0.3
            x, y = x + math.sin(a) * comp / 3, y + math.cos(a) * comp / 3
            pts.append((x, y))
        segs.append((pts, larg))
        for k in range(2 if nivel < 2 else rnd.choice((1, 2))):
            ramo(x, y, a + rnd.choice((-1, 1)) * rnd.uniform(0.45, 0.85), comp * rnd.uniform(0.55, 0.72), larg * 0.62, nivel + 1)

    ramo(0.0, 0.0, inclina, alt * 0.45, 1.0, 0)

    def fn(c):
        f = cena.fog(Z)
        s = cena.cam.escala(Z)
        bx, by = cena.cam.p(X, 0, Z)
        corpo = skia.Path()
        for k, (pts, larg) in enumerate(segs):
            scr = np.array([(bx + px * s, by - py * s) for px, py in pts])
            w = max(1.6, larg * 0.32 * s * grossura)
            corpo.addPath(T.traco_tinta(T.catmull(scr, False, 4), w, 0, semente * 100 + k, ponta=(0.0, 0.3)))
        sx, sy = T.sombra_px(min(1400.0, 160.0 * s))
        if T.com_sombra():
            c.drawPath(T.deslocado(corpo, sx, sy), skia.Paint(AntiAlias=True, Color=T.cor_sombra(1 - f)))
        cor = T.mistura(T.mistura(cena.tinta, T.APOIO, 0.3), cena.nevoa, f * 0.8)
        c.drawPath(corpo, T.tinta_paint(cor))
        c.drawPath(corpo, T.fibra_paint(semente, 0.4))
    cena.item(Z, fn)


def mato(cena, X, Z, larg=0.8, alt=0.6, semente=1, n=14, cor=(96, 86, 64), Y=0.0):
    """Tufo de mato seco: hastes finas e algumas folhas mortas."""
    rnd = random.Random(semente)
    hastes = []
    for k in range(n):
        x0 = rnd.uniform(-larg / 2, larg / 2)
        h = alt * rnd.uniform(0.4, 1.0)
        dobra = rnd.uniform(-0.25, 0.25)
        hastes.append((x0, h, dobra))

    def fn(c):
        f = cena.fog(Z)
        s = cena.cam.escala(Z)
        bx, by = cena.cam.p(X, Y, Z)
        vento = 0.05 * math.sin(cena.t * 1.4 + X)
        for k, (x0, h, dobra) in enumerate(hastes):
            pts = np.array([(bx + x0 * s, by), (bx + (x0 + (dobra + vento) * h * 0.5) * s, by - h * 0.55 * s),
                            (bx + (x0 + (dobra + vento) * 1.3 * h) * s, by - h * s)])
            c.drawPath(T.traco_tinta(T.catmull(pts, False, 5), max(0.6, 0.02 * s), cena.var, semente * 50 + k, amp=0.4, ponta=(0.0, 0.8)),
                       T.tinta_paint(T.mistura(T.mistura(cor, T.TINTA, 0.5), cena.nevoa, f), 230 * (1 - 0.7 * f)))
    cena.item(Z - 0.05, fn)


def rachadura(cena, origem, direcao, comp=1.0, semente=1, z=None):
    """Rachadura em zigue-zague num plano (direção 3D), com uma ramificação."""
    rnd = random.Random(semente)
    x, y, zz = origem
    dx, dy, dz = direcao
    pts = [(x, y, zz)]
    for k in range(6):
        d = comp / 6
        x += dx * d + rnd.uniform(-0.05, 0.05) * (1 - abs(dx))
        y += dy * d + rnd.uniform(-0.06, 0.06) * (1 - abs(dy))
        zz += dz * d + rnd.uniform(-0.05, 0.05) * (1 - abs(dz))
        pts.append((x, y, zz))
    cena.linha(pts, 0.35, z=z)
    b = pts[3]
    cena.linha([b, (b[0] + dx * comp * 0.3 + 0.08, b[1] + dy * comp * 0.3 - 0.1, b[2] + dz * comp * 0.3)], 0.25, z=z)


def tex_tijolo(face_pts, linhas=0.2, cols=0.4, alfa=110):
    """Textura de tijolo aparente num retângulo 3D [a, b, c, d] (a-b na base)."""
    a, b, c_, d = [np.array(p, float) for p in face_pts]

    def tex(c, cena, f):
        hgt = np.linalg.norm(d - a)
        nl = max(1, int(hgt / linhas))
        larg = np.linalg.norm(b - a)
        nc = max(1, int(larg / cols))
        pa = skia.Paint(AntiAlias=True, Color=T.cor_skia(T.TINTA, alfa * (1 - f)), Style=skia.Paint.kStroke_Style, StrokeWidth=0.9)
        path = skia.Path()
        for i in range(nl + 1):
            u = i / nl
            p0, p1 = a + (d - a) * u, b + (c_ - b) * u
            s0, s1 = cena.p(p0), cena.p(p1)
            path.moveTo(*s0)
            path.lineTo(*s1)
            if i < nl:
                off = 0.5 if i % 2 else 0.0
                for j in range(nc):
                    v = (j + off) / nc
                    q0 = p0 + (p1 - p0) * v
                    q1 = q0 + (d - a) / nl
                    path.moveTo(*cena.p(q0))
                    path.lineTo(*cena.p(q1))
        c.drawPath(path, pa)
    return tex


def tex_tabuas(face_pts, n=8, ao_longo=0, alfa=120, nos=True):
    """Tábuas (assoalho, porteira, cerca): n linhas paralelas ao lado `ao_longo` (0 = a-b)."""
    a, b, c_, d = [np.array(p, float) for p in face_pts]

    def tex(c, cena, f):
        pa = skia.Paint(AntiAlias=True, Color=T.cor_skia(T.TINTA, alfa * (1 - f)), Style=skia.Paint.kStroke_Style, StrokeWidth=1.0)
        path = skia.Path()
        rnd = random.Random(int(a[0] * 31 + a[2] * 17))
        for i in range(1, n):
            u = i / n
            if ao_longo == 0:
                p0, p1 = a + (d - a) * u, b + (c_ - b) * u
            else:
                p0, p1 = a + (b - a) * u, d + (c_ - d) * u
            path.moveTo(*cena.p(p0))
            path.lineTo(*cena.p(p1))
            if nos and rnd.random() < 0.5:
                v = rnd.uniform(0.2, 0.8)
                q = p0 + (p1 - p0) * v
                x, y = cena.p(q)
                path.addOval(skia.Rect.MakeXYWH(x - 3, y - 1.5, 6, 3))
        c.drawPath(path, pa)
    return tex


def tex_telhas(face_pts, linhas=0.28, alfa=150):
    """Telhado de telha colonial: fileiras com bordas onduladas (as bocas das telhas)."""
    a, b, c_, d = [np.array(p, float) for p in face_pts]

    def tex(c, cena, f):
        hgt = np.linalg.norm(d - a)
        nl = max(1, int(hgt / linhas))
        pa = skia.Paint(AntiAlias=True, Color=T.cor_skia(T.TINTA, alfa * (1 - f)), Style=skia.Paint.kStroke_Style, StrokeWidth=1.0)
        path = skia.Path()
        larg = np.linalg.norm(b - a)
        nc = max(2, int(larg / 0.22))
        for i in range(nl):
            u = i / nl
            p0, p1 = a + (d - a) * u, b + (c_ - b) * u
            path.moveTo(*cena.p(p0))
            for j in range(nc):
                v0, v1 = j / nc, (j + 1) / nc
                q0, q1 = p0 + (p1 - p0) * v0, p0 + (p1 - p0) * v1
                meio = (q0 + q1) / 2 + (d - a) / nl * 0.35
                m = cena.p(meio)
                e = cena.p(q1)
                path.quadTo(*m, *e)
            for j in range(0, nc, 1):
                q0 = p0 + (p1 - p0) * (j / nc)
                path.moveTo(*cena.p(q0))
                path.lineTo(*cena.p(q0 + (d - a) / nl))
        c.drawPath(path, pa)
    return tex


def janela(cena, pts, acesa=0.0, grade=True, cor_luz=LAMPADA, z=None):
    """Janela num plano (4 pontos 3D): escura ou com luz fraca, com grade de ferro."""
    pts = [tuple(p) for p in pts]
    cor = T.mistura((20, 18, 22), cor_luz, 0.55 * acesa)
    cena.face(pts, cor, contorno=0.9, hach=False, z=z, luz_extra=acesa)
    if acesa:
        X = np.mean([p[0] for p in pts])
        Y = np.mean([p[1] for p in pts])
        Z = np.mean([p[2] for p in pts])
        cena.luz(X, Y, Z, 1.6, cor_luz, 0.35 * acesa, chao=False)
    if grade:
        a, b, c_, d = [np.array(p, float) for p in pts]
        for k in range(1, 5):
            u = k / 5
            cena.linha([a + (b - a) * u, d + (c_ - d) * u], 0.35, z=(z if z is not None else float(a[2])) - 0.01)
        cena.linha([a + (d - a) * 0.5, b + (c_ - b) * 0.5], 0.35, z=(z if z is not None else float(a[2])) - 0.01)


def poste(cena, X, Z, alt=7.5, inclina=0.08, lado=1, acesa=1.0, semente=1):
    """Poste de concreto inclinado, com cruzeta, luminária e halo."""
    topo = (X + inclina * alt, alt, Z)
    w = 0.12
    cena.face([(X - w, 0, Z), (X + w, 0, Z), (topo[0] + w * 0.7, alt, Z), (topo[0] - w * 0.7, alt, Z)], (120, 116, 108), contorno=0.9, rim=True)
    cruz = [(topo[0] - 0.7, alt - 0.5, Z), (topo[0] + 0.7, alt - 0.38, Z)]
    cena.linha(cruz, 0.9)
    braco = [(topo[0], alt - 0.8, Z), (topo[0] - lado * 0.8, alt - 0.6, Z), (topo[0] - lado * 1.4, alt - 0.75, Z)]
    cena.linha(braco, 0.8)
    if acesa > 0:
        cena.luz(topo[0] - lado * 1.4, alt - 0.9, Z, 4.5, LAMPADA, acesa, pisca=semente)
    return topo


def fio(cena, a, b, barriga=0.6, k=0.45, n=14, vivo=False):
    pts = []
    for j in range(n + 1):
        u = j / n
        pts.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u - barriga * 4 * u * (1 - u), a[2] + (b[2] - a[2]) * u))
    cena.linha(pts, k, z=max(a[2], b[2]) - 0.3, vivo=vivo)


# ---------------------------------------------------------------- casa

def casa(cena, x0, x1, z0, z1, alt=2.9, cor=(150, 140, 120), telhado="duas", semente=1, frente_rua=1, acesa=0.0, lean=0.03,
         tijolo=0.3, laje_caixa=False, picho=0.35):
    """Casa térrea torta. frente_rua = +1 se a fachada é a face X=x1 (rua à direita), -1 se X=x0."""
    rnd = random.Random(semente)
    lean = lean * rnd.choice((-1, 1)) * rnd.uniform(0.5, 1.2)
    df = torto(lean=lean, sag=0.05, wob=0.025, semente=semente, base=((x0 + x1) / 2, 0, (z0 + z1) / 2))
    textura = None
    fx = x1 if frente_rua > 0 else x0
    fachada = [(fx, 0, z0), (fx, 0, z1), (fx, alt, z1), (fx, alt, z0)]
    if rnd.random() < tijolo:
        y0 = rnd.uniform(0.3, 1.0)
        za, zb = z0 + rnd.uniform(0.2, 1.5), z0 + rnd.uniform(2.0, 4.0)
        remendo = [df((fx + frente_rua * 0.01, y0, za)), df((fx + frente_rua * 0.01, y0, zb)), df((fx + frente_rua * 0.01, y0 + 1.0, zb)),
                   df((fx + frente_rua * 0.01, y0 + 1.2, za))]
    else:
        remendo = None
    V = cena.caixa(x0, x1, 0, alt, z0, z1, cor, deforma=df, topo=(telhado == "laje"),
                   textura_face=lambda pts: tex_parede(pts, semente, picho=picho, umidade=0.8, rachas=1))
    if alt > 5:  # janela do andar de cima, acima do muro
        zj2 = z0 + (z1 - z0) * rnd.uniform(0.3, 0.6)
        jan2 = [df((fx + frente_rua * 0.02, 3.6, zj2)), df((fx + frente_rua * 0.02, 3.6, zj2 + 1.0)),
                df((fx + frente_rua * 0.02, 4.7, zj2 + 1.0)), df((fx + frente_rua * 0.02, 4.7, zj2))]
        janela(cena, jan2, acesa=(acesa * 0.6), z=(z0 + z1) / 2 - 0.03)
    if remendo:
        cena.face(remendo, (136, 98, 78), contorno=0.5, hach=False, textura=tex_tijolo(remendo), z=(z0 + z1) / 2 - 0.02)
    # janela e porta na fachada
    zj = z0 + (z1 - z0) * rnd.uniform(0.2, 0.35)
    jan = [df((fx + frente_rua * 0.02, 1.0, zj)), df((fx + frente_rua * 0.02, 1.0, zj + 1.1)), df((fx + frente_rua * 0.02, 2.0, zj + 1.1)),
           df((fx + frente_rua * 0.02, 2.0, zj))]
    janela(cena, jan, acesa=acesa, z=(z0 + z1) / 2 - 0.03)
    zp = z0 + (z1 - z0) * 0.62
    porta = [df((fx + frente_rua * 0.02, 0, zp)), df((fx + frente_rua * 0.02, 0, zp + 0.9)), df((fx + frente_rua * 0.02, 2.1, zp + 0.9)),
             df((fx + frente_rua * 0.02, 2.1, zp))]
    cena.face(porta, (62, 52, 46), contorno=0.9, z=(z0 + z1) / 2 - 0.03, textura=tex_tabuas(porta, 5, ao_longo=1, nos=False))
    for k in range(2):
        rachadura(cena, df((fx + frente_rua * 0.02, alt - 0.1, z0 + rnd.uniform(0.3, z1 - z0 - 0.3))), (0, -1, rnd.uniform(-0.3, 0.3)),
                  rnd.uniform(0.6, 1.4), semente * 10 + k, z=(z0 + z1) / 2 - 0.04)
    if telhado == "duas":
        cume = alt + rnd.uniform(1.6, 2.6)
        xm = (x0 + x1) / 2
        ab = 0.35
        P = {k: df(v) for k, v in {"a": (x0 - ab, alt - 0.15, z0 - ab), "b": (x1 + ab, alt - 0.15, z0 - ab),
                                    "c": (xm, cume, z0 - ab), "e": (x0 - ab, alt - 0.15, z1 + ab), "f": (x1 + ab, alt - 0.15, z1 + ab),
                                    "g": (xm, cume, z1 + ab)}.items()}
        tel = (112, 76, 62)
        lado_vis = [P["b"], P["f"], P["g"], P["c"]] if cena.cam.x > xm else [P["a"], P["e"], P["g"], P["c"]]
        cena.face(lado_vis, tel, textura=tex_telhas(lado_vis), z=(z0 + z1) / 2 - 0.05, rim=True)
        if cena.cam.z < z0:
            cena.face([P["a"], P["b"], P["c"]], T.escurece(cor, 0.9), z=z0 - 0.06)
        cena.linha([P["c"], P["g"]], 1.2, z=(z0 + z1) / 2 - 0.06)
    elif laje_caixa:
        caixa_dagua(cena, (x0 + x1) / 2 + rnd.uniform(-1, 1), alt, (z0 + z1) / 2, semente=semente)
    if cena.cam.z < z0:
        andares = max(1, int(alt / 2.8))
        for a in range(andares):
            yb = a * 2.8
            n = max(1, int((x1 - x0) / 2.6))
            for j in range(n):
                if rnd.random() < 0.25:
                    continue
                xa = x0 + (x1 - x0) * (j + 0.5) / n - 0.5
                jan = [df((xa, yb + 1.0, z0 - 0.02)), df((xa + 1.0, yb + 1.0, z0 - 0.02)), df((xa + 1.0, yb + 2.0, z0 - 0.02)),
                       df((xa, yb + 2.0, z0 - 0.02))]
                janela(cena, jan, acesa=(acesa if (a + j) == 0 else 0.0), grade=rnd.random() < 0.7, z=z0 - 0.03)
        rachadura(cena, df((x0 + (x1 - x0) * rnd.uniform(0.2, 0.8), alt - 0.05, z0 - 0.02)), (rnd.uniform(-0.2, 0.2), -1, 0),
                  rnd.uniform(0.8, 1.8), semente * 7, z=z0 - 0.04)
    return V


def _tex_reboco(semente):
    """Reboco velho: manchas de umidade escorrendo e pontos de chapisco."""
    def tex(c, cena, f):
        r = c.getLocalClipBounds()
        rnd = random.Random(semente)
        for k in range(3):
            x = rnd.uniform(r.left(), r.right())
            w = rnd.uniform(0.06, 0.18) * r.width()
            c.drawRect(skia.Rect.MakeLTRB(x - w / 2, r.top(), x + w / 2, r.top() + r.height() * rnd.uniform(0.3, 0.8)), skia.Paint(
                AntiAlias=True, Shader=skia.GradientShader.MakeLinear([skia.Point(0, r.top()), skia.Point(0, r.bottom())],
                                                                      [T.cor_skia((30, 26, 22), 90 * (1 - f)), T.cor_skia((30, 26, 22), 0)]),
                MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, max(2.0, w * 0.3))))
        pts = skia.Path()
        for k in range(int(min(400, r.width() * r.height() / 900))):
            pts.addCircle(rnd.uniform(r.left(), r.right()), rnd.uniform(r.top(), r.bottom()), 0.8)
        c.drawPath(pts, T.tinta_paint(T.TINTA, 70 * (1 - f)))
    return tex


def caixa_dagua(cena, X, Y, Z, r=0.65, h=0.95, semente=1, cor=(132, 140, 142), n=14, tampa_torta=0.12):
    """Caixa d'água de fibra (cilindro com tampa torta), com a sombra escorrida."""
    lados = []
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        p = [(X + r * math.cos(a0), Y, Z + r * math.sin(a0)), (X + r * math.cos(a1), Y, Z + r * math.sin(a1)),
             (X + r * 0.92 * math.cos(a1), Y + h, Z + r * 0.92 * math.sin(a1)), (X + r * 0.92 * math.cos(a0), Y + h, Z + r * 0.92 * math.sin(a0))]
        frente = math.sin((a0 + a1) / 2) < 0.2
        if frente:
            lados.append(p)
    for p in lados:
        cena.face(p, cor, contorno=0.0, z=Z - 0.02)
    # contorno da silhueta e anéis
    sil = [(X - r, Y, Z), (X - r * 0.92, Y + h, Z)]
    cena.linha(sil, 1.0, z=Z - 0.03)
    cena.linha([(X + r, Y, Z), (X + r * 0.92, Y + h, Z)], 1.0, z=Z - 0.03)
    for yy in (Y + 0.02, Y + h * 0.5):
        rr = r * (1 - 0.08 * (yy - Y) / h)
        cena.linha([(X + rr * math.cos(a), yy, Z - rr * abs(math.sin(a))) for a in np.linspace(math.pi, 2 * math.pi, 9)], 0.6, z=Z - 0.03)
    tampa = [(X + r * 1.02 * math.cos(a), Y + h + tampa_torta * math.cos(a) * 0.5 + 0.06, Z + r * 1.02 * math.sin(a)) for a in
             np.linspace(0, 2 * math.pi, 18, endpoint=False)]
    cena.face(tampa, T.escurece(cor, 1.08), z=Z - 0.04, rim=True)
    cena.linha([(X + 0.1, Y + h + 0.06, Z - r * 0.6), (X + 0.3, Y + h * 0.4, Z - r * 0.95), (X + 0.28, Y + 0.1, Z - r)], 0.4, z=Z - 0.05,
               alfa=160)


# ---------------------------------------------------------------- cenas prontas

def muro(cena, x, z0, z1, alt=1.9, semente=1, portao=True, esp=0.18):
    rnd = random.Random(semente)
    df = torto(lean=rnd.uniform(-0.03, 0.03), wob=0.02, semente=semente, base=(x, 0, z0))
    x0, x1 = x - esp / 2, x + esp / 2
    zp = z0 + (z1 - z0) * rnd.uniform(0.25, 0.55)
    pedacos = [(z0, zp), (zp + 2.4, z1)] if portao else [(z0, z1)]
    cor = rnd.choice(((132, 126, 114), (118, 112, 104), (144, 134, 116)))
    for a, b in pedacos:
        if b - a < 0.2:
            continue
        V = cena.caixa(x0, x1, 0.16, alt, a, b, cor, deforma=df, rim=True,
                       textura_face=lambda pts, sm=semente * 13 + int(a): tex_parede(pts, sm, picho=0.55, umidade=0.9, rachas=1))
        lado = [V["b"], V["f"], V["g"], V["c"]] if cena.cam.x > x else [V["a"], V["e"], V["h"], V["d"]]
        if rnd.random() < 0.5:
            rachadura(cena, df((x1 if cena.cam.x > x else x0, alt - 0.05, (a + b) / 2)), (0, -1, 0.3), 1.0, semente * 3 + int(a), z=(a + b) / 2 - 0.05)
        if rnd.random() < 0.5:  # caco de vidro em cima do muro
            for j in range(int((b - a) / 0.35)):
                zz = a + 0.15 + j * 0.35
                cena.linha([df((x, alt, zz)), df((x, alt + 0.14, zz + 0.04)), df((x, alt, zz + 0.12))], 0.35, z=(a + b) / 2 - 0.06)
    if portao:
        pts = [df((x, 0.16, zp)), df((x, 0.16, zp + 2.4)), df((x, alt + 0.15, zp + 2.4)), df((x, alt + 0.15, zp))]
        a, b, c_, d = [np.array(p) for p in pts]
        for j in range(13):
            u = j / 12
            cena.linha([a + (b - a) * u, d + (c_ - d) * u + np.array([0, 0.12 * math.sin(u * 9), 0])], 0.45, z=(z0 + z1) / 2 - 0.05)
        cena.linha([a + (d - a) * 0.15, b + (c_ - b) * 0.15], 0.5, z=(z0 + z1) / 2 - 0.05)
        cena.linha([a + (d - a) * 0.85, b + (c_ - b) * 0.85], 0.5, z=(z0 + z1) / 2 - 0.05)


def _tex_asfalto():
    def tex(c, cena, f):
        rnd = random.Random(8)
        pa = skia.Paint(AntiAlias=True, Color=T.cor_skia(T.TINTA, 140 * (1 - f)), Style=skia.Paint.kStroke_Style, StrokeWidth=1.0)
        path = skia.Path()
        for k in range(26):  # rachaduras compridas no asfalto
            x, z = rnd.uniform(-3, 3), rnd.uniform(1.0, 40)
            path.moveTo(*cena.p((x, 0, z)))
            for j in range(5):
                x += rnd.uniform(-0.4, 0.4)
                z += rnd.uniform(0.2, 1.4)
                path.lineTo(*cena.p((x, 0, z)))
        for k in range(10):  # buracos
            x, z = rnd.uniform(-2.8, 2.8), rnd.uniform(2, 30)
            r = rnd.uniform(0.2, 0.5)
            pts = [cena.p((x + r * math.cos(a) * (0.8 + 0.3 * _n(k, a)), 0, z + r * 0.7 * math.sin(a))) for a in np.linspace(0, 6.28, 12)]
            hp = T.caminho(np.array(pts))
            c.drawPath(hp, T.tinta_paint((30, 28, 28), 160 * (1 - f)))
            c.drawPath(hp, pa)
        c.drawPath(path, pa)
        # faixa central apagada
        for z in np.arange(1.5, 60, 3.0):
            q = [cena.p((-0.06, 0.0, z)), cena.p((0.06, 0, z)), cena.p((0.06, 0, z + 1.2)), cena.p((-0.06, 0, z + 1.2))]
            c.drawPath(T.caminho(np.array(q)), T.tinta_paint((150, 146, 128), 70 * (1 - f)))
    return tex


def _tex_juntas(l):
    def tex(c, cena, f):
        pa = skia.Paint(AntiAlias=True, Color=T.cor_skia(T.TINTA, 110 * (1 - f)), Style=skia.Paint.kStroke_Style, StrokeWidth=0.9)
        path = skia.Path()
        for z in np.arange(1.0, 60, 1.4):
            path.moveTo(*cena.p((l * 3.4, 0.16, z)))
            path.lineTo(*cena.p((l * 5.4, 0.16, z + 0.05)))
        c.drawPath(path, pa)
    return tex


PORTA_X = (1.1, 2.0)          # porta no fundo, à direita da janela


def _quarto_fixo(cam, luz_lua=1.0, porta_abre=0.8):
    t = 0.0
    """Quarto à noite: paredes de papel listrado descascando, assoalho de tábuas, janela torta com a lua, cama com
    coberta, guarda-roupa entreaberto (fresta preta) e a porta da direita aberta pro escuro."""
    cena = Cena(cam, t, nevoa=(30, 28, 34), alcance=40.0, luz=(0.35, 0.5, -0.8), w_tinta=2.6)
    X0, X1, Y1, ZF = -2.3, 2.3, 2.75, 5.0
    df = torto(lean=0.02, wob=0.03, semente=4)
    parede, papel2 = (138, 126, 104), (124, 112, 96)
    piso = [df((X0, 0, -1)), df((X1, 0, -1)), df((X1, 0, ZF)), df((X0, 0, ZF))]
    cena.face(piso, (84, 66, 52), z=100, hach=False, textura=tex_tabuas(piso, 9, ao_longo=1))
    teto = [df((X0, Y1, -1)), df((X1, Y1, -1)), df((X1, Y1 + 0.1, ZF)), df((X0, Y1, ZF))]
    cena.face(teto, (70, 64, 60), z=100)
    fundo = [df((X0, 0, ZF)), df((X1, 0, ZF)), df((X1, Y1 + 0.1, ZF)), df((X0, Y1, ZF))]
    cena.face(fundo, parede, z=99, textura=_tex_listras(fundo, 14), hach=False)
    esq = [df((X0, 0, -1)), df((X0, 0, ZF)), df((X0, Y1, ZF)), df((X0, Y1, -1))]
    cena.face(esq, papel2, z=98, textura=_tex_listras(esq, 22, eixo=1))
    dir_ = [df((X1, 0, -1)), df((X1, 0, ZF)), df((X1, Y1 + 0.1, ZF)), df((X1, Y1, -1))]
    cena.face(dir_, papel2, z=98, textura=_tex_listras(dir_, 22, eixo=1))
    # rodapé e rachadura no teto
    cena.linha([df((X0, 0.12, ZF)), df((X1, 0.12, ZF))], 0.6, z=97)
    rachadura(cena, df((0.3, Y1, 1.2)), (0.4, 0, 1), 2.4, 5, z=97)
    rachadura(cena, df((X1, 2.2, 3.4)), (0, -1, -0.3), 1.0, 6, z=97)
    # papel de parede descascando (lasca triangular clara)
    for k, (zz, yy) in enumerate(((1.0, 2.2), (3.6, 1.6))):
        pts = [df((X0 + 0.01, yy, zz)), df((X0 + 0.01, yy + 0.25, zz + 0.2)), df((X0 + 0.12, yy - 0.03, zz + 0.28))]
        cena.face(pts, (112, 100, 84), contorno=0.6, z=97, hach=True)
    # janela no fundo com a lua
    jx0, jx1, jy0, jy1 = -1.25, 0.15, 1.0, 2.2
    jan = [df((jx0, jy0, ZF - 0.01)), df((jx1, jy0, ZF - 0.01)), df((jx1, jy1, ZF - 0.01)), df((jx0, jy1 + 0.08, ZF - 0.01))]

    def lado_de_fora(cc, cena_, f):
        x, y = cena_.p((-0.35, 1.9, ZF))
        cc.drawPaint(T.tinta_paint((52, 54, 66)))
        cc.drawCircle(x, y, 120, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
            skia.Point(x, y), 120, [T.cor_skia(LUA, 200), T.cor_skia(LUA, 0)])))
        cc.drawCircle(x, y, 26, T.tinta_paint(LUA))
        rnd = random.Random(3)
        for k in range(6):  # galhos pretos lá fora
            p = skia.Path()
            bx, by = cena_.p((jx0 + rnd.uniform(0, 1.5), jy0, ZF))
            p.moveTo(bx, by)
            for j in range(4):
                bx += rnd.uniform(-30, 30)
                by -= rnd.uniform(20, 40)
                p.lineTo(bx, by)
            cc.drawPath(p, skia.Paint(AntiAlias=True, Color=T.cor_skia(T.TINTA), Style=skia.Paint.kStroke_Style, StrokeWidth=3))
    cena.face(jan, (52, 54, 66), contorno=1.2, hach=False, z=96, textura=lado_de_fora)
    a, b, c_, d = [np.array(p) for p in jan]
    cena.linha([(a + b) / 2, (d + c_) / 2], 0.9, z=95.9)
    cena.linha([(a + d) / 2, (b + c_) / 2], 0.9, z=95.9)
    cena.luz(-0.55, 1.6, ZF - 0.2, 1.8, LUA, 0.5 * luz_lua, chao=False)
    # cortina rasgada
    for l, xx in ((-1, jx0), (1, jx1)):
        pts = [(xx - l * 0.05, jy1 + 0.25, ZF - 0.05), (xx + l * 0.35, jy1 + 0.25, ZF - 0.05),
               (xx + l * (0.2 + 0.05 * math.sin(t * 1.3)), 0.4, ZF - 0.08), (xx + l * 0.05, 0.3, ZF - 0.08), (xx - l * 0.1, 0.5, ZF - 0.08)]
        cena.face([df(p) for p in pts], (92, 84, 92), contorno=0.9, z=95.8)
    # feixe de luar no chão
    def feixe(cc):
        q = [cena.p(df((jx0 + 0.1, 0, ZF - 0.2))), cena.p(df((jx1 + 0.1, 0, ZF - 0.2))), cena.p(df((jx1 + 0.8, 0, 1.6))),
             cena.p(df((jx0 + 0.4, 0, 1.2)))]
        p = T.tinta_paint(LUA, 46 * luz_lua)
        p.setBlendMode(skia.BlendMode.kScreen)
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 14))
        cc.drawPath(T.caminho(np.array(q)), p)
    cena.item(90, feixe)
    # guarda-roupa encostado na parede da esquerda, porta entreaberta
    g = torto(lean=-0.04, wob=0.02, semente=9)
    V = cena.caixa(X0 + 0.02, X0 + 0.62, 0, 2.2, 2.9, 4.4, (84, 66, 54), deforma=g, textura=None)
    porta_g = [g((X0 + 0.63, 0.1, 2.95)), g((X0 + 0.63, 0.1, 3.62)), g((X0 + 0.63, 2.1, 3.62)), g((X0 + 0.63, 2.1, 2.95))]
    cena.face(porta_g, (92, 72, 58), z=3.4, textura=tex_tabuas(porta_g, 4, ao_longo=1))
    fresta = [g((X0 + 0.63, 0.1, 3.62)), g((X0 + 0.63, 0.1, 3.76)), g((X0 + 0.63, 2.1, 3.76)), g((X0 + 0.63, 2.1, 3.62))]
    cena.face(fresta, (4, 2, 4), contorno=0.5, z=3.39, hach=False)
    for k, yy in enumerate((0.9, 1.6)):  # puxadores
        cena.linha([g((X0 + 0.64, yy, 3.52)), g((X0 + 0.64, yy + 0.12, 3.52))], 0.8, z=3.38)
    # cama na direita, perto da câmera (dá profundidade)
    cama = torto(lean=0.0, wob=0.02, semente=12)
    BX0, BX1, BZ0, BZ1 = -2.28, -1.3, 0.2, 2.25        # cama de solteiro encostada na parede da esquerda
    cena.caixa(BX0, BX1, 0, 0.45, BZ0, BZ1, (78, 62, 52), deforma=cama)
    coberta = [cama((BX0 - 0.02, 0.5, BZ0 - 0.05)), cama((BX1 + 0.04, 0.5, BZ0 - 0.05)), cama((BX1 + 0.04, 0.62, BZ1)),
               cama((BX0 - 0.02, 0.6, BZ1))]
    cena.face(coberta, (104, 108, 116), z=BZ0 - 0.1, textura=tex_tabuas(coberta, 6, ao_longo=0, alfa=70, nos=False))
    cena.face([cama((BX1 + 0.04, 0.5, BZ0 - 0.05)), cama((BX1 + 0.04, 0.62, BZ1)), cama((BX1 + 0.04, 0.05, BZ1 + 0.05)),
               cama((BX1 + 0.04, 0.05, BZ0 - 0.1))], (92, 96, 104), z=BZ0 - 0.11)
    cena.face([cama((BX0 + 0.12, 0.62, BZ1 - 0.5)), cama((BX1 - 0.15, 0.62, BZ1 - 0.5)), cama((BX1 - 0.18, 0.82, BZ1 - 0.05)),
               cama((BX0 + 0.15, 0.8, BZ1 - 0.05))], (156, 150, 132), z=BZ0 - 0.09)
    cena.caixa(BX0, BX1, 0.4, 1.3, BZ1 - 0.02, BZ1 + 0.08, (66, 50, 44), deforma=cama)
    # criado-mudo e abajur apagado, no canto do fundo à direita
    cena.caixa(1.75, 2.27, 0, 0.6, 3.6, 4.1, (80, 64, 52), deforma=cama)
    cena.linha([(2.2, 0.6, 3.85), (2.2, 1.0, 3.85)], 0.7)
    cena.face([(2.05, 1.0, 3.85), (2.27, 1.0, 3.85), (2.25, 1.26, 3.85), (2.1, 1.26, 3.85)], (130, 118, 96), z=3.5)
    # retrato torto na parede da direita
    q = [(X1 - 0.02, 1.45, 1.9), (X1 - 0.02, 1.4, 2.45), (X1 - 0.02, 2.1, 2.5), (X1 - 0.02, 2.16, 1.95)]
    cena.face([df(p) for p in q], (60, 52, 46), contorno=1.0, z=95.5, textura=_tex_retrato())
    # porta no fundo, aberta pro corredor escuro (é por onde a ameaça entra); a folha abre pra dentro do quarto
    px0, px1 = PORTA_X
    vao = [df((px0, 0, ZF - 0.01)), df((px1, 0, ZF - 0.01)), df((px1, 2.1, ZF - 0.01)), df((px0, 2.1, ZF - 0.01))]
    cena.face(vao, (6, 4, 8), contorno=1.2, hach=False, z=96.9)
    ang = math.radians(20 + 62 * porta_abre)        # dobradiça no batente da direita: a folha não tampa o vão
    fx, fz = px1 + 0.88 * math.cos(ang), ZF - 0.88 * math.sin(ang)
    folha = [df((px1, 0, ZF)), df((fx, 0, fz)), df((fx, 2.1, fz)), df((px1, 2.1, ZF))]
    cena.face(folha, (96, 76, 60), textura=tex_tabuas(folha, 4, ao_longo=0, nos=False))
    cena.linha([df((px0 - 0.06, 2.16, ZF - 0.02)), df((px1 + 0.06, 2.16, ZF - 0.02))], 1.0, z=96.85)
    cena.vao_porta = [df((px0, 0, ZF)), df((px1, 0, ZF)), df((px1, 2.1, ZF)), df((px0, 2.1, ZF))]
    # lâmpada pendurada no fio, apagada, balançando de leve
    bal = 0.04 * math.sin(t * 1.1)
    cena.linha([df((0.2, Y1, 2.6)), (0.2 + bal * 0.5, 2.35, 2.6), (0.2 + bal, 2.12, 2.6)], 0.6)
    cena.face([(0.2 + bal - 0.07, 2.12, 2.6), (0.2 + bal + 0.07, 2.12, 2.6), (0.2 + bal + 0.05, 1.98, 2.6), (0.2 + bal, 1.95, 2.6),
               (0.2 + bal - 0.05, 1.98, 2.6)], (120, 116, 100), contorno=0.8, hach=True)
    # chinelo largado e roupa jogada no chão (primeiro plano)
    chinelo(cena, -0.95, 0.55, 0.5)
    roupa_chao(cena, 0.9, 0.7, semente=3)
    return cena


def quarto(c, t, cam=None, atores=(), luz_lua=1.0, porta_abre=0.8, roll=1.5, extras=None):
    """Quarto à noite: papel de parede listrado descascando, assoalho, janela torta com a lua, cama, guarda-roupa com
    fresta preta, criado-mudo, retrato de olhos furados, lâmpada pendurada, chinelo, roupa no chão e a porta do fundo
    aberta pro corredor escuro (`PORTA_X`, `cena.vao_porta`)."""
    cam = cam or Cam3D(x=-0.2, h=1.35, F=700, hz=820, cx=W / 2, z=-1.6)
    cena = _fixa("quarto", cam, t, _quarto_fixo, luz_lua=luz_lua, porta_abre=porta_abre)
    for X, Z, desenha, alt in atores:
        cena.ator(X, Z, desenha, alt, rim=0.4)
    cena.escuro(0.55, [(-0.55, 1.6, 5.0, 3.2, 0.9), (-0.2, 0.0, 2.6, 2.6, 0.75)])
    if extras:
        extras(cena)
    c.save()
    c.rotate(roll, W / 2, H / 2)
    c.drawPaint(T.tinta_paint((8, 6, 10)))
    cena.desenha(c)
    c.restore()
    return cena


def _tex_listras(face_pts, n=14, eixo=0, alfa=55):
    a, b, c_, d = [np.array(p, float) for p in face_pts]

    def tex(c, cena, f):
        pa = skia.Paint(AntiAlias=True, Color=T.cor_skia((40, 30, 36), alfa * (1 - f)), Style=skia.Paint.kStroke_Style, StrokeWidth=5)
        pa2 = skia.Paint(pa)
        pa2.setStrokeWidth(1.0)
        pa2.setColor(T.cor_skia(T.TINTA, 90 * (1 - f)))
        path, finos = skia.Path(), skia.Path()
        for i in range(1, n):
            u = i / n
            if eixo == 0:
                p0, p1 = a + (b - a) * u, d + (c_ - d) * u
            else:
                p0, p1 = a + (b - a) * u, d + (c_ - d) * u
            path.moveTo(*cena.p(p0))
            path.lineTo(*cena.p(p1))
            q0 = p0 + (b - a) / n * 0.5
            q1 = p1 + (c_ - d) / n * 0.5
            for k in range(8):  # florzinhas do papel de parede (pontinhos)
                v = (k + 0.5) / 8
                x, y = cena.p(q0 + (q1 - q0) * v)
                finos.addCircle(x, y, 1.6)
        c.drawPath(path, pa)
        c.drawPath(finos, pa2)
        # mancha de umidade descendo do teto
        x, y = cena.p(a + (b - a) * 0.6 + (d - a) * 0.95)
        c.drawOval(skia.Rect.MakeXYWH(x - 60, y - 10, 120, 160), skia.Paint(AntiAlias=True, Color=T.cor_skia((40, 34, 24), 70 * (1 - f)),
                                                                            MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 20)))
    return tex


def _tex_retrato():
    def tex(c, cena, f):
        r = c.getLocalClipBounds()
        cx, cy = r.centerX(), r.centerY()
        c.drawRect(r, T.tinta_paint((120, 112, 96)))
        d = T.Desenho()
        T.forma(d, T.elipse(cx, cy - r.height() * 0.08, r.width() * 0.22, r.height() * 0.2, 24), (150, 140, 120), cena.var, 77, contorno=1.4,
                sombra=0.6)
        T.forma(d, T.catmull([(cx - r.width() * 0.36, r.bottom()), (cx - r.width() * 0.2, cy + r.height() * 0.12),
                              (cx + r.width() * 0.2, cy + r.height() * 0.12), (cx + r.width() * 0.36, r.bottom())], True, 6), (60, 54, 52),
                cena.var, 78, contorno=1.4)
        d.desenha(c)
        # rosto riscado: os olhos foram arrancados da foto (dois furos pretos)
        for l in (-1, 1):
            c.drawCircle(cx + l * r.width() * 0.08, cy - r.height() * 0.1, r.width() * 0.04, T.tinta_paint((4, 2, 4)))
    return tex


def _tex_concreto(face_pts):
    a, b, c_, d = [np.array(p, float) for p in face_pts]

    def tex(c, cena, f):
        rnd = random.Random(4)
        for k in range(9):
            u, v = rnd.random(), rnd.random()
            p = a + (b - a) * u + (d - a) * v
            x, y = cena.p(p)
            s = cena.cam.escala(p[2])
            c.drawOval(skia.Rect.MakeXYWH(x - 0.35 * s, y - 0.08 * s, 0.7 * s, 0.16 * s), skia.Paint(
                AntiAlias=True, Color=T.cor_skia((40, 36, 32), 45 * (1 - f)), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 8)))
        for k in range(4):
            u = rnd.random()
            rachadura(cena, tuple(a + (b - a) * u + (d - a) * 0.05), (rnd.uniform(-0.3, 0.3), 0, 1), 2.5, 300 + k)
    return tex


def _tex_sulcos():
    def tex(c, cena, f):
        pa = skia.Paint(AntiAlias=True, Color=T.cor_skia(T.TINTA, 150 * (1 - f)), Style=skia.Paint.kStroke_Style, StrokeWidth=1.2)
        path = skia.Path()
        for x0 in (-1.2, -0.9, 0.9, 1.2):
            path.moveTo(*cena.p((x0, 0, 0.6)))
            for z in np.arange(1.0, 60, 1.0):
                path.lineTo(*cena.p((x0 * (1 - z / 200) + 0.06 * math.sin(z * 0.7), 0, z)))
        rnd = random.Random(2)
        for k in range(120):  # pedrinhas
            x, z = rnd.uniform(-2.2, 2.2), rnd.uniform(0.8, 25)
            px, py = cena.p((x, 0, z))
            s = cena.cam.escala(z) * 0.03
            path.addOval(skia.Rect.MakeXYWH(px - s, py - s * 0.5, 2 * s, s))
        for k in range(5):  # poças
            x, z = rnd.uniform(-1.5, 1.5), rnd.uniform(3, 18)
            pts = np.array([cena.p((x + 0.6 * math.cos(a), 0, z + 0.4 * math.sin(a))) for a in np.linspace(0, 6.28, 14)])
            c.drawPath(T.caminho(pts), T.tinta_paint(T.mistura((60, 62, 70), LUA, 0.15), 200 * (1 - f)))
        c.drawPath(path, pa)
    return tex


def _tex_capim(l):
    def tex(c, cena, f):
        rnd = random.Random(10 + l)
        path = skia.Path()
        for k in range(900):
            x, z = l * rnd.uniform(2.6, 40), rnd.uniform(0.8, 60)
            px, py = cena.p((x, 0, z))
            s = cena.cam.escala(z)
            h = s * rnd.uniform(0.15, 0.4)
            path.moveTo(px, py)
            path.lineTo(px + rnd.uniform(-0.3, 0.3) * h, py - h)
        fz = 0.5
        c.drawPath(path, skia.Paint(AntiAlias=True, Color=T.cor_skia(T.TINTA, 120 * (1 - f * fz)), Style=skia.Paint.kStroke_Style,
                                    StrokeWidth=1.0))
    return tex


# ================================================================ segunda rodada: cache, nuvens, parede, objetos

_CENAS = {}


def _fixa(nome, cam, t, fabrica, **kw):
    """Cena montada uma vez (a parte que não mexe) e reaproveitada: só troca câmera/tempo e recebe os itens vivos."""
    k = (nome,) + tuple(sorted(kw.items()))
    cena = _CENAS.get(k)
    if cena is None:
        cena = fabrica(cam, **kw)
        cena._k_fixo = cena.k
        cena.cache_id = k
        if len(_CENAS) > 12:
            _CENAS.clear()
        _CENAS[k] = cena
    cena.prepara(cam, t)
    cena.k = cena._k_fixo
    return cena


def _amostra(path, passo=6.0):
    """Pontos ao longo do caminho (primeiro contorno fechado)."""
    pm = skia.PathMeasure(path, True, 1.0)
    out = []
    while True:
        L = pm.getLength()
        if L > passo * 4:
            n = int(L / passo)
            for k in range(n):
                pos, _ = pm.getPosTan(L * k / n)
                out.append((pos.x(), pos.y()))
            break
        if not pm.nextContour():
            break
    return np.array(out) if out else None


def _nuvem(d, x, y, larg, alt, rnd, var, sid, cor, escura, clara, tinta):
    """Nuvem de papel: as bolas juntas viram uma peça só, recortada, com uma segunda peça mais clara colada por
    cima (o lado que pega a lua) e a sombra dura da peça no céu."""
    circ = []
    n = max(4, int(larg / (alt * 0.55)))
    for i in range(n):
        u = i / (n - 1)
        r = alt * (0.28 + 0.42 * math.sin(math.pi * u) ** 0.7) * rnd.uniform(0.8, 1.2)
        circ.append((x + larg * u + rnd.uniform(-8, 8), y - r * 0.5, r))
    for i in range(max(2, n // 2)):
        u = rnd.uniform(0.2, 0.75)
        r = alt * rnd.uniform(0.3, 0.52)
        circ.append((x + larg * u, y - alt * 0.42 - r * 0.25, r))
    path = None
    for cx, cy, r in circ:
        p = skia.Path()
        p.addCircle(cx, cy, r)
        path = p if path is None else skia.Op(path, p, skia.PathOp.kUnion_PathOp)
    corte = skia.Path()
    corte.addRect(x - larg, y - alt * 4, x + larg * 2, y + alt * 0.1)
    path = skia.Op(path, corte, skia.PathOp.kIntersect_PathOp)
    pts = _amostra(path, 7.0)
    if pts is None:
        return
    fill = T.peca(d, pts, cor, sid, sombra=1.4)
    # a peça clara de cima: a mesma nuvem um pouco menor e mais alta, recortada pela de baixo
    cx0, cy0 = pts.mean(axis=0)
    topo = (pts - (cx0, cy0)) * 0.86 + (cx0 - alt * 0.06, cy0 - alt * 0.16)
    sub = T.Desenho()
    T.peca(sub, topo, T.mistura(cor, clara, 0.35), sid + 1, sombra=0.6)
    d.recorte(fill, sub)


def nuvens(c, cena, cores=((40, 44, 56), (22, 24, 32), (120, 122, 126)), n=7, semente=17, faixa=(0.03, 0.4), vel=7.0):
    """Camada de nuvens de papel em 2 planos: as de longe menores e apagadas, as de perto grandes. Montada uma vez
    (cache) e empurrada devagar, em degraus de stop motion."""
    LW = 2 * W
    cores = [_cor_ceu(k) for k in cores]
    chave = ("nuvens", getattr(cena, "cache_id", None), cena.var, semente, n)
    ent = _BANDAS.get(chave)
    sup = c.getSurface()
    if ent is None:
        d = T.Desenho()
        rnd = random.Random(semente)
        base, esc, clara = cores
        for plano, (k_n, k_esc, k_tam) in enumerate(((0.6, 0.55, 0.6), (0.4, 1.0, 1.0))):
            for i in range(int(n * k_n) + 1):
                larg = rnd.uniform(260, 520) * k_tam
                alt = rnd.uniform(70, 120) * k_tam
                x = rnd.uniform(0, LW - larg - 40)
                y = H * rnd.uniform(*faixa) + (60 if plano == 0 else 0)
                cor = T.mistura(base, cena.nevoa, 0.4 * (1 - k_esc))
                _nuvem(d, x, y, larg, alt, rnd, cena.var, semente * 100 + plano * 30 + i, cor, T.mistura(esc, cor, 0.3 * (1 - k_esc)),
                       clara, T.mistura(T.TINTA, cor, 0.35 * (1 - k_esc)))
        off = sup.makeSurface(LW, H) if sup is not None else None
        if off is None:
            img = None
        else:
            oc = off.getCanvas()
            oc.clear(skia.Color(0, 0, 0, 0))
            d.desenha(oc)
            img = off.makeImageSnapshot()
        ent = (img, d)
        _BANDAS[chave] = ent
    img, d = ent
    dx = (T.passo_stop(cena.t) / 12.0 * vel) % LW
    for ox in (-dx, LW - dx):
        if img is not None:
            c.drawImage(img, ox, 0)
        else:
            c.save()
            c.translate(ox, 0)
            d.desenha(c)
            c.restore()


def _letra(rnd):
    """Um "garrancho" de pichação: traço de letra inventada (zigue-zague, laço, perna comprida)."""
    tipo = rnd.randrange(5)
    if tipo == 0:
        return [(0, 1), (0.2, 0), (0.5, 0.8), (0.8, 0), (1, 1)]
    if tipo == 1:
        return [(0.1, 1), (0.1, 0), (0.8, 0.1), (0.85, 0.45), (0.1, 0.55), (0.9, 1)]
    if tipo == 2:
        return [(0.9, 0.1), (0.2, 0.05), (0.05, 0.5), (0.3, 1), (0.9, 0.9), (0.6, 0.55)]
    if tipo == 3:
        return [(0, 0), (1, 0), (0.5, 0), (0.45, 1.15)]
    return [(0.05, 1), (0.5, 0), (0.95, 1), (0.25, 0.6), (0.8, 0.6)]


def tex_parede(face_pts, semente=1, picho=0.6, umidade=0.8, rachas=2, reboco=True):
    """Parede de rua: reboco manchado com chapisco, mancha de umidade subindo do chão (com a marca d'água), pichação
    apagada (garranchos de letras inventadas, com escorrido) e rachaduras. Tudo preso no plano da face."""
    A, B, C_, D = [np.array(p, float) for p in face_pts]

    def P(u, v):
        return (A + (B - A) * u) * (1 - v) + (D + (C_ - D) * u) * v

    def tex(c, cena, f):
        rnd = random.Random(semente)
        k = 1 - f
        if k < 0.08:
            return
        hgt = np.linalg.norm(D - A)
        if reboco:
            for i in range(5):
                u, v = rnd.random(), rnd.uniform(0.2, 1.0)
                q = P(u, v)
                x, y = cena.p(q)
                s_ = cena.cam.escala(q[2])
                c.drawOval(skia.Rect.MakeXYWH(x - 0.4 * s_, y - 0.25 * s_, 0.8 * s_, 0.5 * s_), skia.Paint(
                    AntiAlias=True, Color=T.cor_skia((40, 36, 30), 34 * k), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 0.2 * s_ + 1)))
            pontos = skia.Path()
            for i in range(140):
                x, y = cena.p(P(rnd.random(), rnd.random()))
                pontos.addCircle(x, y, 0.9)
            c.drawPath(pontos, T.tinta_paint(T.TINTA, 70 * k))
        if umidade and rnd.random() < umidade:
            alt_u = min(0.6, 0.55 / max(0.6, hgt)) * rnd.uniform(0.6, 1.0)
            topo = [P(u, alt_u * (0.7 + 0.5 * abs(math.sin(u * 9 + semente)))) for u in np.linspace(0, 1, 16)]
            base = [P(u, 0) for u in np.linspace(1, 0, 4)]
            scr = np.array([cena.p(q) for q in topo + base])
            p = T.tinta_paint((30, 30, 24), 120 * k)
            p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 5))
            c.drawPath(T.caminho(scr), p)
            c.drawPath(T.traco_tinta(np.array([cena.p(q) for q in topo]), 1.4, cena.var, semente + 3, amp=0.6),
                       T.tinta_paint((26, 22, 18), 140 * k))
        if rnd.random() < picho:
            cor = rnd.choice(((96, 40, 40), (40, 40, 60), (36, 34, 34), (90, 92, 100)))
            u0, v0 = rnd.uniform(0.1, 0.45), rnd.uniform(0.35, 0.6)
            n = rnd.randint(4, 7)
            alt_l = min(0.35, 0.55 / max(0.6, hgt))
            larg_l = alt_l * 0.6 * hgt / max(0.5, np.linalg.norm(B - A))
            esp = max(1.2, 0.035 * cena.cam.escala(P(u0, v0)[2]))
            for i in range(n):
                pts = [P(u0 + (i + x_ * 0.9) * larg_l, v0 + (1 - y_) * alt_l + rnd.uniform(-0.01, 0.01)) for x_, y_ in _letra(rnd)]
                scr = np.array([cena.p(q) for q in pts])
                c.drawPath(T.traco_tinta(T.catmull(scr, False, 5), esp, cena.var, semente * 31 + i, amp=0.5, ponta=(0.05, 0.3)),
                           T.tinta_paint(cor, 150 * k))
                if rnd.random() < 0.5:  # escorrido
                    q0 = P(u0 + (i + 0.5) * larg_l, v0)
                    q1 = P(u0 + (i + 0.5) * larg_l, v0 - rnd.uniform(0.04, 0.12))
                    c.drawPath(T.traco_tinta(np.array([cena.p(q0), cena.p(q1)]), esp * 0.4, cena.var, semente * 37 + i, ponta=(0.0, 0.6)),
                               T.tinta_paint(cor, 130 * k))
            q0, q1 = P(u0 - 0.02, v0 - 0.03), P(u0 + n * larg_l + 0.02, v0 - 0.01)   # sublinhado
            c.drawPath(T.traco_tinta(T.catmull(np.array([cena.p(q0), cena.p(P((u0 + u0 + n * larg_l) / 2, v0 - 0.06)), cena.p(q1)]), False, 6),
                                     esp * 0.7, cena.var, semente * 41, ponta=(0.1, 0.5)), T.tinta_paint(cor, 120 * k))
        for i in range(rachas):
            u, v = rnd.uniform(0.1, 0.9), rnd.uniform(0.6, 0.98)
            pts = [P(u, v)]
            for j in range(6):
                u += rnd.uniform(-0.04, 0.04)
                v -= rnd.uniform(0.04, 0.1)
                pts.append(P(u, max(0.0, v)))
            scr = np.array([cena.p(q) for q in pts])
            c.drawPath(T.traco_tinta(scr, 1.3, cena.var, semente * 43 + i, amp=0.3, ponta=(0.3, 0.6)), T.tinta_paint(T.TINTA, 200 * k))
    return tex


# ---------------------------------------------------------------- objetos de primeiro plano

def _cilindro(cena, X, Y, Z, r0, r1, h, cor, n=12, tampa=True, vivo=False):
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        if math.sin((a0 + a1) / 2) > 0.25:
            continue
        cena.face([(X + r0 * math.cos(a0), Y, Z + r0 * math.sin(a0)), (X + r0 * math.cos(a1), Y, Z + r0 * math.sin(a1)),
                   (X + r1 * math.cos(a1), Y + h, Z + r1 * math.sin(a1)), (X + r1 * math.cos(a0), Y + h, Z + r1 * math.sin(a0))], cor,
                  contorno=0.0, z=Z - 0.01, vivo=vivo)
    cena.linha([(X - r0, Y, Z), (X - r1, Y + h, Z)], 0.9, z=Z - 0.02, vivo=vivo)
    cena.linha([(X + r0, Y, Z), (X + r1, Y + h, Z)], 0.9, z=Z - 0.02, vivo=vivo)
    cena.linha([(X + r0 * math.cos(a), Y, Z + r0 * math.sin(a)) for a in np.linspace(0, -math.pi, 10)], 0.8, z=Z - 0.02, vivo=vivo)
    if tampa:
        cena.face([(X + r1 * math.cos(a), Y + h, Z + r1 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 16, endpoint=False)],
                  T.escurece(cor, 0.7), contorno=0.8, z=Z - 0.03, hach=False, vivo=vivo)


def balde(cena, X, Z, Y=0.0, r=0.16, h=0.3, cor=(70, 84, 96)):
    """Balde de plástico com alça."""
    _cilindro(cena, X, Y, Z, r * 0.8, r, h, cor)
    cena.linha([(X - r, Y + h, Z), (X - r * 0.4, Y + h + 0.16, Z - 0.02), (X + r * 0.4, Y + h + 0.16, Z - 0.02), (X + r, Y + h, Z)], 0.6,
               z=Z - 0.04)


def vaso_seco(cena, X, Z, Y=0.0, r=0.17, semente=1):
    """Vaso de barro rachado com planta morta."""
    _cilindro(cena, X, Y, Z, r * 0.75, r, r * 1.5, (120, 84, 66), tampa=False)
    rachadura(cena, (X - r * 0.3, Y + r * 1.4, Z - r * 0.9), (0.1, -1, 0), r * 1.2, semente, z=Z - 0.05)
    mato(cena, X, Z - 0.05, larg=r * 1.4, alt=0.55, semente=semente, n=12, cor=(110, 96, 66), Y=Y + r * 1.5)


def chinelo(cena, X, Z, ang=0.3, cor=(118, 112, 102)):
    """Par de chinelos de dedo largado no chão."""
    for k, (dx, dz, da) in enumerate(((0.0, 0.0, 0.0), (0.16, 0.12, 0.5))):
        a = ang + da
        ca, sa = math.cos(a), math.sin(a)
        x0, z0 = X + dx, Z + dz
        sola = []
        for t_ in np.linspace(0, 2 * math.pi, 14, endpoint=False):
            u, v = 0.13 * math.cos(t_) * (1 + 0.15 * math.sin(t_)), 0.05 * math.sin(t_) * (1.1 if math.cos(t_) > 0 else 0.85)
            sola.append((x0 + u * ca - v * sa, 0.012, z0 + u * sa + v * ca))
        cena.face(sola, cor, contorno=0.7, hach=False, z=z0 - 0.01)
        frente = (x0 + 0.08 * ca, 0.02, z0 + 0.08 * sa)
        for s_ in (-1, 1):
            cena.linha([frente, (x0 - 0.02 * ca - s_ * 0.045 * sa, 0.04, z0 - 0.02 * sa + s_ * 0.045 * ca)], 0.7, z=z0 - 0.02,
                       cor=(50, 54, 70))


def roupa_chao(cena, X, Z, semente=1, cor=(92, 90, 104)):
    """Camiseta largada no chão, com dobras."""
    rnd = random.Random(semente)
    pts = []
    for k in range(12):
        a = 2 * math.pi * k / 12
        r = rnd.uniform(0.18, 0.34)
        pts.append((X + r * math.cos(a), 0.015, Z + r * 0.7 * math.sin(a)))
    cena.face(pts, cor, contorno=0.8, z=Z - 0.01)
    for k in range(3):
        a = rnd.uniform(0, 6.28)
        cena.linha([(X + 0.05 * math.cos(a), 0.02, Z + 0.05 * math.sin(a)), (X + 0.22 * math.cos(a + 0.3), 0.02, Z + 0.15 * math.sin(a + 0.3))],
                   0.4, z=Z - 0.02)


def bicicleta(cena, X, Z, ang=math.pi / 2, inclina=0.22, cor=(64, 58, 56)):
    """Bicicleta velha encostada (no plano vertical que passa por X, Z na direção `ang`, tombada `inclina`)."""
    ca, sa = math.cos(ang), math.sin(ang)

    def P(s_, y):
        return (X + ca * s_ + sa * y * inclina, y, Z + sa * s_ - ca * y * inclina)
    R = 0.33
    for cxr in (-0.52, 0.52):
        aro = [P(cxr + R * math.cos(a), R + R * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 26)]
        cena.linha(aro, 1.5, z=Z - 0.1)
        cena.linha([P(cxr + R * 0.86 * math.cos(a), R + R * 0.86 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 22)], 0.5, z=Z - 0.1)
        for k in range(8):
            a = math.pi * k / 4
            cena.linha([P(cxr, R), P(cxr + R * 0.86 * math.cos(a), R + R * 0.86 * math.sin(a))], 0.25, z=Z - 0.1, alfa=170)
    eixo_t, sel, guid, eixo_f, pedal = P(-0.52, R), P(-0.16, 0.86), P(0.36, 0.96), P(0.52, R), P(0.0, R * 0.85)
    for a, b in ((eixo_t, pedal), (pedal, sel), (sel, eixo_t), (pedal, guid), (sel, P(0.33, 0.86)), (guid, eixo_f)):
        cena.linha([a, b], 1.1, z=Z - 0.11, cor=cor)
    cena.linha([P(-0.26, 0.9), P(-0.04, 0.92)], 2.0, z=Z - 0.12)                     # selim
    cena.linha([P(0.3, 1.04), P(0.46, 1.0), P(0.42, 1.06)], 0.9, z=Z - 0.12)          # guidão
    cena.linha([pedal, P(0.12, R * 0.6)], 0.8, z=Z - 0.12)


def entulho(cena, X, Z, larg=1.3, semente=1):
    """Monte de entulho: caco de bloco, tijolo, pedaço de reboco e ferro torto."""
    rnd = random.Random(semente)
    for k in range(9):
        x = X + rnd.uniform(-larg / 2, larg / 2)
        z = Z + rnd.uniform(-0.3, 0.3)
        w, h, dd = rnd.uniform(0.15, 0.4), rnd.uniform(0.08, 0.22), rnd.uniform(0.12, 0.3)
        y = max(0.0, 0.25 * (1 - abs(x - X) / (larg / 2))) * rnd.random()
        cor = rnd.choice(((130, 120, 110), (140, 92, 76), (110, 106, 100)))
        cena.caixa(x, x + w, y, y + h, z, z + dd, cor, deforma=torto(rot=rnd.uniform(-0.6, 0.6), wob=0.03, semente=semente * 10 + k,
                                                                    base=(x, y, z)))
    for k in range(2):
        x = X + rnd.uniform(-larg / 3, larg / 3)
        cena.linha([(x, 0.1, Z), (x + 0.15, 0.45, Z - 0.05), (x + 0.4, 0.55, Z - 0.1)], 0.5, z=Z - 0.4, cor=(110, 70, 50))
    mato(cena, X + larg * 0.4, Z - 0.2, larg=0.5, alt=0.4, semente=semente + 5, n=8)


def fio_caido(cena, topo, X, Z):
    """Fio que caiu do poste: desce em curva e enrola no chão."""
    pts = []
    for k in range(13):
        u = k / 12
        pts.append((topo[0] + (X - topo[0]) * u, topo[1] * (1 - u) ** 1.6, topo[2] + (Z - topo[2]) * u))
    cena.linha(pts, 0.5, z=Z - 0.2)
    rolo = [(X + 0.25 * math.cos(a) * (1 - a / 30), 0.01, Z + 0.15 * math.sin(a) * (1 - a / 30)) for a in np.linspace(0, 4 * math.pi, 30)]
    cena.linha(rolo, 0.45, z=Z - 0.21)


def cadeira_plastico(cena, X, Z, Y=0.0, ang=0.4, cor=(176, 170, 156)):
    """Cadeira de plástico (monobloco) encardida, virada `ang`."""
    ca, sa = math.cos(ang), math.sin(ang)

    def P(x, y, z):
        return (X + x * ca - z * sa, Y + y, Z + x * sa + z * ca)
    assento = [P(-0.22, 0.42, -0.2), P(0.22, 0.42, -0.2), P(0.22, 0.44, 0.2), P(-0.22, 0.44, 0.2)]
    encosto = [P(-0.22, 0.44, 0.2), P(0.22, 0.44, 0.2), P(0.25, 0.88, 0.28), P(-0.25, 0.88, 0.28)]
    for (x, z) in ((-0.2, -0.18), (0.2, -0.18), (-0.2, 0.18), (0.2, 0.18)):
        cena.linha([P(x * 1.15, 0.0, z * 1.15), P(x, 0.42, z)], 1.4, z=Z + z * ca, cor=T.escurece(cor, 0.8))
    cena.face(encosto, T.escurece(cor, 0.92), z=Z + 0.2, textura=_tex_ripas(encosto))
    cena.face(assento, cor, z=Z - 0.05)
    mancha = [P(-0.1, 0.441, -0.05), P(0.08, 0.441, -0.1), P(0.12, 0.441, 0.08)]
    cena.face(mancha, (120, 112, 96), contorno=0.0, hach=False, z=Z - 0.06)


def _tex_ripas(face_pts):
    A, B, C_, D = [np.array(p, float) for p in face_pts]

    def tex(c, cena, f):
        pa = skia.Paint(AntiAlias=True, Color=T.cor_skia(T.TINTA, 150 * (1 - f)), Style=skia.Paint.kStroke_Style, StrokeWidth=2.2)
        for k in range(1, 5):
            u = k / 5
            a, b = A + (B - A) * u, D + (C_ - D) * u
            pa_, pb_ = cena.p(a + (b - a) * 0.25), cena.p(a + (b - a) * 0.85)
            c.drawLine(pa_[0], pa_[1], pb_[0], pb_[1], pa)
    return tex


def vergalhoes(cena, X, Y, Z, n=4, alt=0.7, semente=1):
    """Ferro de coluna saindo da laje (a obra que nunca acabou), meio torto e enferrujado."""
    rnd = random.Random(semente)
    for k in range(n):
        x, z = X + (k % 2) * 0.16 - 0.08, Z + (k // 2) * 0.16 - 0.08
        dob = rnd.uniform(-0.15, 0.15)
        cena.linha([(x, Y, z), (x + dob * 0.3, Y + alt * 0.6, z), (x + dob, Y + alt * rnd.uniform(0.85, 1.05), z + dob * 0.5)], 0.55, z=Z - 0.02,
                   cor=(116, 72, 52))


def mangueira(cena, X, Z, Y=0.0, voltas=3):
    pts = [(X + (0.12 + 0.05 * a) * math.cos(a * 2 * math.pi / 6), Y + 0.02, Z + (0.08 + 0.03 * a) * math.sin(a * 2 * math.pi / 6))
           for a in np.linspace(0, voltas * 6, voltas * 18)]
    cena.linha(pts, 1.3, z=Z - 0.02, cor=(60, 80, 70))


def tijolos(cena, X, Z, Y=0.0, n=6, semente=1):
    rnd = random.Random(semente)
    for k in range(n):
        x = X + (k % 3) * 0.2 + rnd.uniform(-0.02, 0.02)
        y = Y + (k // 3) * 0.09
        cena.caixa(x, x + 0.19, y, y + 0.09, Z, Z + 0.14, (150, 96, 76), deforma=torto(rot=rnd.uniform(-0.1, 0.1), wob=0.01,
                                                                                         semente=semente + k, base=(x, y, Z)),
                   textura_face=lambda pts: tex_tijolo(pts, 0.03, 0.06, 90))


# ---------------------------------------------------------------- cenas prontas (segunda rodada)

def _rua_fixa(cam, lua=(0.76, 0.16)):
    cena = Cena(cam, 0.0, nevoa=(46, 52, 62), alcance=60.0, luz=(-0.5, 0.6, -0.35))
    rnd = random.Random(3)
    cena.face([(-3.0, 0, 0.3), (3.0, 0, 0.3), (3.0, 0, 120), (-3.0, 0, 120)], (64, 62, 62), hach=False, z=200, textura=_tex_asfalto())
    for l in (-1, 1):
        cena.face([(l * 3.0, 0.0, 0.3), (l * 3.0, 0.16, 0.3), (l * 3.0, 0.16, 120), (l * 3.0, 0.0, 120)], (116, 114, 108), z=199, hach=False)
        cena.face([(l * 3.0, 0.16, 0.3), (l * 4.5, 0.16, 0.3), (l * 4.5, 0.16, 120), (l * 3.0, 0.16, 120)], (92, 90, 88), z=199.5,
                  hach=False, textura=_tex_juntas(l))
    z, k = 1.2, 0
    tons = [(146, 136, 118), (126, 132, 124), (138, 120, 126), (152, 146, 128), (116, 120, 126), (144, 126, 110)]
    while z < 70:
        for l in (-1, 1):
            comp = rnd.uniform(7.5, 10.5)
            xc0, xc1 = (l * 6.0, l * 12.0) if l > 0 else (l * 12.0, l * 6.0)
            alt = rnd.choice((3.0, 3.2, 5.8, 6.2, 8.6))
            casa(cena, min(xc0, xc1), max(xc0, xc1), z + 0.4, z + comp - 0.4, alt=alt, cor=tons[k % len(tons)], semente=k + 1, picho=0.9,
                 frente_rua=-l, acesa=(0.9 if k in (2, 5, 8, 11) else 0.0), telhado=("duas" if alt < 5 and rnd.random() < 0.7 else "laje"),
                 laje_caixa=True, lean=0.06)
            muro(cena, l * 4.6, z, z + comp, alt=rnd.uniform(1.7, 2.2), semente=k + 50, portao=True)
            if rnd.random() < 0.6:
                mato(cena, l * 4.35, z + rnd.uniform(1, comp - 1), larg=1.0, alt=0.7, semente=k + 90)
            k += 1
        z += comp
    tops = []
    for j, zp in enumerate((6.0, 18.0, 30.0, 42.0, 54.0)):
        l = 1 if j % 2 == 0 else -1
        inc = l * (0.03 + 0.04 * (j % 3))
        tops.append(poste(cena, l * 4.1, zp, inclina=inc, lado=l, semente=j, acesa=(0.0 if j == 2 else 1.0)))
    for a, b in zip(tops[:-1], tops[1:]):
        fio(cena, a, b, barriga=0.9)
        fio(cena, (a[0], a[1] - 0.3, a[2]), (b[0], b[1] - 0.3, b[2]), barriga=1.1, k=0.35)
    arvore_seca(cena, -3.8, 10.0, alt=6.5, semente=7, inclina=0.12)
    arvore_seca(cena, 3.9, 34.0, alt=5.0, semente=11, inclina=-0.1)
    # primeiro plano: entulho na sarjeta, bicicleta no muro, balde, chinelo, fio caído do poste, mato, vaso seco
    # (perto da câmera só cabe o que está perto do meio: em Z=1,5 a tela vê ~1,3 m pra cada lado)
    entulho(cena, -1.2, 2.9, larg=1.5, semente=4)
    bicicleta(cena, 2.3, 3.1, ang=math.pi / 2 + 0.5, inclina=0.12)
    balde(cena, 1.5, 1.75)
    chinelo(cena, 0.45, 1.3, 0.4)
    poca = [(0.4, 0.004, 1.9), (1.3, 0.004, 1.8), (1.6, 0.004, 2.3), (0.9, 0.004, 2.6), (0.3, 0.004, 2.3)]
    cena.face(poca, (60, 66, 80), contorno=0.5, hach=False, z=150, luz_extra=0.6)
    fio_caido(cena, tops[0], 0.9, 2.6)
    mato(cena, 0.0, 1.05, larg=0.7, alt=0.55, semente=61, n=18)
    mato(cena, 1.75, 1.2, larg=0.6, alt=0.6, semente=62, n=16)
    vaso_seco(cena, -1.9, 3.6, semente=63)
    for zn, al in ((9.0, 0.12), (18.0, 0.17), (30.0, 0.22), (46.0, 0.3)):
        cena.neblina(zn, altura=1.1, alfa=al)
    return cena


def rua(c, t, cam=None, atores=(), roll=-2.0, lua=(0.76, 0.16), extras=None):
    """Rua de bairro à noite (câmera baixa): casas tortas e sobrados, muros com reboco, pichação e umidade, portões,
    poste inclinado com luz quente falhando, fios, árvore seca; no primeiro plano entulho, bicicleta encostada, balde,
    chinelo, fio caído do poste, mato e vaso seco. `atores` = [(X, Z, desenha(c, x, y, alt), altura_m)]."""
    cam = cam or Cam3D(x=0.7, h=1.05, F=600, hz=1150, cx=W / 2, z=0.0)
    cena = _fixa("rua", cam, t, _rua_fixa, lua=lua)
    for X, Z, desenha, alt in atores:
        cena.ator(X, Z, desenha, alt)
    if extras:
        extras(cena)
    c.save()
    c.rotate(roll, W / 2, H / 2)
    cena.desenha(c, ceu=lambda cc, ce: ceu_noite(cc, ce, lua=lua, r_lua=70, cores=((10, 12, 20), (28, 34, 46), (66, 72, 82)), nuvens=False),
                 nuvens=lambda cc, ce: nuvens(cc, ce, semente=17))
    c.restore()
    return cena


def _laje_fixa(cam):
    cena = Cena(cam, 0.0, nevoa=(48, 54, 66), alcance=80.0, luz=(-0.4, 0.7, -0.45))
    Y0 = 3.0
    piso = [(-4.2, Y0, -3.0), (4.2, Y0, -3.0), (4.2, Y0, 7.0), (-4.2, Y0, 7.0)]
    cena.face(piso, (100, 98, 94), z=60, hach=False, textura=_tex_concreto(piso))
    # mureta de bloco aparente
    for (x0, x1, z0, z1) in ((-4.2, -4.0, 1.5, 7.0), (4.0, 4.2, 1.5, 7.0), (-4.2, 4.2, 6.8, 7.0)):
        df = torto(lean=0.02, wob=0.02, semente=int(x0 * 10 + z0))
        cena.caixa(x0, x1, Y0, Y0 + 0.95, z0, z1, (124, 110, 98), deforma=df,
                   textura_face=lambda pts: (lambda a, b: (lambda c_, cena_, f: (a(c_, cena_, f), b(c_, cena_, f))))(
                       tex_tijolo(pts, 0.19, 0.39, 120), tex_parede(pts, 77, picho=0.0, umidade=0.6, rachas=1, reboco=False)))
    # puxadinho inacabado: parede de tijolo baiano no fundo à esquerda e coluna com ferro saindo
    pare = [(-4.0, Y0, 6.4), (-1.6, Y0, 6.4), (-1.6, Y0 + 1.7, 6.4), (-4.0, Y0 + 1.5, 6.4)]
    cena.face(pare, (146, 96, 74), z=6.4, textura=tex_tijolo(pare, 0.19, 0.29, 140))
    cena.caixa(-1.6, -1.35, Y0, Y0 + 2.1, 6.25, 6.5, (128, 126, 120), rim=True)
    vergalhoes(cena, -1.47, Y0 + 2.1, 6.37, n=4, alt=0.8, semente=5)
    vergalhoes(cena, 1.4, Y0, 6.6, n=4, alt=0.5, semente=6)
    # caixa d'água no alto de uma base de bloco, com cano descendo e correndo pelo chão
    cena.caixa(1.3, 3.1, Y0, Y0 + 0.75, 3.1, 4.6, (118, 112, 104), textura_face=lambda pts: tex_parede(pts, 81, picho=0.0, umidade=1.0, rachas=2))
    caixa_dagua(cena, 2.2, Y0 + 0.75, 3.85, r=0.82, h=1.1, semente=3)
    cano = [(1.5, Y0 + 0.95, 3.3), (1.2, Y0 + 0.95, 3.2), (1.15, Y0 + 0.04, 3.15), (-0.2, Y0 + 0.04, 3.1), (-0.25, Y0 + 0.04, 6.7)]
    cena.linha(cano, 2.4, z=3.0, cor=(118, 120, 116))
    for q in cano[1:4]:
        cena.linha([(q[0] - 0.05, q[1] - 0.05, q[2]), (q[0] + 0.05, q[1] + 0.05, q[2])], 1.2, z=2.99)   # joelho
    # antena torta
    base = (-2.4, Y0, 4.4)
    cena.linha([base, (-2.3, Y0 + 2.4, 4.4), (-2.0, Y0 + 3.1, 4.5)], 0.7)
    for k in range(5):
        y = Y0 + 2.0 + 0.22 * k
        cena.linha([(-2.7 + 0.05 * k, y + 0.1 * k * 0.3, 4.4), (-1.8 - 0.06 * k, y - 0.15, 4.4)], 0.45)
    # postes do varal
    for x in (-3.8, 1.2):
        cena.linha([(x, Y0, 2.6), (x, Y0 + 1.9, 2.6)], 0.9)
    # objetos: cadeira de plástico, balde, chinelo, mangueira, tijolos, entulho, vaso seco, poça
    cadeira_plastico(cena, -1.8, 2.3, Y=Y0, ang=0.5)
    balde(cena, -1.25, 2.9, Y=Y0, r=0.17, h=0.32)
    chinelo(cena, -0.55, 0.35, ang=1.1)
    mangueira(cena, 0.6, 1.9, Y=Y0)
    tijolos(cena, -1.9, 1.1, Y=Y0, n=7, semente=8)
    for k in range(4):   # cacos de bloco e um ferro no chão, perto
        cena.caixa(-0.9 + 0.35 * k, -0.75 + 0.35 * k, Y0, Y0 + 0.06, 0.6 + 0.12 * (k % 2), 0.72 + 0.12 * (k % 2), (120, 116, 110),
                   deforma=torto(rot=0.5 * k, wob=0.01, semente=700 + k, base=(-0.9 + 0.35 * k, Y0, 0.6)))
    cena.linha([(-1.1, Y0 + 0.02, 1.4), (-0.2, Y0 + 0.03, 1.2), (0.3, Y0 + 0.06, 1.5)], 0.6, cor=(116, 72, 52))
    entulho_laje = [(-3.0, 5.3), (3.3, 6.0)]
    for k, (x, z) in enumerate(entulho_laje):
        mato(cena, x, z, larg=0.6, alt=0.45, semente=90 + k, Y=Y0)
    vaso_seco(cena, 3.5, 2.2, Y=Y0, semente=91)
    poca = [(-1.6, Y0 + 0.005, 3.0), (-0.2, Y0 + 0.005, 2.8), (0.3, Y0 + 0.005, 3.7), (-0.8, Y0 + 0.005, 4.1), (-1.8, Y0 + 0.005, 3.7)]
    cena.face(poca, (52, 58, 70), contorno=0.5, hach=False, z=55, luz_extra=0.5)
    # lajes vizinhas em camadas (cada fileira mais longe e mais apagada)
    rnd = random.Random(21)
    tons = [(140, 130, 114), (120, 116, 110), (146, 120, 104), (110, 112, 116), (132, 126, 106), (150, 140, 120)]
    k = 0
    for fileira, (zf, h_base) in enumerate(((10.0, 0.0), (16.0, 0.5), (24.0, 1.5), (34.0, 3.0), (46.0, 5.0))):
        x = -30.0 + rnd.uniform(0, 3)
        while x < 30:
            w = rnd.uniform(4, 7)
            if not (abs(x + w / 2) < 4.5 and fileira == 0):
                h = rnd.choice((3.0, 3.0, 6.0, 6.0, 8.8)) + h_base
                z0 = zf + rnd.uniform(0, 2.5)
                casa(cena, x, x + w, z0, z0 + rnd.uniform(4, 6), alt=h, cor=tons[k % 6], semente=200 + k, frente_rua=(1 if x < 0 else -1),
                     telhado="laje", laje_caixa=rnd.random() < 0.65, acesa=(0.85 if rnd.random() < 0.18 else 0.0), lean=0.03)
                if rnd.random() < 0.4:
                    vergalhoes(cena, x + rnd.uniform(0.5, w - 0.5), h, z0 + 0.4, n=4, alt=0.6, semente=300 + k)
                if rnd.random() < 0.3:
                    cena.linha([(x + 0.5, h, z0 + 1), (x + 0.6, h + 1.8, z0 + 1), (x + 0.9, h + 2.3, z0 + 1.1)], 0.5)
            x += w + rnd.choice((0.0, 0.2, 0.8))
            k += 1
    for j in range(90):  # morro de casinhas no fundo, com janelinha quente aqui e ali
        x = rnd.uniform(-70, 70)
        z = rnd.uniform(56, 90)
        yb = max(0.0, 16 - abs(x) * 0.2) * (1 - (z - 56) / 60)
        hh = rnd.uniform(2.5, 5.0)
        cena.caixa(x, x + rnd.uniform(2.5, 4.5), yb, yb + hh, z, z + 3, tons[j % 6], lados=False, topo=False)
        if rnd.random() < 0.22:
            cena.luz(x + 1.2, yb + hh * 0.5, z - 0.1, 0.9, LAMPADA, 0.55, chao=False)
    cena.linha([(4.8, 0, 3.0), (4.85, 8.0, 3.0)], 1.0)
    fio(cena, (4.85, 7.6, 3.0), (-12, 7.0, 13), barriga=1.2)
    fio(cena, (4.85, 7.3, 3.0), (14, 7.2, 30), barriga=1.6)
    cena.luz(3.6, 7.0, 3.0, 3.2, LAMPADA, 0.9, pisca=4)
    for zn, al in ((18.0, 0.1), (30.0, 0.16), (44.0, 0.22), (62.0, 0.3)):
        cena.neblina(zn, altura=2.0 + zn * 0.12, alfa=al)
    return cena


def _roupas_varal(cena, t, Y0=3.0):
    va, vb = (-3.8, Y0 + 1.82, 2.6), (1.2, Y0 + 1.9, 2.6)
    fio(cena, va, vb, barriga=0.22, k=0.4, vivo=True)
    for k, (u, larg, alt, cor) in enumerate(((0.12, 0.5, 0.7, (120, 118, 128)), (0.34, 0.38, 0.95, (150, 140, 120)),
                                             (0.58, 0.6, 0.5, (90, 96, 110)), (0.82, 0.32, 0.75, (136, 106, 108)))):
        x = va[0] + (vb[0] - va[0]) * u
        z = va[2]
        y = va[1] + (vb[1] - va[1]) * u - 0.22 * 4 * u * (1 - u)
        bal = 0.1 * math.sin(t * 1.6 + k) + 0.04 * math.sin(t * 3.7 + 2 * k)
        pts = [(x - larg / 2, y, z), (x + larg / 2, y, z), (x + larg / 2 + bal, y - alt, z + 0.05 + bal * 0.3),
               (x + bal * 0.5, y - alt * 0.85, z + 0.05), (x - larg / 2 + bal, y - alt, z + 0.05 + bal * 0.3)]
        cena.face(pts, cor, contorno=0.9, z=z - 0.02, vivo=True)
        for s_ in (-1, 1):  # pregador
            cena.linha([(x + s_ * larg * 0.38, y + 0.05, z - 0.01), (x + s_ * larg * 0.38, y - 0.07, z - 0.01)], 0.9, z=z - 0.03, vivo=True)


def laje(c, t, cam=None, atores=(), roll=-1.0, extras=None):
    """Laje de periferia de madrugada (câmera na altura de quem está na laje): caixa d'água com tampa e cano em
    cima de uma base de bloco, varal com roupa balançando, antena torta, tijolo aparente, puxadinho inacabado com ferro
    de coluna saindo, cadeira de plástico, balde, chinelo, mangueira, tijolos, poça com a lua e as lajes vizinhas em
    camadas até o morro. `atores` ficam em Y=3 (o piso da laje)."""
    cam = cam or Cam3D(x=-0.2, h=4.15, F=640, hz=1040, cx=W / 2, z=-1.3)
    cena = _fixa("laje", cam, t, _laje_fixa)
    _roupas_varal(cena, t)
    for X, Z, desenha, alt in atores:
        cena.ator(X, Z, desenha, alt, Y=3.0)
    if extras:
        extras(cena)
    c.save()
    c.rotate(roll, W / 2, H / 2)
    cena.desenha(c, ceu=lambda cc, ce: ceu_noite(cc, ce, lua=(0.24, 0.13), r_lua=58, cores=((10, 12, 20), (30, 36, 50), (74, 80, 90)), nuvens=False),
                 nuvens=lambda cc, ce: nuvens(cc, ce, semente=23, faixa=(0.03, 0.34)))
    c.restore()
    return cena


def _estrada_fixa(cam):
    cena = Cena(cam, 0.0, nevoa=(54, 60, 64), alcance=60.0, luz=(0.5, 0.6, -0.4))
    terra = [(-2.6, 0, 0.3), (2.6, 0, 0.3), (1.6, 0, 140), (-1.6, 0, 140)]
    cena.face(terra, (100, 88, 70), z=300, hach=False, textura=_tex_sulcos())
    for l in (-1, 1):
        campo = [(l * 2.6, 0, 0.3), (l * 80, 0, 0.3), (l * 80, 0, 140), (l * 1.6, 0, 140)]
        cena.face(campo, (78, 80, 64), z=301, hach=False, textura=_tex_capim(l))
    rnd = random.Random(6)
    for l in (-1, 1):
        topos = []
        for k in range(16):
            z = 2.0 + k * 3.2
            x = l * (3.2 + 0.02 * z)
            inc = rnd.uniform(-0.12, 0.12)
            h = rnd.uniform(1.1, 1.4)
            cena.face([(x - 0.07, 0, z), (x + 0.07, 0, z), (x + 0.07 + inc * h, h, z), (x - 0.07 + inc * h, h + 0.05, z)], (96, 82, 66),
                      contorno=0.9, rim=True)
            topos.append((x + inc * h, h, z))
        for fy in (0.45, 0.8, 1.05):
            for a, b in zip(topos[:-1], topos[1:]):
                pa = (a[0], a[1] * fy / 1.2, a[2])
                pb = (b[0], b[1] * fy / 1.2, b[2])
                fio(cena, pa, pb, barriga=0.06, k=0.3, n=6)
                for j in range(3):
                    u = (j + 0.5) / 3
                    q = (pa[0] + (pb[0] - pa[0]) * u, pa[1] + (pb[1] - pa[1]) * u - 0.06 * 4 * u * (1 - u), pa[2] + (pb[2] - pa[2]) * u)
                    cena.linha([(q[0], q[1] - 0.04, q[2] - 0.04), (q[0], q[1] + 0.04, q[2] + 0.04)], 0.3, z=q[2] - 0.02)
    px, pz, ab = -3.2, 7.0, 0.5
    folha = [(px, 0.1, pz), (px - 2.6 * math.cos(ab), 0.1, pz + 2.6 * math.sin(ab)), (px - 2.6 * math.cos(ab), 1.3, pz + 2.6 * math.sin(ab)),
             (px, 1.35, pz)]
    a, b, c_, d = [np.array(p) for p in folha]
    for k in range(5):
        u = k / 4
        cena.linha([a + (d - a) * u, b + (c_ - b) * u], 1.1, z=pz)
    cena.linha([a, c_], 1.0, z=pz)
    cena.face([(px - 0.12, 0, pz - 0.1), (px + 0.12, 0, pz - 0.1), (px + 0.12, 1.7, pz - 0.1), (px - 0.12, 1.75, pz - 0.1)], (90, 76, 60), rim=True)
    casa(cena, 6.0, 13.0, 26.0, 33.0, alt=3.2, cor=(150, 140, 118), telhado="duas", semente=77, frente_rua=-1, acesa=1.0, lean=0.04)
    for k in range(4):
        cena.linha([(5.2, 0, 26.5 + 2.0 * k), (5.25, 2.7, 26.5 + 2.0 * k)], 0.8)
    cena.luz(5.4, 2.5, 27.0, 2.2, LAMPADA, 0.8, pisca=9)   # lâmpada da varanda
    for X, Z, alt_, s_ in ((-6.5, 12.0, 7.5, 3), (5.5, 18.0, 6.0, 5), (-9.0, 30.0, 8.0, 9), (3.8, 44.0, 5.0, 14), (-4.5, 56.0, 6.0, 21)):
        arvore_seca(cena, X, Z, alt=alt_, semente=s_, galhos=6, inclina=0.18 * (1 if X < 0 else -1))
    for k in range(30):
        l = rnd.choice((-1, 1))
        mato(cena, l * rnd.uniform(2.5, 9.0), rnd.uniform(1.5, 40), larg=rnd.uniform(0.6, 1.4), alt=rnd.uniform(0.4, 0.9), semente=400 + k)
    # primeiro plano: capim alto nos cantos, pedras, galho caído, garrafa e poça com a lua
    mato(cena, -0.45, 1.0, larg=0.6, alt=0.7, semente=71, n=26)
    mato(cena, 1.05, 1.15, larg=0.6, alt=0.65, semente=72, n=24)
    mato(cena, -1.3, 2.0, larg=0.8, alt=0.6, semente=73, n=18)
    for k in range(5):   # pedras achatadas (polígono irregular no chão + face de cima)
        x, z = rnd.uniform(-0.8, 1.5), rnd.uniform(1.4, 3.6)
        r = rnd.uniform(0.05, 0.12)
        topo = [(x + r * math.cos(a) * rnd.uniform(0.7, 1.2), r * 0.45, z + r * 0.8 * math.sin(a) * rnd.uniform(0.7, 1.2))
                for a in np.linspace(0, 2 * math.pi, 9, endpoint=False)]
        cena.face([(p[0], 0.0, p[2] - 0.02) for p in topo[4:]] + [(p[0], p[1], p[2]) for p in topo[:5][::-1]], (96, 92, 86), z=z)
        cena.face(topo, (126, 122, 114), z=z - 0.01, rim=True)
    cena.linha([(-1.2, 0.03, 2.4), (-0.6, 0.06, 2.2), (-0.1, 0.04, 2.5), (0.2, 0.08, 2.3)], 1.6, z=2.2)
    cena.linha([(-0.6, 0.06, 2.2), (-0.5, 0.25, 2.1), (-0.35, 0.33, 2.15)], 0.8, z=2.19)
    _cilindro(cena, 1.3, 0.0, 2.0, 0.04, 0.04, 0.22, (60, 76, 64))
    for zn, al in ((8.0, 0.1), (15.0, 0.15), (24.0, 0.2), (38.0, 0.26), (58.0, 0.34)):
        cena.neblina(zn, altura=0.9, alfa=al)
    return cena


def estrada(c, t, cam=None, atores=(), roll=1.0, extras=None):
    """Estrada de terra de sítio (câmera baixa): sulco, pedra, poça; cerca de mourão torto com arame farpado; porteira;
    casa de sítio com varanda e lâmpada quente; árvores mortas; capim alto no primeiro plano; galho caído, garrafa."""
    cam = cam or Cam3D(x=0.3, h=1.1, F=640, hz=1150, cx=W / 2, z=0.0)
    cena = _fixa("estrada", cam, t, _estrada_fixa)
    for X, Z, desenha, alt in atores:
        cena.ator(X, Z, desenha, alt)
    if extras:
        extras(cena)
    c.save()
    c.rotate(roll, W / 2, H / 2)
    cena.desenha(c, ceu=lambda cc, ce: ceu_noite(cc, ce, lua=(0.3, 0.2), r_lua=80, cores=((12, 14, 20), (34, 40, 50), (80, 86, 90)), nuvens=False),
                 nuvens=lambda cc, ce: nuvens(cc, ce, semente=29))
    c.restore()
    return cena
