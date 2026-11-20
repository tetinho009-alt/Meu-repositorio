# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Trava do gancho: o primeiro bloco decide se a pessoa fica (metodo/ganchos.md).

Confere quatro coisas, com os valores das preferências do canal (prefs: ganchos e roteiro):
- tempo: a fala do gancho termina até `ganchos.gancho_max_s` (padrão 3 s). Passou um pouco, aviso; passou mais de
  1 s, erro;
- lacuna: a fala abre uma pergunta na cabeça de quem assiste (pergunta, contradição, número ou hora, "isso",
  "ninguém", "mas"). Cumprimento ou anúncio ("oi", "neste vídeo", "hoje eu vou") sem lacuna é erro;
- tela: o bloco 1 tem texto grande na tela (muita gente assiste sem som);
- abertura muda: a fala começa até 0,5 s (imagem e texto já no quadro 0, nada de tela preta ou silêncio).

E, à parte, as viradas: entre uma virada e outra ("só que", "mas", "até que", "de repente", "porém", ou um bloco
novo de item, quiz, revelação ou antes e depois) não pode passar de `roteiro.viradas_max_s` (padrão 15 s). Vira aviso.

Uso (a partir da pasta kit/):
    python qa/gancho.py "Seu corpo faz isso e você nunca reparou." --tela "VOCÊ NUNCA REPAROU" [--dur 2.6]
Sem --dur, o tempo é estimado pelo ritmo médio da fala. Sai com código 1 se houver erro.

Para o painel e a IA:
    avaliar(fala, tela, dur_s, inicio_fala_s=0.0) -> (erros, avisos)
    viradas(blocos, janelas) -> avisos
    moldes(estilo, n=None) -> [ {gancho, por_que, de_onde, variacoes} ]   (prefs/ganchos.json + "Meus ganchos")
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
if str(KIT) not in sys.path:
    sys.path.insert(0, str(KIT))

ARQ_MOLDES = KIT / "prefs" / "ganchos.json"
PALAVRAS_POR_S = 2.6  # um pouco abaixo da fala real (2,4 a 2,8): a estimativa erra para o lado seguro
INICIO_PADRAO = 0.15  # o motor de cartelas começa a fala aos 0,15 s
TOLERANCIA_AVISO = 0.2
TOLERANCIA_ERRO = 1.0
FALA_MAX_INICIO = 0.5
FALA_IDEAL_INICIO = 0.3


def _norm(texto):
    t = unicodedata.normalize("NFKD", str(texto or "").lower())
    return " ".join("".join(c for c in t if not unicodedata.combining(c)).split())


def _s(x):
    """Segundos no jeito brasileiro: 3,5 s."""
    return f"{x:.1f}".replace(".", ",")


def _original(fala, trecho_norm):
    """As primeiras palavras da fala original, do tamanho do trecho achado no texto sem acento."""
    n = len(trecho_norm.split())
    return " ".join(str(fala).split()[:n]).rstrip(",.!:;")


# Abertura que só cumprimenta, anuncia ou descreve o vídeo: o estranho ainda não tem motivo para ficar.
ABERTURA_VAZIA = re.compile(
    r"^(oi+|ola|e ai|eai|fala+ (galera|pessoal|gente|ai)|salve|bom dia|boa tarde|boa noite|seja(m)? bem.vindos?|"
    r"bem.vindos?|(neste|nesse|no) video( de hoje)?|hoje (eu )?(vou|vamos|a gente vai)|hoje e dia|"
    r"vem comigo|vamos (la|falar|ver|aprender|conhecer)|bora (la|ver)|eu vou (te |lhes |)(mostrar|contar|explicar|ensinar)|"
    r"voce sabia que|sabia que|deixa eu (te )?(mostrar|contar)|antes de (comecar|mais nada)|"
    r"esse (e|eh) (o|um) video|este (e|eh) (o|um) video)\b")
ANUNCIO_SOLTO = re.compile(r"^(voce sabia que|sabia que)\b")

