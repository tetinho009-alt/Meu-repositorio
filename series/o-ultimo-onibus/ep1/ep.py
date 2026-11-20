"""O Último Ônibus · Parte 1 · "O ponto que não existe" (canal Rua Sem Saída).

Estilo desenhado do canal (recorte de papel, proporção realista). Narrador: voz grátis do Google (Gemini TTS, Charon),
uma tomada por linha do narrador.txt. Trilha e efeitos por código. Roteiro em roteiro.md, bíblia em ../SERIE.md.

Uso (da pasta kit/):
    python ../series/o-ultimo-onibus/ep1/ep.py --stills     # quadros-marco (sem gravar voz)
    python ../series/o-ultimo-onibus/ep1/ep.py              # vídeo completo
"""
import argparse
import json
import math
import os
import random
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
KIT = AQUI.parents[2] / "kit"
sys.path.insert(0, str(KIT))

import numpy as np  # noqa: E402
import skia  # noqa: E402

from config import CFG, pasta  # noqa: E402

import estilo_desenhado as G  # noqa: E402
from estilo_desenhado import elenco as E, interface as UI, tinta as T  # noqa: E402
from estilo_desenhado.ameaca import Rasgado  # noqa: E402
from estilo_desenhado.cenario3d import CamG, Cena, LAMPADA, _fixa, poste, tex_parede  # noqa: E402
from estilo_desenhado.personagem import BonecoPapel, PADRAO  # noqa: E402
from estilo_desenhado.elenco import pose_sentada_cama  # noqa: E402

W, H = 1080, 1920
NOME = "o_ultimo_onibus_p1"
SERIE = "O Último Ônibus"
PROVEDOR, VOZ = "gemini", "Charon"

ap = argparse.ArgumentParser()
ap.add_argument("--stills", action="store_true")
ap.add_argument("--cpu", action="store_true")
ARGS, _ = ap.parse_known_args()

# ---------------------------------------------------------------- elenco

_prot = E.ELENCO[E.PAPEIS["protagonista"]]
DAVI = BonecoPapel("Davi", cfg={**PADRAO, **_prot, "cabelo_estilo": "curto", "roupa": "#4A6FA5", "roupa_esc": "#35517C",
                                "roupa_tipo": "blusa"})
LURDES = E.pessoa("idoso")
VULTO = Rasgado()

# ---------------------------------------------------------------- narração e linha do tempo

LINHAS = [l.strip() for l in (AQUI / "narrador.txt").read_text(encoding="utf-8").splitlines() if l.strip()]
PAUSAS = {0: 0.35, 1: 0.5, 5: 0.5, 9: 0.45, 11: 0.5, 13: 0.6, 15: 0.7, 16: 0.5, 19: 0.4, 20: 1.4, 21: 0.6, 23: 0.6,
          24: 0.6}
CAUDA_VOTO = 9.5        # a tela de voto fica ~10 s depois da pergunta
B_VOTO = 25             # "E agora? O que o Davi faz?"


