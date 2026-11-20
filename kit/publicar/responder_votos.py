# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Sugere (e, só com --sei-o-risco, envia) respostas a comentários que são VOTO no Instagram, pela API oficial.

NÃO RECOMENDADO RESPONDER PELA API: a Meta trata resposta automática como sinal de robô e pode rebaixar ou travar a
conta. O jeito recomendado é responder à mão, no app (metodo/comunidade-e-votos.md, seção 4). Por isso, sem
--sei-o-risco, este script só LÊ os comentários e mostra as respostas sugeridas, para a pessoa colar à mão; nada é
enviado. Com --sei-o-risco, ele responde de verdade, com os limites abaixo.

Uso:
    python -m publicar.responder_votos --respostas respostas.json [--seco] [--comentarios-exemplo arq.json] [--hora H]
    python -m publicar.responder_votos --manual respostas_manuais.json [--seco] [--comentarios-exemplo arq.json]
    python -m publicar.responder_votos --respostas respostas.json --sei-o-risco   # responde de verdade (não recomendado)
    python -m publicar.responder_votos --status

Regras (anti-ban, no código):
- só responde comentário que é voto (número da opção no começo ou a palavra dela; regra em maquina/votos.py);
  negação ("não entra") e comentário com as duas opções ficam sem resposta: o robô nunca arrisca responder errado;
- lote pequeno por rodada (respostas.por_rodada, 3) e teto diário somando tudo (respostas.por_dia, 30);
- amostra: responde só uma fração dos votos (respostas.amostra, 0,5), por sorteio fixo pelo id do comentário;
- 1 resposta por pessoa por vídeo; só comentários recentes (respostas.idade_max_dias, 7);
- texto variado, nunca o mesmo duas vezes seguidas no mesmo vídeo;
- pausa aleatória entre respostas (respostas.pausa_s, 4 a 11 s);
- só no horário de gente (respostas.horario, das 9h à 1h, hora do computador): conta que responde de madrugada
  parece robô;
- PARA no primeiro erro da API e só tenta de novo na próxima rodada.
Não curte (não existe na API oficial), não segue, não manda DM. Não agende o envio: rode à mão, quando for colar as
respostas no app (ver `comandos/conectar-redes.md`, "Respostas aos votos").

--manual: respostas escritas pelo dono a comentários que NÃO são voto (pergunta, elogio, teoria), uma por vez,
com 60 a 150 s entre elas e dentro do mesmo teto diário. Arquivo: [{"video": "<id ou link do reel>",
"usuario": "@quem", "trecho": "começo do comentário", "texto": "a resposta aprovada"}].

respostas.json: {"<id da mídia ou link do reel>": {"opcoes": {"1": ["ENTRAR"], "2": ["FUGIR"]},
                                                   "respostas": {"1": ["texto", ...], "2": ["texto", ...]}}}
