# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import canais as C  # noqa: E402


def main():
    ap = argparse.ArgumentParser(prog="python -m canais", description="Vários canais no mesmo estúdio.")
    ap.add_argument("--novo", metavar="NOME", help="guarda o canal em uso e começa um canal novo")
    ap.add_argument("--usar", metavar="ID", help="troca para outro canal (o id aparece na lista)")
    a = ap.parse_args()
    try:
        if a.novo:
            c = C.novo(a.novo)
            print(f"CANAL NOVO: {c['nome']} ({c['id']}). Falta configurar: rode comandos/instalar.md ou abra o painel.")
        elif a.usar:
            c = C.usar(a.usar)
            print(f"EM USO: {c['nome']}" + (f" (@{c['arroba']})" if c["arroba"] else ""))
        else:
            lista = C.listar()
            if not lista:
                print("Nenhum canal ainda.")
            for c in lista:
                marca = "  <- em uso" if c["ativo"] else ""
                print(f"{c['id']:30s} {c['nome']}" + (f" (@{c['arroba']})" if c["arroba"] else "") + marca)
    except C.ErroCanal as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
