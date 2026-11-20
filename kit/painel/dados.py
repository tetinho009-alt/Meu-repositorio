# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""O que o painel mostra, lido dos arquivos do estúdio a cada pedido (o que a IA muda aparece no próximo refresh).

Nada aqui lê nem devolve chave: a presença de uma chave é conferida pelo `config.segredo` do kit e só vira
verdadeiro ou falso. Os módulos de outras partes do kit (métricas, conferidor de gancho, biblioteca de ganchos) são
importados só na hora do uso; se ainda não existirem, o painel mostra que o recurso chega numa próxima versão.
"""
import ast
import hashlib
import importlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

PAINEL = Path(__file__).resolve().parent
KIT = PAINEL.parent
ESTUDIO = KIT.parent
CANAL = ESTUDIO / "canal"
if str(KIT) not in sys.path:
    sys.path.insert(0, str(KIT))

import md  # noqa: E402  (painel/md.py, mesmo diretório)

EXT_MIDIA = {".mp4": "video/mp4", ".webm": "video/webm", ".mov": "video/quicktime", ".jpg": "image/jpeg",
             ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp", ".gif": "image/gif",
             ".mp3": "audio/mpeg", ".wav": "audio/wav"}
REDE_DA_PASTA = {"IG": "instagram", "INSTAGRAM": "instagram", "TIKTOK": "tiktok", "YOUTUBE": "youtube_shorts",
                 "YOUTUBE_LONGO": "youtube_longo", "KWAI": "kwai"}
ROTULOS_OPCOES = {
    "gratis": "Grátis", "recomendado": "Recomendado (pago)", "pt-BR": "Português do Brasil",
    "pergunta_aberta": "Pergunta aberta", "sem_voto": "Sem voto",
    "gemini": "Gemini (grátis, Google)", "kokoro": "Kokoro (grátis, sem internet)", "elevenlabs": "ElevenLabs (paga)",
    "flash_whoosh": "Flash com som de passagem", "corte_seco": "Corte seco",
    "titulo_grande": "Título grande", "titulo_e_personagem": "Título e personagem",
    "auto": "Automático (usa a placa se funcionar)", "blender": "Blender (precisa de placa de vídeo)",
    "threejs": "Three.js (roda sem placa, na nuvem também)", "nao": "Não usar a placa (só processador)",
    "30": "30 quadros", "60": "60 quadros", "6M": "6 Mb/s", "8M": "8 Mb/s", "12M": "12 Mb/s",
    "instagram": "Instagram", "tiktok": "TikTok", "youtube_shorts": "YouTube Shorts",
    "youtube_longo": "YouTube longo (16:9)", "kwai": "Kwai",
}
PEDIDOS_CABECALHO = ("# Pedidos do painel\n\n> O que você pediu pelo painel. A IA lê antes de cada episódio, faz o "
                     "pedido e marca com [x].\n\n")
_trava_arquivos = threading.Lock()


# ---------------------------------------------------------------- utilidades

def ler_json(p, padrao=None):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return padrao


def ler_texto(p, limite=400_000):
    try:
        texto = Path(p).read_text(encoding="utf-8")[:limite]
    except OSError:
        return ""
    # Guia .md: sem o comentário de autoria do topo, para o título continuar na primeira linha.
    return md.sem_autoria(texto) if str(p).lower().endswith(".md") else texto


def importar(nome):
    """Módulo do kit importado na hora; None se não existir ou não carregar (inclusive licença inativa)."""
    try:
        return importlib.import_module(nome)
    except BaseException:  # noqa: BLE001  (config.py chama licenca.exigir, que sai com SystemExit)
        return None


def prefs():
    return importar("prefs")


def _cfg_pastas():
    """Pastas e fontes do kit, como o config.py resolve (config.json por cima do exemplo), sem importar config."""
    pastas, fontes = {}, {}
    for arq in (KIT / "config.exemplo.json", Path(os.environ.get("MAQUINA_CONFIG") or KIT / "config.json")):
        dados = ler_json(arq, {}) or {}
        base = arq.resolve().parent
        for nome, valor in (dados.get("pastas") or {}).items():
            if isinstance(valor, str) and valor:
                p = Path(os.path.expandvars(valor)).expanduser()
                pastas[nome] = p if p.is_absolute() else (base / p).resolve()
        fontes.update({k: v for k, v in (dados.get("fontes") or {}).items() if isinstance(v, str)})
    return pastas, fontes


def pasta(nome):
    pastas, _ = _cfg_pastas()
    return pastas.get(nome) or (KIT / nome)


def trabalho():
    return pasta("trabalho")


def chave_midia(p):
    """Caminho que o navegador usa para pedir um arquivo: relativo ao estúdio (ou à pasta de trabalho, se ela
    estiver fora dele)."""
    p = Path(p).resolve()
    for prefixo, raiz in (("", ESTUDIO.resolve()), ("~t/", trabalho().resolve())):
        try:
            return prefixo + p.relative_to(raiz).as_posix()
        except ValueError:
            continue
    return None


def resolver_midia(chave):
    """Arquivo de mídia pedido pelo navegador, só dentro do estúdio (ou da pasta de trabalho) e só de mídia."""
    chave = str(chave or "").replace("\\", "/")
    if not chave or "\x00" in chave:
        return None
    raiz = ESTUDIO
    if chave.startswith("~t/"):
        raiz, chave = trabalho(), chave[3:]
    partes = [x for x in chave.split("/") if x]
    if not partes or any(x in (".", "..") or x.startswith(".") for x in partes):
        return None
    raiz = raiz.resolve()
    alvo = raiz.joinpath(*partes).resolve()
    try:
        alvo.relative_to(raiz)
    except ValueError:
        return None
    if alvo.suffix.lower() not in EXT_MIDIA or not alvo.is_file():
        return None
    return alvo


EXT_TEXTO_CHAT = {".md", ".txt", ".json", ".srt", ".csv"}


def _resolver_em(chave, exts):
    """Como o resolver_midia, para outras extensões: só dentro do estúdio ou da pasta de trabalho."""
    chave = str(chave or "").replace("\\", "/")
    if not chave or "\x00" in chave:
        return None
    raiz = ESTUDIO
    if chave.startswith("~t/"):
        raiz, chave = trabalho(), chave[3:]
    partes = [x for x in chave.split("/") if x]
    if not partes or any(x in (".", "..") or x.startswith(".") for x in partes):
        return None
    raiz = raiz.resolve()
    alvo = raiz.joinpath(*partes).resolve()
    try:
        alvo.relative_to(raiz)
    except ValueError:
        return None
    nome = alvo.as_posix().lower()
    if alvo.suffix.lower() not in exts or not alvo.is_file() or "segredo" in nome or "licenca" in nome:
        return None
    return alvo


EXT_EPISODIO = set(EXT_MIDIA) | {".md", ".txt", ".srt"}


def _sem_acento(t):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")


def _grupo_arquivo(p):
    ext = p.suffix.lower()
    if ext in (".mp4", ".webm", ".mov"):
        return "video"
    if ext in (".mp3", ".wav"):
        return "falas" if p.parent.name.lower() in ("falas", "teste", "tomadas") else "audio"
    if ext in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
        return "imagem"
    return "texto"


def episodios_em_producao(limite=8):
    """Episódios em produção (series/<serie>/epN na raiz e em kit/series, mais as pastas de trabalho da série),
    do mais recente para o mais antigo, com os arquivos que a pessoa pode abrir no painel."""
    grupos = {}
    for raiz in (ESTUDIO / "series", KIT / "series"):
        if not raiz.is_dir():
            continue
        for serie in raiz.iterdir():
            if not serie.is_dir() or serie.name.startswith((".", "_")):
                continue
            for ep in serie.iterdir():
                if ep.is_dir() and re.match(r"^(ep|parte|p)\d+", ep.name, re.I):
                    grupos.setdefault((serie.name, ep.name), []).append(ep)
    trab = trabalho()
    saida = []
    for (serie, ep), pastas in grupos.items():
        n = re.sub(r"\D", "", ep)
        nomes = {serie.lower(), serie.lower().replace("-", "_")}
        for pasta in pastas:
            try:
                titulo = json.loads((pasta / "episodio.json").read_text(encoding="utf-8")).get("serie") or ""
            except (OSError, ValueError, AttributeError):
                titulo = ""
            if titulo:
                nomes.add(re.sub(r"[^a-z0-9]+", "_", _sem_acento(titulo).lower()).strip("_"))
        if trab.is_dir():
            pastas = pastas + [d for d in trab.iterdir() if d.is_dir() and d.name != "entregas"
                               and any(d.name.lower().startswith(x) for x in nomes if x)
                               and (not n or re.search(rf"(p|ep|parte)_?{n}(\b|_)", d.name.lower()))]
        vistos, arquivos = set(), []
        for pasta in pastas:
            for p in pasta.rglob("*"):
                if len(arquivos) >= 120:
                    break
                try:
                    if not p.is_file() or p.suffix.lower() not in EXT_EPISODIO:
                        continue
                    chave = chave_midia(p)
                    nome = p.as_posix().lower()
                    rel_partes = p.relative_to(pasta).parts
                    if (not chave or chave in vistos or any(x.startswith(".") for x in rel_partes)
                            or any(x.lower() in ("quadros", "qa", "cache", "tmp") for x in rel_partes[:-1])
                            or "segredo" in nome or "licenca" in nome):
                        continue
                    st = p.stat()
                except OSError:
                    continue
                vistos.add(chave)
                arquivos.append({"c": chave, "nome": p.name, "grupo": _grupo_arquivo(p), "kb": round(st.st_size / 1024),
                                 "mtime": int(st.st_mtime)})
        if not arquivos:
            continue
        arquivos.sort(key=lambda a: -a["mtime"])
        saida.append({"id": f"{serie}/{ep}", "serie": serie, "ep": ep, "mtime": arquivos[0]["mtime"],
                      "arquivos": arquivos})
    saida.sort(key=lambda e: -e["mtime"])
    return {"episodios": saida[:limite]}


def arquivo_para_chat(chave):
    """Arquivo que a IA gravou, para abrir no chat: mídia vai pelo /midia; texto volta aqui (até 200 mil letras).
    Só dentro do estúdio, sem pasta oculta, licença ou segredo."""
    chave = str(chave or "").replace("\\", "/")
    m = resolver_midia(chave)
    if m:
        return {"ok": True, "tipo": "midia", "mime": EXT_MIDIA[m.suffix.lower()], "nome": m.name}
    alvo = _resolver_em(chave, EXT_TEXTO_CHAT)
    if not alvo:
        return {"ok": False, "msg": "Arquivo não encontrado."}
    try:
        texto = alvo.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {"ok": False, "msg": "Não consegui ler esse arquivo."}
    return {"ok": True, "tipo": "texto", "nome": alvo.name, "texto": texto[:200000]}


def versao_kit():
    return ler_texto(ESTUDIO / "VERSAO", 40).strip()


# ---------------------------------------------------------------- canal e preferências

def status_canal_md():
    texto = ler_texto(CANAL / "canal.md", 4000)
    m = re.search(r"^status:\s*(.*)$", texto, re.M)
    return (m.group(1).strip() if m else "") or "nao-configurado"


def sincronizar_caminho(valor):
    """Mantém o `caminho:` do canal/canal.md igual ao das preferências (a IA lê os dois)."""
    arq = CANAL / "canal.md"
    texto = ler_texto(arq)
    if not texto.startswith("---"):
        return
    fim = texto.find("\n---", 3)
    if fim < 0:
        return
    topo = texto[:fim]
    if not re.search(r"^caminho:.*$", topo, re.M):
        return
    novo = re.sub(r"^caminho:.*$", f"caminho: {valor}", topo, count=1, flags=re.M)
    if novo != topo:
        with _trava_arquivos:
            arq.write_text(novo + texto[fim:], encoding="utf-8")


def prefs_payload():
    p = prefs()
    if not p:
        return {"erro": "As preferências do kit não carregaram (kit/prefs). Peça pra IA: confere o kit/prefs."}
    valores = p.carregar()
    return {
        "esquema": p.esquema(), "valores": valores, "recomendados": p.recomendados(),
        "faltando": [list(x) for x in p.faltando()], "avisos": p.avisos(valores), "rotulos": ROTULOS_OPCOES,
    }


def canal_resumo(valores):
    c = valores.get("canal", {})
    logo = c.get("logo") or ""
    mascote = c.get("mascote") or ""
    return {
        "nome": c.get("nome") or "", "arroba": c.get("arroba") or "", "caminho": c.get("caminho") or "",
        "logo": chave_midia(ESTUDIO / logo) if logo and (ESTUDIO / logo).is_file() else None,
        "mascote": chave_midia(ESTUDIO / mascote) if mascote and (ESTUDIO / mascote).is_file() else None,
        "status_md": status_canal_md(),
    }


# ---------------------------------------------------------------- pronúncia

def _padrao_para_termo(padrao):
    """Termo escrito de um padrão `\\btermo\\b`; None se o padrão for uma expressão regular de verdade."""
    m = re.match(r"^\\b(.+)\\b$", padrao or "")
    if not m or re.search(r"(?<!\\)[()\[\]{}?*+|^$.]", m.group(1)):
        return None
    return re.sub(r"\\(.)", r"\1", m.group(1))


def pronuncia():
    canal = ler_json(CANAL / "pronuncia.json", {}) or {}
    base = ler_json(KIT / "voz" / "pronuncia.json", {}) or {}
    trocas = []
    for par in canal.get("trocas", []):
        if isinstance(par, (list, tuple)) and len(par) == 2:
            termo = _padrao_para_termo(str(par[0]))
            trocas.append({"termo": termo if termo is not None else str(par[0]), "grafia": str(par[1]),
                           "padrao": str(par[0])})
    base_lista = []
    for par in base.get("trocas", []):
        if isinstance(par, (list, tuple)) and len(par) == 2:
            t = _padrao_para_termo(str(par[0]))
            base_lista.append([t if t is not None else str(par[0]), str(par[1])])
    return {"trocas": trocas, "fora_da_fala": [str(x) for x in canal.get("fora_da_fala", [])],
            "base": base_lista, "base_fora": [str(x) for x in base.get("fora_da_fala", [])]}


def salvar_pronuncia(dados):
    """Valida e grava canal/pronuncia.json. (ok, erros)."""
    erros, trocas, vistos = [], [], set()
    itens = (dados or {}).get("trocas") or []
    fora = (dados or {}).get("fora_da_fala") or []
    if not isinstance(itens, list) or not isinstance(fora, list):
        return False, ["Formato inválido."]
    if len(itens) > 300 or len(fora) > 300:
        return False, ["No máximo 300 linhas em cada lista."]
    for i, it in enumerate(itens, 1):
        if not isinstance(it, dict):
            erros.append(f"Linha {i}: formato inválido.")
            continue
        termo = str(it.get("termo") or "").strip()
        grafia = str(it.get("grafia") or "").strip()
        padrao = str(it.get("padrao") or "")
        if not termo and not grafia:
            continue
        if not termo or not grafia:
            erros.append(f"Linha {i}: preencha o termo e o jeito de falar.")
            continue
        if len(termo) > 60 or len(grafia) > 80 or "\n" in termo + grafia:
            erros.append(f"Linha {i}: termo até 60 letras e jeito de falar até 80, numa linha só.")
            continue
        if termo.lower() == grafia.lower():
            erros.append(f"Linha {i}: o jeito de falar é igual ao termo; mude a grafia ou apague a linha.")
            continue
        if termo.lower() in vistos:
            erros.append(f"Linha {i}: '{termo}' já está na lista.")
            continue
        vistos.add(termo.lower())
        if padrao and _padrao_para_termo(padrao) is None and padrao == termo:
            regra = padrao  # padrão escrito pela IA (expressão regular): fica como está
        else:
            regra = rf"\b{re.escape(termo)}\b"
        trocas.append([regra, grafia])
    fora_ok = []
    for i, t in enumerate(fora, 1):
        t = str(t or "").strip()
        if not t:
            continue
        if len(t) > 60 or "\n" in t:
            erros.append(f"Fora da fala, linha {i}: até 60 letras.")
            continue
        if t.lower() not in (x.lower() for x in fora_ok):
            fora_ok.append(t)
    if erros:
        return False, erros
    CANAL.mkdir(parents=True, exist_ok=True)
    arq = CANAL / "pronuncia.json"
    dados_novos = {"_sobre": "Pronúncia do canal (editada pelo painel ou pela IA). Vale antes da base do kit. "
                             "Só muda o texto enviado à voz; a legenda e a tela usam a grafia normal.",
                   "trocas": trocas, "fora_da_fala": fora_ok}
    with _trava_arquivos:
        tmp = arq.with_suffix(".tmp")
        tmp.write_text(json.dumps(dados_novos, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        tmp.replace(arq)
    return True, []


# ---------------------------------------------------------------- vídeos e pedidos

def _primeiro(pasta_, padroes):
    for padrao in padroes:
        achados = sorted(pasta_.glob(padrao))
        if achados:
            return achados[0]
    return None


def _rede_da_pasta(nome):
    sem_num = re.sub(r"^\d{2}_", "", nome).upper()
    return REDE_DA_PASTA.get(sem_num, sem_num.lower())


def _e_pasta_rede(nome):
    """Pasta de uma rede: com número ("01_INSTAGRAM") ou só o nome de uma rede conhecida ("IG", do Explicativo 3D)."""
    return bool(re.match(r"^\d{2}_", nome)) or nome.upper() in REDE_DA_PASTA


def _pacote_rede(sub):
    video = _primeiro(sub, ["*.mp4", "*.mov", "*.webm"])
    capa = _primeiro(sub, ["*_capa.jpg", "*capa*.png", "*.jpg", "*.png"])
    txt = _primeiro(sub, ["*titulo_descricao.txt", "*legenda.txt", "*.txt"])
    md_arq = _primeiro(sub, ["*titulo_descricao.md", "*legenda.md", "*.md"])
    texto_md = ler_texto(md_arq) if md_arq else ""
    titulo = md.secao(texto_md, "Título").strip() if texto_md else ""
    fixado = ""
    m = re.search(r"Comentário para fixar:\s*\"(.+)\"", texto_md)
    if m:
        fixado = m.group(1).strip()
    ao_publicar = md.secao(texto_md, "Ao publicar") if texto_md else ""
    return {
        "pasta": sub.name, "rede": _rede_da_pasta(sub.name), "caminho": chave_midia(sub),
        "video": chave_midia(video) if video else None, "capa": chave_midia(capa) if capa else None,
        "legenda": ler_texto(txt, 20_000).strip() if txt else "", "titulo": titulo, "fixado": fixado,
        "ao_publicar_html": md.para_html(ao_publicar) if ao_publicar else "",
    }


def _pasta_trabalho(nome_entrega):
    t = trabalho()
    for candidato in (nome_entrega, re.sub(r"^\d{2}_", "", nome_entrega)):
        p = t / candidato
        if p.is_dir() and p.name != "entregas":
            return p
    return None


def _extras_trabalho(p):
    if not p:
        return {}
    folha = p / "folha.jpg"
    capa = p / "capa.jpg"
    video = _primeiro(p, [f"{p.name}.mp4", "*.mp4"])
    return {"folha": chave_midia(folha) if folha.is_file() else None,
            "capa_base": chave_midia(capa) if capa.is_file() else None,
            "video_base": chave_midia(video) if video else None}


def episodios(limite=40):
    t = trabalho()
    entregas = t / "entregas"
    lista, usados = [], set()
    if entregas.is_dir():
        pastas = sorted((d for d in entregas.iterdir() if d.is_dir() and not d.name.startswith(".")),
                        key=lambda d: d.stat().st_mtime, reverse=True)
        for d in pastas[:limite]:
            redes = [_pacote_rede(s) for s in sorted(d.iterdir()) if s.is_dir() and _e_pasta_rede(s.name)]
            pt = _pasta_trabalho(d.name)
            if pt:
                usados.add(pt.name)
            extras = _extras_trabalho(pt)
            if not extras.get("video_base"):
                # Vídeo solto na pasta da entrega (sem pasta por rede): também aparece e baixa
                solto = _primeiro(d, ["*.mp4", "*.mov", "*.webm"])
                if solto:
                    extras["video_base"] = chave_midia(solto)
            lista.append({"nome": d.name, "pronto": True, "quando": _quando(d), "caminho": chave_midia(d),
                          "redes": redes, **extras})
    producao = []
    if t.is_dir():
        for d in sorted((d for d in t.iterdir() if d.is_dir() and d.name not in ("entregas",) and
                         not d.name.startswith(".") and d.name not in usados),
                        key=lambda d: d.stat().st_mtime, reverse=True)[:limite]:
            extras = _extras_trabalho(d)
            # Pasta de trabalho que já tem as pastas das redes (o Explicativo 3D grava IG/, TIKTOK/, YOUTUBE/)
            redes = [r for r in (_pacote_rede(s) for s in sorted(d.iterdir()) if s.is_dir() and _e_pasta_rede(s.name))
                     if r["video"]]
            if extras.get("folha") or extras.get("video_base") or redes:
                producao.append({"nome": d.name, "pronto": bool(redes), "quando": _quando(d), "caminho": chave_midia(d),
                                 "redes": redes, **extras})
    return lista + producao


def _quando(p):
    try:
        return datetime.fromtimestamp(p.stat().st_mtime).strftime("%d/%m/%Y %H:%M")
    except OSError:
        return ""


def ideias(limite=3):
    """Ideias de vídeo da pauta do canal (canal/pauta.md): as marcadas com ★ primeiro, sem as já feitas."""
    lista = []
    for linha in ler_texto(CANAL / "pauta.md").splitlines():
        cel = [c.strip() for c in linha.strip().strip("|").split("|")]
        if len(cel) < 3 or not linha.strip().startswith("|") or set(cel[0]) <= set("-: ") and set(cel[1]) <= set("-: "):
            continue
        estrela, formato, ideia = cel[0], cel[1], cel[2]
        status = (cel[4] if len(cel) > 4 else "").lower()
        if not ideia or ideia.lower().startswith("ideia (") or re.search(r"feito|postado|publicado", status):
            continue
        lista.append({"ideia": _texto_simples(ideia, 160), "formato": _texto_simples(formato, 40), "estrela": "★" in estrela})
    lista.sort(key=lambda x: not x["estrela"])
    return lista[:limite]


def pedidos():
    itens = []
    for linha in ler_texto(CANAL / "pedidos.md").splitlines():
        m = re.match(r"^- \[( |x|X)\] (.*)$", linha.strip())
        if m:
            ep = re.search(r"episódio `([^`]+)`", m.group(2))
            itens.append({"feito": m.group(1).lower() == "x", "texto": m.group(2), "episodio": ep.group(1) if ep else ""})
    return itens


def adicionar_pedido(episodio, cena, texto):
    """Acrescenta um pedido em canal/pedidos.md. (ok, mensagem)."""
    episodio = str(episodio or "").strip()
    texto = " ".join(str(texto or "").split())
    if not re.match(r"^[\w.\-]{1,100}$", episodio):
        return False, "Escolha o episódio."
    if not texto:
        return False, "Escreva o que você quer mudar."
    if len(texto) > 600:
        return False, "Escreva em até 600 letras."
    try:
        cena = int(cena) if str(cena).strip() else 0
    except ValueError:
        return False, "A cena é um número (o da folha de cenas)."
    if cena < 0 or cena > 400:
        return False, "Use o número da cena que aparece na folha."
    texto = texto.replace("`", "'")
    onde = f"cena {cena}" if cena else "vídeo inteiro"
    linha = f"- [ ] {datetime.now().strftime('%d/%m/%Y %H:%M')} · episódio `{episodio}` · {onde} · {texto}\n"
    arq = CANAL / "pedidos.md"
    with _trava_arquivos:
        CANAL.mkdir(parents=True, exist_ok=True)
        atual = ler_texto(arq) or PEDIDOS_CABECALHO
        if not atual.endswith("\n"):
            atual += "\n"
        arq.write_text(atual + linha, encoding="utf-8")
    return True, "Pedido anotado. A IA lê antes do próximo episódio; peça no chat: \"faz os pedidos do painel\"."


# ---------------------------------------------------------------- estilos, personagens, ganchos, ajuda

def _segundos(txt):
    txt = txt.strip()
    if ":" in txt:
        m, s = txt.split(":", 1)
        return int(m) * 60 + int(s)
    return int(txt)


def _faixa(texto):
    m = re.search(r"(\d+(?::\d{2})?)\s*a\s*(\d+(?::\d{2})?)", texto or "")
    return [_segundos(m.group(1)), _segundos(m.group(2))] if m else None


def _texto_simples(md_txt, limite=260):
    t = re.sub(r"[*_`>#|]", "", md_txt or "")
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    t = " ".join(t.split())
    return t if len(t) <= limite else t[:limite].rsplit(" ", 1)[0] + "…"


def estilos():
    readme = ler_texto(ESTUDIO / "metodo" / "estilos" / "README.md")
    lista = []
    for linha in readme.splitlines():
        cel = [c.strip() for c in linha.strip().strip("|").split("|")]
        if len(cel) < 6 or "metodo/estilos/" not in cel[1]:
            continue
        m = re.search(r"metodo/estilos/([\w\-]+)\.md", cel[1])
        if not m:
            continue
        ident = m.group(1)
        ficha = ler_texto(ESTUDIO / "metodo" / "estilos" / f"{ident}.md")
        lista.append({
            "id": ident, "nome": cel[0], "duracao": cel[2], "faixa_s": _faixa(cel[2]),
            "exemplo": {"video": bool(resolver_exemplo(ident, "video")), "capa": bool(resolver_exemplo(ident, "capa"))},
            "motor": _texto_simples(cel[3], 80), "dificuldade": cel[4], "gratis": _texto_simples(cel[5], 120),
            "resumo": _texto_simples(md.secao(ficha, "O que é")),
            "estrutura_html": md.para_html(md.secao(ficha, "Estrutura do roteiro")),
            "ficha_html": md.para_html(re.sub(r"^#\s+.*\n", "", ficha, count=1)),
        })
    return {"lista": lista, "como_escolher_html": md.para_html(md.secao(readme, "Como escolher")),
            "comum_html": md.para_html(md.secao(readme, "O que todo estilo tem em comum"))}


def _boneco(d):
    partes = ler_json(d / "partes.json", {}) or {}
    p = partes.get("partes") or {}
    ordem = [r[0] for r in partes.get("rig", []) if isinstance(r, list) and r]
    camadas = []
    for nome in ordem:
        if nome.startswith("palpebra"):
            continue  # pálpebra fechada só aparece no piscar
        if nome == "boca":
            nome = "boca_feliz" if "boca_feliz" in p else ("boca_M" if "boca_M" in p else nome)
        info, arq = p.get(nome), d / "partes" / f"{nome}.png"
        if info and arq.is_file():
            camadas.append({"src": chave_midia(arq), "x": info["x"], "y": info["y"], "w": info["w"], "h": info["h"]})
    if not camadas:
        return None
    x0 = min(c["x"] for c in camadas)
    y0 = min(c["y"] for c in camadas)
    x1 = max(c["x"] + c["w"] for c in camadas)
    y1 = max(c["y"] + c["h"] for c in camadas)
    return {"camadas": camadas, "caixa": [x0, y0, x1 - x0, y1 - y0]}


# Personagens que saíram do kit: não aparecem no painel mesmo que a pasta antiga continue numa instalação velha.
PERSONAGENS_RETIRADOS = {"ana", "beto"}


def personagens():
    raiz = pasta("personagens")
    lista = []
    if raiz.is_dir():
        for d in sorted(x for x in raiz.iterdir() if x.is_dir() and not x.name.startswith(".")
                        and x.name.lower() not in PERSONAGENS_RETIRADOS):
            info = ler_json(d / "personagem.json", {}) or {}
            previa = _primeiro(d, ["previa.png", "previa.jpg", "folha.jpg", "folha.png", "*.png", "*.jpg"])
            lista.append({"nome": d.name, "descricao": str(info.get("descricao") or ""),
                          "pronto": (d / "partes.json").is_file(),
                          "previa": chave_midia(previa) if previa else None,
                          "boneco": None if previa else _boneco(d)})
    cenarios = []
    for arq in ("cenario3d.py", "interiores.py", "paisagens.py"):
        p = KIT / "estilo_desenhado" / arq
        try:
            doc = ast.get_docstring(ast.parse(ler_texto(p))) or ""
        except SyntaxError:
            doc = ""
        if doc:
            cenarios.append({"arquivo": f"kit/estilo_desenhado/{arq}", "texto": doc.split("\n\n")[0].replace("\n", " ")})
    exemplos = [{"pasta": f"kit/{rel}", "texto": texto} for rel, texto in (
        ("cartelas/exemplo", "Top 5 com teste no fim, no motor de cartelas (o mais rápido para ver funcionando)."),
        ("exemplo", "Episódio de série 2D com voto, com o elenco de exemplo do kit."),
        ("estilo_desenhado/exemplo", "Demonstração do estilo desenhado (recorte de papel colorido, cenários em camadas)."),
        ("explicativo3d/exemplo", "Explicativo 3D no Blender, com o objeto em corte."),
    ) if (KIT / rel).is_dir()]
    identidade = md.secao(ler_texto(CANAL / "identidade.md"), "Personagem principal")
    return {"lista": lista, "cenarios": cenarios, "exemplos": exemplos,
            "identidade_html": md.para_html(identidade) if identidade else ""}


def ganchos():
    biblioteca = ler_json(KIT / "prefs" / "ganchos.json", None)
    if isinstance(biblioteca, dict):
        biblioteca = {k: v for k, v in biblioteca.items() if not k.startswith("_") and isinstance(v, list)}
    extras = []
    p = prefs()
    if p:
        extras = p.carregar().get("ganchos", {}).get("biblioteca_extra") or []
    conferidor = importlib.util.find_spec("qa.gancho") is not None if (KIT / "qa").is_dir() else False
    eng = ler_texto(ESTUDIO / "metodo" / "engajamento.md")
    gan = ler_texto(ESTUDIO / "metodo" / "ganchos.md")
    return {"biblioteca": biblioteca, "meus": extras, "conferidor": conferidor,
            "engajamento_html": md.para_html(eng) if eng else "", "ganchos_html": md.para_html(gan) if gan else ""}


def avaliar_gancho(fala, tela, dur_s, inicio_fala_s=0.0):
    g = importar("qa.gancho")
    if not g or not hasattr(g, "avaliar"):
        return None
    estimado = False
    if dur_s in (None, ""):
        if hasattr(g, "estimar_s"):
            dur_s, estimado = g.estimar_s(fala), True
        else:
            dur_s = None
    erros, avisos = g.avaliar(fala, tela, None if dur_s is None else float(dur_s), float(inicio_fala_s or 0))
    return {"erros": list(erros), "avisos": list(avisos), "dur_s": dur_s, "estimado": estimado}


def ajuda():
    e = importar("erros")
    conhecidos = [{"explica": x[1], "fazer": x[2]} for x in getattr(e, "CONHECIDOS", [])] if e else []
    return {"erros": conhecidos}


# ---------------------------------------------------------------- vídeo-exemplo de cada estilo

EXEMPLOS_ESTILOS = ESTUDIO / "exemplos" / "estilos"
ARQ_EXEMPLO = {"video": "exemplo.mp4", "capa": "capa.jpg"}


def resolver_exemplo(ident, tipo):
    """exemplos/estilos/<id>/exemplo.mp4 ou capa.jpg; None se o id não for de uma ficha ou o arquivo faltar.
    O nome do arquivo é fixo e o id passa por uma lista fechada: nada fora de exemplos/estilos/ sai daqui."""
    ident = str(ident or "")
    if tipo not in ARQ_EXEMPLO or not re.fullmatch(r"[a-z0-9][a-z0-9\-]{0,40}", ident):
        return None
    if not (ESTUDIO / "metodo" / "estilos" / f"{ident}.md").is_file():
        return None
    raiz = EXEMPLOS_ESTILOS.resolve()
    alvo = (raiz / ident / ARQ_EXEMPLO[tipo]).resolve()
    try:
        alvo.relative_to(raiz)
    except ValueError:
        return None
    return alvo if alvo.is_file() and alvo.stat().st_size > 0 else None


# ---------------------------------------------------------------- tutoriais (área Aprender)

# Lista fechada: o navegador só pede pelo id, e o arquivo é o primeiro que existir entre os candidatos. Os guias do
# próprio painel ficam em kit/painel/guias/.
TUTORIAIS = [
    ("comece", "Comece aqui", "Começar", ["LEIA-ME.md"],
     "O que é o estúdio, os 3 passos e como abrir a IA."),
    ("primeiro-video", "Seu primeiro vídeo", "Começar", ["comandos/modo-rapido.md"],
     "Um vídeo do zero, no caminho mais rápido."),
    ("preparar", "Preparar o computador", "Começar", ["kit/INSTALAR.md"],
     "Python, ffmpeg e o que o kit precisa para gravar."),
    ("celular", "Só no celular", "Começar", ["celular/COMECE-AQUI.md"],
     "O caminho pela nuvem, para quem não tem computador."),
    ("novidades", "O que há de novo", "Começar", ["NOVIDADES.md"],
     "O que mudou nesta versão do kit."),
    ("caminhos", "Grátis ou recomendado", "Caminho, voz e chaves", ["metodo/caminhos.md"],
     "Os dois caminhos, do começo ao fim, e o que cada um custa."),
    ("chaves", "Chave da voz, passo a passo", "Caminho, voz e chaves", ["kit/painel/guias/chaves.md"],
     "Como pegar a chave grátis do Google ou a da ElevenLabs e colar no painel."),
    ("voz", "A voz por dentro", "Caminho, voz e chaves", ["metodo/voz.md"],
     "Opções de voz, direção e as regras de gravação."),
    ("estilos", "Os 13 estilos", "Estilos", ["metodo/estilos/README.md"],
     "Como escolher o estilo e o que todo estilo tem."),
    ("roteiro", "Roteiro", "Roteiro e engajamento", ["metodo/formula-roteiro.md"],
     "Como o roteiro é montado, batida por batida."),
    ("ganchos", "Ganchos: o primeiro segundo", "Roteiro e engajamento", ["metodo/ganchos.md"],
     "Como prender nos 3 primeiros segundos, com casos reais."),
    ("estudar", "Estudar vídeos de referência", "Roteiro e engajamento", ["metodo/estudar-referencias.md"],
     "Transcrever, tirar o raio-x e usar a fórmula de um vídeo que deu certo."),
    ("engajamento", "Engajamento e voto", "Roteiro e engajamento", ["metodo/engajamento.md"],
     "Voto, comentário, horário de postar e o que medir."),
    ("publicar", "Publicar nas redes", "Publicar e medir", ["comandos/publicar.md"],
     "O pacote de cada rede: vídeo, capa e legenda."),
    ("plataformas", "Montar os perfis", "Publicar e medir", ["metodo/plataformas.md"],
     "Nome, @ e foto iguais nas três redes, e como operar cada uma."),
    ("metricas", "Métricas", "Publicar e medir", ["metodo/metricas.md"],
     "Quais números olhar, quando, e o que mudar no próximo."),
    ("seguranca", "Segurança da conta", "Publicar e medir", ["metodo/seguranca.md"],
     "O que derruba conta, rótulo de IA, direitos e público."),
    ("ajuda", "Travou ou deu erro", "Ajuda", ["comandos/ajuda.md"],
     "Como pedir ajuda pra IA e as dúvidas mais comuns."),
]


def _arquivo_do_kit(rel):
    """Arquivo .md de dentro da pasta do estúdio; None se sair dela (link, '..') ou não existir."""
    raiz = ESTUDIO.resolve()
    alvo = (ESTUDIO / rel).resolve()
    try:
        alvo.relative_to(raiz)
    except ValueError:
        return None
    return alvo if alvo.suffix.lower() == ".md" and alvo.is_file() else None


def _titulo_md(texto, padrao):
    m = re.search(r"^#\s+(.+?)\s*$", texto or "", re.M)
    return m.group(1).strip() if m else padrao


def tutoriais():
    """Guias do kit em HTML seguro (md.para_html escapa tudo), na ordem da área Aprender."""
    lista = []

    def junta(ident, titulo, grupo, rel, resumo):
        arq = _arquivo_do_kit(rel)
        if not arq:
            return
        texto = ler_texto(arq)
        corpo = re.sub(r"^#\s+.*\n", "", texto, count=1)
        lista.append({"id": ident, "titulo": titulo, "grupo": grupo, "resumo": resumo,
                      "arquivo": arq.relative_to(ESTUDIO.resolve()).as_posix(),
                      "html": md.para_html(corpo), "texto": _texto_simples(corpo, 60_000)})

    for ident, titulo, grupo, candidatos, resumo in TUTORIAIS:
        for rel in candidatos:
            if _arquivo_do_kit(rel):
                junta(ident, titulo, grupo, rel, resumo)
                break
        if ident == "estilos":
            for est in estilos()["lista"]:
                junta(f"estilo-{est['id']}", est["nome"], "Estilos", f"metodo/estilos/{est['id']}.md",
                      est.get("resumo") or "")
    return {"lista": lista}


def videos_feitos():
    """Vídeos entregues (uma pasta por vídeo em trabalho/entregas), sem limite."""
    ent = trabalho() / "entregas"
    try:
        return sum(1 for d in ent.iterdir() if d.is_dir() and not d.name.startswith("."))
    except OSError:
        return 0


def video_ia():
    """Modelos, preços de tabela e gastos da IA de vídeo (kit/video_ia.py). Nunca a chave."""
    mod = importar("video_ia")
    return mod.estado_painel() if mod else None


def conquistas():
    c = importar("conquistas")
    if not c or not hasattr(c, "atualizar"):
        return {"disponivel": False, "lista": [], "novas": []}
    hist = metricas_historico().get("historico") or []
    return {"disponivel": True, **c.atualizar(videos_feitos(), hist)}


def metricas_historico():
    m = importar("metricas")
    if m and hasattr(m, "historico"):
        try:
            return {"disponivel": True, "historico": m.historico()}
        except Exception:  # noqa: BLE001
            return {"disponivel": True, "historico": []}
    return {"disponivel": False, "historico": ler_json(CANAL / "metricas.json", []) or []}


# ---------------------------------------------------------------- chaves (só presença)

_chaves_cache = {"quando": 0.0, "valor": {}}
_trava_cfg = threading.Lock()
NOMES_CHAVE = {"elevenlabs": "ElevenLabs", "GEMINI_API_KEY": "Google AI Studio (Gemini)",
               "OPENAI_API_KEY": "OpenAI", "FAL_KEY": "fal.ai", "HIGGSFIELD_API_KEY": "Higgsfield"}


def chaves(forcar=False):
    """{nome: True/False}: se cada chave existe (variável de ambiente ou arquivo de segredos). Nunca o valor."""
    with _trava_cfg:
        if not forcar and time.time() - _chaves_cache["quando"] < 15:
            return dict(_chaves_cache["valor"])
        resultado = {n: False for n in NOMES_CHAVE}
        try:
            import config  # noqa: PLC0415
            config = importlib.reload(config)
            for n in NOMES_CHAVE:
                try:
                    resultado[n] = bool(config.segredo(n, obrigatorio=False))
                except Exception:  # noqa: BLE001
                    resultado[n] = False
        except BaseException:  # noqa: BLE001
            pass
        _chaves_cache.update(quando=time.time(), valor=resultado)
        return dict(resultado)


# ---------------------------------------------------------------- status da máquina

PASTA_FFMPEG = Path.home() / ".temporada-viral" / "ffmpeg"


def ffmpeg_no_path():
    """Põe no PATH deste processo (e dos que ele abre: verificação, chat da IA) o ffmpeg que o painel instalou com
    `instalar_recursos.py ffmpeg`. Alguns scripts do kit chamam "ffmpeg" pelo nome, sem passar pelo config.json."""
    caminhos = os.environ.get("PATH", "").split(os.pathsep)
    if PASTA_FFMPEG.is_dir() and str(PASTA_FFMPEG) not in caminhos:
        os.environ["PATH"] = os.pathsep.join([str(PASTA_FFMPEG), *caminhos])


class Verificacao:
    """Roda o verificar.py do kit num processo à parte (leva uns segundos) e guarda o resultado."""

    def __init__(self):
        self.trava = threading.Lock()
        self.linhas = {}
        self.rodando = False
        self.quando = None
        self.final = ""
        self.erro = ""

    def rodar(self, esperar=False):
        with self.trava:
            if not self.rodando:
                self.rodando = True
                threading.Thread(target=self._executar, daemon=True).start()
        if esperar:
            while self.rodando:
                time.sleep(0.2)

    def _executar(self):
        ffmpeg_no_path()
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
        extra = {"creationflags": 0x08000000} if os.name == "nt" else {}  # sem janela de console no Windows
        try:
            r = subprocess.run([sys.executable, str(KIT / "verificar.py")], cwd=str(KIT), capture_output=True,
                               text=True, encoding="utf-8", errors="replace", timeout=240, env=env, **extra)
            saida, self.erro = r.stdout + "\n" + r.stderr, ""
        except Exception as e:  # noqa: BLE001
            saida, self.erro = "", f"não consegui rodar o verificar.py ({type(e).__name__})"
        linhas, final = {}, ""
        for linha in saida.splitlines():
            m = re.match(r"^\[(ok|--|FALTA)\s*\]\s(.*)$", linha.rstrip())
            if m:
                resto = m.group(2)
                if len(resto) > 28 and resto[28] == " " and resto[:28].strip():
                    nome, det = resto[:28].strip(), resto[29:].strip()
                else:
                    nome, _, det = resto.partition(" ")
                estado = {"ok": "ok", "--": "opcional", "FALTA": "falta"}[m.group(1)]
                linhas[nome] = (estado, det)
            elif linha.startswith("VERIFICAR_") or "licença" in linha.lower():
                final = linha.strip()
        placas_de_video(forcar=True)  # aquece o cache aqui, fora do pedido da página
        with self.trava:
            self.linhas, self.final, self.quando, self.rodando = linhas, final, time.time(), False

    def instantaneo(self):
        with self.trava:
            return dict(self.linhas), self.rodando, self.quando, self.final, self.erro


VERIFICACAO = Verificacao()

# ---------------------------------------------------------------- placa de vídeo (sem depender do skia)

_placas = {"quando": 0.0, "lista": None}
_trava_placas = threading.Lock()
# Adaptadores que não desenham nada: telas virtuais (Parsec, emuladores, área de trabalho remota) e o básico do Windows.
_VIRTUAL = re.compile(r"virtual|basic|parsec|mumu|remote|microsoft|vmware|virtualbox|citrix|hyper-v|spacedesk|"
                      r"displaylink|idd|meta|bluestacks|ldplayer|nox", re.I)
# Placa dedicada (a que acelera o vídeo); Intel UHD/Iris e gráficos integrados da AMD ficam de fora.
_DEDICADA = re.compile(r"nvidia|geforce|quadro|\brtx\b|\bgtx\b|radeon\s*(rx|pro|r9|vii)|\barc\s*a\d|apple\s*m\d", re.I)


def _rodar_curto(cmd):
    extra = {"creationflags": 0x08000000} if os.name == "nt" else {}
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15, **extra)
        return r.stdout if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def placas_de_video(forcar=False, so_cache=False):
    """Nomes das placas de vídeo de verdade deste computador, achados pelo sistema (nvidia-smi, WMI no Windows,
    system_profiler no Mac, lspci no Linux), sem depender das bibliotecas do kit. None = ainda não procurou."""
    with _trava_placas:
        if so_cache or (not forcar and _placas["lista"] is not None and time.time() - _placas["quando"] < 600):
            return None if _placas["lista"] is None else list(_placas["lista"])
    nomes = [n.strip() for n in _rodar_curto(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"]).splitlines()
             if n.strip()]
    if os.name == "nt":
        saida = _rodar_curto(["powershell", "-NoProfile", "-NonInteractive", "-Command",
                              "Get-CimInstance Win32_VideoController | ForEach-Object { $_.Name + '|' + $_.PNPDeviceID }"])
        for linha in saida.splitlines():
            nome, _, pnp = linha.strip().partition("|")
            if nome and pnp.upper().startswith("PCI\\") and not _VIRTUAL.search(nome):
                nomes.append(nome.strip())
    elif sys.platform == "darwin":
        nomes += re.findall(r"Chipset Model:\s*(.+)", _rodar_curto(["system_profiler", "SPDisplaysDataType"]))
    else:
        for linha in _rodar_curto(["lspci"]).splitlines():
            if re.search(r"VGA|3D|Display", linha):
                nomes.append(linha.split(":", 2)[-1].strip())
    vistos, lista = set(), []
    for n in nomes:
        if n.lower() not in vistos and not _VIRTUAL.search(n):
            vistos.add(n.lower())
            lista.append(n)
    with _trava_placas:
        _placas.update(quando=time.time(), lista=lista)
    return list(lista)


def placa_dedicada(lista):
    return next((n for n in lista or [] if _DEDICADA.search(n)), "")


def _py():
    """O Python do painel, entre aspas: a IA instala nele, e não num outro Python do computador."""
    return f'"{sys.executable}"'


def _item(ident, titulo, estado, detalhe, pedir="", acao=None, caso="", medida=None):
    """Um item do status. `medida` leva os números para os mostradores do painel (espaço, canal, placa, voz)."""
    return {"id": ident, "titulo": titulo, "estado": estado, "detalhe": detalhe, "pedir": pedir, "acao": acao,
            "caso": caso, "medida": medida}


def checagens(licenca_info=("ativa", "")):
    linhas, rodando, quando, final, erro = VERIFICACAO.instantaneo()
    tem = bool(linhas)
    itens = []
    estado_lic, plano = licenca_info
    plano_txt = {"": "padrão", "padrao": "padrão"}.get(plano or "", plano)
    itens.append(_item("licenca", "Licença", "ok", f"Ativa · plano {plano_txt}"))
    ok_py = sys.version_info >= (3, 10)
    itens.append(_item("python", "Python", "ok" if ok_py else "falta", f"Versão {sys.version.split()[0]}"
                       + ("" if ok_py else ": o kit precisa da 3.10 ou mais nova"),
                       "" if ok_py else "instala o Python novo pra mim"))
    if tem:
        faltam = [n for n in ("skia", "numpy", "scipy", "PIL", "requests") if linhas.get(n, ("falta",))[0] == "falta"]
        itens.append(_item("bibliotecas", "Bibliotecas do kit", "falta" if faltam else "ok",
                           ("Faltam: " + ", ".join(faltam)) if faltam else "Motor de desenho, imagem e internet prontos",
                           f"instala o que falta no kit ({_py()} instalar_recursos.py base, a partir de kit/; use exatamente esse Python, que é o do painel)" if faltam else ""))
        ff = linhas.get("ffmpeg", ("falta", ""))
        itens.append(_item("ffmpeg", "Gravador de vídeo (ffmpeg)", "ok" if ff[0] == "ok" else "falta",
                           "Instalado" if ff[0] == "ok" else "Falta instalar: sem ele o vídeo não é gravado",
                           "" if ff[0] == "ok" else f"instala o ffmpeg pra mim ({_py()} instalar_recursos.py ffmpeg, a partir de kit/)"))
        rend = linhas.get("render")
        enc = linhas.get("encoder de vídeo", ("", ""))
        # A placa é achada pelo sistema; o teste do render (verificar.py) só roda com as peças do kit instaladas.
        placas = placas_de_video(so_cache=True)
        dedicada = placa_dedicada(placas)
        nome_placa = dedicada or (placas[0] if placas else "")
        faltam_pecas = bool(faltam) or ff[0] != "ok"
        titulo_r = "Placa de vídeo e render"
        medida_r = {"placa": nome_placa, "dedicada": bool(dedicada)}
        if rend and rend[0] == "ok" and rend[1].startswith("GPU"):
            placa = re.search(r"OpenGL: ([^/|)]+)", rend[1])
            nome = dedicada or (placa.group(1).strip() if placa else "")
            itens.append(_item("render", titulo_r, "ok",
                               f"Desenha na placa{(' ' + nome) if nome else ''} e grava com {enc[1] or 'o encoder da placa'}",
                               caso="gpu", medida=medida_r))
        elif not rend or (rend[0] == "falta" and faltam_pecas):
            # Depende das peças do programa: não é um problema à parte.
            itens.append(_item("render", titulo_r, "depende",
                               (f"{nome_placa} encontrada. " if nome_placa else "")
                               + "O teste do vídeo roda depois que as peças do programa estiverem instaladas"
                               + ("" if placas is not None else " (procurando a placa…)"), caso="depende", medida=medida_r))
        elif rend[0] == "falta":
            itens.append(_item("render", titulo_r, "falta",
                               (f"{nome_placa}: " if nome_placa else "") + rend[1],
                               "o render não está usando a placa de vídeo, confere pra mim", caso="falha", medida=medida_r))
        elif dedicada:
            itens.append(_item("render", titulo_r, "aviso",
                               f"A placa {dedicada} existe, mas o vídeo está saindo pelo processador ({rend[1]})",
                               "o render não está usando a placa de vídeo, confere pra mim", caso="cpu_com_placa", medida=medida_r))
        else:
            itens.append(_item("render", titulo_r, "aviso",
                               "Sem placa de vídeo dedicada" + (f" (só {nome_placa})" if nome_placa else "")
                               + ": o render vai pelo processador, mais devagar (funciona)",
                               "meu computador é fraco, deixa o render mais leve",
                               {"tipo": "prefs", "rotulo": "Ligar o modo leve", "mudancas": {"render": {"modo_leve": True}}},
                               caso="sem_placa", medida=medida_r))
    else:
        texto = erro or ("Conferindo… leva alguns segundos" if rodando else "Ainda não conferido")
        for ident, titulo in (("bibliotecas", "Bibliotecas do kit"), ("ffmpeg", "Gravador de vídeo (ffmpeg)"),
                              ("render", "Placa de vídeo e render")):
            itens.append(_item(ident, titulo, "falta" if erro else "conferindo", texto,
                               "roda o verificar.py do kit e me conta o que falta" if erro else ""))
    try:
        uso = shutil.disk_usage(str(trabalho() if trabalho().exists() else ESTUDIO))
        livre, total = uso.free / 1024 ** 3, uso.total / 1024 ** 3
        est = "falta" if livre < 5 else ("aviso" if livre < 30 else "ok")
        itens.append(_item("disco", "Espaço no disco", est, f"{livre:.0f} GB livres"
                           + ("" if est == "ok" else " (o render precisa de uns 5 GB; com menos de 30, apague testes antigos)"),
                           "" if est == "ok" else "me ajuda a liberar espaço apagando os testes antigos da pasta trabalho",
                           medida={"livre_gb": round(livre, 1), "total_gb": round(total, 1), "alerta_gb": 30, "minimo_gb": 5}))
    except OSError:
        itens.append(_item("disco", "Espaço no disco", "aviso", "Não deu para medir"))
    _, fontes = _cfg_pastas()
    dir_fontes = pasta("fontes")
    faltam_f = [a for a in fontes.values() if not (dir_fontes / a).is_file()]
    itens.append(_item("fontes", "Fontes das letras", "falta" if faltam_f or not fontes else "ok",
                       ("Faltam: " + ", ".join(faltam_f)) if faltam_f else f"{len(fontes)} fontes no lugar",
                       "baixa as fontes do kit" if faltam_f else ""))
    v = versao_kit()
    itens.append(_item("versao", "Versão do kit", "ok" if v else "aviso", f"Temporada Viral {v}" if v else
                       "Arquivo VERSAO não encontrado", "" if v else "qual a versão do meu kit?"))
    ch = chaves()
    kokoro = importlib.util.find_spec("kokoro") is not None
    p = prefs()
    provedor = p.carregar()["voz"]["provedor"] if p else "gemini"
    prontas = [n for n, ok in (("Google (Gemini)", ch.get("GEMINI_API_KEY")), ("ElevenLabs", ch.get("elevenlabs")),
                               ("Kokoro", kokoro)) if ok]
    precisa = {"gemini": ch.get("GEMINI_API_KEY"), "elevenlabs": ch.get("elevenlabs"), "kokoro": kokoro}.get(provedor)
    medida_v = {"provedor": ROTULOS_OPCOES.get(provedor, provedor), "pronta": bool(precisa), "prontas": prontas}
    if precisa:
        itens.append(_item("voz", "Voz dos vídeos", "ok", "Pronta: " + ", ".join(prontas), medida=medida_v))
    elif prontas:
        itens.append(_item("voz", "Voz dos vídeos", "aviso",
                           f"A voz escolhida, {ROTULOS_OPCOES.get(provedor, provedor)}, ainda não está conectada. "
                           f"Já funciona: {', '.join(prontas)}",
                           "conecta a voz que eu escolhi no painel", {"tipo": "ir", "tela": "potencializar",
                                                                       "rotulo": "Conectar a voz"}, medida=medida_v))
    else:
        itens.append(_item("voz", "Voz dos vídeos", "falta",
                           "Nenhuma voz pronta. A grátis do Google leva 2 minutos (se você usa o conector oficial da "
                           "ElevenLabs no Claude, pode ignorar este item)",
                           "conecta a voz grátis do Google pra mim",
                           {"tipo": "ir", "tela": "potencializar", "rotulo": "Conectar a voz"}, medida=medida_v))
    falta = [x[2] for x in (p.faltando() if p else [])]
    total_canal = len(getattr(p, "OBRIGATORIOS", ())) or 4
    itens.append(_item("canal", "Seu canal", "ok" if not falta else "falta",
                       "Tudo preenchido" if not falta else "Falta: " + ", ".join(falta),
                       "" if not falta else "vamos configurar o meu canal",
                       None if not falta else {"tipo": "ir", "tela": "canal", "rotulo": "Preencher agora"},
                       medida={"feitos": max(0, total_canal - len(falta)), "total": total_canal}))
    # Aviso conta como pronto (dá para fazer o vídeo), menos na voz: a voz escolhida sem chave para no primeiro vídeo
    feitos = sum(1 for i in itens if i["estado"] == "ok" or (i["estado"] == "aviso" and i.get("id") != "voz"))
    return {"itens": itens, "pct": round(100 * feitos / len(itens)), "feitos": feitos, "total": len(itens),
            "rodando": rodando, "quando": datetime.fromtimestamp(quando).strftime("%d/%m %H:%M") if quando else "",
            "final": final}


# ---------------------------------------------------------------- assinatura (para o refresh)

def assinatura():
    """Muda quando algum arquivo que o painel mostra muda (canal, config, entregas, trabalho, personagens,
    vídeos-exemplo dos estilos)."""
    h = hashlib.md5()

    def junta(p):
        try:
            st = p.stat()
            h.update(f"{p}|{st.st_mtime_ns}|{st.st_size};".encode("utf-8", "replace"))
        except OSError:
            pass

    for p in (KIT / "config.json", ESTUDIO / "VERSAO", KIT / "prefs" / "ganchos.json",
              ESTUDIO / "metodo" / "engajamento.md", ESTUDIO / "metodo" / "ganchos.md"):
        junta(p)
    if CANAL.is_dir():
        for p in CANAL.iterdir():
            junta(p)
    t = trabalho()
    if t.is_dir():
        for d in t.iterdir():
            junta(d)
            if d.is_dir():
                for p in (d / "folha.jpg", d / "capa.jpg"):
                    junta(p)
        ent = t / "entregas"
        if ent.is_dir():
            for d in ent.iterdir():
                junta(d)
                if d.is_dir():
                    for s in d.iterdir():
                        junta(s)
    pers = pasta("personagens")
    if pers.is_dir():
        for d in pers.iterdir():
            junta(d)
    if EXEMPLOS_ESTILOS.is_dir():  # vídeo-exemplo novo de um estilo aparece sem recarregar a página
        for d in EXEMPLOS_ESTILOS.iterdir():
            if d.is_dir():
                for nome in ARQ_EXEMPLO.values():
                    junta(d / nome)
    _, _, quando, _, _ = VERIFICACAO.instantaneo()
    h.update(str(quando).encode())
    return h.hexdigest()[:16]
