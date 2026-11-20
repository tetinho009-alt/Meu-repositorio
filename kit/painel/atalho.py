# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Ícone "Temporada Viral": abre o painel com dois cliques, sem janela preta de terminal.

Uso, a partir da pasta do estúdio, com o mesmo Python do kit:
    python kit/painel/atalho.py --criar      # cria o ícone (área de trabalho e menu Iniciar / Aplicativos)
    python kit/painel/atalho.py --remover    # tira os ícones criados por aqui
    python kit/painel/atalho.py --gerar-app PASTA   # só monta o Temporada Viral.app do Mac em PASTA (conferência)

- Windows: atalho .lnk que roda o servidor com o pythonw (sem console) e o ícone do site (icone.ico).
- Mac: Temporada Viral.app (Info.plist, ícone .icns e um executável que roda o servidor em segundo plano), em
  ~/Applications e na Mesa. O Mac não pede confirmação porque o app é criado aqui mesmo, não baixado.
- Linux: atalho .desktop no menu de aplicativos e na área de trabalho.

Se o painel já estiver aberto, o ícone só abre o navegador de novo (o servidor.py confere sozinho).
Sem dependência além da biblioteca padrão: o .lnk sai do WScript.Shell, chamado pelo PowerShell.
"""
import argparse
import base64
import os
import plistlib
import shutil
import stat
import subprocess
import sys
from pathlib import Path

PAINEL = Path(__file__).resolve().parent
KIT = PAINEL.parent
ESTUDIO = KIT.parent
SERVIDOR = PAINEL / "servidor.py"
NOME = "Temporada Viral"
ICO = PAINEL / "icone.ico"
ICNS = PAINEL / "icone.icns"
PNG = PAINEL / "estatico" / "icone-256.png"
SEM_JANELA = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def _utf8():
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def _versao():
    try:
        return (ESTUDIO / "VERSAO").read_text(encoding="utf-8").strip() or "1.0"
    except OSError:
        return "1.0"


# ---------------------------------------------------------------- Windows

def _python_sem_janela():
    """O pythonw do mesmo Python do kit; senão o lançador pyw; em último caso o python (janela minimizada)."""
    exe = Path(sys.executable)
    w = exe.with_name("pythonw.exe")
    if w.is_file():
        return str(w), []
    pyw = shutil.which("pyw")
    if pyw:
        return pyw, ["-3"]
    return str(exe), []


def _ps_texto(s):
    return "'" + str(s).replace("'", "''") + "'"


def _powershell(script):
    """Roda um script do PowerShell passado em UTF-16 (base64): acento e espaço no caminho não quebram nada."""
    codigo = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
    r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                        "-EncodedCommand", codigo], capture_output=True, timeout=60, creationflags=SEM_JANELA)
    saida = r.stdout.decode("utf-8", "replace") if r.stdout else ""
    return r.returncode, [x.strip() for x in saida.splitlines() if x.strip()]


_PASTAS_WIN = "@([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs'))"


def criar_windows():
    alvo, extra = _python_sem_janela()
    argumentos = " ".join(extra + [f'"{SERVIDOR}"'])
    script = f"""
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$s = New-Object -ComObject WScript.Shell
foreach ($pasta in {_PASTAS_WIN}) {{
  if (-not $pasta) {{ continue }}
  $l = $s.CreateShortcut((Join-Path $pasta {_ps_texto(NOME + '.lnk')}))
  $l.TargetPath = {_ps_texto(alvo)}
  $l.Arguments = {_ps_texto(argumentos)}
  $l.WorkingDirectory = {_ps_texto(ESTUDIO)}
  $l.IconLocation = {_ps_texto(f'{ICO},0')}
  $l.Description = 'Abre o painel do Temporada Viral'
  $l.WindowStyle = 7
  $l.Save()
  Write-Output $l.FullName
}}
"""
    cod, linhas = _powershell(script)
    if cod != 0 or not linhas:
        return False, []
    return True, linhas


def remover_windows():
    script = f"""
[Console]::OutputEncoding = [Text.Encoding]::UTF8
foreach ($pasta in {_PASTAS_WIN}) {{
  $f = Join-Path $pasta {_ps_texto(NOME + '.lnk')}
  if (Test-Path -LiteralPath $f) {{ Remove-Item -LiteralPath $f -Force; Write-Output $f }}
}}
"""
    _, linhas = _powershell(script)
    return linhas


# ---------------------------------------------------------------- Mac

def _aspas_sh(s):
    return "'" + str(s).replace("'", "'\\''") + "'"


EXECUTAVEL_MAC = """#!/bin/bash
# Gerado por kit/painel/atalho.py: abre o painel do Temporada Viral sem o Terminal.
ESTUDIO={estudio}
PY={python}
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
cd "$ESTUDIO" || exit 1
if [ ! -x "$PY" ]; then PY="$(command -v python3)"; fi
if [ -z "$PY" ]; then
  /usr/bin/osascript -e 'display alert "Temporada Viral" message "Não achei o Python. Abra a pasta do estúdio na sua IA e peça: instala o que falta no kit."'
  exit 1
