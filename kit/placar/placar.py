# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Placar ao vivo: lê os comentários e as métricas pelas APIs oficiais, apura os votos e grava o `placar.json` que a
página do site mostra. Também gera a apuração da parte anterior para o vídeo seguinte (`--detalhe`).

    Instagram  Graph API com login do Instagram: comentários (votos), curtidas, views     IG_ACCESS_TOKEN
    YouTube    Data API v3, só leitura com chave: comentários (votos), views, curtidas    YT_API_KEY
    TikTok     Display API: views, curtidas, compartilhamentos (a API não entrega o texto dos comentários)
               TT_CLIENT_KEY, TT_CLIENT_SECRET, TT_REFRESH_TOKEN
               Votos do TikTok: comentários copiados do TikTok Studio num .txt (campo `tiktok_comentarios`).

Uso (a partir da pasta do kit):
    python placar/placar.py --episodios placar/episodios.json --saida placar/site/placar.json
    python placar/placar.py --episodios placar/episodios.json --so <slug> --detalhe trabalho/apuracao.json
    python placar/placar.py --episodios placar/exemplo/episodios.json --exemplo placar/exemplo/api_exemplo.json \\
                            --saida placar/site/placar.json --detalhe trabalho/apuracao_exemplo.json
    python placar/placar.py --episodios placar/episodios.json --tiktok-link        (autorizar o TikTok, uma vez)
    python placar/placar.py --episodios placar/episodios.json --tiktok-codigo CODIGO
    python placar/placar.py --gh-segredos usuario/repositorio   (copia as chaves para o GitHub, sem mostrar)

