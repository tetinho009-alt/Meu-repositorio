# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Trava de espaço: com a câmera mexendo, só a interface pode ficar parada na tela.

Num plano com câmera andando, tudo que não é interface (céu, lua, nuvem, corvo, galho e mato do primeiro plano,
neblina com desenho) tem que andar na tela junto com a câmera. O que fica parado enquanto o cenário anda está grudado
na tela: o olho lê como "dimensão errada".

Como mede: desenha o quadro três vezes, com a câmera normal, girada 1,2 grau pro lado e inclinada 1,2 grau
(cenario3d.PERTURBA; tudo anda uns 20 px na tela em qualquer profundidade). Bloco de 12 px com desenho (desvio de
luminância > 5) que não mudou nas DUAS versões mexidas está grudado (duas direções porque uma borda reta que desliza ao
longo de si mesma parece parada numa só). Grupo de 3 blocos ou mais reprova.

No seu episódio (plano com câmera andando), desenhe o quadro numa função e chame:
    from qa.espaco import confere
    grudados = confere(lambda c: meu_plano(c, t))     # [] = passou
A câmera do plano tem que ser uma CamG criada DENTRO da função (é na criação que a perturbação entra), e o primeiro
plano tem que receber `ref` (a câmera do primeiro quadro do plano).

Uso direto (da pasta kit/), conferindo as cenas abertas do estilo desenhado:
    python qa/espaco.py [--imagens pasta]
Sai com código 1 se algum plano reprovar.
"""
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT))

import numpy as np  # noqa: E402
import skia  # noqa: E402
from scipy import ndimage  # noqa: E402

from estilo_desenhado import cenario3d as C3  # noqa: E402

W, H = 1080, 1920
GIROS = ((0.0, 0.0, 0.0, 1.2, 0.0), (0.0, 0.0, 0.0, 0.0, 1.2))   # dx, dh, dz, dyaw, dpitch
BLOCO = 12
LIMIAR_DETALHE = 5.0
LIMIAR_PARADO = 0.6
MIN_BLOCOS = 3


def _quadro(desenha):
    sup = skia.Surface.MakeRaster(skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType))
    c = sup.getCanvas()
    c.clear(skia.Color4f(0, 0, 0, 1))
    desenha(c)
    a = sup.toarray(colorType=skia.kRGBA_8888_ColorType)[:, :, :3].astype(np.float32)
    return 0.3 * a[:, :, 0] + 0.59 * a[:, :, 1] + 0.11 * a[:, :, 2]


def _blocos(x, fn):
    h, w = H // BLOCO, W // BLOCO
    return fn(x[: h * BLOCO, : w * BLOCO].reshape(h, BLOCO, w, BLOCO), axis=(1, 3))


def confere(desenha, imagem=None):
    """Desenha o quadro normal e com a câmera mexida; devolve os grupos grudados na tela [(x0, y0, x1, y1, blocos)]."""
    C3._BANDAS.clear()
    base = _quadro(desenha)
    parado = None
    for giro in GIROS:
        C3._BANDAS.clear()
        C3.PERTURBA = giro
        try:
            mexido = _quadro(desenha)
        finally:
            C3.PERTURBA = None
        p = _blocos(np.abs(mexido - base), np.mean) < LIMIAR_PARADO
        parado = p if parado is None else (parado & p)
    detalhe = _blocos(base, np.std) > LIMIAR_DETALHE
    grudado = parado & detalhe
    lab, n = ndimage.label(grudado)
    grupos = []
    for k in range(1, n + 1):
        ys, xs = np.where(lab == k)
        if len(ys) >= MIN_BLOCOS:
            grupos.append((xs.min() * BLOCO, ys.min() * BLOCO, (xs.max() + 1) * BLOCO, (ys.max() + 1) * BLOCO, len(ys)))
    if imagem and grupos:
        from PIL import Image, ImageDraw
        im = Image.fromarray(base.astype(np.uint8)).convert("RGB")
        d = ImageDraw.Draw(im)
        for x0, y0, x1, y1, _ in grupos:
            d.rectangle((x0, y0, x1, y1), outline=(255, 40, 40), width=4)
        im.save(imagem)
    return grupos


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    from estilo_desenhado import paisagens as PS
    pasta = Path(sys.argv[sys.argv.index("--imagens") + 1]) if "--imagens" in sys.argv else None
    falhas = 0
    for nome in ("cemiterio", "estrada_neblina", "cidadezinha", "quintal"):
        cena = getattr(PS, nome)
        orig = cena(skia.Surface(8, 8).getCanvas(), 1.0).cam._orig   # a câmera padrão da cena

        def plano(c, cena=cena, orig=orig):
            cam = C3.CamG(*orig)                       # criada aqui: a perturbação da trava entra nela
            cena(c, 1.0, cam=cam, ref=cam.original())  # primeiro plano ancorado na câmera de composição
        grupos = confere(plano, imagem=(pasta / f"espaco_{nome}.png") if pasta else None)
        print(f"  {'ok   ' if not grupos else 'FALHA'} {nome}: {len(grupos)} grupo(s) grudado(s) na tela"
              + "".join(f"\n        x{x0}-{x1} y{y0}-{y1} ({b} blocos)" for x0, y0, x1, y1, b in grupos))
        falhas += bool(grupos)
    if falhas:
        sys.exit(1)
    print("ESPACO_OK")


if __name__ == "__main__":
    main()
