# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Rig de recorte digital: monta as partes PNG de um personagem com hierarquia e pivôs (Skia; GPU ou CPU).

O personagem é uma pasta `personagens/<nome>/` com `partes.json` (posição de cada PNG no mundo, o RIG e as medidas
do molde) e `partes/<parte>.png`, gerada por `construir_boneco.py`.

Pose = dicionário por parte {"rot": graus, "dx", "dy" (unidades do mundo), "sx", "sy"} + chaves globais:
  visema: boca ("R","A","E","I","O","U","M","F","feliz"); piscar: 0..1; olhar: (x, y) em -1..1;
  estica: estica/amassa a partir dos pés; pulo: unidades do mundo para cima; corpo_rot: inclinação do corpo;
  sorriso: 0..1 troca a boca por um sorriso largo demais (ameaça); tinta: {parte: (r, g, b)} recolore partes
  (ex.: olhos totalmente negros).
"""
import json
import math
from pathlib import Path

import skia

from config import pasta


def _sorriso(c, cx, by, abre=1.0):
    """Sorriso de orelha a orelha com dentes demais, em coordenadas do molde. `abre` de 0 (fino) a 1 (escancarado)."""
    w, h = 190.0, 14 + 30 * abre
    boca = skia.Path()
    boca.moveTo(cx - w, by - 34)
    boca.quadTo(cx, by + 30, cx + w, by - 34)
    boca.quadTo(cx + w * 0.55, by + h + 34, cx, by + h + 26)
    boca.quadTo(cx - w * 0.55, by + h + 34, cx - w, by - 34)
    boca.close()
    contorno = skia.Paint(AntiAlias=True, Color=skia.Color(28, 20, 32), Style=skia.Paint.kStroke_Style, StrokeWidth=12,
                          StrokeJoin=skia.Paint.kRound_Join)
    c.drawPath(boca, skia.Paint(AntiAlias=True, Color=skia.Color(18, 6, 8)))
    c.save()
    c.clipPath(boca, doAntiAlias=True)
    dente = skia.Paint(AntiAlias=True, Color=skia.Color(236, 230, 214))
    risco = skia.Paint(AntiAlias=True, Color=skia.Color(120, 104, 90), Style=skia.Paint.kStroke_Style, StrokeWidth=3)
    for fila, (y0, alt) in enumerate(((by - 40, 40.0), (by + h + 4, 30.0))):
        n = 15
        for k in range(n):
            u = (k + 0.5) / n
            x = cx - w + 2 * w * u
            curva = 1 - (2 * u - 1) ** 2
            y = y0 + (curva * 30 if fila == 0 else -curva * 6)
            r = skia.Rect.MakeXYWH(x - w / n + 2, y if fila == 0 else y - alt, 2 * w / n - 4, alt)
            c.drawRoundRect(r, 6, 6, dente)
            c.drawRoundRect(r, 6, 6, risco)
    c.restore()
    c.drawPath(boca, contorno)


class Boneco:
    """Personagem montado a partir de `personagens/<nome>` (ou de uma pasta qualquer com partes.json)."""

    def __init__(self, nome_ou_pasta):
        p = Path(nome_ou_pasta)
        self.pasta = p if p.is_dir() else pasta("personagens") / str(nome_ou_pasta)
        arq = self.pasta / "partes.json"
        if not arq.is_file():
            raise FileNotFoundError(f"{arq} não existe. Gere com: python construir_boneco.py {self.pasta.name}")
        info = json.loads(arq.read_text(encoding="utf-8"))
        self.nome = self.pasta.name
        self.mapa = info["partes"]
        self.img = {nome: skia.Image.open(str(self.pasta / "partes" / f"{nome}.png")) for nome in self.mapa}
        self.rig = {parte: (pai, tuple(piv)) for parte, pai, piv in info["rig"]}
        self.ordem = [parte for parte, _, _ in info["rig"]]
        self.cx = float(info.get("cx", 500.0))
        self.pes = (self.cx, float(info.get("chao", 1000.0)))
        self.boca_y = float(info.get("boca_y", 392.0))
        self.pose_base = info.get("pose_base") or {}
        self.boca_padrao = info.get("boca_padrao", "R")
        self.amostra = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)

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

    def _base(self, pose):
        """Pose pedida por cima da pose_base do personagem, mesclando por parte."""
        if not self.pose_base:
            return pose or {}
        out = {k: dict(v) if isinstance(v, dict) else v for k, v in self.pose_base.items()}
        for k, v in (pose or {}).items():
            out[k] = {**out.get(k, {}), **v} if isinstance(v, dict) and isinstance(out.get(k), dict) else v
        return out

    def mao(self, lado, x, y, altura, pose=None):
        """Palma da mão ("e" ou "d") na tela nesta pose e o ângulo do antebraço em graus.
        Use para prender objeto na mão (celular, copo) em vez de chutar a posição: objeto solto flutua."""
        pose = self._base(pose)
        parte = f"antebraco_{lado}"
        m = self._mundo(parte, pose, {"_raiz": self._raiz(x, y, altura, pose)})
        ex, ey = self.rig[parte][1]  # pivô do antebraço = cotovelo; a mão fica 162 abaixo no molde
        sinal = -1 if lado == "e" else 1
        px, py = m.mapXY(ex + sinal * 8, ey + 162)
        cx, cy = m.mapXY(ex, ey)
        return (px, py), math.degrees(math.atan2(py - cy, px - cx)) - 90

    def caixa(self, x, y, altura):
        """Retângulo que envolve o boneco na tela (para luz e recorte)."""
        return skia.Rect.MakeLTRB(x - altura * 0.6, y - altura * 1.25, x + altura * 0.6, y + altura * 0.02)

    def desenhar(self, c, x, y, altura, pose=None, partes=None, sombra=True):
        """(x, y) = pés na tela; altura = altura do boneco em px. `partes` = só essas (ex.: redesenhar o antebraço
        por cima de um objeto que ele segura), sem a sombra no chão."""
        pose = self._base(pose)
        s = altura / 1000.0
        if partes is None and sombra:
            k = max(0.25, 1 - pose.get("pulo", 0.0) / 300)
            c.drawOval(skia.Rect.MakeLTRB(x - 210 * s * k, y - 14 * s, x + 210 * s * k, y + 18 * s),
                       skia.Paint(AntiAlias=True, Color=skia.Color(0, 0, 0, int(80 * k)),
                                  MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, max(0.5, 10 * s))))
        cache = {"_raiz": self._raiz(x, y, altura, pose)}
        boca = "boca_" + pose.get("visema", self.boca_padrao)
        ox, oy = pose.get("olhar", (0.0, 0.0))
        piscar = pose.get("piscar", 0.0)
        for parte in self.ordem:
            if partes is not None and parte not in partes:
                continue
            m = self._mundo(parte, pose, cache)
            nome_img = boca if parte == "boca" else parte
            if parte == "cabelo" and pose.get("cabelo_estilo"):
                nome_img = "cabelo_" + pose["cabelo_estilo"]
            if parte.startswith("palpebra") and piscar < 0.05:
                continue
            if parte == "boca" and pose.get("sorriso"):
                c.save()
                c.concat(m)
                _sorriso(c, self.cx, self.boca_y, pose["sorriso"])
                c.restore()
                continue
            if nome_img not in self.mapa:
                continue
            c.save()
            c.concat(m)
            if parte.startswith("iris"):
                c.translate(ox * 13, oy * 10)
            info = self.mapa[nome_img]
            dst = skia.Rect.MakeXYWH(info["x"], info["y"], info["w"], info["h"])
            if parte.startswith("palpebra"):
                topo = info["y"] + 20  # a pálpebra desce a partir do alto do olho
                c.translate(0, topo)
                c.scale(1, max(0.05, piscar))
                c.translate(0, -topo)
            tinta = pose.get("tinta", {}).get(parte)
            if tinta:
                cor = skia.Color(*tinta)
                c.drawImageRect(self.img[nome_img], dst, self.amostra, skia.Paint(
                    ColorFilter=skia.ColorFilters.Blend(cor, skia.BlendMode.kSrcIn),
                    ImageFilter=skia.ImageFilters.Blur(10, 10)))
                c.drawImageRect(self.img[nome_img], dst, self.amostra, skia.Paint(
                    ColorFilter=skia.ColorFilters.Blend(cor, skia.BlendMode.kSrcIn)))
            else:
                c.drawImageRect(self.img[nome_img], dst, self.amostra)
            c.restore()


# ---------------------------------------------------------------- animação de apoio

VISEMA_POR_LETRA = {"a": "A", "á": "A", "ã": "A", "â": "A", "e": "E", "é": "E", "ê": "E", "i": "I", "í": "I",
                    "o": "O", "ó": "O", "ô": "O", "õ": "O", "u": "U", "ú": "U", "m": "M", "b": "M", "p": "M",
                    "f": "F", "v": "F"}


def visema(t, palavras):
    """Boca pela fala: `palavras` = [(ini, fim, palavra)]. Fecha entre palavras (regra: boca só fala na fala)."""
    for ini, fim, p in palavras:
        if ini <= t < fim:
            letras = [ch for ch in p.lower() if ch.isalpha()] or ["a"]
            k = min(len(letras) - 1, int((t - ini) / max(fim - ini, 1e-3) * len(letras)))
            return VISEMA_POR_LETRA.get(letras[k], "E")
    return "R"


def piscadas(duracao, semente=7):
    """Instantes de piscada em intervalo irregular de 2 a 5 s (regra: nunca parado, nunca regular)."""
    import random

    rnd, t, out = random.Random(semente), 1.0, []
    while t < duracao:
        out.append(t)
        t += rnd.uniform(2.0, 5.0)
    return out


def piscar(t, instantes):
    return 1.0 if any(0 <= t - b < 0.11 for b in instantes) else 0.0


def respira(t, k=1.0):
    """Respiração no tronco (±0,7%)."""
    return {"sy": 1 + 0.007 * k * math.sin(t * 2 * math.pi / 3.4)}


MEDO = {"sobrancelha_e": {"dy": -16, "rot": -10}, "sobrancelha_d": {"dy": -16, "rot": 10}}
OLHO_NEGRO = {"olho_e": (4, 2, 6), "olho_d": (4, 2, 6), "iris_e": (0, 0, 0), "iris_d": (0, 0, 0)}