Regras (as mesmas do placar real):
- um voto por perfil em cada rede; o voto vale número ou palavra (regra única em `maquina/votos.py`);
- só conta comentário feito dentro da janela de votação (`regras.janela_horas`, padrão 48 h após `publicado`);
- placar oficial só com `regras.minimo_votos` (10) ou mais; abaixo disso a página mostra "prévia";
- nunca inventa número: se uma rede falhar, mantém a última leitura boa dela (com a data) em vez de zerar;
- o placar público não leva @ nem texto de ninguém; o `--detalhe` (privado, para o vídeo) leva só o texto, sem @.
Chaves: variável de ambiente; dentro do kit, também o arquivo de segredos do config.json. Nunca no repositório.
"""
import argparse
import json
import os
import re
import secrets
import subprocess
import sys
import time
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode, urlparse

AQUI = Path(__file__).resolve().parent
KIT = AQUI.parent
for _p in (AQUI, KIT):  # votos.py ao lado (site publicado) ou maquina/votos.py (dentro do kit)
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
try:
    from votos import apurar, sem_acento  # noqa: E402
except ImportError:
    from maquina.votos import apurar, sem_acento  # noqa: E402

IG_API = "https://graph.instagram.com/v21.0"
YT_API = "https://www.googleapis.com/youtube/v3"
TT_API = "https://open.tiktokapis.com/v2"
TT_AUTORIZAR = "https://www.tiktok.com/v2/auth/authorize/"
MAX_COMENTARIOS = 5000
REDES = ("instagram", "youtube", "tiktok")
NOMES_SEGREDOS = ("IG_ACCESS_TOKEN", "YT_API_KEY", "TT_CLIENT_KEY", "TT_CLIENT_SECRET", "TT_REFRESH_TOKEN")


class ErroRede(RuntimeError):
    pass


# ------------------------------------------------------------------------------------------------ segredos

def _config_kit():
    """config.py do kit, se este arquivo estiver dentro do kit (no site publicado não está)."""
    try:
        import config  # noqa: F401
        return config
    except Exception:
        return None


def segredo(nome):
    valor = os.environ.get(nome, "").strip()
    if not valor and _config_kit():
        valor = _config_kit().segredo(nome, obrigatorio=False)
    return valor


def grava_segredo(nome, valor):
    """Grava no arquivo de segredos do kit (fora da pasta). Devolve False se não houver onde gravar."""
    cfg = _config_kit()
    if not cfg or not cfg.CFG["segredos"].get("arquivo"):
        return False
    arq = cfg.caminho(cfg.CFG["segredos"]["arquivo"])
    if cfg.KIT in arq.parents:
        return False
    dados = json.loads(arq.read_text(encoding="utf-8")) if arq.is_file() else {}
    dados[nome] = valor
    arq.parent.mkdir(parents=True, exist_ok=True)
    arq.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    return True


def _limpa(msg):
    """Mensagem de erro sem chave nem token (vai para o placar público)."""
    msg = str(msg)
    for nome in NOMES_SEGREDOS:
        v = os.environ.get(nome) or ""
        if len(v) > 6:
            msg = msg.replace(v, "***")
    return re.sub(r"(access_token|key|client_secret|refresh_token)=[^&\s\"']+", r"\1=***", msg)[:300]


# ------------------------------------------------------------------------------------------------ HTTP

class HTTP:
    def __init__(self):
        import requests
        self.s = requests.Session()

    def pedido(self, metodo, url, params=None, data=None, json_=None, headers=None):
        r = self.s.request(metodo, url, params=params, data=data, json=json_, headers=headers, timeout=30)
        try:
            corpo = r.json()
        except ValueError:
            corpo = {"texto": r.text[:300]}
        if r.status_code >= 400:
            erro = corpo.get("error") if isinstance(corpo, dict) else None
            msg = erro.get("message") if isinstance(erro, dict) else (corpo.get("error_description") or erro or corpo)
            raise ErroRede(_limpa(f"HTTP {r.status_code} em {urlparse(url).path}: {msg}"))
        return corpo


class HTTPExemplo:
    """Respostas gravadas no formato das APIs (teste sem chave e sem rede). Chave: "<api> <caminho>[ <id>]"."""

    def __init__(self, arq):
        self.d = json.loads(Path(arq).read_text(encoding="utf-8"))

    def pedido(self, metodo, url, params=None, data=None, json_=None, headers=None):
        u = urlparse(url)
        api = {"graph.instagram.com": "ig", "www.googleapis.com": "yt", "open.tiktokapis.com": "tt"}[u.netloc]
        caminho = u.path.replace("/v21.0", "").replace("/youtube/v3", "").replace("/v2", "")
        chave = f"{api} {caminho}"
        if api == "yt" and caminho == "/commentThreads":
            chave += f" {params['videoId']}" + (f" {params['pageToken']}" if params.get("pageToken") else "")
        if u.query:  # página seguinte do Instagram (link "next" completo)
            chave += f" ?{u.query}"
        if chave not in self.d:
            raise ErroRede(f"exemplo sem resposta para {chave}")
        r = self.d[chave]
        if isinstance(r, dict) and r.get("_erro"):
            raise ErroRede(r["_erro"])
        return r


# ------------------------------------------------------------------------------------------------ leitura

def _data(s):
    """ISO 8601 (com Z, +0000 ou -03:00) para datetime com fuso; None se não der."""
    if not s:
        return None
    s = str(s).replace("Z", "+00:00")
    s = re.sub(r"([+-]\d{2})(\d{2})$", r"\1:\2", s)
    try:
        d = datetime.fromisoformat(s)
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def chave_instagram(link):
    """Link do reel (com ou sem www, barra ou parâmetros) -> "/reel/CODIGO"."""
    return re.sub(r"^https?://(www\.)?instagram\.com", "", (link or "").split("?")[0].rstrip("/"))


def id_youtube(link):
    m = re.search(r"(?:shorts/|v=|youtu\.be/)([\w-]{11})", link or "")
    return m.group(1) if m else (link if re.fullmatch(r"[\w-]{11}", link or "") else None)


def id_tiktok(link):
    m = re.search(r"/video/(\d+)", link or "")
    return m.group(1) if m else (link if re.fullmatch(r"\d{8,}", link or "") else None)


def instagram(http, tok, chaves):
    """{chave do reel: {"comentarios": [...], "metricas": {...}}} dos reels pedidos."""
    eu = http.pedido("GET", f"{IG_API}/me", params={"fields": "username", "access_token": tok}).get("username", "")
    midias, url, params, guarda = [], f"{IG_API}/me/media", {
        "fields": "id,permalink,comments_count,like_count", "limit": 50, "access_token": tok}, 0
    while url and guarda < 4 and not all(any(chave_instagram(m.get("permalink")) == c for m in midias) for c in chaves):
        r = http.pedido("GET", url, params=params)
        midias += r.get("data", [])
        url, params, guarda = (r.get("paging") or {}).get("next"), None, guarda + 1
    out = {}
    for m in midias:
        chave = chave_instagram(m.get("permalink"))
        if chave not in chaves:
            continue
        lista, url, params, guarda = [], f"{IG_API}/{m['id']}/comments", {
            "fields": "id,text,timestamp,username,from,like_count", "limit": 50, "access_token": tok}, 0
        while url and len(lista) < MAX_COMENTARIOS and guarda < 120:
            r = http.pedido("GET", url, params=params)
            for c in r.get("data", []):
                autor = c.get("username") or (c.get("from") or {}).get("username") or ""
                if autor and autor == eu:
                    continue  # comentário do próprio perfil não é voto
                quem = f"ig:{autor}" if autor else f"ig-id:{(c.get('from') or {}).get('id') or c['id']}"
                lista.append({"quem": quem, "texto": c.get("text", ""), "data": c.get("timestamp")})
            url, params, guarda = (r.get("paging") or {}).get("next"), None, guarda + 1
        met = {"curtidas": m.get("like_count"), "comentarios": m.get("comments_count")}
        try:  # views e salvamentos só com a permissão de insights; sem ela, fica o que vem na mídia
            ins = http.pedido("GET", f"{IG_API}/{m['id']}/insights",
                              params={"metric": "views,reach,saved,shares", "access_token": tok})
            for it in ins.get("data", []):
                met[it["name"]] = (it.get("total_value") or {}).get("value", (it.get("values") or [{}])[0].get("value"))
        except ErroRede:
            pass
        out[chave] = {"comentarios": lista, "metricas": met}
    return out


def youtube(http, chave_api, ids):
    """{id do vídeo: {"comentarios": [...], "metricas": {...}}}. Cota: ~1 unidade por página de 100 comentários."""
    if not ids:
        return {}
    vs = http.pedido("GET", f"{YT_API}/videos", params={"part": "statistics,snippet", "id": ",".join(ids),
                                                         "key": chave_api})
    out = {}
    for v in vs.get("items", []):
        st, canal = v.get("statistics", {}), v.get("snippet", {}).get("channelId")
        met = {"views": int(st.get("viewCount", 0)), "curtidas": int(st.get("likeCount", 0)),
               "comentarios": int(st.get("commentCount", 0))}
        lista, params, guarda, erro = [], {"part": "snippet", "videoId": v["id"], "textFormat": "plainText",
                                           "maxResults": 100, "key": chave_api}, 0, None
        try:
            while met["comentarios"] > 0 and len(lista) < MAX_COMENTARIOS and guarda < 50:
                r = http.pedido("GET", f"{YT_API}/commentThreads", params=params)
                for t in r.get("items", []):
                    s = t["snippet"]["topLevelComment"]["snippet"]
                    autor = (s.get("authorChannelId") or {}).get("value", "")
                    if autor and autor == canal:
                        continue  # comentário do próprio canal (fixado, aviso) não é voto
                    lista.append({"quem": f"yt:{autor or t['id']}", "texto": s.get("textOriginal") or s.get("textDisplay", ""),
                                  "data": s.get("publishedAt")})
                if not r.get("nextPageToken"):
                    break
                params["pageToken"], guarda = r["nextPageToken"], guarda + 1
        except ErroRede as e:  # comentários desativados ou vídeo marcado como infantil: fica só a métrica
            erro = str(e)
        out[v["id"]] = {"comentarios": None if erro else lista, "metricas": met, "erro": erro}
    return out


def tiktok_acesso(http, ck, cs, refresh):
    r = http.pedido("POST", f"{TT_API}/oauth/token/", data={"client_key": ck, "client_secret": cs,
                                                            "grant_type": "refresh_token", "refresh_token": refresh},
                    headers={"Content-Type": "application/x-www-form-urlencoded"})
    if not r.get("access_token"):
        raise ErroRede(_limpa(f"TikTok não renovou o acesso: {r.get('error_description') or r.get('error')}"))
    novo = r.get("refresh_token")
    if novo and novo != refresh:  # o TikTok pode trocar o refresh token: guarda o novo onde der
        if not grava_segredo("TT_REFRESH_TOKEN", novo):
            print("AVISO: o TikTok trocou o TT_REFRESH_TOKEN. Rode --tiktok-link de novo no computador e atualize o "
                  "segredo (o atual para de valer quando vencer).", flush=True)
    return r["access_token"]


def tiktok(http, acesso, ids):
    """{id do vídeo: {"metricas": {...}}} pela Display API (video.list)."""
    campos = "id,view_count,like_count,comment_count,share_count"
    out, cursor, guarda = {}, None, 0
    while guarda < 10 and not all(i in out for i in ids):
        corpo = {"max_count": 20, **({"cursor": cursor} if cursor else {})}
        r = http.pedido("POST", f"{TT_API}/video/list/", params={"fields": campos}, json_=corpo,
                        headers={"Authorization": f"Bearer {acesso}", "Content-Type": "application/json"})
        if (r.get("error") or {}).get("code", "ok") != "ok":
            raise ErroRede(_limpa(f"TikTok video/list: {r['error'].get('message') or r['error'].get('code')}"))
        for v in (r.get("data") or {}).get("videos", []):
            out[str(v["id"])] = {"metricas": {"views": v.get("view_count", 0), "curtidas": v.get("like_count", 0),
                                              "comentarios": v.get("comment_count", 0), "shares": v.get("share_count", 0)}}
        cursor, guarda = (r.get("data") or {}).get("cursor"), guarda + 1
        if not (r.get("data") or {}).get("has_more"):
            break
    return out


def tiktok_arquivo(arq):
    """Comentários copiados do TikTok Studio, um por linha. "@usuario: texto" ou "usuario<TAB>texto" permite contar
    um voto por perfil; linha sem o @ conta como um perfil à parte (anote isso na apuração)."""
    lista = []
    for n, linha in enumerate(Path(arq).read_text(encoding="utf-8").splitlines()):
        linha = linha.strip()
        if not linha:
            continue
        m = re.match(r"^@?([\w.]{2,30})(?::\s+|\t)(.+)$", linha)
        quem, texto = (f"tt:{m.group(1).lower()}", m.group(2)) if m else (f"tt-linha:{n}", linha)
        lista.append({"quem": quem, "texto": texto, "data": None})
    return lista


# ------------------------------------------------------------------------------------------------ apuração

PEDIDO = r"PARTE\s*({n}|{ext})|PROXIMA\s+PARTE|CONTINUA(CAO)?\b|CADE\s+A\s+PARTE|SEGUNDA\s+PARTE|EP\s*{n}\b"
EXTENSO = {2: "DOIS", 3: "TRES", 4: "QUATRO", 5: "CINCO", 6: "SEIS"}


def texto_tela(t):
    """Comentário para aparecer no vídeo: sem @menção, sem emoji, espaço normalizado."""
    t = re.sub(r"@\S+", "", t or "")
    t = "".join(ch for ch in t if unicodedata.category(ch)[0] in "LNPZ")
    return re.sub(r"\s+", " ", t).strip()


def apurar_episodio(ep, lidos, anterior, regras, agora):
    opcoes = {o["id"]: o.get("palavras") or [o["rotulo"]] for o in ep["opcoes"]}
    pub = _data(ep.get("publicado"))
    fecha = pub + timedelta(hours=float(regras.get("janela_horas", 48))) if pub else None
    minimo = int(regras.get("minimo_votos", 10))
    por_rede, metricas, desatualizado, validos, brutos = {}, {}, {}, [], []
    for rede in REDES:
        d = lidos.get(rede)
        ant = anterior or {}
        if d is None:
            continue
        if d.get("erro_leitura"):
            if rede in (ant.get("por_rede") or {}):  # rede caiu: mantém a última leitura boa, com a data
                por_rede[rede] = ant["por_rede"][rede]
                desatualizado[rede] = (ant.get("desatualizado") or {}).get(rede) or ant.get("atualizado")
            if rede in (ant.get("metricas") or {}):
                metricas[rede] = ant["metricas"][rede]
            continue
        if d.get("metricas"):
            metricas[rede] = d["metricas"]
        if d.get("contagem") is not None and d.get("comentarios") is None:
            por_rede[rede] = {k: int(d["contagem"].get(k, 0)) for k in opcoes}
            continue
        if d.get("comentarios") is None:
            continue
        coms = [c for c in d["comentarios"] if not (fecha and _data(c.get("data")) and _data(c["data"]) > fecha)]
        brutos += [{**c, "rede": rede} for c in coms]
        cont, val = apurar(coms, opcoes, ep.get("nega"))
        por_rede[rede] = cont
        validos += [{**v, "rede": rede} for v in val]
    votos = {k: sum(r.get(k, 0) for r in por_rede.values()) for k in opcoes} if por_rede else None
    total = sum(votos.values()) if votos else 0
    if votos is None:
        status = "aguardando"
    elif fecha and agora >= fecha:
        status = "encerrada" if total >= minimo else "baixa_participacao"
    else:
        status = "votacao"
    vencedor = None
    if votos and total >= minimo:
        topo = max(votos.values())
        ganhadores = [k for k, v in votos.items() if v == topo]
        vencedor = ganhadores[0] if len(ganhadores) == 1 else "empate"
    publico = {
        "slug": ep["slug"], "serie": ep.get("serie"), "parte": ep.get("parte"), "titulo": ep.get("titulo"),
        "pergunta": ep.get("pergunta"), "publicado": ep.get("publicado"),
        "fecha_em": fecha.isoformat() if fecha else None, "status": status,
        "opcoes": [{"id": o["id"], "rotulo": o["rotulo"], "cor": o.get("cor")} for o in ep["opcoes"]],
        "votos": votos, "total": total, "oficial": total >= minimo, "vencedor": vencedor,
        "por_rede": por_rede, "metricas": metricas, "links": ep.get("links", {}),
        "desatualizado": desatualizado or None, "atualizado": agora.isoformat(timespec="seconds"),
    }
    n = int(ep.get("parte") or 1) + 1
    pedido = re.compile(PEDIDO.format(n=n, ext=EXTENSO.get(n, str(n))))
    vistos, tela = set(), []
    for c in sorted(brutos, key=lambda x: str(x.get("data") or "")):
        t = texto_tela(c["texto"])
        if len(t) >= 2 and sem_acento(t) not in vistos:
            vistos.add(sem_acento(t))
            tela.append(t)
    pedintes = {f"{c['rede']}|{c['quem']}" for c in brutos if pedido.search(sem_acento(c["texto"]))}
    detalhe = {**publico, "comentarios_tela": tela[:60], "textos_votos": [texto_tela(v["texto"]) for v in validos][:200],
               "pedidos_proxima_parte": len(pedintes), "comentarios_lidos": len(brutos),
               "regra": "1 voto por perfil por rede; número ou palavra; dentro da janela de votação"}
    return publico, detalhe


def ler_redes(http, episodios, base, exemplo=False):
    """Lê cada rede uma vez para todos os episódios. Devolve ({rede: {slug: dados}}, [avisos])."""
    avisos, lidos = [], {r: {} for r in REDES}
    ig = {ep["slug"]: chave_instagram(ep["links"]["instagram"]) for ep in episodios if ep.get("links", {}).get("instagram")}
    yt = {ep["slug"]: id_youtube(ep["links"]["youtube"]) for ep in episodios if ep.get("links", {}).get("youtube")}
    tt = {ep["slug"]: id_tiktok(ep["links"]["tiktok"]) for ep in episodios if ep.get("links", {}).get("tiktok")}

    def falha(rede, slugs, e):
        avisos.append(f"{rede}: {_limpa(e)}")
        for s in slugs:
            lidos[rede][s] = {"erro_leitura": True}

    tok = "EXEMPLO" if exemplo else segredo("IG_ACCESS_TOKEN")
    if ig and tok:
        if not exemplo and _config_kit():
            try:  # dentro do kit, renova o token longo antes de vencer (grava no arquivo de segredos)
                from publicar.ig_token import renovar
                tok = renovar(tok)
            except Exception as e:  # renovação falhou: usa o atual, que ainda vale até vencer
                avisos.append(f"instagram (renovação): {_limpa(e)}")
        try:
            d = instagram(http, tok, set(ig.values()))
            for s, k in ig.items():
                lidos["instagram"][s] = d.get(k) or {"erro_leitura": True}
                if k not in d:
                    avisos.append(f"instagram: reel {k} não encontrado na conta")
        except ErroRede as e:
            falha("instagram", ig, e)
    elif ig:
        avisos.append("instagram: falta IG_ACCESS_TOKEN")
    chave = "EXEMPLO" if exemplo else segredo("YT_API_KEY")
    if yt and chave:
        try:
            d = youtube(http, chave, sorted({v for v in yt.values() if v}))
            for s, v in yt.items():
                lidos["youtube"][s] = d.get(v) or {"erro_leitura": True}
                if v in d and d[v].get("erro"):
                    avisos.append(f"youtube {v}: comentários indisponíveis ({d[v]['erro']})")
        except ErroRede as e:
            falha("youtube", yt, e)
    elif yt:
        avisos.append("youtube: falta YT_API_KEY")
    ck, cs, rt = (("EXEMPLO",) * 3) if exemplo else (segredo("TT_CLIENT_KEY"), segredo("TT_CLIENT_SECRET"),
                                                    segredo("TT_REFRESH_TOKEN"))
    if tt and ck and cs and rt:
        try:
            d = tiktok(http, tiktok_acesso(http, ck, cs, rt), set(tt.values()))
            for s, v in tt.items():
                lidos["tiktok"][s] = {"metricas": (d.get(v) or {}).get("metricas")}
        except ErroRede as e:
            falha("tiktok", tt, e)
    for ep in episodios:
        arq = ep.get("tiktok_comentarios")
        if arq and (base / arq).is_file():
            lidos["tiktok"].setdefault(ep["slug"], {})["comentarios"] = tiktok_arquivo(base / arq)
            lidos["tiktok"][ep["slug"]].pop("erro_leitura", None)
        elif ep.get("tiktok_votos"):  # contagem feita no computador (os comentários não vão para o site)
            lidos["tiktok"].setdefault(ep["slug"], {})["contagem"] = ep["tiktok_votos"]
            lidos["tiktok"][ep["slug"]].pop("erro_leitura", None)
    return {r: v for r, v in lidos.items()}, avisos


def gerar(arq_episodios, saida=None, detalhe=None, so=None, exemplo=None, agora=None):
    conf = json.loads(Path(arq_episodios).read_text(encoding="utf-8"))
    base = Path(arq_episodios).resolve().parent
    episodios = [e for e in conf["episodios"] if not so or e["slug"] == so]
    if so and not episodios:
        raise SystemExit(f"episódio {so} não está em {arq_episodios}")
    anterior = {}
    if saida and Path(saida).is_file():
        try:
            anterior = {e["slug"]: e for e in json.loads(Path(saida).read_text(encoding="utf-8")).get("episodios", [])}
        except ValueError:
            pass
    http = HTTPExemplo(exemplo) if exemplo else HTTP()
    lidos, avisos = ler_redes(http, episodios, base, exemplo=bool(exemplo))
    agora = agora or datetime.now(timezone.utc)
    regras = conf.get("regras", {})
    publicos, detalhes = [], {}
    for ep in episodios:
        pub, det = apurar_episodio(ep, {r: lidos[r].get(ep["slug"]) for r in REDES}, anterior.get(ep["slug"]), regras,
                                   agora)
        publicos.append(pub)
        detalhes[ep["slug"]] = det
    if so and anterior:  # rodada de um episódio só: os outros ficam como estavam
        publicos += [e for s, e in anterior.items() if s != so]
    canal = {k: v for k, v in conf.get("canal", {}).items() if k in ("nome", "perfil", "site", "perfis")}
    pagina = {"atualizado": agora.isoformat(timespec="seconds"), "canal": canal, "regras": regras,
              "episodios": publicos, "avisos": avisos}
    if saida:
        Path(saida).parent.mkdir(parents=True, exist_ok=True)
        Path(saida).write_text(json.dumps(pagina, ensure_ascii=False, indent=1), encoding="utf-8")
    if detalhe:
        Path(detalhe).parent.mkdir(parents=True, exist_ok=True)
        Path(detalhe).write_text(json.dumps(detalhes[so] if so else detalhes, ensure_ascii=False, indent=1),
                                 encoding="utf-8")
    return pagina, detalhes


# ------------------------------------------------------------------------------------------------ TikTok e GitHub

def _retorno(conf):
    site = (conf.get("canal") or {}).get("site", "").rstrip("/")
    if not site.startswith("https://"):
        raise SystemExit("defina canal.site (https://...) no episodios.json: é para onde o TikTok devolve o código")
    return f"{site}/tiktok_retorno.html"


def tiktok_link(conf):
    ck = segredo("TT_CLIENT_KEY")
    if not ck:
        raise SystemExit("falta TT_CLIENT_KEY (comandos/conectar-redes.md, TikTok)")
    q = {"client_key": ck, "scope": "user.info.basic,video.list", "response_type": "code",
         "redirect_uri": _retorno(conf), "state": secrets.token_hex(8)}
    print("Abra este link logado no @ do canal, autorize e copie o código que a página do seu site mostrar:\n")
    print(f"{TT_AUTORIZAR}?{urlencode(q)}\n")
    print("Depois rode, em até 5 minutos: python placar/placar.py --episodios <arquivo> --tiktok-codigo CODIGO")


def tiktok_codigo(conf, codigo):
    ck, cs = segredo("TT_CLIENT_KEY"), segredo("TT_CLIENT_SECRET")
    if not (ck and cs):
        raise SystemExit("faltam TT_CLIENT_KEY e TT_CLIENT_SECRET")
    if not (_config_kit() and _config_kit().CFG["segredos"].get("arquivo")):
        raise SystemExit("configure segredos.arquivo no config.json do kit antes: o token não pode aparecer na tela")
    r = HTTP().pedido("POST", f"{TT_API}/oauth/token/", data={
        "client_key": ck, "client_secret": cs, "code": codigo, "grant_type": "authorization_code",
        "redirect_uri": _retorno(conf)}, headers={"Content-Type": "application/x-www-form-urlencoded"})
    if not r.get("refresh_token"):
        raise SystemExit(_limpa(f"o TikTok não aceitou o código: {r.get('error_description') or r.get('error')}"))
    grava_segredo("TT_REFRESH_TOKEN", r["refresh_token"])
    print(f"TikTok conectado. TT_REFRESH_TOKEN gravado no arquivo de segredos (escopo: {r.get('scope')}).")


def gh_segredos(repo):
    """Copia as chaves que existirem para os segredos do repositório do site, sem mostrar nenhuma."""
    feitos = []
    for nome in NOMES_SEGREDOS:
        valor = segredo(nome)
        if not valor:
            continue
        r = subprocess.run(["gh", "secret", "set", nome, "-R", repo], input=valor, text=True, capture_output=True)
        if r.returncode:
            raise SystemExit(f"gh falhou em {nome}: {_limpa(r.stderr)}")
        feitos.append(nome)
    print("segredos gravados no GitHub:", ", ".join(feitos) or "nenhum (nenhuma chave encontrada)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--episodios", help="episodios.json (lista de episódios com opções e links de cada rede)")
    ap.add_argument("--saida", help="placar.json público (o que a página lê)")
    ap.add_argument("--detalhe", help="apuração privada com os textos (sem @) para o vídeo seguinte")
    ap.add_argument("--so", help="slug de um episódio só")
    ap.add_argument("--exemplo", help="respostas gravadas das APIs (teste sem chave e sem rede)")
    ap.add_argument("--agora", help="data/hora ISO para simular (teste da janela de votação)")
    ap.add_argument("--tiktok-link", action="store_true")
    ap.add_argument("--tiktok-codigo")
    ap.add_argument("--gh-segredos", metavar="USUARIO/REPOSITORIO")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if a.gh_segredos:
        return gh_segredos(a.gh_segredos)
    if not a.episodios:
        ap.error("informe --episodios")
    conf = json.loads(Path(a.episodios).read_text(encoding="utf-8"))
    if a.tiktok_link:
        return tiktok_link(conf)
    if a.tiktok_codigo:
        return tiktok_codigo(conf, a.tiktok_codigo)
    if not (a.saida or a.detalhe):
        ap.error("informe --saida e/ou --detalhe")
    pagina, _ = gerar(a.episodios, a.saida, a.detalhe, a.so, a.exemplo, _data(a.agora) if a.agora else None)
    for e in pagina["episodios"]:
        votos = " · ".join(f"{o['rotulo']} {(e['votos'] or {}).get(o['id'], 0)}" for o in e["opcoes"])
        print(f"{e['slug']}: {e['status']} | {votos} | total {e['total']}{' (oficial)' if e['oficial'] else ' (prévia)'}"
              f" | por rede {json.dumps(e['por_rede'], ensure_ascii=False)}")
    for av in pagina["avisos"]:
        print("AVISO", av)
    print("PLACAR_OK", a.saida or a.detalhe)


if __name__ == "__main__":
    main()
