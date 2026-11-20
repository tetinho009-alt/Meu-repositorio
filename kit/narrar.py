# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Gera a narração (ou as falas de um personagem) numa geração só, pelo provedor escolhido.

Uso:
    python narrar.py <texto.txt> <saida.mp3> [--provedor kokoro|piper|azure|elevenlabs|edge] [--voz ID]

`texto.txt` = um bloco por linha (o narrador.txt do episódio). Se o provedor devolver tempo de palavra, grava também
`<saida>.palavras.json`, que o `alinhar.py --modo provedor` usa sem precisar do Whisper.
"""
import argparse
import json
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(KIT))

from config import CFG, ErroConfig  # noqa: E402
from voz import PROVEDORES, ErroVoz, provedor  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("texto")
    ap.add_argument("saida")
    ap.add_argument("--provedor", default=CFG["voz"]["provedor"], choices=list(PROVEDORES))
    ap.add_argument("--voz", default=None, help="id/nome da voz (padrão: o do config)")
    a = ap.parse_args()
    linhas = [ln.strip() for ln in Path(a.texto).read_text(encoding="utf-8").splitlines() if ln.strip()]
    try:
        res = provedor(a.provedor).sintetizar("\n".join(linhas), a.voz, a.saida)
    except (ErroVoz, ErroConfig) as e:
        raise SystemExit(f"VOZ_FALHOU: {e}")
    if res.palavras:
        arq = Path(a.saida).with_suffix(".palavras.json")
        arq.write_text(json.dumps([list(p) for p in res.palavras], ensure_ascii=False, indent=0), encoding="utf-8")
        print(f"tempos do provedor: {arq}")
    print(f"VOZ_OK {res.audio} ({res.provedor}, voz {res.voz})")


if __name__ == "__main__":
    main()
