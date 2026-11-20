# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Monta (ou atualiza) a pasta do repositório do site do placar a partir do kit.

    python placar/preparar.py <pasta-do-repositorio>

Copia: placar.py, votos.py (a regra única de `maquina/votos.py`), episodios.json (o seu, de `placar/episodios.json`),
site/index.html, site/tiktok_retorno.html e .github/workflows/placar.yml. Não copia chave nenhuma, nem o placar.json
(o GitHub Actions gera), nem os .txt de comentários do TikTok (têm o @ das pessoas: conte no computador e ponha só o
número em `tiktok_votos`). Rode de novo sempre que mudar o episodios.json ou atualizar o kit.
"""
import json
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
KIT = AQUI.parent


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    destino = Path(sys.argv[1]).resolve()
    if KIT in destino.parents or destino == KIT:
        raise SystemExit("o repositório do site fica FORA da pasta do kit (ele é público)")
    eps = AQUI / "episodios.json"
    if not eps.is_file():
        raise SystemExit("crie placar/episodios.json (copie de placar/exemplo/episodios.json e troque pelos seus)")
    conf = json.loads(eps.read_text(encoding="utf-8"))
    for ep in conf.get("episodios", []):
        ep.pop("tiktok_comentarios", None)  # o .txt fica no computador; no site vai só a contagem
    copias = {
        AQUI / "placar.py": destino / "placar.py",
        KIT / "maquina" / "votos.py": destino / "votos.py",
        AQUI / "site" / "index.html": destino / "site" / "index.html",
        AQUI / "site" / "tiktok_retorno.html": destino / "site" / "tiktok_retorno.html",
        AQUI / "placar.yml": destino / ".github" / "workflows" / "placar.yml",
    }
    for origem, alvo in copias.items():
        alvo.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(origem, alvo)
    (destino / "episodios.json").write_text(json.dumps(conf, ensure_ascii=False, indent=1), encoding="utf-8")
    (destino / ".gitignore").write_text("__pycache__/\n*.pyc\n.env\n*segredos*.json\n*.txt\n!site/*.txt\n", encoding="utf-8")
    print(f"PREPARADO {destino}")
    print("Próximos passos: placar/LEIA-ME.md (publicar no GitHub Pages e cadastrar os segredos).")


if __name__ == "__main__":
    main()
