# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Tempo de cada palavra DO ROTEIRO na narração gravada -> tempos.json (base da legenda e da linha do tempo).

Uso:
    python alinhar.py <audio> <blocos.txt> <saida.json> [--modo whisper|provedor] [--palavras ARQ] [--cpu]

- whisper (padrão): faster-whisper com tempo por palavra; GPU (CUDA, float16) se houver, senão CPU (int8).
- provedor: usa os tempos que o provedor de voz devolveu (`<audio>.palavras.json` do narrar.py, ex.: ElevenLabs),
  sem rodar modelo nenhum.
Nos dois modos a legenda usa a grafia do roteiro; palavra não reconhecida é interpolada.
Confira no resumo se nenhuma tag de direção ([whispers]...) foi lida em voz alta.
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(KIT))

from config import CFG, caminho, ffmpeg  # noqa: E402
from maquina.alinhamento import alinhar_palavras, resumo  # noqa: E402


def _dlls_cuda():
    """No Windows, as DLLs de cuDNN/cuBLAS do PyTorch (se instalado) servem ao CTranslate2."""
    if os.name != "nt":
        return
    try:
        import importlib.util
        spec = importlib.util.find_spec("torch")
        if spec and spec.origin:
            lib = Path(spec.origin).parent / "lib"
            if lib.is_dir():
                os.add_dll_directory(str(lib))
                os.environ["PATH"] = str(lib) + os.pathsep + os.environ.get("PATH", "")
    except Exception:
        pass


def ouvir_whisper(audio, cpu=False):
    from faster_whisper import WhisperModel

    pcm = subprocess.run([ffmpeg(), "-v", "error", "-i", str(audio), "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    amostras = np.frombuffer(pcm, dtype=np.float32)
    pasta_m = CFG["whisper"].get("pasta_modelos") or None
    kw = {"download_root": str(caminho(pasta_m))} if pasta_m else {}
    tentativas = [("cpu", "int8")]
    if not cpu:
        try:
            _dlls_cuda()
            import ctranslate2
            if ctranslate2.get_cuda_device_count() > 0:
                tentativas.insert(0, ("cuda", "float16"))
        except Exception:
            pass
    for disp, tipo in tentativas:
        try:
            modelo = WhisperModel(CFG["whisper"]["modelo"], device=disp, compute_type=tipo, **kw)
            segs, _ = modelo.transcribe(amostras, language="pt", word_timestamps=True)
            ouvidas = [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]
            print(f"Whisper {CFG['whisper']['modelo']} em {disp} ({tipo})", flush=True)
            return ouvidas
        except Exception as e:  # CUDA sem cuDNN/cuBLAS, por exemplo: tenta a próxima opção (CPU)
            if disp == "cpu":
                raise
            print(f"Whisper na GPU falhou ({type(e).__name__}: {e}); usando CPU", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("audio")
    ap.add_argument("blocos")
    ap.add_argument("saida")
    ap.add_argument("--modo", choices=["whisper", "provedor"], default="whisper")
    ap.add_argument("--palavras", help="arquivo de tempos do provedor (padrão: <audio>.palavras.json)")
    ap.add_argument("--cpu", action="store_true", help="força o Whisper na CPU")
    a = ap.parse_args()
    blocos = [ln.strip() for ln in Path(a.blocos).read_text(encoding="utf-8").splitlines() if ln.strip()]
    if a.modo == "provedor":
        arq = Path(a.palavras) if a.palavras else Path(a.audio).with_suffix(".palavras.json")
        ouvidas = [tuple(p) for p in json.loads(arq.read_text(encoding="utf-8"))]
    else:
        ouvidas = ouvir_whisper(a.audio, a.cpu)
    res, casadas = alinhar_palavras(blocos, ouvidas)
    Path(a.saida).parent.mkdir(parents=True, exist_ok=True)
    Path(a.saida).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(resumo(res, blocos))
    print(f"ALINHAR_OK palavras {len(res)}, casadas {casadas} ({100 * casadas / max(1, len(res)):.0f}%) -> {a.saida}")
    if casadas < 0.7 * len(res):
        print("AVISO: menos de 70% das palavras casaram; ouça o áudio (tag lida? texto diferente do roteiro?)")


if __name__ == "__main__":
    main()
