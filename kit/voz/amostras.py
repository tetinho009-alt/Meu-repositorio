# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Amostras de voz: grava a mesma frase do canal em 3 vozes, para o usuário escolher ouvindo.

Uso (a partir da pasta kit/):
    python -m voz.amostras --frase "Como uma pilha desse tamanho ilumina o quintal inteiro?" --genero masculino --idade jovem
    python -m voz.amostras --frase "..." --provedor gemini        # grátis, voz do Google (precisa da chave grátis)
    python -m voz.amostras --frase "..." --provedor kokoro        # grátis, no computador, sem internet
    python -m voz.amostras --br --genero masculino                # vozes brasileiras da biblioteca (prévia grátis)
    python -m voz.amostras --adicionar <id_do_dono> <voice_id> "Nome"   # põe uma voz da biblioteca na sua conta
    python -m voz.amostras ... --seco                             # mostra o plano e o custo, sem gravar

As amostras vão para ../canal/testes-de-voz/ (ou --saida). Cada amostra da ElevenLabs gasta cerca de 1 crédito por
caractere da frase; as prévias da biblioteca (--br), o Gemini (plano grátis) e o Kokoro não gastam nada.
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

_KIT = Path(__file__).resolve().parent.parent
if str(_KIT) not in sys.path:
    sys.path.insert(0, str(_KIT))

from config import segredo  # noqa: E402

from voz import provedor  # noqa: E402

API = "https://api.elevenlabs.io"
GENERO = {"masculino": "male", "feminino": "female"}
IDADE = {"jovem": "young", "adulto": "middle_aged", "maduro": "old"}
KOKORO = [("pm_alex", "masculina, adulta"), ("pm_santa", "masculina, grave"), ("pf_dora", "feminina")]
PADRAO_SAIDA = _KIT.parent / "canal" / "testes-de-voz"


def slug(txt):
    txt = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", txt.lower()).strip("-")[:40] or "voz"


def _get(caminho, **params):
    import requests

    r = requests.get(API + caminho, params=params, headers={"xi-api-key": segredo("elevenlabs")}, timeout=60)
    if r.status_code != 200:
        raise SystemExit(f"ElevenLabs HTTP {r.status_code} em {caminho}: {r.text[:200]}")
    return r.json()


def escolhe_conta(genero, idade, jeito, n):
    """As n vozes da conta que mais batem com gênero, idade e o jeito pedido (palavras soltas)."""
    vozes = _get("/v1/voices")["voices"]
    g, i = GENERO.get(genero), IDADE.get(idade)
    palavras = [p for p in slug(jeito or "").split("-") if len(p) > 2]

    def nota(v):
        lab = {k: str(x).lower() for k, x in (v.get("labels") or {}).items()}
        texto = " ".join([v.get("name", ""), v.get("description") or "", *lab.values()]).lower()
        pontos = (3 if g and lab.get("gender") == g else 0) + (2 if i and lab.get("age", "").replace("-", "_") == i else 0)
        pontos += sum(1 for p in palavras if p in texto)
        return pontos

    vozes = [v for v in vozes if not g or (v.get("labels") or {}).get("gender", g) == g]
    return sorted(vozes, key=nota, reverse=True)[:n]


def grava_elevenlabs(frase, vozes, saida, seco):
    custo = len(frase) * len(vozes)
    print(f"Plano: {len(vozes)} amostras x {len(frase)} caracteres = ~{custo} créditos da ElevenLabs.")
    resultado = []
    for k, v in enumerate(vozes, 1):
        lab = v.get("labels") or {}
        desc = ", ".join(x for x in (lab.get("gender"), lab.get("age"), lab.get("accent"), lab.get("descriptive")
                                     or lab.get("description"), lab.get("use_case")) if x)
        arq = saida / f"{k}_{slug(v['name'])}.mp3"
        print(f"{k}. {v['name']} ({desc}) voice_id={v['voice_id']}")
        if not seco:
            provedor("elevenlabs").sintetizar(frase, v["voice_id"], arq)
            print(f"   -> {arq}")
        resultado.append({"n": k, "nome": v["name"], "voice_id": v["voice_id"], "descricao": desc, "arquivo": str(arq)})
    return resultado


def grava_kokoro(frase, saida, seco):
    print("Plano: 3 amostras no Kokoro, no seu computador, sem custo.")
    resultado = []
    for k, (voz, desc) in enumerate(KOKORO, 1):
        arq = saida / f"{k}_kokoro-{voz}.mp3"
        print(f"{k}. {voz} ({desc})")
        if not seco:
            provedor("kokoro").sintetizar(frase, voz, arq)
            print(f"   -> {arq}")
        resultado.append({"n": k, "nome": voz, "voice_id": voz, "descricao": desc, "arquivo": str(arq)})
    return resultado


GEMINI = {"masculino": [("Charon", "grave e informativa"), ("Orus", "firme"), ("Puck", "animada")],
          "feminino": [("Kore", "firme"), ("Aoede", "leve"), ("Leda", "jovem")]}


