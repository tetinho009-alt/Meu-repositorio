# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Configuração única do kit.

Ordem de leitura:
1. `config.exemplo.json` (valores padrão; é a fonte da verdade dos campos);
2. o arquivo apontado por MAQUINA_CONFIG, ou `config.json` ao lado deste arquivo, se existir.

Caminhos relativos valem a partir da pasta do arquivo de configuração que os definiu. Segredos (chaves de API,
tokens) nunca ficam na configuração: vêm de variável de ambiente ou de um arquivo de segredos FORA da pasta do kit.
"""
import json
import os
import shutil
from pathlib import Path

KIT = Path(__file__).resolve().parent

# Variáveis de ambiente reconhecidas (nome lógico -> variável).
SEGREDOS = {
    "elevenlabs": "ELEVENLABS_API_KEY",
    "azure_speech": "AZURE_SPEECH_KEY",
    "instagram": "IG_ACCESS_TOKEN",
    "youtube_client_id": "YT_CLIENT_ID",
    "youtube_client_secret": "YT_CLIENT_SECRET",
    "youtube_refresh_token": "YT_REFRESH_TOKEN",
    "tiktok": "TIKTOK_ACCESS_TOKEN",
}


class ErroConfig(RuntimeError):
    pass


def _mescla(base, extra):
    for k, v in extra.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _mescla(base[k], v)
        else:
            base[k] = v
    return base


def _ler(caminho):
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


# Campos que são caminhos: cada arquivo de configuração resolve os seus relativos à própria pasta.
_CAMPOS_CAMINHO = (("pastas", "*"), ("ferramentas", "*"), ("segredos", "arquivo"), ("whisper", "pasta_modelos"),
                   ("voz", "kokoro", "pasta_modelo"), ("voz", "piper", "modelo"))


def _absolutiza(camada, base):
    def parece_caminho(v):
        return isinstance(v, str) and v and (v.startswith(".") or "/" in v or "\\" in v)

    for campo in _CAMPOS_CAMINHO:
        no = camada
        for chave in campo[:-1]:
            no = no.get(chave) if isinstance(no, dict) else None
        if not isinstance(no, dict):
            continue
        chaves = list(no) if campo[-1] == "*" else [campo[-1]]
        for k in chaves:
            v = no.get(k)
            if parece_caminho(v):
                p = Path(os.path.expandvars(v)).expanduser()
                no[k] = str(p if p.is_absolute() else (base / p).resolve())
    return camada


def _carregar():
    cfg = _absolutiza(_ler(KIT / "config.exemplo.json"), KIT)
    alvo = os.environ.get("MAQUINA_CONFIG")
    arq = Path(alvo).expanduser() if alvo else KIT / "config.json"
    if arq.is_file():
        _mescla(cfg, _absolutiza(_ler(arq), arq.resolve().parent))
    elif alvo:
        raise ErroConfig(f"MAQUINA_CONFIG aponta para um arquivo que não existe: {arq}")
    cfg["_base"] = str(KIT)
    return cfg


import licenca  # noqa: E402

licenca.exigir()
CFG = _carregar()


def caminho(valor):
    """Resolve um caminho da configuração (relativo à pasta do arquivo de configuração)."""
    p = Path(os.path.expandvars(str(valor))).expanduser()
    return p if p.is_absolute() else (Path(CFG["_base"]) / p).resolve()


def pasta(nome):
    """Pasta configurada em `pastas` (trabalho, fontes, personagens); cria a de trabalho se faltar."""
    p = caminho(CFG["pastas"][nome])
    if nome == "trabalho":
        p.mkdir(parents=True, exist_ok=True)
    return p


def ferramenta(nome):
    """Executável configurado (ffmpeg, ffprobe, vectorcraft). Vazio ou ausente = procura no PATH."""
    valor = CFG["ferramentas"].get(nome) or ""
    if valor and Path(valor).is_absolute():
        return valor if Path(valor).exists() else None
    padrao = {"vectorcraft": "vectorcraft-cli"}.get(nome, nome)
    achado = shutil.which(valor or padrao)
    if not achado and nome == "vectorcraft":  # instalações padrão fora do PATH
        for p in (Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "VectorCraft" / "vectorcraft-cli.exe",
                  Path("/Applications/VectorCraft.app/Contents/MacOS/vectorcraft-cli")):
            if p.is_file():
                return str(p)
    return achado


def ffmpeg():
    exe = ferramenta("ffmpeg")
    if not exe:
        raise ErroConfig("ffmpeg não encontrado. Instale (ver INSTALAR.md) ou aponte ferramentas.ffmpeg no config.json.")
    return exe


def ffprobe():
    exe = ferramenta("ffprobe")
    if not exe:
        raise ErroConfig("ffprobe não encontrado (vem junto com o ffmpeg).")
    return exe


def segredo(nome, obrigatorio=True):
    """Lê um segredo pelo nome lógico (ver SEGREDOS): variável de ambiente primeiro, depois o arquivo de segredos.

    O arquivo de segredos (JSON {"VARIAVEL": "valor"}) precisa estar FORA da pasta do kit, para não ir parar em
    backup, zip de venda ou repositório por acidente.
    """
    var = SEGREDOS.get(nome, nome)
    valor = os.environ.get(var, "").strip()
    if not valor and CFG["segredos"].get("arquivo"):
        arq = caminho(CFG["segredos"]["arquivo"])
        if KIT in arq.parents or arq == KIT:
            raise ErroConfig("O arquivo de segredos está dentro da pasta do kit. Mova para fora (ex.: pasta do usuário).")
        if arq.is_file():
            valor = str(_ler(arq).get(var, "")).strip()
    if not valor and obrigatorio:
        raise ErroConfig(f"Falta o segredo {var}. Defina a variável de ambiente {var} (ver README, seção Chaves).")
    return valor


def cor(nome):
    """Cor da configuração em (r, g, b)."""
    h = CFG["cores"][nome].lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def fonte_arquivo(papel):
    """Arquivo da fonte de um papel (titulo, legenda, texto, mono)."""
    arq = pasta("fontes") / CFG["fontes"][papel]
    if not arq.is_file():
        raise ErroConfig(f"Fonte ausente: {arq}. Rode `python baixar_fontes.py` (fontes OFL oficiais).")
    return arq
