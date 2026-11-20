# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Exemplo de 10 s da série 2D com voto (comédia): a Lola descobre que o Nico pôs senha na geladeira.

Rig 2D do kit (personagens lola e nico), boca pela voz, cortes com chicote, gancho escrito no quadro 0 e o cartão de
voto no fim. Voz grátis (Kokoro), trilha e efeitos por código.

Uso (da pasta kit/): python ../exemplos/estilos/serie-2d-voto/cena.py [--stills] [--cpu]
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import exemplo_base as K  # noqa: E402

ARGS = K.argumentos()

import skia  # noqa: E402

from maquina import cinema as C, som as S, tela as T  # noqa: E402
from maquina.desenho import FPS, H, W, cheio, degrade, ease, fonte, radial, texto_c, traco  # noqa: E402
from maquina.rig import Boneco, piscadas  # noqa: E402

NOME = "exemplo_serie_2d"
FALAS = [
    {"quem": "narrador", "fala": "O Nico pôs senha na geladeira."},
    {"quem": "lola", "fala": "Por que a geladeira pede senha?"},
    {"quem": "nico", "fala": "Pro meu pudim sobreviver."},
    {"quem": "narrador", "fala": "O que a Lola faz?"},
]


def efeitos(linha):
    return [(linha.fala(1)["seg0"], S.notificacao(), 0.5), (linha.fala(2)["t1"] + 0.1, S.impacto(), 0.3)]


LINHA, TRAB, AUDIO = K.preparar(NOME, FALAS, efeitos=efeitos, stills=ARGS.stills)
F = LINHA.falas
CORTES = [F[1]["seg0"], F[2]["seg0"], F[3]["seg0"]]
T_VOTO = F[3]["seg0"]
LOLA, NICO = Boneco("lola"), Boneco("nico")
PA, PB = piscadas(60, 3), piscadas(60, 8)
PE = 1560
XA, XB = 220, 830


def cozinha(c, t):
    c.drawRect(skia.Rect(-900, -400, W + 900, H + 400), degrade((0, 0), (0, PE), [((255, 236, 196), 255), ((246, 208, 160), 255)]))
    for x in range(-880, W + 900, 120):                                  # azulejo da parede
        c.drawLine(x, 860, x, PE - 330, traco((232, 196, 150), 3))
    for y in range(860, PE - 320, 120):
        c.drawLine(-900, y, W + 900, y, traco((232, 196, 150), 3))
    jan = skia.Rect(90, 360, 470, 760)                                   # janela com céu e nuvem andando
    c.drawRect(jan, degrade((0, 360), (0, 760), [((120, 196, 255), 255), ((196, 232, 255), 255)]))
    for k in range(2):
        nx = 90 + ((t * 22 + k * 210) % 520) - 60
        for dx, r in ((0, 34), (36, 44), (78, 30)):
            c.drawCircle(nx + dx, 470 + k * 120, r, cheio((255, 255, 255), 230))
    c.drawRect(jan, traco((255, 255, 255), 22))
    c.drawLine(280, 360, 280, 760, traco((255, 255, 255), 12))
    c.drawRect(skia.Rect(-900, PE - 330, W + 900, PE - 300), cheio((150, 96, 60)))  # bancada
    c.drawRect(skia.Rect(-900, PE - 300, W + 900, PE), cheio((190, 128, 82)))
    for x in range(-810, W + 810, 270):
        c.drawRect(skia.Rect(x + 14, PE - 280, x + 256, PE - 20), traco((160, 104, 66), 6))
    c.drawRect(skia.Rect(-900, PE, W + 900, H + 400), cheio((120, 150, 170)))  # piso
    geladeira(c, t)


