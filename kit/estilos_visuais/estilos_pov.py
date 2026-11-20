# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""POV de apocalipse, versão realista: luz por pixel (lanterna com cone e queda, fogo dos carros, céu de fumaça), textura
presa no mundo (asfalto rachado, concreto manchado, tijolo, vidro, metal queimado), névoa que se mexe, poeira no facho,
chamas, bloom, borrão de movimento, grão e cor de cinema. A mão de luva com a lanterna é vetor com degradê.
Uso (a partir de kit/): python estilos_visuais/estilos.py pov_apocalipse [--quadro T | --parte K/N]"""
import math
import sys
from pathlib import Path

import numpy as np
import skia

import motor as M
import deferido as D
from mao_pov import mao_lanterna
from motor import W, H

from estilos import SAIDA  # noqa: E402  (trabalho/estilos do kit)
WR, HR = W // 2, H // 2  # a luz por pixel roda em meia resolução e é ampliada com filtro
ASF, CAL, CONC, TIJ, VID, CARRO, ENT, FAIXA, PNEU, QUEIM, POSTE = range(1, 12)
ALBEDO = {ASF: (52, 52, 56), CAL: (120, 116, 110), CONC: (150, 144, 136), TIJ: (140, 84, 64), VID: (16, 18, 22),
          ENT: (78, 74, 68), FAIXA: (84, 80, 62), PNEU: (14, 14, 14), QUEIM: (26, 24, 22), POSTE: (64, 64, 68)}


def cena():
    rng = np.random.default_rng(47)
    partes = []

    def p(m, mat):
        partes.append((m, mat))

    p(M.caixa(15, 0.1, 110, ALBEDO[ASF], t=(0, -0.05, 40)), ASF)
    for z in np.arange(-6, 95, 4.0):
        if rng.random() < 0.75:
            p(M.caixa(0.16, 0.012, 2.0, ALBEDO[FAIXA], t=(0.1, 0.006, z)), FAIXA)
    for lado in (-1, 1):
        p(M.caixa(3.0, 0.18, 110, ALBEDO[CAL], t=(lado * 6.0, 0.09, 40)), CAL)
        z = -8.0
        while z < 95:
            larg, alt = rng.uniform(6, 10), rng.uniform(8, 24)
            fase = rng.uniform(0, 6)
            topo = (lambda f, a: (lambda x, zz: abs(math.sin(x * 1.3 + zz * 0.7 + f)) * a * 0.3))(fase, alt)
            mat = CONC if rng.random() < 0.55 else TIJ
            cor = tuple(np.clip(np.array(ALBEDO[mat]) * rng.uniform(0.8, 1.15), 0, 255))
            cx = lado * 10.5
            p(M.caixa(6, alt, larg, cor, t=(cx, 0, z + larg / 2), base=True, topo_irregular=topo), mat)
            fachada = lado * 7.5
            for andar, jy in enumerate(np.arange(3.2, alt * 0.72, 3.0)):
                for jz in np.arange(z + 1.2, z + larg - 0.9, 2.0):
                    quebrada = rng.random() < 0.35
                    p(M.caixa(0.06, 1.45, 1.05, ALBEDO[QUEIM] if quebrada else ALBEDO[VID], t=(fachada - lado * 0.02, jy, jz)),
                      QUEIM if quebrada else VID)
                    p(M.caixa(0.12, 0.12, 1.25, ALBEDO[CONC], t=(fachada - lado * 0.05, jy - 0.8, jz)), CONC)
                if rng.random() < 0.35 and andar > 0:
                    jz = z + larg / 2
                    p(M.caixa(0.95, 0.14, 2.6, ALBEDO[CONC], t=(fachada - lado * 0.47, jy - 0.85, jz)), CONC)
                    for k in range(7):
                        p(M.caixa(0.04, 0.9, 0.04, ALBEDO[POSTE], t=(fachada - lado * 0.92, jy - 0.35, jz - 1.2 + k * 0.4)), POSTE)
            if rng.random() < 0.6:
                p(M.caixa(0.08, 2.6, larg * 0.6, ALBEDO[VID], t=(fachada - lado * 0.03, 1.3, z + larg / 2)), VID)
                if rng.random() < 0.5:
                    p(M.caixa(0.1, 1.3, larg * 0.6, ALBEDO[POSTE], t=(fachada - lado * 0.06, 1.95, z + larg / 2)), POSTE)
            for _ in range(int(rng.integers(2, 6))):
                p(M.icosfera(rng.uniform(0.3, 0.9), ALBEDO[ENT], nivel=0, t=(fachada - lado * rng.uniform(0.4, 1.8), 0.15,
                                                                          z + rng.uniform(0, larg)),
                             achatar=(1.3, 0.6, 1.2), ruido=0.35, semente=int(rng.integers(9999))), ENT)
            z += larg + rng.uniform(0.0, 1.0)
        for zp in np.arange(0, 95, 13.0):
            inclina = rng.uniform(-0.25, 0.25) if rng.random() < 0.4 else 0.0
            p(M.cilindro(0.08, 6.0, 6, ALBEDO[POSTE], R=M.rz(inclina * lado), t=(lado * 4.9, 0, zp)), POSTE)
    fogos = []
    perto = [(2.6, 11.0, 0.35)]
    for k in range(11):
        x, z, ang = perto.pop() if perto else (rng.uniform(-4.0, 4.0), rng.uniform(16, 85), rng.uniform(-0.7, 0.7))
        queimado = k == 0 or rng.random() < 0.45
        cor = (40, 36, 34) if queimado else tuple(int(v) for v in rng.integers(50, 150, 3))
        R = M.ry(ang)
        mat = QUEIM if queimado else CARRO
        p(M.caixa(1.8, 0.7, 4.3, cor, R=R, t=(x, 0.68, z)), mat)
        p(M.caixa(1.62, 0.62, 2.3, cor, R=R, t=(x, 1.33, z) + R @ np.array([0, 0, -0.2])), mat)
        p(M.caixa(1.64, 0.42, 2.0, ALBEDO[VID], R=R, t=(x, 1.36, z) + R @ np.array([0, 0, -0.2])), VID)
        for dx, dz in ((-0.85, 1.35), (0.85, 1.35), (-0.85, -1.35), (0.85, -1.35)):
            p(M.cilindro(0.34, 0.26, 10, ALBEDO[PNEU], R=R @ M.rz(math.pi / 2), t=np.array([x, 0.34, z]) + R @ np.array([dx + 0.13 * np.sign(dx), 0, dz])), PNEU)
        if queimado and len(fogos) < 4:
            fogos.append(np.array([x, 1.9, z]))
    for _ in range(110):
        p(M.icosfera(rng.uniform(0.06, 0.32), ALBEDO[ENT], nivel=0, t=(rng.uniform(-5, 5), 0.04, rng.uniform(2, 90)),
                     achatar=(1.4, 0.5, 1.2), ruido=0.35, semente=int(rng.integers(9999))), ENT)
    for _ in range(25):
        R = M.ry(rng.uniform(0, 3)) @ M.rx(rng.uniform(-0.4, 0.4))
        p(M.caixa(rng.uniform(0.3, 1.2), rng.uniform(0.15, 0.4), rng.uniform(0.3, 1.0), ALBEDO[ENT], R=R,
                  t=(rng.uniform(-5, 5), 0.12, rng.uniform(2, 90))), ENT)
    malha = M.juntar([m for m, _ in partes])
    mat = np.concatenate([np.full(len(m.f), k) for m, k in partes if len(m.f)])
    return malha, mat, fogos


def pov():
    malha, mat, fogos = cena()
    lin_alb = (malha.c / 255.0) ** 2.2
    rng = np.random.default_rng(3)
    poeira = np.c_[rng.uniform(-3.5, 3.5, 900), rng.uniform(0.3, 3.0, 900), rng.uniform(-2, 26, 900)]
    brasas = rng.uniform(0, 1, (140, 4))
    estado = {"ant": None}
    ys, xs = np.mgrid[:HR, :WR].astype(np.float32) * 2

    def quadro(i, t):
        passo = t * 2 * math.pi * 0.9
        z = 1.15 * t
        guinada = 0.28 * math.sin(t * 0.42) - 0.06
        olho = np.array([0.02 * math.sin(passo), 1.66 + 0.025 * math.sin(2 * passo), z])
        olhar = np.array([math.sin(guinada), -0.07 + 0.03 * math.sin(t * 0.37), math.cos(guinada)])
        cam = M.Camera(olho, olho + olhar * 10, fov=68, w=WR, h=HR)
        q = D.Quadro3D(malha, cam, WR, HR)
        fc, n, pos, prof, ceu = q.fc, q.n, q.pos, q.prof, q.ceu
        alb = lin_alb[fc].astype(np.float32)
        m = mat[fc]
        # ---- textura presa no mundo
        u, v, chao = D.coords_parede(pos, n)
        fino = D.fbm(u * 3.1, v * 3.1, 2)
        medio = D.fbm(u * 0.8, v * 0.8, 3)
        grande = D.fbm(u * 0.12 + 5, v * 0.12, 2)
        risca = D.fbm(u * 0.9, v * 0.07, 2)
        perto = np.exp(-prof / 22.0)
        tex = 0.8 + 0.4 * medio
        poca = (m == ASF) & (D.fbm(u * 0.35 + 9, v * 0.35, 3) > 0.6)
        tex = np.where(m == ASF, (0.4 + 0.9 * fino) * (0.65 + 0.7 * medio) * np.where(poca, 0.35, 1.0)
                       * np.where(grande > 0.6, 0.8, 1.0), tex)
        juntas = (np.abs((u / 1.2) % 1 - 0.5) > 0.47) | (np.abs((v / 1.2) % 1 - 0.5) > 0.47)
        tex = np.where(m == CAL, (0.75 + 0.4 * fino) * np.where(juntas, 0.6, 1.0), tex)
        tex = np.where(m == CONC, (0.62 + 0.6 * risca) * (1 - 0.45 * np.exp(-np.maximum(pos[..., 1], 0) / 1.6)) * (0.85 + 0.3 * fino), tex)
        linha = (np.abs((v / 0.32) % 1 - 0.5) > 0.42)
        coluna = np.abs(((u / 0.62) + 0.5 * (np.floor(v / 0.32) % 2)) % 1 - 0.5) > 0.45
        tij = np.where(linha | coluna, 1.45, 0.85 + 0.35 * fino)
        tex = np.where(m == TIJ, (tij * perto + (1 - perto) * 1.0) * (0.75 + 0.4 * risca), tex)
        tex = np.where((m == ENT) | (m == QUEIM), 0.3 + 0.8 * fino, tex)
        tex = np.where(m == FAIXA, 0.35 + 0.8 * fino * medio * 2, tex)
        ferrugem = (m == CARRO) & (medio > 0.62)
        alb = np.where(ferrugem[..., None], np.array([0.22, 0.08, 0.03], np.float32), alb)
        alb = alb * tex[..., None] * (0.85 + 0.3 * grande)[..., None]
        # ---- luz
        hemi = 0.45 + 0.55 * (0.5 + 0.5 * n[..., 1])
        luz = np.array([0.045, 0.03, 0.028], np.float32)[None, None, :] * hemi[..., None] + \
            np.array([0.008, 0.006, 0.005], np.float32)
        brilho_fogo = 0.0
        for k, fpos in enumerate(fogos):
            fl = 0.8 + 0.15 * math.sin(t * 13 + k * 2.1) + 0.1 * math.sin(t * 31 + k)
            brilho_fogo = max(brilho_fogo, fl)
            L = fpos[None, None, :] - pos
            d2 = np.einsum("hwc,hwc->hw", L, L)
            lam = np.clip(np.einsum("hwc,hwc->hw", n, L) / np.sqrt(d2 + 1e-6), 0, 1)
            luz = luz + (np.array([1.0, 0.42, 0.12], np.float32) * 9.0 * fl)[None, None, :] * (lam / (1 + d2 * 0.16))[..., None]
        mira = cam.fw + cam.rt * (0.06 + 0.05 * math.sin(t * 0.9)) - cam.up * 0.24
        mira /= np.linalg.norm(mira)
        fonte = cam.pos + cam.rt * 0.28 - cam.up * 0.36 + cam.fw * 0.3
        L = pos - fonte[None, None, :]
        dist = np.sqrt(np.einsum("hwc,hwc->hw", L, L)) + 1e-6
        ld = L / dist[..., None]
        cosang = ld @ mira
        cone = D.suave(cosang, math.cos(math.radians(17)), math.cos(math.radians(6))) + \
            0.10 * D.suave(cosang, math.cos(math.radians(32)), math.cos(math.radians(17)))
        lam = np.clip(-np.einsum("hwc,hwc->hw", n, ld), 0, 1)
        dd = np.maximum(dist, 2.6)  # perto da lente a luz não estoura
        lant = cone * lam * 8.5 / (1 + 0.07 * dd * dd)
        luz = luz + np.array([1.0, 0.94, 0.82], np.float32)[None, None, :] * lant[..., None]
        brilhante = (m == ASF) | (m == CARRO) | (m == VID) | (m == POSTE)
        forca_spec = np.where(poca, 5.0, 1.0)
        hv = -(ld + q.dir)
        hv /= np.linalg.norm(hv, axis=2, keepdims=True) + 1e-6
        spec = np.where(brilhante, np.clip(np.einsum("hwc,hwc->hw", n, hv), 0, 1) ** 40 * cone * 6.0 * forca_spec / (1 + 0.09 * dd * dd), 0)
        cor = alb * luz + spec[..., None] * np.array([1.0, 0.95, 0.85], np.float32)
        # ---- névoa de fumaça, espalhamento no facho e céu
        fum = D.fbm(xs / 210 + t * 0.12, ys / 260 - t * 0.04, 3)
        nev = 1 - np.exp(-prof * 0.016)
        nev = np.clip(nev * (0.7 + 0.3 * np.exp(-np.maximum(pos[..., 1], 0) / 7)) * (0.7 + 0.6 * fum), 0, 1)
        cor_nev = np.array([0.075, 0.04, 0.028], np.float32)[None, None, :] * (0.8 + 0.5 * fum[..., None])
        cor = cor * (1 - nev[..., None]) + cor_nev * nev[..., None]
        g = D.suave(q.dir @ mira, math.cos(math.radians(22)), math.cos(math.radians(5)))
        cor = cor + (np.array([1.0, 0.92, 0.78], np.float32) * 0.06)[None, None, :] * (g * (1 - np.exp(-np.minimum(q.t, 20) * 0.08)) * (0.7 + 0.6 * fum))[..., None]
        dy = q.dir[..., 1]
        ceu_cor = np.array([0.30, 0.09, 0.035], np.float32) * (1 - D.suave(dy, -0.05, 0.5))[..., None] + \
            np.array([0.025, 0.018, 0.02], np.float32) * D.suave(dy, -0.05, 0.5)[..., None]
        ceu_cor = ceu_cor * (0.55 + 0.7 * fum[..., None])
        cor = np.where(ceu[..., None], ceu_cor, cor)
        # ---- partículas (aditivas): chamas, poeira no facho, brasas
        sp, cvp = M.superficie(WR, HR)
        fumos = []
        cvp.clear(skia.Color(0, 0, 0))
        mais = lambda c, a, r: (lambda p_: (p_.setBlendMode(skia.BlendMode.kPlus), p_)[1])(M.tinta(c, a, borrao=r))
        for k, fpos in enumerate(fogos):
            pc = cam.para_camera(fpos)
            if pc[2] < 0.5:
                continue
            sx, sy = cam.projetar(pc)
            if not (0 <= sx < WR and 0 <= sy < HR) or prof[int(sy), int(sx)] < pc[2] - 1.5:
                continue
            esc = cam.f / pc[2]
            for j in range(70):
                fase = (t * (1.3 + 0.9 * ((j * 37) % 11) / 11) + j * 0.137) % 1.0
                ox = (math.sin(j * 12.9 + t * 5.3) * 0.5 + math.sin(j * 3.1 + t * 11) * 0.15) * (1 - fase * 0.6)
                r = (0.16 * (1 - fase) + 0.03) * esc
                quente = 1 - fase
                c = (255, int(90 + 150 * quente ** 1.5), int(20 + 90 * quente ** 3))
                cvp.drawCircle(sx + ox * esc, sy - fase * 1.9 * esc, r * 1.3, mais(c, int(95 * quente + 15), r * 1.1))
            for j in range(16):
                fase = (t * 0.22 + j / 16) % 1.0
                fumos.append((sx + (math.sin(j * 4.7 + t * 0.6) * 0.8 + fase * 1.5) * esc, sy - (1.6 + fase * 7) * esc,
                              (0.5 + fase * 2.2) * esc, 0.75 * (1 - fase)))
        for px, py, pz in poeira:
            pw = np.array([px, py, (pz + z * 0.0) % 26 + z - 2])
            dl = pw - fonte
            dd = np.linalg.norm(dl)
            ca = dl @ mira / (dd + 1e-6)
            if ca < 0.93 or dd > 12:
                continue
            pc = cam.para_camera(pw)
            if pc[2] < 0.3:
                continue
            sx, sy = cam.projetar(pc)
            a = int(min(255, 200 * (ca - 0.93) / 0.07 / (1 + 0.15 * dd)))
            cvp.drawCircle(sx, sy, 0.8 + 3 / pc[2], mais((255, 240, 210), a, 0.6))
        for bx, by, bz, bv in brasas:
            x = (bx * WR + 20 * math.sin(t * 2 + bv * 9)) % WR
            y = HR - ((by * HR + t * (40 + 75 * bv)) % HR)
            cvp.drawCircle(x, y, 0.8 + 1.5 * bv, mais((255, int(140 + 80 * bv), 50), 200, 1))
        part = (M.pixels(sp).astype(np.float32) / 255.0) ** 2.2
        if fumos:
            sf, cvf = M.superficie(WR, HR)
            cvf.clear(skia.Color(0, 0, 0))
            for fx_, fy_, fr, fa in fumos:
                cvf.drawCircle(fx_, fy_, fr, M.tinta((255, 255, 255), int(255 * fa * 0.5), borrao=fr * 0.45))
            esc_f = M.pixels(sf)[..., 0].astype(np.float32) / 255.0
            cor = cor * (1 - 0.75 * esc_f[..., None])
        cor = cor + part * 1.7
        # ---- tom, cor de cinema, mão por cima
        img = D.reinhard(cor, 2.1)
        img = img + np.array([0.0, 0.012, 0.02], np.float32) * (1 - img)
        rgb = D.de_linear(img)
        s2, cv2 = M.superficie()
        cv2.drawImageRect(skia.Image.fromarray(np.dstack([rgb, np.full(rgb.shape[:2], 255, np.uint8)]),
                                               colorType=skia.kRGBA_8888_ColorType), skia.Rect(0, 0, W, H),
                          skia.SamplingOptions(skia.FilterMode.kLinear))
        alvo = cam.projetar(cam.para_camera(cam.pos + mira * 8)) * 2
        mao_lanterna(cv2, passo, alvo, brilho_fogo)
        M.texto(cv2, "DIA 47", 64, 132, 56, (236, 226, 204), fonte="Consolas", negrito=True, a=220)
        M.texto(cv2, "água: 1/3   bateria: 22%", 64, 186, 30, (222, 212, 192), fonte="Consolas", a=200)
        f = M.pixels(s2).astype(np.float32)
        # ---- bloom, aberração cromática, borrão de movimento, grão, vinheta
        claro = np.clip(f - 185, 0, None)
        f = f + M.borrar(claro, 8) * 0.35 + M.borrar(claro, 24) * 0.3
        f[:, 3:, 0] = f[:, :-3, 0]
        f[:, :-3, 2] = f[:, 3:, 2]
        if estado["ant"] is not None:
            f = f * 0.72 + estado["ant"] * 0.28
        estado["ant"] = f.copy()
        f = f + np.random.default_rng(i).normal(0, 7, f.shape[:2])[..., None]
        return M.vinheta(np.clip(f, 0, 255).astype(np.uint8), 0.55)

    return quadro


def main():
    quadro = pov()
    (SAIDA / "stills").mkdir(parents=True, exist_ok=True)
    if "--quadro" in sys.argv:
        t = float(sys.argv[sys.argv.index("--quadro") + 1])
        M.salvar_png(quadro(int(t * M.FPS), t), SAIDA / "stills" / f"pov_apocalipse_t{t:g}.png")
        print("QUADRO_OK pov", t)
        return
    if "--parte" in sys.argv:
        k, n = (int(x) for x in sys.argv[sys.argv.index("--parte") + 1].split("/"))
        ini, fim = M.NQ * k // n, M.NQ * (k + 1) // n
        if ini > 0:
            quadro(ini - 1, (ini - 1) / M.FPS)  # aquece o borrão de movimento na emenda
        g = M.Gravador(SAIDA / f"pov_parte{k}.mp4")
        for i in range(ini, fim):
            img = quadro(i, i / M.FPS)
            g.quadro(img)
            if i == M.NQ // 2:
                M.salvar_png(img, SAIDA / "stills" / "pov_apocalipse.png")
        g.fechar()
        print("PARTE_OK", k, n)
        return
    M.rodar(SAIDA / "pov_apocalipse.mp4", quadro, still=SAIDA / "stills" / "pov_apocalipse.png")
    print("VIDEO_OK pov_apocalipse")


if __name__ == "__main__":
    main()