def preparar():
    trab = pasta("trabalho") / NOME
    arq_linha = trab / "linha.json"
    if os.environ.get("MAQUINA_FATIA"):
        return json.loads(arq_linha.read_text(encoding="utf-8")), trab, None
    from cartelas import audio as AU
    from estilo_desenhado import som as SD
    from maquina import som as S
    trab.mkdir(parents=True, exist_ok=True)
    aud = trab / "audio"
    blocos = [{"fala": l, "pausa": PAUSAS.get(i, 0.3)} for i, l in enumerate(LINHAS)]
    blocos[B_VOTO]["pausa"] = CAUDA_VOTO
    blocos[-1]["pausa"] = 1.2
    arqs = None if ARGS.stills else AU.gerar_vozes(blocos, PROVEDOR, VOZ, aud)
    narr, janelas, total = AU.juntar(blocos, arqs)
    wav = None
    if not ARGS.stills:
        wav = aud / "narracao.wav"
        S.gravar_wav(wav, np.stack([narr, narr], axis=1))
    por_bloco, _, _ = AU.palavras(blocos, janelas, wav)
    falas = []
    for i, (j, ws) in enumerate(zip(janelas, por_bloco)):
        falas.append({"t0": j["t0"], "t1": j["t1"], "palavras": [[round(a, 3), p] for a, p in ws]})
    segs = [0.0] + [max(0.0, f["t0"] - 0.12) for f in falas[1:]] + [total]
    for i, f in enumerate(falas):
        f["seg0"], f["seg1"] = round(segs[i], 3), round(segs[i + 1], 3)
    linha = {"total": round(total, 3), "falas": falas}
    arq_linha.write_text(json.dumps(linha, ensure_ascii=False, indent=1), encoding="utf-8")
    if ARGS.stills:
        return linha, trab, None
    # ---- som: motor, campainha, porta, poste, silêncio do clímax
    F = falas
    m = S.Mesa(total)
    m.poe(0.0, narr, voz=True)
    _poe = m.poe

    def poe_mono(t0, x, **kw):   # os efeitos do estilo desenhado saem em estéreo; a mesa recebe mono e faz o pan
        x = np.asarray(x)
        if x.ndim == 2:
            x = x.mean(axis=1)
        if SD.SR != S.SR:
            x = np.interp(np.linspace(0, len(x) - 1, int(len(x) * S.SR / SD.SR)), np.arange(len(x)), x)
        return _poe(t0, x, **kw)
    m.poe = poe_mono

    def ate(i):
        return F[i]["seg0"]
    motor = SD._passa_baixa(S.drone(total + 1, f=38.0) * 1.0 + np.random.default_rng(3).normal(0, 0.05, int((total + 1) * S.SR)), 220)
    m.poe(0.0, motor[: int(ate(20) * S.SR) + S.SR // 2], ganho=0.7)                      # motor até o clímax
    m.poe(ate(21) + 1.2, motor[: int((total - ate(21)) * S.SR)], ganho=0.45)             # motor parado (baixo) depois
    m.poe(0.0, SD.drone(total, raiz=28), ganho=0.5)
    m.poe(0.0, SD.rangido(1.2, f_base=140), ganho=0.6)                                  # porta pneumática no quadro 0
    for t0 in (F[1]["t0"] - 0.05, F[18]["t0"] + 0.9, F[26]["t1"] + 0.1):                  # campainha de parada
        m.poe(max(0.0, t0), SD.ding(nota=86), ganho=0.9)
    m.poe(F[19]["t0"], SD.rangido(1.4, semente=33, f_base=120), ganho=0.7)               # porta abrindo
    m.poe(F[9]["t0"], SD.vento(F[12]["t0"] - F[9]["t0"]), ganho=0.5)
    m.poe(F[12]["t1"] + 0.05, SD.estalo_seco(), ganho=0.9)                               # golpe no relance
    m.poe(F[21]["t0"], SD.estalo_seco(semente=40), ganho=1.0)                            # a luz apaga
    m.poe(F[24]["t0"] + 0.3, SD.ding(nota=96, semente=9), ganho=0.5)                     # bipe do validador
    m.poe(F[B_VOTO]["t0"], S.subida(total - F[B_VOTO]["t0"]), ganho=0.8)
    m.poe(F[B_VOTO]["t1"] + 0.3, SD.sussurros(4.0), ganho=0.5)
    m.silencio(F[20]["t1"] + 0.05, F[20]["t1"] + 1.15)                                     # 1 s de silêncio total
    m.gravar(aud / "mix.wav", duck=0.6)
    from masterizar import masterizar
    A = CFG["audio"]
    final = aud / "mix_norm.wav"
    masterizar([aud / "mix.wav"], final, A["lufs"], A["pico_dbtp"], A["lra"], A["taxa"])
    return linha, trab, final


LINHA, TRAB, AUDIO = preparar()
F = LINHA["falas"]
TOTAL = LINHA["total"]


def seg(i):
    return F[i]["seg0"]


def bloco(t):
    for i, f in enumerate(F):
        if f["seg0"] <= t < f["seg1"]:
            return i
    return len(F) - 1


# ---------------------------------------------------------------- cores

AMBAR = (255, 168, 40)
LUZ_FRIA = (200, 225, 235)
LUZ_POSTE = (236, 176, 96)
VERDE = tuple(UI.OPCAO[0])

# ---------------------------------------------------------------- o ônibus (peças 3D)

ONIBUS_COR = (196, 196, 186)
ONIBUS_FAIXA = (60, 120, 92)


def onibus(cena, X, Z0, luz=1.0, porta=0.0, vivo=True, letreiro=True):
    """Ônibus urbano de papel: caixa comprida, faixa verde, janelas acesas de luz fria, para-brisa e letreiro âmbar.
    Frente virada pra câmera (z menor), lado direito (x maior) é o da porta."""
    x0, x1 = X - 1.3, X + 1.3
    z0, z1 = Z0, Z0 + 12.0
    y0, y1 = 0.35, 3.2
    cena.caixa(x0, x1, y0, y1, z0, z1, ONIBUS_COR, vivo=vivo)
    for x in (x0 - 0.005, x1 + 0.005):   # faixa e janelas nos dois lados
        cena.face([(x, 0.9, z0), (x, 0.9, z1), (x, 1.2, z1), (x, 1.2, z0)], ONIBUS_FAIXA, contorno=0.6, hach=False, vivo=vivo)
        z = z0 + 1.6
        while z < z1 - 1.0:
            jan = [(x, 1.6, z), (x, 1.6, z + 1.3), (x, 2.7, z + 1.3), (x, 2.7, z)]
            cena.face(jan, T.mistura((22, 30, 38), LUZ_FRIA, 0.75 * luz), contorno=0.8, hach=False, luz_extra=luz, vivo=vivo)
            z += 1.5
    zf = z0 - 0.005
    cena.face([(x0 + 0.15, 1.5, zf), (x1 - 0.15, 1.5, zf), (x1 - 0.15, 2.65, zf), (x0 + 0.15, 2.65, zf)],
              T.mistura((18, 24, 30), LUZ_FRIA, 0.35 * luz), contorno=0.8, hach=False, luz_extra=0.4 * luz, vivo=vivo)   # para-brisa
    if letreiro:
        cena.face([(x0 + 0.25, 2.72, zf), (x1 - 0.25, 2.72, zf), (x1 - 0.25, 3.08, zf), (x0 + 0.25, 3.08, zf)],
                  T.mistura((20, 12, 4), AMBAR, 0.85), contorno=0.6, hach=False, luz_extra=1.0, vivo=vivo)
    for x in (x0 + 0.35, x1 - 0.35):   # faróis
        cena.face([(x - 0.18, 0.7, zf), (x + 0.18, 0.7, zf), (x + 0.18, 0.92, zf), (x - 0.18, 0.92, zf)], (250, 236, 190),
                  contorno=0.5, hach=False, luz_extra=1.0, vivo=vivo)
    if porta > 0:   # a porta da frente aberta (lado direito): um retângulo de luz
        cena.face([(x1 + 0.01, 0.35, z0 + 0.4), (x1 + 0.01, 0.35, z0 + 1.4), (x1 + 0.01, 2.6, z0 + 1.4), (x1 + 0.01, 2.6, z0 + 0.4)],
                  T.mistura((30, 36, 40), LUZ_FRIA, 0.9 * luz), contorno=0.8, hach=False, luz_extra=luz, vivo=vivo)
    for zr in (z0 + 1.8, z1 - 2.0):   # rodas
        for x in (x0 - 0.01, x1 + 0.01):
            cena.face([(x, 0.0, zr - 0.5), (x, 0.0, zr + 0.5), (x, 0.9, zr + 0.5), (x, 0.9, zr - 0.5)], (20, 20, 24), contorno=0.6,
                      hach=False, vivo=vivo)


def predio(cena, x0, x1, z0, z1, h, cor, semente, lado):
    rnd = random.Random(semente)
    cena.caixa(x0, x1, 0.0, h, z0, z1, cor, textura_face=lambda pts: tex_parede(pts, semente, picho=0.5, umidade=0.6, rachas=1))
    xf = x1 + 0.01 if lado < 0 else x0 - 0.01
    y = 1.0
    while y < h - 1.0:
        z = z0 + 0.6
        while z < z1 - 0.8:
            acesa = rnd.random() < 0.12
            jan = [(xf, y, z), (xf, y, z + 0.9), (xf, y + 1.0, z + 0.9), (xf, y + 1.0, z)]
            cena.face(jan, (236, 190, 110) if acesa else (16, 18, 24), contorno=0.6, hach=False, luz_extra=1.0 if acesa else 0.0)
            z += 1.6
        y += 2.8


def _avenida_fixa(cam):
    """Avenida da zona leste de madrugada: asfalto, calçadas, prédios baixos com poucas janelas acesas, postes."""
    cena = Cena(cam, 0.0, nevoa=(24, 28, 36), alcance=70.0, luz=(0.4, 0.6, 0.7), w_tinta=2.6)
    cena.face([(-60, 0, -10), (60, 0, -10), (60, 0, 160), (-60, 0, 160)], (26, 28, 32), z=900, hach=False)
    cena.face([(-4.0, 0.01, -10), (4.0, 0.01, -10), (4.0, 0.01, 160), (-4.0, 0.01, 160)], (44, 46, 52), z=899, hach=False)
    for z in range(-8, 150, 6):
        cena.face([(-0.08, 0.02, z), (0.08, 0.02, z), (0.08, 0.02, z + 2.5), (-0.08, 0.02, z + 2.5)], (170, 160, 110), contorno=0.0,
                  hach=False, z=898)
    for lado in (-1, 1):
        cena.face([(lado * 4.0, 0.15, -10), (lado * 7.0, 0.15, -10), (lado * 7.0, 0.15, 160), (lado * 4.0, 0.15, 160)], (78, 76, 74),
                  z=897, hach=False)
        rnd = random.Random(7 + lado)
        z = -6.0
        k = 0
        while z < 140:
            comp = rnd.uniform(6, 11)
            h = rnd.choice((4.0, 6.5, 9.0, 12.0))
            cor = rnd.choice(((96, 100, 110), (110, 104, 98), (84, 92, 100), (120, 114, 104)))
            x0, x1 = (7.2, 15.0) if lado > 0 else (-15.0, -7.2)
            predio(cena, x0, x1, z, z + comp, h, cor, 50 + k + 10 * lado, lado)
            z += comp + rnd.uniform(0.2, 1.0)
            k += 1
        for zp in range(4, 140, 16):
            poste(cena, lado * 4.6, zp, alt=7.0, inclina=-0.03 * lado, lado=-lado, acesa=1.0, semente=90 + zp)
    for zn, al, hh in ((40.0, 0.12, 3.0), (80.0, 0.2, 6.0), (130.0, 0.3, 12.0)):
        cena.neblina(zn, altura=hh, alfa=al)
    return cena


def _rua_sem_placa_fixa(cam):
    """A rua estreita que não está no mapa: sem prédio, muro comprido sem janela, um poste só, calçada sem placa."""
    cena = Cena(cam, 0.0, nevoa=(16, 18, 24), alcance=40.0, luz=(0.4, 0.6, 0.7), w_tinta=2.6)
    cena.face([(-60, 0, -10), (60, 0, -10), (60, 0, 160), (-60, 0, 160)], (14, 16, 20), z=900, hach=False)
    cena.face([(-2.6, 0.01, -10), (2.6, 0.01, -10), (2.6, 0.01, 160), (-2.6, 0.01, 160)], (34, 36, 40), z=899, hach=False)
    for lado in (-1, 1):
        cena.face([(lado * 2.6, 0.15, -10), (lado * 4.2, 0.15, -10), (lado * 4.2, 0.15, 160), (lado * 2.6, 0.15, 160)], (54, 54, 56),
                  z=897, hach=False)
        x = lado * 4.3
        cena.face([(x, 0, -10), (x, 0, 160), (x, 3.2, 160), (x, 3.2, -10)], (46, 48, 54), z=896,
                  textura=tex_parede([(x, 0, -10), (x, 0, 160), (x, 3.2, 160), (x, 3.2, -10)], 77 + lado, picho=0.2, umidade=1.0, rachas=3))
    poste(cena, 3.4, 14.0, alt=6.5, inclina=-0.06, lado=-1, acesa=1.0, semente=7)
    for zn, al, hh in ((18.0, 0.18, 1.6), (32.0, 0.3, 3.0), (60.0, 0.5, 8.0)):
        cena.neblina(zn, altura=hh, alfa=al)
    return cena


def rua(c, t, cam, sem_placa=False, onibus_z=None, onibus_x=0.0, luz_bus=1.0, porta=0.0, atores=(), escuro=0.55):
    nome = "sem_placa" if sem_placa else "avenida"
    cena = _fixa(nome, cam, t, _rua_sem_placa_fixa if sem_placa else _avenida_fixa)
    if onibus_z is not None:
        onibus(cena, onibus_x, onibus_z, luz=luz_bus, porta=porta)
        cena.luz(onibus_x, 0.4, onibus_z - 2.5, 5.0, (250, 236, 190), 0.7 * luz_bus, chao=True, vivo=True)
    for X, Z, desenha, alt in atores:
        cena.ator(X, Z, desenha, alt, rim=0.3)
    pisca = 0.25 if (sem_placa and int(t * 7) % 5 == 0) else 1.0      # o poste da rua sem placa falha
    buracos = [(3.4 - 0.4, 6.0, 14.0, 6.0, 0.9 * pisca)] if sem_placa else \
        [(s * 4.6, 6.4, zp, 7.0, 0.9) for s in (-1, 1) for zp in range(4, 140, 16)]
    if onibus_z is not None:
        buracos.append((onibus_x, 1.8, onibus_z + 4, 6.0, 0.8 * luz_bus))
    cena.escuro(escuro, buracos, tom=(6, 6, 10))
    c.drawPaint(T.tinta_paint((6, 7, 12)))
    cena.desenha(c, ceu=lambda cc, ce: cc.drawPaint(T.tinta_paint((8, 10, 18))))
    return cena


# ---------------------------------------------------------------- o ônibus por dentro

BANCOS_Z = (1.6, 2.6, 3.6, 4.6, 5.6, 6.6, 7.6)


def _interior_fixo(cam):
    """Corredor do ônibus: piso de borracha, bancos azuis de plástico dos dois lados, janelas escuras, balaústres,
    teto com as calhas de luz fria, catraca e validador lá na frente (z pequeno), banco do fundo inteiro."""
    cena = Cena(cam, 0.0, nevoa=(20, 24, 30), alcance=30.0, luz=(0.2, 0.9, -0.3), w_tinta=2.4)
    x0, x1, y1, z0, zf = -1.25, 1.25, 2.25, -1.0, 9.0
    cena.face([(x0, 0, z0), (x1, 0, z0), (x1, 0, zf), (x0, 0, zf)], (58, 60, 64), z=100, hach=False)
    cena.face([(x0, y1, z0), (x1, y1, z0), (x1, y1, zf), (x0, y1, zf)], (150, 150, 144), z=100)
    cena.face([(x0, 0, zf), (x1, 0, zf), (x1, y1, zf), (x0, y1, zf)], (120, 122, 118), z=99)
    cena.face([(x0 + 0.3, 1.1, zf - 0.01), (x1 - 0.3, 1.1, zf - 0.01), (x1 - 0.3, 2.0, zf - 0.01), (x0 + 0.3, 2.0, zf - 0.01)],
              (14, 18, 24), contorno=0.8, hach=False, z=98.9)   # vidro de trás, escuro
    for x in (x0, x1):
        cena.face([(x, 0, z0), (x, 0, zf), (x, y1, zf), (x, y1, z0)], (136, 136, 130), z=98)
        cena.face([(x, 0.95, z0), (x, 0.95, zf), (x, 1.05, zf), (x, 1.05, z0)], ONIBUS_FAIXA, contorno=0.4, hach=False, z=97.9)
        z = z0 + 0.4
        while z < zf - 0.6:
            cena.face([(x, 1.15, z), (x, 1.15, z + 1.1), (x, 2.0, z + 1.1), (x, 2.0, z)], (14, 18, 24), contorno=0.8, hach=False, z=97.8)
            z += 1.3
    for xc, sgn in ((-0.75, -1), (0.75, 1)):   # fileiras de bancos
        for z in BANCOS_Z:
            cena.caixa(xc - 0.45, xc + 0.45, 0.42, 0.5, z, z + 0.45, (40, 70, 130))                      # assento
            cena.caixa(xc - 0.45, xc + 0.45, 0.5, 1.15, z + 0.4, z + 0.5, (46, 80, 146))                 # encosto
    cena.caixa(x0, x1, 0.42, 1.15, zf - 0.55, zf - 0.05, (40, 70, 130))                                     # banco do fundo inteiro
    for z in (1.0, 3.1, 5.1, 7.1):   # balaústres e o cano do teto
        for x in (-0.28, 0.28):
            cena.linha([(x, 0, z), (x, y1, z)], 1.2, cor=(200, 196, 160))
    for x in (-0.3, 0.3):
        cena.linha([(x, y1 - 0.12, z0), (x, y1 - 0.12, zf)], 0.9, cor=(200, 196, 160))
    for x in (-0.75, 0.75):   # calhas de luz
        cena.face([(x - 0.12, y1 - 0.01, z0 + 0.5), (x + 0.12, y1 - 0.01, z0 + 0.5), (x + 0.12, y1 - 0.01, zf - 0.5),
                   (x - 0.12, y1 - 0.01, zf - 0.5)], (236, 244, 246), contorno=0.4, hach=False, luz_extra=1.0, z=99.5)
    cena.caixa(0.6, 0.95, 0.0, 1.0, 0.3, 0.45, (90, 92, 96))   # catraca
    cena.caixa(0.98, 1.2, 0.95, 1.3, 0.3, 0.45, (40, 40, 44))  # validador
    return cena


def interior(c, t, cam, luz=1.0, atores=(), lurdes=True, fundo_vulto=False):
    cena = _fixa("interior", cam, t, _interior_fixo)
    if lurdes:
        cena.ator(-0.75, 1.75, lambda cc, x, y, a: LURDES.desenhar(cc, x, y, a, pose_sentada_cama(E.stop(t), medo=0.0,
                                                                                                   olhar=(0.0, 0.0))), 1.6, rim=0.2)
    if fundo_vulto:
        cena.ator(0.2, 8.6, lambda cc, x, y, a: VULTO.desenhar(cc, x, y, a, {"t": E.stop(t)}), 2.1, rim=0.0)
    for a_ in atores:
        X, Z, desenha, alt = a_
        cena.ator(X, Z, desenha, alt, rim=0.2)
    buracos = [(x, 2.2, z, 2.6, 0.95 * luz) for x in (-0.75, 0.75) for z in (1.0, 3.5, 6.0, 8.0)]
    cena.escuro(0.2 + 0.75 * (1 - luz), buracos, tom=(4, 6, 10))
    c.drawPaint(T.tinta_paint((4, 6, 10)))
    cena.desenha(c)
    return cena


# ---------------------------------------------------------------- closes 2D (papel)

def _papel_fundo(c, cor, semente=1):
    c.drawPaint(T.tinta_paint(cor))
    c.drawPaint(T.fibra_paint(semente, 0.5, 1.6))


def _ret(x, y, w, h):
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def letreiro(c, t, texto="340 · 00:40", aceso=1.0, zoom=1.0):
    """Close do letreiro de LED do ônibus: placa preta, pontinhos âmbar acesos formando o texto."""
    _papel_fundo(c, (10, 10, 14), 3)
    c.save()
    c.translate(W / 2, H * 0.42)
    c.scale(zoom, zoom)
    c.translate(-W / 2, -H * 0.42)
    d = T.Desenho()
    T.peca(d, _ret(60, 620, W - 120, 380), (24, 22, 26), 11, sombra=1.4)
    T.peca(d, _ret(90, 650, W - 180, 320), (6, 6, 8), 12, sombra=0.4)
    d.desenha(c)
    if aceso > 0.02:
        # o texto vira máscara de pontos (matriz de LED)
        sup = skia.Surface(W, H)
        cc = sup.getCanvas()
        cc.clear(skia.Color4f(0, 0, 0, 0))
        f = skia.Font(skia.Typeface("DejaVu Sans Mono", skia.FontStyle.Bold()), 112)
        largura = f.measureText(texto)
        cc.drawString(texto, W / 2 - largura / 2, 850, f, skia.Paint(Color=skia.ColorWHITE))
        img = sup.makeImageSnapshot().toarray()
        passo = 14
        brilho = skia.Paint(AntiAlias=True, Color=T.cor_skia(AMBAR, 90 * aceso),
                            MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10))
        ponto = skia.Paint(AntiAlias=True, Color=T.cor_skia(T.mistura(AMBAR, (255, 240, 200), 0.3), 255 * aceso))
        apag = skia.Paint(AntiAlias=True, Color=T.cor_skia((40, 26, 10), 255))
        for y in range(660, 960, passo):
            for x in range(100, W - 100, passo):
                if img[y, x, 3] > 100:
                    c.drawCircle(x, y, 7, brilho)
                    c.drawCircle(x, y, 5, ponto)
                else:
                    c.drawCircle(x, y, 2.4, apag)
    c.restore()


def celular(c, t, u):
    """Tela do celular: o mapa com o pontinho azul num lugar em branco; depois a mensagem que não vai."""
    _papel_fundo(c, (12, 14, 20), 5)
    d = T.Desenho()
    T.peca(d, _ret(230, 300, 620, 1240), (18, 18, 22), 21, sombra=1.6)
    T.peca(d, _ret(260, 360, 560, 1110), (232, 230, 220), 22, sombra=0.3)
    d.desenha(c)
    if u < 0.5:   # mapa: ruas até a metade, depois branco
        for k in range(7):
            y = 420 + k * 70
            c.drawLine(260, y, 820, y + 30, skia.Paint(AntiAlias=True, Color=T.cor_skia((190, 186, 170)), StrokeWidth=10))
        c.drawLine(540, 360, 520, 860, skia.Paint(AntiAlias=True, Color=T.cor_skia((236, 196, 90)), StrokeWidth=22))
        pis = 0.5 + 0.5 * math.sin(t * 6)
        c.drawCircle(530, 1150, 46 + 10 * pis, skia.Paint(AntiAlias=True, Color=T.cor_skia((60, 130, 240), 70)))
        c.drawCircle(530, 1150, 26, skia.Paint(AntiAlias=True, Color=T.cor_skia((60, 130, 240))))
        UI.texto_tinta(c, "VOCÊ ESTÁ AQUI", 540, 1250, 40, (60, 60, 70), t=t, nome=UI.TEXTO, borda=0, sombra=False, rugoso=0)
    else:
        UI.texto_tinta(c, "MÃE", 540, 430, 54, (40, 40, 50), t=t, borda=0, sombra=False, rugoso=0)
        d2 = T.Desenho()
        T.peca(d2, _ret(400, 760, 380, 130), (120, 200, 140), 23, sombra=0.4)
        d2.desenha(c)
        UI.texto_tinta(c, "tô indo", 590, 840, 44, (20, 40, 26), t=t, nome=UI.TEXTO, borda=0, sombra=False, rugoso=0)
        UI.texto_tinta(c, "não enviada", 640, 940, 30, (200, 60, 50), t=t, nome=UI.TEXTO, borda=0, sombra=False, rugoso=0)
        UI.texto_tinta(c, "SEM SINAL", 540, 1180, 84, VERDE, t=t)


def vidro(c, t, u, texto=None, reflexo=0.0):
    """Close no vidro da janela: escuro lá fora, embaçado, com gotas; o reflexo do banco do fundo (4 quadros) ou a
    frase escrita com o dedo."""
    _papel_fundo(c, (16, 22, 30), 9)
    rnd = random.Random(4)
    for _ in range(90):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(2, 7)
        c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Color=T.cor_skia((150, 170, 190), 90)))
    c.drawRect(skia.Rect.MakeWH(W, H), T.tinta_paint((170, 186, 196), 70))
    if reflexo > 0:
        c.saveLayer(None, skia.Paint(Alphaf=0.55 * reflexo))
        VULTO.desenhar(c, 700, 1500, 900, {"t": E.stop(t)})
        c.restore()
    if texto:
        n = len(texto)
        k = min(1.0, u * 1.6)
        visivel = texto[: max(1, int(n * k))]
        for i, linha in enumerate(visivel.split("\n")):
            UI.texto_tinta(c, linha, W / 2, 760 + i * 150, 120, (12, 16, 22), t=t, borda=0, sombra=False, rugoso=1.6)


