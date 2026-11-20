# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Gerador de identidade visual (IDV) de um canal de séries de vídeo, a partir de um marca.json.

Desenha tudo em vetor com Skia: logos (PNG transparente e SVG), foto de perfil, banner e marca d'água do YouTube,
capas de destaque do Instagram, modelos para preencher (capa de episódio, post de feed, card de parte nova, card
de resultado da votação, capa de playlist), a prancha do manual, o MANUAL_IDV.md e a prancha de conferência.

Visual dos modelos: o mesmo sistema "cartão e adesivo" da capa do episódio (`kit/maquina/capa.py`): fundo liso com
listras diagonais discretas, cartão inclinado com retícula na cor da série, mascote ou elenco como adesivo (borda
clara e sombra dura), selo redondo com o número da parte, texto alinhado à esquerda e as opções do voto como
etiquetas nas cores das opções. Fontes de cartaz (`titulo`) e de apoio (`mono`) do marca.json.

Uso:
  python gerar_idv.py tudo   --marca marca.json --saida PASTA [--cpu]
  python gerar_idv.py recortar arte_ia.png arte.png [--chave verde|magenta]
  python gerar_idv.py modelo capa|post|parte|resultado|playlist|destaque --marca marca.json --saida ARQ
         [--serie ID] [--titulo T] [--parte N] [--subtitulo S] [--pergunta P] [--linha L] [--texto X]
         [--cor #RRGGBB] [--arte PNG] [--opcoes "SIM=62" "NAO=38"] [--votos N] [--guia] [--demo] [--cpu]

Render na GPU (OpenGL por janela oculta, nada aparece na tela). `--cpu` usa o rasterizador do Skia na CPU,
para quem não tem placa de vídeo: o resultado é o mesmo, só mais lento.
"""
from __future__ import annotations

import argparse
import datetime
import json
import math
import re
import shutil
import sys
from pathlib import Path

import numpy as np
import skia

KIT_FONTES = Path(__file__).resolve().parent.parent / "fontes"

# ------------------------------------------------------------------------------------------------ medidas
# Medidas de cada peça e a fonte de onde vieram (citadas no MANUAL_IDV.md).
MEDIDAS = [
    ("Foto de perfil", "1080x1080 (exibida em círculo de 98 px no YouTube)",
     "YouTube Help: Manage your channel branding (support.google.com/youtube/answer/10456525)"),
    ("Banner do YouTube", "2560x1440; mínimo 2048x1152; área segura 1235x338 no mínimo = 1546x423 em 2560x1440",
     "YouTube Help: Manage your channel branding (support.google.com/youtube/answer/10456525)"),
    ("Marca d'água do YouTube", "150x150, quadrada, menos de 1 MB",
     "YouTube Help: Manage your channel branding (support.google.com/youtube/answer/10456525)"),
    ("Capa de playlist / miniatura", "16:9; recomendado 3840x2160; largura mínima 640; 2 MB no celular",
     "YouTube Help: Add custom thumbnails (support.google.com/youtube/answer/72431)"),
    ("Capa de Reels/TikTok/Shorts", "1080x1920 (9:16); a grade do Instagram mostra o miolo 3:4 (1080x1440)",
     "Guias de terceiros (Hopper HQ, Planoly, 2025-2026); o Instagram não publica a medida em página oficial"),
    ("Post de feed", "1080x1350 (4:5); na grade 3:4 perde ~34 px de cada lado",
     "Guias de terceiros (Hopper HQ, Planoly, 2025-2026)"),
    ("Capa de destaque", "1080x1920; o Instagram recorta um círculo no centro",
     "Prática corrente; o Instagram não publica a medida em página oficial"),
]

# ------------------------------------------------------------------------------------------------ cores


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def cor(h, a=255):
    r, g, b = rgb(h) if isinstance(h, str) else h
    return skia.ColorSetARGB(int(max(0, min(255, a))), r, g, b)


def misturar(a, b, t):
    """Cor entre a e b (t=0 dá a, t=1 dá b), em hex."""
    ra, rb = rgb(a), rgb(b)
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(ra, rb))


def luminancia(h):
    def canal(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb(h)
    return 0.2126 * canal(r) + 0.7152 * canal(g) + 0.0722 * canal(b)


def contraste(a, b):
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def tinta(c, a=255, traco=None, blur=None):
    p = skia.Paint(AntiAlias=True, Color=cor(c, a))
    if traco:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(traco)
        p.setStrokeJoin(skia.Paint.kRound_Join)
        p.setStrokeCap(skia.Paint.kRound_Cap)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


# ------------------------------------------------------------------------------------------------ limpeza de adesivo


def limpar_adesivo(caminho):
    """Conserta o defeito de recorte mais comum em arte feita por IA e recortada por remoção de fundo automática:
    buraco no alfa dentro da figura (ex.: pedaço do olho apagado). Sobre fundo escuro ele some; sobre o cartão
    colorido, aparece. Só preenche buraco fechado cuja cor escondida é clara (luminância > 70); o vão escuro entre
    braço e corpo é espaço negativo e continua vazado.
    """
    from PIL import Image
    from scipy import ndimage as nd

    a = np.array(Image.open(caminho).convert("RGBA"))
    al = a[..., 3]
    r, g, b = (a[..., i].astype(int) for i in range(3))

    lab, n = nd.label(al < 128)
    externos = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    buraco = np.zeros(al.shape, bool)
    for i in range(1, n + 1):
        if i in externos:
            continue
        m = lab == i
        if m.sum() >= 20 and lum[m].mean() > 70:
            buraco |= nd.binary_dilation(m, iterations=2) & (al < 250)
    preenchidos = int(buraco.sum())
    if preenchidos:
        # A cor guardada embaixo do alfa zero é lixo de compressão: pinta o buraco com a cor opaca mais próxima
        # e suaviza só dentro dele.
        _, (iy, ix) = nd.distance_transform_edt(buraco, return_indices=True)
        for c in range(3):
            liso = nd.uniform_filter(a[..., c][iy, ix].astype(float), 5)
            a[..., c] = np.where(buraco, liso, a[..., c]).astype(np.uint8)
        al[buraco] = 255
        print(f"  limpeza {caminho.name}: {preenchidos} px de buraco preenchidos", flush=True)
    a[..., 3] = al
    return skia.Image.fromarray(np.ascontiguousarray(a), colorType=skia.kRGBA_8888_ColorType,
                                alphaType=skia.kUnpremul_AlphaType)


def com_margem(img, caminho, px=8):
    """Margem transparente em volta do adesivo antes de escalar: sem ela, a amostragem estica o último pixel da
    borda e o contorno sai serrilhado. Avisa quando a arte encosta na borda do arquivo (recorte cortou a figura:
    a margem não recupera o que falta; corrija o arquivo de origem)."""
    a = img.toarray(colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType)
    al = a[..., 3]
    lados = {"topo": al[0], "base": al[-1], "esquerda": al[:, 0], "direita": al[:, -1]}
    cortados = [k for k, v in lados.items() if int((v > 128).sum()) > 2]
    if cortados:
        print(f"  AVISO {Path(caminho).name}: arte encosta na borda do arquivo ({', '.join(cortados)}); "
              "a figura pode estar cortada", flush=True)
    b = np.zeros((a.shape[0] + 2 * px, a.shape[1] + 2 * px, 4), np.uint8)
    b[px:-px, px:-px] = a
    return skia.Image.fromarray(b, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType)


# ------------------------------------------------------------------------------------------------ marca


class Marca:
    """Lê o marca.json e resolve caminhos relativos à pasta do próprio arquivo."""

    def __init__(self, caminho):
        caminho = Path(caminho).resolve()
        self.arquivo = caminho
        d = json.loads(caminho.read_text(encoding="utf-8"))
        self.d = d
        base = caminho.parent

        def resolve(p):
            if not p:
                return None
            p = Path(p)
            return p if p.is_absolute() else (base / p).resolve()

        self.nome = d["nome"]
        self.arroba = d["arroba"]
        self.site = d.get("site", "")
        self.slogan = d.get("slogan", "")
        self.chamada = d.get("chamada", "")
        self.banner_linhas = d.get("banner_linhas") or [self.chamada.upper()]
        # Fundo pronto do banner (arte feita em IA de imagem, sem texto): o kit escreve o nome por cima.
        self.banner_fundo = resolve(d.get("banner_fundo"))
        self.c = d["cores"]
        # Cores do voto (etiquetas e barras do placar): as mesmas opcao1/opcao2 do kit/config.json; sem elas, o
        # destaque e o acento.
        self.c.setdefault("opcao1", self.c["destaque"])
        self.c.setdefault("opcao2", self.c["acento"])

        def fonte_arq(v):
            # Caminho do marca.json; se não existir, o arquivo de mesmo nome em kit/fontes (baixar_fontes.py).
            p = resolve(v)
            if p and not p.exists() and (KIT_FONTES / p.name).exists():
                return KIT_FONTES / p.name
            return p

        self.fontes = {k: fonte_arq(v) for k, v in d["fontes"].items()}
        self.fontes.setdefault("logo", self.fontes["titulo"])
        if not self.fontes.get("logo"):
            self.fontes["logo"] = self.fontes["titulo"]
        logo = d.get("logo", {})
        self.logo_ilustrado = resolve(logo.get("ilustrado"))
        self.logo_linhas = [s.upper() for s in (logo.get("linhas") or self._linhas_auto())]
        # "inicial" (letra do nome, sem arte nenhuma) ou caminho de um PNG quadrado com o símbolo do canal.
        tipo = logo.get("icone", "inicial")
        self.icone_png = None if tipo == "inicial" else resolve(tipo)
        self.icone_tipo = "inicial" if self.icone_png is None else "png"
        self.fundo_icone = logo.get("fundo_icone") or self.c["destaque"]
        mas = d.get("mascote", {})
        self.mascote_nome = mas.get("nome", "")
        self.mascote_desc = mas.get("descricao", "")
        self.poses = {k: resolve(v) for k, v in mas.get("poses", {}).items()}
        self.pose_padrao = mas.get("pose_padrao") or (next(iter(self.poses)) if self.poses else None)
        self.series = d.get("series", [])
        self.destaques_extra = d.get("destaques_extra", [])
        self.voz = d.get("voz", [])
        self.fazer = d.get("fazer", [])
        self.nao_fazer = d.get("nao_fazer", [])
        self.paleta_doc = d.get("paleta_doc", [])
        self.tipografia_doc = d.get("tipografia_doc", [])
        self._tf, self._img = {}, {}
        for k, p in self.fontes.items():
            if p and not p.exists():
                raise SystemExit(f"ERRO: a fonte '{k}' não foi encontrada ({p}).\n"
                                 "O QUE FAZER: rode `python baixar_fontes.py` a partir de kit/ ou corrija o caminho "
                                 "em fontes no marca.json.")

    def _linhas_auto(self):
        p = self.nome.split()
        return [p[0], " ".join(p[1:])] if len(p) > 1 else p

    def fonte(self, tipo, tam):
        p = self.fontes[tipo]
        if p not in self._tf:
            self._tf[p] = skia.Typeface.MakeFromFile(str(p))
        f = skia.Font(self._tf[p], tam)
        f.setEdging(skia.Font.Edging.kAntiAlias)
        f.setSubpixel(True)
        return f

    def imagem(self, caminho, adesivo=False):
        """Carrega uma imagem. adesivo=True (logo ilustrado e poses) passa pela limpeza de recorte quando o
        marca.json pede ("limpar_adesivos": true); arte de episódio (--arte) nunca é alterada."""
        if caminho is None:
            return None
        caminho = Path(caminho)
        chave = (caminho, adesivo)
        if chave not in self._img:
            if not caminho.exists():
                raise SystemExit(f"Imagem não encontrada: {caminho}")
            if adesivo and self.d.get("limpar_adesivos"):
                img = limpar_adesivo(caminho)
            else:
                img = skia.Image.open(str(caminho))
            self._img[chave] = com_margem(img, caminho) if adesivo else img
        return self._img[chave]

    def pose(self, nome):
        if not nome:
            nome = self.pose_padrao
        if nome and nome in self.poses:
            return self.imagem(self.poses[nome], adesivo=True)
        if nome and Path(nome).suffix:
            return self.imagem(nome)
        return None

    def logo_img(self):
        return self.imagem(self.logo_ilustrado, adesivo=True)

    def serie(self, sid):
        for s in self.series:
            if s["id"] == sid:
                return s
        raise SystemExit(f"Série '{sid}' não está no marca.json")


# ------------------------------------------------------------------------------------------------ render


class Render:
    """Superfícies Skia na GPU (contexto OpenGL de uma janela oculta) ou na CPU com --cpu."""

    def __init__(self, gpu=True):
        self.ctx = None
        self.janela = None
        if gpu:
            try:
                import glfw
            except ImportError as e:
                raise SystemExit("GPU pedida, mas o pacote glfw não está instalado. Instale ou rode com --cpu.") from e
            if not glfw.init():
                raise SystemExit("glfw.init falhou: sem OpenGL. Rode com --cpu.")
            glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
            self.janela = glfw.create_window(64, 64, "idv", None, None)
            if not self.janela:
                raise SystemExit("Não deu para criar o contexto OpenGL oculto. Rode com --cpu.")
            glfw.make_context_current(self.janela)
            self.ctx = skia.GrDirectContext.MakeGL()
            if self.ctx is None:
                raise SystemExit("Skia não abriu o contexto GL. Rode com --cpu.")
        self.modo = "GPU (OpenGL)" if self.ctx else "CPU"

    def tela(self, w, h):
        info = skia.ImageInfo.MakeN32Premul(int(w), int(h))
        if self.ctx:
            s = skia.Surface.MakeRenderTarget(self.ctx, skia.Budgeted.kNo, info)
            if s is None:
                raise SystemExit(f"Sem superfície GPU {w}x{h}")
        else:
            s = skia.Surface.MakeRaster(info)
        s.getCanvas().clear(skia.ColorTRANSPARENT)
        return s

    def imagem(self, surf):
        if self.ctx:
            self.ctx.flushAndSubmit()
        w, h = surf.width(), surf.height()
        arr = np.zeros((h, w, 4), np.uint8)
        info = skia.ImageInfo.Make(w, h, skia.kRGBA_8888_ColorType, skia.kUnpremul_AlphaType)
        if not surf.readPixels(info, arr, w * 4, 0, 0):
            raise SystemExit("Falha ao ler os pixels da superfície")
        return skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType)

    def salvar(self, surf, caminho, qualidade=92, max_bytes=None):
        caminho = Path(caminho)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        img = self.imagem(surf)
        if caminho.suffix.lower() in (".jpg", ".jpeg"):
            q = qualidade
            while True:
                dados = bytes(img.encodeToData(skia.EncodedImageFormat.kJPEG, q))
                if not max_bytes or len(dados) <= max_bytes or q <= 60:
                    break
                q -= 4
        else:
            dados = bytes(img.encodeToData(skia.EncodedImageFormat.kPNG, 100))
        caminho.write_bytes(dados)
        print(f"  {caminho.name}  {surf.width()}x{surf.height()}  {len(dados) // 1024} KB", flush=True)
        return img

    def fechar(self):
        if self.janela is not None:
            import glfw
            self.ctx.abandonContext()
            glfw.destroy_window(self.janela)
            glfw.terminate()


def svg(caminho, w, h, desenho):
    """Roda a mesma função de desenho num SVGCanvas (texto já vira curva; sem desfoque nem gradiente de efeito)."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    stream = skia.FILEWStream(str(caminho))
    cv = skia.SVGCanvas.Make(skia.Rect(w, h), stream, skia.SVGCanvas.kConvertTextToPaths_Flag)
    desenho(cv)
    del cv
    stream.flush()
    del stream
    print(f"  {caminho.name}  (vetor {int(w)}x{int(h)})", flush=True)


# ------------------------------------------------------------------------------------------------ texto


def texto_path(font, s, x=0.0, y=0.0, tracking=0.0):
    """Texto como curva (serve para traço, brilho e SVG). Retorna (path, largura)."""
    glifos = font.textToGlyphs(s)
    larguras = font.getWidths(glifos)
    p = skia.Path()
    cx = x
    for g, w in zip(glifos, larguras):
        gp = font.getPath(g)
        if gp is not None and not gp.isEmpty():
            q = skia.Path(gp)
            q.offset(cx, y)
            # União booleana: contornos sobrepostos (dentro do glifo ou entre letras coladas) não abrem buraco
            # no preenchimento nem desenham traço interno no contorno.
            p = skia.Op(p, q, skia.PathOp.kUnion_PathOp) if not p.isEmpty() else q
        cx += w + tracking
    largura = cx - x - (tracking if len(glifos) else 0)
    return p, largura


def largura_txt(font, s, tracking=0.0):
    return texto_path(font, s, 0, 0, tracking)[1]


def escrever(cv, s, x, y, font, c, alinhar="c", tracking=0.0, contorno=(), brilho=None, sombra=None, a=255,
             dura=None):
    """Escreve `s` com a linha de base em y. contorno = [(cor, espessura), ...] de fora para dentro.
    brilho = (cor, sigma, alfa). sombra = (dy, sigma, alfa). dura = (cor, dx, dy): sombra sem desfoque, a do
    sistema "cartão e adesivo". Retorna o retângulo ocupado."""
    p, w = texto_path(font, s, 0, 0, tracking)
    dx = x - w / 2 if alinhar == "c" else (x - w if alinhar == "d" else x)
    p.offset(dx, y)
    if dura:
        q = skia.Path(p)
        q.offset(dura[1], dura[2])
        cv.drawPath(q, tinta(dura[0], a))
    if sombra:
        dy, sg, al = sombra
        q = skia.Path(p)
        q.offset(0, dy)
        cv.drawPath(q, tinta("#000000", al, blur=sg))
    if brilho:
        bc, sg, al = brilho
        cv.drawPath(p, tinta(bc, al, blur=sg))
    for cc, esp in contorno:
        cv.drawPath(p, tinta(cc, a, traco=esp * 2))
    cv.drawPath(p, tinta(c, a))
    return p.computeTightBounds()


def caber(m, tipo, s, tam, larg, tracking_em=0.0, minimo=12):
    while tam > minimo:
        f = m.fonte(tipo, tam)
        if largura_txt(f, s, tracking_em * tam) <= larg:
            return f
        tam *= 0.97
    return m.fonte(tipo, minimo)


def titulo_linhas(m, s, larg, tam_max, tam_min, tipo="titulo"):
    """Uma linha se couber grande; senão quebra em duas linhas equilibradas."""
    f = caber(m, tipo, s, tam_max, larg)
    if f.getSize() >= tam_min or " " not in s:
        return [s], f
    pal = s.split()
    f100 = m.fonte(tipo, 100)
    melhor = min(range(1, len(pal)), key=lambda i: max(largura_txt(f100, " ".join(pal[:i])),
                                                       largura_txt(f100, " ".join(pal[i:]))))
    linhas = [" ".join(pal[:melhor]), " ".join(pal[melhor:])]
    maior = max(linhas, key=lambda l: largura_txt(f100, l))
    return linhas, caber(m, tipo, maior, tam_max, larg)


def quebrar(font, s, larg):
    linhas, atual = [], ""
    for p in s.split():
        t = f"{atual} {p}".strip()
        if largura_txt(font, t) <= larg or not atual:
            atual = t
        else:
            linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas


def altura_caixa(font):
    """Altura de maiúscula da fonte (H), para centralizar texto na vertical."""
    return texto_path(font, "H")[0].computeTightBounds().height()


def tinta_sobre(fundo, m):
    """Cor de texto legível sobre `fundo`: escuro em fundo claro, claro em fundo escuro."""
    return m.c["fundo"] if contraste(fundo, m.c["fundo"]) > contraste(fundo, "#FFFFFF") else "#FFFFFF"


def etiqueta(cv, m, x, y, s, fundo, font, alt, pad=34, raio=20):
    """Etiqueta do voto: retângulo arredondado na cor `fundo` com sombra dura curta e o texto centrado na altura.
    Retorna a largura."""
    w = largura_txt(font, s) + 2 * pad
    cv.drawRoundRect(skia.Rect(x + 8, y + 10, x + w + 8, y + alt + 10), raio, raio, tinta(paleta(m)["sombra"]))
    cv.drawRoundRect(skia.Rect(x, y, x + w, y + alt), raio, raio, tinta(fundo))
    escrever(cv, s, x + pad, y + (alt + altura_caixa(font)) / 2, font, tinta_sobre(fundo, m), "e")
    return w


# ------------------------------------------------------------------------------------------------ cartão e adesivo
# O mesmo sistema da capa do episódio (kit/maquina/capa.py): fundo liso com listras, cartão inclinado com retícula,
# arte como adesivo, selo da parte e etiquetas do voto. Sem raio, brilho nem pílula.

SOMBRA_DURA = (14, 18)      # deslocamento da sombra sem desfoque (adesivo, cartão, selo)
BORDA_ADESIVO = 14          # px da borda clara em volta do adesivo
X0, LARG = 88, 904          # coluna de texto das peças 9:16, alinhada à esquerda


def paleta(m):
    c = m.c
    return dict(fundo=c["fundo"], texto=c["texto"], destaque=c["destaque"], op1=c["opcao1"], op2=c["opcao2"],
                suave=misturar(c["texto"], c["fundo"], 0.32), sombra=misturar(c["fundo"], "#000000", 0.55),
                trilho=c.get("painel2") or misturar(c["fundo"], c["texto"], 0.12))


def claro(ac):
    """Tom claro da cor da série: rótulo em versal acima do título (nome da parte, kicker)."""
    return misturar(ac, "#FFFFFF", 0.45)


def topo_base(font):
    """Distância do topo da maiúscula até a linha de base: escreve com o topo do texto em y."""
    return altura_caixa(font)


def fundo_liso(cv, m, w, h, ac, pe=True):
    """Fundo liso na cor de fundo com listras diagonais discretas na cor da série. `pe` escurece a base (área da
    legenda do app nas peças 9:16)."""
    f = m.c["fundo"]
    cv.drawRect(skia.Rect(w, h), tinta(f))
    listras = skia.Path()
    passo, grossura, incl = 64, 20, h * 0.55
    for k in range(-int(incl // passo) - 2, int(w // passo) + 2):
        x = k * passo
        listras.moveTo(x, 0)
        listras.lineTo(x + grossura, 0)
        listras.lineTo(x + grossura - incl, h)
        listras.lineTo(x - incl, h)
        listras.close()
    cv.drawPath(listras, tinta(misturar(f, ac, 0.07)))
    if pe:
        y0, s = h * 0.73, paleta(m)["sombra"]
        sh = skia.GradientShader.MakeLinear([(0, y0), (0, h)], [cor(s, 0), cor(s, 200)])
        cv.drawRect(skia.Rect(0, y0, w, h), skia.Paint(Shader=sh))


def cartao(cv, m, r, ac, angulo=-3.0, raio=56, circulo=False):
    """Cartão inclinado na cor da série: degradê, retícula de pontos que crescem para o canto de baixo à direita e
    sombra dura. `circulo` faz o disco (capa de destaque)."""
    f = m.c["fundo"]
    sx, sy = SOMBRA_DURA

    def forma(rr):
        p = skia.Path()
        if circulo:
            p.addOval(rr)
        else:
            p.addRoundRect(rr, raio, raio)
        return p

    cv.save()
    cv.rotate(angulo, r.centerX(), r.centerY())
    cv.drawPath(forma(r.makeOffset(sx, sy)), tinta(paleta(m)["sombra"], 230))
    sh = skia.GradientShader.MakeLinear([(0, r.top()), (0, r.bottom())],
                                        [cor(misturar(f, ac, 0.55)), cor(misturar(f, ac, 0.30))])
    corpo = forma(r)
    cv.drawPath(corpo, skia.Paint(AntiAlias=True, Shader=sh))
    cv.clipPath(corpo, doAntiAlias=True)
    pontos = skia.Path()
    passo = 30
    gy = r.top()
    while gy < r.bottom():
        gx = r.left()
        while gx < r.right():
            t = ((gx - r.left()) / r.width() + (gy - r.top()) / r.height()) / 2
            if t > 0.35:
                pontos.addCircle(gx, gy, 1.0 + 6.5 * (t - 0.35) / 0.65)
            gx += passo
        gy += passo
    cv.drawPath(pontos, tinta(misturar(f, ac, 0.72)))
    cv.restore()


_ADESIVOS = {}


def adesivo(cv, m, img, x, y, w, h, alinhar="base", sombra=True):
    """Cola a arte como adesivo (borda clara e sombra dura), encaixada sem distorcer na caixa (x, y, w, h); a borda
    e a sombra ficam por fora da caixa. A borda é feita em pixel na escala real da tela (nítida também na capa 4K).
    Retorna o retângulo da figura."""
    from PIL import Image, ImageFilter

    esc = abs(cv.getTotalMatrix().getScaleX()) or 1.0
    iw, ih = img.width(), img.height()
    s = min(w / iw, h / ih)
    dw, dh = iw * s, ih * s
    dx = x + (w - dw) / 2
    dy = {"base": y + h - dh, "centro": y + (h - dh) / 2, "topo": y}[alinhar]
    pw, ph = max(1, round(dw * esc)), max(1, round(dh * esc))
    chave = (id(img), pw, ph, sombra)
    if chave not in _ADESIVOS:
        a = img.toarray(colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType)
        arte = Image.fromarray(a, "RGBA").resize((pw, ph), Image.LANCZOS)
        B = max(1, round(BORDA_ADESIVO * esc))
        ox, oy = (round(v * esc) for v in SOMBRA_DURA)
        M = B + 4
        alfa = Image.new("L", (pw + 2 * M, ph + 2 * M), 0)
        alfa.paste(arte.getchannel("A"), (M, M))
        anel = alfa
        for _ in range(B // 2):
            anel = anel.filter(ImageFilter.MaxFilter(5))
        if B % 2:
            anel = anel.filter(ImageFilter.MaxFilter(3))
        anel = anel.filter(ImageFilter.GaussianBlur(1.2 * esc))
        saida = Image.new("RGBA", (alfa.width + ox, alfa.height + oy), (0, 0, 0, 0))
        if sombra:
            camada = Image.new("RGBA", alfa.size, (*rgb(paleta(m)["sombra"]), 0))
            camada.putalpha(anel.point(lambda v: int(v * 0.85)))
            saida.alpha_composite(camada, (ox, oy))
        camada = Image.new("RGBA", alfa.size, (*rgb(m.c["texto"]), 0))
        camada.putalpha(anel)
        saida.alpha_composite(camada, (0, 0))
        saida.alpha_composite(arte, (M, M))
        arr = np.ascontiguousarray(np.array(saida))
        _ADESIVOS[chave] = (skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType,
                                                 alphaType=skia.kUnpremul_AlphaType), M / esc)
    sk, M = _ADESIVOS[chave]
    cv.drawImageRect(sk, skia.Rect(dx - M, dy - M, dx - M + sk.width() / esc, dy - M + sk.height() / esc),
                     skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kNone), skia.Paint(AntiAlias=True))
    return skia.Rect(dx, dy, dx + dw, dy + dh)


def arte_ou_icone(cv, m, arte_img, caixa, cart, alinhar="base"):
    """Arte como adesivo na caixa; sem arte (canal ainda sem mascote), o ícone do canal no meio do cartão, para o
    cartão não ficar vazio."""
    if arte_img is not None:
        return adesivo(cv, m, arte_img, *caixa, alinhar)
    S = min(cart.width(), cart.height()) * 0.56
    desenhar_icone(cv, m, cart.centerX() - S / 2, cart.centerY() - S / 2, S)
    return None


def selo(cv, m, cx, cy, numero, raio=96, angulo=-8.0):
    """Selo redondo com 'PARTE' e o número grande, levemente girado."""
    p = paleta(m)
    k = raio / 96
    cv.save()
    cv.rotate(angulo, cx, cy)
    cv.drawCircle(cx + SOMBRA_DURA[0] * 0.7, cy + SOMBRA_DURA[1] * 0.7, raio, tinta(p["sombra"], 235))
    cv.drawCircle(cx, cy, raio, tinta(p["texto"]))
    fa = m.fonte("mono", 26 * k)
    escrever(cv, "PARTE", cx, cy - raio * 0.62 + topo_base(fa), fa, p["fundo"], "c", 0.18 * fa.getSize())
    fn = caber(m, "titulo", str(numero), 104 * k, raio * 1.5)
    escrever(cv, str(numero), cx, cy - raio * 0.22 + topo_base(fn), fn, p["fundo"])
    cv.restore()


def etiquetas(cv, m, x, y, op1, op2, larg_max, alt=112, medir=False):
    """As duas opções do voto como etiquetas nas cores das opções, com 'ou' entre elas: numa linha se couberem com
    corpo legível (>= 44 px), senão uma embaixo da outra. Devolve a altura usada; com `medir`, só mede."""
    p = paleta(m)
    fo = m.fonte("mono", 40)
    meio = "ou"
    w_meio = fo.measureText(meio) + 36
    pad = 34

    def corpo(textos, larg):
        tam = 64
        while tam > 30 and sum(m.fonte("titulo", tam).measureText(t) + 2 * pad for t in textos) > larg:
            tam -= 2
        return tam

    tam = corpo((op1, op2), larg_max - w_meio)
    linhas = [[(op1, p["op1"]), (op2, p["op2"])]]
    if tam < 44:
        tam = min(corpo((op1,), larg_max), corpo((op2,), larg_max - w_meio))
        linhas = [[(op1, p["op1"])], [(op2, p["op2"])]]
    f = m.fonte("titulo", tam)
    alt = min(alt, int(tam * 1.75))
    total = len(linhas) * (alt + 10) + (len(linhas) - 1) * 12
    if medir:
        return total
    xo = texto_path(fo, "o")[0].computeTightBounds().height()
    yy = y
    for k, linha in enumerate(linhas):
        cx = x
        if k == 1:      # na segunda linha, o "ou" abre a linha
            escrever(cv, meio, cx, yy + (alt + xo) / 2, fo, p["texto"], "e")
            cx += w_meio - 18
        for i, (texto, c) in enumerate(linha):
            cx += etiqueta(cv, m, cx, yy, texto, c, f, alt, pad)
            if i == 0 and len(linha) == 2:
                escrever(cv, meio, cx + 18, yy + (alt + xo) / 2, fo, p["texto"], "e")
                cx += w_meio
        yy += alt + 10 + 12
    return total


def quebra(m, texto, tam_max, larg, alt_max, max_linhas=3, tipo="titulo"):
    """Uma linha se couber grande; senão 2 ou 3, quebradas onde as linhas ficam mais parecidas. Devolve
    (linhas, fonte). Mais uma linha só entra se o corpo crescer de verdade (12%)."""
    palavras = texto.split()
    ref = m.fonte(tipo, 100)

    def equilibrada(n):
        melhor, pior_melhor = None, None
        cortes = [()]
        for _ in range(n - 1):
            cortes = [c + (k,) for c in cortes for k in range((c[-1] if c else 0) + 1, len(palavras))]
        for c in cortes:
            lim = (0, *c, len(palavras))
            linhas = [" ".join(palavras[lim[i]:lim[i + 1]]) for i in range(n)]
            pior = max(ref.measureText(l) for l in linhas)
            if pior_melhor is None or pior < pior_melhor:
                melhor, pior_melhor = linhas, pior
        return melhor

    opcoes = [[texto]] + [equilibrada(n) for n in range(2, min(max_linhas, len(palavras)) + 1)]
    escolha = None
    for linhas in opcoes:
        tam = tam_max
        while tam > 40:
            f = m.fonte(tipo, tam)
            if all(f.measureText(l) <= larg for l in linhas) and len(linhas) * tam <= alt_max:
                break
            tam -= 2
        if escolha is None or tam > escolha[1].getSize() * 1.12:
            escolha = (linhas, m.fonte(tipo, tam))
    return escolha


def escrever_titulo(cv, m, linhas, f, x, y, cor_txt=None, sombra_dy=8):
    """Linhas do título com o topo em y, sombra dura para baixo. Devolve o y depois da última linha."""
    p = paleta(m)
    for l in linhas:
        escrever(cv, l, x, y + topo_base(f), f, cor_txt or p["texto"], "e", dura=(p["sombra"], 0, sombra_dy))
        y += f.getSize()
    return y


def opcoes_do_voto(pergunta):
    """'ENTRAR OU FUGIR?' -> ('ENTRAR', 'FUGIR'); None se a pergunta não tiver esse formato."""
    r = re.match(r"^\s*(.+?)\s+OU\s+(.+?)\s*\??\s*$", pergunta or "", re.I)
    return (r.group(1).strip(), r.group(2).strip()) if r else None


def desenhar_imagem(cv, img, x, y, w, h, alinhar="base", sombra=True):
    """Encaixa a imagem na caixa sem distorcer (escala uniforme). alinhar: base | centro | topo."""
    iw, ih = img.width(), img.height()
    s = min(w / iw, h / ih)
    dw, dh = iw * s, ih * s
    dx = x + (w - dw) / 2
    dy = {"base": y + h - dh, "centro": y + (h - dh) / 2, "topo": y}[alinhar]
    p = skia.Paint(AntiAlias=True)
    if sombra:
        p.setImageFilter(skia.ImageFilters.DropShadow(0, 0.035 * dh, 0.03 * dh, 0.03 * dh, cor("#000000", 115)))
    amostra = skia.SamplingOptions(skia.CubicResampler.Mitchell()) if s > 1 else \
        skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)
    cv.drawImageRect(img, skia.Rect(dx, dy, dx + dw, dy + dh), amostra, p)
    return skia.Rect(dx, dy, dx + dw, dy + dh)


# ------------------------------------------------------------------------------------------------ símbolo


def _fundo_icone(m):
    return m.fundo_icone


def _inicial_path(m, x, y, S):
    """Símbolo genérico 'inicial': primeira letra do nome, centralizada num quadrado de lado S."""
    letra = m.nome.strip()[0].upper()
    p, w = texto_path(m.fonte("logo", S * 0.72), letra)
    b = p.computeTightBounds()
    p.offset(x + (S - b.width()) / 2 - b.left(), y + (S - b.height()) / 2 - b.top())
    return p


def icone_mono_path(m, x, y, S):
    """Símbolo em uma cor como curva (serve para PNG e SVG). None quando o símbolo é um PNG do cliente."""
    if m.icone_tipo == "inicial":
        quad = skia.Path()
        quad.addRoundRect(skia.Rect(x, y, x + S, y + S), 0.156 * S, 0.156 * S)
        return skia.Op(quad, _inicial_path(m, x, y, S), skia.PathOp.kDifference_PathOp)
    return None


def desenhar_icone_mono(cv, m, x, y, S, c):
    p = icone_mono_path(m, x, y, S)
    if p is not None:
        cv.drawPath(p, tinta(c))
        return
    # Ícone em PNG: silhueta tingida na cor pedida (no SVG ela sai como imagem embutida, não como vetor).
    paint = skia.Paint(AntiAlias=True, ColorFilter=skia.ColorFilters.Blend(cor(c), skia.BlendMode.kSrcIn))
    img = m.imagem(m.icone_png)
    bx, by, bw, bh, alinhar = _caixa_icone(img, x, y, S, False)
    s = min(bw / img.width(), bh / img.height())
    w, h = img.width() * s, img.height() * s
    top = by + bh - h if alinhar == "base" else by + (bh - h) / 2
    cv.drawImageRect(img, skia.Rect(bx + (bw - w) / 2, top, bx + (bw + w) / 2, top + h),
                     skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear), paint)


