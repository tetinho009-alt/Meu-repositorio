# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Desenho das cartelas: fundo escuro com brilho, texto que entra palavra por palavra no tempo da voz e os layouts de
cada tipo de bloco (gancho, texto, item, quiz, revela, imagem, antes_depois, cta, voto, fim).

O padrão visual segue o que já foi aprovado nos vídeos reais: fundo quase preto, cor da marca só como brilho e luz,
nada parado (câmera viva, partículas), tranco de zoom e flash no corte, palavra-chave com brilho, conteúdo no meio
da tela (fora da faixa de cima, da de baixo e da coluna da direita, que a interface das redes cobre).
"""
import math
from functools import lru_cache
from pathlib import Path

import numpy as np
import skia

from maquina.desenho import (CX_SEGURO, FPS, H, LARG_SEGURA, W, ZS, caber, cheio, ease, fonte, quebrar, radial,
                             suave, traco)
from maquina.legenda import legenda

TEMA_PADRAO = {"fundo": "#0F1424", "fundo2": "#181E31", "destaque": "#FF6B4A", "destaque2": "#4FB3FF",
               "destaque3": "#C5EE4F", "texto": "#FFFFFF", "certo": "#4CD38C", "opcao1": "#FF6B4A",
               "opcao2": "#4FB3FF"}


def _prefs():
    """Preferências do canal (canal/preferencias.json); sem elas, os valores recomendados do próprio kit."""
    try:
        import prefs
        return prefs.carregar()
    except Exception:  # noqa: BLE001
        return None


PREFS = _prefs()
if PREFS:
    TEMA_PADRAO.update({"fundo": PREFS["canal"]["cor_fundo"], "destaque": PREFS["canal"]["cor_destaque"],
                        "destaque2": PREFS["canal"]["cor_destaque2"], "destaque3": PREFS["canal"]["cor_destaque3"]})
VIS = PREFS["visual"] if PREFS else {"camera_viva": True, "transicao": "flash_whoosh", "particulas": True}
LEG = PREFS["legenda"] if PREFS else {"ativa": True, "tamanho": 64, "cor": "#FFFFFF", "cor_destaque": None}
Y_TEXTO = 760              # centro do texto principal
Y_TOPO = ZS["y0"] + 150    # topo do conteúdo (longe da faixa de cima)
LARG = LARG_SEGURA * 0.94


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def tema(t):
    base = dict(TEMA_PADRAO)
    base.update(t or {})
    return {k: hex_rgb(v) if isinstance(v, str) and v.startswith("#") else v for k, v in base.items()}


def norm(p):
    import unicodedata
    s = unicodedata.normalize("NFKD", p).encode("ascii", "ignore").decode().lower()
    return "".join(ch for ch in s if ch.isalnum())


# ---------------------------------------------------------------- recursos com cache

@lru_cache(maxsize=64)
def imagem(caminho):
    p = Path(caminho)
    if not p.is_file():
        return None
    return skia.Image.open(str(p))


@lru_cache(maxsize=1)
def _grao():
    rng = np.random.default_rng(3)
    v = rng.integers(0, 255, (256, 256), dtype=np.uint8)
    rgba = np.stack([v, v, v, np.full_like(v, 255)], axis=-1)
    return skia.Image.fromarray(np.ascontiguousarray(rgba), colorType=skia.kRGBA_8888_ColorType)


@lru_cache(maxsize=1)
def _particulas():
    rng = np.random.default_rng(11)
    return rng.random((44, 4))   # x, y, profundidade, fase


# ---------------------------------------------------------------- camadas globais

def fundo(c, t, T):
    c.drawRect(skia.Rect(0, 0, W, H), cheio(T["fundo"]))
    c.drawRect(skia.Rect(0, 0, W, H), radial(W / 2, H * 0.42, H * 0.75, [(T["fundo2"], 255), (T["fundo"], 255)]))
    for k, (chave, fx, fy, r) in enumerate((("destaque3", 0.18, 0.30, 620), ("destaque2", 0.85, 0.62, 700),
                                            ("destaque", 0.40, 0.92, 520))):
        x = W * fx + 90 * math.sin(t * 0.21 + k * 2.1)
        y = H * fy + 70 * math.cos(t * 0.17 + k * 1.3)
        c.drawRect(skia.Rect(0, 0, W, H), radial(x, y, r, [(T[chave], 58), (T[chave], 0)]))
    if not VIS.get("particulas", True):
        return
    for x, y, z, f in _particulas():
        px = (x * W + 30 * math.sin(t * 0.3 + f * 6)) % W
        py = (y * H - t * (14 + 40 * z)) % H
        c.drawCircle(px, py, 1.5 + 3 * z, cheio(T["texto"], 40 + 70 * z, blur=1.2 + 2 * z))


def acabamento(c, t, T):
    """Vinheta e grão por cima de tudo (menos a legenda)."""
    c.drawRect(skia.Rect(0, 0, W, H), radial(W / 2, H / 2, H * 0.72, [((0, 0, 0), 0), ((0, 0, 0), 0), ((0, 0, 0), 150)],
                                             [0.0, 0.62, 1.0]))
    g = _grao()
    p = skia.Paint()
    p.setAlphaf(0.045)
    p.setBlendMode(skia.BlendMode.kOverlay)
    dx, dy = int(t * FPS * 37) % 256, int(t * FPS * 53) % 256
    for gx in range(-256, W + 256, 256):
        for gy in range(-256, H + 256, 256):
            c.drawImage(g, gx + dx, gy + dy, skia.SamplingOptions(), p)


def camera(c, u, dur):
    """Câmera viva: aproxima devagar durante o bloco e dá um tranco de zoom no corte."""
    if not VIS.get("camera_viva", True):
        return
    z = 1 + 0.045 * (u / max(dur, 0.1)) + 0.05 * math.exp(-u / 0.09) * (u < 0.6)
    c.translate(W / 2, H * 0.45)
    c.scale(z, z)
    c.translate(-W / 2, -H * 0.45)


def flash(c, u, T):
    if VIS.get("transicao", "flash_whoosh") == "flash_whoosh" and u < 0.12:
        c.drawRect(skia.Rect(0, 0, W, H), cheio((255, 255, 255), 70 * (1 - u / 0.12)))


# ---------------------------------------------------------------- texto que entra no tempo da voz

def _tempos_das_palavras(palavras_tela, falado, t0, t1):
    """Instante de entrada de cada palavra da tela: o da mesma palavra na voz, ou em sequência no começo do bloco.

    A frase inteira fica na tela até a metade da fala (quem assiste sem som precisa ler tudo).
    """
    fila = [(tp, norm(p)) for tp, p in falado]
    tempos, usado = [], 0
    prazo = t0 + 0.5 * max(t1 - t0, 0.4)
    passo = max(0.06, min(0.22, (prazo - t0) / max(len(palavras_tela), 1)))
    ultimo = t0 - passo
    for p in palavras_tela:
        alvo = norm(p)
        achou = None
        for k in range(usado, len(fila)):
            if fila[k][1] == alvo:
                achou, usado = fila[k][0], k + 1
                break
        tp = achou if achou is not None else ultimo + passo
        restantes = len(palavras_tela) - len(tempos) - 1
        tp = min(max(tp, ultimo + 0.04), prazo - restantes * 0.04)
        tempos.append(tp)
        ultimo = tp
    return tempos


_NO_GANCHO = [False]   # o quadro() marca quando o bloco da vez é o primeiro


def texto_cinetico(c, t, texto, falado, t0, t1, T, destaque=(), cy=Y_TEXTO, tam=150, larg=LARG, papel="titulo",
                   max_linhas=4):
    """Texto grande centralizado; cada palavra salta no instante em que a voz a fala. Palavra-chave com brilho."""
    if not texto:
        return
    texto = texto.upper()
    f = fonte(papel, tam)
    linhas = quebrar(texto, f, larg)
    while (len(linhas) > max_linhas or any(f.measureText(li) > larg for li in linhas)) and tam > 56:
        tam -= 8
        f = fonte(papel, tam)
        linhas = quebrar(texto, f, larg)
    palavras = [p for li in linhas for p in li.split()]
    tempos = _tempos_das_palavras(palavras, falado, t0, t1)
    if _NO_GANCHO[0]:  # gancho: o texto inteiro já está no quadro 0 (ele vira a miniatura e prende nos 3 s)
        tempos = [-1.0] * len(palavras)
    chaves = {norm(d) for d in destaque}
    passo = tam * 1.05
    y0 = cy - (len(linhas) - 1) * passo / 2 + tam * 0.36
    esp = f.measureText(" ")
    k = 0
    for li, linha in enumerate(linhas):
        ws = linha.split()
        total = sum(f.measureText(w) for w in ws) + esp * (len(ws) - 1)
        x = CX_SEGURO - total / 2
        y = y0 + li * passo
        for w in ws:
            larg_w = f.measureText(w)
            u = t - tempos[k]
            k += 1
            if u < 0:
                x += larg_w + esp
                continue
            e = ease(u / 0.2)
            esc = 1 + 0.35 * (1 - e) + 0.04 * math.exp(-u * 9) * math.sin(u * 36)
            chave = norm(w) in chaves
            corw = T["destaque"] if chave else T["texto"]
            c.save()
            c.translate(x + larg_w / 2, y - tam * 0.36)
            c.scale(esc, esc)
            c.translate(-larg_w / 2, tam * 0.36)
            if chave:
                c.drawString(w, 0, 0, f, cheio(corw, 200 * e, blur=22))
            c.drawString(w, 0, 10, f, cheio((0, 0, 0), 150 * e, blur=10))
            c.drawString(w, 0, 0, f, cheio(corw, 255 * e))
            c.restore()
            x += larg_w + esp


def rotulo(c, texto, y, T, a=255, tam=34):
    if not texto:
        return
    f = fonte("mono", tam)
    s = texto.upper()
    w = f.measureText(s)
    r = skia.Rect(CX_SEGURO - w / 2 - 26, y - tam - 6, CX_SEGURO + w / 2 + 26, y + 18)
    c.drawRRect(skia.RRect.MakeRectXY(r, 30, 30), cheio(T["destaque2"], 40 * a / 255))
    c.drawRRect(skia.RRect.MakeRectXY(r, 30, 30), traco(T["destaque2"], 3, 200 * a / 255))
    c.drawString(s, CX_SEGURO - w / 2, y, f, cheio(T["texto"], a))


def cartao(c, rect, cor_borda, a, T, brilho=0.0, preenchido=0.0):
    rr = skia.RRect.MakeRectXY(rect, 34, 34)
    if brilho:
        c.drawRRect(rr, cheio(cor_borda, 150 * brilho * a / 255, blur=26))
    c.drawRRect(rr, cheio(T["fundo2"], 235 * a / 255))
    if preenchido:
        c.drawRRect(rr, cheio(cor_borda, 90 * preenchido * a / 255))
    c.drawRRect(rr, traco(cor_borda, 5, 255 * a / 255))


# ---------------------------------------------------------------- layouts

def _cobrir(c, img, zoom, dx, dy, a=255):
    s = max(W / img.width(), H / img.height()) * zoom
    w, h = img.width() * s, img.height() * s
    p = skia.Paint()
    p.setAlphaf(a / 255)
    c.drawImageRect(img, skia.Rect(0, 0, img.width(), img.height()),
                    skia.Rect((W - w) / 2 + dx, (H - h) / 2 + dy, (W + w) / 2 + dx, (H + h) / 2 + dy),
                    skia.SamplingOptions(skia.FilterMode.kLinear), p)


def _sem_imagem(c, nome, T):
    r = skia.Rect(ZS["x0"], 420, ZS["x1"], 1180)
    c.drawRRect(skia.RRect.MakeRectXY(r, 30, 30), cheio(T["fundo2"], 220))
    p = traco(T["destaque3"], 4, 220)
    p.setPathEffect(skia.DashPathEffect.Make([22, 16], 0))
    c.drawRRect(skia.RRect.MakeRectXY(r, 30, 30), p)
    f = fonte("mono", 34)
    for i, s in enumerate(("FALTA A IMAGEM", Path(nome or "?").name)):
        w = f.measureText(s)
        c.drawString(s, CX_SEGURO - w / 2, 790 + i * 56, f, cheio(T["destaque3"], 230))


def _degrade_texto(c):
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, H * 0.30), skia.Point(0, H * 0.75)],
        [skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, 200)]))
    c.drawRect(skia.Rect(0, 0, W, H), p)


def desenho(c, d, u, base, cy, caixa_w, caixa_h):
    """Desenho do assunto do bloco (`"desenho": "arquivo.png"`, PNG transparente na pasta do episódio): entra com
    um salto e fica flutuando. É o que faz a cartela mostrar o mel, o bicho, o objeto, e não só texto."""
    im = imagem(str(Path(base) / d["desenho"])) if d.get("desenho") else None
    if im is None:
        return False
    esc = min(caixa_w / im.width(), caixa_h / im.height())
    e = ease(u / 0.3)
    pulo = 1 + 0.25 * (1 - e) + 0.05 * math.exp(-u * 6) * math.sin(u * 30)
    c.save()
    c.translate(CX_SEGURO, cy + 12 * math.sin(u * 2.2))
    c.rotate(2.5 * math.sin(u * 1.7))
    c.scale(esc * pulo, esc * pulo)
    pt = skia.Paint(AntiAlias=True)
    pt.setAlphaf(e)
    c.drawImage(im, -im.width() / 2, -im.height() / 2, skia.SamplingOptions(skia.FilterMode.kLinear), pt)
    c.restore()
    return True


def bloco(c, t, b, T, contexto):
    """Desenha o conteúdo do bloco `b` no instante t (sem fundo, sem legenda)."""
    tipo = b["tipo"]
    u = t - b["seg0"]
    dur = b["seg1"] - b["seg0"]
    falado = b["palavras"]
    d = b["dados"]
    tela = d.get("tela", "")
    destaque = d.get("destaque", [])
    if tipo in ("gancho", "texto", "fim"):
        rotulo(c, d.get("rotulo"), Y_TOPO, T, 255 * ease(u / 0.3))
        if desenho(c, d, max(u, 1.0) if b is contexto.get("primeiro") else u, contexto.get("base", "."), 470, 760, 500):
            texto_cinetico(c, t, tela, falado, b["t0"], b["t1"], T, destaque, cy=1000,
                           tam=150 if tipo == "gancho" else 120, max_linhas=3)
        else:
            texto_cinetico(c, t, tela, falado, b["t0"], b["t1"], T, destaque, tam=170 if tipo == "gancho" else 140)
    elif tipo == "item":
        n = str(d.get("numero", ""))
        e = ease(u / 0.25)
        f = fonte("titulo", 330)
        s = f"#{n}" if n else ""
        w = f.measureText(s)
        tem_desenho = bool(d.get("desenho"))
        c.save()
        c.translate(CX_SEGURO, 330 if tem_desenho else 560)
        esc = (1.6 - 0.6 * e) * (0.6 if tem_desenho else 1.0)
        c.scale(esc, esc)
        c.drawString(s, -w / 2, 110, f, cheio(T["destaque"], 210 * e, blur=40))
        c.drawString(s, -w / 2, 110, f, cheio(T["destaque"], 255 * e))
        c.restore()
        if tem_desenho:
            desenho(c, d, u, contexto.get("base", "."), 640, 700, 400)
        else:
            rotulo(c, d.get("rotulo"), 330, T, 255 * e)
        texto_cinetico(c, t, tela, falado, b["t0"], b["t1"], T, destaque, cy=930, tam=118, max_linhas=3)
    elif tipo in ("quiz", "revela"):
        q = contexto["quiz"] if tipo == "revela" else d
        opcoes = q.get("opcoes", [])
        certa = q.get("certa", -1)
        pergunta = (q.get("tela") or "") if tipo == "quiz" else (q.get("tela") or "")
        u_quiz = t - (contexto["quiz_seg0"] if tipo == "revela" else b["seg0"])
        if tipo == "quiz":
            texto_cinetico(c, t, pergunta, falado, b["t0"], b["t1"], T, destaque, cy=470, tam=96, max_linhas=3)
        else:
            f = fonte("titulo", 80)
            for i, li in enumerate(quebrar(pergunta.upper(), f, LARG)[:3]):
                w = f.measureText(li)
                c.drawString(li, CX_SEGURO - w / 2, 430 + i * 86, f, cheio(T["texto"], 150))
        revela = 0.0 if tipo == "quiz" else ease(u / 0.35)
        n = max(len(opcoes), 1)
        alt = min(150, 520 / n) if contexto.get("apresentador") is None else min(136, 460 / n)  # cabe acima do apresentador
        for i, op in enumerate(opcoes):
            e = ease((u_quiz - 0.35 - 0.18 * i) / 0.3)
            if e <= 0:
                continue
            y = 800 + i * (alt + 26)
            dx = 60 * (1 - e)
            r = skia.Rect(ZS["x0"] + 10 + dx, y, ZS["x1"] - 10 + dx, y + alt)
            ok = i == certa
            borda = T["certo"] if (revela and ok) else T["destaque2"]
            a = 255 * e * (1 - 0.65 * revela * (not ok and certa >= 0))
            cartao(c, r, borda, a, T, brilho=revela if ok else 0.0, preenchido=revela if ok else 0.0)
            letra = "ABCD"[i]
            fl = fonte("titulo", int(alt * 0.5))
            c.drawCircle(r.left() + alt * 0.5, r.centerY(), alt * 0.32, cheio(borda, a))
            wl = fl.measureText(letra)
            c.drawString(letra, r.left() + alt * 0.5 - wl / 2, r.centerY() + alt * 0.18, fl, cheio(T["fundo"], a))
            ft = caber("titulo", str(op).upper(), int(alt * 0.42), r.width() - alt * 1.2, minimo=30)
            c.drawString(str(op).upper(), r.left() + alt * 1.0, r.centerY() + alt * 0.15, ft, cheio(T["texto"], a))
        cont = q.get("contagem", 0)
        if tipo == "quiz" and cont and t >= b["t1"]:
            k = t - b["t1"]
            resta = max(0, math.ceil(cont - k))
            if resta:
                cx, cy, r = CX_SEGURO, 700, 52
                c.drawCircle(cx, cy, r, traco(T["fundo2"], 12))
                prog = (k % 1.0)
                arco = skia.Path()
                arco.addArc(skia.Rect(cx - r, cy - r, cx + r, cy + r), -90, 360 * (1 - prog))
                c.drawPath(arco, traco(T["destaque3"], 12))
                f = fonte("titulo", 76)
                s = str(resta)
                c.drawString(s, cx - f.measureText(s) / 2, cy + 27, f, cheio(T["texto"]))
    elif tipo == "imagem":
        img = imagem(contexto["base"] / d["imagem"]) if d.get("imagem") else None
        if img:
            lado = 1 if b["i"] % 2 else -1
            k = suave(u / max(dur, 0.1))
            _cobrir(c, img, 1.0 + 0.10 * k, lado * 40 * (k - 0.5), -20 * k)
            _degrade_texto(c)
        else:
            _sem_imagem(c, d.get("imagem"), T)
        rotulo(c, d.get("rotulo"), Y_TOPO, T, 255 * ease(u / 0.3))
        texto_cinetico(c, t, tela, falado, b["t0"], b["t1"], T, destaque, cy=1040, tam=104, max_linhas=3)
    elif tipo == "antes_depois":
        antes = imagem(contexto["base"] / d["antes"]) if d.get("antes") else None
        depois = imagem(contexto["base"] / d["depois"]) if d.get("depois") else None
        k = suave((u - 0.6) / max(dur * 0.55, 0.5))
        corte = W * k
        if antes:
            _cobrir(c, antes, 1.04, 0, 0)
        else:
            _sem_imagem(c, d.get("antes"), T)
        if depois:
            c.save()
            c.clipRect(skia.Rect(0, 0, corte, H))
            _cobrir(c, depois, 1.04, 0, 0)
            c.restore()
        if 0 < k < 1:
            c.drawRect(skia.Rect(corte - 4, 0, corte + 4, H), cheio(T["texto"], 240))
            c.drawRect(skia.Rect(corte - 14, 0, corte + 14, H), cheio(T["destaque"], 120, blur=14))
        f = fonte("titulo", 64)
        for s, x, a in (("ANTES", ZS["x0"] + 20, 255 * (1 - k)), ("DEPOIS", ZS["x1"] - 20, 255 * k)):
            w = f.measureText(s)
            xx = x if s == "ANTES" else x - w
            r = skia.Rect(xx - 22, Y_TOPO - 66, xx + w + 22, Y_TOPO + 20)
            c.drawRRect(skia.RRect.MakeRectXY(r, 20, 20), cheio(T["fundo"], 200 * a / 255))
            c.drawString(s, xx, Y_TOPO, f, cheio(T["destaque"] if s == "DEPOIS" else T["texto"], a))
        texto_cinetico(c, t, tela, falado, b["t0"], b["t1"], T, destaque, cy=1080, tam=100, max_linhas=2)
    elif tipo == "cta":
        e = ease(u / 0.35)
        s = (tela or "SEGUE PRA VER A PARTE 2").upper()
        f = caber("titulo", s, 92, LARG - 80, minimo=40)
        w = f.measureText(s)
        pulso = 1 + 0.03 * math.sin(u * 6)
        r = skia.Rect(CX_SEGURO - w / 2 - 50, Y_TEXTO - 90, CX_SEGURO + w / 2 + 50, Y_TEXTO + 70)
        c.save()
        c.translate(CX_SEGURO, Y_TEXTO)
        c.scale(pulso * (0.7 + 0.3 * e), pulso * (0.7 + 0.3 * e))
        c.translate(-CX_SEGURO, -Y_TEXTO)
        rr = skia.RRect.MakeRectXY(r, 80, 80)
        c.drawRRect(rr, cheio(T["destaque3"], 170 * e, blur=34))
        c.drawRRect(rr, cheio(T["destaque3"], 255 * e))
        c.drawString(s, CX_SEGURO - w / 2, Y_TEXTO + 30, f, cheio((255, 255, 255), 255 * e))
        c.restore()
    elif tipo == "voto":
        rotulo(c, "VOCÊS DECIDEM", Y_TOPO, T, 255 * ease(u / 0.3))
        texto_cinetico(c, t, tela, falado, b["t0"], b["t1"], T, destaque, cy=560, tam=100, max_linhas=3)
        for i, op in enumerate(d.get("opcoes", [])[:2]):
            e = ease((u - 0.4 - 0.25 * i) / 0.3)
            if e <= 0:
                continue
            corop = T["opcao1"] if i == 0 else T["opcao2"]
            y = 820 + i * 210
            r = skia.Rect(ZS["x0"] + 20, y, ZS["x1"] - 20, y + 170)
            cartao(c, r, corop, 255 * e, T, brilho=0.5 + 0.5 * math.sin(u * 4 + i * 3) ** 2, preenchido=0.4)
            f = caber("titulo", f"{i + 1}  {str(op).upper()}", 92, r.width() - 80, minimo=40)
            s = f"{i + 1}  {str(op).upper()}"
            c.drawString(s, r.centerX() - f.measureText(s) / 2, r.centerY() + 33, f, cheio((255, 255, 255), 255 * e))


def quadro(c, t, linha, T, contexto, com_legenda=True):
    """Um quadro completo: fundo, bloco da vez com câmera viva e flash, acabamento e legenda."""
    blocos = linha["blocos"]
    b = blocos[-1]
    for x in blocos:
        if x["seg0"] <= t < x["seg1"]:
            b = x
            break
    if b["tipo"] == "revela":
        anteriores = [x for x in blocos if x["tipo"] == "quiz" and x["seg0"] < b["seg0"]]
        if anteriores:
            contexto["quiz"] = anteriores[-1]["dados"]
            contexto["quiz_seg0"] = anteriores[-1]["seg0"]
        else:
            contexto["quiz"], contexto["quiz_seg0"] = {}, b["seg0"]
    _NO_GANCHO[0] = b is blocos[0]
    contexto["primeiro"] = blocos[0]
    u = t - b["seg0"]
    fundo(c, t, T)
    c.save()
    camera(c, u, b["seg1"] - b["seg0"])
    bloco(c, t, b, T, contexto)
    c.restore()
    if contexto.get("apresentador") is not None:
        contexto["apresentador"].desenhar(c, t, b, T)
    if b["seg0"] > 0.05:  # sem flash no quadro 0: o clarão cobria o gancho
        flash(c, u, T)
    acabamento(c, t, T)
    return b


def legenda_do_quadro(c, t, b, T):
    if b["tipo"] in ("cta",) or not b["palavras"] or not LEG.get("ativa", True):
        return
    falado = [(tp, p) for tp, p in b["palavras"] if tp <= t + 0.03]
    if falado and t > b["t1"] + 0.35:
        return
    cor_chave = hex_rgb(LEG["cor_destaque"]) if LEG.get("cor_destaque") else T["destaque"]
    legenda(c, t, falado, chave=b["dados"].get("destaque", []), cor_chave=cor_chave, tam=int(LEG.get("tamanho", 64)))


def capa(saida, titulo, T, destaque=(), rotulo_capa=None):
    """Capa 1080x1920: fundo da série, título grande com brilho dentro do recorte 3:4 do centro."""
    sup = skia.Surface(W, H)
    c = sup.getCanvas()
    fundo(c, 2.0, T)
    if rotulo_capa:
        rotulo(c, rotulo_capa, 560, T, tam=40)
    texto = titulo.upper()
    tam = 170
    f = fonte("titulo", tam)
    linhas = quebrar(texto, f, LARG)
    while len(linhas) > 4 and tam > 70:
        tam -= 10
        f = fonte("titulo", tam)
        linhas = quebrar(texto, f, LARG)
    chaves = {norm(x) for x in destaque}
    passo = tam * 1.04
    y = 960 - (len(linhas) - 1) * passo / 2 + tam * 0.36
    for li in linhas:
        ws = li.split()
        esp = f.measureText(" ")
        total = sum(f.measureText(w) for w in ws) + esp * (len(ws) - 1)
        x = W / 2 - total / 2
        for w in ws:
            corw = T["destaque"] if norm(w) in chaves else T["texto"]
            c.drawString(w, x, y, f, traco((0, 0, 0), 22))
            c.drawString(w, x, y, f, cheio(corw, 200, blur=26))
            c.drawString(w, x, y, f, cheio(corw))
            x += f.measureText(w) + esp
        y += passo
    acabamento(c, 2.0, T)
    img = sup.makeImageSnapshot()
    Path(saida).parent.mkdir(parents=True, exist_ok=True)
    img.save(str(saida), skia.kJPEG, 92)
    return saida