def validador(c, t, u):
    _papel_fundo(c, (10, 10, 14), 13)
    d = T.Desenho()
    T.peca(d, _ret(210, 520, 660, 820), (54, 56, 60), 31, sombra=1.6)
    T.peca(d, _ret(280, 600, 520, 300), (20, 34, 30), 32, sombra=0.4)
    T.peca(d, _ret(330, 1000, 420, 260), (90, 92, 98), 33, sombra=0.8)
    d.desenha(c)
    texto = "00:40" if u < 0.3 else "14/03/2009"
    cor = (140, 240, 170)
    f = skia.Font(skia.Typeface("DejaVu Sans Mono", skia.FontStyle.Bold()), 96 if len(texto) > 6 else 140)
    largura = f.measureText(texto)
    pis = 1.0 if u < 0.3 or int(t * 10) % 7 else 0.4
    c.drawString(texto, W / 2 - largura / 2, 790, f, skia.Paint(AntiAlias=True, Color=T.cor_skia(cor, 255 * pis),
                                                               MaskFilter=skia.MaskFilter.MakeBlur(skia.kSolid_BlurStyle, 6)))
    UI.texto_tinta(c, "APROXIME O CARTÃO", W / 2, 1140, 40, (220, 220, 220), t=t, nome=UI.TEXTO, borda=0, sombra=False, rugoso=0)