def _busto(img):
    """Arte de busto: a base vem cortada reta (opaca na última linha). Ela encosta no pé do quadro, não flutua."""
    al = img.toarray(colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType)[..., 3]
    return float((al[-1] > 128).mean()) > 0.25


def _caixa_icone(img, x, y, S, com_fundo):
    """Caixa do símbolo em PNG dentro do quadrado de lado S: centrado com folga, ou encostado na base se for busto."""
    if _busto(img):
        return x + 0.06 * S, y + 0.1 * S, 0.88 * S, 0.9 * S, "base"
    k = 0.1 if com_fundo else 0.0
    return x + k * S, y + k * S, (1 - 2 * k) * S, (1 - 2 * k) * S, "centro"


def desenhar_icone(cv, m, x, y, S, efeitos=True, com_fundo=True):
    """Símbolo da marca: 'inicial' (letra) ou PNG do cliente."""
    raio = 0.156 * S
    if com_fundo:
        cv.drawRoundRect(skia.Rect(x, y, x + S, y + S), raio, raio, tinta(_fundo_icone(m)))
    if m.icone_tipo == "inicial":
        cv.drawPath(_inicial_path(m, x, y, S), tinta(tinta_sobre(_fundo_icone(m), m) if com_fundo else _fundo_icone(m)))
    else:
        img = m.imagem(m.icone_png)
        bx, by, bw, bh, alinhar = _caixa_icone(img, x, y, S, com_fundo)
        cv.save()
        if com_fundo:
            cv.clipRRect(skia.RRect.MakeRectXY(skia.Rect(x, y, x + S, y + S), raio, raio), doAntiAlias=True)
        desenhar_imagem(cv, img, bx, by, bw, bh, alinhar, False)
        cv.restore()


