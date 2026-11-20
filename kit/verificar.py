# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Confere o ambiente do kit e diz o que falta, sem alterar nada.

Uso: python verificar.py [--cpu]

Mostra: Python e bibliotecas, ffmpeg/ffprobe, encoder que será usado, render GPU ou CPU (e a placa), fontes, personagens,
VectorCraft (opcional), voz local e Whisper (opcionais) e quais chaves de API estão definidas (só se existem;
nunca o valor). Sai com código 1 se faltar algo obrigatório.

Regra do render: PC com placa desenha na GPU e grava no encoder da placa; nuvem, celular ou PC sem placa desenha na
CPU em partes paralelas (um processo por núcleo) e grava no libx264. Placa que existe mas não desenha (glfw faltando,
driver velho) reprova aqui, porque o render cairia na CPU sem ninguém perceber.
"""
import argparse
import importlib
import os
import platform
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(KIT))

OBRIGATORIAS = ["skia", "numpy", "scipy", "PIL", "requests"]
OPCIONAIS = {"glfw": "render na GPU", "faster_whisper": "alinhar.py (tempo de palavra)", "kokoro": "voz local Kokoro",
             "azure.cognitiveservices.speech": "tempos de palavra no Azure", "edge_tts": "voz de teste"}


def linha(ok, nome, detalhe=""):
    marca = "ok " if ok is True else ("-- " if ok is None else "FALTA")
    print(f"[{marca:5}] {nome:28} {detalhe}")
    return ok is not False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cpu", action="store_true")
    a = ap.parse_args()
    tudo = True
    print(f"Sistema: {platform.system()} {platform.release()} | Python {sys.version.split()[0]}")
    tudo &= linha(sys.version_info >= (3, 10), "Python 3.10+", sys.executable)
    for m in OBRIGATORIAS:
        try:
            mod = importlib.import_module(m)
            tudo &= linha(True, m, getattr(mod, "__version__", ""))
        except ImportError:
            tudo &= linha(False, m, "pip install -r requirements.txt")
    for m, uso in OPCIONAIS.items():
        try:
            importlib.import_module(m)
            linha(True, m, uso)
        except Exception:
            linha(None, m, f"opcional ({uso})")
    try:
        import config
        from config import CFG, ferramenta, pasta
    except Exception as e:
        linha(False, "config", str(e))
        sys.exit(1)
    for f in ("ffmpeg", "ffprobe"):
        tudo &= linha(bool(ferramenta(f)), f, ferramenta(f) or "instale o ffmpeg (ver INSTALAR.md)")
    if ferramenta("ffmpeg"):
        from maquina.motor import Superficie, _processos_cpu, escolher_encoder, placa_sem_uso
        try:
            enc = escolher_encoder(a.cpu)
            linha(True, "encoder de vídeo", enc + ("" if enc != "libx264" else " (CPU: mais lento, funciona)"))
        except Exception as e:
            tudo &= linha(False, "encoder de vídeo", str(e))
        sup = Superficie(cpu=a.cpu)
        if sup.ctx is not None:
            linha(True, "render", sup.backend + " | 1 processo + encoder da placa")
        else:
            aviso = placa_sem_uso(sup, a.cpu)
            detalhe = f"{sup.backend} ({sup.motivo_cpu}) | {_processos_cpu()} processos em paralelo + libx264"
            tudo &= linha(False if aviso else True, "render", aviso or detalhe)
        sup.fechar()
    for papel, arq in CFG["fontes"].items():
        p = pasta("fontes") / arq
        tudo &= linha(p.is_file(), f"fonte {papel}", arq if p.is_file() else "python baixar_fontes.py")
    pers = sorted(d.name for d in pasta("personagens").iterdir() if (d / "partes.json").is_file())
    tudo &= linha(bool(pers), "personagens prontos", ", ".join(pers) or "python construir_boneco.py <nome>")
    vc = ferramenta("vectorcraft")
    linha(True if vc else None, "VectorCraft (opcional)", vc or "sem ele, construir_boneco usa o motor Skia")
    chaves = dict(config.SEGREDOS, GEMINI_API_KEY="GEMINI_API_KEY")
    for nome, var in chaves.items():
        tem = bool(config.segredo(nome, obrigatorio=False))
        linha(True if tem else None, var, "definida" if tem else "não definida")
    import shutil
    livre = shutil.disk_usage(str(pasta("trabalho"))).free / 1024 ** 3
    tudo &= linha(livre >= 5, "espaço em disco", f"{livre:.0f} GB livres" + ("" if livre >= 30 else
                  " (pouco: apague testes antigos em trabalho/ depois de aprovar os vídeos)"))
    print("\nVERIFICAR_OK" if tudo else "\nVERIFICAR_FALHOU: corrija os itens FALTA (ver INSTALAR.md)")
    sys.exit(0 if tudo else 1)


if __name__ == "__main__":
    main()
