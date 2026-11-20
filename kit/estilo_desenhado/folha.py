# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Folha de prévia do estilo do canal (1080x1920): a caixa de papéis, o elenco de corpo inteiro com o nome e a
ficha do estilo (corte, textura, fontes, semente). É o que o usuário aprova antes de fechar o estilo, ou pede "sorteia de novo".

Uso (da pasta kit/):
    python -m estilo_desenhado.folha [saida.jpg]          # padrão: <pastas.trabalho>/estilo/folha.jpg
    ESTILO_JSON=outro.json python -m estilo_desenhado.folha teste.jpg
"""
import sys
from pathlib import Path

import numpy as np
import skia

from . import tinta as T
from .elenco import PAPEIS, pessoa
from .estilo import PERGUNTAS

W, H = 1080, 1920
KIT = Path(__file__).resolve().parents[1]


def _fonte(nome, tam):
    import os
    try:
        from config import pasta
        arq = pasta("fontes") / nome
    except Exception:
        arq = Path(os.environ.get("ESTILO_FONTES", KIT / "fontes")) / nome
    tf = skia.Typeface.MakeFromFile(str(arq)) if arq.is_file() else skia.Typeface.MakeDefault()
    return skia.Font(tf, tam)


def _texto(c, s, x, y, tam, cor, nome, centro=True):
    f = _fonte(nome, tam)
    larg = f.measureText(s)
    c.drawString(s, x - larg / 2 if centro else x, y, f, skia.Paint(AntiAlias=True, Color=T.cor_skia(cor)))


def desenhar(c, t=0.0):
    e = T.ESTILO
    R, F = e["respostas"], e["fontes"]
    with T.quadro(c, t, W, H):
        c.clear(T.cor_skia(T.PAPEL))
        # a caixa de papéis: cada cor um quadrado de papel recortado, colado torto, com a sombra dura
        cores = [("papel", e["paleta"]["papel"]), ("escuro", e["paleta"]["tinta"]), ("destaque", e["paleta"]["destaque"])]
        cores += [(f"papel {k + 1}", p) for k, p in enumerate(e["paleta"].get("papeis", []))]
        d = T.Desenho()
        for k, (n, cor) in enumerate(cores[:8]):
            x = 70 + (k % 4) * 245
            y = 220 + (k // 4) * 120
            q = np.array([(x, y), (x + 200, y + 4 * (k % 2)), (x + 198, y + 90), (x + 2, y + 92)])
            T.peca(d, q, tuple(cor), 500 + k, sombra=1.6)
        d.desenha(c)
        # elenco de corpo inteiro, no chão
        chao = 1500
        c.drawRect(skia.Rect.MakeLTRB(0, chao, W, H), skia.Paint(Color=T.cor_skia(T.mistura(T.PAPEL, T.SOMBRA, 0.25), 140)))
        for k, papel in enumerate(("adulto", "protagonista", "idoso")):
            x = 210 + k * 330
            b = pessoa(papel)
            b.desenhar(c, x, chao, 820 if papel != "idoso" else 760, {"t": t, "olhar": ((1 - k) * 0.4, 0.0)})
            _texto(c, PAPEIS[papel], x, chao + 90, 46, T.TINTA, F["titulo"])
            _texto(c, papel, x, chao + 135, 26, T.TINTA, F["texto"])
    # ficha (fora da gradação, para ler a cor de verdade)
    _texto(c, "ESTILO DO CANAL", W / 2, 150, 92, T.TINTA, F["titulo"])
    ficha = f"{R['clima']} · {R.get('recorte', R.get('traco', ''))} · {R['cor']} · {R['proporcao']} · {R['textura']}"
    _texto(c, ficha, W / 2, 490, 30, T.TINTA, F["texto"])
    _texto(c, f"semente {e['semente']}  ·  título: {Path(F['titulo']).stem}", W / 2, 1830, 26, T.TINTA, F["texto"])


def main():
    saida = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if saida is None:
        try:
            sys.path.insert(0, str(KIT))
            from config import pasta
            saida = pasta("trabalho") / "estilo" / "folha.jpg"
        except Exception:
            saida = KIT / "folha_estilo.jpg"
    saida.parent.mkdir(parents=True, exist_ok=True)
    sup = skia.Surface(W, H)
    desenhar(sup.getCanvas())
    img = sup.makeImageSnapshot()
    img.save(str(saida), skia.kJPEG, 90)
    print(f"FOLHA_OK {saida}")


if __name__ == "__main__":
    main()
