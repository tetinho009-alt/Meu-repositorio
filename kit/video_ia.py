# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""IA de vídeo com a chave do próprio usuário (fal.ai ou Higgsfield): orçamento, geração de clipe e gastos.

Uso (a partir da pasta kit/):
    python video_ia.py modelos                         # modelos, preço por segundo e qual conta está ligada
    python video_ia.py conferir                        # testa as chaves salvas (não gasta nada)
    python video_ia.py custo --modelo seedance --segundos 8 [--resolucao 480p] [--audio]
    python video_ia.py gerar --modelo seedance --prompt-arquivo cena01.txt --imagem morango.png --imagem uva.png \
        --segundos 8 --saida cena01.mp4 --ate-usd 2.00
    python video_ia.py gastos                          # quanto já foi gasto, por mês

Regras de dinheiro:
- `gerar` só envia se `--ate-usd` cobrir o orçamento. A IA mostra o custo ao usuário e só passa o teto depois do "pode".
- Nunca reenviar por conta própria um pedido que falhou no meio do envio: pode ter sido cobrado. Conferir em `gastos`.

As chaves ficam no arquivo de segredos fora do kit (painel, tela IA de vídeo). Nada aqui imprime a chave.
Só biblioteca padrão: roda no Python do painel sem instalar nada.
"""
import argparse
import json
import mimetypes
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime
from pathlib import Path

KIT = Path(__file__).resolve().parent
GASTOS = KIT.parent / "canal" / "video_ia_gastos.json"
UA = {"User-Agent": "temporada-viral-kit"}
CONFERIDO_EM = "16/11/2026"

# Nome da chave no arquivo de segredos -> nome no painel.
CHAVES = {"FAL_KEY": "fal.ai", "HIGGSFIELD_API_KEY": "Higgsfield"}

# Preço de tabela por segundo (US$), conferido nas páginas dos modelos. O Higgsfield tem orçamento exato grátis
# (/estimate), usado antes de gerar; a tabela dele aqui é só a referência quando o orçamento não responde.
MODELOS = {
    "seedance": {
        "nome": "Seedance 2.5",
        "faz": "Fala em português com a boca sincronizada, até 30 imagens de referência (personagem igual em toda cena).",
        "segundos": (4, 30), "resolucoes": ("480p", "720p"), "audio_padrao": True, "fala_pt": True,
        "fal": {"id": "bytedance/seedance-2.5/reference-to-video", "por_s": {"480p": 0.2205, "720p": 0.473}},
        "higgsfield": {"id": "bytedance/seedance-2.5/reference-to-video", "por_s": {"480p": 0.2205, "720p": 0.473}},
    },
    "kling": {
        "nome": "Kling 3.0 Standard",
        "faz": "Movimento bonito a partir de uma imagem. A fala dele é só inglês ou chinês: a voz vem do narrador do kit.",
        "segundos": (3, 15), "resolucoes": ("720p",), "audio_padrao": False, "fala_pt": False,
        "fal": {"id": "fal-ai/kling-video/v3/standard/image-to-video", "por_s": {"720p": 0.084}, "por_s_audio": 0.126},
        "higgsfield": {"id": "kling-video/v3.0/std/image-to-video", "por_s": {"720p": 0.084}, "por_s_audio": 0.126},
    },
    "minimax": {
        "nome": "MiniMax H3",
        "faz": "O mais barato, bom para testar o roteiro. Sem fala: a voz vem do narrador do kit.",
        "segundos": (5, 15), "resolucoes": ("480p", "768p"), "audio_padrao": False, "fala_pt": False,
        "fal": {"id": "minimax/h3/image-to-video", "por_s": {"480p": 0.05, "768p": 0.06}},
    },
}
PROVEDOR_DA_CHAVE = {"fal": "FAL_KEY", "higgsfield": "HIGGSFIELD_API_KEY"}


class ErroVideo(RuntimeError):
    pass


# ---------------------------------------------------------------- chaves

def segredo(nome):
    """Valor da chave salva, ou "" se não houver. Nunca imprime."""
    try:
        sys.path.insert(0, str(KIT))
        import config  # noqa: PLC0415
        return (config.segredo(nome, obrigatorio=False) or "").strip()
    except BaseException:  # noqa: BLE001  (config sai com SystemExit sem licença; o painel não pode cair por isso)
        return ""


def ligados():
    """{"fal": bool, "higgsfield": bool}"""
    return {p: bool(segredo(n)) for p, n in PROVEDOR_DA_CHAVE.items()}


def _cabecalho(provedor, chave):
    return dict(UA, Authorization=f"Key {chave}")


def _http(metodo, url, cabecalhos=None, corpo=None, bruto=None, tempo=60):
    """(status, json ou {}). Status -1 = sem internet."""
    dados = bruto if bruto is not None else (json.dumps(corpo).encode("utf-8") if corpo is not None else None)
    cab = dict(cabecalhos or {})
    if corpo is not None:
        cab["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=dados, headers=cab, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=tempo) as r:
            texto = r.read().decode("utf-8", "replace")
            return r.status, (json.loads(texto) if texto.strip().startswith(("{", "[")) else {})
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read(20000).decode("utf-8", "replace"))
        except Exception:  # noqa: BLE001
            return e.code, {}
    except Exception:  # noqa: BLE001
        return -1, {}


def testar(nome, valor):
    """(ok, mensagem, None) sem gastar nada. Usado pelo painel antes de salvar."""
    valor = "".join(str(valor or "").split())
    if nome == "FAL_KEY":
        st, _ = _http("GET", "https://api.fal.ai/v1/models/pricing?endpoint_id=" + MODELOS["seedance"]["fal"]["id"],
                      _cabecalho("fal", valor), tempo=30)
        if st == 200:
            return True, "A chave funcionou. O vídeo é cobrado do saldo da sua conta fal.ai, por segundo gerado.", None
        servico = "O fal.ai"
    elif nome == "HIGGSFIELD_API_KEY":
        if ":" not in valor:
            return False, ("A chave do Higgsfield tem duas partes: o Key ID e o Secret. Cole os dois, separados por "
                           "dois-pontos (ID:SECRET)."), None
        st, _ = _http("GET", f"https://api.higgsfield.ai/requests/{uuid.uuid4()}/status",
                      _cabecalho("higgsfield", valor), tempo=30)
        if st in (200, 404, 422):     # 404: pedido inexistente, mas a chave foi aceita
            return True, ("A chave funcionou. O vídeo é cobrado do saldo em dólar da sua conta de API do Higgsfield "
                          "(não é o mesmo do plano do site)."), None
        servico = "O Higgsfield"
    else:
        return False, "Tipo de chave desconhecido.", None
    if st == -1:
        return False, "Sem internet ou o serviço não respondeu. Tente de novo em instantes.", None
    if st in (401, 403):
        return False, f"{servico} recusou essa chave. Confira se copiou o código inteiro e tente de novo.", None
    return False, f"{servico} respondeu de um jeito inesperado (código {st}). Tente de novo em instantes.", None


# ---------------------------------------------------------------- orçamento

def escolher_provedor(modelo, pedido=None):
    disp = [p for p in ("fal", "higgsfield") if p in MODELOS[modelo]]
    lig = ligados()
    if pedido:
        if pedido not in disp:
            raise ErroVideo(f"O {MODELOS[modelo]['nome']} não está disponível pelo {pedido}.")
        if not lig[pedido]:
            raise ErroVideo(f"A chave do {pedido} não está salva. No painel: IA de vídeo, conectar.")
        return pedido
    for p in disp:
        if lig[p]:
            return p
    raise ErroVideo("Nenhuma conta de IA de vídeo ligada para esse modelo. No painel: IA de vídeo, conectar.")


def _validar(modelo, segundos, resolucao):
    if modelo not in MODELOS:
        raise ErroVideo(f"Modelo desconhecido: {modelo}. Opções: {', '.join(MODELOS)}.")
    m = MODELOS[modelo]
    lo, hi = m["segundos"]
    if not lo <= segundos <= hi:
        raise ErroVideo(f"O {m['nome']} gera de {lo} a {hi} segundos por clipe.")
    resolucao = resolucao or m["resolucoes"][0]
    if resolucao not in m["resolucoes"]:
        raise ErroVideo(f"Resolução do {m['nome']}: {', '.join(m['resolucoes'])}.")
    return resolucao


def preco_tabela(modelo, provedor, segundos, resolucao, audio):
    info = MODELOS[modelo][provedor]
    por_s = info.get("por_s_audio") if audio and info.get("por_s_audio") else info["por_s"][resolucao]
    return round(por_s * segundos, 3)


def corpo(modelo, provedor, prompt, imagens, segundos, resolucao, audio):
    """Corpo do pedido no formato de cada serviço (nomes conferidos na documentação de cada modelo)."""
    if modelo == "seedance":
        c = {"prompt": prompt, "image_urls": imagens, "resolution": resolucao, "aspect_ratio": "9:16",
             "generate_audio": bool(audio)}
        c["duration"] = str(segundos) if provedor == "fal" else int(segundos)
        return c
    if modelo == "kling":
        if provedor == "fal":
            return {"prompt": prompt, "start_image_url": imagens[0], "duration": str(segundos), "generate_audio": bool(audio)}
        return {"prompt": prompt, "image_url": imagens[0], "duration": int(segundos), "sound": "on" if audio else "off"}
    if modelo == "minimax":
        return {"prompt": prompt, "image_url": imagens[0], "duration": int(segundos), "resolution": resolucao.upper()}
    raise ErroVideo(f"Modelo desconhecido: {modelo}")


def orcamento(modelo, segundos, resolucao=None, audio=None, provedor=None, imagens_exemplo=None):
    """{"usd", "exato", "provedor", ...}. No Higgsfield pede o orçamento exato (grátis); no fal usa a tabela."""
    resolucao = _validar(modelo, segundos, resolucao)
    audio = MODELOS[modelo]["audio_padrao"] if audio is None else audio
    prov = escolher_provedor(modelo, provedor)
    usd, exato = preco_tabela(modelo, prov, segundos, resolucao, audio), False
    if prov == "higgsfield":
        info = MODELOS[modelo]["higgsfield"]
        ex = imagens_exemplo or ["https://example.com/personagem.png"]
        st, r = _http("POST", f"https://api.higgsfield.ai/estimate/{info['id']}",
                      _cabecalho(prov, segredo("HIGGSFIELD_API_KEY")),
                      corpo(modelo, prov, "orçamento", ex, segundos, resolucao, audio), tempo=30)
        try:
            if st == 200 and r.get("usd") is not None:
                usd, exato = round(float(r["usd"]), 3), True
        except (TypeError, ValueError):
            pass
    return {"usd": usd, "exato": exato, "provedor": prov, "modelo": modelo, "segundos": segundos,
            "resolucao": resolucao, "audio": audio}


# ---------------------------------------------------------------- envio de imagem e geração

def _tipo(caminho):
    t = mimetypes.guess_type(str(caminho))[0] or ""
    if t not in ("image/png", "image/jpeg", "image/webp"):
        raise ErroVideo(f"Imagem de referência precisa ser PNG, JPG ou WebP: {Path(caminho).name}")
    return t


def subir_imagem(provedor, caminho, chave):
    """Sobe a imagem local para o armazenamento do próprio serviço e devolve a URL pública dela."""
    caminho = Path(caminho)
    if not caminho.is_file():
        raise ErroVideo(f"Não achei a imagem: {caminho}")
    tipo, dados = _tipo(caminho), caminho.read_bytes()
    if provedor == "fal":
        st, r = _http("POST", "https://rest.fal.ai/storage/upload/initiate?storage_type=fal-cdn-v3",
                      _cabecalho(provedor, chave), {"file_name": caminho.name, "content_type": tipo})
        if st != 200 or not r.get("upload_url"):
            raise ErroVideo(f"O fal.ai não aceitou a imagem {caminho.name} (código {st}).")
        st2, _ = _http("PUT", r["upload_url"], {"Content-Type": tipo}, bruto=dados, tempo=180)
        if st2 not in (200, 201, 204):
            raise ErroVideo(f"A imagem {caminho.name} não subiu (código {st2}).")
        return r["file_url"]
    st, r = _http("POST", "https://api.higgsfield.ai/files/generate-upload-url", _cabecalho(provedor, chave),
                  {"content_type": tipo})
    if st != 200 or not r.get("upload_url"):
        raise ErroVideo(f"O Higgsfield não aceitou a imagem {caminho.name} (código {st}).")
    st2, _ = _http("PUT", r["upload_url"], dict(r.get("upload_headers") or {"Content-Type": tipo}), bruto=dados, tempo=180)
    if st2 not in (200, 201, 204):
        raise ErroVideo(f"A imagem {caminho.name} não subiu (código {st2}).")
    return r["public_url"]


def _registrar(item):
    GASTOS.parent.mkdir(parents=True, exist_ok=True)
    try:
        lista = json.loads(GASTOS.read_text(encoding="utf-8")) if GASTOS.is_file() else []
    except (OSError, ValueError):
        lista = []
    lista.append(item)
    GASTOS.write_text(json.dumps(lista, ensure_ascii=False, indent=1), encoding="utf-8")


def _esperar(provedor, chave, status_url, response_url, limite_s=1800):
    """Consulta o pedido até terminar. Espera cresce de 5 s até 20 s. Devolve a URL do vídeo."""
    cab, inicio, espera, falhas = _cabecalho(provedor, chave), time.time(), 5, 0
    while time.time() - inicio < limite_s:
        time.sleep(espera)
        espera = min(20, espera + 3)
        st, r = _http("GET", status_url, cab, tempo=60)
        if st == -1 or st >= 500:
            falhas += 1
            if falhas > 10:
                raise ErroVideo("O serviço parou de responder. O pedido pode terminar sozinho: confira no site da conta.")
            continue
        falhas = 0
        estado = str(r.get("status", "")).lower()
        if provedor == "fal":
            if estado != "completed":
                continue
            if r.get("error"):
                raise ErroVideo(f"O fal.ai não conseguiu gerar: {r['error']}")
            st, res = _http("GET", response_url, cab, tempo=60)
            url = (res.get("video") or {}).get("url")
            if not url:
                raise ErroVideo("O fal.ai terminou, mas não devolveu o vídeo.")
            return url
        if estado == "completed":
            url = (r.get("video") or {}).get("url")
            if not url:
                raise ErroVideo("O Higgsfield terminou, mas não devolveu o vídeo.")
            return url
        if estado in ("failed", "nsfw", "canceled"):
            motivo = {"nsfw": "a moderação recusou a cena (troque o pedido)", "canceled": "o pedido foi cancelado"}
            raise ErroVideo(f"O Higgsfield não gerou: {motivo.get(estado, r.get('error') or 'falhou')}. Não foi cobrado.")
    raise ErroVideo("Passou de 30 minutos sem terminar. Confira no site da conta antes de pedir de novo.")


def gerar(modelo, prompt, imagens, segundos, saida, ate_usd, resolucao=None, audio=None, provedor=None):
    """Gera um clipe e salva em `saida`. Recusa se o orçamento passar de `ate_usd`."""
    if not prompt.strip():
        raise ErroVideo("Escreva o que acontece na cena (o pedido).")
    if not imagens:
        raise ErroVideo("Passe pelo menos uma imagem de referência (--imagem).")
    if modelo != "seedance" and len(imagens) > 1:
        raise ErroVideo(f"O {MODELOS[modelo]['nome']} usa uma imagem só (o primeiro quadro). Para vários personagens "
                        "na mesma cena, use o seedance.")
    orc = orcamento(modelo, segundos, resolucao, audio, provedor)
    if ate_usd is None or orc["usd"] > float(ate_usd) + 1e-9:
        raise ErroVideo(f"Esse clipe custa {'' if orc['exato'] else 'cerca de '}US$ {orc['usd']:.2f} e o teto "
                        f"autorizado é US$ {float(ate_usd or 0):.2f}. Mostre o custo e peça o ok antes.")
    prov, chave = orc["provedor"], segredo(PROVEDOR_DA_CHAVE[orc["provedor"]])
    urls = [subir_imagem(prov, im, chave) for im in imagens]
    c = corpo(modelo, prov, prompt, urls, segundos, orc["resolucao"], orc["audio"])
    cab = _cabecalho(prov, chave)
    if prov == "fal":
        st, r = _http("POST", f"https://queue.fal.run/{MODELOS[modelo]['fal']['id']}", cab, c)
    else:
        cab["Idempotency-Key"] = str(uuid.uuid4())
        st, r = _http("POST", f"https://api.higgsfield.ai/{MODELOS[modelo]['higgsfield']['id']}", cab, c)
    if st == -1:
        raise ErroVideo("A internet caiu no envio. NÃO peça de novo antes de conferir no site da conta se ele entrou.")
    if st == 403 and prov == "higgsfield":
        raise ErroVideo("Saldo insuficiente na conta de API do Higgsfield. Coloque saldo e tente de novo.")
    if st in (401, 403):
        raise ErroVideo("O serviço recusou a chave ou o saldo acabou. Confira a conta.")
    if st not in (200, 201, 202) or not r.get("status_url"):
        detalhe = r.get("detail") if isinstance(r, dict) else ""
        raise ErroVideo(f"O pedido foi recusado (código {st}). {detalhe if isinstance(detalhe, str) else ''}".strip())
    item = {"quando": datetime.now().isoformat(timespec="seconds"), "provedor": prov, "modelo": modelo,
            "segundos": segundos, "resolucao": orc["resolucao"], "usd": orc["usd"], "exato": orc["exato"],
            "pedido": r.get("request_id"), "saida": str(saida), "estado": "enviado"}
    _registrar(item)   # registra já no envio: se cair depois, o gasto continua anotado
    url = _esperar(prov, chave, r["status_url"], r.get("response_url"))
    saida = Path(saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as resp:
        saida.write_bytes(resp.read())
    _marcar_pronto(item["pedido"])
    return {"saida": str(saida), "usd": orc["usd"], "provedor": prov}


def _marcar_pronto(pedido):
    try:
        lista = json.loads(GASTOS.read_text(encoding="utf-8"))
        for it in lista:
            if it.get("pedido") == pedido:
                it["estado"] = "pronto"
        GASTOS.write_text(json.dumps(lista, ensure_ascii=False, indent=1), encoding="utf-8")
    except (OSError, ValueError):
        pass


def resumo_gastos():
    """{"mes": US$ do mês, "total": US$, "clipes": n, "por_mes": {...}} para o painel."""
    try:
        lista = json.loads(GASTOS.read_text(encoding="utf-8")) if GASTOS.is_file() else []
    except (OSError, ValueError):
        lista = []
    por_mes = {}
    for it in lista:
        m = str(it.get("quando", ""))[:7]
        por_mes[m] = round(por_mes.get(m, 0) + float(it.get("usd") or 0), 2)
    agora = datetime.now().strftime("%Y-%m")
    return {"mes": por_mes.get(agora, 0.0), "total": round(sum(por_mes.values()), 2), "clipes": len(lista),
            "por_mes": por_mes}


def estado_painel():
    """Tudo que a tela IA de vídeo precisa, sem chave nenhuma."""
    lig = ligados()
    modelos = []
    for ident, m in MODELOS.items():
        prov = [p for p in ("fal", "higgsfield") if p in m]
        base = m[prov[0]]
        res = m["resolucoes"][0]
        por_s = base["por_s"][res]
        modelos.append({"id": ident, "nome": m["nome"], "faz": m["faz"], "fala_pt": m["fala_pt"], "provedores": prov,
                        "por_s": por_s, "resolucao": res, "novelinha_60s": [round(por_s * 30, 2), round(por_s * 60, 2)]})
    return {"ligados": lig, "modelos": modelos, "gastos": resumo_gastos(), "conferido_em": CONFERIDO_EM}


# ---------------------------------------------------------------- linha de comando

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("modelos")
    sub.add_parser("conferir")
    sub.add_parser("gastos")
    for nome in ("custo", "gerar"):
        p = sub.add_parser(nome)
        p.add_argument("--modelo", required=True, choices=list(MODELOS))
        p.add_argument("--segundos", type=int, required=True)
        p.add_argument("--resolucao")
        p.add_argument("--provedor", choices=["fal", "higgsfield"])
        g = p.add_mutually_exclusive_group()
        g.add_argument("--audio", dest="audio", action="store_true", default=None)
        g.add_argument("--sem-audio", dest="audio", action="store_false")
        if nome == "gerar":
            p.add_argument("--prompt")
            p.add_argument("--prompt-arquivo")
            p.add_argument("--imagem", action="append", default=[])
            p.add_argument("--saida", required=True)
            p.add_argument("--ate-usd", type=float, required=True,
                           help="teto autorizado pelo usuário para ESTE clipe, em dólar")
    a = ap.parse_args()
    try:
        if a.cmd == "modelos":
            lig = ligados()
            print(f"Contas ligadas: fal.ai {'sim' if lig['fal'] else 'não'}, Higgsfield {'sim' if lig['higgsfield'] else 'não'}")
            print(f"Preços de tabela conferidos em {CONFERIDO_EM} (US$ por segundo de vídeo):")
            for ident, m in MODELOS.items():
                prov = [p for p in ("fal", "higgsfield") if p in m]
                precos = ", ".join(f"{r} {v}" for r, v in m[prov[0]]["por_s"].items())
                print(f"- {ident} ({m['nome']}; {' e '.join(prov)}): {precos}. {m['faz']}")
        elif a.cmd == "conferir":
            for nome, rot in CHAVES.items():
                v = segredo(nome)
                print(f"{rot}: " + (testar(nome, v)[1] if v else "sem chave salva."))
        elif a.cmd == "gastos":
            g = resumo_gastos()
            print(f"Este mês: US$ {g['mes']:.2f}. Total: US$ {g['total']:.2f} em {g['clipes']} clipes.")
        elif a.cmd == "custo":
            o = orcamento(a.modelo, a.segundos, a.resolucao, a.audio, a.provedor)
            print(f"{MODELOS[a.modelo]['nome']} pelo {o['provedor']}, {o['segundos']} s em {o['resolucao']}"
                  f"{' com áudio' if o['audio'] else ''}: {'' if o['exato'] else 'cerca de '}US$ {o['usd']:.2f}"
                  f"{' (orçamento exato da conta)' if o['exato'] else ' (preço de tabela)'}.")
        else:
            prompt = a.prompt or (Path(a.prompt_arquivo).read_text(encoding="utf-8") if a.prompt_arquivo else "")
            r = gerar(a.modelo, prompt, a.imagem, a.segundos, a.saida, a.ate_usd, a.resolucao, a.audio, a.provedor)
            print(f"Pronto: {r['saida']} (US$ {r['usd']:.2f} pelo {r['provedor']}).")
    except ErroVideo as e:
        print(f"ERRO: {e}\nO QUE FAZER: siga o que a mensagem diz; a chave e o saldo ficam no painel, tela IA de vídeo.")
        sys.exit(3)


if __name__ == "__main__":
    main()
