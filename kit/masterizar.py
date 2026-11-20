# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Masterização em um passo: mix -> loudnorm (2 passadas) -> estéreo 48 kHz -> checagem de volume e de pico.

Uso:
    python masterizar.py <mix.wav> [outro.wav ...] -o <mix_norm.wav> [--lufs -14] [--pico -1.5]
    python masterizar.py --verificar <arquivo.wav|video.mp4>

- Vários arquivos de entrada são somados (sem normalizar cada um) antes do loudnorm.
- Alvo padrão (config.audio): -14 LUFS integrados, pico real -1,5 dBTP, LRA 11; saída sempre ESTÉREO 48 kHz
  (mono deixou prévia muda em celular: lição real).
- A checagem mede de novo o arquivo final e sai com erro (código 1) se o volume, o pico, os canais ou a taxa
  estiverem fora. Use o --verificar também no vídeo final antes de publicar (no vídeo o pico tolera +1 dB,
  porque o AAC sobe o pico real; o WAV master tolera +0,5 dB).
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(KIT))

from config import CFG, ffmpeg, ffprobe  # noqa: E402

A = CFG["audio"]


def _roda(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def medir_loudnorm(arq, lufs, pico, lra):
    r = _roda([ffmpeg(), "-hide_banner", "-nostats", "-i", str(arq), "-af",
               f"loudnorm=I={lufs}:TP={pico}:LRA={lra}:print_format=json", "-f", "null", "-"])
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S)
    if not m:
        raise SystemExit("loudnorm não devolveu medição:\n" + r.stderr[-1500:])
    return json.loads(m.group(0))


def medir(arq):
    """Volume integrado (LUFS), pico real (dBTP), canais e taxa do áudio de um arquivo (wav ou vídeo)."""
    r = _roda([ffmpeg(), "-hide_banner", "-nostats", "-i", str(arq), "-map", "0:a:0", "-af", "ebur128=peak=true",
               "-f", "null", "-"])
    resumo = r.stderr[r.stderr.rfind("Summary:"):]
    integ = re.search(r"I:\s*(-?[\d.]+|-inf)\s*LUFS", resumo)
    pico = re.search(r"Peak:\s*(-?[\d.]+|-inf)\s*dBFS", resumo)
    p = _roda([ffprobe(), "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=channels,sample_rate",
               "-of", "json", str(arq)])
    st = (json.loads(p.stdout or "{}").get("streams") or [{}])[0]
    return dict(lufs=float(integ.group(1)) if integ else None, pico_dbtp=float(pico.group(1)) if pico else None,
                canais=int(st.get("channels", 0)), taxa=int(st.get("sample_rate", 0)))


def conferir(m, lufs, pico, taxa, margem_pico=0.5):
    erros = []
    if m["lufs"] is None or abs(m["lufs"] - lufs) > 1.0:
        erros.append(f"volume {m['lufs']} LUFS fora de {lufs}±1")
    if m["pico_dbtp"] is None or m["pico_dbtp"] > pico + margem_pico:
        erros.append(f"pico {m['pico_dbtp']} dBTP acima de {pico + margem_pico:.1f}")
    if m["canais"] != 2:
        erros.append(f"{m['canais']} canal(is): precisa ser estéreo")
    if m["taxa"] != taxa:
        erros.append(f"taxa {m['taxa']} Hz: precisa ser {taxa}")
    return erros


def masterizar(entradas, saida, lufs, pico, lra, taxa):
    saida = Path(saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        fonte = Path(entradas[0])
        if len(entradas) > 1:  # mix: soma simples, o loudnorm acerta o volume depois
            fonte = Path(tmp) / "mix.wav"
            cmd = [ffmpeg(), "-v", "error", "-y"]
            for e in entradas:
                cmd += ["-i", str(e)]
            cmd += ["-filter_complex", f"amix=inputs={len(entradas)}:normalize=0:duration=longest",
                    "-ac", "2", "-c:a", "pcm_f32le", str(fonte)]
            subprocess.run(cmd, check=True)
        m = medir_loudnorm(fonte, lufs, pico, lra)
        filtro = (f"loudnorm=I={lufs}:TP={pico}:LRA={lra}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
                  f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:"
                  f"linear=true,aresample={taxa}")
        subprocess.run([ffmpeg(), "-v", "error", "-y", "-i", str(fonte), "-af", filtro, "-ar", str(taxa), "-ac", "2",
                        "-c:a", "pcm_s24le", str(saida)], check=True)
    return saida


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entradas", nargs="+")
    ap.add_argument("-o", "--saida")
    ap.add_argument("--lufs", type=float, default=float(A["lufs"]))
    ap.add_argument("--pico", type=float, default=float(A["pico_dbtp"]))
    ap.add_argument("--lra", type=float, default=float(A["lra"]))
    ap.add_argument("--verificar", action="store_true", help="só mede e confere o arquivo")
    a = ap.parse_args()
    taxa = int(A["taxa"])
    if a.verificar:
        alvo = Path(a.entradas[0])
    else:
        if not a.saida:
            ap.error("informe -o saida.wav")
        alvo = masterizar(a.entradas, a.saida, a.lufs, a.pico, a.lra, taxa)
    m = medir(alvo)
    # Codificador com perda (AAC no vídeo) sobe o pico real em até ~1 dB: tolerância maior fora do WAV.
    margem = 0.5 if alvo.suffix.lower() in (".wav", ".flac") else 1.0
    erros = conferir(m, a.lufs, a.pico, taxa, margem)
    print(json.dumps({"arquivo": str(alvo), **m, "ok": not erros, "erros": erros}, ensure_ascii=False))
    if erros:
        print("MASTER_FALHOU: " + "; ".join(erros))
        sys.exit(1)
    print("MASTER_OK")


if __name__ == "__main__":
    main()