# ------------------------------------------------------------------------------------------------ logotipo


def wordmark_path(m, altura):
    """Nome da marca em linhas de mesma largura (a linha curta cresce), empilhadas pela caixa real dos glifos."""
    f100 = m.fonte("logo", 100)
    ws = [largura_txt(f100, l) for l in m.logo_linhas]
    alvo = max(ws)
    partes, y = [], 0.0
    gap = 9.0
    for l, w in zip(m.logo_linhas, ws):
        p, _ = texto_path(m.fonte("logo", 100 * alvo / w), l)
        b = p.computeTightBounds()
        p.offset(-b.left(), y - b.top())
        partes.append(p)
        y += b.height() + gap
    total = skia.Path()
    for p in partes:
        total.addPath(p)
    b = total.computeTightBounds()
    k = altura / b.height()
    total.transform(skia.Matrix.Scale(k, k))
    b = total.computeTightBounds()
    total.offset(-b.left(), -b.top())
    return total, b.width(), b.height()


def lockup_medidas(m, S):
    _, ww, _ = wordmark_path(m, S)
    gap = 0.17 * S
    return S + gap + ww, S, gap


def desenhar_lockup(cv, m, x, y, S, modo="cor", cor_mono=None, efeitos=True):
    """Símbolo + nome. modo 'cor': nome na cor de destaque com contorno escuro; 'mono': uma cor só."""
    wm, ww, wh = wordmark_path(m, S)
    _, _, gap = lockup_medidas(m, S)
    wm.offset(x + S + gap, y)
    if modo == "mono":
        desenhar_icone_mono(cv, m, x, y, S, cor_mono)
        cv.drawPath(wm, tinta(cor_mono))
        return
    # Só contorno escuro. Borda branca de adesivo feita por traço vaza para dentro da boca aberta das letras
    # (o E, por exemplo); a borda de adesivo fica para o logo ilustrado.
    cv.drawPath(wm, tinta(m.c["contorno"], traco=2 * 0.03 * S))
    desenhar_icone(cv, m, x, y, S, efeitos)
    if efeitos:
        topo, base = wm.computeTightBounds().top(), wm.computeTightBounds().bottom()
        d = m.c["destaque"]
        sh = skia.GradientShader.MakeLinear([(0, topo), (0, base)], [cor(misturar(d, "#FFFFFF", 0.25)), cor(d),
                                                                     cor(misturar(d, "#000000", 0.1))], [0.0, 0.45, 1.0])
        cv.drawPath(wm, skia.Paint(AntiAlias=True, Shader=sh))
    else:
        cv.drawPath(wm, tinta(m.c["destaque"]))


