# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Personagem do canal em um comando: personagem.json -> partes do boneco -> folha do personagem.

Uso (da pasta kit/):
    python personagem_novo.py <nome> --descricao "Rita, 40 anos, eletricista" \\
        [--cores '{"pele": "#C98B63", "roupa": "#F2B33D", "calca": "#2F4A6B"}'] [--acessorios bone oculos] [--cilios]
    python personagem_novo.py <nome> --folha      # só refaz a folha de um personagem que já existe

Cores aceitas: pele, roupa, calca, sapato, iris, cabelo, acessorio. Acessórios: oculos, laco, bone, cachecol, topete.
Saída em personagens/<nome>/: as partes do boneco (o mesmo que a série, as cartelas e o painel usam) e folha.png,
o personagem em 5 poses (parado, falando, susto, apontando, comemorando) para o usuário ver antes do 1º vídeo.

Todo vídeo do estúdio tem personagem (comandos/novo-video.md). Este é o caminho para criar o do canal quando ainda
não existe: o apresentador das cartelas e o Boneco da série passam a usar este personagem.
"""
import argparse
import json
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(KIT))

from config import pasta  # noqa: E402

CORES = ("pele", "roupa", "calca", "sapato", "iris", "cabelo", "acessorio")
ACESSORIOS = ("oculos", "laco", "bone", "cachecol", "topete")
EXEMPLOS = ("lola", "nico")      # personagens de exemplo do kit: não contam como personagem do canal


def personagem_do_canal():
    """Nome do personagem próprio do canal (a pasta mais nova em personagens/ fora os exemplos), ou None."""
    raiz = pasta("personagens")
    proprios = [d for d in raiz.iterdir() if d.is_dir() and d.name not in EXEMPLOS and (d / "partes.json").is_file()] \
        if raiz.is_dir() else []
    return max(proprios, key=lambda d: (d / "partes.json").stat().st_mtime).name if proprios else None


def _poses():
    from maquina.rig import MEDO
    medo = {k: dict(v) for k, v in MEDO.items()}
    return [
        ("PARADO", {"visema": "R"}),
        ("FALANDO", {"visema": "A", "braco_d": {"rot": -30}, "antebraco_d": {"rot": -30}}),
        ("SUSTO", {**medo, "visema": "O", "braco_d": {"rot": -110}, "braco_e": {"rot": 110},
                   "antebraco_d": {"rot": -50}, "antebraco_e": {"rot": 50}}),
        ("APONTANDO", {"visema": "E", "braco_d": {"rot": -125}, "antebraco_d": {"rot": -10},
                       "olhar": (0.5, -0.15)}),
        ("COMEMORANDO", {"visema": "feliz", "braco_d": {"rot": -150}, "braco_e": {"rot": 150}, "pulo": 40}),
    ]


def folha(nome):
    import skia

    from maquina.desenho import fonte, texto_c
    from maquina.rig import Boneco
    b = Boneco(nome)
    larg, alt, alt_boneco = 2000, 1000, 560
    surf = skia.Surface(larg, alt)
    c = surf.getCanvas()
    c.clear(skia.Color(244, 240, 232))
    info = json.loads((pasta("personagens") / nome / "personagem.json").read_text(encoding="utf-8"))
    texto_c(c, nome.upper(), larg / 2, 110, fonte("titulo", 84), (30, 26, 40))
    texto_c(c, info.get("descricao", "")[:110], larg / 2, 175, fonte("texto", 32), (90, 84, 100))
    poses = _poses()
    passo = larg / len(poses)
    pe = 860
    for i, (rotulo, pose) in enumerate(poses):
        x = passo * (i + 0.5)
        c.drawOval(skia.Rect.MakeLTRB(x - 120, pe - 14, x + 120, pe + 18), skia.Paint(Color=skia.Color(0, 0, 0, 40),
                   AntiAlias=True))
        b.desenhar(c, x, pe - pose.get("pulo", 0), alt_boneco, pose)
        texto_c(c, rotulo, x, pe + 90, fonte("titulo", 36), (60, 54, 72))
    arq = pasta("personagens") / nome / "folha.png"
    surf.makeImageSnapshot().save(str(arq), skia.kPNG)
    return arq


def criar(nome, descricao, cores=None, acessorios=(), cilios=False):
    from maquina.molde import PADRAO
    cores = cores or {}
    ruins = [k for k in cores if k not in CORES]
    if ruins:
        raise SystemExit(f"ERRO: cor desconhecida: {', '.join(ruins)}.\nO QUE FAZER: use só {', '.join(CORES)}.")
    fora = [a for a in acessorios if a not in ACESSORIOS]
    if fora:
        raise SystemExit(f"ERRO: acessório desconhecido: {', '.join(fora)}.\nO QUE FAZER: use só {', '.join(ACESSORIOS)}.")
    destino = pasta("personagens") / nome
    destino.mkdir(parents=True, exist_ok=True)
    molde = {**PADRAO, **cores, "acessorios": list(acessorios), "cilios": bool(cilios)}
    (destino / "personagem.json").write_text(json.dumps({"descricao": descricao, "molde": molde}, ensure_ascii=False,
                                                        indent=2), encoding="utf-8")
    import construir_boneco
    construir_boneco.construir(nome, "auto")
    return folha(nome)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("nome", help="nome curto, sem espaço nem acento (ex.: rita)")
    ap.add_argument("--descricao", help="quem é, em uma linha")
    ap.add_argument("--cores", help="JSON com as cores (pele, roupa, calca, sapato, iris, cabelo, acessorio)")
    ap.add_argument("--acessorios", nargs="*", default=[])
    ap.add_argument("--cilios", action="store_true")
    ap.add_argument("--folha", action="store_true", help="só refaz a folha de um personagem que já existe")
    a = ap.parse_args()
    nome = a.nome.strip().lower()
    if not nome.isascii() or not nome.replace("_", "").isalnum():
        raise SystemExit("ERRO: nome com espaço, acento ou símbolo.\nO QUE FAZER: use só letras sem acento (ex.: rita).")
    if a.folha:
        arq = folha(nome)
    else:
        if not a.descricao:
            raise SystemExit("ERRO: falta a descrição.\nO QUE FAZER: passe --descricao \"quem é, em uma linha\".")
        arq = criar(nome, a.descricao, json.loads(a.cores) if a.cores else None, a.acessorios, a.cilios)
    print(f"PERSONAGEM_OK {nome}\n  folha: {arq}\n  Mostre a folha ao usuário. A partir de agora, as cartelas e a série "
          f"usam este personagem.")


if __name__ == "__main__":
    main()