# Sinais de lacuna: o que faz a pessoa querer a resposta.
LACUNA = [
    ("pergunta", re.compile(r"\?")),
    ("negação ou contradição", re.compile(r"\b(nao|nunca|ninguem|nada|nenhum|nenhuma|jamais|nem|sem)\b")),
    ("virada", re.compile(r"\b(mas|so que|porem|ate que|de repente|so tem um problema|o problema e)\b")),
    # "um/uma" ficam de fora: são artigo na maioria das frases.
    ("número ou hora", re.compile(r"\d|\b(dois|duas|tres|quatro|cinco|seis|sete|oito|nove|dez|doze|vinte|trinta|"
                                  r"cem|cento|mil|milhao|milhoes|metade|dobro|meia.noite|meio.dia|horas?|minutos?|"
                                  r"segundos?|dias?)\b")),
    # "esta/este" ficam de fora: sem acento, "está" vira "esta".
    ("apontar para a imagem", re.compile(r"\b(isso|isto|esse|essa|olha|aqui)\b")),
    ("afirmação que surpreende", re.compile(
        r"\b(errado|errada|proibid\w*|segredo|mentira|ninguem te conta|pior|absurd\w*|impossivel|estranh\w*|"
        r"sumiu|sumir|morreu|morrer|explod\w*|perigos\w*|cuidado|nao faca|para de|pare de|o unico|a unica|"
        r"o maior|a maior|o primeiro|ultim[oa]|nojent\w*|deu errado|quase|falta|faltam|faltava|sozinh\w*|"
        r"vazi[oa])\b")),
    ("pergunta sem ponto", re.compile(r"^(por que|porque|como|quem|qual|quanto|quantos|quantas|o que|onde|"
                                      r"e se|imagina|se voce)\b")),
]

# Palavras e tipos de bloco que contam como virada.
VIRADA = re.compile(r"\b(so que|mas|ate que|de repente|porem)\b")
TIPOS_VIRADA = {"item", "quiz", "revela", "antes_depois"}

MOLDE_REESCRITA = ("molde para reescrever: comece pelo que não devia acontecer ou pela imagem mais forte, com um "
                   "número ou uma hora e uma contradição, em até 7 palavras. Ex.: \"Meia-noite. O elevador desceu. "
                   "Ninguém chamou.\" ou \"Essa ponte não tem nenhum prego.\" (mais moldes em metodo/ganchos.md)")


def limites():
    """Valores em vigor (preferências do canal, ou os recomendados quando elas não carregam)."""
    v = {"gancho_max_s": 3.0, "sem_abertura_muda": True, "variacoes_ab": 3, "viradas_max_s": 15.0,
         "biblioteca_extra": []}
    try:
        from prefs import carregar
        p = carregar()
        g, r = p.get("ganchos", {}), p.get("roteiro", {})
        v.update({k: g[k] for k in ("gancho_max_s", "sem_abertura_muda", "variacoes_ab", "biblioteca_extra") if k in g})
        if "viradas_max_s" in r:
            v["viradas_max_s"] = r["viradas_max_s"]
    except Exception:  # noqa: BLE001
        pass
    v["gancho_max_s"] = float(v["gancho_max_s"])
    v["viradas_max_s"] = float(v["viradas_max_s"])
    return v


def estimar_s(fala, inicio=INICIO_PADRAO):
    """Fim estimado da fala do gancho, contado do quadro 0 (antes de gravar a voz)."""
    n = len(re.sub(r"\[[^\]]*\]|<[^>]*>", " ", fala or "").split())
    return 0.0 if not n else round(inicio + 0.25 + n / PALAVRAS_POR_S, 2)


def sinais(fala):
    """Nomes dos sinais de lacuna encontrados na fala."""
    t = _norm(fala)
    return [nome for nome, rx in LACUNA if rx.search(t if nome != "pergunta" else str(fala or ""))]


def checar_tempo(dur_s, inicio_fala_s=0.0, lim=None):
    lim = lim or limites()
    erros, avisos = [], []
    mx = lim["gancho_max_s"]
    if dur_s is not None:
        if dur_s > mx + TOLERANCIA_ERRO:
            erros.append(f"o gancho (bloco 1) termina em {_s(dur_s)} s; corte para caber em {_s(mx)} s (até 7 "
                         "palavras): quem não entende o vídeo nesse tempo, pula. Tire o cumprimento e a explicação, "
                         "fica só a lacuna; a contradição pode vir colada no bloco 2")
        elif dur_s > mx + TOLERANCIA_AVISO:
            avisos.append(f"o gancho termina em {_s(dur_s)} s; o ideal é até {_s(mx)} s (corte uma ou duas palavras)")
    if inicio_fala_s is not None:
        muda = (f"a fala começa só em {_s(inicio_fala_s)} s: abertura muda faz a pessoa passar o dedo. Imagem e "
                "texto grande já no quadro 0 e a voz entrando até 0,3 s")
        if inicio_fala_s > FALA_MAX_INICIO:
            (erros if lim["sem_abertura_muda"] else avisos).append(muda)
        elif inicio_fala_s > FALA_IDEAL_INICIO:
            avisos.append(f"a fala começa em {_s(inicio_fala_s)} s; o ideal é até 0,3 s")
    return erros, avisos


def checar_tela(tela):
    if not str(tela or "").strip():
        return ["o bloco 1 não tem texto na tela ('tela'): muita gente assiste sem som, e o texto grande no quadro 0 "
                "é o que segura quem está de mudo. Ponha a frase do gancho, curta, em letra grande"], []
    if len(str(tela).split()) > 9:
        return [], [f"o texto da tela do gancho tem {len(str(tela).split())} palavras; até 7 se lê num relance"]
    return [], []


