# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Estudo de referências: transcrever um vídeo que deu certo, tirar o raio-x dele e comparar vários do nicho.

O que sai daqui é análise e molde (a estrutura do vídeo, em palavras genéricas). Nunca o texto de outro criador
para regravar: o molde descreve o que cada trecho faz, não o que ele diz.

Uso (a partir de kit/):
    python -m estudo <link do YouTube ou Instagram, ou caminho de um vídeo>   transcreve e tira o raio-x
    python -m estudo --buscar "assunto" [--curtos]                          vídeos do YouTube sobre o assunto
    python -m estudo --listar                                                estudos guardados
    python -m estudo --nicho [id id id ...]                                  compara 3 ou mais estudos

Os estudos ficam em canal/estudos/<id>/ (estudo.json, transcricao.txt, transcricao.srt e molde.md), junto do canal
em uso: trocar de canal leva os estudos dele, e a atualização do kit não mexe nessa pasta.
"""
import json
import re
import unicodedata
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
ESTUDIO = KIT.parent
ESTUDOS = ESTUDIO / "canal" / "estudos"
MIN_NICHO = 3


def slug(texto, limite=48):
    s = unicodedata.normalize("NFKD", str(texto or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:limite] or "video"


def id_valido(ident):
    return bool(re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,80}", str(ident or "")))


def pasta_estudo(ident):
    if not id_valido(ident):
        raise ValueError("id de estudo inválido")
    return ESTUDOS / ident


def ts_srt(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def analisar_e_gravar(dados):
    """Raio-x e molde a partir dos segmentos guardados; grava estudo.json, transcricao.txt/.srt e molde.md."""
    from . import raiox
    meta = dados.get("metadados") or {}
    dur = dados.get("duracao_s") or meta.get("duration") or (dados.get("extra") or {}).get("duracao_audio")
    r = raiox.analisar(dados["segmentos"], dur, meta.get("width"), meta.get("height"))
    dados.update(raiox=r, molde=raiox.molde(r) if r.get("blocos") else None, raiox_versao=raiox.VERSAO)
    pasta = pasta_estudo(dados["id"])
    pasta.mkdir(parents=True, exist_ok=True)
    seg = dados["segmentos"]
    (pasta / "transcricao.txt").write_text(
        "\n".join(f"[{raiox.fmt_t(s['ini'])}] {s['texto']}" for s in seg) + "\n", encoding="utf-8")
    (pasta / "transcricao.srt").write_text(
        "\n".join(f"{i}\n{ts_srt(s['ini'])} --> {ts_srt(s['fim'])}\n{s['texto']}\n" for i, s in enumerate(seg, 1)),
        encoding="utf-8")
    titulo = meta.get("title") or meta.get("arquivo_nome") or dados["id"]
    origem = meta.get("webpage_url") or meta.get("arquivo_nome") or ""
    if dados.get("molde"):
        quadros = pasta / "quadros.jpg"
        dados["quadros"] = str(quadros) if quadros.is_file() else None
        (pasta / "molde.md").write_text(raiox.molde_md(titulo, dados["molde"], origem, dados["quadros"]),
                                        encoding="utf-8")
    (pasta / "estudo.json").write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    return dados


def _em_dia(e):
    """Estudo feito por uma versão antiga do raio-x: refaz a partir da transcrição guardada (sem baixar nada)."""
    from . import raiox
    if e and e.get("segmentos") and e.get("raiox_versao") != raiox.VERSAO and id_valido(e.get("id")):
        try:
            return analisar_e_gravar(e)
        except (OSError, ValueError, KeyError, TypeError):
            return e
    return e


def ler_estudo(ident):
    try:
        return _em_dia(json.loads((pasta_estudo(ident) / "estudo.json").read_text(encoding="utf-8")))
    except (OSError, ValueError):
        return None


def listar():
    """Resumo de cada estudo guardado, do mais novo para o mais velho (sem a transcrição)."""
    saida = []
    if not ESTUDOS.is_dir():
        return saida
    for arq in ESTUDOS.glob("*/estudo.json"):
        try:
            e = _em_dia(json.loads(arq.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            continue
        saida.append(resumo(e))
    return sorted(saida, key=lambda x: x.get("quando") or "", reverse=True)


def resumo(e):
    m, r = e.get("metadados") or {}, e.get("raiox") or {}
    g = r.get("gancho") or {}
    return {
        "id": e.get("id"), "quando": e.get("quando"), "plataforma": e.get("plataforma"),
        "titulo": m.get("title") or m.get("arquivo_nome") or e.get("id"), "autor": m.get("uploader") or m.get("channel"),
        "link": m.get("webpage_url"), "duracao_s": r.get("duracao_s"), "views": m.get("view_count"),
        "likes": m.get("like_count"), "comentarios": m.get("comment_count"), "formato": r.get("formato"),
        "primeira_fala_s": g.get("primeira_fala_s"), "tipo_gancho": g.get("tipo"),
        "viradas_por_min": (r.get("viradas") or {}).get("por_min"), "palavras_por_min": r.get("palavras_por_min"),
        "perguntas": len(r.get("perguntas") or []), "cta": len(r.get("cta") or []),
        "metodo": e.get("metodo"), "esqueleto": (e.get("molde") or {}).get("esqueleto"),
    }
