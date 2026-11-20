# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Episódio de demonstração: "A Luz da Casa 7 · Parte 1 · Alguém acenou" (~16 s).

Uma rua de bairro em perspectiva (fila por profundidade), a casa 7 no fim da rua, um boneco (Lola), narração com
legenda palavra a palavra e o cartão de voto. Sincronizado a <trabalho>/linha.json (gerado pelo trilha.py).

Gancho no quadro 0: a primeira imagem já é a anomalia (a janela acesa, colada na câmera), com o texto grande e a voz
dizendo o que não devia acontecer, sem título antes. O nome da série entra depois do gancho.

É também o ponto de partida de um episódio novo (episodio_novo.py copia este arquivo): troque as cenas em `cena()`
e mantenha o resto (pós, legenda, selo, voto).

Uso: python ep.py --trabalho PASTA [--cpu] [--stills] [--saida video.mp4]
"""
import argparse
import json
import math
import random
import sys
from pathlib import Path

import skia

AQUI = Path(__file__).resolve().parent


def _acha_kit(aqui):
    """Pasta do kit: a primeira acima deste arquivo que tem maquina/ (ou a variável MAQUINA_KIT)."""
    import os
    for d in (aqui, *aqui.parents):
        if (d / "maquina" / "__init__.py").is_file():
            return d
    if os.environ.get("MAQUINA_KIT"):
        return Path(os.environ["MAQUINA_KIT"])
    raise SystemExit("não achei a pasta do kit; defina MAQUINA_KIT")


sys.path.insert(0, str(_acha_kit(AQUI)))

from maquina import cinema as C  # noqa: E402
from maquina import slug  # noqa: E402
from maquina import perspectiva as P  # noqa: E402
from maquina import tela as T  # noqa: E402
from maquina.desenho import (CX_SEGURO, FPS, LARG_SEGURA, H, W, caber, cheio, degrade, ease, fonte, mix,  # noqa: E402
                             texto_c, traco)
from maquina.legenda import legenda, palavras_do_evento  # noqa: E402
from maquina.motor import renderizar  # noqa: E402
from maquina.rig import MEDO, Boneco, piscadas, piscar, respira  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--trabalho", required=True)
ap.add_argument("--cpu", action="store_true", help="força render na CPU + libx264")
ap.add_argument("--stills", action="store_true", help="só os quadros-marco (conferência rápida)")
ap.add_argument("--saida")
ARGS = ap.parse_args()

TRAB = Path(ARGS.trabalho)
EP = json.loads((AQUI / "episodio.json").read_text(encoding="utf-8"))
LN = json.loads((TRAB / "linha.json").read_text(encoding="utf-8"))
EV = {e["tipo"]: e for e in LN["eventos"]}
TOTAL, T_LUZ, T_ACENO, T_VOTO, CORTES = LN["total"], LN["t_luz"], LN["t_aceno"], LN["t_voto"], LN["cortes"]
SERIE, PARTE, TITULO = EP["serie"], EP["parte"], EP["titulo"]
LOLA = Boneco(EP["personagem"])
PISCADAS = piscadas(TOTAL, semente=11)

# ---------------------------------------------------------------- mundo (metros)

CASA7 = dict(x0=-4.5, x1=4.5, z0=24.0, z1=32.0, h=6.2)
JANELA = (-2.45, -1.15, 3.7, 5.0)           # x0, x1, y0, y1 na fachada da casa 7 (a janela que acende)
POSTE = (3.3, 8.5)
LUZ_POSTE = (255, 205, 150)
LUZ_JANELA = (255, 214, 140)


def _casas_laterais():
    rnd = random.Random(5)
    casas = []
    for lado in (-1, 1):
        z = 2.0
        while z < 22.5:
            comp = rnd.uniform(5.5, 7.5)
            alto = 5.4 if rnd.random() < 0.35 else 3.2
            cor = rnd.choice([(150, 132, 120), (120, 136, 150), (160, 140, 110), (126, 120, 140), (140, 150, 128)])
            janelas = [(z + comp * f, rnd.random() < 0.3) for f in (0.3, 0.7)]
            casas.append(dict(lado=lado, z0=z, z1=min(z + comp, 23.4), h=alto, cor=cor, janelas=janelas))
            z += comp + rnd.uniform(0.2, 0.6)
    return casas


CASAS = _casas_laterais()


def luz_janela(t):
    """A janela da casa 7: apagada, pisca ao acender (lâmpada velha) e fica acesa com tremida leve."""
    if t < T_LUZ:
        return 0.0
    u = t - T_LUZ
    if u < 0.3:
        return 1.0 if int(u * 30) % 3 != 1 else 0.15
    return 0.9 + 0.1 * math.sin(t * 31) * math.sin(t * 7)


def _janela_lateral(c, cam, xf, zc, y0, y1, acesa, brilhos, luzes):
    pts = [(xf, y0, zc - 0.55), (xf, y0, zc + 0.55), (xf, y1, zc + 0.55), (xf, y1, zc - 0.55)]
    if acesa:
        def b(cc, pts=pts):
            P.quad(cc, cam, pts, cheio((255, 196, 120), 230))
        brilhos.append(b)
        x, y = cam.p(xf, (y0 + y1) / 2, zc)
        luzes.append((x, y, 2.6 * cam.escala(zc), 0.55))
    else:
        P.quad(c, cam, pts, cheio((20, 22, 30)))
    P.quad(c, cam, pts, traco((40, 36, 40), max(1.0, 0.06 * cam.escala(zc))))


def _casa_lateral(c, cam, cs, brilhos, luzes):
    lado = cs["lado"]
    x0, x1 = (5.6, 12.0) if lado > 0 else (-12.0, -5.6)
    xf = x0 if lado > 0 else x1
    escuro = mix(cs["cor"], (0, 0, 0), 0.5)
    P.caixa(c, cam, x0, x1, 0.0, cs["h"], cs["z0"], cs["z1"], cheio(escuro),
            degrade(cam.p(xf, 0, cs["z0"]), cam.p(xf, 0, cs["z1"]), [cs["cor"], mix(cs["cor"], (0, 0, 0), 0.35)]))
    P.quad(c, cam, [(xf, cs["h"], cs["z0"]), (xf, cs["h"], cs["z1"]), (xf, cs["h"] + 0.25, cs["z1"]),
                    (xf, cs["h"] + 0.25, cs["z0"])], cheio(mix(cs["cor"], (0, 0, 0), 0.65)))   # platibanda
    for zc, acesa in cs["janelas"]:
        _janela_lateral(c, cam, xf, zc, 1.0, 2.1, acesa, brilhos, luzes)
        if cs["h"] > 4:
            _janela_lateral(c, cam, xf, zc, 3.4, 4.5, acesa and zc % 2 > 1, brilhos, luzes)


def _muro_lateral(c, cam, cs):
    lado = cs["lado"]
    xm = 5.0 * lado
    alto = 1.3
    P.quad(c, cam, [(xm, 0.12, cs["z0"]), (xm, 0.12, cs["z1"]), (xm, alto, cs["z1"]), (xm, alto, cs["z0"])],
           degrade(cam.p(xm, 0, cs["z0"]), cam.p(xm, 0, cs["z1"]), [(92, 88, 86), (60, 58, 58)]))
    P.quad(c, cam, [(xm, alto, cs["z0"]), (xm, alto, cs["z1"]), (xm + 0.18 * lado, alto, cs["z1"]),
                    (xm + 0.18 * lado, alto, cs["z0"])], cheio((120, 116, 112)))


def _rect_janela(cam):
    x0, x1, y0, y1 = JANELA
    z = CASA7["z0"] - 0.01
    a, b = cam.p(x0, y1, z), cam.p(x1, y0, z)
    return skia.Rect.MakeLTRB(a[0], a[1], b[0], b[1])


def _silhueta(c, r, t):
    """Alguém na janela, contra a luz: cabeça, ombros e (depois do "acenou") o braço acenando."""
    w, h = r.width(), r.height()
    cx = r.centerX() + w * 0.06
    c.save()
    c.clipRect(r)
    sombra = cheio((10, 7, 10), 245, blur=max(0.5, w * 0.012))
    corpo = skia.Path()
    corpo.moveTo(cx - w * 0.36, r.bottom())
    corpo.cubicTo(cx - w * 0.34, r.top() + h * 0.70, cx - w * 0.2, r.top() + h * 0.62, cx, r.top() + h * 0.62)
    corpo.cubicTo(cx + w * 0.2, r.top() + h * 0.62, cx + w * 0.34, r.top() + h * 0.70, cx + w * 0.36, r.bottom())
    corpo.close()
    c.drawPath(corpo, sombra)
    c.drawOval(skia.Rect.MakeXYWH(cx - w * 0.15, r.top() + h * 0.26, w * 0.30, h * 0.38), sombra)
    if t >= T_ACENO - 0.35:
        ang = -150 + 28 * math.sin((t - T_ACENO) * 9)
        ox, oy = cx + w * 0.26, r.top() + h * 0.70
        L = h * 0.42
        ex, ey = ox + L * math.cos(math.radians(ang + 90)), oy - L * abs(math.sin(math.radians(ang + 90)))
        c.drawLine(ox, oy, ex, ey, traco((10, 7, 10), w * 0.11, 245))
        c.drawCircle(ex, ey, w * 0.075, sombra)
    c.restore()


def _casa7(c, cam, t, brilhos, luzes):
    k = CASA7
    cor = (78, 90, 82)
    P.caixa(c, cam, k["x0"], k["x1"], 0.0, k["h"], k["z0"], k["z1"],
            degrade(cam.p(0, k["h"], k["z0"]), cam.p(0, 0, k["z0"]), [mix(cor, (0, 0, 0), 0.2), mix(cor, (0, 0, 0), 0.5)]),
            cheio(mix(cor, (0, 0, 0), 0.6)))
    P.quad(c, cam, [(k["x0"] - 0.3, k["h"], k["z0"] - 0.05), (0.0, k["h"] + 1.9, k["z0"] - 0.05),
                    (k["x1"] + 0.3, k["h"], k["z0"] - 0.05)], cheio((70, 40, 36)))                       # empena
    zf = k["z0"] - 0.02
    P.quad(c, cam, [(0.6, 0, zf), (1.7, 0, zf), (1.7, 2.2, zf), (0.6, 2.2, zf)], cheio((48, 34, 28)))   # porta
    for x0, x1, y0, y1 in ((1.0, 2.3, 3.7, 5.0), (-2.6, -1.0, 1.0, 2.1), (2.4, 3.6, 1.0, 2.1)):          # janelas mortas
        P.quad(c, cam, [(x0, y0, zf), (x1, y0, zf), (x1, y1, zf), (x0, y1, zf)], cheio((16, 18, 24)))
        for yy in (y0 + (y1 - y0) * 0.35, y0 + (y1 - y0) * 0.7):                                       # tábuas
            P.quad(c, cam, [(x0 - 0.05, yy - 0.08, zf - 0.01), (x1 + 0.05, yy + 0.04, zf - 0.01),
                            (x1 + 0.05, yy + 0.16, zf - 0.01), (x0 - 0.05, yy + 0.04, zf - 0.01)], cheio((84, 64, 48)))
    # placa com o número
    px, py = cam.p(2.0, 1.9, zf - 0.01)
    s = cam.escala(zf)
    c.drawRoundRect(skia.Rect.MakeXYWH(px, py, 0.42 * s, 0.42 * s), 0.05 * s, 0.05 * s, cheio((200, 196, 180)))
    if s > 30:
        texto_c(c, "7", px + 0.21 * s, py + 0.36 * s, fonte("titulo", max(8, int(0.36 * s))), (30, 30, 40))
    r = _rect_janela(cam)
    lj = luz_janela(t)
    if lj <= 0.01:
        c.drawRect(r, cheio((14, 16, 22)))
        c.drawRect(r, traco((60, 56, 50), max(1.0, 0.05 * s)))
        return

    def acesa(cc):
        cc.drawRect(r, degrade((0, r.top()), (0, r.bottom()), [(LUZ_JANELA, 255 * lj), (mix(LUZ_JANELA, (90, 60, 20), 0.4), 255 * lj)]))
        _silhueta(cc, r, t)
        cc.drawRect(r, traco((60, 56, 50), max(1.0, 0.05 * s)))
        cc.drawRect(skia.Rect.MakeLTRB(r.left() - r.width(), r.top() - r.height(), r.right() + r.width(), r.bottom() + r.height()),
                    cheio(LUZ_JANELA, 40 * lj, blur=r.width() * 0.5))
    brilhos.append(acesa)
    luzes.append((r.centerX(), r.centerY(), 3.5 * s, 0.8 * lj))


def _portao7(c, cam):
    z = CASA7["z0"] - 1.0
    s = cam.escala(z)
    for x0, x1 in ((-4.5, 0.2), (2.1, 4.5)):
        P.quad(c, cam, [(x0, 0, z), (x1, 0, z), (x1, 1.4, z), (x0, 1.4, z)], cheio((70, 66, 64)))
    x = 0.25
    while x < 2.1:
        P.linha(c, cam, (x, 0, z), (x, 1.8, z), traco((30, 30, 34), max(1.0, 0.05 * s)))
        x += 0.18
    P.linha(c, cam, (0.2, 1.8, z), (2.1, 1.8, z), traco((30, 30, 34), max(1.0, 0.07 * s)))


def _poste(c, cam, t, brilhos, luzes):
    x, z = POSTE
    s = cam.escala(z)
    P.linha(c, cam, (x, 0, z), (x, 5.6, z), traco((70, 70, 76), max(2.0, 0.18 * s)))
    lamp = cam.p(x - 1.2, 5.4, z)
    c.drawLine(*cam.p(x, 5.6, z), *lamp, traco((60, 60, 66), max(1.5, 0.1 * s)))

    def b(cc):
        C.lampada(cc, lamp[0], lamp[1], max(2.0, 0.16 * s), LUZ_POSTE, 1.0, t)
    brilhos.append(b)
    luzes.append((lamp[0], lamp[1] + 1.5 * s, 7.0 * s, 0.95))


def mundo(c, cam, t, nivel=0.74, lua=True):
    """A rua inteira, do fundo para a frente; luz da cena aplicada no fim. Devolve a posição da luz do poste."""
    P.ceu_noturno(c, cam, t=t)
    c.drawCircle(W * 0.18, cam.hz * 0.22, 46, cheio((236, 232, 214)))                                   # lua
    c.drawCircle(W * 0.18, cam.hz * 0.22, 140, cheio((200, 200, 230), 40, blur=60))
    c.drawRect(skia.Rect.MakeLTRB(-400, cam.hz, W + 400, H + 400), cheio((16, 16, 20)))
    zp, zf = cam.z + 0.4, CASA7["z0"]
    P.quad(c, cam, [(-3.2, 0, zp), (3.2, 0, zp), (3.2, 0, zf), (-3.2, 0, zf)],
           degrade(cam.p(0, 0, zp), cam.p(0, 0, zf), [(54, 52, 56), (30, 30, 34)]))                   # asfalto
    for lado in (-1, 1):
        P.quad(c, cam, [(lado * 3.2, 0.12, zp), (lado * 5.0, 0.12, zp), (lado * 5.0, 0.12, zf), (lado * 3.2, 0.12, zf)],
               cheio((84, 82, 80)))                                                                   # calçada
        P.quad(c, cam, [(lado * 3.2, 0, zp), (lado * 3.2, 0.12, zp), (lado * 3.2, 0.12, zf), (lado * 3.2, 0, zf)],
               cheio((128, 124, 118)))                                                                # meio-fio
        z = zp
        while z < zf:                                                                                 # faixa
            P.quad(c, cam, [(-0.06, 0.001, z), (0.06, 0.001, z), (0.06, 0.001, z + 1.2), (-0.06, 0.001, z + 1.2)],
                   cheio((150, 140, 100), 120))
            z += 3.0
    brilhos, luzes = [], [(W * 0.18, cam.hz * 0.22, 900, 0.3)] if lua else []
    fila = P.Cena()
    for cs in CASAS:
        if cs["z1"] > cam.z + 0.5:
            fila.poe(cs["z1"], lambda cc, cs=cs: _casa_lateral(cc, cam, cs, brilhos, luzes), desempate=1)
            fila.poe(cs["z1"], lambda cc, cs=cs: _muro_lateral(cc, cam, cs), desempate=0)
    fila.poe(CASA7["z0"], lambda cc: _casa7(cc, cam, t, brilhos, luzes))
    fila.poe(CASA7["z0"] - 1.0, lambda cc: _portao7(cc, cam))
    if POSTE[1] > cam.z + 0.8:
        fila.poe(POSTE[1], lambda cc: _poste(cc, cam, t, brilhos, luzes))
    fila.desenha(c)
    C.escuro(c, luzes, nivel=nivel)
    for b in brilhos:
        b(c)


# ---------------------------------------------------------------- personagem

def pose_lola(t, olhar=(0.0, 0.0), medo=False, extra=None):
    pose = {"piscar": piscar(t, PISCADAS), "tronco": respira(t), "visema": "M", "olhar": olhar,
            "cabeca": {"rot": 2 * math.sin(t * 0.9)}}
    if medo:
        pose.update(MEDO)
    if extra:
        pose.update(extra)
    return pose


def iluminar(c, b, x, pe, alt, pose):
    C.boneco_iluminado(c, b, x, pe, alt, pose, chave=(LUZ_POSTE, (1.0, -0.6)), aro=((150, 170, 255), (-1.0, -0.4), 0.75),
                       exposicao=0.85, projeta=True)


# ---------------------------------------------------------------- linha do tempo

def cam_janela(F):
    x0, x1, y0, y1 = JANELA
    return P.Cam3D(x=(x0 + x1) / 2, h=(y0 + y1) / 2, F=F, hz=820, z=0.0)


def cena(c, t):
    n0, n1, n2 = EV["n0"], EV["n1"], EV["n2"]
    if t < n1["t0"]:                                     # gancho (quadro 0): a janela acesa colada na câmera, já com voz
        mundo(c, cam_janela(9000 - 700 * min(t, 2.0)), t, nivel=0.9, lua=False)
    elif t < n2["t0"]:                                   # recua: a rua, a casa 7 no fim, a Lola na frente
        u = t - n1["t0"]
        cam = P.Cam3D(x=0.3, h=1.5, F=1000 + 25 * u, hz=760, z=0.12 * u)
        mundo(c, cam, t)
        P.boneco_3d(c, cam, LOLA, 1.1, 4.2, pose_lola(t, (-0.3, -0.2)), iluminar=iluminar)
    elif t < T_ACENO - 0.35:                             # close: a Lola olha para a casa, o fundo desfocado
        u = t - n2["t0"]
        with C.foco(c, 9):
            mundo(c, P.Cam3D(x=0.0, h=1.6, F=1500, hz=900, z=2.0), t)
        olhar = (-0.6, -0.5) if u < 1.0 else (-0.7, -0.6)
        iluminar(c, LOLA, 560 - 6 * u, 1900 + 8 * u, 1250 + 14 * u,
                 pose_lola(t, olhar, medo=u >= 1.2, extra={"corpo_rot": -2}))
    elif t < T_VOTO:                                     # a janela: alguém acena
        u = t - (T_ACENO - 0.35)
        mundo(c, cam_janela(8400 + 800 * u), t, nivel=0.9, lua=False)
    else:                                                # a escolha: a Lola pequena na rua, a janela acesa
        u = t - T_VOTO
        cam = P.Cam3D(x=0.6, h=3.2, F=1100 - 10 * u, hz=640, z=-2.0)
        mundo(c, cam, t)
        P.boneco_3d(c, cam, LOLA, 1.0, 7.0, pose_lola(t, (-0.4, -0.5), medo=True), iluminar=iluminar)


def legendas(c, t):
    chaves = EP.get("chaves", {})
    for b in range(EP["bloco_voto"]):                    # sem legenda na tela de voto (o texto já está no cartão)
        e = EV[f"n{b}"]
        if e["t0"] <= t < e["t1"] + 0.35:
            legenda(c, t, palavras_do_evento(e), chaves.get(str(b), []))


def quadro(c, t):
    C.chicote(c, t, CORTES, lambda cc: cena(cc, t))
    C.correcao(c, forca=0.12)
    C.vinheta(c, 0.85)
    C.grao(c, t, 0.1, FPS)
    fim_gancho = EV["n1"]["t0"]
    if t < fim_gancho:  # texto grande já no quadro 0 (sem fade de entrada: o quadro 0 vira a miniatura)
        a = 255 * min(1.0, (fim_gancho - t) / 0.3)
        y = 600
        for i, linha in enumerate(EP.get("gancho", [])):
            f = caber("titulo", linha, 132, LARG_SEGURA, minimo=60)
            texto_c(c, linha, CX_SEGURO, y, f, (255, 255, 255) if i == 0 else T.OPCOES[0], a, contorno=12)
            y += f.getSize() * 1.05
        texto_c(c, "USE FONE", CX_SEGURO, 1150, fonte("mono", 30), (220, 220, 235), 0.8 * a)
    legendas(c, t)
    T.abertura(c, t, fim_gancho - 0.2, SERIE, f"Parte {PARTE} · {TITULO}", dur=2.8)
    if t < T_VOTO:
        T.selo(c, f"{SERIE} · PARTE {PARTE} · FICÇÃO")
    else:
        T.cartao_voto(c, t, T_VOTO, EP["pergunta"], [tuple(o) for o in EP["opcoes"]], duracao=TOTAL - T_VOTO,
                      parte_seguinte=PARTE + 1)


def main():
    nome = f"{slug(SERIE)}_p{PARTE}"
    saida = Path(ARGS.saida) if ARGS.saida else TRAB / f"{nome}.mp4"
    marcos = [0.0, 1.0, EV["n1"]["t0"] + 0.8, EV["n1"]["t0"] + 2.5, EV["n2"]["t0"] + 0.8, EV["n2"]["t0"] + 2.0,
              T_ACENO + 0.3, T_VOTO + 1.2, TOTAL - 0.4]
    renderizar(quadro, TOTAL, saida, audio=TRAB / "audio" / "mix_norm.wav", cpu=ARGS.cpu, marcos=marcos,
               pasta_quadros=TRAB / "quadros", so_marcos=ARGS.stills)


if __name__ == "__main__":
    main()
