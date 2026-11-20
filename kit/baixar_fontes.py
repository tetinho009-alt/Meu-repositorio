# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Baixa as fontes do kit das fontes oficiais, com os textos de licença (todas SIL Open Font License 1.1).

- Anton (títulos do vídeo) e IBM Plex Mono (selos): repositório oficial do Google Fonts (github.com/google/fonts).
- Archivo Black (título da capa) e Barlow Bold (apoio da capa): repositório oficial do Google Fonts.
- Inter ExtraBold/SemiBold (legenda e textos): release oficial do autor (github.com/rsms/inter).

Uso: python baixar_fontes.py [--pasta PASTA]   (padrão: pastas.fontes do config)
Só usa a biblioteca padrão do Python: roda igual no Windows, macOS, Linux e na nuvem.
"""
import argparse
import io
import sys
import urllib.request
import zipfile
from pathlib import Path

KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(KIT))

GF = "https://raw.githubusercontent.com/google/fonts/main/ofl"
DIRETOS = {
    "Anton-Regular.ttf": f"{GF}/anton/Anton-Regular.ttf",
    "Anton-OFL.txt": f"{GF}/anton/OFL.txt",
    "IBMPlexMono-SemiBold.ttf": f"{GF}/ibmplexmono/IBMPlexMono-SemiBold.ttf",
    "IBMPlexMono-OFL.txt": f"{GF}/ibmplexmono/OFL.txt",
    "ArchivoBlack-Regular.ttf": f"{GF}/archivoblack/ArchivoBlack-Regular.ttf",
    "ArchivoBlack-OFL.txt": f"{GF}/archivoblack/OFL.txt",
    "Barlow-Bold.ttf": f"{GF}/barlow/Barlow-Bold.ttf",
    "Barlow-OFL.txt": f"{GF}/barlow/OFL.txt",
}
INTER_ZIP = "https://github.com/rsms/inter/releases/download/v4.1/Inter-4.1.zip"
INTER = {"extras/ttf/Inter-ExtraBold.ttf": "Inter-ExtraBold.ttf", "extras/ttf/Inter-SemiBold.ttf": "Inter-SemiBold.ttf",
         "LICENSE.txt": "Inter-OFL.txt"}


def baixar(url):
    req = urllib.request.Request(url, headers={"User-Agent": "temporada-viral-kit"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pasta")
    a = ap.parse_args()
    if a.pasta:
        destino = Path(a.pasta)
    else:
        from config import pasta
        destino = pasta("fontes")
    destino.mkdir(parents=True, exist_ok=True)
    for nome, url in DIRETOS.items():
        alvo = destino / nome
        if not alvo.is_file():
            alvo.write_bytes(baixar(url))
        print("ok", nome)
    if not all((destino / n).is_file() for n in INTER.values()):
        print("baixando Inter (release oficial, ~34 MB)...", flush=True)
        with zipfile.ZipFile(io.BytesIO(baixar(INTER_ZIP))) as z:
            for interno, nome in INTER.items():
                (destino / nome).write_bytes(z.read(interno))
    for nome in INTER.values():
        print("ok", nome)
    print(f"FONTES_OK em {destino}")


if __name__ == "__main__":
    main()
