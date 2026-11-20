# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Base do rig usada pelo estilo desenhado: a cinemática do boneco (matrizes por parte, com hierarquia e pivôs) e a
boca de sorriso (`_sorriso`, de compatibilidade; a ameaça do papel usa o rasgo dela). Fica aqui dentro para o pacote não depender de nenhum outro módulo do kit.
"""
import math

import skia

R_CABECA, BOCA_ABAIXO = 240.0, 150.0  # cabeça do molde: raio e distância do centro dela até a boca
R_ROSTO = math.sqrt(R_CABECA ** 2 - BOCA_ABAIXO ** 2)  # meia-largura da cabeça na altura da boca (~187)
R_DENTES = 210.0                     # raio em que os dentes são repartidos por ângulo (estreitam nos cantos)
SORRISO_W = 190.0                    # meia-largura do sorriso (de orelha a orelha)
DENTES_FILA = 16                     # dentes por fileira (par: a linha do meio cai entre os dois incisivos)
COR_FUNDO, COR_GARGANTA = (18, 6, 8), (4, 0, 2)
COR_GENGIVA, COR_DENTE, COR_RISCO = (104, 34, 46), (236, 230, 214), (112, 98, 86)


def _sorriso(c, cx, by, abre=1.0, vira=0.0):
    """Sorriso de orelha a orelha com dentes demais, em coordenadas do molde (cabeça de raio 240, boca em by).

    `abre` de 0 (dentes quase cerrados) a 1 (escancarado). `vira` = seno do giro da cabeça (-1..1, 0 = de frente);
    `cx` é o eixo da cabeça, então de frente o centro da boca fica em cx e, virada, em cx + R_ROSTO * vira.
    A boca é desenhada na esfera da cabeça: virada, cada ponto gira no círculo da cabeça naquela altura, então nada
    passa da borda do rosto. Os dentes nascem nos lábios (amostrados ao longo da curva de cima e da de baixo), ficam
    em pé no eixo da cabeça e são repartidos por ângulo: estreitam nos cantos e do lado que se afasta no 3/4.
    Tudo é recortado pela forma da boca; gengiva, sombra no fundo e na base dos dentes."""
    abre = max(0.0, min(1.2, abre))
    w, h = SORRISO_W, 14 + 30 * abre       # cabe no rosto: o lábio de baixo para antes do queixo
    giro = math.asin(max(-0.95, min(0.95, vira)))

    def cima(u):    # lábio de cima: a mesma quadrática de antes, (cx-w, by-34) -> controle (cx, by+30) -> (cx+w, by-34)
        return by - 34 + 32 * (1 - (u / w) ** 2)

    def baixo(u):   # lábio de baixo: quadrática (w, by-34) -> controle (0,55w, by+h+34) -> (0, by+h+26), espelhada
        q = min(1.0, abs(u) / w)
        t = (-0.9 + math.sqrt(0.81 - 0.4 * (q - 1))) / 0.2
        return (1 - t) ** 2 * (by - 34) + 2 * t * (1 - t) * (by + h + 34) + t * t * (by + h + 26)

    def proj(u, y):  # da boca vista de frente (u = distância ao centro) para a tela, com o giro da cabeça na esfera
        r = math.sqrt(max(1.0, R_CABECA ** 2 - (y - (by - BOCA_ABAIXO)) ** 2))  # meia-largura da cabeça nessa altura
        a = math.asin(max(-1.0, min(1.0, u / r))) + giro
        lim = math.asin(max(0.0, (r - 8) / r))  # o contorno do lábio (12 de espessura) para dentro da borda do rosto
        return skia.Point(cx + r * math.sin(max(-lim, min(lim, a))), y)

    def poli(pontos, fecha=False):
        p = skia.Path()
        p.moveTo(pontos[0])
        for q in pontos[1:]:
            p.lineTo(q)
        if fecha:
            p.close()
        return p

    n = 72
    us = [-w + 2 * w * k / n for k in range(n + 1)]
    labio_cima = [proj(u, cima(u)) for u in us]
    labio_baixo = [proj(u, baixo(u)) for u in reversed(us)]
    boca = poli(labio_cima + labio_baixo, fecha=True)

    def cheio(cor, a=255, **kw):
        return skia.Paint(AntiAlias=True, Color=skia.Color(*cor, a), **kw)

    def traco(cor, larg, a=255, **kw):
        return skia.Paint(AntiAlias=True, Color=skia.Color(*cor, a), Style=skia.Paint.kStroke_Style, StrokeWidth=larg,
                          StrokeJoin=skia.Paint.kRound_Join, StrokeCap=skia.Paint.kRound_Cap, **kw)

    c.drawPath(boca, cheio(COR_FUNDO))
    c.save()
    c.clipPath(boca, doAntiAlias=True)
    meio = proj(0.0, (cima(0.0) + baixo(0.0)) / 2)
    c.drawPath(boca, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
        meio, w * 0.7, [skia.Color(*COR_GARGANTA, 255), skia.Color(*COR_FUNDO, 0)])))  # fundo da boca mais escuro
    c.drawPath(poli(labio_cima), traco(COR_GENGIVA, 22))   # gengiva: só a metade de dentro aparece (clip)
    c.drawPath(poli(labio_baixo), traco(COR_GENGIVA, 22))

    # Até onde cabem dentes: os cantos fecham, então a fileira para onde a boca fica fina demais.
    vao0 = baixo(0.0) - cima(0.0)
    ut = next((u for u in (w * (1 - k / 200) for k in range(200)) if baixo(u) - cima(u) >= max(8.0, 0.16 * vao0)), w * 0.8)
    amax = math.asin(ut / R_DENTES)
    da = 2 * amax / DENTES_FILA
    folga = 0.06 * da
    raiz = 7.0                              # a raiz fica escondida embaixo do contorno do lábio e da gengiva
    risco = traco(COR_RISCO, 2.4)
    vs = [k / 7 for k in range(8)]
    for fila, labio, dirc, frac in ((0, cima, 1.0, 0.56 - 0.14 * abre), (1, baixo, -1.0, 0.42 - 0.12 * abre)):
        for k in range(DENTES_FILA):
            a0, a1 = -amax + k * da + folga, -amax + (k + 1) * da - folga
            am = (a0 + a1) / 2
            frente = math.cos(am + giro)
            if frente < 0.08:               # do outro lado da cabeça: não aparece
                continue
            ue = [R_DENTES * math.sin(a0 + v * (a1 - a0)) for v in vs]
            vao = [baixo(u) - cima(u) for u in ue]
            comp = [max(3.0, g * frac - raiz) for g in vao]
            arred = [math.sin(math.pi * v) ** 0.5 for v in vs]   # 0 nas quinas, 1 no meio: quinas arredondadas
            pts = [proj(u, labio(u) + dirc * (raiz + 3 * (1 - r))) for u, r in zip(ue, arred)]
            pts += [proj(u, labio(u) + dirc * (raiz + L * (0.82 + 0.18 * r))) for u, L, r in reversed(list(zip(ue, comp, arred)))]
            dente = poli(pts, fecha=True)
            luz = (0.70 + 0.30 * frente) * (1.0 if fila == 0 else 0.9)   # cantos e fileira de baixo na sombra
            base = tuple(int(v * luz) for v in COR_DENTE)
            sombra = tuple(int(v * 0.6) for v in base)
            um = R_DENTES * math.sin(am)
            p0 = proj(um, labio(um) + dirc * raiz)
            p1 = proj(um, labio(um) + dirc * (raiz + max(3.0, (baixo(um) - cima(um)) * frac - raiz)))
            c.drawPath(dente, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear(
                [p0, p1], [skia.Color(*sombra), skia.Color(*base), skia.Color(*base)], [0.0, 0.45, 1.0])))
            c.drawPath(dente, risco)
    # sombra de dentro, junto dos lábios: escurece a base dos dentes e a gengiva
    c.drawPath(boca, traco((0, 0, 0), 18, 110, MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 5)))
    c.restore()
    c.drawPath(boca, traco((28, 20, 32), 12))


class Cinematica:
    """Só as matrizes do rig (sem desenho): quem usa preenche `rig` {parte: (pai, pivô)} e `pes`."""

    def _local(self, parte, pose):
        """Matriz local: gira/escala em volta do pivô e desloca."""
        _, (px, py) = self.rig[parte]
        q = pose.get(parte) if isinstance(pose.get(parte), dict) else {}
        m = skia.Matrix()
        m.preTranslate(q.get("dx", 0.0), q.get("dy", 0.0))
        m.preTranslate(px, py)
        m.preRotate(q.get("rot", 0.0))
        m.preScale(q.get("sx", 1.0), q.get("sy", 1.0))
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
        """Matriz do corpo inteiro: pés em (x, y) na tela, escala pela altura, pulo, giro e estica."""
        s = altura / 1000.0
        pes_x, pes_y = self.pes
        e = pose.get("estica", 1.0)
        m = skia.Matrix()
        m.preTranslate(x, y)
        m.preScale(s, s)
        m.preTranslate(0, -pose.get("pulo", 0.0))
        m.preRotate(pose.get("corpo_rot", 0.0))
        m.preScale(1 / math.sqrt(e), e)
        m.preTranslate(-pes_x, -pes_y)
        return m
