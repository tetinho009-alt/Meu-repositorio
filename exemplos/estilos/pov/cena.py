# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Exemplo de 10 s do POV (série em "você"): o vizinho novo olha nos seus olhos e dá um aviso estranho.

A câmera é você: tremida de mão, o vizinho fala olhando para a lente, a porta do corredor ao fundo e o voto em
"o que você faz?". Rig 2D do kit (personagem nico), voz grátis (Kokoro), trilha e efeitos por código.

Uso (da pasta kit/): python ../exemplos/estilos/pov/cena.py [--stills] [--cpu]
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

NOME = "exemplo_pov"
FALAS = [
    {"quem": "narrador", "fala": "Seu primeiro dia no prédio novo."},
    {"quem": "nico", "fala": "Só um aviso, vizinho."},
    {"quem": "nico", "fala": "Depois das três, não abre a janela."},
    {"quem": "narrador", "fala": "O que você faz?"},
]


def efeitos(linha):
    return [(linha.fala(2)["t1"] + 0.05, S.impacto(), 0.35), (0.0, S.drone(linha.total, 52.0) * 0.25, 1.0)]


LINHA, TRAB, AUDIO = K.preparar(NOME, FALAS, efeitos=efeitos, stills=ARGS.stills)
F = LINHA.falas
T_VOTO = F[3]["seg0"]
NICO = Boneco("nico")
PB = piscadas(60, 5)


def corredor(c, t):
    c.drawRect(skia.Rect(-300, -300, W + 300, H + 300), cheio((58, 52, 70)))
    fuga = (W / 2, 820)                                   # corredor em perspectiva, saindo do ponto de fuga
    for lado in (-1, 1):
        p = skia.Path()
        p.moveTo(fuga[0] + lado * 120, fuga[1] - 220)
        p.lineTo(W / 2 + lado * 900, -300)
        p.lineTo(W / 2 + lado * 900, H + 300)
        p.lineTo(fuga[0] + lado * 120, fuga[1] + 260)
        p.close()
        c.drawPath(p, cheio((96, 84, 110) if lado < 0 else (84, 74, 98)))
    chao = skia.Path()
    chao.moveTo(fuga[0] - 120, fuga[1] + 260)
    chao.lineTo(fuga[0] + 120, fuga[1] + 260)
    chao.lineTo(W + 600, H + 300)
    chao.lineTo(-600, H + 300)
    chao.close()
    c.drawPath(chao, degrade((0, fuga[1]), (0, H), [((70, 50, 44), 255), ((120, 86, 70), 255)]))
    c.drawRect(skia.Rect(fuga[0] - 120, fuga[1] - 220, fuga[0] + 120, fuga[1] + 260), cheio((40, 34, 48)))
    for k, z in enumerate((0.25, 0.5, 0.8)):                  # portas ao longo do corredor, uma com luz por baixo
        for lado in (-1, 1):
            x = fuga[0] + lado * (120 + 780 * z)
            top, bot = fuga[1] - 220 - 520 * z, fuga[1] + 260 + 640 * z
            w = 90 + 260 * z
            r = skia.Rect(min(x, x + lado * w), top + 0.1 * (bot - top), max(x, x + lado * w), bot)
            c.drawRect(r, cheio((120, 82, 60)))
            c.drawRect(r, traco((60, 40, 30), 4 + 6 * z))
            if k == 1 and lado > 0:
                luz = 0.6 + 0.4 * math.sin(t * 13) * math.sin(t * 3.1)
                c.drawRect(skia.Rect(r.left(), r.bottom() - 10, r.right(), r.bottom() + 4), cheio((255, 220, 140), 200 * luz, blur=8))
    for k in range(3):                                     # lâmpadas do teto
        y = fuga[1] - 260 - 260 * k
        c.drawCircle(W / 2, y, 18 + 14 * k, cheio((255, 230, 170), 230))
        c.drawCircle(W / 2, y, 90 + 60 * k, cheio((255, 210, 140), 40, blur=40))


def cena(c, t):
    u = t
    tx = 14 * math.sin(u * 1.7) + 6 * math.sin(u * 5.3)      # câmera na mão: você está ali
    ty = 10 * math.sin(u * 1.3 + 1) + 4 * math.sin(u * 4.1)
    z = 1.0 + 0.035 * min(t, F[2]["t1"]) / max(F[2]["t1"], 1)
    c.save()
    c.translate(W / 2 + tx, H / 2 + ty)
    c.scale(z, z)
    c.rotate(0.6 * math.sin(u * 0.9))
    c.translate(-W / 2, -H / 2)
    corredor(c, t)
    k = LINHA.atual(t)
    serio = k >= 2
    extra = {"braco_d": {"rot": -12 - 50 * ease((t - F[1]["seg0"]) / 0.3) * (k == 1)},
             "antebraco_d": {"rot": -60 * (k == 1)}}
    if serio:
        extra.update({"sobrancelha_e": {"dy": 8, "rot": 12}, "sobrancelha_d": {"dy": 8, "rot": -12},
                      "braco_e": {"rot": 70 * ease((t - F[2]["seg0"]) / 0.3)}, "antebraco_e": {"rot": 80}})
    pose = K.pose_viva(t, "nico", LINHA, PB, extra, olhar=(0.0, 0.05))
    if t < F[1]["seg0"]:
        entra = ease((t - 0.2) / 0.9)
        NICO.desenhar(c, W / 2 + 40 - 500 * (1 - entra), 2040, 1300, pose)
    else:
        NICO.desenhar(c, W / 2 + 40, 2040 + 30 * serio, 1300 + 90 * serio, pose)
    c.restore()


def quadro(c, t):
    cena(c, t)
    C.vinheta(c, 0.95)
    C.grao(c, t, 0.08, FPS)
    K.gancho(c, t, [("POV:", False), ("O VIZINHO NOVO", False), ("TE DÁ UM AVISO", True)], F[1]["seg0"], y=480)
    K.legenda(c, t, LINHA, chaves=("TRÊS", "JANELA"), ate=T_VOTO, desde=F[1]["seg0"])
    if t < T_VOTO:
        T.selo(c, "O PRÉDIO · PARTE 1 · FICÇÃO")
    else:
        T.cartao_voto(c, t, T_VOTO, "O que você faz?", [("Perguntar", "por que depois das três"),
                                                       ("Abrir", "a janela hoje mesmo")],
                      duracao=LINHA.total - T_VOTO, parte_seguinte=2)


K.renderizar(quadro, LINHA, TRAB, AUDIO, NOME, ARGS,
             marcos=[0.0, F[1]["seg0"] + 0.6, F[2]["seg0"] + 1.0, T_VOTO + 1.4])