def grava_gemini(frase, genero, saida, seco):
    print("Plano: 3 amostras na voz do Google (Gemini TTS), plano grátis, sem custo.")
    vozes = GEMINI.get(genero) or [GEMINI["masculino"][0], GEMINI["feminino"][0], GEMINI["masculino"][2]]
    from voz.pronuncia import aplicar
    resultado = []
    for k, (voz, desc) in enumerate(vozes, 1):
        arq = saida / f"{k}_gemini-{voz}.mp3"
        print(f"{k}. {voz} ({desc})")
        if not seco:
            provedor("gemini").sintetizar(aplicar(frase), voz, arq)
            print(f"   -> {arq}")
        resultado.append({"n": k, "nome": voz, "voice_id": voz, "descricao": desc, "arquivo": str(arq)})
    return resultado


def biblioteca_br(genero, idade, n, saida, seco):
    """Vozes brasileiras da biblioteca pública: baixa a prévia de cada uma (não gasta crédito)."""
    import requests

    params = {"language": "pt", "accent": "brazilian", "page_size": n, "sort": "trending"}
    if GENERO.get(genero):
        params["gender"] = GENERO[genero]
    if IDADE.get(idade):
        params["age"] = IDADE[idade]
    vozes = _get("/v1/shared-voices", **params).get("voices", [])
    if not vozes:
        print("Nenhuma voz brasileira encontrada com esses filtros. Tente sem --idade.")
        return []
    resultado = []
    for k, v in enumerate(vozes, 1):
        arq = saida / f"br{k}_{slug(v.get('name', 'voz'))}.mp3"
        print(f"{k}. {v.get('name')} ({v.get('gender')}, {v.get('age')}, {v.get('use_case') or v.get('category')}): "
              f"{(v.get('description') or '')[:90]}")
        print(f"   para usar: python -m voz.amostras --adicionar {v.get('public_owner_id')} {v.get('voice_id')} "
              f"\"{v.get('name')}\"")
        if not seco and v.get("preview_url"):
            r = requests.get(v["preview_url"], timeout=60)
            if r.ok:
                arq.write_bytes(r.content)
                print(f"   prévia -> {arq}")
        resultado.append({"n": k, "nome": v.get("name"), "voice_id": v.get("voice_id"),
                          "dono": v.get("public_owner_id"), "arquivo": str(arq)})
    print("Atenção: confira na página da voz se ela permite uso comercial no seu plano.")
    return resultado


def adicionar(dono, voice_id, nome):
    import requests

    r = requests.post(f"{API}/v1/voices/add/{dono}/{voice_id}", json={"new_name": nome},
                      headers={"xi-api-key": segredo("elevenlabs")}, timeout=60)
    if r.status_code != 200:
        raise SystemExit(f"Não deu pra adicionar (HTTP {r.status_code}): {r.text[:200]}")
    novo = r.json().get("voice_id", voice_id)
    print(f"VOZ_ADICIONADA: {nome} voice_id={novo}. Ponha esse id em voz.elevenlabs.voz no config.json.")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--frase", help="a frase de teste, no jeito do canal")
    ap.add_argument("--provedor", choices=["elevenlabs", "gemini", "kokoro"], default="elevenlabs")
    ap.add_argument("--genero", choices=list(GENERO))
    ap.add_argument("--idade", choices=list(IDADE))
    ap.add_argument("--jeito", default="", help="palavras do jeito da voz, ex.: 'animado energético conversa'")
    ap.add_argument("-n", type=int, default=3)
    ap.add_argument("--br", action="store_true", help="vozes brasileiras da biblioteca pública (prévias grátis)")
    ap.add_argument("--adicionar", nargs=3, metavar=("DONO", "VOICE_ID", "NOME"))
    ap.add_argument("--saida", type=Path, default=PADRAO_SAIDA)
    ap.add_argument("--seco", action="store_true", help="mostra o plano e o custo, sem gravar")
    a = ap.parse_args()

    if a.adicionar:
        return adicionar(*a.adicionar)
    a.saida.mkdir(parents=True, exist_ok=True)
    if a.br:
        resultado = biblioteca_br(a.genero, a.idade, max(a.n, 5), a.saida, a.seco)
    else:
        if not a.frase:
            ap.error("--frase é obrigatória (a frase de teste no jeito do canal)")
        if a.provedor == "kokoro":
            resultado = grava_kokoro(a.frase, a.saida, a.seco)
        elif a.provedor == "gemini":
            resultado = grava_gemini(a.frase, a.genero, a.saida, a.seco)
        else:
            resultado = grava_elevenlabs(a.frase, escolhe_conta(a.genero, a.idade, a.jeito, a.n), a.saida, a.seco)
    if resultado and not a.seco:
        (a.saida / "amostras.json").write_text(json.dumps(resultado, indent=1, ensure_ascii=False), encoding="utf-8")
        print("AMOSTRAS_OK:", a.saida)


if __name__ == "__main__":
    main()
