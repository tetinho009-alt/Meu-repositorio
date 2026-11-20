# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Capa do episódio a partir do episodio.json: elenco recortado (rig + luz de cinema) + molde de capa.

Uso:
    python capa.py <episodio.json> <saida.jpg> [--arte PNG] [--cpu]
    python capa.py <episodio.json> <saida.jpg> --redes        # 3 capas: <saida>_ig.jpg, _tiktok.jpg, _youtube.jpg
    python capa.py <episodio.json> <saida.jpg> --redes --tema desenhado   # capa no estilo próprio do canal

Sem --arte, o elenco sai do personagem do episódio (campo "personagem" ou lista "elenco").
A pergunta da capa repete as opções do voto ("ENTRAR OU FUGIR?").
--redes: a mesma arte nas 3, cada uma diagramada para a sua rede. Instagram: "USE FONE · SEGUE PRA VER A PARTE 2".
TikTok: tudo dentro do recorte 3:4 que o app mostra (y 240 a 1680). YouTube (Shorts): mais exagerada, com o gancho
gigante no alto (campo "gancho" do episodio.json; sem ele, o título), elenco maior e sem a pergunta. O elenco é
renderizado uma vez só.
--tema desenhado (ou "estilo": "desenhado" no kit/config.json): elenco e capa no estilo sorteado para o canal
(kit/estilo.json, ver comandos/criar-estilo.md).
"""
import argparse
import json
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(KIT))

from config import CFG  # noqa: E402
from maquina.capa import capa, elenco  # noqa: E402
from maquina.rig import MEDO  # noqa: E402


def _gancho(ep):
    """Gancho da capa: o campo "gancho" do episodio.json (texto ou lista de linhas) ou, sem ele, o título."""
    g = ep.get("gancho") or ep["titulo"]
    return " ".join(g) if isinstance(g, list) else g


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episodio")
    ap.add_argument("saida")
    ap.add_argument("--arte", help="PNG com fundo transparente no lugar do elenco")
    ap.add_argument("--redes", action="store_true", help="uma capa por rede, com o CTA de cada uma")
    ap.add_argument("--tema", choices=("padrao", "desenhado"), help="padrão: o \"estilo\" do config.json")
    ap.add_argument("--sangra", default="", help="lados do elenco cortados reto que saem pra fora da capa: esq,dir")
    ap.add_argument("--dissolve", default="", help="lados do elenco cortados reto que somem em degradê: topo,esq,dir")
    ap.add_argument("--cpu", action="store_true")
    a = ap.parse_args()
    ep = json.loads(Path(a.episodio).read_text(encoding="utf-8"))
    a.sangra = [s.strip() for s in a.sangra.split(",") if s.strip()]
    a.dissolve = [s.strip() for s in a.dissolve.split(",") if s.strip()]
    saida = Path(a.saida)
    if (a.tema or CFG.get("estilo", "padrao")) == "desenhado":
        return capa_desenhada(ep, saida, a)
    arte = a.arte
    if not arte:
        nomes = ep.get("elenco") or [ep["personagem"]]
        n = len(nomes)
        atores = [dict(nome=nm, x=540 + (k - (n - 1) / 2) * 380, pe=1650, altura=1150 if k == 0 else 1000,
                       pose={"visema": "O", "olhar": (0.5 if k == 0 else -0.5, -0.2), **MEDO,
                             "braco_d": {"rot": -25}, "antebraco_d": {"rot": -95}})
                  for k, nm in enumerate(nomes)]
        arte = elenco(atores, saida.with_name(saida.stem + "_elenco.png"), cpu=a.cpu)
    op = [o[0] for o in ep["opcoes"]]
    args = (arte, f"PARTE {ep['parte']} · {ep['titulo'].upper()}", ep["serie"].upper(), f"{op[0]} ou {op[1]}?".upper())
    if not a.redes:
        capa(*args, f"USE FONE · VOCÊS DECIDEM A PARTE {ep['parte'] + 1}", saida, sangra=a.sangra, dissolve=a.dissolve)
        print(f"CAPA_OK {saida}")
        return
    from cta_redes import REDES, texto_cta
    for _pasta, sufixo, modelo in REDES:
        destino = saida.with_name(f"{saida.stem}_{sufixo}{saida.suffix}")
        capa(*args, f"USE FONE · {texto_cta(modelo, ep['parte'], None)}", destino, rede=sufixo,
             gancho=_gancho(ep), sangra=a.sangra, dissolve=a.dissolve)
        print(f"CAPA_OK {destino}")


def capa_desenhada(ep, saida, a):
    from estilo_desenhado import capa as D
    nomes = ep.get("elenco") or [ep.get("personagem", "protagonista")]
    arte = a.arte or D.elenco(nomes, saida.with_name(saida.stem + "_elenco.png"))
    op = [o[0] for o in ep["opcoes"]]
    args = (arte, f"PARTE {ep['parte']}", ep["serie"].upper(), _gancho(ep).upper(), f"{op[0]} ou {op[1]}?".upper())
    redes = (("ig", "_ig"), ("tiktok", "_tiktok"), ("youtube", "_youtube")) if a.redes else (("ig", ""),)
    for rede, sufixo in redes:
        destino = saida.with_name(f"{saida.stem}{sufixo}{saida.suffix}")
        D.gera(*args, destino, rede=rede, sangra=a.sangra, dissolve=a.dissolve)
        print(f"CAPA_OK {destino}")


if __name__ == "__main__":
    main()
