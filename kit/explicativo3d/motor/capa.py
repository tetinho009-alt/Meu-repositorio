# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Capa 1080x1920 a partir de um quadro RGBA do Blender, com a pergunta do gancho dentro do recorte 3:4 do grid do
Instagram (faixa y 240-1680) e da zona segura, para a mesma imagem servir às 3 redes.

    python explicativo3d/motor/capa.py <quadro.png> <saida.jpg> [--topo Y] "LINHA 1" "*LINHA EM AMARELO*" ...

Grava também `<saida>_grid_3x4.jpg`, a prévia de como a capa aparece no grid do perfil.
"""
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import compor as C  # noqa: E402


def capa(quadro, saida, linhas, topo=320):
    cena = Image.open(quadro).convert("RGBA")
    if cena.size != (C.W, C.H):
        cena = cena.resize((C.W, C.H), Image.LANCZOS)
    img = Image.alpha_composite(C.fundo(), cena)
    C.titulo(img, [(t.strip("*"), C.DESTAQUE if t.startswith("*") else C.BRANCO) for t in linhas], topo=topo, tam=124)
    saida = Path(saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(saida, quality=93)
    prev = img.convert("RGB").crop((0, 240, C.W, 1680)).resize((360, 480))
    prev.save(saida.with_name(saida.stem + "_grid_3x4.jpg"), quality=85)
    return saida


def main():
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    quadro, saida, *linhas = sys.argv[1:]
    topo = 320
    if linhas and linhas[0] == "--topo":
        topo, linhas = int(linhas[1]), linhas[2:]
    print(capa(quadro, saida, linhas, topo))


if __name__ == "__main__":
    main()