def nuca_motorista(c, t):
    """O motorista de costas: banco, nuca e o boné, o para-brisa escuro lá na frente com a rua sem placa."""
    _papel_fundo(c, (8, 10, 14), 17)
    d = T.Desenho()
    T.peca(d, _ret(120, 300, 840, 560), (16, 20, 26), 41, sombra=0.6)                 # para-brisa
    T.peca(d, T.elipse(540, 1260, 300, 340, 40), (30, 34, 40), 42, sombra=1.2)       # ombros
    T.peca(d, T.elipse(540, 900, 150, 180, 36), (60, 44, 34), 43, sombra=1.0)        # nuca
    T.peca(d, T.elipse(540, 790, 165, 90, 30), (34, 40, 52), 44, sombra=1.0)         # boné
    T.peca(d, _ret(330, 1000, 420, 80), (52, 72, 110), 45, sombra=0.6)               # gola do uniforme
    T.peca(d, T.elipse(540, 1750, 360, 300, 40), (40, 44, 50), 46, sombra=1.0)       # encosto do banco
    d.desenha(c)
    c.drawCircle(860, 480, 26, skia.Paint(AntiAlias=True, Color=T.cor_skia(LUZ_POSTE, 200 if int(t * 7) % 5 else 60),
                                          MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 14)))


