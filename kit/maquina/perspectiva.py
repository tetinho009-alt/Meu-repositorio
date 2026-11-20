# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Cenário "3D" por projeção em perspectiva, desenhado em Skia do fundo para a frente.

Não é motor 3D: é uma câmera pinhole (`Cam3D`) que projeta pontos em metros na tela, polígonos (`quad`) e uma fila
de desenho ordenada pela profundidade (`Cena`). Bonecos 2D entram em pé num ponto do chão, escalados pela distância.

Unidades: X lateral (metros, + para a direita), Y altura (metros, chão = 0), Z profundidade (metros, + para longe).

Regra de ouro (aprendida com "caixa d'água atrás do muro"): TUDO entra na fila pela própria profundidade, nunca por
tipo. Objeto que está depois de um muro tem chave maior que o muro; quem está na frente tem chave menor.
"""
import skia

from .desenho import H, W


class Cam3D:
    """Câmera pinhole: x lateral, h altura do olho, F distância focal em px, hz linha do horizonte na tela,
    cx centro horizontal, z posição da câmera ao longo da profundidade (dolly)."""

    def __init__(self, x=0.0, h=1.6, F=1000.0, hz=1000.0, cx=W / 2, z=0.0):
        self.x, self.h, self.F, self.hz, self.cx, self.z = x, h, F, hz, cx, z

    def p(self, X, Y, Z):
        """Ponto do mundo -> (x, y) na tela."""
        Z = max(Z - self.z, 0.35)
        return (self.cx + (X - self.x) * self.F / Z, self.hz + (self.h - Y) * self.F / Z)

    def escala(self, Z):
        """Pixels por metro na profundidade Z."""
        return self.F / max(Z - self.z, 0.35)

    def visivel(self, Z, margem=0.5):
        return Z > self.z + margem


def caminho(cam, pts):
    path = skia.Path()
    path.moveTo(*cam.p(*pts[0]))
    for q in pts[1:]:
        path.lineTo(*cam.p(*q))
    path.close()
    return path


def quad(c, cam, pts, paint):
    """Polígono com vértices em metros (lista de (X, Y, Z))."""
    path = caminho(cam, pts)
    c.drawPath(path, paint)
    return path


def linha(c, cam, a, b, paint):
    c.drawLine(*cam.p(*a), *cam.p(*b), paint)


def caixa(c, cam, x0, x1, y0, y1, z0, z1, frente, lado, topo=None):
    """Paralelepípedo: desenha só as faces que a câmera vê (frente, lateral voltada para a câmera, topo se abaixo
    do olho). `frente`, `lado`, `topo` são Paints."""
    if cam.visivel(z0, 0.1):
        quad(c, cam, [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)], frente)
    if cam.x < x0:
        quad(c, cam, [(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)], lado)
    elif cam.x > x1:
        quad(c, cam, [(x1, y0, z0), (x1, y0, z1), (x1, y1, z1), (x1, y1, z0)], lado)
    if topo is not None and cam.h > y1:
        quad(c, cam, [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], topo)


class Cena:
    """Fila de desenho por profundidade: `poe(z, funcao)`; `desenha(c)` chama do mais longe para o mais perto.
    `desempate` resolve itens na mesma profundidade (maior = desenhado antes)."""

    def __init__(self):
        self.itens = []

    def poe(self, z, funcao, desempate=0.0):
        self.itens.append((z, desempate, len(self.itens), funcao))

    def desenha(self, c):
        for _, _, _, f in sorted(self.itens, key=lambda e: (-e[0], -e[1], e[2])):
            f(c)
        self.itens.clear()


def boneco_3d(c, cam, boneco, X, Z, pose, Y=0.0, altura_m=1.65, afunda=0.0, iluminar=None):
    """Personagem 2D de pé no ponto (X, Y, Z), na escala da distância. `afunda` desce o boneco (atrás de mureta).
    `iluminar(c, boneco, x, pe, alt, pose)` aplica a luz da cena (ex.: cinema.boneco_iluminado)."""
    pe = cam.p(X, Y - afunda, Z)
    alt = altura_m * cam.escala(Z)
    if iluminar:
        iluminar(c, boneco, pe[0], pe[1], alt, pose)
    else:
        boneco.desenhar(c, pe[0], pe[1], alt, pose)
    return pe, alt


def ceu_noturno(c, cam, topo=(6, 6, 18), meio=(24, 18, 48), baixo=(70, 40, 60), estrelas=60, t=0.0, semente=9):
    """Céu em degradê até o horizonte, com estrelas que cintilam."""
    import math
    import random

    from .desenho import cheio, degrade

    c.drawRect(skia.Rect.MakeLTRB(-200, -200, W + 200, cam.hz + 40),
               degrade((0, 0), (0, cam.hz), [topo, meio, baixo], [0.0, 0.6, 1.0]))
    rnd = random.Random(semente)
    for _ in range(estrelas):
        x, y = rnd.uniform(-200, W + 200), rnd.uniform(0, cam.hz * 0.7)
        c.drawCircle(x, y, rnd.uniform(1, 2.4), cheio((255, 250, 230), 110 + 90 * math.sin(t * 2 + x)))


__all__ = ["Cam3D", "Cena", "boneco_3d", "caixa", "caminho", "ceu_noturno", "linha", "quad", "H", "W"]
