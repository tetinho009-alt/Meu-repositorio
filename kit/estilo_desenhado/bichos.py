# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Bichos no estilo gótico (segunda rodada): Gato, Cachorro e Ave (corvo, urubu, pardal), de perfil com a cabeça
em 3/4, olhando pra direita.

Corpo com volume (tórax, barriga, ombro, anca), pelo e pena em tufos de nanquim irregulares (contorno quebrado,
hachura que acompanha o pelo) e patas articuladas por IK de 2 ossos: o pé fica plantado no chão e o joelho, o
cotovelo e o jarrete dobram no lugar certo. A versão "errada" é outro bicho montado do mesmo molde: pescoço comprido
demais, perna comprida com a junta dobrando ao contrário, olhos humanos e o sorriso do rig (_rig._sorriso).

Mundo de cada bicho: patas em y=1000 (a versão errada é mais alta), centro x=500; `altura` em desenhar() = quantos px
valem 1000 unidades. {"lado": -1} vira pra esquerda.

Pose (por parte, como no rig) e chaves próprias:
  t (fervura, respiração, rabo)   susto 0..1   errado False/True   piscar 0..1 (lenta)   olhar -1..1
  boca 0..1 (chiar / ofegar / grasnar)   asa 0..1 (ave)   pes {"pata_fd": (dx, dy), ...} deslocando o alvo do pé
