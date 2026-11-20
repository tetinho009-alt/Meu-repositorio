# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Roda o episódio de demonstração de ponta a ponta:

    voz (opcional) -> tempos de palavra -> trilha estéreo -> masterização -> render -> checagem do áudio do vídeo
    -> grade de QA -> capa

Uso:
    python exemplo/rodar.py                 # usa o mp3 de exemplo que vem no kit (sem baixar modelo nenhum)
    python exemplo/rodar.py --cpu           # força render na CPU + libx264 (prova da queda automática)
    python exemplo/rodar.py --voz kokoro    # gera a narração de novo (kokoro, piper, azure, elevenlabs)
    python exemplo/rodar.py --stills        # só os quadros-marco, para conferir rápido

Saída em <pastas.trabalho>/<série>_p<parte>[_cpu]/: o vídeo, folha.jpg (marcos), qa/qa_grade_*.jpg e capa.jpg.
"""
import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent


def _acha_kit(aqui):
    """Pasta do kit: a primeira acima deste arquivo que tem maquina/ (ou a variável MAQUINA_KIT)."""
    import os
    for d in (aqui, *aqui.parents):
        if (d / "maquina" / "__init__.py").is_file():
            return d
    if os.environ.get("MAQUINA_KIT"):
        return Path(os.environ["MAQUINA_KIT"])
    raise SystemExit("não achei a pasta do kit; defina MAQUINA_KIT")


KIT = _acha_kit(AQUI)
sys.path.insert(0, str(KIT))

from config import pasta  # noqa: E402
from maquina import slug  # noqa: E402

PY = sys.executable


def passo(nome, args):
    print(f"\n== {nome}", flush=True)
    t0 = time.perf_counter()
    r = subprocess.run([PY, *[str(a) for a in args]], cwd=str(KIT))
    if r.returncode:
        raise SystemExit(f"FALHOU em: {nome}")
    print(f"   ({time.perf_counter() - t0:.1f} s)", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cpu", action="store_true")
    ap.add_argument("--voz", help="provedor para gerar a narração de novo (padrão: usa o mp3 de exemplo)")
    ap.add_argument("--voz-id", help="voz do provedor")
    ap.add_argument("--stills", action="store_true")
    ap.add_argument("--trabalho", help="pasta de saída")
    a = ap.parse_args()
    ep = json.loads((AQUI / "episodio.json").read_text(encoding="utf-8"))
    nome = f"{slug(ep['serie'])}_p{ep['parte']}" + ("_cpu" if a.cpu else "")
    trab = Path(a.trabalho) if a.trabalho else pasta("trabalho") / nome
    trab.mkdir(parents=True, exist_ok=True)
    aud = trab / "audio"
    aud.mkdir(exist_ok=True)
    if a.voz:
        extra = ["--voz", a.voz_id] if a.voz_id else []
        passo("voz", [KIT / "narrar.py", AQUI / "narrador.txt", aud / "narrador.mp3", "--provedor", a.voz, *extra])
        palavras = aud / "narrador.palavras.json"
        modo = ["--modo", "provedor"] if palavras.is_file() else []
        passo("tempos de palavra", [KIT / "alinhar.py", aud / "narrador.mp3", AQUI / "narrador.txt", aud / "tempos.json",
                                    *modo, *(["--cpu"] if a.cpu else [])])
    elif (AQUI / "audio" / "tempos.json").is_file():  # áudio que acompanha o episódio (no exemplo: o mp3 de demonstração)
        for arq in ("narrador.mp3", "tempos.json"):
            shutil.copy2(AQUI / "audio" / arq, aud / arq)
    elif not (aud / "tempos.json").is_file():
        raise SystemExit("sem narração: rode com --voz kokoro (ou piper, azure, elevenlabs)")
    passo("trilha", [AQUI / "trilha.py", "--audio", aud, "--trabalho", trab])
    passo("masterização", [KIT / "masterizar.py", aud / "mix.wav", "-o", aud / "mix_norm.wav"])
    render = [AQUI / "ep.py", "--trabalho", trab, *(["--cpu"] if a.cpu else []), *(["--stills"] if a.stills else [])]
    passo("render", render)
    if a.stills:
        print(f"\nSTILLS_OK {trab / 'folha.jpg'}")
        return
    video = next(trab.glob(f"*_p{ep['parte']}.mp4"))
    passo("áudio do vídeo", [KIT / "masterizar.py", "--verificar", video])
    passo("grade de QA", [KIT / "qa_grade.py", video, "--zona"])
    passo("capa", [KIT / "capa.py", AQUI / "episodio.json", trab / "capa.jpg", *(["--cpu"] if a.cpu else [])])
    print(f"\nEXEMPLO_OK {video}")


if __name__ == "__main__":
    main()