# ------------------------------------------------------------------------------------------------ peças fixas


def gerar_logos(r, m, pasta):
    print("logo/", flush=True)
    pasta = Path(pasta)
    if m.logo_ilustrado:
        img = m.logo_img()
        pad = int(0.06 * img.width())
        s = r.tela(img.width() + 2 * pad, img.height() + 2 * pad)
        s.getCanvas().drawImage(img, pad, pad)
        r.salvar(s, pasta / "logo_principal_ilustrado.png")
    S = 600
    lw, lh, _ = lockup_medidas(m, S)
    pad = 0.12 * S
    W, H = lw + 2 * pad, lh + 2 * pad
    for nome, modo, c in (("logo_principal_vetor", "cor", None), ("logo_mono_branco", "mono", "#FFFFFF"),
                          ("logo_mono_preto", "mono", m.c["fundo"])):
        s = r.tela(W, H)
        desenhar_lockup(s.getCanvas(), m, pad, pad, S, modo, c)
        r.salvar(s, pasta / f"{nome}.png")
        svg(pasta / f"{nome}.svg", W, H, lambda cv, modo=modo, c=c: desenhar_lockup(cv, m, pad, pad, S, modo, c, False))
    for lado in (1024, 512):
        s = r.tela(lado, lado)
        desenhar_icone(s.getCanvas(), m, 0, 0, lado)
        r.salvar(s, pasta / f"icone_quadrado_{lado}.png")
    svg(pasta / "icone_quadrado.svg", 1024, 1024, lambda cv: desenhar_icone(cv, m, 0, 0, 1024, False))
    s = r.tela(1024, 1024)
    desenhar_icone(s.getCanvas(), m, 0, 0, 1024, com_fundo=False)
    r.salvar(s, pasta / "icone_simbolo_transparente.png")
    svg(pasta / "icone_simbolo_transparente.svg", 1024, 1024,
        lambda cv: desenhar_icone(cv, m, 0, 0, 1024, False, com_fundo=False))
    for nome, c in (("icone_mono_branco", "#FFFFFF"), ("icone_mono_preto", m.c["fundo"])):
        s = r.tela(1024, 1024)
        desenhar_icone_mono(s.getCanvas(), m, 0, 0, 1024, c)
        r.salvar(s, pasta / f"{nome}.png")
        svg(pasta / f"{nome}.svg", 1024, 1024, lambda cv, c=c: desenhar_icone_mono(cv, m, 0, 0, 1024, c))


def perfil(cv, m, S=1080):
    """Foto de perfil: símbolo em tela cheia, dimensionado para o recorte em círculo. Arte de busto (base cortada
    reta) sai encostada no pé do quadro e maior: o círculo do app faz o resto."""
    cv.drawRect(skia.Rect(S, S), tinta(_fundo_icone(m)))
    if m.icone_tipo == "inicial":
        cv.drawPath(_inicial_path(m, 0.18 * S, 0.18 * S, 0.64 * S), tinta(tinta_sobre(_fundo_icone(m), m)))
        return
    img = m.imagem(m.icone_png)
    if _busto(img):
        desenhar_imagem(cv, img, 0.07 * S, 0.16 * S, 0.86 * S, 0.84 * S, "base", False)
        return
    desenhar_icone(cv, m, 0.18 * S, 0.18 * S, 0.64 * S, com_fundo=False)


def _cabecalho(cv, m, y, S=84):
    """Ícone e @ no alto dos stories (abaixo da barra do app)."""
    desenhar_icone(cv, m, X0, y, S)
    f = m.fonte("mono", 36)
    escrever(cv, m.arroba, X0 + S + 24, y + (S + altura_caixa(f)) / 2, f, m.c["texto"], "e", 0.04 * 36)


def banner(cv, m, guia=False):
    W, H = 2560, 1440
    p = paleta(m)
    sx0, sy0, sx1, sy1 = (W - 1546) / 2, (H - 423) / 2, (W + 1546) / 2, (H + 423) / 2
    if m.banner_fundo:
        # Arte pronta cobrindo o quadro; uma faixa escura atrás da área segura garante a leitura do nome.
        fundo = m.imagem(m.banner_fundo)
        k = max(W / fundo.width(), H / fundo.height())
        fw, fh = fundo.width() * k, fundo.height() * k
        cv.drawImageRect(fundo, skia.Rect((W - fw) / 2, (H - fh) / 2, (W + fw) / 2, (H + fh) / 2),
                         skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint(AntiAlias=True))
        cv.drawRoundRect(skia.Rect(sx0 + 8, sy0 + 8, sx1 - 8, sy1 - 8), 36, 36, tinta(m.c["fundo"], 175))
    else:
        fundo_liso(cv, m, W, H, m.c["acento"], pe=False)
    # Mascote nas laterais: aparece no desktop (faixa 2560x423) e na TV; no celular fica de fora sem perder nada.
    lados = [q for q in (m.d.get("banner_poses") or []) if m.pose(q)]
    if len(lados) >= 2 and not m.banner_fundo:
        for i, (x, ang, c) in enumerate(((120, -4.0, m.c["destaque"]), (W - 480, 4.0, m.c["acento"]))):
            cartao(cv, m, skia.Rect(x, sy0 + 70, x + 360, sy1 + 10), c, ang, raio=40)
            adesivo(cv, m, m.pose(lados[i]), x - 20, sy0 - 50, 400, sy1 + 30 - (sy0 - 50))
    # Tudo empilhado e centrado dentro da área segura do celular (1546x423): logo, a chamada numa linha só (a
    # primeira parte na cor de destaque) e o @. Assim a chamada sai grande, sem espremer ao lado do logo.
    larg = 1546 - 80
    chamada = [l for l in m.banner_linhas if l]
    f1 = caber(m, "titulo", "  ".join(chamada), 66, larg)
    hc = altura_caixa(f1)
    arroba = f"{m.arroba}  ·  {m.site}" if m.site else m.arroba
    fm = caber(m, "mono", arroba, 36, larg, 0.06)
    hm = altura_caixa(fm)
    S = 423 - 2 * 24 - hc - 34 - hm - 30
    if m.logo_ilustrado:
        img = m.logo_img()
        lw, lh = S * img.width() / img.height(), S
    else:
        lw = lockup_medidas(m, S)[0]
        if lw > larg:
            S *= larg / lw
            lw = larg
        lh = S
    bloco = lh + 34 + hc + 30 + hm
    y = (H - bloco) / 2
    if m.logo_ilustrado:
        adesivo(cv, m, img, (W - lw) / 2, y, lw, lh, "centro")
    else:
        desenhar_lockup(cv, m, (W - lw) / 2, y, S)
    y += lh + 34 + hc
    ws = [largura_txt(f1, l) for l in chamada]
    espaco = f1.measureText("  ")
    x = (W - sum(ws) - espaco * (len(ws) - 1)) / 2
    for i, (l, w) in enumerate(zip(chamada, ws)):
        escrever(cv, l, x, y, f1, m.c["destaque"] if i == 0 else p["texto"], "e", dura=(p["sombra"], 0, 6))
        x += w + espaco
    escrever(cv, arroba, W / 2, y + 30 + hm, fm, p["suave"], "c", 0.06 * fm.getSize())
    if guia:
        _guia_banner(cv, m, W, H)


