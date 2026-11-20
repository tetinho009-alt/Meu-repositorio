# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Exemplo de 10 s da novela (romance com voto): o reencontro no pôr do sol, depois de dez anos.

Motion comic no rig 2D do kit (lola e nico): céu de fim de tarde, pétalas caindo, brilho de lente, rosto corado,
closes alternados no tempo da fala e o voto no fim. No caminho com imagem gerada (metodo/estilos/novela-anime.md) o
mesmo roteiro sai no traço anime; este exemplo é o grátis, sem gerar imagem.

Uso (da pasta kit/): python ../exemplos/estilos/novela-anime/cena.py [--stills] [--cpu]
"""
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import exemplo_base as K  # noqa: E402

ARGS = K.argumentos()

import skia  # noqa: E402

from maquina import cinema as C, som as S, tela as T  # noqa: E402
from maquina.desenho import FPS, H, W, cheio, degrade, ease, radial, traco  # noqa: E402
from maquina.rig import Boneco, piscadas  # noqa: E402

NOME = "exemplo_novela"
FALAS = [
    {"quem": "narrador", "fala": "Ela voltou depois de dez anos."},
    {"quem": "nico", "fala": "Você não mudou nada."},
    {"quem": "lola", "fala": "E você mudou tudo."},
    {"quem": "narrador", "fala": "Ela conta o segredo?"},
]


def efeitos(linha):
    return [(linha.fala(2)["t1"] + 0.05, S.coracao(1.6, 70, 96), 0.6)]


LINHA, TRAB, AUDIO = K.preparar(NOME, FALAS, efeitos=efeitos, stills=ARGS.stills)
F = LINHA.falas
T_VOTO = F[3]["seg0"]
CORTES = [F[1]["seg0"], F[2]["seg0"], F[3]["seg0"]]
LOLA, NICO = Boneco("lola"), Boneco("nico")
PA, PB = piscadas(60, 21), piscadas(60, 4)
PE = 1620
XA, XB = 330, 760
PETALAS = [(random.Random(k).random(), random.Random(k + 99).random(), random.Random(k + 7).random()) for k in range(40)]


def por_do_sol(c, t):
    c.drawRect(skia.Rect(-900, -400, W + 900, H + 400), degrade((0, 0), (0, PE), [
        ((86, 60, 140), 255), ((236, 110, 140), 255), ((255, 186, 120), 255)], [0.0, 0.55, 1.0]))
    sx, sy = W * 0.5, 860
    c.drawCircle(sx, sy, 520, cheio((255, 220, 160), 90, blur=120))
    c.drawCircle(sx, sy, 150, cheio((255, 236, 190), 255))
    for k in range(7):                                       # prédios recortados no horizonte
        x0 = -200 + k * 220
        h = 260 + 140 * ((k * 37) % 5) / 4
        c.drawRect(skia.Rect(x0, 1260 - h, x0 + 180, 1300), cheio((70, 40, 90), 230))
    c.drawRect(skia.Rect(-900, 1290, W + 900, H + 400), degrade((0, 1290), (0, H), [((120, 70, 110), 255), ((60, 36, 70), 255)]))
    c.drawRect(skia.Rect(-900, PE - 40, W + 900, PE + 30), cheio((40, 24, 50), 120, blur=20))


def petalas(c, t):
    for a, b, d in PETALAS:
        x = (a * W * 1.4 - 200 + 60 * math.sin(t * (0.8 + d) + a * 9) + t * 40 * (0.5 + d)) % (W + 200) - 100
        y = (b * H + t * (90 + 120 * d)) % (H + 100) - 50
        c.save()
        c.translate(x, y)
        c.rotate(t * 90 * (d - 0.5) + a * 360)
        c.scale(1.0, 0.5 + 0.5 * math.sin(t * 3 + a * 7))
        c.drawOval(skia.Rect(-10 - 8 * d, -6 - 4 * d, 10 + 8 * d, 6 + 4 * d), cheio((255, 196, 214), 210))
        c.restore()


def rubor(c, x, pe, alt, forca):
    if forca <= 0:
        return
    s = alt / 1000.0
    for dx in (-118, 118):
        c.drawOval(skia.Rect.MakeXYWH(x + (dx - 46) * s, pe - (1000 - 320) * s, 92 * s, 40 * s),
                   cheio((255, 90, 120), 120 * forca, blur=10 * s))


def cena(c, t):
    k = LINHA.atual(t)
    c.save()
    if k in (1, 2):                                          # close em quem fala, com zoom lento
        alvo = XB if k == 1 else XA
        z = 1.75 + 0.05 * (t - F[k]["seg0"])
        c.translate(W / 2, 1000)
        c.scale(z, z)
        c.translate(-alvo, -1150)
    else:
        z = 1.0 + 0.02 * t
        c.translate(W / 2, 1100)
        c.scale(z, z)
        c.translate(-W / 2, -1100)
    por_do_sol(c, t)
    timida = ease((t - F[2]["seg0"]) / 0.5) if k >= 2 else 0.0
    lola = K.pose_viva(t, "lola", LINHA, PA, {"cabeca": {"rot": -5 * timida}, "braco_e": {"rot": 20},
                                            "braco_d": {"rot": -15 - 20 * timida}, "antebraco_d": {"rot": -70 * timida}},
                      olhar=(0.6, 0.1 * timida))
    nico = K.pose_viva(t, "nico", LINHA, PB, {"braco_d": {"rot": -10}, "braco_e": {"rot": 10}}, olhar=(-0.6, 0.0))
    if k >= 2:
        nico["visema"] = nico["visema"] if nico["visema"] != "R" else "O"
    LOLA.desenhar(c, XA, PE, 760, lola)
    NICO.desenhar(c, XB, PE + 10, 800, nico)
    rubor(c, XA, PE, 760, 0.3 + 0.7 * timida)
    rubor(c, XB, PE + 10, 800, 0.5 if k >= 1 else 0.0)
    c.restore()
    petalas(c, t)
    brilho = 0.5 + 0.5 * math.sin(t * 1.3)                    # brilho de lente vindo do sol
    c.drawRect(skia.Rect(0, 0, W, H), radial(W * 0.5, 860, 900, [((255, 210, 170), 50 + 30 * brilho), ((255, 210, 170), 0)]))


def quadro(c, t):
    C.chicote(c, t, CORTES, lambda cc: cena(cc, t))
    C.vinheta(c, 0.7)
    C.grao(c, t, 0.05, FPS)
    K.gancho(c, t, [("ELA VOLTOU", False), ("DEPOIS DE 10 ANOS", True)], F[1]["seg0"], cor_destaque=(255, 120, 160))
    K.legenda(c, t, LINHA, chaves=("NADA", "TUDO"), ate=T_VOTO, desde=F[1]["seg0"])
    if t < T_VOTO:
        T.selo(c, "DEZ ANOS DEPOIS · PARTE 1 · FICÇÃO")
    else:
        T.cartao_voto(c, t, T_VOTO, "Ela conta o segredo?", [("Conta", "agora, no pôr do sol"),
                                                            ("Guarda", "mais um pouco")],
                      duracao=LINHA.total - T_VOTO, parte_seguinte=2)


K.renderizar(quadro, LINHA, TRAB, AUDIO, NOME, ARGS,
             marcos=[0.0, F[1]["seg0"] + 0.6, F[2]["seg0"] + 0.9, T_VOTO + 1.4])
