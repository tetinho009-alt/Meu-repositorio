# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Gera as imagens dos exemplos de 10 s que usam imagem (antes e depois, bastidores e faceless), tudo por código e
sem gastar crédito. As imagens já vêm prontas no kit; rode só se quiser refazer.

Uso (da pasta kit/): python ../exemplos/estilos/imagens.py
"""
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
KIT = AQUI.parents[1] / "kit"
sys.path.insert(0, str(KIT))

import skia  # noqa: E402

from maquina.desenho import H, W, cheio, fonte, quebrar, radial, traco  # noqa: E402


def salvar(sup, arq):
    arq.parent.mkdir(parents=True, exist_ok=True)
    sup.makeImageSnapshot().save(str(arq), skia.kJPEG, 88)
    print("ok", arq.relative_to(AQUI))


def capa_fraca(arq):
    """Antes: a capa que ninguém para pra ver (fundo chapado, letra pequena, sem contraste, sem foco)."""
    sup = skia.Surface(W, H)
    c = sup.getCanvas()
    c.drawRect(skia.Rect(0, 0, W, H), cheio((128, 132, 140)))
    f = fonte("texto", 44)
    for i, li in enumerate(["meu vídeo de hoje", "sobre umas curiosidades", "dos animais parte 1"]):
        c.drawString(li, 120, 860 + i * 60, f, cheio((205, 208, 212)))
    salvar(sup, arq)


def capa_forte(arq):
    """Depois: a mesma ideia com o padrão do kit (fundo escuro com brilho, título enorme, palavra-chave na cor)."""
    from cartelas import visual as V
    T = V.tema({"fundo": "#041419", "destaque": "#FFD23F", "destaque2": "#2FD3C4", "destaque3": "#FF4F8B"})
    V.capa(arq, "O bicho que dorme de mãos dadas", T, destaque=["MÃOS", "DADAS"], rotulo_capa="TOP 3")
    print("ok", arq.relative_to(AQUI))


def roteiro_na_tela(arq):
    """Bastidores 1: o roteiro.json aberto, como num editor."""
    sup = skia.Surface(W, H)
    c = sup.getCanvas()
    c.drawRect(skia.Rect(0, 0, W, H), cheio((12, 16, 24)))
    janela = skia.Rect(70, 470, W - 70, 1000)
    c.drawRRect(skia.RRect.MakeRectXY(janela, 28, 28), cheio((22, 28, 40)))
    c.drawRRect(skia.RRect.MakeRectXY(janela, 28, 28), traco((60, 72, 96), 3))
    for i, cor in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
        c.drawCircle(120 + i * 44, 515, 13, cheio(cor))
    c.drawString("roteiro.json", 270, 527, fonte("mono", 34), cheio((150, 160, 180)))
    linhas = [
        ('  "estilo": "top5",', (47, 211, 196)), ('  "voz": "grátis",', (47, 211, 196)),
        ('  "apresentador": "lola",', (47, 211, 196)),
        ('    "gancho": "3 bichos que',  (255, 210, 63)), ('       dormem esquisito"', (255, 210, 63)),
        ('    "item 3": "a lontra"', (255, 79, 139)), ('    "item 2": "o golfinho"', (255, 79, 139)),
        ('    "item 1": "a girafa"', (255, 79, 139))]
    f = fonte("mono", 40)
    for i, (s, cor) in enumerate(linhas):
        c.drawString(f"{i + 1:>2}", 100, 610 + i * 46, f, cheio((80, 92, 116)))
        c.drawString(s, 190, 610 + i * 46, f, cheio(cor))
    salvar(sup, arq)


def folha_de_quadros(arq, quadros):
    """Bastidores 2: a folha de quadros que o kit mostra antes do render (o still de cada bloco)."""
    sup = skia.Surface(W, H)
    c = sup.getCanvas()
    c.drawRect(skia.Rect(0, 0, W, H), cheio((10, 14, 22)))
    img = skia.Image.open(str(quadros)) if quadros and Path(quadros).is_file() else None
    if img:
        larg = W - 120
        alt = larg * img.height() / img.width()
        y = 520
        r = skia.Rect.MakeXYWH(60, y, larg, alt)
        c.drawRect(r.makeOutset(10, 10), cheio((255, 210, 63), 200, blur=24))
        c.drawImageRect(img, r, skia.SamplingOptions(skia.FilterMode.kLinear))
    salvar(sup, arq)


def paisagens(pasta):
    """Faceless: três quadros do estilo desenhado, sem nenhum rosto (estrada, cidade e cemitério na neblina)."""
    import estilo_desenhado as G
    from estilo_desenhado import paisagens as PS
    for nome, cena in (("estrada", PS.estrada_neblina), ("cidade", PS.cidadezinha), ("cemiterio", PS.cemiterio)):
        sup = skia.Surface(W, H)
        c = sup.getCanvas()
        with G.quadro(c, 1.0, **G.tinta.NOITE):
            cena(c, 1.0)
        salvar(sup, pasta / f"{nome}.jpg")


if __name__ == "__main__":
    capa_fraca(AQUI / "antes-depois" / "antes.jpg")
    capa_forte(AQUI / "antes-depois" / "depois.jpg")
    roteiro_na_tela(AQUI / "bastidores" / "roteiro.jpg")
    folha = KIT / "trabalho" / "exemplo_top5" / "folha.jpg"
    folha_de_quadros(AQUI / "bastidores" / "quadros.jpg", folha)
    paisagens(AQUI / "faceless")