Use `pose_viva(bicho, t, ...)`: respiração, piscada lenta, rabo em S, orelhas, ofegar, trancos de pássaro e pulinho.
"""
import math
import random

import numpy as np
import skia

from . import tinta as T
from .rig_simples import RigSimples


def _q(v, passo=0.25):
    return round(float(v) / passo) * passo


# ---------------------------------------------------------------- traço de pelo

def _tubo(a, b, r0, r1, n=8):
    ax, ay = a
    bx, by = b
    ang = math.atan2(by - ay, bx - ax)
    ca = [(ax + r0 * math.cos(ang + math.pi / 2 + math.pi * k / n), ay + r0 * math.sin(ang + math.pi / 2 + math.pi * k / n)) for k in range(n + 1)]
    cb = [(bx + r1 * math.cos(ang - math.pi / 2 + math.pi * k / n), by + r1 * math.sin(ang - math.pi / 2 + math.pi * k / n)) for k in range(n + 1)]
    return np.array(ca + cb)


def _normais_fora(q):
    nrm, _ = T._normais(q, True)
    cen = q.mean(axis=0)
    if np.mean(np.sum((q - cen) * nrm, axis=1)) < 0:
        nrm = -nrm
    return nrm


def tufos(pts, comp, rnd, fluxo=(-1.0, 0.0), onde=None, passo=9.0):
    """Contorno com tufos de pelo: cada tufo é uma ponta curva que sai pela normal e varre na direção do pelo."""
    q, _ = T.reamostra(pts, passo, True)
    nrm = _normais_fora(q)
    fx, fy = fluxo
    out = []
    n = len(q)
    for k in range(n):
        p, nv = q[k], nrm[k]
        f = onde(p[0], p[1]) if onde else 1.0
        if f <= 0.02 or k % 2:
            out.append((p[0], p[1]))
            continue
        L = comp * f * rnd.uniform(0.55, 1.25)
        dx, dy = nv[0] * 0.75 + fx * 0.65, nv[1] * 0.75 + fy * 0.65
        m = math.hypot(dx, dy) or 1
        out.append((p[0] + dx / m * L * 0.45 + nv[0] * L * 0.15, p[1] + dy / m * L * 0.45 + nv[1] * L * 0.15))
        out.append((p[0] + dx / m * L, p[1] + dy / m * L))
        if rnd.random() < 0.35:  # tufo duplo
            out.append((p[0] + dx / m * L * 0.5 - nv[0] * 2, p[1] + dy / m * L * 0.5 - nv[1] * 2))
            out.append((p[0] + dx / m * L * 0.8 + fy * 3, p[1] + dy / m * L * 0.8 - fx * 3))
    return np.array(out)


def contorno_quebrado(d, pts, larg, var, sid, cortes=5, alfa=255, cor=T.TINTA, fechado=True):
    """Nanquim em pedaços: o contorno é feito de traços que começam e acabam (com falhas), não uma linha só."""
    q, _ = T.reamostra(pts, 3.0, fechado)
    n = len(q)
    if n < 8:
        return
    if not fechado:  # traço aberto: só falhas no meio
        rnd = random.Random(sid * 7 + (var or 0))
        corte = rnd.randrange(n // 3, 2 * n // 3) if cortes else n
        for j, seg in enumerate((q[:corte], q[corte + 2:])):
            if len(seg) > 4:
                d.pinta(T.traco_tinta(seg, larg * rnd.uniform(0.85, 1.1), var, sid + j, amp=0.6, ponta=(0.15, 0.2)), T.tinta_paint(cor, alfa))
        return
    rnd = random.Random(sid * 7 + (var or 0))
    ini = rnd.randrange(n)
    cortes_ = sorted(rnd.sample(range(n), min(cortes, n // 6)))
    k0 = ini
    marcas = [(ini + c) % n for c in cortes_] + [ini + n]
    for j, k1 in enumerate(sorted(set(marcas))):
        if k1 <= k0:
            continue
        idx = [(k0 + i) % n for i in range(k1 - k0 + 2)]
        seg = q[idx]
        if len(seg) > 4:
            d.pinta(T.traco_tinta(seg, larg * rnd.uniform(0.8, 1.15), var, sid + j, amp=0.7, ponta=(0.12, 0.2)), T.tinta_paint(cor, alfa))
        k0 = k1 + rnd.randint(1, 3)  # a falha entre um traço e outro


def pelagem(d, regiao, ang, passo, comp, var, sid, alfa=150, larg=1.1, cor=T.TINTA, curva=0.35):
    """Hachura que acompanha o pelo: traços curtos e curvos na direção `ang` (radianos), recortados pela região."""
    r = regiao.computeTightBounds()
    if r.isEmpty():
        return
    rnd = random.Random(T._sem(sid, var, "pelo"))
    p = skia.Path()
    y = r.top()
    linha_ = 0
    while y < r.bottom():
        x = r.left() + (passo * 0.5 if linha_ % 2 else 0)
        while x < r.right():
            px, py = x + rnd.uniform(-passo * 0.4, passo * 0.4), y + rnd.uniform(-passo * 0.4, passo * 0.4)
            a = ang + rnd.uniform(-0.3, 0.3)
            L = comp * rnd.uniform(0.6, 1.2)
            ex, ey = px + math.cos(a) * L, py + math.sin(a) * L
            cx, cy = (px + ex) / 2 - math.sin(a) * L * curva, (py + ey) / 2 + math.cos(a) * L * curva
            p.moveTo(px, py)
            p.quadTo(cx, cy, ex, ey)
            x += passo
        y += passo * 0.8
        linha_ += 1
    sub = T.Desenho()
    sub.pinta(p, skia.Paint(AntiAlias=True, Color=T.cor_skia(cor, alfa), Style=skia.Paint.kStroke_Style, StrokeWidth=larg,
                            StrokeCap=skia.Paint.kRound_Cap))
    d.recorte(regiao, sub)


def vol(d, pts, cor, var, sid, ang_pelo=math.pi, contorno=3.4, sombra=1.0, luz=(-0.55, -0.83), rim=None, passo=7.0, comp=11.0,
        cortes=5, prof=(0.32, 0.14), pelo=True):
    """Volume de bicho: tom, meia-sombra com pelo hachurado, sombra funda mais densa, borda de luz e contorno quebrado."""
    q, _ = T.tremido(pts, var, sid, 0.8, True)
    fill = T.caminho(q)
    d.pinta(fill, T.tinta_paint(cor))
    if sombra:
        meia, funda = T.sombra_regioes(fill, luz, prof)
        esc = T.escurece(T.mistura(cor, T.SOMBRA, 0.3), 0.6)
        d.pinta(meia, T.tinta_paint(esc, 105 * sombra))
        d.pinta(funda, T.tinta_paint(T.escurece(esc, 0.7), 110 * sombra))
        if pelo:
            pelagem(d, meia, ang_pelo, passo, comp, var, sid, alfa=130 * sombra)
            pelagem(d, funda, ang_pelo + 0.25, passo * 0.7, comp * 0.9, var, sid + 1, alfa=170 * sombra)
    if rim:
        luzp = skia.Op(fill, T.deslocado(fill, -luz[0] * 4, -luz[1] * 4), skia.PathOp.kDifference_PathOp)
        d.pinta(luzp, T.tinta_paint(rim, 130))
    if contorno:
        contorno_quebrado(d, pts, contorno, var, sid + 7, cortes=cortes)
    return fill


def membro(d, a, b, r0, r1, cor, var, sid, rnd, pelo=7.0, ang_pelo=math.pi / 2, tampa_fim=False, fluxo=(-0.3, 1.0), rim=None):
    """Gomo de perna/rabo sem costura: o preenchimento cobre a junta, o nanquim só corre pelos lados (quebrado),
    então o joelho e o cotovelo dobram sem aparecer o "encaixe de boneco de madeira"."""
    pts = _tubo(a, b, r0, r1, 8)
    if pelo:
        pts = tufos(pts, pelo, rnd, fluxo=fluxo, onde=lambda x, y: 0.8)
    vol(d, pts, cor, var, sid, ang_pelo=ang_pelo, contorno=0, comp=max(5.0, pelo), passo=6, rim=rim)
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    nx, ny = -math.sin(ang), math.cos(ang)
    tx, ty = math.cos(ang), math.sin(ang)
    for k, sn in enumerate((1, -1)):
        lado = [(a[0] - tx * r0 * 0.4 + sn * nx * r0, a[1] - ty * r0 * 0.4 + sn * ny * r0),
                ((a[0] + b[0]) / 2 + sn * nx * (r0 + r1) / 2, (a[1] + b[1]) / 2 + sn * ny * (r0 + r1) / 2),
                (b[0] + tx * r1 * 0.4 + sn * nx * r1, b[1] + ty * r1 * 0.4 + sn * ny * r1)]
        contorno_quebrado(d, np.array(T.catmull(lado, False, 8)), 2.8, var, sid + 30 + k, cortes=1, fechado=False)
    if tampa_fim:
        cap = [(b[0] + r1 * math.cos(ang - math.pi / 2 + math.pi * j / 8), b[1] + r1 * math.sin(ang - math.pi / 2 + math.pi * j / 8))
               for j in range(9)]
        T.linha(d, cap, 2.8, var, sid + 40, ponta=(0.1, 0.1))


def _olho_humano(d, x, y, r, var, sid, olhar=0.0, abre=1.0, iris=(92, 70, 52)):
    """Olho humano num bicho: branco amendoado, íris castanha, pálpebra com dobra, bolsa embaixo e cílios."""
    pts = []
    for a in np.linspace(0, 2 * math.pi, 36, endpoint=False):
        ry = r * (0.58 if math.sin(a) < 0 else 0.42) * abre
        pts.append((x + r * math.cos(a), y + ry * math.sin(a) + 0.15 * r * math.cos(a) ** 2))
    branco = np.array(pts)
    q, _ = T.tremido(branco, var, sid, 0.3, True)
    bp = T.caminho(q)
    d.pinta(bp, T.tinta_paint((222, 214, 198)))
    sub = T.Desenho()
    ix = x + olhar * r * 0.35
    sub.pinta(T.caminho(T.elipse(ix, y, r * 0.42, r * 0.42, 24)), T.tinta_paint(iris))
    sub.pinta(T.caminho(T.elipse(ix, y, r * 0.42, r * 0.42, 24)), skia.Paint(AntiAlias=True, Color=T.cor_skia(T.TINTA, 200),
                                                                         Style=skia.Paint.kStroke_Style, StrokeWidth=r * 0.07))
    sub.pinta(T.caminho(T.elipse(ix, y, r * 0.17, r * 0.17, 16)), T.tinta_paint((10, 6, 8)))
    sub.pinta(T.caminho(T.elipse(ix - r * 0.12, y - r * 0.13, r * 0.07, r * 0.07, 10)), T.tinta_paint((240, 232, 214), 230))
    sub.pinta(T.caminho(np.array([(x - r, y - r), (x + r, y - r), (x + r, y - r * 0.18), (x - r, y - r * 0.25)])),
              T.tinta_paint((150, 132, 120), 70))
    d.recorte(bp, sub)
    d.pinta(T.traco_tinta(q, r * 0.1, var, sid + 1, fechado=True, amp=0.3), T.tinta_paint(T.TINTA))
    T.linha(d, [(x - r * 0.9, y - r * 0.62 * abre), (x, y - r * 0.85 * abre), (x + r * 0.95, y - r * 0.55 * abre)], r * 0.07, var, sid + 2,
            alfa=210)  # dobra da pálpebra
    T.linha(d, [(x - r * 0.7, y + r * 0.62), (x, y + r * 0.75), (x + r * 0.7, y + r * 0.58)], r * 0.05, var, sid + 3, alfa=150)  # bolsa
    for k in range(4):  # cílios
        u = 0.2 + 0.2 * k
        bx, by = x - r + 2 * r * u, y - r * 0.55 * abre * math.sin(math.pi * u) - r * 0.05
        T.linha(d, [(bx, by), (bx + r * 0.12, by - r * 0.22)], r * 0.05, var, sid + 4 + k, ponta=(0.0, 0.7), suave=False)


def _ik(p0, alvo, L0, L1, pref):
    """IK de 2 ossos: ângulos absolutos (rad) dos 2 ossos; a junta fica do lado de `pref` (vetor)."""
    dx, dy = alvo[0] - p0[0], alvo[1] - p0[1]
    dist = max(abs(L0 - L1) + 1.0, min(L0 + L1 - 0.5, math.hypot(dx, dy)))
    base = math.atan2(dy, dx)
    a = math.acos(max(-1.0, min(1.0, (L0 * L0 + dist * dist - L1 * L1) / (2 * L0 * dist))))
    melhor = max((base + a, base - a), key=lambda g: math.cos(g) * pref[0] + math.sin(g) * pref[1])
    kx, ky = p0[0] + L0 * math.cos(melhor), p0[1] + L0 * math.sin(melhor)
    return melhor, math.atan2(alvo[1] - ky, alvo[0] - kx)


def _nivela(J):
    """Todas as pontas das patas no mesmo chão (a mais baixa)."""
    chave = [k for k in J if len(k) == 3 and k.endswith("3")]
    chao = max(J[k][1] for k in chave)
    for k in chave:
        J[k] = (J[k][0], chao)
    J["_chao"] = chao


def _xy(p):
    return (p.x(), p.y()) if hasattr(p, "x") else (p[0], p[1])


# ---------------------------------------------------------------- base dos bichos

class _Bicho(RigSimples):
    """Base: juntas (J), pernas com IK e o gêmeo "errado"."""

    def __init__(self, semente=1, errado=False, vetor=False):
        self.errado = errado
        self.J = self._juntas()
        self.PARTES = self._partes()
        self.PES = (500.0, self.J.get("_chao", 1000.0))
        super().__init__(semente + (500 if errado else 0), vetor=vetor)
        self._gemeo = None

    def gemeo(self):
        if self._gemeo is None:
            self._gemeo = type(self)(**self._args_gemeo())
        return self._gemeo

    def _args_gemeo(self):
        return dict(semente=self.semente, errado=not self.errado)

    def desenhar(self, c, x, y, altura, pose=None, partes=None, sombra=True):
        pose = pose or {}
        if bool(pose.get("errado")) != self.errado:
            return self.gemeo().desenhar(c, x, y, altura, pose, partes, sombra)
        return super().desenhar(c, x, y, altura, self.resolve(pose), partes, sombra)

    def resolve(self, pose):
        """Planta os pés: IK de cada perna (ossos o1, o2 + pata o3) a partir da matriz do corpo."""
        pose = {k: (dict(v) if isinstance(v, dict) else v) for k, v in pose.items()}
        pes = pose.get("pes") or {}
        m_c = self._local("corpo", pose)
        rot_c = (pose.get("corpo") or {}).get("rot", 0.0)
        for perna, (o1, o2, o3, j0, j1, j2, j3, pref, inclina) in self.PERNAS.items():
            J0, J1, J2, J3 = self.J[j0], self.J[j1], self.J[j2], self.J[j3]
            if "rot" in (pose.get(o1) or {}):
                continue
            hip = _xy(m_c.mapXY(*J0))
            dx, dy = pes.get(perna, (0.0, 0.0))
            r2 = math.atan2(J3[1] - J2[1], J3[0] - J2[0])
            inc = math.radians(inclina + (pose.get("_inclina_pata") or 0.0))
            L2 = math.hypot(J3[0] - J2[0], J3[1] - J2[1])
            pe = (J3[0] + dx, J3[1] + dy)
            tornoz = (pe[0] - L2 * math.cos(r2 + inc), pe[1] - L2 * math.sin(r2 + inc))
            L0 = math.hypot(J1[0] - J0[0], J1[1] - J0[1])
            L1 = math.hypot(J2[0] - J1[0], J2[1] - J1[1])
            p = pref if not self.errado else (-pref[0], -pref[1])
            a0, a1 = _ik(hip, tornoz, L0, L1, p)
            r0 = math.atan2(J1[1] - J0[1], J1[0] - J0[0])
            r1 = math.atan2(J2[1] - J1[1], J2[0] - J1[0])
            rot1 = math.degrees(a0 - r0) - rot_c
            rot2 = math.degrees(a1 - r1) - math.degrees(a0 - r0)
            rot3 = math.degrees(inc) - math.degrees(a1 - r1)
            pose[o1] = {**(pose.get(o1) or {}), "rot": rot1}
            pose[o2] = {**(pose.get(o2) or {}), "rot": rot2}
            pose[o3] = {**(pose.get(o3) or {}), "rot": rot3}
        return pose

    def _depois_sorriso(self, c, ponto, escala, abre, vira=0.55, rot=0.0):
        from ._rig import _sorriso
        c.save()
        c.translate(*ponto)
        c.rotate(rot)
        c.scale(escala, escala)
        _sorriso(c, 0.0, 0.0, abre, vira)
        c.restore()


# ---------------------------------------------------------------- gato

class Gato(_Bicho):
    """Gato magro de rua, preto-carvão: tórax fundo, barriga recolhida, anca redonda, cabeça grande em 3/4,
    orelhas grandes que deitam, olho de fenda que dilata no susto, rabo de 6 gomos em S."""
    COR, COR_ESC, PEITO, OLHO = (72, 68, 70), (44, 41, 45), (108, 102, 98), (180, 170, 96)

    def _juntas(self):
        k = 1.55 if self.errado else 1.0
        J = {"N": (640.0, 648.0), "T": (318.0, 656.0), "C0": (490.0, 700.0)}

        def perna(nome, base, v1, v2, v3, dxl=0.0):
            b = (base[0] + dxl, base[1])
            J[nome + "0"] = b
            J[nome + "1"] = (b[0] + v1[0] * k, b[1] + v1[1] * k)
            J[nome + "2"] = (J[nome + "1"][0] + v2[0] * k, J[nome + "1"][1] + v2[1] * k)
            J[nome + "3"] = (J[nome + "2"][0] + v3[0], J[nome + "2"][1] + v3[1])
        for lado, dxl in (("d", 0.0), ("e", -20.0)):
            perna("F" + lado, (600.0, 700.0), (-12, 100), (10, 135), (30, 57), dxl)
            perna("H" + lado, (385.0, 700.0), (36, 100), (-66, 100), (33, 92), dxl)
        _nivela(J)
        J["HP"] = (J["N"][0] + 60, J["N"][1] - 230) if self.errado else J["N"]
        return J

    def _partes(self):
        J = self.J
        P = [(f"rabo{i}", "corpo" if i == 1 else f"rabo{i - 1}", (J["T"][0] - 52 * (i - 1), J["T"][1])) for i in range(1, 7)]
        for lado in ("e", "d"):
            P += [(f"fe_braco_{lado}", "corpo", J[f"F{lado}0"]), (f"fe_antebraco_{lado}", f"fe_braco_{lado}", J[f"F{lado}1"]),
                  (f"fe_pata_{lado}", f"fe_antebraco_{lado}", J[f"F{lado}2"]),
                  (f"tr_coxa_{lado}", "corpo", J[f"H{lado}0"]), (f"tr_canela_{lado}", f"tr_coxa_{lado}", J[f"H{lado}1"]),
                  (f"tr_pata_{lado}", f"tr_canela_{lado}", J[f"H{lado}2"])]
            if lado == "e":
                P += [("corpo", "raiz", J["C0"])]
        if self.errado:
            P += [("pescoco", "corpo", J["N"])]
        pai = "pescoco" if self.errado else "corpo"
        P += [("orelha_l", "cabeca", (J["HP"][0] + 48, J["HP"][1] - 108)), ("cabeca", pai, J["HP"]),
              ("orelha_p", "cabeca", (J["HP"][0] + 104, J["HP"][1] - 110))]
        # orelha de longe atrás da cabeça: reordena (orelha_l antes da cabeça, orelha_p depois)
        self.PERNAS = {f"pata_f{lado}": (f"fe_braco_{lado}", f"fe_antebraco_{lado}", f"fe_pata_{lado}", f"F{lado}0", f"F{lado}1",
                                         f"F{lado}2", f"F{lado}3", (-1.0, 0.0), 0.0) for lado in ("e", "d")}
        self.PERNAS.update({f"pata_t{lado}": (f"tr_coxa_{lado}", f"tr_canela_{lado}", f"tr_pata_{lado}", f"H{lado}0", f"H{lado}1",
                                              f"H{lado}2", f"H{lado}3", (1.0, 0.0), 0.0) for lado in ("e", "d")})
        return P

    def expr(self, parte, pose):
        s = _q(pose.get("susto", 0))
        if parte == "corpo":
            return (s,)
        if parte == "cabeca":
            return (s, _q(pose.get("boca", 0)), _q(pose.get("piscar", 0), 0.2), _q(pose.get("olhar", 0), 0.5))
        if parte.startswith("orelha") or parte.startswith("rabo"):
            return (s,)
        return ()

    def monta(self, parte, d, var, e):
        J = self.J
        rnd = random.Random(T._sem(self.semente, parte))
        sid = T._sem(self.semente, parte, "g") % 100000
        cor, esc = self.COR, self.COR_ESC
        if parte == "corpo":
            s = e[0]
            self._corpo(d, var, sid, s, rnd)
        elif parte.startswith("rabo"):
            i = int(parte[4])
            s = e[0]
            a = (J["T"][0] - 52 * (i - 1), J["T"][1])
            b = (a[0] - 56, a[1])
            r0, r1 = 13 - 1.3 * (i - 1), 12 - 1.4 * i
            if i == 6:
                r1 = 4
            r0, r1 = r0 * (1 + 0.9 * s), r1 * (1 + 0.9 * s)
            membro(d, a, b, r0, max(3.0, r1), cor, var, sid, rnd, pelo=9 + 16 * s, ang_pelo=math.pi, tampa_fim=(i == 6), fluxo=(-1, 0))
        elif parte.startswith("fe_") or parte.startswith("tr_"):
            self._perna(d, parte, var, sid, rnd)
        elif parte.startswith("orelha"):
            self._orelha(d, parte, var, sid, e[0])
        elif parte == "pescoco":
            N, HP = J["N"], J["HP"]
            pts = tufos(_tubo(N, HP, 30, 24, 8), 10, rnd, fluxo=(0, 1))
            vol(d, pts, cor, var, sid, ang_pelo=math.pi / 2, contorno=3.2)
            for k in range(5):
                u = 0.15 + 0.17 * k
                x, y = N[0] + (HP[0] - N[0]) * u, N[1] + (HP[1] - N[1]) * u
                T.linha(d, [(x - 18, y + 4), (x, y - 2), (x + 18, y + 4)], 1.4, var, sid + 10 + k, alfa=170)  # anéis de pele
        elif parte == "cabeca":
            self._cabeca(d, var, sid, e, rnd)

    def _corpo(self, d, var, sid, s, rnd):
        a = s
        top = [(668, 676), (642, 638 - 10 * a), (600, 624 - 50 * a), (540, 612 - 120 * a), (470, 610 - 150 * a), (400, 616 - 120 * a),
               (345, 632 - 60 * a), (318, 652)]
        fundo = [(296, 678), (300, 722), (338, 752), (392, 760), (440, 740), (500, 728 - 6 * a), (560, 742), (612, 768), (656, 752),
                 (676, 712)]
        pts = T.catmull(top + fundo, True, 6)
        onde = lambda x, y: (0.5 + 1.5 * a) if y < 660 - 60 * a else (0.6 if x > 560 else 0.35)
        pts = tufos(pts, 9 + 24 * a, rnd, fluxo=(-1, 0.2), onde=onde)
        fill = vol(d, pts, self.COR, var, sid, ang_pelo=math.pi + 0.15, rim=(122, 116, 110), comp=12)
        # peito mais claro com tufos, anca e omoplata marcadas, costelas sob o pelo ralo
        peito = tufos(T.catmull([(640, 690), (668, 712), (650, 760), (612, 768), (598, 730)], True, 6), 10, rnd, fluxo=(0, 1))
        vol(d, peito, self.PEITO, var, sid + 20, ang_pelo=math.pi / 2, contorno=0, sombra=0.7, comp=9)
        T.linha(d, [(392, 650 - 100 * a), (360, 690 - 40 * a), (372, 740)], 2.2, var, sid + 30, alfa=200)   # anca
        T.linha(d, [(600, 650 - 40 * a), (586, 690), (596, 730)], 2.0, var, sid + 31, alfa=190)            # omoplata
        for k in range(4):
            x = 560 - 30 * k
            T.linha(d, [(x, 666 - 90 * a * (1 - abs(k - 1.5) / 3)), (x - 12, 700), (x - 6, 728)], 1.4, var, sid + 40 + k, alfa=120)

    def _perna(self, d, parte, var, sid, rnd):
        J = self.J
        lado = parte[-1]
        longe = lado == "e"
        cor = self.COR_ESC if longe else self.COR
        frente = parte.startswith("fe_")
        L = ("F" if frente else "H") + lado
        if parte.split("_")[1] in ("braco", "coxa"):
            a, b = J[L + "0"], J[L + "1"]
            r0, r1 = (30, 15) if frente else (44, 17)
            membro(d, (a[0], a[1] - 18), b, r0, r1, cor, var, sid, rnd, pelo=8, ang_pelo=math.pi / 2 + 0.3)
        elif "antebraco" in parte or "canela" in parte:
            a, b = J[L + "1"], J[L + "2"]
            r0, r1 = (15, 9) if frente else (17, 9)
            membro(d, a, b, r0, r1, cor, var, sid, rnd, pelo=5, ang_pelo=math.pi / 2)
        else:  # pata: dedos com almofada
            a, b = J[L + "2"], J[L + "3"]
            ang = math.atan2(b[1] - a[1], b[0] - a[0])
            pts = [(a[0] - 8, a[1]), (a[0] + 9, a[1] - 2), (b[0] + 10, b[1] - 10), (b[0] + 14, b[1] + 2), (b[0] - 4, b[1] + 6),
                   (b[0] - 22, b[1] + 4), (a[0] - 10, a[1] + 20)]
            vol(d, T.catmull(pts, True, 5), cor, var, sid, ang_pelo=ang, contorno=2.8, cortes=2, comp=6, passo=6)
            for k in range(3):
                x = b[0] - 14 + 9 * k
                T.linha(d, [(x, b[1] - 6), (x + 1, b[1] + 3)], 1.4, var, sid + 10 + k, alfa=180, suave=False)

    def _orelha(self, d, parte, var, sid, s):
        HP = self.J["HP"]
        perto = parte == "orelha_p"
        bx, by = (HP[0] + 104, HP[1] - 110) if perto else (HP[0] + 48, HP[1] - 108)
        alt = 92
        pts = [(bx - 30, by + 10), (bx - 14, by - alt * 0.6), (bx + 2, by - alt), (bx + 16, by - alt * 0.55), (bx + 30, by + 8)]
        rnd = random.Random(sid)
        pts = tufos(T.catmull(pts, True, 5), 7, rnd, fluxo=(0, -1), onde=lambda x, y: 1.0 if y > by - alt * 0.5 else 0.25)
        vol(d, pts, self.COR if perto else self.COR_ESC, var, sid, ang_pelo=-math.pi / 2, contorno=3.0, cortes=2, comp=8)
        dentro = T.catmull([(bx - 16, by + 4), (bx + 1, by - alt * 0.78), (bx + 16, by + 2)], True, 5)
        T.forma(d, dentro, (96, 78, 80), var, sid + 5, contorno=0, sombra=0.9, passo_h=3.5)
        for k in range(4):  # pelos de dentro da orelha
            T.linha(d, [(bx - 10 + 7 * k, by + 2), (bx - 6 + 4 * k, by - alt * 0.45)], 1.1, var, sid + 10 + k, cor=(170, 160, 150), alfa=200)

    def _cabeca(self, d, var, sid, e, rnd):
        s, boca, pisc, olhar = e
        HP = self.J["HP"]
        cx, cy = HP[0] + 78, HP[1] - 48
        # crânio redondo em 3/4 com bochecha fofa (tufos pra baixo e pra trás)
        pts = [(cx - 70, cy + 10), (cx - 62, cy - 42), (cx - 22, cy - 72), (cx + 30, cy - 70), (cx + 66, cy - 38), (cx + 86, cy - 2),
               (cx + 90, cy + 26), (cx + 70, cy + 52), (cx + 34, cy + 64), (cx - 10, cy + 66), (cx - 52, cy + 50)]
        cab = tufos(T.catmull(pts, True, 7), 12 + 10 * s, rnd, fluxo=(-1, 0.4),
                    onde=lambda x, y: 1.0 if (y > cy + 20 or x < cx - 40) else 0.15)
        vol(d, cab, self.COR, var, sid, ang_pelo=math.pi * 0.9, rim=(122, 116, 110), comp=10, prof=(0.24, 0.1))
        # focinho claro
        foc = T.catmull([(cx + 52, cy + 10), (cx + 88, cy + 6), (cx + 96, cy + 30), (cx + 76, cy + 50), (cx + 48, cy + 44)], True, 5)
        vol(d, foc, T.mistura(self.COR, self.PEITO, 0.5), var, sid + 2, ang_pelo=0.2, contorno=0, sombra=0.6, comp=6, passo=5)
        T.forma(d, T.quina([(cx + 84, cy + 8), (cx + 100, cy + 10), (cx + 92, cy + 22)], True, 3), (64, 46, 50), var, sid + 3,
                contorno=1.8, sombra=0)  # nariz
        # olhos: o de perto maior, o de longe espremido perto da borda
        for k, (ox, oy, r, sx) in enumerate(((cx + 40, cy - 14, 17, 1.0), (cx - 8, cy - 18, 13, 0.7))):
            self._olho(d, ox, oy, r, sx, var, sid + 10 + 5 * k, s, pisc, olhar)
        # boca: fechada em "w"; chiando: aberta com presas, língua e nariz franzido
        if boca > 0.05:
            ab = boca
            bx, by = cx + 80, cy + 34
            m = T.catmull([(bx - 46, by - 2), (bx + 4, by - 6), (bx + 16, by + 4), (bx, by + 18 + 44 * ab), (bx - 36, by + 14 + 30 * ab)], True, 6)
            T.forma(d, m, (30, 12, 18), var, sid + 30, contorno=2.4, sombra=0)
            T.forma(d, T.elipse(bx - 14, by + 12 + 30 * ab, 14, 7 + 6 * ab, 16), (120, 66, 74), var, sid + 31, contorno=0, sombra=0.5,
                    hach=False)
            for k, (px, sentido) in enumerate(((bx - 30, 1), (bx + 2, 1), (bx - 28, -1), (bx, -1))):  # presas
                y0 = by - 2 if sentido > 0 else by + 14 + 40 * ab
                T.forma(d, T.quina([(px - 4, y0), (px + 4, y0), (px, y0 + sentido * (12 + 6 * ab))], True, 3), (226, 218, 196), var,
                        sid + 32 + k, contorno=1.0, sombra=0)
            for k in range(3):  # nariz franzido
                T.linha(d, [(cx + 62 + 8 * k, cy - 4), (cx + 70 + 8 * k, cy + 4)], 1.4, var, sid + 40 + k, alfa=200)
        else:
            T.linha(d, [(cx + 92, cy + 22), (cx + 90, cy + 32), (cx + 78, cy + 38), (cx + 68, cy + 34)], 2.2, var, sid + 33)
            T.linha(d, [(cx + 90, cy + 32), (cx + 98, cy + 38)], 1.8, var, sid + 34)
        for k in range(4):  # bigode
            T.linha(d, [(cx + 80, cy + 26 + 4 * k), (cx + 130, cy + 14 + 10 * k), (cx + 158, cy + 18 + 16 * k)], 1.0, var, sid + 50 + k,
                    cor=(200, 194, 176), alfa=210)
        T.linha(d, [(cx + 30, cy - 38), (cx + 62, cy - 62), (cx + 80, cy - 70)], 0.9, var, sid + 60, cor=(200, 194, 176), alfa=180)

    def _olho(self, d, x, y, r, sx, var, sid, s, pisc, olhar):
        if self.errado:
            _olho_humano(d, x, y, r * 1.2, var, sid, olhar=olhar)
            return
        orb = T.elipse(x, y, r * 1.5 * sx, r * 1.25, 24)
        T.mancha(d, orb, (20, 14, 22), 200, borra=r * 0.3)
        abre = max(0.0, 1.0 - pisc)
        pts = [(x - r * sx, y), (x - r * 0.3 * sx, y - r * 0.95 * abre), (x + r * 0.6 * sx, y - r * 0.75 * abre), (x + r * sx, y + 1),
               (x + r * 0.3 * sx, y + r * 0.7 * abre), (x - r * 0.5 * sx, y + r * 0.6 * abre)]
        if abre > 0.08:
            o = T.catmull(pts, True, 6)
            q, _ = T.tremido(o, var, sid, 0.3, True)
            op = T.caminho(q)
            d.pinta(op, T.tinta_paint(self.OLHO))
            sub = T.Desenho()
            px = x + olhar * r * 0.25 * sx
            lar = r * (0.16 + 0.55 * s)    # fenda que dilata no susto
            sub.pinta(T.caminho(T.elipse(px, y, lar * sx, r * 0.9, 18)), T.tinta_paint((8, 6, 8)))
            sub.pinta(T.caminho(T.elipse(px - r * 0.3, y - r * 0.35, r * 0.13, r * 0.13, 10)), T.tinta_paint((232, 226, 204), 230))
            sub.pinta(T.caminho(np.array([(x - r * 2, y - r * 2), (x + r * 2, y - r * 2), (x + r * 2, y - r * 0.5), (x - r * 2, y - r * 0.3)])),
                      T.tinta_paint((40, 34, 20), 90))
            d.recorte(op, sub)
            d.pinta(T.traco_tinta(q, r * 0.16, var, sid + 1, fechado=True, amp=0.3), T.tinta_paint(T.TINTA))
        # pálpebra de cima (piscada lenta desce até fechar)
        y_t = y - r * 0.95 * abre
        T.linha(d, [(x - r * 1.05 * sx, y - r * 0.1), (x - r * 0.2 * sx, y_t - 1), (x + r * 1.05 * sx, y - r * 0.1 * abre)], r * 0.2, var,
                sid + 2, ponta=(0.1, 0.4))

    def depois(self, c, parte, pose, var):
        if self.errado and parte == "cabeca":
            HP = self.J["HP"]
            self._depois_sorriso(c, (HP[0] + 112, HP[1] - 6), 0.42, 0.75 + 0.35 * pose.get("boca", 0.0), vira=0.55, rot=-6)


# ---------------------------------------------------------------- cachorro

class Cachorro(_Bicho):
    """Vira-lata brasileiro magro: costela aparecendo, barriga chupada, osso do quadril marcado, pernas compridas,
    focinho comprido, orelha meio caída, rabo enrolado pra cima (entre as pernas no susto)."""
    COR, COR_ESC, PEITO, OLHO = (138, 112, 82), (96, 78, 58), (178, 160, 130), (96, 70, 44)

    def _juntas(self):
        k = 1.5 if self.errado else 1.0
        J = {"N": (690.0, 560.0), "T": (300.0, 585.0), "C0": (480.0, 620.0)}

        def perna(nome, base, v1, v2, v3, dxl=0.0):
            b = (base[0] + dxl, base[1])
            J[nome + "0"] = b
            J[nome + "1"] = (b[0] + v1[0] * k, b[1] + v1[1] * k)
            J[nome + "2"] = (J[nome + "1"][0] + v2[0] * k, J[nome + "1"][1] + v2[1] * k)
            J[nome + "3"] = (J[nome + "2"][0] + v3[0], J[nome + "2"][1] + v3[1])
        for lado, dxl in (("d", 0.0), ("e", -24.0)):
            perna("F" + lado, (660.0, 615.0), (-14, 125), (8, 182), (34, 70), dxl)
            perna("H" + lado, (350.0, 610.0), (52, 112), (-78, 160), (34, 112), dxl)
        _nivela(J)
        J["HP"] = (J["N"][0] + 70, J["N"][1] - 250) if self.errado else J["N"]
        return J

    def _partes(self):
        J = self.J
        P = [(f"rabo{i}", "corpo" if i == 1 else f"rabo{i - 1}", (J["T"][0] - 46 * (i - 1), J["T"][1])) for i in range(1, 6)]
        for lado in ("e", "d"):
            P += [(f"fe_braco_{lado}", "corpo", J[f"F{lado}0"]), (f"fe_antebraco_{lado}", f"fe_braco_{lado}", J[f"F{lado}1"]),
                  (f"fe_pata_{lado}", f"fe_antebraco_{lado}", J[f"F{lado}2"]),
                  (f"tr_coxa_{lado}", "corpo", J[f"H{lado}0"]), (f"tr_canela_{lado}", f"tr_coxa_{lado}", J[f"H{lado}1"]),
                  (f"tr_pata_{lado}", f"tr_canela_{lado}", J[f"H{lado}2"])]
            if lado == "e":
                P += [("corpo", "raiz", J["C0"])]
        if self.errado:
            P += [("pescoco", "corpo", J["N"])]
        pai = "pescoco" if self.errado else "corpo"
        P += [("orelha_l", "cabeca", (J["HP"][0] + 40, J["HP"][1] - 100)), ("cabeca", pai, J["HP"]),
              ("orelha_p", "cabeca", (J["HP"][0] + 96, J["HP"][1] - 104))]
        self.PERNAS = {f"pata_f{lado}": (f"fe_braco_{lado}", f"fe_antebraco_{lado}", f"fe_pata_{lado}", f"F{lado}0", f"F{lado}1",
                                         f"F{lado}2", f"F{lado}3", (-1.0, 0.0), 0.0) for lado in ("e", "d")}
        self.PERNAS.update({f"pata_t{lado}": (f"tr_coxa_{lado}", f"tr_canela_{lado}", f"tr_pata_{lado}", f"H{lado}0", f"H{lado}1",
                                              f"H{lado}2", f"H{lado}3", (1.0, 0.0), 0.0) for lado in ("e", "d")})
        return P

    def expr(self, parte, pose):
        s = _q(pose.get("susto", 0))
        if parte == "cabeca":
            return (s, _q(pose.get("boca", 0)), _q(pose.get("piscar", 0), 0.2), _q(pose.get("olhar", 0), 0.5))
        if parte in ("corpo",) or parte.startswith("orelha") or parte.startswith("rabo"):
            return (s,)
        return ()

    def monta(self, parte, d, var, e):
        J = self.J
        rnd = random.Random(T._sem(self.semente, parte))
        sid = T._sem(self.semente, parte, "c") % 100000
        if parte == "corpo":
            self._corpo(d, var, sid, e[0], rnd)
        elif parte.startswith("rabo"):
            i = int(parte[4])
            a = (J["T"][0] - 46 * (i - 1), J["T"][1])
            b = (a[0] - 50, a[1])
            r0, r1 = 11 - 1.4 * (i - 1), 10 - 1.6 * i
            membro(d, a, b, r0, max(3.0, r1), self.COR, var, sid, rnd, pelo=6 + 4 * (i > 3), ang_pelo=math.pi, tampa_fim=(i == 5),
                   fluxo=(-1, 0.3))
        elif parte.startswith("fe_") or parte.startswith("tr_"):
            self._perna(d, parte, var, sid, rnd)
        elif parte.startswith("orelha"):
            self._orelha(d, parte, var, sid, e[0])
        elif parte == "pescoco":
            N, HP = J["N"], J["HP"]
            vol(d, tufos(_tubo(N, HP, 34, 26, 8), 9, rnd, fluxo=(0, 1)), self.COR, var, sid, ang_pelo=math.pi / 2, contorno=3.2)
            for k in range(6):
                u = 0.1 + 0.15 * k
                x, y = N[0] + (HP[0] - N[0]) * u, N[1] + (HP[1] - N[1]) * u
                T.linha(d, [(x - 22, y + 4), (x, y - 3), (x + 22, y + 4)], 1.4, var, sid + 10 + k, alfa=170)
        elif parte == "cabeca":
            self._cabeca(d, var, sid, e, rnd)

    def _corpo(self, d, var, sid, s, rnd):
        top = [(724, 590), (694, 552), (640, 540), (560, 548), (480, 552), (410, 548), (352, 540), (318, 556), (298, 580)]
        fundo = [(286, 612), (304, 660), (360, 672), (420, 632), (480, 614), (540, 640), (600, 690), (660, 706), (712, 680), (734, 630)]
        pts = T.catmull(top + fundo, True, 6)
        pts = tufos(pts, 6 + 22 * s, rnd, fluxo=(-1, -0.2),
                    onde=lambda x, y: (0.4 + 1.6 * s * (1 if 560 < x < 720 else 0.4)) if y < 600 else 0.35)
        vol(d, pts, self.COR, var, sid, ang_pelo=math.pi + 0.2, rim=(196, 180, 150), comp=11)
        peito = tufos(T.catmull([(700, 620), (730, 640), (712, 690), (660, 708), (640, 670)], True, 5), 8, rnd, fluxo=(0, 1))
        vol(d, peito, self.PEITO, var, sid + 20, ang_pelo=math.pi / 2, contorno=0, sombra=0.6, comp=8)
        for k in range(6):  # costelas
            x = 640 - 28 * k
            T.linha(d, [(x, 572), (x - 14, 610), (x - 8, 650 - 4 * k)], 1.8, var, sid + 40 + k, alfa=170)
        T.linha(d, [(372, 548), (346, 576), (362, 608)], 2.2, var, sid + 30, alfa=200)        # osso do quadril
        T.linha(d, [(660, 556), (640, 590), (650, 624)], 2.0, var, sid + 31, alfa=190)        # omoplata
        T.linha(d, [(420, 630), (480, 612), (536, 636)], 1.6, var, sid + 32, alfa=170)        # barriga chupada
        T.mancha(d, T.elipse(420, 580, 70, 26, 20), self.COR_ESC, 110, borra=12)               # malhado

    def _perna(self, d, parte, var, sid, rnd):
        J = self.J
        lado = parte[-1]
        cor = self.COR_ESC if lado == "e" else self.COR
        frente = parte.startswith("fe_")
        L = ("F" if frente else "H") + lado
        if parte.split("_")[1] in ("braco", "coxa"):
            a, b = J[L + "0"], J[L + "1"]
            r0, r1 = (30, 14) if frente else (44, 16)
            membro(d, (a[0], a[1] - 18), b, r0, r1, cor, var, sid, rnd, pelo=6, ang_pelo=math.pi / 2 + 0.3)
        elif "antebraco" in parte or "canela" in parte:
            a, b = J[L + "1"], J[L + "2"]
            membro(d, a, b, 13, 8, cor, var, sid, rnd, pelo=3, ang_pelo=math.pi / 2)
            T.linha(d, [(a[0] - 6, a[1] + 4), (a[0] + 2, a[1] - 3), (a[0] + 8, a[1] + 3)], 1.6, var, sid + 4, alfa=180)  # junta ossuda
        else:
            a, b = J[L + "2"], J[L + "3"]
            pts = [(a[0] - 9, a[1]), (a[0] + 9, a[1] - 2), (b[0] + 10, b[1] - 12), (b[0] + 16, b[1] + 2), (b[0] - 4, b[1] + 6),
                   (b[0] - 26, b[1] + 4), (a[0] - 12, a[1] + 24)]
            vol(d, T.catmull(pts, True, 5), cor, var, sid, ang_pelo=math.pi / 2, contorno=2.8, cortes=2, comp=6, passo=6)
            for k in range(3):
                x = b[0] - 16 + 10 * k
                T.linha(d, [(x, b[1] - 6), (x + 2, b[1] + 4)], 1.4, var, sid + 10 + k, alfa=180, suave=False)
                T.linha(d, [(x + 4, b[1] + 3), (x + 9, b[1] + 6)], 1.8, var, sid + 20 + k, cor=(30, 24, 20), suave=False)  # unhas

    def _orelha(self, d, parte, var, sid, s):
        HP = self.J["HP"]
        perto = parte == "orelha_p"
        bx, by = (HP[0] + 96, HP[1] - 104) if perto else (HP[0] + 40, HP[1] - 100)
        # meio caída: sobe e a ponta dobra pra frente
        pts = [(bx - 26, by + 12), (bx - 16, by - 50), (bx + 2, by - 82), (bx + 28, by - 74), (bx + 18, by - 50), (bx + 26, by + 8)]
        rnd = random.Random(sid)
        pts = tufos(T.catmull(pts, True, 5), 5, rnd, fluxo=(0, -1), onde=lambda x, y: 0.6)
        vol(d, pts, self.COR if perto else self.COR_ESC, var, sid, ang_pelo=-math.pi / 2, contorno=3.0, cortes=2, comp=7)
        T.linha(d, [(bx - 2, by - 70), (bx + 14, by - 60), (bx + 24, by - 72)], 1.8, var, sid + 3, alfa=190)  # dobra da ponta
        T.forma(d, T.catmull([(bx - 12, by + 6), (bx - 4, by - 50), (bx + 12, by + 4)], True, 4), (110, 84, 74), var, sid + 5, contorno=0,
                sombra=0.8, passo_h=3.5)

    def _cabeca(self, d, var, sid, e, rnd):
        s, boca, pisc, olhar = e
        HP = self.J["HP"]
        cx, cy = HP[0] + 80, HP[1] - 48
        alonga = 70 if self.errado else 0
        pts = [(cx - 62, cy + 30), (cx - 58, cy - 34), (cx - 20, cy - 62), (cx + 30, cy - 60), (cx + 60, cy - 36), (cx + 108 + alonga, cy - 14),
               (cx + 150 + alonga, cy - 2), (cx + 158 + alonga, cy + 18), (cx + 128 + alonga, cy + 36), (cx + 70, cy + 52), (cx + 10, cy + 60),
               (cx - 40, cy + 54)]
        cab = tufos(T.catmull(pts, True, 7), 9 + 8 * s, rnd, fluxo=(-1, 0.3), onde=lambda x, y: 1.0 if x < cx - 20 else 0.15)
        vol(d, cab, self.COR, var, sid, ang_pelo=math.pi * 0.95, rim=(196, 180, 150), comp=9, prof=(0.22, 0.09))
        if getattr(self, "mancha_olho", False):   # vira-lata com a mancha escura em volta do olho
            T.mancha(d, T.catmull([(cx + 8, cy - 40), (cx + 50, cy - 50), (cx + 70, cy - 20), (cx + 56, cy + 10), (cx + 14, cy + 6)], True, 6),
                     (40, 32, 28), 230, borra=4)
        T.mancha(d, T.catmull([(cx + 60, cy + 10), (cx + 150 + alonga, cy + 4), (cx + 140 + alonga, cy + 30), (cx + 70, cy + 44)], True, 5),
                 self.PEITO, 120, borra=6)
        nx, ny = cx + 156 + alonga, cy + 4
        T.forma(d, T.elipse(nx, ny, 13, 10, 16), (34, 26, 28), var, sid + 1, contorno=1.6, sombra=0)   # trufa
        if boca > 0.05 or s > 0.4:
            ab = max(boca, 0.35 * s)
            lab = [(cx + 64, cy + 34), (nx - 12, cy + 20), (nx - 6, cy + 30), (nx - 40, cy + 40 + 46 * ab), (cx + 72, cy + 44 + 20 * ab)]
            T.forma(d, T.catmull(lab, True, 5), (30, 12, 18), var, sid + 30, contorno=2.4, sombra=0)
            # dentes à mostra: lábio de cima repuxado no susto
            for k in range(6 if s > 0.4 else 2):
                x = nx - 22 - 13 * k
                T.forma(d, T.quina([(x - 4, cy + 22 + k), (x + 4, cy + 22 + k), (x, cy + 34 + k + (6 if k in (1, 4) else 0))], True, 3),
                        (226, 218, 196), var, sid + 40 + k, contorno=0.9, sombra=0)
            if s < 0.4:  # ofegando: língua pra fora (o balanço é desenhado por quadro em depois())
                pass
            else:
                for k in range(3):  # focinho franzido
                    T.linha(d, [(cx + 90 + 12 * k, cy - 8), (cx + 96 + 12 * k, cy + 2)], 1.4, var, sid + 50 + k, alfa=200)
        else:
            T.linha(d, [(nx - 8, cy + 18), (cx + 104, cy + 30), (cx + 70, cy + 36)], 2.2, var, sid + 31)
        self._olho(d, cx + 36, cy - 18, 14, 1.0, var, sid + 10, s, pisc, olhar)
        self._olho(d, cx - 6, cy - 20, 11, 0.7, var, sid + 16, s, pisc, olhar)
        # sobrancelha: sobe no miolo quando assustado
        T.linha(d, [(cx + 18, cy - 36 + 6 * s), (cx + 36, cy - 42 - 4 * s), (cx + 54, cy - 36)], 2.4, var, sid + 20)

    def _olho(self, d, x, y, r, sx, var, sid, s, pisc, olhar):
        if self.errado:
            _olho_humano(d, x, y, r * 1.35, var, sid, olhar=olhar)
            return
        T.mancha(d, T.elipse(x, y, r * 1.5 * sx, r * 1.3, 20), (34, 24, 22), 190, borra=r * 0.3)
        abre = max(0.0, 1.0 - pisc)
        if abre > 0.08:
            o = T.elipse(x, y, r * sx, r * 0.85 * abre, 20)
            q, _ = T.tremido(o, var, sid, 0.3, True)
            op = T.caminho(q)
            d.pinta(op, T.tinta_paint(self.OLHO))
            sub = T.Desenho()
            px = x + olhar * r * 0.3 * sx
            sub.pinta(T.caminho(T.elipse(px, y, r * 0.55 * sx, r * 0.55, 16)), T.tinta_paint((10, 6, 6)))
            if s > 0.4:  # branco do olho aparecendo (olhar de baleia)
                sub.pinta(T.caminho(T.elipse(x - r * 0.8 * sx, y + r * 0.1, r * 0.5 * sx, r * 0.5, 12)), T.tinta_paint((214, 206, 186)))
            sub.pinta(T.caminho(T.elipse(px - r * 0.25, y - r * 0.3, r * 0.15, r * 0.15, 10)), T.tinta_paint((232, 226, 204), 220))
            d.recorte(op, sub)
            d.pinta(T.traco_tinta(q, r * 0.17, var, sid + 1, fechado=True, amp=0.3), T.tinta_paint(T.TINTA))
        T.linha(d, [(x - r * 1.05 * sx, y - r * 0.05), (x, y - r * 0.9 * abre - 1), (x + r * 1.05 * sx, y - r * 0.15)], r * 0.2, var, sid + 2,
                ponta=(0.1, 0.4))

    def depois(self, c, parte, pose, var):
        HP = self.J["HP"]
        if parte != "cabeca":
            return
        cx, cy = HP[0] + 80, HP[1] - 48
        if self.errado:
            self._depois_sorriso(c, (cx + 110, cy + 22), 0.5, 0.8 + 0.3 * pose.get("boca", 0.0), vira=0.6, rot=-4)
            return
        ofega = pose.get("boca", 0.0)
        if ofega > 0.25 and pose.get("susto", 0.0) < 0.4:  # língua balançando
            t = pose.get("t", 0.0)
            bal = 6 * math.sin(t * 2 * math.pi * 3.2)
            x0, y0 = cx + 118, cy + 38
            lingua = T.catmull([(x0 - 22, y0), (x0 + 6, y0 - 2), (x0 + 10 + bal * 0.4, y0 + 46), (x0 - 4 + bal, y0 + 62),
                                (x0 - 18 + bal, y0 + 48)], True, 6)
            dd = T.Desenho()
            T.forma(dd, lingua, (150, 84, 90), var, 991, contorno=2.2, sombra=0.6, hach=False)
            T.linha(dd, [(x0 - 6, y0 + 4), (x0 - 4 + bal * 0.6, y0 + 44)], 1.2, var, 992, alfa=160)
            dd.desenha(c)


# ---------------------------------------------------------------- aves

class Ave(_Bicho):
    """Corvo, urubu ou pardal, de perfil. Asa com penas separadas que abre, cabeça que vira aos trancos, pulinho."""
    CORES = {"corvo": ((44, 42, 50), (80, 78, 92), (26, 24, 28)), "urubu": ((46, 40, 42), (84, 76, 72), (150, 128, 122)),
             "pardal": ((132, 104, 76), (176, 152, 120), (86, 68, 52))}

    def __init__(self, tipo="corvo", semente=21, errado=False, vetor=False):
        self.tipo = tipo
        super().__init__(semente + {"corvo": 0, "urubu": 1, "pardal": 2}[tipo], errado=errado, vetor=vetor)

    def _args_gemeo(self):
        return dict(tipo=self.tipo, semente=self.semente - {"corvo": 0, "urubu": 1, "pardal": 2}[self.tipo] - (500 if self.errado else 0),
                    errado=not self.errado)

    def _juntas(self):
        k = 1.7 if self.errado else 1.0
        peq = self.tipo == "pardal"
        J = {"C0": (500.0, 700.0), "N": (590.0, 640.0) if not peq else (585.0, 660.0), "Rb": (392.0, 714.0), "Sh": (558.0, 650.0)}
        for lado, dxl in (("d", 0.0), ("e", -16.0)):
            b = (510.0 + dxl, 780.0)
            J["P" + lado + "0"] = b
            J["P" + lado + "1"] = (b[0] - 28 * k, b[1] + (88 if not peq else 70) * k)
            J["P" + lado + "2"] = (J["P" + lado + "1"][0] + 26 * k, J["P" + lado + "1"][1] + (108 if not peq else 80) * k)
            J["P" + lado + "3"] = (J["P" + lado + "2"][0] + 50, J["P" + lado + "2"][1] + 14)
        J["_chao"] = J["Pd2"][1] + 15
        pesc = {"corvo": 0, "pardal": 0, "urubu": 60}[self.tipo]
        J["HP"] = (J["N"][0] + 40, J["N"][1] - 300) if self.errado else (J["N"][0] + pesc * 0.3, J["N"][1] - pesc)
        return J

    def _partes(self):
        J = self.J
        P = []
        for lado in ("e", "d"):
            P += [(f"tibio_{lado}", "corpo", J[f"P{lado}0"]), (f"tarso_{lado}", f"tibio_{lado}", J[f"P{lado}1"]),
                  (f"dedos_{lado}", f"tarso_{lado}", J[f"P{lado}2"])]
            if lado == "e":
                P += [("rabo", "corpo", J["Rb"]), ("corpo", "raiz", J["C0"])]
        if self.errado or self.tipo == "urubu":
            P += [("pescoco", "corpo", J["N"])]
        pai = "pescoco" if (self.errado or self.tipo == "urubu") else "corpo"
        P += [("asa", "corpo", J["Sh"]), ("cabeca", pai, J["HP"])]
        # asa por cima do corpo e da perna de perto: reordena pra perna de perto vir antes da asa
        self.PERNAS = {f"pe_{lado}": (f"tibio_{lado}", f"tarso_{lado}", f"dedos_{lado}", f"P{lado}0", f"P{lado}1", f"P{lado}2",
                                      f"P{lado}3", (-1.0, 0.0), 0.0) for lado in ("e", "d")}
        return P

    def resolve(self, pose):
        pose = super().resolve(pose)
        # dedos sempre retos no chão (mesmo com o tarso girado)
        rot_c = (pose.get("corpo") or {}).get("rot", 0.0)
        for lado in ("e", "d"):
            soma = rot_c + (pose.get(f"tibio_{lado}") or {}).get("rot", 0.0) + (pose.get(f"tarso_{lado}") or {}).get("rot", 0.0)
            pose[f"dedos_{lado}"] = {**(pose.get(f"dedos_{lado}") or {}), "rot": -soma + (pose.get("_dedos_rot") or 0.0)}
        return pose

    def expr(self, parte, pose):
        s = _q(pose.get("susto", 0))
        if parte == "cabeca":
            return (s, _q(pose.get("boca", 0)), _q(pose.get("piscar", 0), 0.5), _q(pose.get("olhar", 0), 0.5))
        if parte == "asa":
            return (s, _q(pose.get("asa", 0), 0.125))
        if parte in ("corpo", "rabo"):
            return (s,)
        return ()

    def monta(self, parte, d, var, e):
        cor, claro, extra = self.CORES[self.tipo]
        J = self.J
        rnd = random.Random(T._sem(self.semente, parte))
        sid = T._sem(self.semente, parte, "a") % 100000
        peq = self.tipo == "pardal"
        if parte == "corpo":
            s = e[0]
            g = 1 + 0.18 * s
            cx, cy = 500, 712
            pts = [(cx + 120 * g, cy - 62), (cx + 92 * g, cy - 96 * g), (cx + 10, cy - 104 * g), (cx - 70 * g, cy - 74), (cx - 118, cy - 6),
                   (cx - 96, cy + 34), (cx - 20, cy + 78 * g), (cx + 60, cy + 70 * g), (cx + 112 * g, cy + 24), (cx + 128 * g, cy - 22)]
            if peq:
                pts = [(x * 1.0, y) for x, y in pts]
            base = tufos(T.catmull(pts, True, 7), 10 + 18 * s, rnd, fluxo=(-1, 0.3), onde=lambda x, y: 0.5 if y > cy - 40 else 0.25)
            vol(d, base, cor, var, sid, ang_pelo=math.pi + 0.3, rim=claro, comp=10)
            if peq:   # peito claro e rajado
                T.mancha(d, T.elipse(cx + 70, cy + 10, 52, 60, 20), (200, 182, 150), 170, borra=10)
                for k in range(8):
                    x, y = cx + 50 + rnd.uniform(-20, 40), cy - 20 + rnd.uniform(0, 70)
                    T.linha(d, [(x, y), (x - 4, y + 9)], 1.6, var, sid + 30 + k, cor=(96, 76, 56), alfa=200, suave=False)
            if self.tipo == "urubu":  # gola de penas fofas
                gola = tufos(T.elipse(cx + 96, cy - 70, 46, 30, 24), 12, rnd, fluxo=(0, 1))
                vol(d, gola, T.mistura(cor, claro, 0.3), var, sid + 40, ang_pelo=math.pi / 2, contorno=2.6, comp=8)
        elif parte == "rabo":
            if peq:
                penas = [((392, 714), (280, 690)), ((392, 720), (276, 706)), ((392, 726), (282, 724))]
            else:
                penas = [((392, 710), (232, 742)), ((394, 716), (226, 762)), ((396, 722), (234, 782)), ((398, 728), (248, 798))]
            for k, (a, b) in enumerate(penas):
                pts = _tubo(a, b, 14, 10, 6)
                T.forma(d, pts, T.escurece(cor, 0.9 + 0.04 * k), var, sid + k, contorno=2.4, sombra=0.6, hach=False, amp=0.6)
                T.linha(d, [a, b], 1.1, var, sid + 10 + k, cor=claro, alfa=150)
        elif parte.startswith("tibio"):
            a, b = J["P" + parte[-1] + "0"], J["P" + parte[-1] + "1"]
            pts = tufos(_tubo((a[0], a[1] - 10), b, 22, 9, 6), 8, rnd, fluxo=(0, 1), onde=lambda x, y: 1.0 if y < a[1] + 30 else 0.0)
            vol(d, pts, T.escurece(cor, 0.9 if parte[-1] == "d" else 0.7), var, sid, ang_pelo=math.pi / 2, contorno=2.6, comp=7, cortes=2)
        elif parte.startswith("tarso"):
            a, b = J["P" + parte[-1] + "1"], J["P" + parte[-1] + "2"]
            pele = (60, 52, 48) if not peq else (120, 92, 70)
            T.forma(d, _tubo(a, b, 6, 5, 6), pele, var, sid, contorno=2.2, sombra=0.4, hach=False, amp=0.4)
            for k in range(6):  # escamas
                u = (k + 0.5) / 6
                x, y = a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u
                T.linha(d, [(x - 5, y), (x + 5, y + 1)], 1.0, var, sid + 10 + k, alfa=160, suave=False)
            T.forma(d, T.elipse(a[0], a[1], 8, 8, 12), pele, var, sid + 30, contorno=1.6, sombra=0.4, hach=False)  # junta
        elif parte.startswith("dedos"):
            b = J["P" + parte[-1] + "2"]
            pele = (60, 52, 48) if not peq else (120, 92, 70)
            for k, (dx, dy) in enumerate(((54, 14), (40, 16), (-34, 12))):
                T.linha(d, [b, (b[0] + dx * 0.55, b[1] + dy * 0.8), (b[0] + dx, b[1] + dy)], 4.2, var, sid + k, cor=pele, ponta=(0.0, 0.3))
                T.linha(d, [(b[0] + dx, b[1] + dy), (b[0] + dx * 1.14, b[1] + dy + 4)], 2.2, var, sid + 10 + k, cor=(20, 16, 14),
                        ponta=(0.0, 0.8), suave=False)  # unha
        elif parte == "asa":
            self._asa(d, var, sid, e[0], e[1], cor, claro, rnd)
        elif parte == "pescoco":
            N, HP = J["N"], J["HP"]
            pele = extra if self.tipo == "urubu" else cor
            pts = _tubo(N, HP, 26, 16, 8)
            if self.tipo != "urubu":
                pts = tufos(pts, 8, rnd, fluxo=(0, 1))
            vol(d, pts, pele, var, sid, ang_pelo=math.pi / 2, contorno=2.8, comp=7, pelo=self.tipo != "urubu")
            for k in range(int(math.hypot(HP[0] - N[0], HP[1] - N[1]) / 22)):
                u = (k + 0.5) / max(1, int(math.hypot(HP[0] - N[0], HP[1] - N[1]) / 22))
                x, y = N[0] + (HP[0] - N[0]) * u, N[1] + (HP[1] - N[1]) * u
                T.linha(d, [(x - 14, y + 3), (x, y - 2), (x + 14, y + 3)], 1.2, var, sid + 10 + k, alfa=150)  # rugas
        elif parte == "cabeca":
            self._cabeca(d, var, sid, e, cor, claro, extra, rnd)

    def _asa(self, d, var, sid, s, abre, cor, claro, rnd):
        sx, sy = self.J["Sh"]
        escura = T.escurece(cor, 0.85)
        n = 7
        if abre <= 0.06:
            # dobrada: coberteiras em cima, primárias compridas e separadas na ponta
            cob = [(sx + 16, sy - 6), (sx + 30, sy + 40), (sx - 40, sy + 92), (sx - 130, sy + 108), (sx - 150, sy + 80), (sx - 80, sy + 26)]
            for k in range(n):
                a0 = (sx - 60 - 12 * k, sy + 60 + 6 * k)
                b0 = (sx - 210 - 10 * k + rnd.uniform(-6, 6), sy + 104 + 7 * k)
                T.forma(d, T.catmull([a0, ((a0[0] + b0[0]) / 2, a0[1] + 8), b0, ((a0[0] + b0[0]) / 2 + 6, a0[1] + 26)], True, 4), escura, var,
                        sid + k, contorno=2.2, sombra=0.5, hach=False, amp=0.5)
                T.linha(d, [a0, b0], 1.0, var, sid + 20 + k, cor=claro, alfa=140)
            vol(d, tufos(T.catmull(cob, True, 6), 8, rnd, fluxo=(-1, 0.4)), cor, var, sid + 40, ang_pelo=math.pi + 0.4, rim=claro, comp=9)
            for k in range(3):
                T.linha(d, [(sx - 10 - 28 * k, sy + 30 + 10 * k), (sx - 60 - 28 * k, sy + 70 + 8 * k)], 1.3, var, sid + 50 + k, cor=claro, alfa=160)
            return
        # aberta: braço da asa sobe; primárias em leque, separadas como dedos (o urubu abre mais)
        L = (300 if self.tipo != "pardal" else 210) * (0.55 + 0.45 * abre)
        base = [(sx + 20, sy + 10), (sx - 30, sy + 40)]
        penas = []
        for k in range(n + 2):
            u = k / (n + 1)
            ang = math.radians(-150 + 85 * u * abre - 10 * (1 - abre))
            comp = L * (1.0 - 0.45 * u)
            raiz = (sx - 20 - 60 * u, sy - 10 + 30 * u)
            ponta = (raiz[0] + math.cos(ang) * comp, raiz[1] + math.sin(ang) * comp)
            penas.append((raiz, ponta, comp))
        cob = [(sx + 24, sy + 8), (sx + 4, sy - L * 0.35), (penas[2][1][0] * 0.5 + sx * 0.5, penas[2][1][1] * 0.5 + sy * 0.5),
               (penas[6][1][0] * 0.4 + sx * 0.6, penas[6][1][1] * 0.4 + sy * 0.6), (sx - 80, sy + 34)]
        for k, (raiz, ponta, comp) in enumerate(reversed(penas)):
            larg = 14 - k * 0.6
            pts = _tubo(raiz, ponta, larg, larg * 0.55, 6)
            T.forma(d, pts, escura, var, sid + 60 + k, contorno=2.2, sombra=0.5, hach=False, amp=0.5)
            T.linha(d, [raiz, ponta], 1.0, var, sid + 80 + k, cor=claro, alfa=150)
        vol(d, tufos(T.catmull(cob, True, 6), 9, rnd, fluxo=(-0.5, 1)), cor, var, sid + 100, ang_pelo=math.pi / 2, rim=claro, comp=9)

    def _cabeca(self, d, var, sid, e, cor, claro, extra, rnd):
        s, boca, pisc, olhar = e
        HP = self.J["HP"]
        urubu, peq = self.tipo == "urubu", self.tipo == "pardal"
        cx, cy = HP[0] + 46, HP[1] - 44
        r = 50 if not peq else 46
        cab = T.elipse(cx, cy, r, r * 0.92, 32)
        if not urubu:
            cab = tufos(cab, 7 + 10 * s, rnd, fluxo=(-1, 0), onde=lambda x, y: 1.0 if x < cx else 0.2)
        vol(d, cab, extra if urubu else cor, var, sid, ang_pelo=math.pi, rim=claro, comp=8, pelo=not urubu)
        if urubu:  # pele pelada enrugada
            for k in range(5):
                T.linha(d, [(cx - 30 + 12 * k, cy - 30), (cx - 26 + 12 * k, cy + 10), (cx - 30 + 12 * k, cy + 30)], 1.2, var, sid + 30 + k, alfa=150)
        comp = {"corvo": 118, "urubu": 92, "pardal": 50}[self.tipo]
        grosso = {"corvo": 32, "urubu": 22, "pardal": 18}[self.tipo]
        bx, by = cx + r * 0.75, cy + 2
        ab = boca
        gancho = 18 if urubu else 0
        cima = [(bx, by - grosso * 0.6), (bx + comp * 0.6, by - grosso * 0.45), (bx + comp, by + 2 + gancho), (bx + comp * 0.85, by + 6),
                (bx + comp * 0.4, by + 2), (bx, by + 4)]
        baixo = [(bx, by + 4), (bx + comp * 0.8, by + 6 + ab * 40), (bx + comp * 0.3, by + grosso * 0.55 + ab * 22), (bx, by + grosso * 0.5)]
        bico = (70, 64, 60) if not peq else (110, 92, 58)
        if ab > 0.05:
            T.forma(d, T.catmull([(bx, by + 2), (bx + comp * 0.9, by + 6), (bx + comp * 0.75, by + 8 + ab * 36), (bx, by + 10)], True, 5),
                    (28, 12, 16), var, sid + 4, contorno=1.6, sombra=0)
        T.forma(d, T.quina(cima, True, 4), bico, var, sid + 1, contorno=2.4, sombra=0.6, hach=False)
        T.forma(d, T.quina(baixo, True, 4), T.escurece(bico, 0.85), var, sid + 2, contorno=2.4, sombra=0.6, hach=False)
        T.linha(d, [(bx + 8, by - grosso * 0.2), (bx + comp * 0.3, by - grosso * 0.25)], 1.2, var, sid + 3, cor=claro, alfa=160)  # narina
        ox, oy = cx + 10, cy - 10
        if self.errado:
            _olho_humano(d, ox, oy, 19, var, sid + 10, olhar=olhar)
            return
        T.mancha(d, T.elipse(ox, oy, 15, 13, 16), (14, 10, 12), 180, borra=4)
        if pisc > 0.5:
            T.linha(d, [(ox - 9, oy), (ox, oy + 3), (ox + 9, oy)], 2.2, var, sid + 11)
        else:
            T.forma(d, T.elipse(ox, oy, 9, 9, 16), (24, 20, 22) if not urubu else (120, 70, 50), var, sid + 12, contorno=1.8, sombra=0, amp=0.2)
            d.pinta(T.caminho(T.elipse(ox + olhar * 2, oy, 4.5, 4.5, 12)), T.tinta_paint((6, 4, 6)))
            d.pinta(T.caminho(T.elipse(ox - 3, oy - 3, 2.2, 2.2, 8)), T.tinta_paint((236, 228, 210), 230))
        if s > 0.4:
            T.linha(d, [(ox - 14, oy - 14), (ox, oy - 18), (ox + 14, oy - 12)], 2.0, var, sid + 13)

    def depois(self, c, parte, pose, var):
        if self.errado and parte == "cabeca":
            HP = self.J["HP"]
            r = 50 if self.tipo != "pardal" else 46
            self._depois_sorriso(c, (HP[0] + 46 + r * 0.3, HP[1] - 44 + 26), 0.3, 0.8, vira=0.65, rot=-8)


# ---------------------------------------------------------------- vida

def _piscada_lenta(t, piscadas, dur=0.55):
    """Piscada lenta de gato: fecha devagar, segura, abre devagar (0..1)."""
    for b in piscadas:
        u = (t - b) / dur
        if 0 <= u < 1:
            return math.sin(math.pi * u) ** 0.7
    return 0.0


def pose_viva(bicho, t, susto=0.0, errado=False, vira=0.0, rabo=1.0, piscadas=(0.9, 3.1, 4.4, 6.8), extra=None, boca=None,
              ofega=None, asa=None, pulinho=False):
    """Pose com vida pronta pro bicho. Gato: rabo em S, respiração, piscada lenta, orelhas que mexem; no susto
    arqueia, eriça, deita as orelhas e chia. Cachorro: rabo e orelhas, ofegando; no susto encolhe, rabo entre as
    pernas, dente à mostra. Ave: trancos de cabeça, asa (abre com `asa`), pulinho."""
    s = susto
    p = {"t": t, "susto": s, "errado": errado, "olhar": 0.6 * math.sin(t * 1.3)}
    if isinstance(bicho, Gato):
        resp = math.sin(t * 2 * math.pi / (0.6 if s > 0.5 else 2.6))
        p["piscar"] = 0.0 if s > 0.3 else _piscada_lenta(t, piscadas)
        p["boca"] = s * (0.75 + 0.25 * math.sin(t * 9)) if boca is None else boca      # chiado
        p["corpo"] = {"dy": -42 * s, "sy": 1 + 0.014 * resp, "rot": -2 * s}
        p["_inclina_pata"] = 0.0
        p["cabeca"] = {"rot": vira + 3 * math.sin(t * 1.1) + s * (10 + 2 * math.sin(t * 31)), "dy": 14 * s}
        ore = -52 * s + (6 * math.sin(t * 0.7) if s < 0.3 else 0) + (12 if 1.9 < (t % 4.0) < 2.1 and s < 0.3 else 0)
        p["orelha_p"] = {"rot": ore}
        p["orelha_l"] = {"rot": ore * 0.9}
        # rabo em S: base sobe, onda passa pelos gomos
        base_rot = [52, 22, 8, -22, -30, 12] if s < 0.5 else [84, 6, 2, -4, -6, -4]
        for i in range(6):
            onda = (14 - 6 * s) * math.sin(t * (1.6 + 4 * s) - 0.9 * i) * rabo
            p[f"rabo{i + 1}"] = {"rot": base_rot[i] * (1 - s) + [84, 6, 2, -4, -6, -4][i] * s + onda * (0.4 if i == 0 else 1.0)}
        p["pes"] = {"pata_fd": (6 * s, 0), "pata_fe": (-4 * s, 0), "pata_td": (-6 * s, 0), "pata_te": (4 * s, 0)}
    elif isinstance(bicho, Cachorro):
        of = (0.0 if s > 0.4 else 0.55) if ofega is None else ofega
        resp = math.sin(t * 2 * math.pi * (3.2 if of > 0.2 else 0.4))
        p["piscar"] = _piscada_lenta(t, piscadas, 0.18)
        p["boca"] = (of * (0.8 + 0.2 * resp) if s < 0.4 else 0.4 + 0.1 * math.sin(t * 6)) if boca is None else boca
        p["corpo"] = {"dy": 64 * s, "rot": -7 * s, "sy": 1 + (0.02 if of > 0.2 else 0.012) * resp}
        p["cabeca"] = {"rot": vira + 2 * math.sin(t * 0.9) + 14 * s, "dy": 16 * s}
        ore = -60 * s + 8 * math.sin(t * 0.6)
        p["orelha_p"] = {"rot": ore}
        p["orelha_l"] = {"rot": ore}
        if s < 0.5:
            base_rot = [62, 36, 34, 40, 30]
            for i in range(5):
                p[f"rabo{i + 1}"] = {"rot": base_rot[i] + 16 * math.sin(t * 5.0 - 0.8 * i) * rabo}
        else:  # entre as pernas
            for i, r_ in enumerate([-118, 22, 24, 16, 8]):
                p[f"rabo{i + 1}"] = {"rot": r_ + 3 * math.sin(t * 9 - i)}
        p["pes"] = {"pata_fd": (-10 * s, 0), "pata_fe": (-14 * s, 0), "pata_td": (16 * s, 0), "pata_te": (12 * s, 0)}
    else:  # Ave
        # trancos: a cabeça segura uma posição e pula pra outra em 2 quadros
        passo = int(t * 2.3)
        alvo = [0, -14, 8, -6, 16, -10, 4][passo % 7]
        p["cabeca"] = {"rot": vira + alvo + (2 * math.sin(t * 40) if s > 0.5 else 0)}
        p["piscar"] = 1.0 if any(0 <= t - b < 0.08 for b in piscadas) else 0.0
        p["boca"] = 0.0 if boca is None else boca
        p["asa"] = (0.15 * s if asa is None else asa)
        resp = math.sin(t * 2 * math.pi / (0.5 if s > 0.5 else 1.6))
        p["corpo"] = {"sy": 1 + 0.015 * resp, "dy": 14 * s}
        p["rabo"] = {"rot": 4 * math.sin(t * 3.1) * rabo + (8 if passo % 3 == 0 else 0)}
        if pulinho:
            u = (t % 1.4) / 1.4
            if u < 0.18:      # agacha
                p["corpo"]["dy"] += 26 * math.sin(math.pi * u / 0.18)
            elif u < 0.48:    # no ar: pés recolhidos
                v = (u - 0.18) / 0.3
                p["pulo"] = 120 * math.sin(math.pi * v)
                p["pes"] = {"pe_d": (8, -50 * math.sin(math.pi * v)), "pe_e": (8, -50 * math.sin(math.pi * v))}
                p["asa"] = max(p["asa"], 0.35 * math.sin(math.pi * v))
            elif u < 0.6:     # pousa amortecendo
                p["corpo"]["dy"] += 20 * math.sin(math.pi * (u - 0.48) / 0.12)
    if extra:
        for k, v in extra.items():
            p[k] = {**p.get(k, {}), **v} if isinstance(v, dict) and isinstance(p.get(k), dict) else v
    return p


class ViraLata(Cachorro):
    """Vira-lata magro, com a mancha escura em volta do olho."""
    mancha_olho = True
