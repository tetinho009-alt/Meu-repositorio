# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Folha de contato: junta stills (PNG 1080x1920) numa grade, com o nome de cada estilo por baixo.
Uso: python folha.py saida.png col largura_celula img1.png[:rótulo] img2.png[:rótulo] ..."""
import sys

import skia

import motor as M


def main():
    saida, col, cel = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    itens = []
    for a in sys.argv[4:]:
        arq, _, rot = a.partition("::")
        itens.append((arq, rot or arq.rsplit("\\", 1)[-1].rsplit("/", 1)[-1].rsplit(".", 1)[0]))
    alt = int(cel * 16 / 9)
    faixa = int(cel * 0.16)
    linhas = (len(itens) + col - 1) // col
    s, cv = M.superficie(col * cel + (col + 1) * 16, linhas * (alt + faixa) + (linhas + 1) * 16)
    cv.clear(M.cor((18, 18, 22)))
    for k, (arq, rot) in enumerate(itens):
        x, y = 16 + (k % col) * (cel + 16), 16 + (k // col) * (alt + faixa + 16)
        img = skia.Image.open(arq)
        cv.drawImageRect(img, skia.Rect(x, y, x + cel, y + alt), skia.SamplingOptions(skia.FilterMode.kLinear))
        M.texto(cv, rot, x + cel / 2, y + alt + faixa * 0.62, faixa * 0.42, (235, 235, 240), negrito=True,
                alinhar="centro")
    M.salvar_png(M.pixels(s), saida)
    print("FOLHA_OK", saida)


if __name__ == "__main__":
    main()
