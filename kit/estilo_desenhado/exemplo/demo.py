# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Demonstração do estilo desenhado, recorte de papel (12 s): abertura sem voz com o gancho escrito, plano aberto na neblina com a
ameaça (o Rasgado) ao longe, a personagem com medo em stop motion (12 poses por segundo, câmera a 60 qps) e a tela de voto.
Trilha e efeitos sintetizados aqui mesmo, masterizados a -14 LUFS; não usa voz (a legenda mostra onde a narração
entraria). O plano aberto tem câmera andando, o caso caro do estilo.

Uso (da pasta kit/):
    python estilo_desenhado/exemplo/demo.py            # vídeo completo em <pastas.trabalho>/demo_papel/
    python estilo_desenhado/exemplo/demo.py --stills   # só os quadros-marco, para conferir rápido
    python estilo_desenhado/exemplo/demo.py --cpu      # força CPU + libx264
"""
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KIT))

from config import CFG, pasta  # noqa: E402
from masterizar import masterizar  # noqa: E402
from maquina.motor import renderizar  # noqa: E402

import estilo_desenhado as G  # noqa: E402
from estilo_desenhado import elenco as E, interface as UI, interiores as IN, paisagens as PS, som as S  # noqa: E402
from estilo_desenhado.ameaca import Rasgado  # noqa: E402
from estilo_desenhado.cenario3d import CamG  # noqa: E402

DUR = 12.0
T_ABRE, T_QUARTO, T_VOTO = 2.4, 5.0, 8.6
PROT = E.pessoa("protagonista")    # o elenco sorteado com o estilo do canal
NOME = E.PAPEIS["protagonista"]
VULTO = Rasgado()
FALA = [(T_QUARTO + 0.4, "ELE"), (T_QUARTO + 0.7, "VOLTOU"), (T_QUARTO + 1.2, "PRA"), (T_QUARTO + 1.45, "PORTA.")]


def audio(saida):
    tr = S.trilha(DUR, silencios=((T_QUARTO - 0.4, T_QUARTO + 0.3),)) * 0.8
    m = S.mix(tr, S.vento(DUR) * 0.9,
              S.coloca(DUR, S.rangido(), 0.2, 0.6),
              S.coloca(DUR, S.ding(), 0.3),
              S.coloca(DUR, S.corvo(), T_ABRE + 0.8, 0.8),
              S.coloca(DUR, S.batidas(), T_QUARTO + 2.0, 0.9),
              S.coloca(DUR, S.ding(nota=91), T_VOTO),
              S.coloca(DUR, S.sussurros(3.0), T_VOTO + 0.3, 0.7), dur=DUR)
    bruto = saida.with_name(saida.stem + "_bruto.wav")
    S.salva(bruto, S.normaliza(m, 0.85))
    A = CFG["audio"]
    masterizar([bruto], saida, A["lufs"], A["pico_dbtp"], A["lra"], A["taxa"])
    bruto.unlink()
    return saida


def quadro(c, t):
    ts = E.stop(t)                 # pose em degraus de 12 por segundo (peças recolocadas); a câmera anda liso
    with G.quadro(c, t, **G.tinta.NOITE):
        if t < T_QUARTO:
            cam = CamG(x=0.2, h=1.5, F=760, hz=1080, z=-0.4 + 0.12 * t)
            ref = CamG(x=0.2, h=1.5, F=760, hz=1080, z=-0.4)   # câmera do 1º quadro: o primeiro plano anda com o mundo
            PS.estrada_neblina(c, t, cam=cam, ref=ref, atores=[(1.6, 26.0, lambda cc, x, y, a: VULTO.desenhar(cc, x, y, a, {"t": ts}), 2.4)])
            UI.intertitulo(c, t, 0.0, "TEM ALGUÉM NA ESTRADA", "sempre que a neblina desce", dur=T_ABRE)
            UI.abertura(c, t, T_ABRE + 0.2, "A Casa da Estrada", "Parte 1", dur=2.4)
        else:
            pose = G.pose_medo(1.0, t=ts, olhar=(0.5, -0.1))
            IN.quarto_vela(c, t, atores=[(-0.2, 2.3, lambda cc, x, y, a: PROT.desenhar(cc, x, y, a, pose), 1.65)])
            if t < T_VOTO:
                UI.legenda(c, FALA, chave=("PORTA.",), t=t)
        UI.selos_ficcao(c, "A CASA DA ESTRADA · PARTE 1 · FICÇÃO", "FICÇÃO")
        UI.voto_cartao(c, t, T_VOTO, f"O que {NOME} faz?", [("Abrir", "e descobre quem bate", "olho_aberto"),
                                                         ("Esconder", "e espera a neblina subir", "esconder")],
                       duracao=DUR - T_VOTO + 0.5, rotulo="PARTE", numero=1)


def main():
    saida = pasta("trabalho") / "demo_papel"
    saida.mkdir(parents=True, exist_ok=True)
    stills = "--stills" in sys.argv
    som = None if stills else audio(saida / "demo_papel.wav")
    renderizar(quadro, DUR, saida / "demo_papel.mp4", audio=som, cpu="--cpu" in sys.argv,
               marcos=[1.2, 3.6, 6.2, 10.2], so_marcos=stills)


if __name__ == "__main__":
    main()
