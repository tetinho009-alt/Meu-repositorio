# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Elenco do estilo e o que ele faz em cena: os três personagens sorteados com o estilo (protagonista, adulto e
idoso, ver estilo.json), objetos de mão (vela,
terço), poses de medo de duas pessoas (abraçadas, tapando a boca da outra, encostadas na porta) e os ciclos de
animação em "stop motion" (andar, correr, escorregar, se jogar e cair na porta).

Stop motion: a pose troca 12 vezes por segundo (`stop(t)`), cada peça de papel é recolocada com um tremidinho a cada
pose, e a câmera desliza a 60 qps.

    from estilo_desenhado import elenco as E
    prot = E.pessoa("protagonista")
    pose = E.andar(E.stop(t), vel=1.0)
    prot.desenhar(c, x, y, altura, pose)
"""
import math

import numpy as np
import skia

from . import tinta as T
from .personagem import CX, MEMBRO, PADRAO, BonecoGotico, BonecoPapel, _punho, pose_medo  # noqa: F401

QPS_STOP = 12.0

# Rostos diferentes no mesmo molde: `rosto` (oval/redondo/gota), `nariz` (bolinha/meia_lua/triangulo),
# `labios` (cheia/fina/murcha) e `bochecha`; ver personagem._cabeca_pts, _nariz_e_marcas e _boca.
def _elenco():
    """O elenco do estilo do canal (sorteado junto com o estilo): nome -> configuração do molde."""
    return {p["nome"]: p["molde"] for p in T.ESTILO["elenco"]}


ELENCO = _elenco()
PAPEIS = {p["papel"]: p["nome"] for p in T.ESTILO["elenco"]}   # protagonista, adulto, idoso -> nome


def pessoa(nome, vetor=False):
    """Boneco de um personagem do elenco do estilo, pelo nome ou pelo papel ("protagonista", "adulto", "idoso").
    Para um personagem seu, use BonecoPapel("<pasta em personagens/>") ou passe o seu dict em `cfg`."""
    nome = PAPEIS.get(nome, nome)
    return BonecoPapel(nome, cfg={**PADRAO, **ELENCO[nome]}, vetor=vetor)


def stop(t, qps=QPS_STOP):
    """Tempo em degraus de stop motion (12 poses por segundo)."""
    return math.floor(t * qps) / qps


# ---------------------------------------------------------------- objetos de mão

def vela_na_mao(c, b, lado, x, y, altura, pose, t, acesa=1.0, deita=0.0):
    """Vela num pires, presa na palma (pelo `mao` do rig); a chama dança e deita na direção `deita` (-1..1)."""
    (px, py), ang = b.mao(lado, x, y, altura, pose)
    s = altura / 1000.0
    c.save()
    c.translate(px, py - 6 * s)
    k = s * 1.0
    pires = T.elipse(0, 8 * k, 34 * k, 9 * k, 24)
    sx, sy = T.sombra_px(altura * 0.5)
    pires_p = T.caminho(T.tesoura(pires, 31))
    if T.com_sombra():
        c.drawPath(T.deslocado(pires_p, sx, sy), skia.Paint(AntiAlias=True, Color=T.cor_sombra()))
    c.drawPath(pires_p, T.tinta_paint(T.mistura(T.APOIO, (96, 86, 72), 0.4)))
    c.drawPath(pires_p, T.borda_paint(T.APOIO, 1.2 * k))
    corpo = np.array([(-9 * k, 6 * k), (9 * k, 6 * k), (8 * k, -64 * k), (-8 * k, -64 * k)])
    cera = T.mistura(T.PAPEL, (255, 255, 255), 0.5)
    corpo_p = T.caminho(T.tesoura(T.quina(corpo, True, 6), 32))
    if T.com_sombra():
        c.drawPath(T.deslocado(corpo_p, sx, sy), skia.Paint(AntiAlias=True, Color=T.cor_sombra()))
    c.drawPath(corpo_p, T.tinta_paint(cera))
    c.drawPath(corpo_p, T.borda_paint(cera, 1.2 * k))
    if acesa > 0:
        osc = math.sin(t * 17) * 0.15 + math.sin(t * 31) * 0.08
        dx = (deita + osc) * 22 * k
        chama = T.catmull([(0, -66 * k), (6 * k, -80 * k), (dx * 0.6 + 3 * k, -98 * k), (dx, -118 * k), (dx * 0.6 - 3 * k, -98 * k),
                           (-6 * k, -80 * k)], True, 6)
        c.drawCircle(dx * 0.4, -90 * k, 160 * k * acesa, skia.Paint(AntiAlias=True, BlendMode=skia.BlendMode.kScreen,
                                                                    Shader=skia.GradientShader.MakeRadial(skia.Point(dx * 0.4, -90 * k), 160 * k,
                                                                                                          [T.cor_skia((230, 170, 90), 120 * acesa),
                                                                                                           T.cor_skia((200, 120, 60), 0)])))
        c.drawPath(T.caminho(chama), T.tinta_paint((246, 214, 140), 255 * acesa))
        c.drawPath(T.caminho(T.elipse(dx * 0.3, -86 * k, 4 * k, 9 * k, 12)), T.tinta_paint((255, 250, 230), 230 * acesa))
    c.restore()


def terco(c, b, lado, x, y, altura, pose, t):
    """Terço de contas pendurado da mão, balançando, com a cruz embaixo."""
    (px, py), ang = b.mao(lado, x, y, altura, pose)
    s = altura / 1000.0
    bal = 0.18 * math.sin(t * 2.3)
    contas = []
    for k in range(18):
        u = k / 17
        contas.append((px + (math.sin(bal) * 120 * u + 26 * math.sin(math.pi * u)) * s, py + (20 + 130 * u - 30 * math.sin(math.pi * u)) * s))
    for k, (cx, cy) in enumerate(contas):
        c.drawCircle(cx, cy, 4.2 * s, T.tinta_paint((70, 58, 50)))
        c.drawCircle(cx + 1.5 * s, cy + 1.5 * s, 4.2 * s, skia.Paint(AntiAlias=True, Color=T.cor_sombra()))
        c.drawCircle(cx, cy, 4.2 * s, T.tinta_paint((70, 58, 50)))
    cx, cy = contas[-1]
    cruz = skia.Path()
    cruz.addRect(skia.Rect.MakeXYWH(cx - 2.5 * s, cy, 5 * s, 30 * s))
    cruz.addRect(skia.Rect.MakeXYWH(cx - 9 * s, cy + 8 * s, 18 * s, 5 * s))
    c.drawPath(cruz, T.tinta_paint((150, 130, 100)))
    c.drawPath(cruz, T.borda_paint((150, 130, 100), 1.0 * s))


# ---------------------------------------------------------------- poses de cena

def pose_encostada_porta(t=0.0, medo=1.0, olha=-0.8, **extra):
    """De costas na porta (de frente pra câmera): mãos espalmadas na madeira dos lados, ombro colado, queixo
    levantado e o rosto virando pro lado."""
    p = pose_medo(medo, t=t, ik={"mao_e": (CX - 150, 640, 160), "mao_d": (CX + 150, 650, 20), "pe_e": (CX - 40, 962), "pe_d": (CX + 46, 966)},
                  mao_e={"dedos": 0.05}, mao_d={"dedos": 0.05}, cabeca={"rot": 10 * olha, "dy": 4}, olhar=(olha, -0.1),
                  tronco={"sy": 0.99})
    p.update(extra)
    return p


def pose_sentada_cama(t=0.0, medo=1.0, **extra):
    """Sentada na cama, acordando num susto: o quadril baixa até o colchão, as pernas somem debaixo da coberta,
    as mãos apoiadas no colchão atrás e o tronco pra trás."""
    p = pose_medo(medo, t=t, repouso=0.0, pulo=-250, perna_e={"some": True}, perna_d={"some": True}, canela_e={"some": True},
                  canela_d={"some": True}, tenis_e={"some": True}, tenis_d={"some": True}, quadril={"some": True}, saia={"some": True},
                  ik={"mao_e": (CX - 120, 700, 120), "mao_d": (CX + 120, 700, 60)}, tronco={"rot": -2, "sy": 0.97},
                  cabeca={"dy": 6, "rot": 4})
    p.update(extra)
    return p


def abraco(t, b1, x1, b2, x2, y, altura, medo=1.0):
    """Duas pessoas abraçadas de medo (lado a lado, de frente): cada uma passa o braço de dentro pelas costas da
    outra (a mão aparece no ombro de lá) e a outra mão agarra a roupa da outra no peito. Devolve (pose1, pose2)."""
    p1 = pose_medo(medo, t=t, olhar=(0.6, -0.1))
    p2 = pose_medo(medo, t=t + 0.37, olhar=(-0.6, -0.1))
    d = x2 - x1
    # alvo na tela -> molde de cada um
    om2 = (x2 - d * 0.08, y - altura * 0.56)       # ombro de fora do 2 (visto do 1)
    om1 = (x1 + d * 0.08, y - altura * 0.56)
    pe2 = (x2 - d * 0.22, y - altura * 0.47)        # peito do 2
    pe1 = (x1 + d * 0.22, y - altura * 0.47)
    m = b1.no_molde(x1, y, altura, p1, om2)
    n = b1.no_molde(x1, y, altura, p1, pe2)
    p1["ik"] = {"mao_d": (m[0], m[1], 10), "mao_e": (n[0], n[1], 20)}
    p1["mao_d"] = {"dedos": 0.6}
    p1["mao_e"] = {"dedos": 0.9}
    p1["cabeca"] = {"rot": 9, "dy": 10}
    m = b2.no_molde(x2, y, altura, p2, om1)
    n = b2.no_molde(x2, y, altura, p2, pe1)
    p2["ik"] = {"mao_e": (m[0], m[1], 170), "mao_d": (n[0], n[1], 160)}
    p2["mao_e"] = {"dedos": 0.6}
    p2["mao_d"] = {"dedos": 0.9}
    p2["cabeca"] = {"rot": -9, "dy": 10}
    p2["na_frente"] = ["braco_d", "antebraco_d", "mao_d"]
    return p1, p2


def tapa_boca(t, b, x, y, altura, outro, xo, yo, alt_o, pose_outro, lado="d"):
    """`b` tapa a boca do `outro` com a mão (`lado`); a outra mão segura o ombro dele. Devolve a pose de `b`."""
    alvo = outro.boca_tela(xo, yo, alt_o, pose_outro)
    p = pose_medo(1.0, t=t, olhar=(0.8 if xo > x else -0.8, 0.0))
    m = b.no_molde(x, y, altura, p, (alvo[0], alvo[1] + 0.03 * alt_o))
    o = "e" if lado == "d" else "d"
    om = b.no_molde(x, y, altura, p, (xo + (x - xo) * 0.2, yo - alt_o * 0.58))
    p["ik"] = {f"mao_{lado}": (m[0], m[1], -90), f"mao_{o}": (om[0], om[1], 0 if xo > x else 180)}
    p[f"mao_{lado}"] = {"dedos": 0.2}
    p[f"mao_{o}"] = {"dedos": 0.8}
    p["na_frente"] = [f"braco_{lado}", f"antebraco_{lado}", f"mao_{lado}"]
    return p


# ---------------------------------------------------------------- ciclos (stop motion)

# Distância da mão ao meio do corpo (molde) na caminhada: do lado de fora da coxa, que engrossa com o membro do estilo
MAO_FORA = max(84.0, 25 + 19 * MEMBRO + 26)


def andar(t, vel=1.0, medo=0.6, passo=0.62):
    """Andar (de frente pra câmera ou de costas, com pose["costas"]): pés alternando por IK, quadril e ombro
    contrários, braço balançando, sobe e desce. `t` já em degraus (stop)."""
    f = 2 * math.pi * t / (passo / vel)
    s = math.sin(f)
    p = pose_medo(medo, t=t, repouso=0.0)
    lev_e, lev_d = max(0.0, s), max(0.0, -s)
    ik = {"pe_e": (CX - 30, 962 - 46 * lev_e + 10 * math.cos(f)), "pe_d": (CX + 30, 962 - 46 * lev_d - 10 * math.cos(f))}
    # Braço solto do lado do corpo, a mão do lado de fora da coxa, balançando ao contrário da perna do mesmo lado. De
    # frente ou de costas o balanço é na profundidade: a mão sobe um pouco (escorço) e chega um tico pro meio quando vem
    # pra frente. Girar os dois braços pro mesmo lado com o antebraço dobrado pra dentro junta as mãos nas costas.
    for lado, l, v in (("e", -1, -s), ("d", 1, s)):
        frente, tras = max(0.0, v), max(0.0, -v)
        ik[f"mao_{lado}"] = (CX + l * (MAO_FORA - 6 * frente + 3 * tras), 724 - 12 * frente - 7 * tras - 12 * medo, 90 + l * 4)
    p["ik"] = ik
    p["_ciclo"] = "andar"   # a trava de mãos (personagem.QA_MAOS) confere todo quadro de caminhada
    p["quadril"] = {"rot": 3 * s}
    p["tronco"] = {"rot": -2 * s}
    p["cabeca"] = {"rot": 1.5 * s}
    p["pulo"] = 10 * abs(math.cos(f))
    return p


def correr(t, vel=1.0, medo=1.0):
    """Correr: passada curta e rápida, joelho alto, braço dobrado batendo forte, corpo pra frente, quica."""
    f = 2 * math.pi * t / (0.34 / vel)
    s = math.sin(f)
    p = pose_medo(medo, t=t, repouso=0.0)
    lev_e, lev_d = max(0.0, s), max(0.0, -s)
    # Perna que sobe: de frente, o joelho vem PRA CÂMERA. Encurtar a perna (escorço) sobe o pé sem jogar o joelho pro
    # lado; com IK o joelho dobrava pra fora e a canela saía pela lateral da saia (a "aba cor de pele").
    # braços batendo junto do corpo (cotovelo dobrado, mão subindo até o peito e descendo até o quadril)
    # (a mão fica do lado de fora do tronco: no corpo cheio do estilo, 78 do meio já caía dentro das costas)
    fora = max(78.0, MAO_FORA + 6)   # +6: o balanço lateral de 10 leva a mão pro meio no pico
    ik = {"mao_e": (CX - fora + 10 * s, 640 - 150 * max(0.0, -s) + 30 * max(0.0, s), -70),
          "mao_d": (CX + fora + 10 * s, 640 - 150 * max(0.0, s) + 30 * max(0.0, -s), -110)}
    for lado, lev in (("e", lev_e), ("d", lev_d)):
        if lev > 0.04:
            # escorço coerente: a coxa que sobe aponta uns 35 graus pra câmera (encurtar mais faz a perna "encolher")
            p[f"perna_{lado}"] = {"rot": (4 if lado == "e" else -4) * lev, "sy": 1 - 0.18 * lev}
            p[f"canela_{lado}"] = {"rot": (-6 if lado == "e" else 6) * lev}
        else:
            ik[f"pe_{lado}"] = (CX + (-26 if lado == "e" else 26), 962)
    p["ik"] = ik
    p["_ciclo"] = "correr"
    p["quadril"] = {"rot": 5 * s}
    p["tronco"] = {"rot": -4 * s, "sy": 0.98}
    p["cabeca"] = {"rot": 3 * s, "dy": 8}
    p["pulo"] = 40 * abs(math.cos(f))
    p["corpo_rot"] = 2 * s
    return p


def escorregar(u, t=0.0):
    """Escorregar na terra (u 0..1): um pé corre pra frente, os braços jogam pra cima, o corpo tomba e cai sentado."""
    u = max(0.0, min(1.0, u))
    k = u * u * (3 - 2 * u)
    p = pose_medo(1.0, t=t, repouso=0.0)
    p["ik"] = {"pe_d": (CX + 40 + 90 * k, 962 - 20 * math.sin(math.pi * k)), "pe_e": (CX - 30, 962),
               "mao_e": (CX - 170, 520 - 180 * math.sin(math.pi * min(1, u * 1.4)), -120), "mao_d": (CX + 170, 520 - 160 * math.sin(math.pi * min(1, u * 1.4)), -60)}
    p["corpo_rot"] = -18 * k
    p["pulo"] = -240 * max(0.0, (u - 0.55) / 0.45) ** 1.5
    p["cabeca"] = {"rot": 12 * k, "dy": 10 * k}
    p["visema"] = "O" if u > 0.2 else "R"
    if u > 0.85:
        for o in ("perna_e", "perna_d"):
            p[o] = {"sy": 0.5}
        p["canela_e"] = {"sy": 0.5}
        p["canela_d"] = {"sy": 0.5}
    return p


def se_jogar_na_porta(u, t=0.0, lado=1):
    """Se jogar e cair encostada na porta (u 0..1): impulso de lado, o corpo voa inclinado, bate (achata) e
    escorrega até o chão encostada. O deslocamento x na tela é do chamador (`deslocamento_jogar`)."""
    u = max(0.0, min(1.0, u))
    p = pose_medo(1.0, t=t, repouso=0.0)
    if u < 0.45:            # impulso e voo
        k = u / 0.45
        p["corpo_rot"] = lado * 28 * math.sin(math.pi * 0.5 * k)
        p["pulo"] = 60 * math.sin(math.pi * k)
        p["ik"] = {"mao_e": (CX - 120 * lado + 200 * lado * k, 400, -90), "mao_d": (CX + 180 * lado, 420 - 40 * k, -90 + 60 * lado)}
    elif u < 0.6:           # batida: achata
        p["corpo_rot"] = lado * 8
        p["estica"] = 0.92
        p["ik"] = {"mao_e": (CX - 140, 600, 160), "mao_d": (CX + 140, 600, 20)}
    else:                   # escorrega até sentar
        k = (u - 0.6) / 0.4
        p["corpo_rot"] = lado * 6 * (1 - k)
        p["pulo"] = -260 * k ** 1.3
        p["ik"] = {"mao_e": (CX - 150, 640 + 60 * k, 160), "mao_d": (CX + 150, 640 + 60 * k, 20)}
        if k > 0.6:
            for o in ("perna_e", "perna_d", "canela_e", "canela_d"):
                p[o] = {"sy": 0.55}
    p["visema"] = "O"
    return p


def deslocamento_jogar(u, dist):
    """Quanto o corpo andou de lado na tela no `se_jogar_na_porta` (ease-out até bater)."""
    k = max(0.0, min(1.0, u / 0.5))
    return dist * (1 - (1 - k) ** 2)