def checar_fala(fala):
    erros, avisos = [], []
    t = _norm(fala)
    if not t:
        return ["o bloco 1 não tem fala: o gancho precisa da voz dizendo a lacuna desde o começo"], []
    achados = sinais(fala)
    vazio = ABERTURA_VAZIA.match(t)
    if vazio and not achados:
        erros.append(f"o gancho começa com '{_original(fala, vazio.group(0))}' e só anuncia o vídeo, sem abrir uma "
                     f"pergunta na cabeça de quem assiste: ela não tem motivo para ficar. {MOLDE_REESCRITA}")
    elif vazio:
        avisos.append(f"o gancho começa com '{_original(fala, vazio.group(0))}': corte essa abertura; a lacuna "
                      f"({', '.join(achados)}) tem que estar nas primeiras palavras")
    elif not achados:
        erros.append("o gancho só descreve o assunto e não abre lacuna (nenhuma pergunta, contradição, número, "
                     f"'isso' ou 'ninguém'): a pessoa entende do que é e vai embora. {MOLDE_REESCRITA}")
    elif ANUNCIO_SOLTO.match(t) and len(achados) < 2:
        avisos.append("'você sabia que' sozinho é fraco: diga o fato surpreendente direto, com o número na frente")
    return erros, avisos


def avaliar(fala, tela, dur_s, inicio_fala_s=0.0):
    """(erros, avisos) do gancho. `dur_s`: segundo em que a fala do bloco 1 termina, contado do quadro 0 (None pula
    a conferência de tempo). `inicio_fala_s`: segundo em que a voz começa."""
    lim = limites()
    erros, avisos = [], []
    for e, a in (checar_fala(fala), checar_tela(tela), checar_tempo(dur_s, inicio_fala_s, lim)):
        erros += e
        avisos += a
    return erros, avisos


def _tem_virada(bloco):
    return bloco.get("tipo") in TIPOS_VIRADA or bool(VIRADA.search(_norm(bloco.get("fala", ""))))


def viradas(blocos, janelas):
    """Avisos quando passa tempo demais sem virada. `janelas`: [{"t0", "t1"}] de cada bloco (reais ou estimadas)."""
    if not blocos or not janelas:
        return []
    mx = limites()["viradas_max_s"]
    marcos = [0.0] + [j["t0"] for b, j in zip(blocos[1:], janelas[1:]) if _tem_virada(b)]
    fim = janelas[-1].get("fim", janelas[-1]["t1"])
    avisos = []
    for a, b in zip(marcos, marcos[1:] + [fim]):
        if b - a > mx:
            avisos.append(f"de {a:.0f} s a {b:.0f} s ({_s(b - a)} s) não acontece nenhuma virada; o máximo é {mx:g} s. "
                          "Ponha um 'só que...', um item novo ou uma revelação no meio desse trecho: é onde a curva cai")
    return avisos


def moldes(estilo=None, n=None):
    """Ganchos-modelo do estilo (prefs/ganchos.json), com os do usuário ("Meus ganchos") na frente.
    `n`: quantos devolver (padrão: ganchos.variacoes_ab, o número de aberturas que a IA propõe para o teste A/B;
    0 = todos)."""
    lim = limites()
    try:
        base = json.loads(ARQ_MOLDES.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        base = {}
    lista = [{"gancho": g, "por_que": "gancho seu que funcionou", "de_onde": "Meus ganchos", "variacoes": []}
             for g in lim["biblioteca_extra"]]
    if estilo:
        lista += base.get(estilo, [])
    else:
        lista += [m for ms in base.values() for m in ms]
    n = int(lim["variacoes_ab"] if n is None else n)
    return lista[:n] if n > 0 else lista


def main():
    import argparse
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Confere o gancho do vídeo (o primeiro bloco).")
    ap.add_argument("fala", help="a fala do gancho, entre aspas")
    ap.add_argument("--tela", default="", help="o texto grande na tela do bloco 1")
    ap.add_argument("--dur", type=float, help="segundo em que a fala do gancho termina (sem isso, estima)")
    ap.add_argument("--inicio", type=float, default=INICIO_PADRAO, help="segundo em que a voz começa (padrão 0,15)")
    a = ap.parse_args()
    dur = a.dur if a.dur is not None else estimar_s(a.fala, a.inicio)
    erros, avisos = avaliar(a.fala, a.tela, dur, a.inicio)
    print(f"\n== GANCHO  ({_s(dur)} s{'' if a.dur is not None else ', estimado'}; "
          f"sinais de lacuna: {', '.join(sinais(a.fala)) or 'nenhum'})")
    for e in erros:
        print(f"  ERRO  {e}")
    for av in avisos:
        print(f"  AVISO {av}")
    if not erros and not avisos:
        print("  tudo certo")
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    main()
