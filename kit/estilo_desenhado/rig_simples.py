# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Rig hierárquico mínimo para o que não é gente do molde (ameaças e bichos): partes com pai, pivô e uma função
que monta a peça de papel da parte. Pose por parte {"rot", "dx", "dy", "sx", "sy"} como no rig.Boneco.

Cada parte é montada uma vez por expressão e guardada em cache: por quadro só se pinta. Cada peça projeta a sombra
dura na de baixo (sempre pro mesmo lado da tela) e, com `t` na pose, é recolocada com um tremidinho a cada pose do
stop motion.
"""
import math

import skia

from . import tinta as T


class RigSimples:
    """Subclasses definem PARTES = [(nome, pai, (px, py))] na ordem de desenho, PES = (x, y) e o método
    monta(parte, d, var, expr). `expr(parte, pose)` devolve a tupla de expressão que muda o desenho daquela parte
    (a chave do cache)."""

    PARTES = []
    PES = (500.0, 1000.0)
    ALTURA = 1000.0
    ESCALA = {}          # escala fixa por parte (ex.: cabeça maior), aplicada em volta do pivô

    def __init__(self, semente=1, vetor=False):
        self.semente = semente
        self.vetor = vetor          # True: caminhos ao vivo; False: cada parte vira textura em cache (bem mais rápido)
        self.rig = {n: (pai, piv) for n, pai, piv in self.PARTES}
        self.ordem = [n for n, _, _ in self.PARTES]
        self.cache = T.Cache()

    def expr(self, parte, pose):
        return ()

    def monta(self, parte, d, var, expr):
        raise NotImplementedError

    def _local(self, parte, pose):
        _, (px, py) = self.rig[parte]
        q = pose.get(parte) if isinstance(pose.get(parte), dict) else {}
        m = skia.Matrix()
        m.preTranslate(q.get("dx", 0.0), q.get("dy", 0.0))
        m.preTranslate(px, py)
        m.preRotate(q.get("rot", 0.0))
        k = self.ESCALA.get(parte, 1.0)
        m.preScale(q.get("sx", 1.0) * k, q.get("sy", 1.0) * k)
        m.preTranslate(-px, -py)
        return m

    def _mundo(self, parte, pose, cache):
        if parte in cache:
            return cache[parte]
        pai, _ = self.rig[parte]
        base = self._mundo(pai, pose, cache) if pai in self.rig else cache["_raiz"]
        m = skia.Matrix.Concat(base, self._local(parte, pose))
        cache[parte] = m
        return m

    def _raiz(self, x, y, altura, pose):
        s = altura / self.ALTURA
        px, py = self.PES
        e = pose.get("estica", 1.0)
        m = skia.Matrix()
        m.preTranslate(x, y)
        m.preScale(s * pose.get("lado", 1), s)
        m.preTranslate(0, -pose.get("pulo", 0.0))
        m.preRotate(pose.get("corpo_rot", 0.0))
        m.preScale(1 / math.sqrt(e), e)
        m.preTranslate(-px, -py)
        return m

    def ponto(self, parte, xy, x, y, altura, pose=None):
        """Onde um ponto do mundo da parte cai na tela nesta pose (prender coisa na mão, na boca...)."""
        pose = pose or {}
        m = self._mundo(parte, pose, {"_raiz": self._raiz(x, y, altura, pose)})
        return m.mapXY(*xy)

    def antes(self, c, parte, pose, var):
        """Gancho por parte, chamado já na matriz da parte e antes do desenho em cache (brilhos que mudam por quadro)."""

    def depois(self, c, parte, pose, var):
        """Gancho por parte, chamado depois do desenho em cache."""

    def desenhar(self, c, x, y, altura, pose=None, partes=None, sombra=True):
        pose = pose or {}
        t = pose.get("t")
        var = 0
        sx, sy = T.sombra_px(altura)
        if sombra and partes is None and T.com_sombra():   # sombra no chão: elipse de papel escuro, dura
            s = altura / self.ALTURA
            c.drawOval(skia.Rect.MakeLTRB(x - 150 * s + sx * 2, y - 9 * s, x + 150 * s + sx * 2, y + 12 * s),
                       skia.Paint(AntiAlias=True, Color=T.cor_sombra(0.8)))
        somb = (sx * 0.75, sy * 0.75) if sombra and partes is None else None
        cache = {"_raiz": self._raiz(x, y, altura, pose)}
        esc = None if self.vetor else 1.15 * c.getTotalMatrix().getMaxScale() * altura / self.ALTURA * max(self.ESCALA.values() or [1.0])
        for parte in self.ordem:
            if partes is not None and parte not in partes:
                continue
            q = pose.get(parte)
            if isinstance(q, dict) and q.get("some"):
                continue
            m = self._mundo(parte, pose, cache)
            c.save()
            c.concat(m)
            if t is not None:   # recoloca a peça a cada pose do stop motion
                dx, dy, g = T.recoloca(t, (self.semente, parte), amp=0.8, giro=0.4)
                px, py = self.rig[parte][1]
                c.translate(px + dx, py + dy)
                c.rotate(g)
                c.translate(-px, -py)
            self.antes(c, parte, pose, var)
            e = self.expr(parte, pose)
            chave = (parte, e)
            self.cache.pega(chave, lambda d, p=parte, e=e: self.monta(p, d, var, e)).pinta_em(c, esc, somb)
            self.depois(c, parte, pose, var)
            c.restore()