# ---------------------------------------------------------------- poses

def pose_davi(t, medo=0.0, olhar=(0.0, 0.0), dormindo=False):
    p = G.pose_medo(medo, t=E.stop(t), olhar=olhar)
    if dormindo:
        p["piscar"] = 1.0
    return p


def davi_sentado(t, medo=0.0, olhar=(0.0, 0.0), dormindo=False):
    def fn(c, x, y, a):
        p = pose_sentada_cama(E.stop(t), medo=medo, olhar=olhar)
        if dormindo:
            p["piscar"] = 1.0
            p["cabeca"] = {"rot": 14, "dy": 8}
        DAVI.desenhar(c, x, y, a, p)
    return fn


def close_davi(c, t, fundo, medo=0.0, olhar=(0.0, 0.0), dormindo=False, x=560, escala=1.0):
    """Close: o fundo (uma função que desenha o plano) desfocado e o Davi grande na frente, da cintura pra cima."""
    c.saveLayer(None, skia.Paint(ImageFilter=skia.ImageFilters.Blur(14, 14)))
    fundo(c)
    c.restore()
    c.drawRect(skia.Rect.MakeWH(W, H), T.tinta_paint((4, 6, 10), 70))
    p = pose_davi(t, medo, olhar, dormindo)
    if dormindo:
        p["cabeca"] = {"rot": 12, "dy": 6}
    DAVI.desenhar(c, x, 2650 * escala + (1 - escala) * 1900, 2300 * escala, p)


