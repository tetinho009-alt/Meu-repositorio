# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Exemplo de 10 s do terror com voto, no estilo desenhado do kit: a estrada na neblina com o vulto ao longe, o
quarto à luz de vela com o personagem com medo em stop motion (12 poses por segundo) e o voto.

Voz grátis (Kokoro), batidas na porta e vento por código. A câmera anda no plano aberto, o caso caro do estilo:
leva uns 5 min numa placa de vídeo comum e mais na CPU.

Uso (da pasta kit/): python ../exemplos/estilos/terror-voto/cena.py [--stills] [--cpu]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import exemplo_base as K  # noqa: E402

ARGS = K.argumentos()

from maquina import som as S  # noqa: E402

import estilo_desenhado as G  # noqa: E402
from estilo_desenhado import elenco as E, interface as UI, interiores as IN, paisagens as PS  # noqa: E402
from estilo_desenhado.ameaca import Vulto  # noqa: E402
from estilo_desenhado.cenario3d import CamG  # noqa: E402

NOME = "exemplo_terror"
PROT = E.pessoa("protagonista")
QUEM = E.PAPEIS["protagonista"]
VULTO = Vulto()
FALAS = [
    {"quem": "narrador", "fala": "Toda noite, a neblina desce na estrada."},
    {"quem": "narrador", "fala": "E alguém volta pra bater na porta."},
    {"quem": "narrador", "fala": f"O que {QUEM} faz?"},
]


def efeitos(linha):
    bate = linha.fala(1)["t1"] + 0.15
    return [(0.0, S.vento(linha.total) * 0.6, 1.0), (0.0, S.drone(linha.total, 44.0) * 0.5, 1.0)] + \
           [(bate + k * 0.32, S.impacto(), 0.7) for k in range(3)]


LINHA, TRAB, AUDIO = K.preparar(NOME, FALAS, clima="tenso", efeitos=efeitos, stills=ARGS.stills)
F = LINHA.falas
T_QUARTO, T_VOTO = F[1]["seg0"], F[2]["seg0"]


def quadro(c, t):
    ts = E.stop(t)
    with G.quadro(c, t, **G.tinta.NOITE):
        if t < T_QUARTO:
            cam = CamG(x=0.2, h=1.5, F=760, hz=1080, z=-0.4 + 0.14 * t)
            ref = CamG(x=0.2, h=1.5, F=760, hz=1080, z=-0.4)
            PS.estrada_neblina(c, t, cam=cam, ref=ref,
                               atores=[(1.6, 24.0 - 1.5 * t, lambda cc, x, y, a: VULTO.desenhar(cc, x, y, a, {"t": ts}), 2.4)])
            for i, linha_txt in enumerate(("TEM ALGUÉM", "NA ESTRADA")):   # gancho escrito já no quadro 0
                UI.texto_tinta(c, linha_txt, 540, 640 + i * 120, 110, t=t)
        else:
            medo = min(1.0, (t - T_QUARTO) / 0.6)
            pose = G.pose_medo(medo, t=ts, olhar=(0.5, -0.1))
            IN.quarto_vela(c, t, atores=[(-0.2, 2.3, lambda cc, x, y, a: PROT.desenhar(cc, x, y, a, pose), 1.65)])
            if t < T_VOTO:
                ps, _ = LINHA.legenda(t)
                UI.legenda(c, [tuple(p) for p in ps], chave=("PORTA.",), t=t)
        UI.selos_ficcao(c, "A CASA DA ESTRADA · PARTE 1 · FICÇÃO", "FICÇÃO")
        UI.voto_cartao(c, t, T_VOTO, f"O que {QUEM} faz?", [("Abrir", "e descobre quem bate", "olho_aberto"),
                                                          ("Esconder", "e espera a neblina subir", "esconder")],
                       duracao=LINHA.total - T_VOTO + 0.5, rotulo="PARTE", numero=1)


K.renderizar(quadro, LINHA, TRAB, AUDIO, NOME, ARGS, marcos=[0.0, 1.8, T_QUARTO + 1.2, T_VOTO + 1.2])
