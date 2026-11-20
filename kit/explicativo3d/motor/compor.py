# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Composição final: fundo + quadros RGBA do Blender + gancho, legenda, rótulos e o cartão de CTA de cada rede.

    python explicativo3d/motor/compor.py <spec.json> [--cpu]

Uma passada só gera as versões de todas as redes: até o CTA o quadro é o mesmo e vai para os encoders de uma vez;
no cartão final cada versão desenha o CTA da sua rede. Encoder e áudio seguem o kit (NVENC -> QSV -> AMF ->
VideoToolbox -> libx264; AAC estéreo 48 kHz). Todo texto respeita a `zona_segura` do config do kit.

spec.json (caminhos relativos à pasta do spec):
    quadros:   pasta com q_0001.png ...
    etiquetas: etiquetas.json (âncora de cada rótulo, quadro a quadro, 0..1)
    audio:     wav já masterizado (masterizar.py)
    duracao:   segundos
    gancho:    {"linhas": [["TEXTO", "branco"|"destaque"], ...], "ate": 2.0}
    legenda:   [[ini, fim, "PALAVRA", destaque], ...]
    rotulos:   [["ROTULO", ini, fim, "normal"|"alerta"], ...]   (o nome tem de existir em etiquetas.json)
    cta:       {"inicio": s, "perfil": "@perfil" ou ""}
    versoes:   {"IG": {"saida": "IG/01_video.mp4", "linhas": [...], "selo": "SEGUIR"}, ...}