Token: IG_ACCESS_TOKEN (permissão instagram_business_manage_comments). Estado em <trabalho>/respondidos.json.
"""
import argparse
import hashlib
import json
import random
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from config import CFG, pasta

from maquina.votos import voto_do

from .http import Cliente
from .ig_token import token_instagram

IG = CFG["publicar"]["instagram"]
R = CFG["respostas"]


def _chave_link(permalink):
    return re.sub(r"^https?://(www\.)?instagram\.com", "", (permalink or "").split("?")[0].rstrip("/"))


def _autor(c):
    """A API nem sempre manda `username` no comentário; o @ também vem em `from`."""
    return c.get("username") or (c.get("from") or {}).get("username") or ""


def _sorteado(cid, fracao):
    return int(hashlib.md5(("r" + cid).encode()).hexdigest()[:4], 16) / 0xFFFF < fracao


def no_horario(hora, janela=None):
    """True se `hora` (0-23) está na janela [ini, fim) de respostas.horario; janela que vira a meia-noite vale."""
    ini, fim = janela or R.get("horario", [9, 1])
    return ini <= hora < fim if ini < fim else (hora >= ini or hora < fim)


def _estado(arq):
    hoje = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    est = json.loads(arq.read_text(encoding="utf-8")) if arq.is_file() else {}
    est = {"ids": [], "pessoas": [], "dia": hoje, "hoje": 0, "ultima": {}, "feitas": [], **est}
    if est["dia"] != hoje:
        est.update(dia=hoje, hoje=0)
    return est


def _gravar(est, arq):
    for k in ("ids", "pessoas"):
        est[k] = est[k][-3000:]
    est["feitas"] = est["feitas"][-50:]
    arq.write_text(json.dumps(est, ensure_ascii=False), encoding="utf-8")


class FonteAPI:
    """Lê mídias e comentários pela API (no seco, só mostra os pedidos de leitura e não lê nada)."""

    def __init__(self, cli, tok):
        self.cli, self.tok = cli, tok
        self.base = f"{IG['api'].rstrip('/')}/{IG['versao']}"

    def eu(self):
        r, _ = self.cli.pedido("GET", f"{self.base}/me", params={"fields": "username", "access_token": self.tok},
                               descricao="ler o próprio @", falso={"username": "seu_perfil"})
        return r.get("username", "")

    def midias(self):
        r, _ = self.cli.pedido("GET", f"{self.base}/me/media", params={"fields": "id,permalink", "limit": 50,
                                                                        "access_token": self.tok},
                               descricao="listar reels", falso={"data": []})
        return r.get("data", [])

    def comentarios(self, mid):
        r, _ = self.cli.pedido("GET", f"{self.base}/{mid}/comments", params={
            "fields": "id,text,username,from,timestamp,replies{username,from}", "limit": 50, "access_token": self.tok},
            descricao=f"comentários de {mid}", falso={"data": []})
        return r.get("data", [])


class FonteExemplo:
    """Comentários de um arquivo (teste offline da lógica, sem token e sem rede)."""

    def __init__(self, arq):
        self.d = json.loads(Path(arq).read_text(encoding="utf-8"))

    def eu(self):
        return self.d.get("eu", "")

    def midias(self):
        return [{"id": m["id"], "permalink": m.get("permalink", "")} for m in self.d["midias"]]

    def comentarios(self, mid):
        out = []
        for cm in next(m["comentarios"] for m in self.d["midias"] if m["id"] == mid):
            cm = dict(cm)
            if "minutos_atras" in cm:  # o arquivo de teste usa idade relativa para não "vencer"
                ts = datetime.fromtimestamp(time.time() - cm.pop("minutos_atras") * 60, timezone.utc)
                cm["timestamp"] = ts.strftime("%Y-%m-%dT%H:%M:%S+0000")
            out.append(cm)
        return sorted(out, key=lambda c: c["timestamp"], reverse=True)  # igual à API: mais novo primeiro


def _responder(cli, tok, cid, texto, descricao):
    cli.pedido("POST", f"{IG['api'].rstrip('/')}/{IG['versao']}/{cid}/replies",
               data={"message": texto, "access_token": tok}, descricao=descricao, falso={"id": "SECO_RESPOSTA"})


AVISO = ("AVISO: responder comentário pela API não é recomendado (a Meta trata como robô e pode rebaixar a conta). "
         "Sem --sei-o-risco, nada é enviado: as respostas abaixo são sugestões para colar à mão no app.")


def rodada(conf, fonte, cli, tok, seco, arq_estado, agora=None, enviar=True):
    """Uma rodada de respostas aos votos. `enviar=False`: só sugere (lê os comentários e não responde nada)."""
    est = _estado(arq_estado)
    agora = agora or time.time()
    idade_max = float(R["idade_max_dias"]) * 86400
    # Sugestão para colar à mão não gasta limite de API: o lote é o teto do dia, não o da rodada.
    por_rodada = int(R["por_rodada"]) if enviar else int(R["por_dia"])
    eu = fonte.eu()
    feitas, erros = [], []
    for m in fonte.midias():
        c = conf.get(m["id"]) or conf.get(_chave_link(m.get("permalink")))
        if not c:
            continue
        chave_video = m["id"]
        for cm in reversed(fonte.comentarios(m["id"])):  # a API devolve do mais novo para o mais antigo
            if len(feitas) >= por_rodada or est["hoje"] >= int(R["por_dia"]):
                break
            autor = _autor(cm)
            if cm["id"] in est["ids"] or (autor and autor == eu):
                continue
            ts = datetime.strptime(cm["timestamp"].replace("Z", "+0000"), "%Y-%m-%dT%H:%M:%S%z").timestamp()
            if agora - ts > idade_max:
                continue
            if any(_autor(rp) == eu for rp in cm.get("replies", {}).get("data", [])):
                est["ids"].append(cm["id"])
                continue
            v = voto_do(cm.get("text", ""), c["opcoes"])
            if v is None:
                continue
            quem = f"{chave_video}:{autor or cm['id']}"
            if not _sorteado(cm["id"], float(R["amostra"])) or quem in est["pessoas"]:
                est["ids"].append(cm["id"])
                continue
            lista = c["respostas"][v]
            ult = est["ultima"].get(f"{chave_video}:{v}", -1)
            i = int(hashlib.md5(cm["id"].encode()).hexdigest()[:6], 16) % len(lista)
            if i == ult and len(lista) > 1:
                i = (i + 1) % len(lista)
            if not enviar:
                feitas.append({"video": chave_video, "usuario": f"@{autor}", "comentario": cm.get("text", ""),
                               "voto": v, "sugestao": lista[i]})
                est["ultima"][f"{chave_video}:{v}"] = i
                est["pessoas"].append(quem)
                continue
            try:
                _responder(cli, tok, cm["id"], lista[i], f"responder voto {v} de @{autor}")
            except Exception as e:
                erros.append(str(e)[:300])
                break  # erro da API: para tudo; tenta de novo só na próxima rodada
            est["ids"].append(cm["id"])
            est["pessoas"].append(quem)
            est["hoje"] += 1
            est["ultima"][f"{chave_video}:{v}"] = i
            item = {"quando": datetime.now(timezone.utc).isoformat(), "video": chave_video, "voto": v, "resposta": lista[i]}
            feitas.append(item)
            est["feitas"].append(item)
            pausa = random.uniform(*R["pausa_s"])
            print(f"respondido voto {v}; pausa de {pausa:.1f} s" + (" (simulada no seco)" if seco else ""), flush=True)
            if not seco:
                time.sleep(pausa)
        if erros or len(feitas) >= por_rodada or est["hoje"] >= int(R["por_dia"]):
            break
    if not enviar:
        return dict(enviadas=0, sugestoes=feitas)
    if not seco:
        _gravar(est, arq_estado)
    return dict(respondidas=len(feitas), hoje=est["hoje"], feitas=feitas, erros=erros)


def manual(lista, fonte, cli, tok, seco, arq_estado, enviar=True):
    """Respostas aprovadas pelo dono, uma por vez, dentro do teto diário; nunca duas vezes no mesmo comentário.

    `enviar=False`: só confere que o comentário existe e mostra a resposta para colar à mão.
    """
    est = _estado(arq_estado)
    eu = fonte.eu()
    midias = fonte.midias()
    out = []
    for n, r in enumerate(lista):
        texto = r["texto"].strip()
        if len(texto) > int(R.get("manual_max_caracteres", 300)):
            out.append({"usuario": r["usuario"], "erro": "resposta longa demais"})
            continue
        if est["hoje"] >= int(R["por_dia"]):
            out.append({"usuario": r["usuario"], "erro": "teto diário"})
            break
        m = next((m for m in midias if r["video"] in (m["id"], _chave_link(m.get("permalink")))
                  or _chave_link(r["video"]) == _chave_link(m.get("permalink"))), None)
        if not m:
            out.append({"usuario": r["usuario"], "erro": "vídeo não encontrado"})
            continue
        quem, trecho = r["usuario"].lstrip("@"), (r.get("trecho") or "").strip().lower()
        cm = next((c for c in fonte.comentarios(m["id"])
                   if _autor(c) == quem and (c.get("text") or "").lower().startswith(trecho)), None)
        if not cm:
            out.append({"usuario": r["usuario"], "erro": "comentário não encontrado"})
            continue
        if cm["id"] in est["ids"] or any(_autor(rp) == eu for rp in cm.get("replies", {}).get("data", [])):
            out.append({"usuario": r["usuario"], "pulado": "já respondido"})
            continue
        if not enviar:
            out.append({"usuario": r["usuario"], "comentario": cm.get("text", ""), "colar": texto})
            continue
        try:
            _responder(cli, tok, cm["id"], texto, f"resposta manual a @{quem}")
        except Exception as e:
            out.append({"usuario": r["usuario"], "erro": str(e)[:300]})
            break
        est["ids"].append(cm["id"])
        est["hoje"] += 1
        est["feitas"].append({"quando": datetime.now(timezone.utc).isoformat(), "video": m["id"], "voto": "manual",
                              "resposta": texto})
        out.append({"usuario": r["usuario"], "respondido": True})
        if n < len(lista) - 1:
            pausa = random.uniform(*R.get("manual_pausa_s", [60, 150]))
            print(f"respondido @{quem}; pausa de {pausa:.0f} s" + (" (simulada no seco)" if seco else ""), flush=True)
            if not seco:
                time.sleep(pausa)
    if enviar and not seco:
        _gravar(est, arq_estado)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--respostas", help="respostas.json (respostas automáticas aos votos)")
    ap.add_argument("--manual", help="respostas_manuais.json (respostas aprovadas, uma por comentário)")
    ap.add_argument("--seco", action="store_true", help="monta as respostas e não envia nada")
    ap.add_argument("--comentarios-exemplo", help="arquivo com comentários de teste (só com --seco)")
    ap.add_argument("--hora", type=int, help="simula a hora local (teste do horário)")
    ap.add_argument("--status", action="store_true", help="só mostra o registro do dia")
    ap.add_argument("--sei-o-risco", action="store_true",
                    help="responde de verdade pela API (não recomendado: a Meta pode rebaixar a conta). "
                         "Sem esta opção, só mostra as respostas sugeridas para colar à mão")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # comentário com emoji não quebra o terminal do Windows
    arq_estado = pasta("trabalho") / "respondidos.json"
    if a.status:
        est = _estado(arq_estado)
        print(json.dumps({"dia": est["dia"], "hoje": est["hoje"], "teto": R["por_dia"], "ultimas": est["feitas"][-10:]},
                         ensure_ascii=False, indent=1))
        return
    if not (a.respostas or a.manual):
        ap.error("informe --respostas ou --manual")
    if a.comentarios_exemplo and not a.seco:
        ap.error("--comentarios-exemplo só vale com --seco")
    enviar = a.sei_o_risco
    print(AVISO if not enviar else "AVISO: --sei-o-risco ligado: as respostas vão ser enviadas pela API "
          "(não recomendado; a Meta pode rebaixar a conta).", flush=True)
    hora = datetime.now().hour if a.hora is None else a.hora
    if enviar and a.respostas and not no_horario(hora):
        ini, fim = R.get("horario", [9, 1])
        print(json.dumps({"respondidas": 0, "pulado": f"fora do horário ({hora}h; o robô responde das {ini}h às {fim}h)"},
                         ensure_ascii=False))
        return
    # Sem envio, a leitura dos comentários (GET) continua real; só as respostas (POST) não saem.
    tok = token_instagram(a.seco)
    cli = Cliente(a.seco)
    fonte = FonteExemplo(a.comentarios_exemplo) if a.comentarios_exemplo else FonteAPI(cli, tok)
    if a.manual:
        lista = json.loads(Path(a.manual).read_text(encoding="utf-8"))
        print(json.dumps(manual(lista, fonte, cli, tok, a.seco, arq_estado, enviar), ensure_ascii=False, indent=1))
    else:
        conf = json.loads(Path(a.respostas).read_text(encoding="utf-8"))
        print(json.dumps(rodada(conf, fonte, cli, tok, a.seco, arq_estado, enviar=enviar), ensure_ascii=False,
                         indent=1))


if __name__ == "__main__":
    main()