def geladeira(c, t):
    r = skia.Rect(400, 420, 690, PE)
    c.drawRRect(skia.RRect.MakeRectXY(r.makeOffset(10, 10), 40, 40), cheio((0, 0, 0), 50, blur=18))
    c.drawRRect(skia.RRect.MakeRectXY(r, 40, 40), cheio((248, 250, 252)))
    c.drawRRect(skia.RRect.MakeRectXY(r, 40, 40), traco((60, 70, 90), 8))
    c.drawLine(400, 820, 690, 820, traco((60, 70, 90), 8))
    c.drawRoundRect(skia.Rect(425, 520, 445, 760), 10, 10, cheio((150, 160, 180)))
    c.drawRoundRect(skia.Rect(425, 880, 445, 1180), 10, 10, cheio((150, 160, 180)))
    pisca = 0.5 + 0.5 * math.sin(t * 8)                                  # o teclado de senha, a piada
    tec = skia.Rect(480, 900, 640, 1100)
    c.drawRoundRect(tec, 16, 16, cheio((30, 36, 50)))
    c.drawRoundRect(tec, 16, 16, cheio((255, 70, 90), 90 * pisca, blur=18))
    for i in range(3):
        for j in range(3):
            c.drawCircle(510 + j * 50, 940 + i * 50, 14, cheio((120, 220, 255), 200))
    texto_c(c, "SENHA?", 560, 1150, fonte("titulo", 40), (255, 70, 90), 200 + 55 * pisca)


def cena(c, t):
    k = LINHA.atual(t)
    c.save()
    if k in (1, 2):                              # close em quem fala, centralizado na tela
        alvo = XA if k == 1 else XB
        z = 1.6 + 0.03 * (t - F[k]["seg0"])
        c.translate(W / 2, 1050)
        c.scale(z, z)
        c.translate(-alvo, -1130)
    else:
        z = 1.0 + 0.012 * t
        c.translate(W / 2, 1000)
        c.scale(z, z)
        c.translate(-W / 2, -1000)
    cozinha(c, t)
    u1 = t - F[1]["seg0"]
    braco_lola = {"braco_d": {"rot": -110 * ease(u1 / 0.3)}, "antebraco_d": {"rot": -30},
                 "braco_e": {"rot": 25}} if k >= 1 else {}
    lola = K.pose_viva(t, "lola", LINHA, PA, braco_lola, olhar=(0.7, -0.1))
    if k == 2:
        lola.update({"sobrancelha_e": {"dy": -14, "rot": -10}, "sobrancelha_d": {"dy": -14, "rot": 10}})
    orgulho = {"braco_e": {"rot": 40}, "antebraco_e": {"rot": -100}, "braco_d": {"rot": -40},
               "antebraco_d": {"rot": 100}} if k >= 2 else {"braco_d": {"rot": -12}}
    nico = K.pose_viva(t, "nico", LINHA, PB, orgulho, olhar=(-0.7, 0.0))
    if k >= 2:
        nico["pulo"] = 18 * abs(math.sin((t - F[2]["seg0"]) * 6)) * (t < F[2]["t1"])
    LOLA.desenhar(c, XA, PE + 20, 660, lola)
    NICO.desenhar(c, XB, PE + 25, 690, nico)
    c.restore()


def quadro(c, t):
    C.chicote(c, t, CORTES, lambda cc: cena(cc, t))
    C.vinheta(c, 0.5)
    C.grao(c, t, 0.05, FPS)
    K.gancho(c, t, [("O NICO PÔS SENHA", False), ("NA GELADEIRA", True)], F[1]["seg0"])
    K.legenda(c, t, LINHA, chaves=("SENHA", "PUDIM"), ate=T_VOTO, desde=F[1]["seg0"])
    if t < T_VOTO:
        T.selo(c, "O PUDIM DO NICO · PARTE 1 · FICÇÃO")
    else:
        T.cartao_voto(c, t, T_VOTO, "O que a Lola faz?", [("Chutar", "a senha até acertar"),
                                                        ("Desistir", "e fazer outro pudim")],
                      duracao=LINHA.total - T_VOTO, parte_seguinte=2)


K.renderizar(quadro, LINHA, TRAB, AUDIO, NOME, ARGS,
             marcos=[0.0, F[1]["seg0"] + 0.8, F[2]["seg0"] + 0.6, T_VOTO + 1.4])
