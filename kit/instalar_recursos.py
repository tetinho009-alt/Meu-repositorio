# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Instala o que falta para o estúdio, só com receitas fixas. O chat do painel roda este script em vez de pip à mão,
para quem nunca abriu um terminal não precisar abrir.

Uso (a partir de kit/):
  python instalar_recursos.py --conferir       mostra o que já está instalado
  python instalar_recursos.py base             núcleo do kit (render, som, capa)
  python instalar_recursos.py voz-gratis       voz grátis no computador (Kokoro), com teste de uma frase
  python instalar_recursos.py tempos           tempo de cada palavra (Whisper)
  python instalar_recursos.py ffmpeg           gravador de vídeo (ffmpeg), sem terminal e sem winget
  python instalar_recursos.py estudo           estudar vídeos de referência (leitor de links; o Whisper é a receita tempos)
  python instalar_recursos.py estudo --atualizar   põe o leitor de links na versão mais nova (o YouTube muda)
"""
import argparse
import importlib.util
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent

RECEITAS = {
    "base": {"nome": "o núcleo do kit (render, som, capa)", "pip": ["-r", str(AQUI / "requirements.txt")],
             "modulos": ["skia", "numpy", "scipy", "PIL", "requests"]},
    "voz-gratis": {"nome": "a voz grátis no computador (Kokoro)",
                   "pip": ["kokoro>=0.9.4", "misaki[en]>=0.9.4", "espeakng-loader", "phonemizer-fork", "soundfile"],
                   "modulos": ["kokoro"], "python_max": (3, 12)},
    "tempos": {"nome": "o tempo de cada palavra (Whisper)", "pip": ["faster-whisper>=1.1"],
               "modulos": ["faster_whisper"]},
    "ffmpeg": {"nome": "o gravador de vídeo (ffmpeg)", "modulos": []},
    # Só o leitor de links: o Whisper (receita "tempos") entra quando o estudo precisa ouvir um arquivo.
    "estudo": {"nome": "o leitor de links do estudo de vídeos", "pip": ["yt-dlp"], "modulos": ["yt_dlp"]},
}

# ffmpeg sem terminal: as compilações que o ffmpeg.org indica, baixadas para uma pasta do usuário (fora do kit, para
# sobreviver às atualizações). O config.json passa a apontar para elas, e o painel põe a pasta no PATH dos programas
# que abre (alguns scripts chamam "ffmpeg" pelo nome).
PASTA_FFMPEG = Path.home() / ".temporada-viral" / "ffmpeg"
FONTES_FFMPEG = {
    "win32": ["https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"],
    "darwin": ["https://evermeet.cx/ffmpeg/getrelease/zip", "https://evermeet.cx/ffmpeg/getrelease/ffprobe/zip"],
    "linux": ["https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz"],
}

TESTE_KOKORO = ("from kokoro import KPipeline\n"
                "p = KPipeline(lang_code='p', repo_id='hexgrad/Kokoro-82M')\n"
                "n = sum(1 for _ in p('Teste da voz.', voice='pf_dora'))\n"
                "print('VOZ_OK' if n else 'VOZ_VAZIA')\n")


def tem(modulo):
    try:
        return importlib.util.find_spec(modulo) is not None
    except (ImportError, ValueError):
        return False


def exe_ffmpeg(nome="ffmpeg"):
    """Caminho do ffmpeg (ou ffprobe): o da pasta do kit, se instalado por aqui; senão o do sistema."""
    local = PASTA_FFMPEG / (nome + (".exe" if os.name == "nt" else ""))
    return str(local) if local.is_file() else shutil.which(nome)


def _baixar(url, destino):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "temporada-viral"}),
                                timeout=60) as resp:
        total = int(resp.headers.get("Content-Length") or 0)
        feito, aviso = 0, 0
        with open(destino, "wb") as f:
            while True:
                bloco = resp.read(1 << 20)
                if not bloco:
                    break
                f.write(bloco)
                feito += len(bloco)
                if total and feito * 10 // total > aviso:
                    aviso = feito * 10 // total
                    print(f"  baixando: {aviso * 10}% de {total / 1e6:.0f} MB", flush=True)
    return destino


def _extrair(pacote, pasta):
    """Tira só ffmpeg e ffprobe do pacote, direto para `pasta`."""
    nomes = {"ffmpeg", "ffprobe", "ffmpeg.exe", "ffprobe.exe"}
    achados = 0
    if zipfile.is_zipfile(pacote):
        with zipfile.ZipFile(pacote) as z:
            for info in z.infolist():
                nome = info.filename.rsplit("/", 1)[-1]
                if nome in nomes and not info.is_dir():
                    (pasta / nome).write_bytes(z.read(info))
                    achados += 1
    else:
        with tarfile.open(pacote) as t:
            for m in t.getmembers():
                nome = m.name.rsplit("/", 1)[-1]
                if nome in nomes and m.isfile():
                    (pasta / nome).write_bytes(t.extractfile(m).read())
                    achados += 1
    return achados


def _apontar_config(ffmpeg, ffprobe):
    cfg_arq = Path(os.environ.get("MAQUINA_CONFIG") or AQUI / "config.json")
    cfg = json.loads(cfg_arq.read_text(encoding="utf-8")) if cfg_arq.is_file() else {}
    cfg.setdefault("ferramentas", {}).update({"ffmpeg": ffmpeg, "ffprobe": ffprobe})
    cfg_arq.write_text(json.dumps(cfg, indent=1, ensure_ascii=False), encoding="utf-8")


def instalar_ffmpeg():
    if exe_ffmpeg() and exe_ffmpeg("ffprobe"):
        print(f"JA_INSTALADO: o gravador de vídeo (ffmpeg) já está pronto ({exe_ffmpeg()}).")
        return 0
    chave = "win32" if os.name == "nt" else ("darwin" if sys.platform == "darwin" else "linux")
    if chave == "linux" and platform.machine().lower() in ("arm64", "aarch64"):
        FONTES_FFMPEG["linux"] = [FONTES_FFMPEG["linux"][0].replace("linux64", "linuxarm64")]
    PASTA_FFMPEG.mkdir(parents=True, exist_ok=True)
    print("Instalando o gravador de vídeo (ffmpeg). Baixa uns 115 MB e leva de 2 a 6 minutos; o andamento aparece abaixo.", flush=True)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            for i, url in enumerate(FONTES_FFMPEG[chave]):
                pacote = _baixar(url, Path(tmp) / f"pacote{i}")
                if not _extrair(pacote, PASTA_FFMPEG):
                    raise OSError(f"o pacote de {url} não tinha o ffmpeg dentro")
    except (OSError, urllib.error.URLError, zipfile.BadZipFile, tarfile.TarError) as e:
        print(f"ERRO: não consegui baixar o ffmpeg ({e}).\n"
              "O QUE FAZER: confira a internet e peça de novo. Se repetir, mande esta linha no suporte "
              "(painel, 'Falar com o suporte').")
        return 1
    ffmpeg, ffprobe = exe_ffmpeg(), exe_ffmpeg("ffprobe")
    for exe in (ffmpeg, ffprobe):
        if exe and os.name != "nt":
            os.chmod(exe, 0o755)
    try:
        teste = subprocess.run([ffmpeg, "-hide_banner", "-encoders"], capture_output=True, text=True, timeout=60,
                               encoding="utf-8", errors="replace")
        ok = teste.returncode == 0 and "libx264" in teste.stdout
    except (OSError, subprocess.TimeoutExpired, TypeError):
        ok, teste = False, None
    if not ok or not ffprobe:
        print("ERRO: o ffmpeg baixou, mas não abriu neste computador.\n"
              "O QUE FAZER: no painel, em 'Conversar com a IA', abra 'Avançado…' e use 'Abrir a IA aqui' para pedir "
              "\"instala o ffmpeg\"." + (" No Mac com chip Apple, instale antes o Rosetta." if chave == "darwin" else ""))
        return 1
    _apontar_config(ffmpeg, ffprobe)
    placa = " (com gravação na placa da NVIDIA)" if teste and "h264_nvenc" in teste.stdout else ""
    print(f"FFMPEG_OK: o gravador de vídeo está pronto{placa}, em {PASTA_FFMPEG}.")
    return 0


def conferir():
    print(f"Python {sys.version.split()[0]} ({sys.executable})")
    for chave, r in RECEITAS.items():
        if chave == "ffmpeg":
            print(f"  {'OK   ' if exe_ffmpeg() and exe_ffmpeg('ffprobe') else 'FALTA'} ffmpeg: {r['nome']}")
            continue
        ok = all(tem(m) for m in r["modulos"])
        print(f"  {'OK   ' if ok else 'FALTA'} {chave}: {r['nome']}")
    return 0


def instalar(chave, atualizar=False):
    if chave == "ffmpeg":
        return instalar_ffmpeg()
    r = RECEITAS[chave]
    if not atualizar and all(tem(m) for m in r["modulos"]):
        print(f"JA_INSTALADO: {r['nome']} já está pronto neste computador.")
        return _testar(chave)
    teto = r.get("python_max")
    if teto and sys.version_info[:2] > teto:
        print(f"ERRO: {r['nome']} ainda não funciona no Python {sys.version_info[0]}.{sys.version_info[1]} deste "
              f"computador (precisa do {teto[0]}.{teto[1]}).\n"
              "O QUE FAZER: use a voz grátis do Google, que funciona em qualquer computador: no painel, abra "
              "'Chave da voz', cartão Google, siga os 3 passos e cole a chave. Depois peça a voz de novo no chat.")
        return 2
    print(f"Instalando {r['nome']}. Leva alguns minutos; o andamento aparece abaixo.", flush=True)
    cmd = [sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "--progress-bar", "off",
           *(["-U"] if atualizar else []), *r["pip"]]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                            errors="replace")
    ultimas = []
    for linha in proc.stdout:
        linha = linha.rstrip()
        if linha.startswith(("Collecting", "Downloading", "Installing", "Successfully")):
            print("  " + linha[:160], flush=True)
        ultimas = (ultimas + [linha])[-12:]
    proc.wait()
    if proc.returncode != 0:
        print("ERRO: a instalação não terminou. Últimas linhas:\n  " + "\n  ".join(ultimas))
        print("O QUE FAZER: confira a internet e peça de novo. Se repetir, mande estas linhas no suporte "
              "(painel, 'Falar com o suporte').")
        return 1
    print(f"INSTALADO: {r['nome']}.", flush=True)
    return _testar(chave)


def _testar(chave):
    if chave != "voz-gratis":
        return 0
    print("Testando a voz com uma frase (na primeira vez baixa a voz, uns 330 MB)...", flush=True)
    try:
        res = subprocess.run([sys.executable, "-c", TESTE_KOKORO], capture_output=True, text=True, timeout=1200,
                             encoding="utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        print("ERRO: o teste da voz passou de 20 minutos.\nO QUE FAZER: confira a internet e peça de novo.")
        return 1
    if "VOZ_OK" in res.stdout:
        print("VOZ_OK: a voz grátis está funcionando.")
        return 0
    print("ERRO: a voz instalou, mas o teste falhou:\n  " + "\n  ".join((res.stderr or res.stdout).splitlines()[-8:]))
    print("O QUE FAZER: use a voz grátis do Google (painel, 'Chave da voz', cartão Google).")
    return 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("receita", nargs="?", choices=sorted(RECEITAS))
    ap.add_argument("--conferir", action="store_true")
    ap.add_argument("--atualizar", action="store_true", help="instala a versão mais nova mesmo se já tiver")
    a = ap.parse_args()
    if a.conferir or not a.receita:
        return conferir()
    return instalar(a.receita, a.atualizar)


if __name__ == "__main__":
    sys.exit(main())