def davi_em_pe(t, medo=0.0, olhar=(0.0, 0.0), andando=False):
    def fn(c, x, y, a):
        p = E.andar(t, vel=0.8, medo=medo) if andando else pose_davi(t, medo, olhar)
        DAVI.desenhar(c, x, y, a, p)
    return fn


# ---------------------------------------------------------------- linha do tempo

def plano(c, t):
    b = bloco(t)
    u = t - seg(b)
    d = F[b]["seg1"] - F[b]["seg0"]
    k = u / max(d, 0.01)
    if b == 0:                                   # gancho: letreiro aceso, recua pro ônibus parado no ponto sem placa
        if t < 1.3:
            letreiro(c, t, zoom=1.25 - 0.15 * t)
        else:
            cam = CamG(x=3.0, h=1.6, F=1000, hz=900, z=-4.0 - 2.0 * (t - 1.3), yaw=-8)
            rua(c, t, cam, sem_placa=True, onibus_z=6.0, porta=1.0)
    elif b == 1:                                 # título: o letreiro com a hora
        letreiro(c, t, zoom=1.0 + 0.04 * u)
    elif b in (2, 3):                            # Davi sai do restaurante e anda pela avenida
        cam = CamG(x=-3.0, h=1.6, F=1400, hz=900, z=0.6 + 0.4 * (t - seg(2)), yaw=-14)
        x_davi = -5.0
        z_davi = 6.0 + (0.9 * (t - seg(3)) if b == 3 else 0.0)
        rua(c, t, cam, atores=[(x_davi, z_davi, davi_em_pe(t, andando=(b == 3)), 1.75)])
        if b == 3 and 1.2 <= u < 1.2 + 4 / 30:   # 4 quadros: o vulto no reflexo da vitrine
            c.saveLayer(None, skia.Paint(Alphaf=0.6))
            VULTO.desenhar(c, 180, 1150, 700, {"t": E.stop(t)})
            c.restore()
    elif b in (4, 5):                            # o ponto na avenida, Davi esperando, o 340 chegando
        cam = CamG(x=4.3, h=1.5, F=1200, hz=900, z=-0.6 + 0.15 * (t - seg(4)), yaw=0)
        bz = 50.0 - 7.0 * max(0.0, t - seg(5)) if b == 5 else 80.0
        rua(c, t, cam, onibus_z=bz, onibus_x=2.0, atores=[(5.0, 4.0, davi_em_pe(t, olhar=(-0.4, 0.0)), 1.75)])
    elif b == 6:                                 # por dentro: Dona Lurdes no primeiro banco
        cam = CamG(x=-0.2, h=1.5, F=900, hz=880, z=5.4 - 0.12 * u, yaw=180)
        interior(c, t, cam)
    elif b == 7:                                 # Davi senta, encosta no vidro e fecha o olho
        close_davi(c, t, lambda cc: interior(cc, t, CamG(x=0.6, h=1.3, F=900, hz=900, z=2.0, yaw=8)), dormindo=k > 0.55,
                   olhar=(0.4, 0.1))
    elif b in (8, 9):                            # acorda: a avenida acabou, a rua estreita sem placa descendo
        cam = CamG(x=0.0, h=3.4, F=950, hz=760, z=-6.0 + 1.2 * (t - seg(8)), pitch=6)
        rua(c, t, cam, sem_placa=True, onibus_z=4.0 + 1.2 * (t - seg(8)), luz_bus=1.0)
    elif b in (10, 11):                          # o celular
        celular(c, t, 0.0 if b == 10 else 1.0)
    elif b == 12:                                # o reflexo no vidro
        vidro(c, t, k, reflexo=1.0 if k > 0.45 else 0.0)
    elif b == 13:                                # vira: o banco do fundo vazio
        if k < 0.45:
            close_davi(c, t, lambda cc: interior(cc, t, CamG(x=0.0, h=1.4, F=900, hz=900, z=1.0, yaw=0)), medo=1.0,
                       olhar=(0.0, -0.2), x=420)
        else:   # o banco do fundo, vazio
            interior(c, t, CamG(x=0.0, h=1.3, F=1300, hz=900, z=3.0, yaw=0))
    elif b in (14, 15):                          # o vidro embaçado com a regra
        vidro(c, t, (t - seg(14)) / 3.0, texto="NUNCA DESÇA\nNUM PONTO\nSEM PLACA")
    elif b == 16:                                # pedido de seguir: o ônibus de fora na rua escura
        cam = CamG(x=-3.0, h=1.0, F=900, hz=980, z=-4.0, yaw=12)
        rua(c, t, cam, sem_placa=True, onibus_z=10.0 + 2.0 * u)
    elif b == 17:                                # parando devagar
        cam = CamG(x=3.0, h=1.4, F=1000, hz=900, z=-5.0, yaw=-10)
        rua(c, t, cam, sem_placa=True, onibus_z=8.0 + 2.0 * (1 - min(1.0, k)) - 2.0)
    elif b == 18:                                # a campainha toca sozinha
        cam = CamG(x=0.0, h=1.6, F=900, hz=880, z=8.6, yaw=180)
        interior(c, t, cam)
        if u > 0.6:
            UI.carimbo(c, "PARADA SOLICITADA", W / 2, 420, tam=50, rot=-2, t=t, cor=(200, 40, 30))
    elif b == 19:                                # a porta abre pra calçada escura e o poste piscando
        cam = CamG(x=1.2, h=1.6, F=900, hz=900, z=-3.0, yaw=0)
        rua(c, t, cam, sem_placa=True)
        porta = 1.0 - min(1.0, k * 2.0)
        for lado in (-1, 1):
            larg = W * 0.5 * porta
            x0 = 0 if lado < 0 else W - larg
            c.drawRect(skia.Rect.MakeXYWH(x0, 0, larg, H), T.tinta_paint((28, 30, 34)))
        c.drawRect(skia.Rect.MakeXYWH(0, 0, 120, H), T.tinta_paint((40, 42, 46)))
        c.drawRect(skia.Rect.MakeXYWH(W - 120, 0, 120, H), T.tinta_paint((40, 42, 46)))
    elif b == 20:                                # alguém chamou o nome dele: close de medo; depois 1 s de silêncio
        close_davi(c, t, lambda cc: interior(cc, t, CamG(x=0.6, h=1.3, F=900, hz=900, z=2.0, yaw=20)), medo=1.0,
                   olhar=(0.7, -0.1), escala=1.15)
    elif b == 21:                                # a luz apaga
        cam = CamG(x=0.0, h=1.55, F=900, hz=880, z=8.6, yaw=180)
        interior(c, t, cam, luz=0.0 if k < 0.7 else (0.2 if int(t * 12) % 2 else 0.0))
    elif b == 22:                                # volta: o primeiro banco vazio
        cam = CamG(x=0.0, h=1.55, F=900, hz=880, z=8.6 - 0.2 * u, yaw=180)
        interior(c, t, cam, lurdes=False)
    elif b == 23:                                # o motorista sem virar o rosto
        nuca_motorista(c, t)
    elif b == 24:                                # o validador mostra a data
        validador(c, t, k)
    elif b == B_VOTO:                            # a escolha: Davi pequeno na porta, a calçada escura
        cam = CamG(x=6.5, h=2.4, F=950, hz=820, z=-6.0 + 0.1 * u, yaw=-22)
        rua(c, t, cam, sem_placa=True, onibus_z=4.0, porta=1.0,
            atores=[(1.6, 4.8, davi_em_pe(t, medo=1.0, olhar=(0.7, 0.0)), 1.75)])
    else:                                        # fecho: o letreiro apagando
        letreiro(c, t, aceso=max(0.0, 1.0 - k * 1.4))


