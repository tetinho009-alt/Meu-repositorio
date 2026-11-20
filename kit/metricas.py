# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Números de cada vídeo e o que mudar no próximo (metodo/engajamento.md).

Os números vêm do painel da rede (Insights do Instagram, Estatísticas do TikTok, YouTube Studio), lidos pelo próprio
usuário 2 dias depois de postar (prefs: metricas.dias_para_medir). Ficam em `canal/metricas.json`, com a data.

Chaves aceitas em `numeros` (todas opcionais; porcentagem em %, ex.: 32.4):
    views, pulados_pct, compartilhamentos_pct, comentarios_pct, salvamentos_pct, curtidas_pct,
    tempo_medio_s, duracao_s, retencao_queda_s (segundo em que a curva de retenção despenca)

Uso (a partir da pasta kit/):
    python metricas.py --pulados 32,4 --compartilhamentos 0,1 --comentarios 0,2 --curtidas 10,2 --salvamentos 0,8
    python metricas.py --episodio dia6 --rede instagram --registrar --pulados 32,4 ...   # grava em canal/metricas.json
    python metricas.py --historico

Para o painel e a IA:
    registrar(episodio, rede, numeros) -> registro gravado
    sugestoes(numeros) -> [frases em português com o ajuste do próximo episódio]
    historico(episodio=None, rede=None) -> [registros]
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

KIT = Path(__file__).resolve().parent
ESTUDIO = KIT.parent
ARQ = ESTUDIO / "canal" / "metricas.json"

CHAVES = ("views", "pulados_pct", "compartilhamentos_pct", "comentarios_pct", "salvamentos_pct", "curtidas_pct",
          "tempo_medio_s", "duracao_s", "retencao_queda_s")
REDES = ("instagram", "tiktok", "youtube_shorts", "youtube_longo", "kwai")

# Faixas de referência. Vêm de um canal real (série com voto no Instagram, 31/10 a 06/11/2026, resultado pessoal) e
# do que o próprio painel do Instagram chama de "melhor" ou "pior que o normal". Servem de bússola, não de promessa.
PULADOS_ALTO = 40.0
PULADOS_ATENCAO = 35.0
COMPART_BAIXO = 0.5
COMENT_BAIXO = 0.5
SALV_BAIXO = 0.5
CURT_BAIXO = 4.0
RETENCAO_CEDO_S = 12.0
POUCAS_VIEWS = 500


def _num(v):
    """Número escrito do jeito brasileiro ou não: "32,4", "32.4", "1.850" (mil oitocentos e cinquenta), "1,85 mil"."""
    if v is None or v == "":
        return None
    if isinstance(v, (int, float)):
        return float(v)
    t = str(v).strip().lower().replace("%", "").replace(" ", "")
    mult = 1
    for sufixo, m in (("mil", 1_000), ("mi", 1_000_000), ("k", 1_000)):
        if t.endswith(sufixo):
            t, mult = t[: -len(sufixo)], m
            break
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(\.\d{3})+", t):
        t = t.replace(".", "")
    return float(t) * mult


def _f(x):
    """Número no jeito brasileiro: 0,1 e 1850."""
    return f"{x:g}".replace(".", ",")


def limpar(numeros):
    """Só as chaves conhecidas, como número. Chave desconhecida ou valor que não é número dá erro em português."""
    fora = [k for k in (numeros or {}) if k not in CHAVES]
    if fora:
        raise ValueError(f"número que o kit não conhece: {', '.join(fora)}. Use: {', '.join(CHAVES)}")
    limpo = {}
    for k, v in (numeros or {}).items():
        try:
            n = _num(v)
        except ValueError:
            raise ValueError(f"{k}: '{v}' não é um número (ex.: 32,4)") from None
        if n is None:
            continue
        if n < 0 or (k.endswith("_pct") and n > 100):
            raise ValueError(f"{k}: {v} está fora da faixa ({'0 a 100' if k.endswith('_pct') else 'a partir de 0'})")
        limpo[k] = n
    return limpo


