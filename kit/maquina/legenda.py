# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Legenda palavra a palavra, no tempo real da fala (tempos de `alinhar.py`).

Padrão: caixa alta, fonte de legenda da configuração, no máximo 2 linhas, cada palavra entra com "batida" de escala
em 0,16 s, contorno escuro + sombra suave LOGO ABAIXO (sombra deslocada foi reprovada). Palavras-chave em cor de
destaque; fala de personagem inclinada e na cor da opção 1 (`cores.opcao1` do config).

Posição: dentro da zona segura (x 120–900 por padrão; a direita é coberta pelos botões do TikTok e do Shorts) e
com a BORDA DE BAIXO da legenda acima de `zona_segura.legenda_y_max` (1420 em 1920 por padrão: a faixa de baixo é
coberta pela descrição do post e pelos botões; mais alto que isso a legenda cai no rosto do personagem).
"""
import math

from config import CFG, cor

from .desenho import CX_SEGURO, LARG_SEGURA, cheio, ease, fonte, traco

Y_MAX = float(CFG["zona_segura"]["legenda_y_max"])   # borda de baixo máxima
DESCIDA = 0.30                                        # parte da fonte abaixo da linha de base (com contorno e sombra)
Y_PADRAO = Y_MAX - 74 * DESCIDA - 6                   # linha de base da última linha, encostada no limite
DESTAQUE = cor("opcao1")                              # palavra-chave e fala de personagem


def _limpa(p):
    return p.strip(".,!?:;…\"'“”").upper()


def palavras_do_evento(evento):
    """[(t, palavra)] a partir de um evento da linha do tempo ({"palavras": [[t, palavra], ...]})."""
    return [(float(t), p) for t, p in evento.get("palavras", [])]


def legenda(c, t, palavras, chave=(), y=Y_PADRAO, fala=False, cor_chave=None, tam=74, sumir_apos=0.35):
    """Desenha a legenda no instante t. `palavras` = [(t_inicio, palavra)] em ordem.

    Some `sumir_apos` s depois da última palavra. Mostra as 2 últimas linhas já faladas.
    """
    if y + tam * DESCIDA > Y_MAX + 0.5:
        raise ValueError(f"legenda com base em y={y:.0f} passa da borda de baixo permitida ({Y_MAX:.0f})")
    vis = [(tp, p.upper()) for tp, p in palavras if tp <= t + 0.03]
    if not vis:
        return
    cor_chave = cor_chave or DESTAQUE
    f = fonte("legenda", tam)
    esp = f.measureText(" ")
    larg_max = LARG_SEGURA * 0.98
    linhas, atual, larg = [], [], 0.0
    for tp, p in vis:
        w = f.measureText(p)
        if atual and larg + esp + w > larg_max:
            linhas.append(atual)
            atual, larg = [], 0.0
        atual.append((tp, p, w))
        larg += w + (esp if len(atual) > 1 else 0)
    linhas.append(atual)
    linhas = linhas[-2:]
    alvo = {_limpa(ch) for ch in chave}
    passo = tam * 1.2
    for li, linha in enumerate(linhas):
        total = sum(w for _, _, w in linha) + esp * (len(linha) - 1)
        x = CX_SEGURO - total / 2
        yy = y - (len(linhas) - 1 - li) * passo
        for tp, p, w in linha:
            u = t - tp
            k = ease(u / 0.16)
            esc = 1 + 0.2 * (1 - k) + 0.05 * math.exp(-u * 10) * math.sin(u * 40)
            cor = cor_chave if _limpa(p) in alvo else (DESTAQUE if fala else (255, 255, 255))
            c.save()
            c.translate(x + w / 2, yy)
            c.scale(esc, esc)
            if fala:
                c.skew(-0.12, 0)
            c.drawString(p, -w / 2, 8, f, traco((0, 0, 0), 12, 190 * k, blur=7))   # sombra suave logo abaixo
            c.drawString(p, -w / 2, 0, f, traco((10, 8, 14), 12, 255 * k))        # contorno
            c.drawString(p, -w / 2, 0, f, cheio(cor, 255 * k))
            c.restore()
            x += w + esp


def falas_uniformes(t0, t1, texto):
    """Tempos aproximados para uma fala SEM alinhamento (último recurso; prefira alinhar.py)."""
    ps = texto.split()
    dur = max(t1 - t0, 0.1)
    return [(t0 + dur * j / len(ps), p) for j, p in enumerate(ps)]
