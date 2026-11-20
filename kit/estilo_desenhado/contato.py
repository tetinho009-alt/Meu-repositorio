# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Contato de objeto com o apoio medido em pixel: "nada flutua".

Dizer que um objeto está na mesa não garante que a base dele toque o tampo: uma vela desenhada 30 px acima da linha
do tampo parece pendurada no ar. Aqui o objeto é desenhado SOZINHO numa camada, acha-se o pixel mais baixo dele nas
colunas em que encosta (a pegada) e compara-se com a linha do apoio (3D: a pegada projetada pela câmera; close 2D: o
tampo com profundidade, `Tampo2D`). Tolerância de ±2 px (a sombra projetada da peça fica fora da medida; `folga_tinta`
desconta a borda clara do corte). A borda é
medida com subpixel pela cobertura (alfa) das duas últimas linhas: contar só o índice da linha puxa a medida meio
pixel pra cima e o objeto "flutua" no teste.

Uso no episódio (ligado só na conferência):
    from estilo_desenhado import contato
    contato.liga("p3_mesa", t)
    contato.mede("vela", lambda c: vela(c, x, y, s, t), (x - 14, x + 14), y_tampo, folga_tinta=1.5)
    ruins = [m for m in contato.ESTADO["medidas"] if abs(m["dif"]) > contato.TOL_PX]
"""
import numpy as np
import skia

from . import tinta as T

ESTADO = {"ligado": False, "medidas": [], "plano": None, "t": None}
TOL_PX = 2.0


def liga(plano, t):
    ESTADO.update(ligado=True, plano=plano, t=t)


def desliga():
    ESTADO["ligado"] = False


def mede(nome, desenha, xs, y_apoio, folga_tinta=0.0, acima=700, abaixo=160):
    """Desenha o objeto sozinho e mede onde ele termina embaixo, nas colunas xs = (x0, x1) da pegada. `dif` < 0: no
    ar; > 0: enterrado; 0: encostado (dentro da meia espessura do traço)."""
    if not ESTADO["ligado"]:
        return None
    x0, x1 = int(min(xs)) - 2, int(max(xs)) + 3
    x1 = max(x1, x0 + 2)
    y0 = int(y_apoio - acima)
    sup = skia.Surface(x1 - x0, acima + abaixo)
    c = sup.getCanvas()
    c.clear(skia.Color(0, 0, 0, 0))
    c.translate(-x0, -y0)
    with T.sem_sombra():   # mede a base da peça, não a sombra que ela projeta
        desenha(c)
    a = sup.makeImageSnapshot().toarray()[:, :, 3]
    linhas = np.where((a > 32).any(axis=1))[0]   # 32: a ponta antisserrilhada de um canto ainda é desenho
    if len(linhas) == 0:
        return None   # fora da tela ou escondido
    ib = int(linhas.max())
    cob = a.max(axis=1) / 255.0
    y_base = y0 + ib + float(cob[ib]) + (float(cob[ib + 1]) if ib + 1 < len(cob) else 0.0)
    d = float(y_base - y_apoio)
    dif = d if d < 0 else (d - folga_tinta if d > folga_tinta else 0.0)
    m = dict(nome=nome, plano=ESTADO["plano"], t=ESTADO["t"], y_base=round(y_base, 1), y_apoio=round(float(y_apoio), 1),
             dif=round(dif, 1))
    ESTADO["medidas"].append(m)
    return m


class Tampo2D:
    """Tampo de móvel num close 2D visto de frente e de cima: a beirada do fundo em `y_fundo` (onde encontra a
    parede) e a da frente em `y_frente`. `y(d)` dá a linha do apoio na profundidade d (0 = fundo, 1 = frente) e
    `escala(d)` o tamanho relativo de um objeto ali. Fora de 0..1 é o ar atrás ou na frente do móvel: erro."""

    def __init__(self, y_fundo, y_frente, escala_fundo=0.85, escala_frente=1.15):
        self.y_fundo, self.y_frente = y_fundo, y_frente
        self.e0, self.e1 = escala_fundo, escala_frente

    def y(self, d):
        if not (0.0 <= d <= 1.0):
            raise ValueError(f"profundidade {d:.2f} fora do tampo (0 = fundo, 1 = frente): o objeto ficaria no ar")
        return self.y_fundo + (self.y_frente - self.y_fundo) * d

    def escala(self, d):
        return self.e0 + (self.e1 - self.e0) * d
