# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Erro em português, com o que fazer: traduz as falhas mais comuns do kit para uma frase de gente.

Uso nos scripts:
    from erros import rodar_amigavel
    if __name__ == "__main__":
        rodar_amigavel(main)

A IA mostra a linha "ERRO:" ao usuário e segue a linha "O QUE FAZER:" sozinha quando puder.
"""
import os
import re
import shutil
import sys
import traceback

# (padrão no texto do erro, explicação, o que fazer)
CONHECIDOS = [
    (r"ffmpeg não encontrado|No such file.*ffmpeg|'ffmpeg' is not recognized",
     "falta o ffmpeg, o programa que grava o vídeo",
     "instale pelo kit/INSTALAR.md (no Windows: winget install Gyan.FFmpeg) e feche e abra o terminal"),
    (r"No module named '?skia'?",
     "falta o motor de desenho (skia-python)",
     "rode, a partir de kit/: python -m pip install -r requirements.txt"),
    (r"No module named '?(kokoro|misaki)'?",
     "a voz local Kokoro não está instalada",
     "rode: python -m pip install -r requirements-opcional.txt, ou use a voz grátis do Google (--voz gemini)"),
    (r"No module named '?faster_whisper'?",
     "falta o Whisper, que acha o tempo de cada palavra para a legenda",
     "rode: python -m pip install faster-whisper"),
    (r"espeak",
     "a voz Kokoro precisa do espeak-ng instalado no computador",
     "instale o espeak-ng (kit/INSTALAR.md) ou use a voz grátis do Google (--voz gemini)"),
    (r"MemoryError|Unable to allocate|out of memory|CUDA out of memory",
     "faltou memória no computador",
     "feche programas abertos e rode de novo; se repetir, use render.processos_cpu = 4 no kit/config.json"),
    (r"No space left|espaço insuficiente|Errno 28",
     "o disco encheu",
     "apague vídeos de teste antigos na pasta trabalho/ e rode de novo (precisa de uns 5 GB livres)"),
    (r"WinError 206|filename.*too long|nome do arquivo.*longo",
     "o caminho da pasta ficou comprido demais para o Windows",
     "mova a pasta do estúdio para um caminho curto, como C:\\temporada-viral"),
    (r"PermissionError|Acesso negado|WinError 32",
     "outro programa está usando um arquivo (o vídeo aberto no player ou o OneDrive sincronizando)",
     "feche o vídeo no player, pause o OneDrive e rode de novo; o ideal é o estúdio fora do OneDrive"),
    (r"HTTP 401|HTTP 403|recusou a chave|invalid.*api.?key",
     "o serviço recusou a chave",
     "crie uma chave nova e cole pela janela: python chave.py (ou --qual gemini)"),
    (r"HTTP 429|limite do plano|quota|RESOURCE_EXHAUSTED",
     "o limite de uso do serviço de voz acabou por agora",
     "espere uns minutos e rode de novo; o kit refaz só o que falta"),
    (r"ConnectionError|Max retries exceeded|getaddrinfo|Name or service not known|sem conexão",
     "sem internet ou o serviço não respondeu",
     "confira a internet e rode de novo"),
    (r"licen[cç]a",
     "a licença do estúdio não está ativa",
     "rode, a partir de kit/: python licenca.py SEU-EMAIL-DA-COMPRA"),
    (r"JSONDecodeError|Expecting .* delimiter|Expecting value",
     "um arquivo de roteiro ou de configuração ficou com erro de digitação (vírgula ou aspas)",
     "a IA abre o arquivo citado acima, corrige a vírgula ou as aspas e roda de novo"),
]


def explicar(texto):
    """(explicação, o que fazer) para o texto de um erro, ou None se não for conhecido."""
    for padrao, expl, fazer in CONHECIDOS:
        if re.search(padrao, texto, re.I):
            return expl, fazer
    return None


def _utf8():
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def rodar_amigavel(main):
    """Roda `main()`. Em erro, mostra a explicação em português e o que fazer; o detalhe técnico vai por último."""
    _utf8()
    try:
        main()
    except KeyboardInterrupt:
        print("\nParado a pedido. Rode de novo quando quiser: o que já ficou pronto é reaproveitado.")
        sys.exit(130)
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        texto = f"{type(e).__name__}: {e}"
        dica = explicar(texto)
        print("\n" + "-" * 60)
        if type(e).__name__ in ("ErroVoz", "ErroConfig"):
            # Erro do próprio kit: a mensagem já diz o que aconteceu e o que fazer, em português.
            print(f"ERRO: {e}")
            print("-" * 60)
            sys.exit(1)
        if dica:
            print(f"ERRO: {dica[0]}.")
            print(f"O QUE FAZER: {dica[1]}.")
        else:
            print(f"ERRO: {texto}")
            print("O QUE FAZER: mostre esta mensagem à IA, ela resolve; se repetir, diga \"deu erro\" (comandos/ajuda.md).")
        if os.environ.get("KIT_DETALHE") or not dica:
            print("\nDetalhe técnico:")
            traceback.print_exc()
        print("-" * 60)
        sys.exit(1)


def espaco_livre_gb(pasta="."):
    return shutil.disk_usage(pasta).free / 1024 ** 3
