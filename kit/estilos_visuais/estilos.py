# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Estilos visuais do kit: vídeos verticais de 10 s (1080x1920, 30 fps), tudo desenhado por código, sem voz e sem
som. Guia para a IA: README.md desta pasta. Uso (a partir de kit/):
    python estilos_visuais/estilos.py <estilo>             grava trabalho/estilos/<estilo>.mp4 e o still do meio
    python estilos_visuais/estilos.py <estilo> --quadro 5  só o quadro do segundo 5 (conferência rápida, antes do vídeo)
    python estilos_visuais/estilos.py --lista              mostra os estilos
"""
import math
import sys
from pathlib import Path

import numpy as np
import skia

import motor as M
from motor import W, H

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
from config import pasta  # noqa: E402  (também confere a licença do kit)

SAIDA = pasta("trabalho") / "estilos"
RNG = np.random.default_rng


# ================================================================ 1) LOW POLY

def low_poly():
    rng = RNG(11)
    cores = {"pele": (236, 184, 146), "camisa": (242, 160, 70), "calca": (70, 92, 150), "sapato": (60, 50, 50),
             "cabelo": (90, 55, 40)}

    def altura(x, z):
        caminho = math.exp(-(x * x) / 6.0)
        h = 0.9 * math.sin(x * 0.35 + 1.3) * math.cos(z * 0.21) + 0.5 * math.sin(z * 0.5 + x * 0.17)
        return h * (1 - 0.9 * caminho) - 0.05

    def cor_t(x, y, z):
        if abs(x) < 1.1:
            return (232, 206, 150)
        return (110 + 40 * y, 182 + 30 * y, 104) if y < 0.9 else (150, 200, 120)

    chao = M.terreno(56, 38, altura, cor_t, centro=(0, 14))
    objs = [chao]
    for _ in range(95):
        x = rng.uniform(2.2, 20) * rng.choice([-1, 1])
        z = rng.uniform(-10, 40)
        y = altura(x, z)
        if rng.random() < 0.7:
            h = rng.uniform(1.6, 3.2)
            objs.append(M.cilindro(0.12, h * 0.4, 5, (120, 82, 56), t=(x, y, z)))
            tom = rng.choice([(64, 150, 92), (52, 132, 98), (92, 170, 88)])
            if rng.random() < 0.5:
                objs.append(M.cilindro(0.9 * h / 2.6, h * 0.8, 6, tom, r_topo=0, t=(x, y + h * 0.3, z)))
            else:
                objs.append(M.icosfera(0.75 * h / 2.4, tom, nivel=0, t=(x, y + h * 0.62, z), ruido=0.15,
                                       semente=int(rng.integers(999))))
        else:
            objs.append(M.icosfera(rng.uniform(0.3, 0.7), (150, 150, 162), nivel=0, t=(x, y + 0.1, z),
                                   achatar=(1.3, 0.7, 1.0), ruido=0.25, semente=int(rng.integers(999))))
    for k in range(7):
        objs.append(M.icosfera(1.4, (255, 255, 255), nivel=0, t=(rng.uniform(-25, 25), rng.uniform(11, 15),
                                                                  rng.uniform(15, 50)), achatar=(1.8, 0.6, 1.0)))
    cenario = M.juntar(objs)
    cenario.emi[-7 * 20:] = True

    def quadro(i, t):
        s, cv = M.superficie()
        M.gradiente_vertical(cv, W, H, (128, 196, 238), (250, 220, 190), 0, H * 0.62)
        cv.drawCircle(W * 0.78, H * 0.18, 110, M.tinta((255, 236, 170)))
        z = 1.25 * t
        boneco = M.boneco(M.pose_caminhada(t * 2 * math.pi * 1.0), cores, pos=(0, altura(0, z) + 0.05, z))
        a = -1.1 + 1.9 * M.suave(t, 0, 10)
        alvo = np.array([0, 1.05 + altura(0, z), z])
        cam = M.Camera(alvo + [4.6 * math.sin(a), 0.75 + 0.3 * math.sin(t * 0.7), 4.6 * math.cos(a)], alvo, fov=42)
        M.desenhar(cv, M.juntar([cenario, boneco]), cam, nevoa=((236, 222, 214), 10, 42), amb=0.5)
        return M.vinheta(M.pixels(s), 0.25)

    return quadro


# ================================================================ 2) CONSOLE ANTIGO (gráfico de console dos anos 2000)

def console_antigo():
    rng = RNG(5)
    LW, LH = 360, 640
    cores = {"pele": (214, 170, 140), "camisa": (60, 66, 80), "calca": (40, 44, 52), "sapato": (25, 25, 25),
             "cabelo": (28, 24, 22)}
    objs = []
    for z in range(-6, 60, 2):
        objs.append(M.caixa(6, 0.05, 2, (52, 54, 60), t=(0, -0.025, z)))
        objs.append(M.caixa(0.15, 0.06, 0.9, (190, 180, 120), t=(0, 0.01, z)))
        for lado in (-1, 1):
            objs.append(M.caixa(2.2, 0.2, 2, (88, 86, 92), t=(lado * 4.1, 0.1, z)))
    for z in np.arange(-6, 62, 7.0):
        for lado in (-1, 1):
            larg, alt = rng.uniform(5, 7), rng.uniform(5, 13)
            tom = tuple(int(v) for v in rng.integers(55, 110, 3))
            objs.append(M.caixa(4, alt, larg, tom, t=(lado * 7.2, 0, z), base=True))
            for jy in np.arange(1.5, alt - 0.5, 1.7):
                for jz in np.arange(z - larg / 2 + 0.8, z + larg / 2 - 0.5, 1.3):
                    acesa = rng.random() < 0.35
                    objs.append(M.caixa(0.05, 0.8, 0.6, (250, 214, 120) if acesa else (30, 34, 44),
                                        t=(lado * 5.18, jy, jz), emi=acesa))
    for z in np.arange(-4, 60, 9.0):
        for lado in (-1, 1):
            objs.append(M.cilindro(0.06, 3.6, 5, (40, 40, 44), t=(lado * 3.3, 0, z)))
            objs.append(M.caixa(0.5, 0.12, 0.3, (255, 240, 200), t=(lado * 3.05, 3.6, z), emi=True))
    cidade = M.juntar(objs)

    def quadro(i, t):
        s, cv = M.superficie(LW, LH)
        M.gradiente_vertical(cv, LW, LH, (20, 22, 36), (70, 74, 96), 0, LH * 0.55)
        z = 1.1 * t
        boneco = M.boneco(M.pose_caminhada(t * 2 * math.pi * 0.95), cores, pos=(0.6, 0, z))
        alvo = np.array([0.5, 1.3, z + 3])
        cam = M.Camera((1.5 + 0.3 * math.sin(t * 0.5), 2.2, z - 3.4), alvo, fov=55, w=LW, h=LH)
        M.desenhar(cv, M.juntar([cidade, boneco]), cam, nevoa=((72, 76, 98), 4, 26), aa=False, grade=1.0,
                   variacao=0.10, amb=0.38, luz=(-0.3, -0.9, 0.4))
        if t < 3.2:
            a = int(255 * min(1, (3.2 - t) / 0.6))
            M.texto(cv, "CAPÍTULO 1", LW / 2, 90, 26, (235, 230, 210), fonte="Arial", negrito=True,
                    alinhar="centro", a=a)
            M.texto(cv, "A rua de baixo", LW / 2, 116, 15, (200, 196, 180), alinhar="centro", a=a)
        cv.drawRect(skia.Rect(14, LH - 34, 14 + 110, LH - 24), M.tinta((20, 20, 20)))
        cv.drawRect(skia.Rect(16, LH - 32, 16 + 80, LH - 26), M.tinta((90, 200, 110)))
        img = M.pixels(s)
        img = M.dithering(img, 24)
        return M.ampliar(img, 3)

    def texto_sem_aa():
        pass

    return quadro


# ================================================================ 4) STICKMAN

def _corpo2d(quadril, a, esc=1.0):
    """Pontos do boneco de palito de perfil (olhando para +x). Ângulos a partir da vertical para baixo; positivo =
    para a frente. Joelho (>=0) dobra para trás; cotovelo (>=0) dobra para a frente."""
    def d(ang, L):
        return np.array([math.sin(ang), math.cos(ang)]) * L * esc

    def up(ang, L):
        return np.array([math.sin(ang), -math.cos(ang)]) * L * esc

    q = np.asarray(quadril, float)
    pesc = q + up(a.get("tronco", 0.08), 150)
    cab = pesc + up(a.get("tronco", 0.08), 52)
    pts = {"q": q, "pesc": pesc, "cab": cab}
    for lado in ("e", "d"):
        k = q + d(a["coxa_" + lado], 112)
        p = k + d(a["coxa_" + lado] - max(0.0, a["joelho_" + lado]), 108)
        o = pesc + up(a.get("tronco", 0.08), -10)
        c = o + d(a["ombro_" + lado], 82)
        m = c + d(a["ombro_" + lado] + max(0.0, a["cot_" + lado]), 78)
        pts.update({"joelho_" + lado: k, "pe_" + lado: p, "ombro_" + lado: o, "cot_" + lado: c, "mao_" + lado: m})
    return pts


def _pose2d_caminhada(fase, passo=1.0, corrida=False):
    p = M.pose_caminhada(fase, passo * (1.5 if corrida else 1.0))
    a = {"tronco": 0.32 if corrida else 0.08}
    for i, lado in enumerate(("e", "d")):
        a["coxa_" + lado] = p["coxa"][i]
        a["joelho_" + lado] = p["joelho"][i] * (1.6 if corrida else 1.0)
        a["ombro_" + lado] = p["ombro"][i] * (1.4 if corrida else 1.0)
        a["cot_" + lado] = p["cotovelo"][i] * (3.0 if corrida else 1.0)
    return a, p["quique"]


def _misturar(a, b, k):
    return {kk: a[kk] * (1 - k) + b[kk] * k for kk in a}


def _desenhar_palito(cv, pts, cor=(20, 20, 24), larg=14, esc=1.0):
    p = M.tinta(cor, traco=larg * esc)
    for a, b in (("q", "pesc"), ("q", "joelho_e"), ("joelho_e", "pe_e"), ("q", "joelho_d"), ("joelho_d", "pe_d"),
                 ("ombro_e", "cot_e"), ("cot_e", "mao_e"), ("ombro_d", "cot_d"), ("cot_d", "mao_d")):
        cv.drawLine(*pts[a], *pts[b], p)
    cv.drawCircle(*pts["cab"], 40 * esc, M.tinta(cor, traco=larg * esc))


def _roteiro_palito(t):
    """Anda (0-3), agacha (3-3.6), pula a caixa (3.6-4.8), aterrissa (4.8-5.4), corre (5.4-8.4), comemora (8.4-10)."""
    caixa_x = 1180.0
    if t < 3.0:
        x = 300 + 190 * t
        a, qq = _pose2d_caminhada(t * 2 * math.pi * 1.1)
        y = 0.0 - 60 * qq
    elif t < 3.6:
        k = M.suave(t, 3.0, 3.6)
        x = 870 + 60 * (t - 3.0)
        base, _ = _pose2d_caminhada(3.0 * 2 * math.pi * 1.1)
        agach = {"tronco": 0.45, "coxa_e": 1.0, "coxa_d": 0.9, "joelho_e": 1.9, "joelho_d": 1.8, "ombro_e": -0.9,
                 "ombro_d": -0.8, "cot_e": 0.4, "cot_d": 0.4}
        a = _misturar(base, agach, float(k))
        y = 70 * float(k)
    elif t < 4.8:
        u = (t - 3.6) / 1.2
        x = 906 + 560 * u
        y = 70 - 70 * u - 420 * math.sin(math.pi * u)
        no_ar = {"tronco": 0.25, "coxa_e": 1.5, "coxa_d": 1.3, "joelho_e": 2.2, "joelho_d": 2.0, "ombro_e": 2.4,
                 "ombro_d": 2.2, "cot_e": 0.3, "cot_d": 0.3}
        agach = {"tronco": 0.45, "coxa_e": 1.0, "coxa_d": 0.9, "joelho_e": 1.9, "joelho_d": 1.8, "ombro_e": -0.9,
                 "ombro_d": -0.8, "cot_e": 0.4, "cot_d": 0.4}
        a = _misturar(agach, no_ar, float(M.suave(u, 0, 0.3)))
        a = _misturar(a, {**no_ar, "coxa_e": 0.7, "coxa_d": 0.5, "joelho_e": 0.6, "joelho_d": 0.5}, float(M.suave(u, 0.6, 1)))
    elif t < 5.4:
        k = math.sin(math.pi * (t - 4.8) / 0.6)
        x = 1466 + 120 * (t - 4.8)
        y = 60 * k
        a = {"tronco": 0.3 + 0.2 * k, "coxa_e": 0.6 + 0.4 * k, "coxa_d": 0.4 + 0.4 * k, "joelho_e": 0.5 + 1.0 * k,
             "joelho_d": 0.4 + 1.0 * k, "ombro_e": 1.2 - 1.6 * k, "ombro_d": 1.0 - 1.6 * k, "cot_e": 0.4, "cot_d": 0.4}
    elif t < 8.4:
        x = 1538 + 520 * (t - 5.4)
        a, qq = _pose2d_caminhada((t - 5.4) * 2 * math.pi * 1.8, corrida=True)
        y = -90 * qq
    else:
        u = t - 8.4
        x = 3098 + 260 * max(0.0, 0.5 - u) * 2 * min(u, 0.5)
        pulo = abs(math.sin(u * math.pi * 1.6)) * (1 if u > 0.4 else 0)
        y = -120 * pulo
        a = {"tronco": 0.0, "coxa_e": 0.15 - 0.1 * pulo, "coxa_d": -0.15 + 0.1 * pulo, "joelho_e": 0.1 + 0.5 * pulo,
             "joelho_d": 0.1 + 0.5 * pulo, "ombro_e": 2.7, "ombro_d": 2.9, "cot_e": 0.25, "cot_d": 0.2}
    return x, y, a, caixa_x


def stickman():
    def quadro(i, t):
        s, cv = M.superficie()
        cv.clear(M.cor((248, 246, 240)))
        x, y, a, caixa_x = _roteiro_palito(t)
        cam_x = x - W * 0.42
        for gx in range(-int(cam_x) % 60 - 60, W, 60):
            cv.drawLine(gx, 0, gx, H, M.tinta((210, 225, 240), traco=2))
        for gy in range(0, H, 60):
            cv.drawLine(0, gy, W, gy, M.tinta((210, 225, 240), traco=2))
        chao = H * 0.68
        cv.drawLine(0, chao, W, chao, M.tinta((30, 30, 34), traco=10))
        bx = caixa_x - cam_x
        cv.drawRect(skia.Rect(bx, chao - 200, bx + 200, chao), M.tinta((30, 30, 34), traco=10))
        cv.drawLine(bx, chao - 200, bx + 200, chao, M.tinta((30, 30, 34), traco=6))
        quadril = (x - cam_x, chao - 222 * 1.35 + y)
        pts = _corpo2d(quadril, a, esc=1.35)
        if 5.4 < t < 8.4:
            for k in range(5):
                yy = quadril[1] - 120 + k * 60
                cv.drawLine(quadril[0] - 160 - 60 * k, yy, quadril[0] - 330 - 60 * k, yy, M.tinta((60, 60, 70), traco=6))
        _desenhar_palito(cv, pts, esc=1.35)
        if 2.4 < t < 3.6:
            M.texto(cv, "!", pts["cab"][0] + 40, pts["cab"][1] - 70, 120, (220, 50, 50), fonte="Impact")
        if t > 8.4:
            M.texto(cv, "CONSEGUI", W / 2, H * 0.22, 140, (20, 20, 24), fonte="Impact", alinhar="centro")
        return M.pixels(s)

    return quadro


ESTILOS = {"low_poly": low_poly, "console_antigo": console_antigo, "stickman": stickman}


def main():
    from estilos2 import EXTRAS
    ESTILOS.update(EXTRAS)
    if len(sys.argv) < 2 or sys.argv[1] == "--lista":
        print("Estilos:", ", ".join(sorted(ESTILOS) + ["pov_apocalipse"]))
        return
    nome = sys.argv[1]
    if nome == "pov_apocalipse":  # o POV realista tem luz por pixel e pode ser dividido em partes (--parte 0/2)
        import estilos_pov
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        estilos_pov.main()
        return
    if nome not in ESTILOS:
        sys.exit(f"ERRO: não conheço o estilo '{nome}'.\nO QUE FAZER: rode com --lista e use um dos nomes.")
    quadro = ESTILOS[nome]()
    (SAIDA / "stills").mkdir(parents=True, exist_ok=True)
    if "--quadro" in sys.argv:
        t = float(sys.argv[sys.argv.index("--quadro") + 1])
        M.salvar_png(quadro(int(t * M.FPS), t), SAIDA / "stills" / f"{nome}_t{t:g}.png")
        print("QUADRO_OK", nome, t)
        return
    M.rodar(SAIDA / f"{nome}.mp4", quadro, still=SAIDA / "stills" / f"{nome}.png")
    print("VIDEO_OK", nome)


if __name__ == "__main__":
    main()