GANCHO_ATE = F[1]["seg0"]


def quadro(c, t):
    with G.quadro(c, t, **G.tinta.NOITE):
        plano(c, t)
        b = bloco(t)
        if t < GANCHO_ATE:
            a = 255 * min(1.0, (GANCHO_ATE - t) / 0.3)
            UI.texto_tinta(c, "O PONTO", W / 2, 330, 140, UI.OSSO, t=t, a=a)
            UI.texto_tinta(c, "NÃO EXISTE", W / 2, 470, 140, VERDE, t=t, a=a)
            UI.use_fone(c, t, 0.0, dur=GANCHO_ATE)
        UI.abertura(c, t, GANCHO_ATE + 0.1, SERIE, "o ponto que não existe", dur=max(3.0, F[1]["seg1"] - GANCHO_ATE))
        if b == 15:
            UI.cartao_regra(c, t, seg(15), 1, "Nunca desça num ponto sem placa", dur=F[15]["seg1"] - seg(15))
        if b == 16:
            UI.cta(c, t, seg(16) + 0.3, ["+ SEGUIR @ruasemsaida"], y=900, dur=F[16]["seg1"] - seg(16))
        if 2 <= b < B_VOTO and b not in (15,):
            f = F[b]
            if f["t0"] <= t <= f["t1"] + 0.35:
                ps = [tuple(p) for p in f["palavras"] if p[0] <= t + 0.03]
                if ps:
                    UI.legenda(c, ps, chave=("DAVI", "NUNCA.", "VAZIO.", "PLACA.", "DATA.", "SUMIDO.", "NOME"), t=t)
        if b == 26:
            f = F[b]
            ps = [tuple(p) for p in f["palavras"] if p[0] <= t + 0.03]
            if ps:
                UI.legenda(c, ps, chave=("VIU?",), t=t)
        if b < B_VOTO:
            UI.selos_ficcao(c, "O ÚLTIMO ÔNIBUS · PARTE 1 · FICÇÃO", "FICÇÃO")
        UI.voto_cartao(c, t, F[B_VOTO]["t1"] + 0.2, "O que o Davi faz?",
                       [("Desce", "e encara o ponto sem placa", "olho_aberto"), ("Fica", "e segue pra onde o ônibus for", "esconder")],
                       duracao=F[B_VOTO]["seg1"] - F[B_VOTO]["t1"] - 0.2, rotulo="PARTE", numero=1)


def main():
    from maquina.motor import renderizar
    marcos = [0.0, 1.8] + [round(f["seg0"] + 0.6 * (f["seg1"] - f["seg0"]), 2) for f in F[1:]]
    saida = TRAB / f"{NOME}.mp4"
    renderizar(quadro, TOTAL, saida, audio=AUDIO, cpu=ARGS.cpu, marcos=marcos, pasta_quadros=TRAB / "quadros",
               so_marcos=ARGS.stills)
    print(("STILLS_OK " + str(TRAB / "folha.jpg")) if ARGS.stills else ("VIDEO_OK " + str(saida)))


if __name__ == "__main__":
    main()