"""
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = Path(__file__).resolve().parent
KIT = AQUI.parents[1]
sys.path.insert(0, str(KIT))

from config import CFG  # noqa: E402

FONTE = AQUI.parent / "fontes" / "Fredoka.ttf"
W, H = int(CFG["render"]["largura"]), int(CFG["render"]["altura"])
Z = CFG["zona_segura"]
CX = (Z["x0"] + Z["x1"]) / 2          # centro da zona segura (a direita é coberta pelos botões das redes)
LARG = Z["x1"] - Z["x0"]
Y_LEGENDA = Z["legenda_y_max"] - 80   # centro da palavra; a base fica acima do limite da legenda

FUNDO_CENTRO = (24, 96, 122)
FUNDO_BORDA = (8, 26, 48)
BRANCO = (255, 248, 236)
DESTAQUE = (255, 228, 94)
TINTA = (27, 21, 48)
VERMELHO = (229, 72, 77)
CORES = {"branco": BRANCO, "destaque": DESTAQUE}


def ease(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


# Fundo de cada cenário: (centro, borda, partículas). O episódio escolhe em episodio.json, campo "fundo", pelo
# assunto do vídeo: o mar é só do fundo do mar. "cores": ["#centro", "#borda"] no episódio troca as cores.
TEMAS_FUNDO = {
    "mar": ((24, 96, 122), (8, 26, 48), "plancton"),
    "ceu": ((150, 214, 255), (64, 140, 214), "nuvens"),
    "tempestade": ((92, 104, 140), (24, 28, 48), "nuvens"),
    "casa": ((255, 226, 186), (196, 140, 104), "luz"),
    "noite": ((44, 56, 118), (10, 12, 36), "estrelas"),
    "cidade": ((255, 178, 128), (92, 62, 124), "luz"),
    "espaco": ((34, 22, 70), (4, 4, 14), "estrelas"),
    "laboratorio": ((214, 240, 236), (110, 160, 170), "luz"),
    "natureza": ((196, 236, 170), (70, 140, 90), "luz"),
    "neutro": ((70, 70, 104), (20, 20, 40), "luz"),
}


def _hexa(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def fundo(tema="mar", cores=None):
    """Gradiente radial do cenário + partículas desfocadas (plâncton, nuvens, estrelas ou luz)."""
    if tema not in TEMAS_FUNDO:
        raise SystemExit(f"ERRO: fundo '{tema}' não existe.\nO QUE FAZER: use um destes em episodio.json, campo "
                         f"\"fundo\": {', '.join(TEMAS_FUNDO)}.")
    centro, borda, part = TEMAS_FUNDO[tema]
    if cores:
        centro, borda = _hexa(cores[0]), _hexa(cores[1])
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = W / 2, H * 0.55
    rmax = (cx ** 2 + (H * 0.6) ** 2) ** 0.5
    k = np.minimum(1.0, np.hypot(x - cx, y - cy) / rmax) ** 1.4
    a, b = np.array(centro, np.float32), np.array(borda, np.float32)
    img = Image.fromarray((a + (b - a) * k[..., None]).astype(np.uint8), "RGB").convert("RGBA")
    camada = Image.new("RGBA", (W, H))
    dr = ImageDraw.Draw(camada)
    rnd = np.random.default_rng(3)
    if part == "plancton":
        for _ in range(140):
            px, py, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(1.5, 4.5)
            dr.ellipse((px - r, py - r, px + r, py + r), fill=(200, 255, 245, int(rnd.integers(25, 80))))
        return Image.alpha_composite(img, camada.filter(ImageFilter.GaussianBlur(1.2)))
    if part == "estrelas":
        for _ in range(220):
            px, py, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(1.0, 3.2)
            dr.ellipse((px - r, py - r, px + r, py + r), fill=(255, 250, 230, int(rnd.integers(60, 200))))
        return Image.alpha_composite(img, camada.filter(ImageFilter.GaussianBlur(0.6)))
    if part == "nuvens":
        claro = 70 if tema == "tempestade" else 150
        for _ in range(16):
            px, py = rnd.uniform(-100, W + 100), rnd.uniform(0, H * 0.7)
            for _ in range(6):
                ox, oy, r = rnd.uniform(-120, 120), rnd.uniform(-40, 40), rnd.uniform(60, 130)
                dr.ellipse((px + ox - r, py + oy - r * 0.6, px + ox + r, py + oy + r * 0.6),
                           fill=(255, 255, 255, int(rnd.integers(claro // 3, claro))))
        return Image.alpha_composite(img, camada.filter(ImageFilter.GaussianBlur(18)))
    for _ in range(26):  # luz: bolinhas grandes e bem desfocadas (bokeh)
        px, py, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(30, 90)
        dr.ellipse((px - r, py - r, px + r, py + r), fill=(255, 255, 240, int(rnd.integers(12, 40))))
    return Image.alpha_composite(img, camada.filter(ImageFilter.GaussianBlur(14)))


_FONTES = {}


def fonte(tam):
    tam = int(tam)
    if tam not in _FONTES:
        f = ImageFont.truetype(str(FONTE), tam)
        try:
            f.set_variation_by_axes([700, 100])  # Fredoka variável: peso 700
        except OSError:
            pass
        _FONTES[tam] = f
    return _FONTES[tam]


def _cabe(dr, texto, tam, largura=LARG):
    f = fonte(tam)
    while dr.textlength(texto, font=f) > largura and tam > 24:
        tam -= 4
        f = fonte(tam)
    return f


def carimbo(dr, xy, texto, f, cor, borda=12):
    """Texto "carimbado": sombra de tinta deslocada + contorno. É a assinatura do estilo."""
    x, y = xy
    dr.text((x + 6, y + 8), texto, font=f, fill=TINTA, stroke_width=borda + 2, stroke_fill=TINTA)
    dr.text((x, y), texto, font=f, fill=cor, stroke_width=borda, stroke_fill=TINTA)


def titulo(img, linhas, topo=None, tam=118):
    """Linhas centradas na zona segura, a partir de `topo` (padrão: o topo da zona). Cor: "branco", "destaque" ou RGB."""
    dr = ImageDraw.Draw(img)
    y = Z["y0"] if topo is None else topo
    for texto, cor in linhas:
        f = _cabe(dr, texto, tam)
        carimbo(dr, (CX - dr.textlength(texto, font=f) / 2, y), texto, f, CORES.get(cor, cor), 12)
        y += int(f.size * 1.02)
    return img


def desenhar_palavra(dr, palavra, destaque, u):
    """Palavra da legenda com "pop" de entrada (escala 0,85 -> 1 em 0,1 s)."""
    f = _cabe(dr, palavra, 104 * (0.85 + 0.15 * ease(u)))
    w = dr.textlength(palavra, font=f)
    carimbo(dr, (CX - w / 2, Y_LEGENDA - f.size / 2), palavra, f, DESTAQUE if destaque else BRANCO, 10)


def desenhar_rotulo(dr, texto, ancora, u, estilo="normal"):
    """Pílula creme ligada ao ponto 3D por um traço curto, entrando em 0,2 s. "alerta" = selo vermelho grande."""
    if u <= 0:
        return
    a = int(255 * ease(u))
    ax, ay = ancora[0] * W, ancora[1] * H
    if estilo == "alerta":
        f = fonte(64)
        w = dr.textlength(texto, font=f)
        x0, y0 = CX - (w + 70) / 2, ay - 190
        dr.rounded_rectangle((x0 + 8, y0 + 10, x0 + w + 78, y0 + 110), radius=26, fill=TINTA + (a,))
        dr.rounded_rectangle((x0, y0, x0 + w + 70, y0 + 100), radius=26, fill=VERMELHO + (a,), outline=TINTA + (a,),
                             width=7)
        dr.text((x0 + 35, y0 + 10), texto, font=f, fill=BRANCO + (a,))
        return
    f = fonte(40)
    w = dr.textlength(texto, font=f) + 44
    dx = 70 - 30 * (1 - ease(u))
    px = ax + dx
    if px + w > Z["x1"]:  # sem espaço à direita da âncora: abre para a esquerda
        px = ax - dx - w
    px = max(Z["x0"], min(px, Z["x1"] - w))
    py = ay - 32
    dr.line((ax, ay, px if px > ax else px + w, py + 32), fill=TINTA + (a,), width=6)
    dr.ellipse((ax - 9, ay - 9, ax + 9, ay + 9), fill=DESTAQUE + (a,), outline=TINTA + (a,), width=4)
    dr.rounded_rectangle((px, py, px + w, py + 64), radius=32, fill=BRANCO + (a,), outline=TINTA + (a,), width=6)
    dr.text((px + 22, py + 6), texto, font=f, fill=TINTA + (a,))


def desenhar_cta(img, versao, cta, t):
    """Cartão final: escurece a cena, as linhas do CTA da rede, o @ do perfil e um selo-botão pulsando."""
    u = ease((t - cta["inicio"]) / 0.35)
    if u <= 0:
        return img
    img = Image.alpha_composite(img, Image.new("RGBA", (W, H), (8, 26, 48, int(170 * u))))
    camada = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(camada)
    y = 620
    if cta.get("perfil"):
        f = _cabe(dr, cta["perfil"], 64)
        carimbo(dr, (CX - dr.textlength(cta["perfil"], font=f) / 2, y), cta["perfil"], f, DESTAQUE, 8)
        y += int(f.size * 1.5)
    for texto, cor in versao["linhas"]:
        f = _cabe(dr, texto, 86)
        carimbo(dr, (CX - dr.textlength(texto, font=f) / 2, y), texto, f, CORES[cor], 10)
        y += int(f.size * 1.08)
    if versao.get("selo"):
        f = fonte(56)
        w = dr.textlength(versao["selo"], font=f)
        x0, y0 = CX - (w + 90) / 2, y + 40
        dx = (w + 90) * 0.04 * math.sin(2 * math.pi * 1.6 * t) / 2
        dr.rounded_rectangle((x0 - dx + 8, y0 + 10, x0 + w + 90 + dx + 8, y0 + 106), radius=48, fill=TINTA)
        dr.rounded_rectangle((x0 - dx, y0, x0 + w + 90 + dx, y0 + 96), radius=48, fill=VERMELHO, outline=TINTA,
                             width=7)
        dr.text((x0 + 45, y0 + 12), versao["selo"], font=f, fill=BRANCO)
    camada.putalpha(camada.getchannel("A").point(lambda v: int(v * u)))
    return Image.alpha_composite(img, camada)


def compor(spec_path, cpu=False):
    from maquina.motor import comando_ffmpeg, encoders_simultaneos

    spec_path = Path(spec_path).resolve()
    base = spec_path.parent
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    fps = int(CFG["render"]["fps"])
    quadros = sorted((base / spec["quadros"]).glob("q_*.png"))
    if not quadros:
        raise SystemExit(f"nenhum quadro em {base / spec['quadros']}: rode a cena no Blender antes")
    ancoras = json.loads((base / spec["etiquetas"]).read_text(encoding="utf-8")) if spec.get("etiquetas") else {}
    gancho, cta, versoes = spec.get("gancho"), spec["cta"], spec["versoes"]
    audio = base / spec["audio"] if spec.get("audio") else None
    encoders = dict(zip(versoes, encoders_simultaneos(len(versoes), cpu)))  # respeita o limite de sessões da placa
    print(f"encoders {sorted(set(encoders.values()))}, {len(quadros)} quadros, {len(versoes)} versões", flush=True)

    ffs = {}
    for rede, v in versoes.items():
        saida = base / v["saida"]
        saida.parent.mkdir(parents=True, exist_ok=True)
        ffs[rede] = subprocess.Popen(comando_ffmpeg(saida, encoders[rede], audio, spec["duracao"]), stdin=subprocess.PIPE)

    bg = fundo(spec.get("fundo", "mar"), spec.get("fundo_cores"))
    try:
        for i, q in enumerate(quadros):
            t = i / fps
            cena = Image.open(q).convert("RGBA")
            if cena.size != (W, H):  # render em escala menor (--leve): volta ao tamanho final
                cena = cena.resize((W, H), Image.LANCZOS)
            img = Image.alpha_composite(bg, cena)
            if gancho:
                alfa = 1 - ease((t - gancho["ate"]) / 0.25)
                if alfa > 0:
                    camada = titulo(Image.new("RGBA", (W, H), (0, 0, 0, 0)), gancho["linhas"])
                    if alfa < 1:
                        camada.putalpha(camada.getchannel("A").point(lambda v: int(v * alfa)))
                    img = Image.alpha_composite(img, camada)
            if t < cta["inicio"]:
                camada = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                dr = ImageDraw.Draw(camada)
                anc = ancoras.get(str(i + 1), {})
                for rotulo, t0, t1, *estilo in spec.get("rotulos", []):
                    if rotulo in anc and t0 <= t <= t1 + 0.2:
                        u = (t - t0) / 0.2 if t <= t1 else (t1 + 0.2 - t) / 0.2
                        desenhar_rotulo(dr, rotulo, anc[rotulo], u, estilo[0] if estilo else "normal")
                for t0, t1, palavra, *dest in spec.get("legenda", []):
                    if t0 <= t < t1:
                        desenhar_palavra(dr, palavra, bool(dest and dest[0]), (t - t0) / 0.1)
                bruto = Image.alpha_composite(img, camada).tobytes("raw", "BGRA")
                for ff in ffs.values():
                    ff.stdin.write(bruto)
            else:
                for rede, ff in ffs.items():
                    ff.stdin.write(desenhar_cta(img, versoes[rede], cta, t).tobytes("raw", "BGRA"))
    finally:
        for ff in ffs.values():
            ff.stdin.close()
        erros = [rede for rede, ff in ffs.items() if ff.wait() != 0]
    if erros:
        raise SystemExit(f"o ffmpeg falhou em: {', '.join(erros)}")
    for rede, v in versoes.items():
        print(f"{rede}: {base / v['saida']}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit(__doc__)
    compor(args[0], cpu="--cpu" in sys.argv)