fi
# Em segundo plano: o app termina na hora e o painel fica rodando até ninguém usar por 3 minutos.
nohup "$PY" kit/painel/servidor.py >/dev/null 2>&1 &
exit 0
"""


def gerar_app(pasta):
    """Monta <pasta>/Temporada Viral.app. Devolve o caminho do app."""
    app = Path(pasta) / f"{NOME}.app"
    if app.exists():
        shutil.rmtree(app)
    macos = app / "Contents" / "MacOS"
    recursos = app / "Contents" / "Resources"
    macos.mkdir(parents=True)
    recursos.mkdir(parents=True)
    info = {
        "CFBundleName": NOME, "CFBundleDisplayName": NOME, "CFBundleIdentifier": "com.temporadaviral.painel",
        "CFBundleExecutable": "temporada-viral", "CFBundleIconFile": "icone", "CFBundlePackageType": "APPL",
        "CFBundleShortVersionString": _versao(), "CFBundleVersion": _versao(), "LSMinimumSystemVersion": "10.13",
        "LSUIElement": True, "NSHighResolutionCapable": True,
    }
    with open(app / "Contents" / "Info.plist", "wb") as f:
        plistlib.dump(info, f)
    exe = macos / "temporada-viral"
    exe.write_text(EXECUTAVEL_MAC.format(estudio=_aspas_sh(ESTUDIO), python=_aspas_sh(sys.executable)),
                   encoding="utf-8", newline="\n")
    exe.chmod(exe.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH | stat.S_IRGRP | stat.S_IROTH)
    if ICNS.is_file():
        shutil.copyfile(ICNS, recursos / "icone.icns")
    (app / "Contents" / "PkgInfo").write_text("APPL????", encoding="ascii")
    return app


def _pastas_mac():
    casa = Path.home()
    return [casa / "Applications", casa / "Desktop"]


def criar_mac():
    feitos = []
    for pasta in _pastas_mac():
        try:
            pasta.mkdir(parents=True, exist_ok=True)
            feitos.append(str(gerar_app(pasta)))
        except OSError:
            pass
    return bool(feitos), feitos


def remover_mac():
    tirados = []
    for pasta in _pastas_mac():
        app = pasta / f"{NOME}.app"
        if (app / "Contents" / "MacOS" / "temporada-viral").is_file():
            shutil.rmtree(app, ignore_errors=True)
            tirados.append(str(app))
    return tirados


# ---------------------------------------------------------------- Linux

def _pastas_linux():
    casa = Path.home()
    return [casa / ".local" / "share" / "applications", casa / "Desktop", casa / "Área de Trabalho"]


def criar_linux():
    conteudo = ("[Desktop Entry]\nType=Application\nName=Temporada Viral\nComment=Abre o painel do Temporada Viral\n"
                f'Exec="{sys.executable}" "{SERVIDOR}"\nPath={ESTUDIO}\nIcon={PNG}\nTerminal=false\n'
                "Categories=AudioVideo;\n")
    feitos = []
    for pasta in _pastas_linux():
        if pasta.name != "applications" and not pasta.is_dir():
            continue
        try:
            pasta.mkdir(parents=True, exist_ok=True)
            arq = pasta / "temporada-viral.desktop"
            arq.write_text(conteudo, encoding="utf-8")
            arq.chmod(0o755)
            feitos.append(str(arq))
        except OSError:
            pass
    return bool(feitos), feitos


def remover_linux():
    tirados = []
    for pasta in _pastas_linux():
        arq = pasta / "temporada-viral.desktop"
        if arq.is_file():
            arq.unlink()
            tirados.append(str(arq))
    return tirados


# ---------------------------------------------------------------- início

def main():
    _utf8()
    ap = argparse.ArgumentParser(description="Cria o ícone Temporada Viral, que abre o painel sem terminal.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--criar", action="store_true", help="cria o ícone na área de trabalho e no menu")
    g.add_argument("--remover", action="store_true", help="tira os ícones criados por aqui")
    g.add_argument("--gerar-app", metavar="PASTA", help="só monta o Temporada Viral.app (Mac) nesta pasta")
    a = ap.parse_args()
    if a.gerar_app:
        print(f"APP: {gerar_app(a.gerar_app)}")
        return 0
    if a.remover:
        tirados = remover_windows() if os.name == "nt" else remover_mac() if sys.platform == "darwin" else remover_linux()
        print("Ícones removidos:" if tirados else "Nenhum ícone do Temporada Viral para remover.")
        for t in tirados:
            print(f"  {t}")
        return 0
    if not SERVIDOR.is_file():
        print("ERRO: não achei kit/painel/servidor.py.\nO QUE FAZER: rode este comando a partir da pasta do estúdio, "
              "com o kit completo.")
        return 1
    if os.name == "nt":
        ok, onde = criar_windows()
    elif sys.platform == "darwin":
        ok, onde = criar_mac()
    else:
        ok, onde = criar_linux()
    if not ok:
        print("ERRO: não consegui criar o ícone.\nO QUE FAZER: use o ABRIR-PAINEL da pasta do estúdio (dois cliques) "
              "e, se quiser o ícone, peça para a IA rodar de novo: python kit/painel/atalho.py --criar")
        return 1
    print("ATALHO_OK: o ícone Temporada Viral abre o painel com dois cliques, sem janela de terminal.")
    for o in onde:
        print(f"  {o}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
