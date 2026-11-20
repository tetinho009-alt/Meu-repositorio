# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Peças de tela da série interativa: abertura, selo de ficção, cartão de regra, cartão de voto, apuração e pílula
de seguir. Tudo dentro da zona segura da configuração (x 120–900, y 280–1250 por padrão).

Texto do voto: "VOCÊS DECIDEM" e "A ESCOLHA DA GALERA VIRA A PARTE N". Nunca "comente a palavra" nem
"curte e compartilha": pedido de comentário/curtida com palavra exata é o exemplo clássico de engagement bait
que as redes rebaixam. A pergunta é da história; as opções ficam na tela com número e palavra (vale os dois).
"""
import math

import skia

from config import CFG, cor as cor_cfg

from .desenho import (CX_SEGURO, LARG_SEGURA, ZS, H, W, caber, cheio, degrade, ease, fonte, largura_espacada, quebrar,
                      texto_c, texto_espacado, traco)

OPCOES = (cor_cfg("opcao1"), cor_cfg("opcao2"))
DESTAQUE = cor_cfg("destaque")
TEXTO = cor_cfg("texto")
X0, X1, Y0, Y1 = ZS["x0"], ZS["x1"], ZS["y0"], ZS["y1"]


def _pop(t, ini, dur):
    return ease((t - ini) / dur)


def abertura(c, t, t0, serie, sub, dur=2.6, y=640):
    """Nome da série gigante com brilho e subtítulo mono espaçado ("Parte N · título"). Entra e sai em 0,3 s."""
    u = t - t0
    a = _pop(u, 0.05, 0.3) * (1 - _pop(u, dur, 0.3))
    if a <= 0:
        return
    nome = serie.upper()
    f = caber("titulo", nome, 230, LARG_SEGURA, minimo=90, espaco=6)
    tam = f.getSize()
    yb = y + tam * 0.36
    for sigma, alfa in ((tam * 0.32, 0.6), (tam * 0.11, 0.9)):  # brilho largo + brilho perto
        texto_espacado(c, nome, CX_SEGURO, yb, f, DESTAQUE, 255 * alfa * a, 6, blur=sigma)
    texto_espacado(c, nome, CX_SEGURO, yb, f, (237, 232, 255), 255 * a, 6)
    sub = sub.upper()
    fs = caber("mono", sub, 44, LARG_SEGURA, minimo=22, espaco=10)
    texto_espacado(c, sub, CX_SEGURO, yb + 90, fs, tuple(min(255, v + 50) for v in DESTAQUE), 255 * a, 10)


def selo(c, texto, y=305, a=255):
    """Selo fixo no topo da zona segura, ex.: "SÉRIE · PARTE 1 · FICÇÃO". Ficção declarada no vídeo."""
    texto = texto.upper()
    f = caber("mono", texto, 30, LARG_SEGURA - 44, minimo=16, espaco=4)
    larg = largura_espacada(texto, f, 4)
    c.drawRoundRect(skia.Rect.MakeXYWH(CX_SEGURO - larg / 2 - 20, y - 27, larg + 40, 52), 12, 12, cheio((14, 11, 12), 180 * a / 255))
    texto_espacado(c, texto, CX_SEGURO, y + 10, f, TEXTO, a, 4)


def cartao_regra(c, t, t0, numero, texto, dur=4.0, y=620):
    """Cartão "REGRA N" (o público ama regra): entra com batida, fica `dur` s."""
    u = t - t0
    if u < 0 or u > dur:
        return
    k = ease(u / 0.25) * (1 - ease((u - dur + 0.3) / 0.3))
    fs = fonte("texto", 46)
    linhas = quebrar(texto, fs, LARG_SEGURA - 80)
    alto = 150 + 58 * len(linhas)
    esc = 1 + 0.12 * (1 - ease(u / 0.2))
    c.save()
    c.translate(CX_SEGURO, y)
    c.scale(esc, esc)
    r = skia.Rect.MakeXYWH(-LARG_SEGURA / 2, 0, LARG_SEGURA, alto)
    c.drawRoundRect(r, 22, 22, cheio((10, 8, 16), 225 * k))
    c.drawRoundRect(r, 22, 22, traco(OPCOES[0], 5, 255 * k))
    texto_c(c, f"REGRA {numero}", 0, 86, fonte("titulo", 70), OPCOES[0], 255 * k)
    for j, ln in enumerate(linhas):
        texto_c(c, ln, 0, 150 + j * 58, fs, (255, 255, 255), 255 * k)
    c.restore()


def cartao_voto(c, t, t0, pergunta, opcoes, duracao, parte_seguinte=2, escurece=200):
    """Tela de voto até o fim do vídeo.

    `opcoes` = [(palavra, consequência curta), (palavra, consequência curta)]; cores fixas da configuração
    (opção 1 âmbar, opção 2 roxo por padrão). Destaque alterna entre as opções; pavio queimando com contagem.
    """
    u = t - t0
    if u < 0:
        return
    k = ease(u / 0.3)
    c.drawRect(skia.Rect.MakeWH(W, H), cheio((0, 0, 0), escurece * k))
    selo_txt = f"PARTE {parte_seguinte - 1} · ESCOLHA"
    fs = fonte("titulo", 30)
    w = fs.measureText(selo_txt) + 40
    c.drawRoundRect(skia.Rect.MakeXYWH(CX_SEGURO - w / 2, 360, w, 48), 8, 8, cheio(DESTAQUE, 255 * k))
    texto_c(c, selo_txt, CX_SEGURO, 395, fs, (255, 255, 255), 255 * k)
    fp = caber("titulo", pergunta.upper(), 86, LARG_SEGURA, minimo=50)
    linhas = quebrar(pergunta.upper(), fp, LARG_SEGURA)
    if len(linhas) > 1:
        fp = fonte("titulo", 64)
        linhas = quebrar(pergunta.upper(), fp, LARG_SEGURA)[:2]
    for j, ln in enumerate(linhas):
        texto_c(c, ln, CX_SEGURO, 500 + j * 72, fp, (255, 255, 255), 255 * k)
    y_ops = 500 + 72 * (len(linhas) - 1) + 50
    ativo = int(u / 1.2) % len(opcoes)
    for j, (palavra, sub) in enumerate(opcoes):
        kj = ease((u - 0.2 - j * 0.15) / 0.3)
        y = y_ops + j * 200
        r = skia.Rect.MakeXYWH(X0 + (1 - kj) * 60, y, LARG_SEGURA, 170)
        on = j == ativo
        cor = OPCOES[j % 2]
        c.drawRoundRect(r, 20, 20, cheio((18, 18, 28), 255 * kj))
        c.drawRoundRect(r, 20, 20, traco(cor if on else (90, 90, 110), 5 if on else 3, 255 * kj))
        c.drawRoundRect(skia.Rect.MakeXYWH(r.left() + 26, y + 45, 80, 80), 14, 14, traco(cor, 4, 255 * kj))
        texto_c(c, str(j + 1), r.left() + 66, y + 110, fonte("titulo", 56), cor, 255 * kj)
        c.drawString(f"OPÇÃO {j + 1}", r.left() + 128, y + 44, fonte("mono", 22), cheio(cor, 255 * kj))
        fw = caber("titulo", palavra.upper(), 70, LARG_SEGURA - 160, minimo=36)
        c.drawString(palavra.upper(), r.left() + 128, y + 112, fw, cheio(cor if on else (255, 255, 255), 255 * kj))
        fsub = caber("texto", sub, 26, LARG_SEGURA - 160, minimo=16)
        c.drawString(sub, r.left() + 130, y + 150, fsub, cheio((170, 170, 190), 255 * kj))
    resta = max(0.0, duracao - u)
    by = y_ops + len(opcoes) * 200 + 20
    xf = X0 + LARG_SEGURA * resta / max(duracao, 1e-3)  # pavio queimando da direita para a esquerda
    c.drawLine(X0, by, X1, by, traco((60, 52, 70), 6, 255 * k))
    c.drawLine(X0, by, xf, by, traco(OPCOES[0], 6, 255 * k))
    c.drawCircle(xf, by, 24, cheio((255, 170, 60), 120 * k, blur=12))
    c.drawCircle(xf, by, 7, cheio((255, 250, 220), 255 * k))
    c.drawString("VOCÊS DECIDEM", X0, by + 60, fonte("titulo", 44), cheio((255, 255, 255), 255 * k))
    seg = f"0:{int(math.ceil(resta)):02d}"
    fc = fonte("titulo", 44)
    c.drawString(seg, X1 - fc.measureText(seg), by + 60, fc, cheio(OPCOES[0] if resta < 3 else (255, 255, 255), 255 * k))
    linha = f"A ESCOLHA DA GALERA VIRA A PARTE {parte_seguinte}"
    fl = caber("mono", linha, 26, LARG_SEGURA, minimo=14)
    c.drawString(linha, X0, by + 104, fl, cheio((190, 190, 210), 255 * k))
    return by + 104  # base da última linha (para conferência da zona segura)


def pilula_seguir(c, t, t0, t1, perfil=None, y=300):
    """Pílula "+ SEGUIR @perfil" (um pedido de seguir por vídeo, nunca junto com o voto)."""
    if not (t0 <= t < t1):
        return
    k = ease((t - t0) / 0.3) * (1 - ease((t - t1 + 0.3) / 0.3))
    txt = f"+ SEGUIR {perfil or CFG['perfil']}"
    f = caber("titulo", txt, 48, LARG_SEGURA - 60, minimo=24)
    w = f.measureText(txt) + 70
    r = skia.Rect.MakeXYWH(CX_SEGURO - w / 2, y - (1 - k) * 50, w, 96)
    c.drawRoundRect(r, 48, 48, cheio(DESTAQUE, 255 * k))
    texto_c(c, txt, CX_SEGURO, r.top() + 64, f, (255, 255, 255), 255 * k)


def apuracao(c, t, t0, pergunta, opcoes, votos, parte=1):
    """Abertura da parte seguinte: a tela racha, cada lado enche com a cor da opção na proporção dos votos, os números
    sobem e o vencedor empurra a divisória. `votos` TEM de ser a contagem real (mínimo sugerido: 10 votos)."""
    u = t - t0
    if u < 0:
        return
    total = max(1, sum(votos))
    pct = [v / total for v in votos]
    vence = 0 if votos[0] >= votos[1] else 1
    c.drawRect(skia.Rect.MakeWH(W, H), cheio((6, 6, 10)))
    empurra = ease((u - 3.3) / 0.9)
    alvo = W * min(0.8, max(0.2, 0.5 + (pct[0] - 0.5) * 1.8))
    xd = W / 2 + (alvo - W / 2) * empurra
    sobe = ease((u - 0.5) / 2.6)
    topo, fundo = 600, 1240
    for j, (x0, x1) in enumerate(((0, xd), (xd, W))):
        cor = OPCOES[j]
        apaga = 0.45 if (u > 4.4 and j != vence) else 1.0
        nivel = fundo - (fundo - topo) * pct[j] * sobe
        onda = skia.Path()
        onda.moveTo(x0, fundo)
        x = x0
        amp = 14 * (1 - ease((u - 3.0) / 1.5)) + 3
        while x <= x1 + 8:
            onda.lineTo(x, nivel + math.sin(x * 0.018 + u * 5 + j * 2) * amp)
            x += 8
        onda.lineTo(x1, fundo)
        onda.close()
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(x0, 0, x1, H))
        claro = tuple(min(255, v + 60) for v in cor)
        c.drawPath(onda, degrade((0, nivel), (0, fundo), [(claro, 235 * apaga), (tuple(v * 0.35 for v in cor), 235 * apaga)]))
        c.drawPath(onda, traco(claro, 4, 220 * apaga))
        # o lado direito da tela é coberto pelos botões: o texto do lado 2 fica dentro de X1
        cx = (max(x0, X0) + min(x1, X1)) / 2
        larg = min(x1, X1) - max(x0, X0)
        texto_c(c, opcoes[j].upper(), cx, topo - 40, caber("titulo", opcoes[j].upper(), 80, max(larg - 20, 60), minimo=28), cor,
                255 * apaga)
        n = int(round(votos[j] * sobe))
        texto_c(c, f"{n}", cx, 960, fonte("titulo", 140 if larg > 330 else 90), (255, 255, 255), 255 * apaga, contorno=10)
        texto_c(c, f"{round(pct[j] * 100 * sobe)}%", cx, 1040, fonte("titulo", 60), (255, 255, 255), 230 * apaga, contorno=8)
        c.restore()
    c.drawRect(skia.Rect.MakeLTRB(xd - 5, topo - 100, xd + 5, fundo + 10), cheio((255, 255, 255), 255 * ease(u / 0.3)))
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, topo - 110), cheio((6, 6, 10)))
    selo_txt = f"PARTE {parte} · RESULTADO"
    fs = fonte("titulo", 32)
    w = fs.measureText(selo_txt) + 40
    c.drawRoundRect(skia.Rect.MakeXYWH(CX_SEGURO - w / 2, 290, w, 52), 8, 8, cheio(DESTAQUE))
    texto_c(c, selo_txt, CX_SEGURO, 328, fs)
    texto_c(c, pergunta.upper(), CX_SEGURO, 420, caber("titulo", pergunta.upper(), 70, LARG_SEGURA, minimo=34))
    texto_c(c, f"{sum(votos)} VOTOS NOS COMENTÁRIOS", CX_SEGURO, 470, fonte("mono", 26), (170, 170, 190))
    kv = ease((u - 4.4) / 0.35)
    if kv > 0:  # carimbo do vencedor com quique
        quique = 1 + 0.25 * math.exp(-(u - 4.4) * 7) * math.cos((u - 4.4) * 20)
        c.save()
        c.translate(CX_SEGURO, 1130)
        c.rotate(-4)
        c.scale(kv * quique, kv * quique)
        txt = f"VENCEU: {opcoes[vence].upper()}"
        f = caber("titulo", txt, 90, LARG_SEGURA - 70, minimo=40)
        tw = f.measureText(txt) + 70
        c.drawRoundRect(skia.Rect.MakeXYWH(-tw / 2, -90, tw, 130), 18, 18, cheio((10, 10, 16), 235))
        c.drawRoundRect(skia.Rect.MakeXYWH(-tw / 2, -90, tw, 130), 18, 18, traco(OPCOES[vence], 8))
        texto_c(c, txt, 0, 12, f, OPCOES[vence])
        c.restore()
    kp = ease((u - 5.4) / 0.3)
    if kp > 0:
        c.drawRect(skia.Rect.MakeLTRB(0, 1170, W, 1250), cheio((6, 6, 10), 225 * kp))
        texto_c(c, f"A PARTE {parte + 1} COMEÇA AGORA", CX_SEGURO, 1228, fonte("titulo", 52), (255, 255, 255), 255 * kp)
