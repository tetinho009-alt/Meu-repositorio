# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Estudo de nicho: vários estudos lado a lado, o padrão que se repete e um molde do nicho.

Conclusão só com 3 vídeos ou mais (MIN_NICHO): um vídeo sozinho mostra um jeito, não um padrão. Um padrão só entra
na lista quando aparece em pelo menos 60% dos vídeos. Comparação entre os mais vistos e os outros é descrição
("nesses vídeos"), nunca promessa de causa.
"""
from collections import Counter
from statistics import median

from . import MIN_NICHO, ler_estudo, resumo
from .raiox import NOME_GANCHO, ROTULO, fmt_t

FATIAS = 5   # o molde do nicho divide o vídeo em 5 partes iguais e pega a função mais comum de cada uma


def _br(x, casas=1):
    return f"{x:.{casas}f}".replace(".", ",")


def _maioria(n, total):
    return total and n / total >= 0.6


def _funcao_em(blocos, pct):
    for b in blocos:
        if b["ini_pct"] <= pct <= max(b["fim_pct"], b["ini_pct"]):
            return b["funcao"]
    antes = [b for b in blocos if b["ini_pct"] <= pct]
    return antes[-1]["funcao"] if antes else (blocos[0]["funcao"] if blocos else None)


def comparar(ids):
    estudos = [e for e in (ler_estudo(i) for i in dict.fromkeys(ids or [])) if e and not (e.get("raiox") or {}).get("sem_fala")]
    linhas = [resumo(e) for e in estudos]
    n = len(estudos)
    if n < MIN_NICHO:
        return {"ok": False, "linhas": linhas, "msg": f"Escolha pelo menos {MIN_NICHO} vídeos com fala. Com menos que "
                f"isso dá pra ver um jeito de fazer, mas não um padrão do nicho."}
    rx = [e["raiox"] for e in estudos]
    padroes, varia = [], []

    def conta(k, singular, plural, resto):
        """"2 de 3 abrem com...", "1 de 3 abre com...", "Nenhum dos 3 abre com..."."""
        if k == 0:
            return f"Nenhum dos {n} {singular} {resto}."
        return f"{k} de {n} {singular if k == 1 else plural} {resto}."

    durs = [r["duracao_s"] for r in rx if r.get("duracao_s")]
    if durs:
        padroes.append(f"Duração entre {fmt_t(min(durs))} e {fmt_t(max(durs))} (meio: {fmt_t(median(durs))}).")
    falas = [r["gancho"]["primeira_fala_s"] for r in rx if r["gancho"].get("primeira_fala_s") is not None]
    rapidas = sum(1 for f in falas if f <= 1.0)
    if _maioria(rapidas, n):
        padroes.append(conta(rapidas, "começa", "começam", "a falar em até 1 s"))
    else:
        varia.append("A primeira fala varia: " + conta(rapidas, "fala", "falam", "em até 1 s")[0].lower()
                     + conta(rapidas, "fala", "falam", "em até 1 s")[1:])
    tipos = Counter(r["gancho"]["tipo"] for r in rx).most_common()
    t0, k0 = tipos[0]
    if _maioria(k0, n):
        padroes.append(conta(k0, "abre", "abrem", "só com imagem, sem fala no começo") if t0 == "muda"
                       else conta(k0, "abre com", "abrem com", NOME_GANCHO.get(t0, t0)))
    else:
        varia.append("O jeito de abrir varia (" + ", ".join(f"{NOME_GANCHO.get(t, t)}: {k}" for t, k in tipos) + ").")
    vms = [r["viradas"]["por_min"] for r in rx]
    padroes.append(f"Viradas: {_br(median(vms))} por minuto no meio da lista (de {_br(min(vms))} a {_br(max(vms))}).")
    sem_buraco = sum(1 for r in rx if not r["viradas"]["buracos"])
    if _maioria(sem_buraco, n):
        padroes.append(conta(sem_buraco, "passa", "passam", "no máximo 15 s sem uma virada"))
    ppm = [r["palavras_por_min"] for r in rx]
    padroes.append(f"Fala a ~{int(median(ppm))} palavras por minuto (de {int(min(ppm))} a {int(max(ppm))}).")
    com_perg = sum(1 for r in rx if r["perguntas"])
    (padroes if _maioria(com_perg, n) else varia).append(conta(com_perg, "faz", "fazem", "pergunta para quem assiste"))
    com_cta = [r for r in rx if r["cta"]]
    if _maioria(len(com_cta), n):
        pos = median(100 * r["cta"][0]["t"] / (r["duracao_s"] or 1) for r in com_cta)
        tipo_cta = Counter(r["cta"][0]["tipo"] for r in com_cta).most_common(1)[0][0]
        padroes.append(conta(len(com_cta), "tem", "têm", f"chamada (a mais comum: {tipo_cta}), por volta de {int(pos)}% do vídeo"))
    else:
        varia.append(conta(len(com_cta), "pede", "pedem", "alguma ação (seguir, comentar, link)"))
    formatos = Counter(r.get("formato") for r in rx if r.get("formato")).most_common()
    if formatos and _maioria(formatos[0][1], n):
        plural = {"vertical": "verticais", "horizontal": "horizontais", "quadrado": "quadrados"}
        padroes.append(conta(formatos[0][1], "é", "são", formatos[0][0] if formatos[0][1] == 1 else plural.get(formatos[0][0], formatos[0][0])))

    # Os mais vistos contra os outros, quando há views em pelo menos 4 vídeos.
    contraste = []
    com_views = sorted([(l["views"], r) for l, r in zip(linhas, rx) if l.get("views")], key=lambda x: -x[0])
    if len(com_views) >= 4:
        meio = len(com_views) // 2
        cima, baixo = [r for _, r in com_views[:meio]], [r for _, r in com_views[meio:]]

        def comp(nome, f, menor_melhor_txt, maior_txt, casas=1):
            a, b = median(f(r) for r in cima), median(f(r) for r in baixo)
            if max(a, b) and abs(a - b) / max(a, b) >= 0.25:
                contraste.append(f"Os {meio} mais vistos {menor_melhor_txt if a < b else maior_txt}: {_br(a, casas)} contra "
                                 f"{_br(b, casas)} {nome}.")
        comp("s até a primeira fala", lambda r: r["gancho"]["primeira_fala_s"] or 0, "começam a falar antes", "demoram mais a falar")
        comp("viradas por minuto", lambda r: r["viradas"]["por_min"], "viram menos", "viram mais")
        comp("s de duração", lambda r: r["duracao_s"] or 0, "são mais curtos", "são mais longos", 0)
        comp("palavras por minuto", lambda r: r["palavras_por_min"], "falam mais devagar", "falam mais rápido", 0)

    return {"ok": True, "n": n, "linhas": linhas, "padroes": padroes, "varia": varia, "contraste": contraste,
            "molde": molde_nicho(rx, durs, tipos[0][0], vms, ppm)}


def molde_nicho(rx, durs, tipo_gancho, vms, ppm):
    """Gancho com o tamanho mediano dos ganchos estudados; o resto do vídeo em 4 fatias iguais, cada uma com a
    função que mais aparece naquele ponto dos vídeos."""
    from .raiox import INSTRUCAO_GANCHO
    dur = median(durs) if durs else 60
    fim_gancho = [100 * b["fim_s"] / (r["duracao_s"] or 1) for r in rx for b in r["blocos"][:1] if b["funcao"] == "gancho"]
    g_pct = max(3, min(15, round(median(fim_gancho)) if fim_gancho else 5))
    passos = [{"funcao": "gancho", "rotulo": ROTULO["gancho"], "ini_pct": 0, "fim_pct": g_pct}]
    fatias = FATIAS - 1
    for k in range(fatias):
        ini = g_pct + (100 - g_pct) * k / fatias
        fim = g_pct + (100 - g_pct) * (k + 1) / fatias
        votos = Counter(f for f in (_funcao_em(r["blocos"], (ini + fim) / 2) for r in rx) if f and f != "gancho").most_common(1)
        fn = votos[0][0] if votos else "contexto"
        if fn == passos[-1]["funcao"]:
            passos[-1]["fim_pct"] = round(fim)
            continue
        passos.append({"funcao": fn, "rotulo": ROTULO.get(fn, fn), "ini_pct": round(ini), "fim_pct": round(fim)})
    instr = {
        "gancho": INSTRUCAO_GANCHO.get(tipo_gancho, INSTRUCAO_GANCHO["afirmacao"]),
        "contexto": "Contexto curto: só o que falta para entender, em frases curtas.",
        "desenvolvimento": "Desenvolvimento: fatos concretos, um por frase.",
        "virada": "Virada: mostre que o que parecia certo não é.",
        "lista": "Itens da lista, um fato por frase, do menos ao mais surpreendente.",
        "pergunta": "Pergunta para quem assiste pensar na resposta.",
        "pergunta_final": "Termine com uma pergunta aberta que qualquer um responde.",
        "chamada": "Chamada numa frase só (seguir, link ou próxima parte).",
    }
    for p in passos:
        p["ini_s"], p["fim_s"] = round(dur * p["ini_pct"] / 100, 1), round(dur * p["fim_pct"] / 100, 1)
        p["instrucao"] = instr.get(p["funcao"], "Desenvolva a ideia.")
        p["frases"], p["palavras"] = 0, 0
    vm = median(vms)
    regras = [f"Duração: {fmt_t(dur)}.", f"Ritmo da fala: ~{int(median(ppm))} palavras por minuto.",
              f"Uma virada a cada ~{int(round(60 / vm))} s." if vm else "A tensão vem da imagem ou da lista, não de virada falada."]
    esqueleto = " → ".join(p["rotulo"] for p in passos)
    return {"esqueleto": esqueleto, "regras": regras, "passos": passos, "duracao_s": round(dur, 1), "nicho": True}