def _guia_banner(cv, m, W, H):
    zonas = [("TV: 2560x1440", 2560, 1440, "#FFFFFF"), ("Desktop: 2560x423", 2560, 423, m.c.get("ok", "#4CD38C")),
             ("Tablet: 1855x423", 1855, 423, m.c["acento"]), ("Área segura (celular): 1546x423", 1546, 423, m.c["destaque"])]
    f = m.fonte("mono", 30)
    for i, (rot, w, h, c) in enumerate(zonas):
        r = skia.Rect((W - w) / 2, (H - h) / 2, (W + w) / 2, (H + h) / 2).makeInset(3, 3)
        cv.drawRect(r, tinta(c, 235, traco=6))
        # TV dentro do quadro; desktop e área segura acima; tablet abaixo (os rótulos não se encostam)
        yr = r.top() + 44 if i == 0 else (r.bottom() + 44 if i == 2 else r.top() - 14)
        escrever(cv, rot, r.left() + 16, yr, f, c, "e", contorno=[("#000000", 4)])


def destaque(cv, m, item):
    """Capa de destaque 1080x1920: disco com retícula na cor do item e o mascote como adesivo, tudo dentro do
    círculo que o Instagram recorta no centro."""
    W, H = 1080, 1920
    ac = item.get("cor") or m.c["acento"]
    fundo_liso(cv, m, W, H, ac, pe=False)
    cx, cy, R = W / 2, H / 2, 400
    cartao(cv, m, skia.Rect(cx - R, cy - R, cx + R, cy + R), ac, angulo=0, circulo=True)
    cv.drawCircle(cx, cy, R - 8, tinta(m.c["texto"], traco=16))
    img = m.pose(item.get("pose"))
    if img is not None:
        adesivo(cv, m, img, cx - 265, cy - 285, 530, 570, "centro")
    else:
        desenhar_icone(cv, m, cx - 230, cy - 230, 460)


# ------------------------------------------------------------------------------------------------ modelos


def _arte(m, arte, pose):
    if arte:
        return m.imagem(arte)
    return m.pose(pose)


def capa(cv, m, titulo, parte, subtitulo, pergunta, linha, ac, arte_img, guia=False):
    """Capa de episódio 1080x1920 no layout da capa do kit (versão Instagram): cartão inclinado com o elenco como
    adesivo, selo da parte, nome da parte em versal, nome da série em fonte de cartaz e as opções do voto como
    etiquetas. Tudo dentro do recorte 3:4 da grade (y 240 a 1680), menos o @ do rodapé. A pergunta repete as
    opções do voto ("BICHO OU LENDA?" vira as etiquetas BICHO e LENDA)."""
    W, H = 1080, 1920
    p = paleta(m)
    cart0, base0, topo, texto0, limite = (64, 330, 1016, 1060), 1085, 250, 1112, 1664
    fundo_liso(cv, m, W, H, ac)
    op = opcoes_do_voto(pergunta)
    fk = caber(m, "mono", subtitulo, 40, LARG, 0.08) if subtitulo else None
    fl = caber(m, "mono", linha, 32, LARG, 0.06, minimo=22) if linha else None
    fq = None if op or not pergunta else caber(m, "titulo", pergunta, 80, LARG)
    alt_op = etiquetas(cv, m, X0, 0, op[0], op[1], LARG, medir=True) if op else (int(fq.getSize() * 1.2) if fq else 0)
    depois = 26 + alt_op + 28 + (int(fl.getSize() * 1.3) if fl else 0)

    def bloco(sobe):
        y0 = texto0 - sobe + (52 if fk else 0)
        return quebra(m, titulo, 190, LARG, limite - y0 - depois)

    # Nome longo (ou opções longas) espremendo o título: o cartão e o elenco cedem até 220 px de altura.
    sobe = 0
    linhas, ft = bloco(0)
    while ft.getSize() < 100 and sobe < 220:
        sobe += 20
        linhas, ft = bloco(sobe)
    cart = skia.Rect(cart0[0], cart0[1], cart0[2], cart0[3] - sobe)
    cartao(cv, m, cart, ac)
    arte_ou_icone(cv, m, arte_img, (W / 2 - 450, topo, 900, base0 - sobe - topo), cart)
    selo(cv, m, cart.left() + 92, cart.top() + 70, parte)
    y = texto0 - sobe
    if fk:
        escrever(cv, subtitulo, X0, y + topo_base(fk), fk, claro(ac), "e", 0.08 * fk.getSize())
        y += 52
    y = escrever_titulo(cv, m, linhas, ft, X0, y) + 26
    if op:
        y += etiquetas(cv, m, X0, y, op[0], op[1], LARG)
    elif fq:
        escrever(cv, pergunta, X0, y + topo_base(fq), fq, p["op1"], "e")
        y += fq.getSize() * 1.2
    y += 28
    if fl:
        trk = 0.06 * fl.getSize() if fl.measureText(linha) < LARG * 0.85 else 0.0
        escrever(cv, linha, X0, y + topo_base(fl), fl, p["suave"], "e", trk)
    fp = m.fonte("mono", 34)
    escrever(cv, m.arroba, X0, 1752 + topo_base(fp), fp, misturar(p["suave"], p["fundo"], 0.2), "e")
    if guia:
        _guia_grade(cv, m, W, H)


def _guia_grade(cv, m, W, H):
    f = m.fonte("mono", 28)
    for rot, w, h, c in (("GRADE IG 3:4 · 1080x1440", 1080, 1440, m.c["destaque"]),
                         ("FEED 4:5 · 1080x1350", 1080, 1350, m.c.get("ok", "#4CD38C")),
                         ("ANTIGO 1:1 · 1080x1080", 1080, 1080, "#FFFFFF")):
        r = skia.Rect((W - w) / 2, (H - h) / 2, (W + w) / 2, (H + h) / 2).makeInset(4, 4)
        cv.drawRect(r, tinta(c, 240, traco=6))
        escrever(cv, rot, r.left() + 18, r.top() + 40, f, c, "e", contorno=[("#000000", 4)])
    cv.drawRect(skia.Rect(0, 0, W, (H - 1440) / 2), tinta("#000000", 120))
    cv.drawRect(skia.Rect(0, (H + 1440) / 2, W, H), tinta("#000000", 120))


