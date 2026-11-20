# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Vários canais no mesmo estúdio.

A pasta `canal/` é sempre o canal em uso: o kit, a IA e o painel leem só ela, como antes. Os outros canais ficam
guardados em `canais/<id>/` (o `canal/` deles e o `estilo.json` do estilo desenhado). Trocar de canal guarda o atual
e põe o escolhido no lugar, por renomeação de pasta (instantânea e sem copiar arquivos grandes); o `kit/config.json`
é refeito a partir das preferências do canal que entrou.

Uso (a partir de kit/):
    python -m canais                       # lista os canais e mostra qual está em uso
    python -m canais --novo "Bicho Esquisito"   # guarda o atual e começa um canal novo (a IA faz as perguntas)
    python -m canais --usar bicho-esquisito     # troca para outro canal
"""
import json
import re
import shutil
import unicodedata
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
ESTUDIO = KIT.parent
ATIVO = ESTUDIO / "canal"
GUARDA = ESTUDIO / "canais"
MODELO = Path(__file__).resolve().parent / "modelo"
ID = ".canal_id"
TRAVA = GUARDA / ".trocando"
ESTILO = KIT / "estilo.json"


class ErroCanal(Exception):
    """Erro com mensagem pronta para o usuário."""


def slug(texto):
    s = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:40] or "canal"


def _prefs(pasta):
    try:
        return json.loads((pasta / "preferencias.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _resumo(pasta, cid, ativo):
    c = _prefs(pasta).get("canal", {})
    return {"id": cid, "nome": c.get("nome") or cid, "arroba": c.get("arroba", ""), "ativo": ativo}


def atual():
    """Id do canal em uso. Na primeira vez, nasce do @ ou do nome do canal (e fica gravado)."""
    if not ATIVO.is_dir():
        return None
    arq = ATIVO / ID
    if arq.is_file():
        cid = arq.read_text(encoding="utf-8").strip()
        if cid:
            return cid
    c = _prefs(ATIVO).get("canal", {})
    cid = _livre(slug(c.get("arroba") or c.get("nome") or "meu-canal"))
    arq.write_text(cid + "\n", encoding="utf-8")
    return cid


def _livre(base):
    cid, n = base, 2
    while (GUARDA / cid).exists():
        cid, n = f"{base}-{n}", n + 1
    return cid


def listar():
    out = []
    cid = atual()
    if cid:
        out.append(_resumo(ATIVO, cid, True))
    if GUARDA.is_dir():
        for p in sorted(GUARDA.iterdir()):
            if p.is_dir() and (p / "canal").is_dir() and p.name != cid:
                out.append(_resumo(p / "canal", p.name, False))
    return out


def _mover(origem, destino):
    destino.parent.mkdir(parents=True, exist_ok=True)
    try:
        origem.rename(destino)
    except OSError:
        shutil.copytree(origem, destino) if origem.is_dir() else shutil.copy2(origem, destino)
        shutil.rmtree(origem) if origem.is_dir() else origem.unlink()


def _confere_trava():
    if TRAVA.exists():
        raise ErroCanal("ERRO: uma troca de canal anterior não terminou.\n"
                        f"O QUE FAZER: confira se a pasta canal/ e as pastas em canais/ estão inteiras e apague o arquivo {TRAVA}.")


def _guardar_atual():
    cid = atual()
    if cid is None:
        return None
    destino = GUARDA / cid
    if (destino / "canal").exists():
        raise ErroCanal(f"ERRO: já existe um canal guardado com o nome {cid}.\n"
                        "O QUE FAZER: renomeie a pasta antiga em canais/ e tente de novo.")
    _mover(ATIVO, destino / "canal")
    if ESTILO.is_file():
        _mover(ESTILO, destino / "estilo.json")
    return cid


def _espelhar():
    import prefs
    prefs.espelhar_config(prefs.carregar())


def usar(cid):
    """Troca o canal em uso. Devolve o resumo do canal que entrou."""
    _confere_trava()
    if cid == atual():
        return _resumo(ATIVO, cid, True)
    origem = GUARDA / cid
    if not (origem / "canal").is_dir():
        nomes = ", ".join(c["id"] for c in listar()) or "nenhum"
        raise ErroCanal(f"ERRO: não achei o canal '{cid}'.\nO QUE FAZER: escolha um destes: {nomes}.")
    GUARDA.mkdir(parents=True, exist_ok=True)
    TRAVA.write_text(cid, encoding="utf-8")
    guardado = None
    try:
        guardado = _guardar_atual()
        _mover(origem / "canal", ATIVO)
        if (origem / "estilo.json").is_file():
            _mover(origem / "estilo.json", ESTILO)
        (ATIVO / ID).write_text(cid + "\n", encoding="utf-8")
        shutil.rmtree(origem, ignore_errors=True)
    except Exception:
        # Desfaz: o canal que estava em uso volta para canal/
        if guardado and not ATIVO.exists() and (GUARDA / guardado / "canal").is_dir():
            _mover(GUARDA / guardado / "canal", ATIVO)
            if (GUARDA / guardado / "estilo.json").is_file() and not ESTILO.exists():
                _mover(GUARDA / guardado / "estilo.json", ESTILO)
        TRAVA.unlink(missing_ok=True)
        raise
    TRAVA.unlink(missing_ok=True)
    _espelhar()
    return _resumo(ATIVO, cid, True)


def novo(nome):
    """Guarda o canal em uso e começa um canal vazio com esse nome (a configuração segue na conversa ou no painel)."""
    _confere_trava()
    if not MODELO.is_dir():
        raise ErroCanal("ERRO: o modelo de canal vazio não está no kit (kit/canais/modelo).\n"
                        "O QUE FAZER: baixe de novo a versão mais recente do kit e descompacte por cima.")
    GUARDA.mkdir(parents=True, exist_ok=True)
    TRAVA.write_text("novo", encoding="utf-8")
    guardado = None
    try:
        guardado = _guardar_atual()
        shutil.copytree(MODELO, ATIVO)
        cid = _livre(slug(nome))
        (ATIVO / ID).write_text(cid + "\n", encoding="utf-8")
    except Exception:
        if guardado and (GUARDA / guardado / "canal").is_dir():
            shutil.rmtree(ATIVO, ignore_errors=True)
            _mover(GUARDA / guardado / "canal", ATIVO)
            if (GUARDA / guardado / "estilo.json").is_file() and not ESTILO.exists():
                _mover(GUARDA / guardado / "estilo.json", ESTILO)
        TRAVA.unlink(missing_ok=True)
        raise
    TRAVA.unlink(missing_ok=True)
    import prefs
    ok, erros, _ = prefs.salvar({"canal": {"nome": nome.strip()}}) if nome.strip() else (True, [], [])
    if not ok:
        _espelhar()
    return _resumo(ATIVO, atual(), True)
