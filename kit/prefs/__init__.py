# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Preferências do canal: um arquivo só (`canal/preferencias.json`) que o painel, a IA e o kit leem.

- O esquema (`prefs/esquema.json`) tem cada campo com o valor recomendado, a explicação de uma linha e o nível
  (básico ou avançado). O arquivo do usuário guarda só o que ele mudou.
- `salvar()` valida tudo em português antes de gravar e espelha no `kit/config.json` o que os scripts do kit já
  usam (fps, qualidade, voz, @, cores), para o painel, o chat e o render ficarem sincronizados.
- Nada aqui guarda chave ou segredo: as chaves ficam no arquivo de segredos fora do kit (`chave.py`).

Uso:
    from prefs import carregar, salvar, validar, voltar_recomendado, esquema
    p = carregar()                       # {"canal": {"nome": ...}, "redes": {...}, ...}
    ok, erros, avisos = salvar({"render": {"fps": 30}})
"""
import json
import os
import re
from functools import lru_cache
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
ESTUDIO = KIT.parent
ARQ_ESQUEMA = Path(__file__).with_name("esquema.json")
ARQ = ESTUDIO / "canal" / "preferencias.json"
COR = re.compile(r"^#[0-9A-Fa-f]{6}$")
ARROBA = re.compile(r"^[a-z0-9._]{1,30}$")


@lru_cache(maxsize=1)
def esquema():
    return json.loads(ARQ_ESQUEMA.read_text(encoding="utf-8"))


def recomendados():
    return {s: {c: m["recomendado"] for c, m in sec["campos"].items()} for s, sec in esquema()["secoes"].items()}


def _do_usuario():
    try:
        return json.loads(ARQ.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def carregar():
    """Valores em vigor: o recomendado de cada campo, com o que o usuário mudou por cima."""
    valores = recomendados()
    for s, campos in _do_usuario().items():
        if s in valores and isinstance(campos, dict):
            for c, v in campos.items():
                if c in valores[s]:
                    valores[s][c] = v
    return valores


def _proibidas(texto):
    try:
        from qa.antes_do_render import ISCA, PROIBIDAS
    except Exception:  # noqa: BLE001
        return None
    m = PROIBIDAS.search(texto) or ISCA.search(texto)
    return m.group(0) if m else None


def validar(secao, campo, valor):
    """(ok, valor normalizado, mensagem). A mensagem diz em português o que está errado e como resolver."""
    sec = esquema()["secoes"].get(secao)
    if not sec or campo not in sec["campos"]:
        return False, valor, f"campo desconhecido: {secao}.{campo}"
    m = sec["campos"][campo]
    tipo, rot = m["tipo"], m["rotulo"]
    try:
        if tipo in ("texto", "texto_longo"):
            v = str(valor or "").strip()
            limite = m.get("max", 300 if tipo == "texto" else 1500)
            if len(v) > limite:
                return False, v, f"{rot}: no máximo {limite} letras (tem {len(v)})"
            if campo in ("assinatura", "cta_meio_frase") and _proibidas(v):
                return False, v, f"{rot}: '{_proibidas(v)}' faz a rede esconder o vídeo; troque por uma frase sem isso"
            return True, v, ""
        if tipo == "arroba":
            v = str(valor or "").strip().lstrip("@").lower()
            if v and not ARROBA.match(v):
                return False, v, f"{rot}: só letras sem acento, números, ponto e sublinhado, até 30 (sem espaço)"
            return True, v, ""
        if tipo == "escolha":
            opcoes = m["opcoes"]
            for o in opcoes:
                if str(o) == str(valor):
                    return True, o, ""
            return False, valor, f"{rot}: escolha uma destas opções: {', '.join(map(str, opcoes))}"
        if tipo == "multi":
            v = [x for x in (valor if isinstance(valor, list) else str(valor).split(",")) if str(x).strip()]
            v = [str(x).strip() for x in v]
            fora = [x for x in v if x not in m["opcoes"]]
            if fora:
                return False, v, f"{rot}: opção que não existe ({', '.join(fora)})"
            if not v:
                return False, v, f"{rot}: marque pelo menos uma"
            return True, v, ""
        if tipo == "numero":
            v = float(str(valor).replace(",", "."))
            if "min" in m and v < m["min"] or "max" in m and v > m["max"]:
                return False, v, f"{rot}: use um número entre {m.get('min')} e {m.get('max')}"
            return True, (int(v) if float(v).is_integer() and isinstance(m["recomendado"], int) else v), ""
        if tipo == "booleano":
            if isinstance(valor, str):
                valor = valor.strip().lower() in ("1", "sim", "true", "ligado", "on")
            return True, bool(valor), ""
        if tipo == "cor":
            v = str(valor).strip()
            if not COR.match(v):
                return False, v, f"{rot}: use uma cor no formato #RRGGBB (ex.: #FF6B4A)"
            return True, v.upper(), ""
        if tipo == "lista":
            v = valor if isinstance(valor, list) else [x for x in re.split(r"[\n,]", str(valor or ""))]
            v = [str(x).strip() for x in v if str(x).strip()]
            if any(len(x) > 200 for x in v):
                return False, v, f"{rot}: cada item com no máximo 200 letras"
            return True, v, ""
        if tipo == "imagem":
            v = str(valor or "").strip()
            if v and not (ESTUDIO / v).is_file():
                return False, v, f"{rot}: não achei a imagem '{v}' dentro da pasta do estúdio"
            return True, v, ""
    except (TypeError, ValueError):
        return False, valor, f"{rot}: valor inválido"
    return False, valor, f"{rot}: tipo de campo desconhecido"


def avisos(valores):
    """Combinações que funcionam, mas que o usuário precisa saber."""
    a = []
    if valores["render"]["modo_leve"] and valores["visual"]["motion_blur"]:
        a.append("modo leve ligado: o borrão de movimento fica desligado no render")
    if valores["render"]["gpu"] == "nao" and int(valores["render"]["fps"]) == 60:
        a.append("sem placa de vídeo, 60 fps deixa o render bem mais lento; 30 fps é o recomendado")
    if valores["canal"]["caminho"] == "gratis" and valores["voz"]["provedor"] == "elevenlabs":
        a.append("a ElevenLabs é paga: no caminho grátis use a voz do Google (gemini) ou a Kokoro")
    if valores["visual"]["motion_blur"] > 4:
        a.append("borrão acima de 4 deixa o render várias vezes mais lento")
    if "youtube_longo" in valores["redes"]["escolhidas"]:
        a.append("o vídeo longo do YouTube sai quando a série tem 3 partes ou mais (metodo/video-longo.md)")
    return a


def salvar(mudancas):
    """Valida e grava. Devolve (ok, erros, avisos). Nada é gravado se houver erro."""
    atual = _do_usuario()
    erros = []
    for s, campos in (mudancas or {}).items():
        for c, v in (campos or {}).items():
            ok, norm, msg = validar(s, c, v)
            if not ok:
                erros.append(msg)
            else:
                atual.setdefault(s, {})[c] = norm
    if erros:
        return False, erros, []
    ARQ.parent.mkdir(parents=True, exist_ok=True)
    tmp = ARQ.with_suffix(".tmp")
    tmp.write_text(json.dumps(atual, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    tmp.replace(ARQ)
    valores = carregar()
    espelhar_config(valores)
    return True, [], avisos(valores)


def voltar_recomendado(secao):
    atual = _do_usuario()
    atual.pop(secao, None)
    ARQ.parent.mkdir(parents=True, exist_ok=True)
    ARQ.write_text(json.dumps(atual, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    espelhar_config(carregar())
    return True


def redes():
    """[(id, detalhe)] das redes escolhidas, na ordem do esquema."""
    det = esquema()["redes_detalhe"]
    escolhidas = carregar()["redes"]["escolhidas"]
    return [(r, det[r]) for r in det if r in escolhidas]


OBRIGATORIOS = (("canal", "nome"), ("canal", "arroba"), ("canal", "nicho"), ("canal", "publico"))


def faltando():
    """Campos que precisam estar preenchidos antes do primeiro vídeo (para a barra de configuração)."""
    v, sec = carregar(), esquema()["secoes"]
    return [(s, c, sec[s]["campos"][c]["rotulo"]) for s, c in OBRIGATORIOS if not v[s][c]]


def espelhar_config(valores):
    """Grava no kit/config.json os campos que os scripts do kit leem (o resto do arquivo fica como está)."""
    arq = Path(os.environ.get("MAQUINA_CONFIG") or KIT / "config.json")
    try:
        cfg = json.loads(arq.read_text(encoding="utf-8")) if arq.is_file() else {}
    except ValueError:
        return False
    r, vz, cn = valores["render"], valores["voz"], valores["canal"]
    leve = bool(r["modo_leve"])
    cfg.setdefault("render", {}).update({
        "fps": 30 if leve else int(r["fps"]), "qualidade": int(r["qualidade"]), "teto_bitrate": r["teto_bitrate"],
        "gpu": r["gpu"], "motor_3d": r.get("motor_3d", "auto"), "escala_cpu": 0.5 if leve else 1.0})
    voz = cfg.setdefault("voz", {})
    voz["provedor"] = vz["provedor"]
    if vz["voz_id"]:
        voz.setdefault(vz["provedor"], {})["voz"] = vz["voz_id"]
    voz.setdefault("gemini", {})["estilo"] = vz["estilo_gemini"]
    voz.setdefault("kokoro", {})["velocidade"] = vz["velocidade_kokoro"]
    voz.setdefault("elevenlabs", {}).update({"estabilidade": vz["estabilidade"], "emocao": vz["emocao"]})
    if cn["arroba"]:
        cfg["perfil"] = "@" + cn["arroba"]
    else:
        cfg.pop("perfil", None)
    cfg.setdefault("cores", {})["destaque"] = cn["cor_destaque"]
    arq.write_text(json.dumps(cfg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return True


def para_ia():
    """Resumo em texto para a IA ler antes de cada episódio (o que mudou do recomendado)."""
    rec, v = recomendados(), carregar()
    linhas = []
    for s, campos in v.items():
        for c, val in campos.items():
            if val != rec[s][c]:
                linhas.append(f"- {s}.{c} = {json.dumps(val, ensure_ascii=False)}")
    return "\n".join(linhas) or "- tudo no recomendado"


if __name__ == "__main__":
    import sys
    for f in (sys.stdout,):
        try:
            f.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    print("Preferências do canal (o que mudou do recomendado):")
    print(para_ia())
    for a in avisos(carregar()):
        print("AVISO", a)