def sugestoes(numeros):
    """Ajustes concretos para o próximo episódio, do mais urgente ao menos urgente."""
    n = limpar(numeros)
    s = []
    if not n:
        return ["Anote pelo menos três números do painel da rede: pulados, compartilhamentos e comentários."]
    pul, comp, com = n.get("pulados_pct"), n.get("compartilhamentos_pct"), n.get("comentarios_pct")
    salv, curt = n.get("salvamentos_pct"), n.get("curtidas_pct")
    dur, medio, queda = n.get("duracao_s"), n.get("tempo_medio_s"), n.get("retencao_queda_s")

    if pul is not None:
        if pul > PULADOS_ALTO:
            s.append(f"Pulados em {_f(pul)}%: o gancho não segurou. Reescreva o primeiro bloco (metodo/ganchos.md): "
                     "imagem e texto grande no quadro 0, voz entrando até 0,3 s e uma lacuna nas primeiras palavras. "
                     "Peça à IA 3 aberturas diferentes e teste uma por episódio.")
        elif pul > PULADOS_ATENCAO:
            s.append(f"Pulados em {_f(pul)}%: no limite. Confira se o primeiro quadro já mostra a imagem mais forte "
                     "(não um título nem tela escura).")
    if queda is not None:
        if queda <= RETENCAO_CEDO_S:
            s.append(f"A curva despenca em {_f(queda)} s: o começo explica demais. Mostre o resultado ou a "
                     "transformação (o antes e depois, a ameaça acontecendo) entre 3 e 5 s, e deixe a explicação para "
                     "depois. Nunca abra com \"ontem\", resumo ou placar.")
        elif dur and queda < 0.85 * dur:
            s.append(f"A curva cai em {_f(queda)} s, no meio do vídeo: veja o que acontece ali. Costuma ser cena "
                     "repetida ou explicação longa. Ponha uma virada (\"só que...\") logo antes desse ponto.")
    if comp is not None and comp < COMPART_BAIXO:
        s.append(f"Compartilhamentos em {_f(comp)}%: o vídeo não se explica sozinho para quem não segue. Faça o "
                 "episódio se explicar em 3 s, sem depender da parte anterior, e ponha um momento de identificação "
                 "(\"todo mundo tem um amigo assim\"). Nunca peça para compartilhar: a rede rebaixa.")
    if com is not None and com < COMENT_BAIXO:
        s.append(f"Comentários em {_f(com)}%: a pergunta chega tarde ou é fechada. Faça uma pergunta aberta no meio "
                 "(antes da resposta) e termine com o voto em duas saídas claras (\"amanhã ele resolve qual: X ou "
                 "Y?\"). Nada de \"comenta X\".")
    if salv is not None and salv < SALV_BAIXO:
        s.append(f"Salvamentos em {_f(salv)}%: falta algo que valha rever. Em explicativo, top 5 e quiz, entregue "
                 "um número, uma lista ou um passo a passo que a pessoa queira guardar.")
    if curt is not None and curt < CURT_BAIXO:
        s.append(f"Curtidas em {_f(curt)}%: a história não entrega a satisfação prometida. Mostre a vitória (a "
                 "limpeza, o acerto, a revelação) com a imagem, não só com a fala.")
    if medio is not None and dur:
        taxa = medio / dur
        if taxa < 0.3:
            s.append(f"Tempo médio de {_f(medio)} s num vídeo de {_f(dur)} s ({100 * taxa:.0f}%): o meio arrasta. "
                     "Uma virada a cada 15 s no máximo e corte a cena que repete mecânica.")
        elif taxa >= 0.6:
            s.append(f"Tempo médio de {_f(medio)} s em {_f(dur)} s ({100 * taxa:.0f}%): a história segura. Mantenha "
                     "o ritmo e o tamanho.")
    if n.get("views") is not None and n["views"] < POUCAS_VIEWS:
        s.append(f"Com {_f(n['views'])} views ainda são poucos dados: espere 2 dias e compare com a média dos seus 3 "
                 "últimos vídeos antes de mudar o formato.")
    if not s:
        s.append("Nenhum número abaixo da faixa: repita a estrutura do gancho e do fim e mude uma coisa por vez "
                 "no próximo, para saber o que fez diferença.")
    elif pul is not None and pul <= PULADOS_ATENCAO:
        s.append(f"O que manter: pulados em {_f(pul)}%, o gancho segurou. Use o mesmo molde de abertura no próximo e "
                 "mexa só no que está acima.")
    return s


def historico(episodio=None, rede=None):
    try:
        dados = json.loads(ARQ.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    regs = dados if isinstance(dados, list) else dados.get("registros", [])
    return [r for r in regs if (episodio is None or r.get("episodio") == episodio)
            and (rede is None or r.get("rede") == rede)]


def registrar(episodio, rede, numeros):
    """Grava os números do episódio na rede, com a data, e devolve o registro (com as sugestões)."""
    episodio = str(episodio or "").strip()
    if not episodio:
        raise ValueError("diga qual é o episódio (ex.: parte_2 ou o nome do vídeo)")
    if rede not in REDES:
        raise ValueError(f"rede '{rede}' não existe; use uma destas: {', '.join(REDES)}")
    limpo = limpar(numeros)
    reg = {"data": datetime.now().isoformat(timespec="minutes"), "episodio": episodio, "rede": rede,
           "numeros": limpo, "sugestoes": sugestoes(limpo)}
    regs = historico()
    regs.append(reg)
    ARQ.parent.mkdir(parents=True, exist_ok=True)
    tmp = ARQ.with_suffix(".tmp")
    tmp.write_text(json.dumps(regs, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    tmp.replace(ARQ)
    return reg


def main():
    import argparse
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Números do vídeo e o que mudar no próximo episódio.")
    campos = {"views": "views", "pulados": "pulados_pct", "compartilhamentos": "compartilhamentos_pct",
              "comentarios": "comentarios_pct", "salvamentos": "salvamentos_pct", "curtidas": "curtidas_pct",
              "tempo-medio": "tempo_medio_s", "duracao": "duracao_s", "queda": "retencao_queda_s"}
    for op, chave in campos.items():
        ap.add_argument(f"--{op}", dest=chave, help=chave)
    ap.add_argument("--episodio")
    ap.add_argument("--rede", default="instagram")
    ap.add_argument("--registrar", action="store_true", help="grava em canal/metricas.json")
    ap.add_argument("--historico", action="store_true")
    a = ap.parse_args()
    if a.historico:
        regs = historico(a.episodio)
        if not regs:
            print("Nenhum número anotado ainda (canal/metricas.json).")
        for r in regs:
            nums = ", ".join(f"{k}={_f(v)}" for k, v in r["numeros"].items())
            print(f"{r['data']}  {r['episodio']}  {r['rede']}: {nums}")
        return
    numeros = {c: getattr(a, c) for c in campos.values() if getattr(a, c) is not None}
    try:
        if a.registrar:
            reg = registrar(a.episodio, a.rede, numeros)
            print(f"REGISTRADO em {ARQ} ({reg['data']})")
            lista = reg["sugestoes"]
        else:
            lista = sugestoes(numeros)
    except ValueError as e:
        raise SystemExit(f"ERRO: {e}\nO QUE FAZER: corrija o que a linha acima aponta e rode de novo.") from None
    print("\nO que mudar no próximo episódio:")
    for i, frase in enumerate(lista, 1):
        print(f"  {i}. {frase}")


if __name__ == "__main__":
    main()
