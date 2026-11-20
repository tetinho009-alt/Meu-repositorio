# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Motor dos estilos visuais do kit: cena 3D em triângulos (flat shading, névoa, painter, contorno por casca
invertida), desenho 2D com skia, efeitos de pós (pixel, dithering, VHS, CRT, meio-tom) e gravação em MP4 pelo ffmpeg.
Tudo por código: nenhuma IA de imagem, nenhum áudio."""
import math
import shutil
import subprocess
from pathlib import Path

import numpy as np
import skia

W, H, FPS, DUR = 1080, 1920, 30, 10.0
NQ = int(FPS * DUR)


# ---------------------------------------------------------------- gravação

def _ffmpeg():
    try:  # o do kit (config.json ou o que o painel instalou)
        import config
        return config.ffmpeg()
    except Exception:  # noqa: BLE001
        pass
    return shutil.which("ffmpeg") or str(Path.home() / ".temporada-viral" / "ffmpeg" / "ffmpeg.exe")


def _tem_nvenc():
    try:
        r = subprocess.run([_ffmpeg(), "-hide_banner", "-encoders"], capture_output=True, text=True, timeout=30)
        return "h264_nvenc" in r.stdout
    except OSError:
        return False


class Gravador:
    def __init__(self, saida, w=W, h=H, fps=FPS):
        enc = ["-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "19", "-b:v", "0"] if _tem_nvenc() \
            else ["-c:v", "libx264", "-preset", "medium", "-crf", "18"]
        cmd = [_ffmpeg(), "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps),
               "-i", "-", *enc, "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(saida)]
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        self.w, self.h = w, h

    def quadro(self, rgb):
        rgb = np.asarray(rgb)[..., :3]
        assert rgb.shape[:2] == (self.h, self.w), rgb.shape
        self.p.stdin.write(np.ascontiguousarray(rgb, dtype=np.uint8).tobytes())

    def fechar(self):
        self.p.stdin.close()
        if self.p.wait():
            raise RuntimeError("ffmpeg falhou")


def rodar(saida, quadro_fn, still=None, n=NQ):
    """Grava `n` quadros de quadro_fn(i, t) -> rgb uint8 (H, W, 3). `still`: grava também o quadro do meio em PNG."""
    g = Gravador(saida)
    meio = n // 2
    for i in range(n):
        img = quadro_fn(i, i / FPS)
        g.quadro(img)
        if still and i == meio:
            salvar_png(img, still)
    g.fechar()


def salvar_png(rgb, arq):
    rgb = np.ascontiguousarray(np.asarray(rgb)[..., :3], dtype=np.uint8)
    rgba = np.dstack([rgb, np.full(rgb.shape[:2], 255, np.uint8)])
    skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType).save(str(arq), skia.kPNG)


# ---------------------------------------------------------------- 2D

def superficie(w=W, h=H):
    s = skia.Surface(w, h)
    return s, s.getCanvas()


def pixels(s):
    return s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3].copy()


def cor(c, a=255):
    return skia.Color(int(c[0]), int(c[1]), int(c[2]), int(a))


def tinta(c, a=255, aa=True, traco=None, cap=skia.Paint.kRound_Cap, borrao=0.0):
    p = skia.Paint(AntiAlias=aa, Color=cor(c, a))
    if traco:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(traco)
        p.setStrokeCap(cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if borrao:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, borrao))
    return p


def caminho(pts, fechar=True):
    pa = skia.Path()
    pa.moveTo(*pts[0])
    for p in pts[1:]:
        pa.lineTo(*p)
    if fechar:
        pa.close()
    return pa


def texto(canvas, t, x, y, tam, c, fonte="Arial", negrito=False, alinhar="esq", a=255, contorno=None):
    tf = skia.Typeface(fonte, skia.FontStyle.Bold() if negrito else skia.FontStyle.Normal())
    f = skia.Font(tf, tam)
    larg = f.measureText(t)
    x0 = x - larg / 2 if alinhar == "centro" else (x - larg if alinhar == "dir" else x)
    if contorno:
        canvas.drawString(t, x0, y, f, tinta(contorno[0], a, traco=contorno[1]))
    canvas.drawString(t, x0, y, f, tinta(c, a))
    return larg


def gradiente_vertical(canvas, w, h, c0, c1, y0=0, y1=None):
    y1 = h if y1 is None else y1
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, y0), (0, y1)], [cor(c0), cor(c1)]))
    canvas.drawRect(skia.Rect(0, 0, w, h), p)


# ---------------------------------------------------------------- 3D: malhas

def rx(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], float)


def ry(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], float)


def rz(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], float)


class Malha:
    """Triângulos com cor por face. `emi`: face sem sombra (luz própria). `casca`: face de contorno (só aparece de costas)."""

    def __init__(self, v, f, c, emi=None, casca=None):
        self.v = np.asarray(v, float).reshape(-1, 3)
        self.f = np.asarray(f, int).reshape(-1, 3)
        c = np.asarray(c, float)
        self.c = np.tile(c, (len(self.f), 1)) if c.ndim == 1 else c.reshape(-1, 3)
        self.emi = np.zeros(len(self.f), bool) if emi is None else np.asarray(emi, bool)
        self.casca = np.zeros(len(self.f), bool) if casca is None else np.asarray(casca, bool)

    def mover(self, R=None, t=(0, 0, 0)):
        v = self.v if R is None else self.v @ np.asarray(R).T
        return Malha(v + np.asarray(t, float), self.f, self.c, self.emi, self.casca)


def juntar(malhas):
    malhas = [m for m in malhas if m is not None and len(m.f)]
    vs, fs, cs, es, ks, base = [], [], [], [], [], 0
    for m in malhas:
        vs.append(m.v)
        fs.append(m.f + base)
        cs.append(m.c)
        es.append(m.emi)
        ks.append(m.casca)
        base += len(m.v)
    if not malhas:
        return Malha(np.zeros((0, 3)), np.zeros((0, 3), int), np.zeros((0, 3)))
    return Malha(np.vstack(vs), np.vstack(fs), np.vstack(cs), np.concatenate(es), np.concatenate(ks))


def _orienta(v, f, centro):
    """Vira as faces para fora (normal apontando para longe do centro da peça convexa)."""
    f = np.array(f, int)
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    n = np.cross(b - a, c - a)
    fora = np.einsum("ij,ij->i", n, (a + b + c) / 3 - centro) < 0
    f[fora] = f[fora][:, [0, 2, 1]]
    return f


def caixa(sx, sy, sz, c, R=None, t=(0, 0, 0), base=False, topo_irregular=None, emi=False):
    """Caixa centrada (ou com a base em y=0 se base=True). topo_irregular: função (x, z) -> desconto no topo."""
    x, y, z = sx / 2, sy / 2, sz / 2
    v = np.array([[-x, -y, -z], [x, -y, -z], [x, y, -z], [-x, y, -z], [-x, -y, z], [x, -y, z], [x, y, z], [-x, y, z]])
    if base:
        v[:, 1] += y
    if topo_irregular:
        for i in (2, 3, 6, 7):
            v[i, 1] -= topo_irregular(v[i, 0], v[i, 2])
    f = [[0, 1, 2], [0, 2, 3], [4, 6, 5], [4, 7, 6], [0, 4, 5], [0, 5, 1], [3, 2, 6], [3, 6, 7], [0, 3, 7], [0, 7, 4],
         [1, 5, 6], [1, 6, 2]]
    f = _orienta(v, f, v.mean(axis=0))
    m = Malha(v, f, c, emi=np.full(len(f), emi))
    return m.mover(R, t)


def icosfera(r, c, nivel=0, R=None, t=(0, 0, 0), achatar=(1, 1, 1), ruido=0.0, semente=0):
    p = (1 + 5 ** 0.5) / 2
    v = np.array([[-1, p, 0], [1, p, 0], [-1, -p, 0], [1, -p, 0], [0, -1, p], [0, 1, p], [0, -1, -p], [0, 1, -p],
                  [p, 0, -1], [p, 0, 1], [-p, 0, -1], [-p, 0, 1]], float)
    f = [[0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11], [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6],
         [7, 1, 8], [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9], [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7],
         [9, 8, 1]]
    v = list(v / np.linalg.norm(v[0]))
    for _ in range(nivel):
        meio, novas = {}, []

        def m(a, b):
            k = (min(a, b), max(a, b))
            if k not in meio:
                q = (v[a] + v[b]) / 2
                v.append(q / np.linalg.norm(q))
                meio[k] = len(v) - 1
            return meio[k]

        for a, b, cc in f:
            ab, bc, ca = m(a, b), m(b, cc), m(cc, a)
            novas += [[a, ab, ca], [b, bc, ab], [cc, ca, bc], [ab, bc, ca]]
        f = novas
    v = np.array(v) * r * np.asarray(achatar, float)
    if ruido:
        rng = np.random.default_rng(semente)
        v *= 1 + rng.uniform(-ruido, ruido, (len(v), 1))
    f = _orienta(v, f, np.zeros(3))
    return Malha(v, f, c).mover(R, t)


def cilindro(r, h, n, c, r_topo=None, R=None, t=(0, 0, 0), tampa=True):
    """Cilindro (ou cone, com r_topo=0) com base em y=0."""
    r_topo = r if r_topo is None else r_topo
    ang = np.linspace(0, 2 * math.pi, n, endpoint=False)
    base = np.c_[np.cos(ang) * r, np.zeros(n), np.sin(ang) * r]
    topo = np.c_[np.cos(ang) * r_topo, np.full(n, h), np.sin(ang) * r_topo]
    v = np.vstack([base, topo, [[0, 0, 0], [0, h, 0]]])
    f = []
    for i in range(n):
        j = (i + 1) % n
        f += [[i, j, n + j], [i, n + j, n + i]]
        if tampa:
            f += [[2 * n, j, i], [2 * n + 1, n + i, n + j]]
    f = _orienta(v, f, np.array([0, h / 2, 0]))
    return Malha(v, f, c).mover(R, t)


def terreno(tam, n, altura, cor_fn, centro=(0, 0)):
    xs = np.linspace(-tam / 2, tam / 2, n + 1) + centro[0]
    zs = np.linspace(-tam / 2, tam / 2, n + 1) + centro[1]
    X, Z = np.meshgrid(xs, zs)
    Y = np.vectorize(altura)(X, Z)
    v = np.c_[X.ravel(), Y.ravel(), Z.ravel()]
    f, c = [], []
    for i in range(n):
        for j in range(n):
            a, b, cc, d = i * (n + 1) + j, i * (n + 1) + j + 1, (i + 1) * (n + 1) + j, (i + 1) * (n + 1) + j + 1
            for tri in ([a, cc, b], [b, cc, d]):
                p0, p1, p2 = v[tri]
                nn = np.cross(p1 - p0, p2 - p0)
                if nn[1] < 0:
                    tri = [tri[0], tri[2], tri[1]]
                f.append(tri)
                c.append(cor_fn(*(v[tri].mean(axis=0))))
    return Malha(v, f, c)


def com_casca(m, esp=0.035, c=(15, 12, 20)):
    """Contorno de desenho por casca invertida: a peça inflada, de dentro para fora, em preto."""
    # Infla pela normal média de cada vértice (as faces das peças já apontam para fora). O desenho mostra só as faces
    # da casca que estão de costas para a câmera: atrás da peça, sobrando na silhueta como traço.
    V = m.v[m.f]
    n = np.cross(V[:, 1] - V[:, 0], V[:, 2] - V[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    nv = np.zeros_like(m.v)
    for k in range(3):
        np.add.at(nv, m.f[:, k], n)
    nv /= np.linalg.norm(nv, axis=1, keepdims=True) + 1e-12
    casca = Malha(m.v + nv * esp, m.f, c, casca=np.ones(len(m.f), bool))
    return juntar([casca, m])


# ---------------------------------------------------------------- 3D: câmera e desenho

class Camera:
    def __init__(self, pos, alvo, fov=50.0, w=W, h=H, orto=None):
        self.pos, self.alvo = np.asarray(pos, float), np.asarray(alvo, float)
        self.fov, self.w, self.h, self.orto = fov, w, h, orto
        fw = self.alvo - self.pos
        self.fw = fw / np.linalg.norm(fw)
        rt = np.cross(self.fw, [0, 1, 0])
        self.rt = rt / np.linalg.norm(rt)
        self.up = np.cross(self.rt, self.fw)
        self.f = (h / 2) / math.tan(math.radians(fov) / 2)

    def para_camera(self, p):
        d = p - self.pos
        return np.stack([d @ self.rt, d @ self.up, d @ self.fw], axis=-1)

    def projetar(self, pc):
        if self.orto:
            s = self.h / self.orto
            return np.stack([self.w / 2 + pc[..., 0] * s, self.h / 2 - pc[..., 1] * s], axis=-1)
        z = np.maximum(pc[..., 2], 1e-3)
        return np.stack([self.w / 2 + pc[..., 0] / z * self.f, self.h / 2 - pc[..., 1] / z * self.f], axis=-1)


LUZ_PADRAO = np.array([-0.45, -0.8, -0.35])


def desenhar(canvas, m, cam, luz=LUZ_PADRAO, amb=0.42, nevoa=None, aa=True, tons=None, grade=0.0,
             variacao=0.0, semente=0, perto=0.15, sombra_cor=None, borda=None):
    """Desenha a malha no canvas. nevoa=(cor, ini, fim). tons: quantiza a luz em N degraus (cel shading).
    grade: arredonda os vértices na tela para essa grade (tremor de console antigo). variacao: ruído de cor por face.
    borda=(cor, largura): traço nas arestas de cada face (estilo facetado)."""
    if not len(m.f):
        return
    luz = np.asarray(luz, float)
    luz = luz / np.linalg.norm(luz)
    V = m.v[m.f]
    n = np.cross(V[:, 1] - V[:, 0], V[:, 2] - V[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    cen = V.mean(axis=1)
    olhar = (cam.pos - cen) if not cam.orto else np.tile(-cam.fw, (len(cen), 1))
    frente = np.einsum("ij,ij->i", n, olhar) > 0
    vis = np.where(m.casca, ~frente, frente)
    pc = cam.para_camera(V)
    vis &= (pc[..., 2] > perto).all(axis=1) if not cam.orto else True
    idx = np.nonzero(vis)[0]
    if not len(idx):
        return
    dif = np.clip(-(n[idx] @ luz), 0, 1)
    if tons:
        dif = np.floor(dif * tons + 0.35) / tons
        dif = np.clip(dif, 0, 1)
    s = amb + (1 - amb) * dif
    col = m.c[idx] * s[:, None]
    if sombra_cor is not None and tons:
        escuro = dif < 0.5
        col[escuro] = np.asarray(m.c[idx][escuro]) * 0.55 + np.asarray(sombra_cor) * 0.45
    col[m.emi[idx]] = m.c[idx][m.emi[idx]]
    col[m.casca[idx]] = m.c[idx][m.casca[idx]]
    if variacao:
        rng = np.random.default_rng(semente)
        ruido = rng.uniform(1 - variacao, 1 + variacao, len(m.f))[idx]
        col = col * ruido[:, None]
    z = pc[idx, :, 2].mean(axis=1)
    if nevoa:
        nc, ini, fim = nevoa
        tt = np.clip((z - ini) / (fim - ini), 0, 1)[:, None]
        col = col * (1 - tt) + np.asarray(nc, float) * tt
    col = np.clip(col, 0, 255)
    tela = cam.projetar(pc[idx])
    if grade:
        tela = np.round(tela / grade) * grade
    ordem = np.argsort(-z)
    paint = skia.Paint(AntiAlias=aa)
    if aa:  # preenche e contorna com a mesma cor: some a costura clara entre triângulos vizinhos
        paint.setStyle(skia.Paint.kStrokeAndFill_Style)
        paint.setStrokeWidth(1.0)
        paint.setStrokeJoin(skia.Paint.kRound_Join)
    pb = tinta(borda[0], traco=borda[1]) if borda else None
    for k in ordem:
        a, b, c = tela[k]
        pa = skia.Path()
        pa.moveTo(a[0], a[1])
        pa.lineTo(b[0], b[1])
        pa.lineTo(c[0], c[1])
        pa.close()
        r, g, bb = col[k]
        paint.setColor(skia.Color(int(r), int(g), int(bb)))
        canvas.drawPath(pa, paint)
        if pb is not None and not m.casca[idx[k]]:
            canvas.drawPath(pa, pb)


# ---------------------------------------------------------------- boneco 3D (corpo + roupa por cima)

def pose_caminhada(fase, passo=1.0):
    """Ângulos (rad) de uma caminhada. Joelho só dobra para trás e cotovelo só para a frente (sinais travados)."""
    s, c = math.sin(fase), math.cos(fase)
    coxa_d = -0.45 * s * passo
    coxa_e = 0.45 * s * passo
    joelho_d = 0.15 + 0.75 * max(0.0, c) * passo
    joelho_e = 0.15 + 0.75 * max(0.0, -c) * passo
    ombro_d = 0.35 * s * passo
    ombro_e = -0.35 * s * passo
    cot_d = 0.25 + 0.3 * max(0.0, -c) * passo
    cot_e = 0.25 + 0.3 * max(0.0, c) * passo
    return {"coxa": (coxa_e, coxa_d), "joelho": (joelho_e, joelho_d), "ombro": (ombro_e, ombro_d),
            "cotovelo": (cot_e, cot_d), "quique": 0.035 * abs(c) * passo}


def boneco(pose, cores, yaw=0.0, pos=(0, 0, 0), casca=None, cabelo=True, esc=1.0):
    """Personagem low poly: pele por baixo, roupa (camiseta e calça) por cima. Frente para +z antes do yaw.
    Joelho: rotação positiva em x (pé vai para trás). Cotovelo: negativa (mão vai para a frente)."""
    pele, camisa, calca, sapato, cab = (cores[k] for k in ("pele", "camisa", "calca", "sapato", "cabelo"))
    Y = ry(yaw)
    pecas = []
    quadril_y = 0.95 + pose.get("quique", 0.0)
    base = np.array([0, quadril_y, 0])

    def seg(piv, R, comp, larg, prof, c, mais=None):
        caixa_ = caixa(larg, comp, prof, c, t=(0, -comp / 2, 0))
        pecas.append(caixa_.mover(R, piv))
        return piv + R @ np.array([0, -comp, 0])

    # tronco (camiseta) e quadril (calça); cintura mais fina que ombro (ampulheta leve)
    pecas.append(caixa(0.40, 0.30, 0.22, camisa, t=base + [0, 0.42, 0]))
    pecas.append(caixa(0.34, 0.22, 0.20, camisa, t=base + [0, 0.17, 0]))
    pecas.append(caixa(0.36, 0.16, 0.21, calca, t=base + [0, 0.0, 0]))
    pecas.append(cilindro(0.06, 0.10, 6, pele, t=base + [0, 0.57, 0]))
    cabeca_c = base + [0, 0.78, 0]
    pecas.append(icosfera(0.15, pele, nivel=1, t=cabeca_c, achatar=(0.95, 1.08, 1.0)))
    if cabelo:
        pecas.append(icosfera(0.158, cab, nivel=1, t=cabeca_c + [0, 0.04, -0.025], achatar=(1.0, 0.85, 1.0)))
    # olhos
    for lado in (-1, 1):
        pecas.append(caixa(0.035, 0.05, 0.012, (25, 20, 30), t=cabeca_c + [0.055 * lado, 0.0, 0.132]))
    # pernas
    for i, lado in enumerate((-1, 1)):
        quadril = base + [0.1 * lado, -0.04, 0]
        Rc = rx(-pose["coxa"][i])
        joelho = seg(quadril, Rc, 0.44, 0.15, 0.16, calca)
        Rs = Rc @ rx(pose["joelho"][i])
        tornozelo = seg(joelho, Rs, 0.42, 0.12, 0.13, calca)
        pecas.append(caixa(0.13, 0.08, 0.24, sapato, t=(0, -0.03, 0.05)).mover(Rs, tornozelo))
    # braços: manga curta (camisa) no braço, antebraço de pele
    for i, lado in enumerate((-1, 1)):
        ombro = base + [0.25 * lado, 0.53, 0]
        Ro = rx(-pose["ombro"][i]) @ rz(0.08 * lado)
        cot = seg(ombro, Ro, 0.30, 0.11, 0.11, camisa)
        Rb = Ro @ rx(-pose["cotovelo"][i])
        pulso = seg(cot, Rb, 0.27, 0.085, 0.085, pele)
        pecas.append(caixa(0.09, 0.10, 0.07, pele, t=(0, -0.05, 0)).mover(Rb, pulso))
    if casca:
        pecas = [com_casca(p, casca, (18, 14, 24)) for p in pecas]
    m = juntar(pecas)
    m = Malha(m.v * esc, m.f, m.c, m.emi, m.casca)
    return m.mover(Y, pos)


# ---------------------------------------------------------------- pós

BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0


def dithering(img, niveis=32):
    h, w = img.shape[:2]
    lim = np.tile(BAYER4, (h // 4 + 1, w // 4 + 1))[:h, :w, None]
    passo = 255.0 / (niveis - 1)
    return np.clip(np.floor(img / passo + lim) * passo, 0, 255).astype(np.uint8)


def ampliar(img, k):
    return np.repeat(np.repeat(img, k, axis=0), k, axis=1)


def reduzir(img, k):
    h, w = img.shape[:2]
    return img[: h // k * k, : w // k * k].reshape(h // k, k, w // k, k, -1).mean(axis=(1, 3))


def borrar(img, k=8):
    """Borrão barato: reduz e amplia de volta (com média)."""
    h, w = img.shape[:2]
    p = ampliar(reduzir(img.astype(float), k), k)
    out = np.zeros_like(img, dtype=float)
    out[: p.shape[0], : p.shape[1]] = p
    out[p.shape[0]:, :] = out[p.shape[0] - 1: p.shape[0], :]
    out[:, p.shape[1]:] = out[:, p.shape[1] - 1: p.shape[1]]
    return out


def granulado(img, forca=12, semente=0):
    rng = np.random.default_rng(semente)
    r = rng.normal(0, forca, img.shape[:2])[..., None]
    return np.clip(img.astype(float) + r, 0, 255).astype(np.uint8)


def vinheta(img, forca=0.55):
    h, w = img.shape[:2]
    y, x = np.ogrid[:h, :w]
    d = ((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2
    m = 1 - forca * np.clip(d / 2, 0, 1) ** 1.2
    return np.clip(img * m[..., None], 0, 255).astype(np.uint8)


def vhs(img, t, semente=0):
    rng = np.random.default_rng(semente)
    x = img.astype(float)
    h, w = x.shape[:2]
    lum = x.mean(axis=2, keepdims=True)
    x = x * 0.75 + lum * 0.25
    x = borrar(x, 2) * 0.6 + x * 0.4
    out = x.copy()
    out[:, 7:, 0] = x[:, :-7, 0]
    out[:, :-5, 2] = x[:, 5:, 2]
    for _ in range(3):
        y0, alt = int(rng.integers(0, h - 40)), int(rng.integers(4, 30))
        out[y0:y0 + alt] = np.roll(out[y0:y0 + alt], int(rng.integers(-25, 25)), axis=1)
    faixa = int((t * 260) % (h + 200)) - 100
    if 0 <= faixa < h - 60:
        out[faixa:faixa + 60] = np.roll(out[faixa:faixa + 60], 18, axis=1) * 0.85 + rng.normal(0, 35, (60, w, 1))
    out[::3] *= 0.86
    out += rng.normal(0, 9, (h, w, 1))
    return np.clip(out, 0, 255).astype(np.uint8)


_MAPA_CRT = {}


def crt(img, curva=0.10):
    h, w = img.shape[:2]
    if (h, w) not in _MAPA_CRT:
        y, x = np.mgrid[:h, :w].astype(float)
        nx, ny = (x - w / 2) / (w / 2), (y - h / 2) / (h / 2)
        r2 = nx * nx + ny * ny
        k = 1 + curva * r2
        sx = np.clip((nx * k + 1) * w / 2, 0, w - 1).astype(int)
        sy = np.clip((ny * k + 1) * h / 2, 0, h - 1).astype(int)
        fora = (np.abs(nx * k) > 0.985) | (np.abs(ny * k) > 0.99)
        _MAPA_CRT[(h, w)] = (sy, sx, fora)
    sy, sx, fora = _MAPA_CRT[(h, w)]
    x = img[sy, sx].astype(float)
    x = x + borrar(x, 6) * 0.35
    mascara = np.ones((1, w, 3))
    mascara[0, 0::3] = (1.0, 0.72, 0.72)
    mascara[0, 1::3] = (0.72, 1.0, 0.72)
    mascara[0, 2::3] = (0.72, 0.72, 1.0)
    x = x * mascara
    x[1::4] *= 0.62
    x[2::4] *= 0.8
    x[fora] = 0
    return vinheta(np.clip(x, 0, 255).astype(np.uint8), 0.6)


def meio_tom(lum, passo=14, ang=0.6):
    """Retícula de mangá: pontos pretos cujo raio cresce com o escuro. lum 0..1 (1 = branco). Devolve 0..1."""
    h, w = lum.shape
    y, x = np.mgrid[:h, :w].astype(float)
    c, s = math.cos(ang), math.sin(ang)
    u, v = (x * c - y * s) / passo, (x * s + y * c) / passo
    du, dv = u - np.round(u), v - np.round(v)
    d = np.sqrt(du * du + dv * dv)
    raio = np.sqrt(np.clip(1 - lum, 0, 1)) * 0.62
    return np.where(d < raio, 0.0, 1.0)


def suave(t, a, b):
    x = np.clip((t - a) / (b - a), 0, 1)
    return x * x * (3 - 2 * x)
