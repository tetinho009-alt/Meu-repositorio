# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Raio-x de um vídeo a partir da transcrição com tempo: gancho, viradas e buracos, perguntas e chamadas, ritmo da
fala, blocos e a fórmula (o molde reutilizável).

Tudo é heurística sobre o texto falado: conta palavra, não entende a imagem. Serve para comparar vídeos entre si e
para enxergar o esqueleto, não como nota absoluta.

O molde nunca leva frase do vídeo estudado: cada bloco vira uma função ("abre com uma pergunta", "contexto em 3
frases curtas", "virada") com o tempo e o tamanho, para a pessoa escrever o dela.
"""
import re
import unicodedata

VERSAO = 6          # suba ao mudar a análise: os estudos guardados se refazem sozinhos a partir da transcrição
BURACO_S = 15.0
ABERTURA_S = 3.0
# Marcadores de virada (contraste, negação, revelação). Lista curta e explícita de propósito.
VIRADAS = ["mas", "só que", "porém", "até que", "de repente", "do nada", "foi aí", "e aí", "não era", "ninguém",
           "nenhum", "nenhuma", "nunca", "o contrário", "em vez", "na verdade", "acontece que", "o problema é",
           "but", "however", "until", "suddenly", "turns out", "actually", "instead", "nobody", "never"]
# Os que abrem bloco novo no molde: contraste de verdade. Negação ("nunca", "ninguém") conta como virada na métrica,
# mas aparece no meio da frase e não muda a direção do texto.
CONTRASTE = ["mas", "só que", "porém", "até que", "de repente", "do nada", "foi aí", "na verdade", "acontece que",
             "o problema é", "o contrário", "em vez", "but", "however", "turns out", "actually", "instead", "suddenly"]
CTA = {
    "seguir": ["segue", "siga", "me segue", "se inscreve", "se inscreva", "inscreva-se", "ativa o sininho",
               "follow", "subscribe"],
    "comentar": ["comenta", "comente", "nos comentarios", "me conta", "escreve ai", "deixa ai", "comment"],
    "link": ["link na bio", "link da bio", "ta na bio", "esta na bio", "link na descricao", "link abaixo",
             "clica no link", "link in bio"],
    "salvar": ["salva esse", "salve esse", "salva o video", "salva pra", "guarda esse", "save this"],
    "compartilhar": ["manda pra", "manda esse", "compartilha", "envia pra", "marca alguem", "marca aquele", "share"],
    "parte 2": ["parte 2", "parte dois", "proxima parte", "proximo episodio", "part 2"],
    "curtir": ["deixa o like", "deixa seu like", "curte o video", "smash the like"],
}
# Sem pontuação (legenda automática), só as aberturas que quase sempre são pergunta: "como", "quando" e "onde" no
# começo de um trecho costumam ser continuação de frase, não pergunta.
INTERROGATIVAS = ["por que", "porque sera", "sera que", "voce sabia", "voce ja", "ja pensou", "sabia que", "e se",
                  "o que acontece", "o que voce", "qual e o", "qual e a", "quem e", "quem nunca", "what", "why",
                  "did you", "have you"]
NEGACAO = ["nao", "nunca", "ninguem", "nada", "nenhum", "nenhuma", "jamais", "never", "nobody", "dont", "not"]
VOCE = ["voce", "voces", "vc", "te", "teu", "tua", "seu", "sua", "you", "your"]
NUMEROS = ["dois", "tres", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez", "cem", "mil", "milhao",
           "milhoes", "bilhao", "bilhoes", "metade", "dobro", "top"]
ORDINAIS = ["primeiro", "primeira", "segundo", "segunda", "terceiro", "terceira", "quarto", "quarta", "quinto",
            "quinta", "numero", "por ultimo", "e o ultimo", "em primeiro", "o primeiro", "a primeira", "first", "number"]

ROTULO = {"gancho": "Gancho", "contexto": "Contexto", "virada": "Virada", "lista": "Item da lista",
          "desenvolvimento": "Desenvolvimento",
          "pergunta": "Pergunta pra quem assiste", "chamada": "Chamada", "pergunta_final": "Pergunta do fim",
          "desfecho": "Desfecho"}
INSTRUCAO_GANCHO = {
    "pergunta": "Abra com uma pergunta que a pessoa não sabe responder de cara.",
    "negacao": "Abra contrariando algo que todo mundo acha (uma negação forte).",
    "numero": "Abra com um número ou uma quantidade que surpreende.",
    "voce": "Abra falando direto com quem assiste e prometa o que ela vai ver.",
    "afirmacao": "Abra com uma afirmação curta que deixa uma pergunta no ar.",
    "muda": "Abra só com imagem forte e texto na tela; a voz entra depois.",
}
NOME_GANCHO = {"pergunta": "pergunta", "negacao": "negação", "numero": "número", "voce": "fala com você",
               "afirmacao": "afirmação curta", "muda": "só imagem"}


def norm(s):
    """Minúsculas, sem acento e sem pontuação, para comparar palavra com marcador."""
    s = unicodedata.normalize("NFKD", str(s).lower())
    return re.sub(r"\s+", " ", "".join(ch for ch in s if (ch.isalnum() and not unicodedata.combining(ch)) or ch == " ")).strip()


_CONTRASTE = sorted((norm(v).split() for v in CONTRASTE), key=len, reverse=True)


def _vira(fr):
    """A frase começa (nas 3 primeiras palavras) com um contraste forte: abre bloco de virada no molde."""
    ws = fr["norm"].split()[:5]
    return next((" ".join(m) for k in range(3) for m in _CONTRASTE if ws[k:k + len(m)] == m), None)


def _tem(texto_norm, marcadores):
    t = f" {texto_norm} "
    return next((m for m in marcadores if f" {norm(m)} " in t), None)


def palavras_com_tempo(segmentos):
    """[(palavra, ini, fim)]. Sem tempo por palavra (legenda manual), distribui o trecho por igual."""
    saida = []
    for s in segmentos:
        if s.get("palavras"):
            saida += [(w["palavra"], float(w["ini"]), float(w.get("fim") or w["ini"])) for w in s["palavras"]]
            continue
        ws = s["texto"].split()
        passo = (s["fim"] - s["ini"]) / max(len(ws), 1)
        saida += [(w, s["ini"] + i * passo, s["ini"] + (i + 1) * passo) for i, w in enumerate(ws)]
    return saida


def _abre_contraste(palavras, i):
    """A palavra i começa um marcador de contraste forte ("mas", "só que"...)."""
    seguintes = [norm(w) for w, _, _ in palavras[i:i + 3]]
    return any(seguintes[:len(m)] == m for m in _CONTRASTE)


def frases(palavras, pontuada):
    """Corta a fala em frases: pela pontuação quando ela é confiável; senão, por pausa (0,6 s), antes de um "mas" ou
    "só que" e a cada 14 palavras."""
    saida, atual = [], []
    for i, (w, ini, fim) in enumerate(palavras):
        if not pontuada and len(atual) >= 4 and _abre_contraste(palavras, i):
            texto = " ".join(x[0] for x in atual)
            saida.append({"ini": round(atual[0][1], 2), "fim": round(atual[-1][2], 2), "texto": texto,
                          "n": len(atual), "norm": norm(texto)})
            atual = []
        atual.append((w, ini, fim))
        prox = palavras[i + 1] if i + 1 < len(palavras) else None
        corta = prox is None
        if not corta and pontuada:
            corta = bool(re.search(r"[.?!…]['\")\]]*$", w))
        elif not corta:
            corta = prox[1] - fim >= 0.6 or len(atual) >= 14
        if corta:
            texto = " ".join(x[0] for x in atual)
            saida.append({"ini": round(atual[0][1], 2), "fim": round(atual[-1][2], 2), "texto": texto,
                          "n": len(atual), "norm": norm(texto)})
            atual = []
    return saida


def _pergunta(f, pontuada):
    if "?" in f["texto"]:
        return True
    return not pontuada and any(f["norm"].startswith(norm(x) + " ") for x in INTERROGATIVAS)


def _tipo_abertura(fr, pontuada):
    if _pergunta(fr, pontuada):
        return "pergunta"
    if _tem(fr["norm"], NEGACAO):
        return "negacao"
    if re.search(r"\d", fr["texto"]) or _tem(fr["norm"], NUMEROS):
        return "numero"
    if _tem(fr["norm"], VOCE):
        return "voce"
    return "afirmacao"


def _cta(fr):
    for tipo, marcas in CTA.items():
        if _tem(fr["norm"], marcas):
            return tipo
    return None


def _ordinal(fr):
    return any(fr["norm"].startswith(norm(x) + " ") or fr["norm"] == norm(x) for x in ORDINAIS) or \
        bool(re.match(r"^(n[uú]mero\s+)?\d+\s*[.)º°:-]", fr["texto"].strip(), re.I))


def achar_viradas(palavras):
    normalizadas = [norm(w) for w, _, _ in palavras]
    marcadores = sorted((norm(v).split() for v in VIRADAS), key=len, reverse=True)
    achadas, i = [], 0
    while i < len(normalizadas):
        m = next((m for m in marcadores if normalizadas[i:i + len(m)] == m), None)
        if m:
            achadas.append({"t": round(palavras[i][1], 2), "marcador": " ".join(m)})
            i += len(m)
        else:
            i += 1
    return achadas


def buracos(tempos, ini, fim):
    """Trechos de mais de 15 s sem virada, do começo da fala ao fim dela."""
    marcos = [ini] + sorted(tempos) + [fim]
    return [{"de": round(a, 1), "ate": round(b, 1), "dur": round(b - a, 1)}
            for a, b in zip(marcos, marcos[1:]) if b - a > BURACO_S]


# ---------------------------------------------------------------- blocos e molde

def _funcao(fr, pontuada, lista_ok):
    if _cta(fr):
        return "chamada"
    if _pergunta(fr, pontuada):
        return "pergunta"
    if lista_ok and _ordinal(fr):
        return "lista"
    if _vira(fr):
        return "virada"
    return "contexto"


def montar_blocos(fs, primeira, dur, pontuada):
    if not fs:
        return []
    lista_ok = sum(1 for f in fs if _ordinal(f)) >= 2
    gancho = [f for f in fs if f["ini"] < primeira + ABERTURA_S] or fs[:1]
    resto = fs[len(gancho):]
    # Fechamento: as frases finais que chamam (seguir, comentar...) ou perguntam.
    fecho = []
    while resto and (_cta(resto[-1]) or _pergunta(resto[-1], pontuada)) and resto[-1]["ini"] >= dur * 0.6:
        fecho.insert(0, resto.pop())
    blocos = [{"funcao": "gancho", "frases": gancho}]
    for f in resto:
        fn = _funcao(f, pontuada, lista_ok)
        if fn == "chamada":
            fn = "contexto" if f["ini"] < dur * 0.6 else "chamada"
        atual = blocos[-1]
        # Virada, pergunta, item de lista e chamada abrem bloco novo; contexto se junta ao bloco anterior.
        if fn == "contexto" and atual["funcao"] != "gancho":
            atual["frases"].append(f)
        elif fn == "contexto":
            blocos.append({"funcao": "contexto", "frases": [f]})
        else:
            blocos.append({"funcao": fn, "frases": [f]})
    if fecho:
        tem_cta = [f for f in fecho if _cta(f)]
        blocos.append({"funcao": "chamada" if tem_cta else "pergunta_final", "frases": fecho})
    # Virada, pergunta ou item que puxa muitas frases atrás de si: as 2 primeiras ficam no bloco e o resto vira
    # desenvolvimento (senão o molde mandaria "vire a expectativa em 14 frases").
    partidos = []
    for b in blocos:
        if b["funcao"] in ("virada", "pergunta", "lista") and len(b["frases"]) > 4:
            partidos += [{"funcao": b["funcao"], "frases": b["frases"][:2]},
                         {"funcao": "desenvolvimento", "frases": b["frases"][2:]}]
        else:
            partidos.append(b)
    blocos = partidos
    # No máximo 9 blocos: junta o menor bloco do meio ao vizinho de antes.
    while len(blocos) > 9:
        meio = range(1, len(blocos) - (1 if blocos[-1]["funcao"] in ("chamada", "pergunta_final") else 0))
        k = min(meio, key=lambda j: sum(x["n"] for x in blocos[j]["frases"]))
        blocos[k - 1]["frases"] += blocos.pop(k)["frases"]
    saida, fim = [], 0.0
    for b in blocos:
        fr = b["frases"]
        ini = max(fr[0]["ini"], fim)   # a legenda automática sobrepõe frases vizinhas; o bloco começa onde o outro acaba
        fim = max(fr[-1]["fim"], ini)
        item = {"funcao": b["funcao"], "rotulo": ROTULO[b["funcao"]], "ini_s": round(ini, 1), "fim_s": round(fim, 1),
                "ini_pct": round(100 * ini / dur), "fim_pct": round(100 * min(fim, dur) / dur),
                "frases": len(fr), "palavras": sum(x["n"] for x in fr), "texto": " ".join(x["texto"] for x in fr)}
        if b["funcao"] in ("chamada",):
            item["tipo"] = next((_cta(x) for x in fr if _cta(x)), None)
        if b["funcao"] == "virada":
            item["marcador"] = _vira(fr[0])
        saida.append(item)
    return saida


def _instrucao(b, tipo_gancho):
    n, p = b["frases"], b["palavras"]
    if b["funcao"] == "gancho":
        return INSTRUCAO_GANCHO.get(tipo_gancho, INSTRUCAO_GANCHO["afirmacao"])
    if b["funcao"] == "contexto":
        return f"Dê só o contexto que falta para entender: {n} frase{'s' if n > 1 else ''}, ~{p} palavras."
    if b["funcao"] == "virada":
        return (f"Vire a expectativa: mostre que o que parecia certo não é, e desenvolva em {n} frase{'s' if n > 1 else ''}."
                if n > 1 else "Vire a expectativa numa frase (um \"mas\" ou \"só que\").")
    if b["funcao"] == "desenvolvimento":
        return f"Desenvolva com fatos concretos, um por frase: {n} frase{'s' if n > 1 else ''}, ~{p} palavras."
    if b["funcao"] == "lista":
        return f"Um item da lista: um fato por frase ({n} frase{'s' if n > 1 else ''}), do menos ao mais surpreendente."
    if b["funcao"] == "pergunta":
        return "Faça uma pergunta para quem assiste pensar na resposta antes de você dar" + \
            (f", e responda em {n - 1} frase{'s' if n > 2 else ''}." if n > 1 else ".")
    if b["funcao"] == "pergunta_final":
        return "Termine com uma pergunta aberta que qualquer um consegue responder nos comentários."
    if b["funcao"] == "chamada":
        alvo = {"seguir": "seguir o perfil", "comentar": "comentar", "link": "o link na bio", "salvar": "salvar o vídeo",
                "compartilhar": "mandar pra alguém", "parte 2": "ver a próxima parte", "curtir": "curtir"}.get(b.get("tipo"), "a ação que você quer")
        return f"Chame para {alvo}, numa frase só e sem pedir \"comenta X ou Y\"."
    return "Feche a ideia."


def fmt_t(s):
    s = max(0, int(s or 0))
    return f"{s // 60}:{s % 60:02d}"


def molde(r):
    """O esqueleto do vídeo em palavras genéricas. Não carrega o texto dos blocos."""
    g, blocos, dur = r["gancho"], r["blocos"], r["duracao_s"] or 1
    passos = []
    for b in blocos:
        passos.append({"funcao": b["funcao"], "rotulo": b["rotulo"], "ini_s": b["ini_s"], "fim_s": b["fim_s"],
                       "ini_pct": b["ini_pct"], "fim_pct": b["fim_pct"], "frases": b["frases"], "palavras": b["palavras"],
                       "instrucao": _instrucao(b, g["tipo"])})
    contados = []
    for b in blocos:
        nome = b["rotulo"] + (f" ({NOME_GANCHO.get(g['tipo'], g['tipo'])})" if b["funcao"] == "gancho" else "")
        if contados and contados[-1][0] == nome:
            contados[-1][1] += 1
        else:
            contados.append([nome, 1])
    esqueleto = " → ".join(n + (f" ×{k}" if k > 1 else "") for n, k in contados)
    vm = r["viradas"]["por_min"]
    regras = [
        f"Duração: {fmt_t(dur)}.",
        "Primeira fala: logo no começo (até 0,5 s)." if (g["primeira_fala_s"] or 0) <= 0.5
        else f"Primeira fala em {str(g['primeira_fala_s']).replace('.', ',')} s: antes disso, só imagem e texto na tela.",
        f"Ritmo da fala: ~{int(r['palavras_por_min'])} palavras por minuto.",
        (f"Uma virada a cada ~{int(round(60 / vm))} s." if vm else "Sem virada falada: a tensão vem da imagem ou da lista."),
    ]
    if r["perguntas"]:
        regras.append(f"{len(r['perguntas'])} pergunta{'s' if len(r['perguntas']) > 1 else ''} para quem assiste.")
    if r["cta"]:
        c = r["cta"][0]
        regras.append(f"Primeira chamada em {round(100 * c['t'] / dur)}% do vídeo ({c['tipo']}).")
    return {"esqueleto": esqueleto, "regras": regras, "passos": passos, "duracao_s": dur}


def molde_md(titulo, m, origem="", quadros=None):
    linhas = [f"# Molde: {titulo}", "",
              "Esqueleto tirado de um vídeo de referência. Use a estrutura, os tempos e o ritmo; escreva tudo com as suas "
              "palavras. Não copie nenhuma frase do vídeo original.", ""]
    if origem:
        linhas += [f"Origem: {origem}", ""]
    if quadros:
        linhas += ["## Visual da referência (obrigatório)", "",
                   f"Abra a folha de quadros `{quadros}` (12 imagens do vídeo, em ordem) antes de escrever o roteiro. "
                   "O visual do seu vídeo segue o mesmo tipo: se a referência tem personagem, o seu tem personagem; se "
                   "tem cenário que muda, o seu muda; se tem objeto animado, o seu anima. Faça com as peças do kit "
                   "(bonecos de `personagens/`, apresentador das cartelas, `mascote()` do Explicativo 3D, "
                   "`estilos_visuais/`). Nunca entregue fundo parado só com texto. Descreva ao usuário, em 2 ou 3 "
                   "linhas, o visual que você viu e como vai fazer, antes do roteiro.", ""]
    else:
        linhas += ["## Visual da referência", "",
                   "O estudo não conseguiu pegar a imagem do vídeo. Pergunte ao usuário, em uma linha, como é o visual "
                   "(tem personagem? cenário? animação?) ou peça um print, e faça o mesmo tipo de visual. Nunca entregue "
                   "fundo parado só com texto.", ""]
    linhas += [f"**Esqueleto:** {m['esqueleto']}", "", "## Regras", ""] + [f"- {x}" for x in m["regras"]]
    linhas += ["", "## Passo a passo", ""]
    for i, p in enumerate(m["passos"], 1):
        linhas.append(f"{i}. **{fmt_t(p['ini_s'])}–{fmt_t(p['fim_s'])} · {p['rotulo']}** ({p['ini_pct']}–{p['fim_pct']}% do "
                      f"vídeo): {p['instrucao']}")
    return "\n".join(linhas) + "\n"


def molde_curto(m):
    """Uma linha para o pedido da IA: os passos com tempo, sem texto do vídeo."""
    partes = [f"{fmt_t(p['ini_s'])} {p['rotulo'].lower()}" + (f" ({p['frases']} frases)" if p["frases"] > 1 else "")
              for p in m["passos"]]
    return "; ".join(partes) + ". " + " ".join(m["regras"])


# ---------------------------------------------------------------- raio-x

def analisar(segmentos, duracao=None, largura=None, altura=None):
    from .transcrever import formato_de
    palavras = palavras_com_tempo(segmentos)
    if not palavras:
        dur = duracao or 0
        return {"sem_fala": True, "duracao_s": dur, "formato": formato_de(largura, altura),
                "gancho": {"primeira_fala_s": None, "tipo": "muda", "abertura_3s": ""}, "viradas": {"n": 0, "por_min": 0,
                "lista": [], "buracos": []}, "perguntas": [], "cta": [], "palavras": 0, "palavras_por_min": 0, "blocos": []}
    texto = " ".join(s["texto"] for s in segmentos)
    pontuada = sum(texto.count(c) for c in ".?!") >= max(2, len(palavras) // 40)
    fim_fala = palavras[-1][2]
    dur = float(duracao or fim_fala) or 1.0
    minutos = max(dur / 60, 1e-6)
    primeira = palavras[0][1]
    fs = frases(palavras, pontuada)
    viradas = achar_viradas(palavras)
    abertura = " ".join(w for w, t, _ in palavras if t < primeira + ABERTURA_S)
    tipo = "muda" if primeira > 1.5 else _tipo_abertura(fs[0], pontuada)
    perguntas = [{"t": f["ini"], "texto": f["texto"], "provavel": "?" not in f["texto"]} for f in fs if _pergunta(f, pontuada)]
    ctas = [{"t": f["ini"], "tipo": _cta(f), "texto": f["texto"]} for f in fs if _cta(f)]
    r = {
        "duracao_s": round(dur, 1), "formato": formato_de(largura, altura), "pontuacao_confiavel": pontuada,
        "gancho": {"primeira_fala_s": round(primeira, 2), "abertura_3s": abertura, "tipo": tipo,
                   "tipo_nome": NOME_GANCHO.get(tipo, tipo), "palavras_3s": len(abertura.split()),
                   "primeira_frase": fs[0]["texto"]},
        "viradas": {"n": len(viradas), "por_min": round(len(viradas) / minutos, 1), "lista": viradas,
                    "buracos": buracos([v["t"] for v in viradas], primeira, fim_fala)},
        "perguntas": perguntas, "cta": ctas,
        "palavras": len(texto.split()), "palavras_por_min": round(len(texto.split()) / minutos, 1),
        "frases": len(fs), "palavras_por_frase": round(len(texto.split()) / max(len(fs), 1), 1),
        "silencio_final_s": round(max(dur - fim_fala, 0), 1),
    }
    r["blocos"] = montar_blocos(fs, primeira, dur, pontuada)
    return r