def post(cv, m, kicker, titulo, texto, ac, arte_img):
    """Post de feed 1080x1350 (4:5): rótulo, título com sombra dura, texto à esquerda e o mascote no cartão à
    direita. Margem lateral de 90 px: sobrevive ao recorte 3:4 da grade."""
    W, H = 1080, 1350
    p = paleta(m)
    fundo_liso(cv, m, W, H, ac, pe=False)
    X, larg = 90, 900
    fk = caber(m, "mono", kicker, 32, larg, 0.1)
    escrever(cv, kicker, X, 120 + topo_base(fk), fk, claro(ac), "e", 0.1 * fk.getSize())
    linhas, ft = quebra(m, titulo, 128, larg, 330)
    y = escrever_titulo(cv, m, linhas, ft, X, 182, sombra_dy=7)
    y_txt = y + 34
    cart = skia.Rect(600, max(y_txt + 70, 560), 1000, 1130)
    cartao(cv, m, cart, ac, raio=44)
    arte_ou_icone(cv, m, arte_img, (cart.left() - 10, y_txt + 10, cart.width() + 20, cart.bottom() + 20 - y_txt - 10),
                  cart)
    fb = m.fonte("texto", 38)
    for l in quebrar(fb, texto, 470)[:max(1, int((1120 - y_txt) // 54))]:
        escrever(cv, l, X, y_txt + topo_base(fb), fb, p["texto"], "e")
        y_txt += 54
    desenhar_icone(cv, m, X, 1170, 88)
    f = m.fonte("mono", 32)
    escrever(cv, m.arroba, X + 110, 1214 + altura_caixa(f) / 2, f, p["texto"], "e", 0.04 * 32)


def card_parte(cv, m, serie, parte, linha, ac, arte_img):
    """Story/Reel 1080x1920 anunciando parte nova. Tudo entre y 250 e 1580 (fora das barras do app)."""
    W, H = 1080, 1920
    p = paleta(m)
    fundo_liso(cv, m, W, H, ac)
    _cabecalho(cv, m, 270)
    cart = skia.Rect(64, 480, 1016, 1070)
    cartao(cv, m, cart, ac)
    arte_ou_icone(cv, m, arte_img, (W / 2 - 420, 420, 840, 1095 - 420), cart)
    selo(cv, m, cart.left() + 108, cart.top() + 84, parte, raio=112)
    y = 1128
    fk = caber(m, "mono", serie, 40, LARG, 0.08)
    escrever(cv, serie, X0, y + topo_base(fk), fk, claro(ac), "e", 0.08 * fk.getSize())
    y += 58
    tit = f"PARTE {parte}"
    y = escrever_titulo(cv, m, [tit], caber(m, "titulo", tit, 190, LARG), X0, y) + 18
    fe = caber(m, "titulo", "JÁ ESTÁ NO AR", 60, LARG - 80)
    etiqueta(cv, m, X0, y, "JÁ ESTÁ NO AR", p["destaque"], fe, 100)
    y += 140
    if linha:
        fm = caber(m, "mono", linha, 34, LARG, 0.08)
        escrever(cv, linha, X0, y + topo_base(fm), fm, p["suave"], "e", 0.08 * fm.getSize())


def card_resultado(cv, m, serie, parte, pergunta, opcoes, votos, ac, arte_img, demo=False):
    """Story/Reel 1080x1920 com o placar. opcoes = [(rótulo, porcentagem), ...]: cada barra na cor da sua opção
    (opcao1, opcao2) e a etiqueta VENCEU na cor de destaque."""
    W, H = 1080, 1920
    p = paleta(m)
    fundo_liso(cv, m, W, H, ac)
    _cabecalho(cv, m, 270)
    y = 430
    fk = m.fonte("mono", 36)
    escrever(cv, "RESULTADO DA VOTAÇÃO", X0, y + topo_base(fk), fk, claro(ac), "e", 0.14 * 36)
    y += 56
    sub = f"{serie} · PARTE {parte}"
    fs = caber(m, "mono", sub, 32, LARG, 0.08)
    escrever(cv, sub, X0, y + topo_base(fs), fs, p["suave"], "e", 0.08 * fs.getSize())
    y += 70
    linhas, fq = quebra(m, pergunta, 132, LARG, 290, 2)
    y = escrever_titulo(cv, m, linhas, fq, X0, y) + 50
    venc = max(range(len(opcoes)), key=lambda i: opcoes[i][1])
    # Uma cor por opção: as duas do voto e, a partir da terceira, as de apoio da paleta.
    cores_op = [p["op1"], p["op2"], m.c.get("ok", "#4CD38C"), m.c.get("acento2", "#3D8EF0"), m.c.get("destaque2", "#F0443A")]
    passo = min(210, 660 / max(1, len(opcoes)))
    fpct = m.fonte("titulo", 76)
    xd = W - 88
    for i, (rot, pct) in enumerate(opcoes):
        c = cores_op[i % len(cores_op)]
        fo = caber(m, "titulo", rot, 60, 560)
        escrever(cv, rot, X0, y + 72, fo, p["texto"], "e")
        escrever(cv, f"{pct:.0f}%", xd, y + 78, fpct, c, "d", dura=(p["sombra"], 0, 6))
        trilho = skia.Rect(X0, y + 102, xd, y + 156)
        cv.drawRoundRect(trilho, 27, 27, tinta(p["trilho"]))
        if pct > 0:
            cv.drawRoundRect(skia.Rect(X0, y + 102, X0 + max(54, (xd - X0) * pct / 100), y + 156), 27, 27, tinta(c))
        if i == venc:
            fv = m.fonte("titulo", 28)
            etiqueta(cv, m, X0 + fo.measureText(rot) + 26, y + 18, "VENCEU", p["destaque"], fv, 58, pad=18, raio=14)
        y += passo
    votos_txt = f"{votos} VOTOS NOS COMENTÁRIOS"
    # Com arte, o mascote ocupa o canto de baixo à direita (abaixo das barras) e os votos ficam na coluna da esquerda.
    com_arte = arte_img is not None and 1585 - (y - 40) >= 240
    fm = caber(m, "mono", votos_txt, 32, 500 if com_arte else LARG, 0.06)
    escrever(cv, votos_txt, X0, y + 10 + topo_base(fm), fm, p["suave"], "e", 0.06 * fm.getSize())
    if com_arte:
        cartao(cv, m, skia.Rect(650, y + 50, 1016, 1570), ac, angulo=3.0, raio=40)
        adesivo(cv, m, arte_img, 640, y - 40, 370, 1585 - (y - 40))
    if demo:
        fd = m.fonte("mono", 28)
        cv.drawRect(skia.Rect(0, 1600, W, 1656), tinta("#000000", 190))
        escrever(cv, "DEMONSTRAÇÃO · NÚMEROS FICTÍCIOS", W / 2, 1628 + altura_caixa(fd) / 2, fd, "#FFFFFF", tracking=3)


def escala_playlist(arte):
    """3840x2160 (recomendado pelo YouTube) só se a arte aguenta: ampliar um adesivo de 500 px para 4K só
    amolece o traço. Com arte pequena, 1920x1080, que já passa da largura mínima de 640 com folga."""
    return 2 if arte is None or arte.height() >= 1000 else 1


def capa_playlist(cv, m, kicker, titulo, linha, ac, arte_img):
    """Capa 16:9 desenhada em 1920x1080 (escalada para 3840x2160). Canto inferior direito livre para o selo do app."""
    W, H = 1920, 1080
    p = paleta(m)
    fundo_liso(cv, m, W, H, ac, pe=False)
    cart = skia.Rect(70, 200, 850, 960)
    cartao(cv, m, cart, ac)
    arte_ou_icone(cv, m, arte_img, (90, 90, 740, 900), cart)
    x, larg = 940, 880
    fk = caber(m, "mono", kicker, 34, larg, 0.1)
    escrever(cv, kicker, x, 250 + topo_base(fk), fk, claro(ac), "e", 0.1 * fk.getSize())
    linhas, ft = quebra(m, titulo, 190, larg, 400)
    y = escrever_titulo(cv, m, linhas, ft, x, 306, sombra_dy=10) + 30
    if linha:
        fe = caber(m, "titulo", linha, 52, larg - 70)
        etiqueta(cv, m, x, y, linha, p["destaque"], fe, int(fe.getSize() * 1.75))
    desenhar_icone(cv, m, x, 870, 88)
    escrever(cv, m.arroba, x + 110, 914 + altura_caixa(m.fonte("mono", 34)) / 2, m.fonte("mono", 34), p["texto"], "e",
             0.04 * 34)


# ------------------------------------------------------------------------------------------------ prancha do manual


def manual_prancha(cv, m, arquivos):
    W, H = 2400, 6000  # altura final = onde o conteúdo termina (ver gerar_tudo)
    cv.drawRect(skia.Rect(W, H), tinta(m.c["fundo"]))
    ft, fm, fx = (lambda t: m.fonte("titulo", t)), (lambda t: m.fonte("mono", t)), (lambda t: m.fonte("texto", t))
    M = 120

    def secao(n, rot, y):
        escrever(cv, f"{n:02d}", M, y, fm(30), m.c["destaque"], "e", 4)
        escrever(cv, rot, M + 80, y, fm(30), m.c["texto"], "e", 4)
        cv.drawRect(skia.Rect(M, y + 22, W - M, y + 24), tinta(m.c["painel2"] if "painel2" in m.c else "#2E2729"))

    desenhar_icone(cv, m, M, 110, 170)
    escrever(cv, "MANUAL DE IDENTIDADE VISUAL", M + 210, 190, ft(96), m.c["texto"], "e")
    escrever(cv, f"{m.nome.upper()}  ·  {m.arroba}  ·  {datetime.date.today():%d/%m/%Y}", M + 214, 258, fm(30),
             m.c["texto_suave"], "e", 3)

    # 1. Logos
    secao(1, "LOGOTIPO", 400)
    y = 450
    cel = [(skia.Rect(M, y, M + 1040, y + 520), m.c["painel"]), (skia.Rect(M + 1120, y, W - M, y + 520), m.c["texto"])]
    for r, c in cel:
        cv.drawRoundRect(r, 28, 28, tinta(c))
    if m.logo_ilustrado:
        desenhar_imagem(cv, m.logo_img(), M + 60, y + 40, 920, 360, "centro")
        escrever(cv, "PRINCIPAL ILUSTRADO · fundo escuro", M + 40, y + 490, fm(24), m.c["texto_suave"], "e", 2)
    else:
        S0 = 220 * min(1.0, 960 / lockup_medidas(m, 220)[0])
        lw0, _, _ = lockup_medidas(m, S0)
        desenhar_lockup(cv, m, M + (1040 - lw0) / 2, y + 230 - S0 / 2, S0)
        escrever(cv, "PRINCIPAL VETOR · fundo escuro", M + 40, y + 490, fm(24), m.c["texto_suave"], "e", 2)
    S = 150
    lw, _, _ = lockup_medidas(m, S)
    xl = M + 1120 + (1040 - lw) / 2
    desenhar_lockup(cv, m, xl, y + 70, S)
    lw2, _, _ = lockup_medidas(m, 110)
    desenhar_lockup(cv, m, M + 1120 + (1040 - lw2) / 2, y + 280, 110, "mono", m.c["fundo"])
    escrever(cv, "VETOR (COR) E MONO PRETO · fundo claro", M + 1160, y + 490, fm(24), "#5A524A", "e", 2)
    y = 1010
    cv.drawRoundRect(skia.Rect(M, y, W - M, y + 300), 28, 28, tinta(m.c["painel"]))
    desenhar_icone(cv, m, M + 50, y + 50, 200)
    desenhar_icone(cv, m, M + 300, y + 50, 200, com_fundo=False)
    lw3, _, _ = lockup_medidas(m, 150)
    desenhar_lockup(cv, m, M + 560, y + 75, 150, "mono", "#FFFFFF")
    escrever(cv, "ÍCONE · SÍMBOLO SOLTO · MONO BRANCO", M + 560 + lw3 + 60, y + 165, fm(26), m.c["texto_suave"], "e", 2)

    # 2. Paleta
    secao(2, "PALETA", 1420)
    y = 1470
    pal = m.paleta_doc or [{"nome": k, "hex": v, "uso": ""} for k, v in m.c.items()]
    n = len(pal)
    cols = min(n, 6)
    cw = (W - 2 * M - (cols - 1) * 24) / cols
    for i, p in enumerate(pal):
        lin, col = divmod(i, cols)
        x0, y0 = M + col * (cw + 24), y + lin * 380
        cv.drawRoundRect(skia.Rect(x0, y0, x0 + cw, y0 + 190), 22, 22, tinta(p["hex"]))
        cv.drawRoundRect(skia.Rect(x0, y0, x0 + cw, y0 + 190), 22, 22, tinta("#FFFFFF", 40, traco=2))
        escrever(cv, p["nome"].upper(), x0, y0 + 236, caber(m, "titulo", p["nome"].upper(), 40, cw), m.c["texto"], "e")
        escrever(cv, p["hex"].upper(), x0, y0 + 280, fm(26), m.c["destaque"], "e", 2)
        for k, l in enumerate(quebrar(fx(22), p.get("uso", ""), cw)[:2]):
            escrever(cv, l, x0, y0 + 316 + k * 28, fx(22), m.c["texto_suave"], "e")
    y = y + ((n - 1) // cols + 1) * 380 + 70

    # 3. Tipografia
    secao(3, "TIPOGRAFIA", y)
    y += 70
    tipos = m.tipografia_doc or [{"papel": k, "nome": Path(v).stem, "uso": "", "amostra": "Aa"}
                                 for k, v in m.fontes.items() if k != "logo"]
    for t in tipos:
        f = m.fonte(t["papel"], 92 if t["papel"] == "titulo" else 64)
        escrever(cv, t.get("amostra", "Aa"), M, y + 92, f, m.c["texto"], "e")
        escrever(cv, t["nome"].upper(), M + 1400, y + 48, fm(28), m.c["destaque"], "e", 3)
        for k, l in enumerate(quebrar(fx(24), t.get("uso", ""), 760)[:3]):
            escrever(cv, l, M + 1400, y + 88 + k * 32, fx(24), m.c["texto_suave"], "e")
        y += 170

    # 4. Mascote
    secao(4, f"MASCOTE{(' · ' + m.mascote_nome.upper()) if m.mascote_nome else ''} E POSES", y + 20)
    y += 80
    poses = list(m.poses.items())
    cols = 9
    cw = (W - 2 * M) / cols
    for i, (nome, _) in enumerate(poses):
        lin, col = divmod(i, cols)
        x0, y0 = M + col * cw, y + lin * 290
        desenhar_imagem(cv, m.pose(nome), x0 + 10, y0 + 10, cw - 20, 220, "base", sombra=False)
        escrever(cv, nome.upper(), x0 + cw / 2, y0 + 268, caber(m, "mono", nome.upper(), 20, cw - 10), m.c["texto_suave"],
                 tracking=1)
    y += ((len(poses) - 1) // cols + 1) * 290 + 80

    # 5. Faça / Não faça
    secao(5, "FAÇA  /  NÃO FAÇA", y)
    y += 70
    colw = (W - 2 * M - 60) / 2
    fim = y
    for j, (rot, itens, c) in enumerate((("FAÇA", m.fazer, m.c.get("ok", "#4CD38C")),
                                         ("NÃO FAÇA", m.nao_fazer, m.c["destaque2"]))):
        x0 = M + j * (colw + 60)
        escrever(cv, rot, x0, y + 40, ft(48), c, "e")
        yy = y + 100
        for it in itens:
            ls = quebrar(fx(26), it, colw - 40)
            cv.drawCircle(x0 + 10, yy - 9, 7, tinta(c))
            for l in ls:
                escrever(cv, l, x0 + 34, yy, fx(26), m.c["texto"], "e")
                yy += 36
            yy += 12
        fim = max(fim, yy)
    return int(fim + 70)


# ------------------------------------------------------------------------------------------------ conferência


def conferencia(r, m, arquivos, saida):
    """Prancha com todas as peças em miniatura e a prova de legibilidade do perfil em tamanho de app."""
    W, cols, cw, ch = 2400, 6, 380, 470
    linhas = (len(arquivos) - 1) // cols + 1
    H = 300 + linhas * (ch + 30) + 420
    s = r.tela(W, H)
    cv = s.getCanvas()
    cv.drawRect(skia.Rect(W, H), tinta("#2A2A2E"))
    escrever(cv, f"CONFERÊNCIA DA IDV · {m.nome.upper()} · {len(arquivos)} PEÇAS · render {r.modo}", 40, 70,
             m.fonte("mono", 34), "#FFFFFF", "e", 3)
    for i, (rot, caminho) in enumerate(arquivos):
        lin, col = divmod(i, cols)
        x0, y0 = 40 + col * (cw + 10), 120 + lin * (ch + 30)
        cv.drawRect(skia.Rect(x0, y0, x0 + cw, y0 + ch - 60), tinta("#3A3A40"))
        img = skia.Image.open(str(caminho))
        desenhar_imagem(cv, img, x0 + 10, y0 + 10, cw - 20, ch - 80, "centro", False)
        f = caber(m, "mono", rot, 20, cw)
        escrever(cv, rot, x0, y0 + ch - 28, f, "#DDDDDD", "e")
    y = 140 + linhas * (ch + 30)
    escrever(cv, "PERFIL EM TAMANHO DE APP: 110, 64, 40 E 32 PX", 40, y,
             m.fonte("mono", 26), "#FFFFFF", "e", 2)
    pf = skia.Image.open(str(Path(saida).parent / "perfil" / "perfil_1080.png"))
    x = 40
    for fundo in ("#FFFFFF", "#000000"):
        cv.drawRect(skia.Rect(x, y + 30, x + 520, y + 230), tinta(fundo))
        xx = x + 30
        for t in (110, 64, 40, 32):
            cv.save()
            cv.clipPath(skia.Path.Circle(xx + t / 2, y + 130, t / 2), doAntiAlias=True)
            cv.drawImageRect(pf, skia.Rect(xx, y + 130 - t / 2, xx + t, y + 130 + t / 2),
                             skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
            cv.restore()
            xx += t + 40
        x += 560
    bn = Path(saida).parent / "youtube" / "banner_2560x1440.jpg"
    if bn.exists():
        b = skia.Image.open(str(bn))
        escrever(cv, "BANNER NO CELULAR (SÓ A ÁREA SEGURA)", 1180, y, m.fonte("mono", 26), "#FFFFFF", "e", 2)
        src = skia.Rect((2560 - 1546) / 2, (1440 - 423) / 2, (2560 + 1546) / 2, (1440 + 423) / 2)
        cv.drawImageRect(b, src, skia.Rect(1180, y + 30, 1180 + 773, y + 30 + 211.5),
                         skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    r.salvar(s, saida, qualidade=88)


# ------------------------------------------------------------------------------------------------ manual .md


def manual_md(m, arquivos, pasta):
    L = [f"# Manual de identidade visual · {m.nome}", "",
         f"Gerado por `gerar_idv.py` a partir de `{m.arquivo.name}` em {datetime.date.today():%d/%m/%Y}. "
         "Para mudar qualquer coisa aqui, edite o marca.json e rode de novo: este arquivo é saída, não fonte.", "",
         f"**Nome:** {m.nome} · **Perfil:** {m.arroba}" + (f" · **Site:** {m.site}" if m.site else "") + "  ",
         f"**Slogan:** {m.slogan}  ", f"**Chamada:** {m.chamada}", "", "![Prancha do manual](manual_idv.png)", "",
         "## Paleta", "", "| Cor | Hex | Onde usar |", "|---|---|---|"]
    for p in (m.paleta_doc or [{"nome": k, "hex": v, "uso": ""} for k, v in m.c.items()]):
        L.append(f"| {p['nome']} | `{p['hex'].upper()}` | {p.get('uso', '')} |")
    if m.series:
        L += ["", "### Cor de cada série", "", "Só nas peças da série (listras do fundo, cartão, rótulo, anel do destaque). "
              "A marca continua com o destaque e o acento do canal.", "", "| Série | Hex | Pose do mascote no destaque |", "|---|---|---|"]
        for s in m.series:
            L.append(f"| {s['nome']} | `{s['cor'].upper()}` | {s.get('pose', '')} |")
    L += ["", "## Tipografia", "", "| Papel | Fonte | Onde usar | Licença |", "|---|---|---|---|"]
    for t in (m.tipografia_doc or []):
        L.append(f"| {t['papel']} | {t['nome']} | {t.get('uso', '')} | {t.get('licenca', '')} |")
    L += ["", "## Logotipo", "",
          "| Arquivo | Para quê |", "|---|---|"]
    if m.logo_ilustrado:
        L.append("| `logo/logo_principal_ilustrado.png` | Logo oficial (mascote + nome). Site, vídeo, banner. Raster: não "
                 "amplie além do tamanho original. |")
    L += [
          "| `logo/logo_principal_vetor.png/.svg` | Versão vetorial (símbolo + nome na fonte do logo). Tamanhos grandes, impressão, fundo claro. |",
          "| `logo/icone_quadrado_1024.png/.svg` | Símbolo no quadrado da cor de destaque: favicon, app, marca d'água. |",
          "| `logo/icone_simbolo_transparente.png/.svg` | Símbolo solto, sobre foto ou fundo escuro. |",
          "| `logo/logo_mono_branco` / `logo_mono_preto` | Uma cor só: carimbo, gravação, fundo de foto. |",
          "| `logo/icone_mono_branco` / `icone_mono_preto` | Símbolo em uma cor. |", "",
          "Área de respiro: no mínimo a altura do símbolo em volta do logo. Tamanho mínimo do logo vetorial: 120 px de "
          "largura na tela; abaixo disso, use só o ícone.", "",
          "## Mascote", "", m.mascote_desc, "", "| Pose | Arquivo | Quando usar |", "|---|---|---|"]
    usos = m.d.get("mascote", {}).get("usos", {})
    for k, v in m.poses.items():
        L.append(f"| {k} | `{v.name}` | {usos.get(k, '')} |")
    L += ["", "Nunca estique, gire em eixo, recolora ou recorte a borda branca do adesivo. Escala sempre uniforme.",
          "", "## Voz da marca", ""]
    L += [f"{i + 1}. {v}" for i, v in enumerate(m.voz)]
    L += ["", "## Faça", ""] + [f"- {x}" for x in m.fazer] + ["", "## Não faça", ""] + [f"- {x}" for x in m.nao_fazer]
    L += ["", "## Medidas das peças e fontes", "", "| Peça | Medida | Fonte |", "|---|---|---|"]
    L += [f"| {a} | {b} | {c} |" for a, b, c in MEDIDAS]
    L += ["", "## Arquivos gerados", ""] + [f"- `./{Path(c).relative_to(pasta).as_posix()}` · {r}" for r, c in arquivos]
    L += ["", "## Como gerar uma peça nova", "", "```",
          f"python gerar_idv.py modelo capa --marca marca.json --serie {m.series[0]['id'] if m.series else 'ID'} "
          "--parte 2 --subtitulo \"NOME DA PARTE\" --pergunta \"A OU B?\" --arte elenco.png --saida capa_p2.jpg",
          "```", "", "Os demais modelos e argumentos estão no README do kit (`kit/idv/README.md`).", ""]
    (pasta / "MANUAL_IDV.md").write_text("\n".join(L), encoding="utf-8")
    print("  MANUAL_IDV.md", flush=True)


# ------------------------------------------------------------------------------------------------ orquestração


def _render_peca(r, w, h, desenho, caminho, **kw):
    s = r.tela(w, h)
    desenho(s.getCanvas())
    r.salvar(s, caminho, **kw)
    return caminho


# Textos dos modelos de exemplo. O campo "exemplo" do marca.json troca qualquer um deles (e "serie" escolhe a série
# cuja cor e pose entram nos modelos), para a pasta de exemplo sair com a cara do canal.
EXEMPLO = dict(titulo="NOME DA SÉRIE", parte=1, subtitulo="NOME DA PARTE", pergunta="OPÇÃO A OU OPÇÃO B?",
               linha="VOCÊ DECIDE A PARTE 2", texto="Uma ou duas frases de contexto, sem spoiler. "
               "O voto nos comentários decide o que acontece na próxima parte.",
               post_titulo="TÍTULO DO POST AQUI", parte_linha="ASSISTA NO PERFIL",
               resultado_pergunta="PERGUNTA DO VOTO AQUI?", opcoes=[["OPÇÃO A", 62], ["OPÇÃO B", 38]], votos=128,
               playlist_kicker="SÉRIE INTERATIVA · TEMPORADA 1", playlist_linha="VOCÊ DECIDE CADA PARTE")


def gerar_tudo(r, m, saida):
    saida = Path(saida)
    saida.mkdir(parents=True, exist_ok=True)
    arq = []
    gerar_logos(r, m, saida / "logo")
    for n in ("logo_principal_ilustrado.png", "logo_principal_vetor.png", "logo_mono_branco.png",
              "logo_mono_preto.png", "icone_quadrado_1024.png", "icone_simbolo_transparente.png",
              "icone_mono_branco.png", "icone_mono_preto.png"):
        if (saida / "logo" / n).exists():
            arq.append((f"logo/{n}", saida / "logo" / n))

    print("perfil/ e youtube/", flush=True)
    arq.append(("perfil 1080", _render_peca(r, 1080, 1080, lambda cv: perfil(cv, m), saida / "perfil" / "perfil_1080.png")))
    arq.append(("banner YouTube", _render_peca(r, 2560, 1440, lambda cv: banner(cv, m),
                                               saida / "youtube" / "banner_2560x1440.jpg", max_bytes=6_000_000)))
    arq.append(("banner guia", _render_peca(r, 2560, 1440, lambda cv: banner(cv, m, True),
                                            saida / "youtube" / "banner_guia_areas.jpg")))
    arq.append(("marca d'água 150", _render_peca(r, 150, 150, lambda cv: desenhar_icone(cv, m, 0, 0, 150),
                                                 saida / "youtube" / "marca_dagua_150.png")))

    print("destaques/", flush=True)
    itens = [{"id": s["id"], "nome": s["nome"], "cor": s.get("cor"), "pose": s.get("pose")} for s in m.series]
    itens += m.destaques_extra
    for it in itens:
        arq.append((f"destaque {it['nome']}", _render_peca(r, 1080, 1920, lambda cv, it=it: destaque(cv, m, it),
                                                           saida / "destaques" / f"destaque_{it['id']}.png")))

    print("modelos/exemplo/", flush=True)
    ex = {**EXEMPLO, **m.d.get("exemplo", {})}
    ac = m.serie(ex["serie"])["cor"] if ex.get("serie") else m.c["acento"]
    poses = m.d.get("modelos", {})
    arte = m.pose(poses.get("pose_capa"))
    pe = saida / "modelos" / "exemplo"
    for guia in (False, True):
        nome = "capa_episodio_guia_grade.jpg" if guia else "capa_episodio.jpg"
        arq.append((nome[:-4].replace("_", " "), _render_peca(
            r, 1080, 1920, lambda cv, g=guia: capa(cv, m, ex["titulo"], ex["parte"], ex["subtitulo"], ex["pergunta"],
                                                   ex["linha"], ac, arte, g), pe / nome)))
    arq.append(("post feed", _render_peca(r, 1080, 1350, lambda cv: post(
        cv, m, f"{ex['titulo']} · PARTE {ex['parte']}", ex["post_titulo"], ex["texto"], ac,
        m.pose(poses.get("pose_post"))), pe / "post_feed.jpg")))
    arq.append(("card parte", _render_peca(r, 1080, 1920, lambda cv: card_parte(
        cv, m, ex["titulo"], ex["parte"] + 1, ex["parte_linha"], ac, m.pose(poses.get("pose_parte"))),
        pe / "card_parte_disponivel.jpg")))
    # Os números do exemplo são inventados: o card sai sempre com o carimbo de demonstração.
    arq.append(("card resultado", _render_peca(r, 1080, 1920, lambda cv: card_resultado(
        cv, m, ex["titulo"], ex["parte"], ex["resultado_pergunta"], [tuple(o) for o in ex["opcoes"]], ex["votos"], ac,
        m.pose(poses.get("pose_resultado")), demo=True), pe / "card_resultado.jpg")))
    k = escala_playlist(arte)
    arq.append(("capa playlist", _render_peca(r, 1920 * k, 1080 * k, lambda cv: (cv.scale(k, k), capa_playlist(
        cv, m, ex["playlist_kicker"], ex["titulo"], ex["playlist_linha"], ac, arte)),
        pe / "capa_playlist_youtube.jpg", max_bytes=2_000_000)))

    if m.d.get("variantes_demo"):
        print("modelos/variantes/", flush=True)
        for nome, w, h, fn in _variantes(m):
            arq.append((nome, _render_peca(r, w, h, fn, saida / "modelos" / "variantes" / f"{nome}.jpg",
                                           max_bytes=2_000_000 if w >= 1920 else None)))

    print("manual", flush=True)
    # Grava o desenho primeiro para saber onde o conteúdo termina e cortar a prancha nessa altura.
    gravador = skia.PictureRecorder()
    altura = manual_prancha(gravador.beginRecording(skia.Rect(2400, 6000)), m, arq)
    figura = gravador.finishRecordingAsPicture()
    s = r.tela(2400, altura)
    s.getCanvas().drawPicture(figura)
    r.salvar(s, saida / "manual_idv.png")
    arq.append(("manual_idv.png", saida / "manual_idv.png"))
    if m.arquivo.resolve() != (saida / "marca.json").resolve():
        shutil.copy(m.arquivo, saida / "marca.json")
    manual_md(m, arq, saida)
    print("conferência", flush=True)
    conferencia(r, m, arq, saida / "conferencia.jpg")


def _variantes(m):
    """Variantes de demonstração definidas no marca.json (campo variantes_demo): provam que os modelos aceitam
    título, parte, cor e arte por argumento."""
    out = []
    for v in m.d["variantes_demo"]:
        s = m.serie(v["serie"])
        ac = v.get("cor") or s["cor"]
        arte = m.imagem(v["arte"]) if v.get("arte") else m.pose(s.get("pose"))
        t = v["tipo"]
        nome = f"{t}_{s['id']}_p{v.get('parte', 1)}"
        if t == "capa":
            out.append((nome, 1080, 1920, lambda cv, s=s, v=v, ac=ac, arte=arte: capa(
                cv, m, s["nome"].upper(), v.get("parte", 1), v.get("subtitulo", ""), v.get("pergunta", ""),
                v.get("linha", ""), ac, arte)))
        elif t == "parte":
            out.append((nome, 1080, 1920, lambda cv, s=s, v=v, ac=ac, arte=arte: card_parte(
                cv, m, s["nome"].upper(), v.get("parte", 2), v.get("linha", "ASSISTA NO PERFIL"), ac, arte)))
        elif t == "resultado":
            ops = [(o.split("=")[0], float(o.split("=")[1])) for o in v["opcoes"]]
            out.append((nome + "_DEMO", 1080, 1920, lambda cv, s=s, v=v, ac=ac, arte=arte, ops=ops: card_resultado(
                cv, m, s["nome"].upper(), v.get("parte", 1), v["pergunta"], ops, v.get("votos", 0), ac,
                m.pose(v.get("pose")) or arte, demo=True)))
        elif t == "post":
            out.append((nome, 1080, 1350, lambda cv, s=s, v=v, ac=ac, arte=arte: post(
                cv, m, f"{s['nome'].upper()} · PARTE {v.get('parte', 1)}", v["titulo"], v["texto"], ac, arte)))
        elif t == "playlist":
            k = escala_playlist(arte)
            out.append((f"playlist_{s['id']}", 1920 * k, 1080 * k, lambda cv, s=s, v=v, ac=ac, arte=arte, k=k: (
                cv.scale(k, k), capa_playlist(cv, m, v.get("kicker", "SÉRIE INTERATIVA"), s["nome"].upper(),
                                              v.get("linha", "VOCÊ DECIDE CADA PARTE"), ac, arte))))
    return out


def recortar_fundo(entrada, saida, chave="verde", margem=16):
    """Tira o fundo chapado de uma arte feita em IA de imagem (verde #00FF00 ou magenta #FF00FF) e salva um PNG
    transparente recortado no conteúdo. Na borda, separa a cor da figura da cor do fundo (sem halo verde).
    Não peça "fundo transparente" à IA de imagem: ela costuma desenhar um xadrez falso."""
    from PIL import Image
    a = np.array(Image.open(entrada).convert("RGB")).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    if chave == "verde":
        dom, cor_fundo = g - np.maximum(r, b), np.array([0, 255, 0], np.float32)
    else:
        dom, cor_fundo = np.minimum(r, b) - g, np.array([255, 0, 255], np.float32)
    alfa = np.clip(1 - (dom - 90) / 80, 0, 1)            # até 90 é figura (verde de roupa fica); de 170 para cima, fundo
    borda = (alfa > 0) & (alfa < 1)
    limpo = a.copy()
    limpo[borda] = np.clip((a[borda] - (1 - alfa[borda, None]) * cor_fundo) / alfa[borda, None], 0, 255)
    out = np.dstack([limpo, alfa * 255]).astype(np.uint8)
    ys, xs = np.nonzero(out[..., 3] > 8)
    if not len(ys):
        raise SystemExit(f"ERRO: {entrada} ficou vazia depois de tirar o fundo {chave}.\n"
                         "O QUE FAZER: confira se o fundo é mesmo chapado; se o personagem for verde, peça fundo "
                         "magenta #FF00FF e rode com --chave magenta.")
    y0, y1 = max(0, ys.min() - margem), min(out.shape[0], ys.max() + margem + 1)
    x0, x1 = max(0, xs.min() - margem), min(out.shape[1], xs.max() + margem + 1)
    Path(saida).parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(out[y0:y1, x0:x1], "RGBA").save(saida, optimize=True)
    print(f"  {Path(saida).name}  {x1 - x0}x{y1 - y0}  fundo {chave} removido", flush=True)


def gerar_modelo(r, m, a):
    serie = m.serie(a.serie) if a.serie else {}
    ac = a.cor or serie.get("cor") or m.c["acento"]
    titulo = (a.titulo or serie.get("nome") or EXEMPLO["titulo"]).upper()
    arte = m.imagem(a.arte) if a.arte else m.pose(serie.get("pose"))
    t, saida = a.tipo, Path(a.saida)
    if t == "capa":
        _render_peca(r, 1080, 1920, lambda cv: capa(cv, m, titulo, a.parte, (a.subtitulo or "").upper(),
                                                    (a.pergunta or "").upper(), (a.linha or "").upper(), ac, arte,
                                                    a.guia), saida)
    elif t == "post":
        _render_peca(r, 1080, 1350, lambda cv: post(cv, m, f"{titulo} · PARTE {a.parte}",
                                                    (a.subtitulo or "TÍTULO DO POST").upper(),
                                                    a.texto or "", ac, arte), saida)
    elif t == "parte":
        _render_peca(r, 1080, 1920, lambda cv: card_parte(cv, m, titulo, a.parte,
                                                          (a.linha or "ASSISTA NO PERFIL").upper(), ac, arte), saida)
    elif t == "resultado":
        if not a.opcoes:
            raise SystemExit('resultado precisa de --opcoes "ROTULO=PORCENTAGEM" ...')
        ops = [(o.split("=")[0].upper(), float(o.split("=")[1])) for o in a.opcoes]
        _render_peca(r, 1080, 1920, lambda cv: card_resultado(cv, m, titulo, a.parte, (a.pergunta or "").upper(),
                                                              ops, a.votos, ac, arte, a.demo), saida)
    elif t == "playlist":
        k = escala_playlist(arte)
        _render_peca(r, 1920 * k, 1080 * k, lambda cv: (cv.scale(k, k), capa_playlist(
            cv, m, (a.subtitulo or "SÉRIE INTERATIVA · TEMPORADA 1").upper(), titulo,
            (a.linha or "VOCÊ DECIDE CADA PARTE").upper(), ac, arte)), saida, max_bytes=2_000_000)
    elif t == "destaque":
        _render_peca(r, 1080, 1920, lambda cv: destaque(cv, m, {"cor": ac, "pose": serie.get("pose")} if not a.arte
                                                        else {"cor": ac, "pose": a.arte}), saida)
    else:
        raise SystemExit(f"modelo desconhecido: {t}")


def main():
    ap = argparse.ArgumentParser(description="Gera a identidade visual a partir de um marca.json")
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("tudo", help="gera a IDV completa")
    t.add_argument("--marca", required=True)
    t.add_argument("--saida", required=True)
    t.add_argument("--cpu", action="store_true", help="render na CPU (sem placa de vídeo)")
    mo = sub.add_parser("modelo", help="gera uma peça a partir de um modelo")
    mo.add_argument("tipo", choices=["capa", "post", "parte", "resultado", "playlist", "destaque"])
    mo.add_argument("--marca", required=True)
    mo.add_argument("--saida", required=True)
    mo.add_argument("--serie")
    mo.add_argument("--titulo")
    mo.add_argument("--parte", type=int, default=1)
    mo.add_argument("--subtitulo")
    mo.add_argument("--pergunta")
    mo.add_argument("--linha")
    mo.add_argument("--texto")
    mo.add_argument("--cor")
    mo.add_argument("--arte")
    mo.add_argument("--opcoes", nargs="+")
    mo.add_argument("--votos", type=int, default=0)
    mo.add_argument("--guia", action="store_true", help="capa: marca os recortes da grade")
    mo.add_argument("--demo", action="store_true", help="resultado: carimba DEMONSTRAÇÃO · NÚMEROS FICTÍCIOS")
    mo.add_argument("--cpu", action="store_true")
    rc = sub.add_parser("recortar", help="tira o fundo verde (ou magenta) de uma arte feita em IA de imagem")
    rc.add_argument("entrada")
    rc.add_argument("saida")
    rc.add_argument("--chave", choices=["verde", "magenta"], default="verde")
    a = ap.parse_args()
    if a.cmd == "recortar":
        recortar_fundo(a.entrada, a.saida, a.chave)
        print("IDV_OK", flush=True)
        return
    m = Marca(a.marca)
    r = Render(gpu=not a.cpu)
    print(f"render: {r.modo}", flush=True)
    try:
        if a.cmd == "tudo":
            gerar_tudo(r, m, a.saida)
        else:
            gerar_modelo(r, m, a)
    finally:
        r.fechar()
    print("IDV_OK", flush=True)


if __name__ == "__main__":
    sys.exit(main())
