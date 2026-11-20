# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Conquistas do canal: troféus por vídeos feitos e por views, com pontos.

Ficam em `canal/conquistas.json`. Troféu ganho nunca se perde (apagar vídeo ou corrigir número não tira). As views
vêm de `canal/metricas.json` (anotadas pelo usuário no painel, tela Métricas): conta o melhor vídeo numa rede, o
último número anotado de cada vídeo em cada rede.

Uso (a partir da pasta kit/):
    python conquistas.py            # troféus, pontos e o próximo marco

Para o painel e a IA:
    atualizar(n_videos, historico) -> {"lista", "pontos", "novas", "proximas", ...}  (grava as datas novas)
    marcar_vistas(ids) -> marca como já comemoradas
"""
import json
import sys
from datetime import datetime
from pathlib import Path

KIT = Path(__file__).resolve().parent
ARQ = KIT.parent / "canal" / "conquistas.json"

# Nível visual do troféu, do mais fácil ao mais raro.
NIVEIS = ("bronze", "prata", "ouro", "diamante", "lendario")

# (id, tipo, meta, nível, pontos, título, frase da conquista)
MARCOS = (
    ("video_1", "videos", 1, "bronze", 50, "Primeiro vídeo", "Fiz meu primeiro vídeo"),
    ("publicado_1", "publicados", 1, "bronze", 50, "No ar", "Postei e anotei os números do meu primeiro vídeo"),
    ("video_3", "videos", 3, "bronze", 75, "Pegou o ritmo", "Já são 3 vídeos feitos"),
    ("video_5", "videos", 5, "prata", 120, "Cinco no ar", "Cheguei a 5 vídeos feitos"),
    ("video_10", "videos", 10, "prata", 250, "Dezena", "10 vídeos feitos"),
    ("video_25", "videos", 25, "ouro", 500, "Maratona", "25 vídeos feitos"),
    ("video_50", "videos", 50, "ouro", 1000, "Fábrica de vídeos", "50 vídeos feitos"),
    ("video_100", "videos", 100, "diamante", 2500, "Centenário", "100 vídeos feitos"),
    ("views_1k", "views", 1000, "bronze", 100, "Mil views", "Um vídeo meu passou de 1 mil views"),
    ("views_5k", "views", 5000, "prata", 250, "5 mil views", "Um vídeo meu passou de 5 mil views"),
    ("views_10k", "views", 10000, "prata", 500, "10 mil views", "Um vídeo meu passou de 10 mil views"),
    ("views_20k", "views", 20000, "ouro", 800, "20 mil views", "Um vídeo meu passou de 20 mil views"),
    ("views_50k", "views", 50000, "ouro", 1500, "50 mil views", "Um vídeo meu passou de 50 mil views"),
    ("views_100k", "views", 100000, "diamante", 3000, "100 mil views", "Um vídeo meu passou de 100 mil views"),
    ("views_1m", "views", 1000000, "lendario", 10000, "1 milhão de views", "Um vídeo meu passou de 1 milhão de views"),
)
TIPOS = ("videos", "publicados", "views")


def _num(v):
    try:
        return float(str(v).replace(".", "").replace(",", ".")) if isinstance(v, str) else float(v)
    except (TypeError, ValueError):
        return 0.0


def numeros_do_canal(n_videos, historico):
    """Vídeos feitos, vídeos com número anotado e o melhor vídeo (views, nome, rede)."""
    ultimo = {}
    for r in historico or []:
        if not isinstance(r, dict):
            continue
        chave = (str(r.get("episodio") or ""), str(r.get("rede") or ""))
        v = _num((r.get("numeros") or {}).get("views"))
        if chave[0] and v > 0:
            ultimo[chave] = v  # o histórico está em ordem de anotação: o último vale
    melhor = max(ultimo.items(), key=lambda kv: kv[1], default=(("", ""), 0.0))
    return {
        "videos": max(0, int(n_videos or 0)),
        "publicados": len({ep for ep, _ in ultimo}),
        "views": int(melhor[1]),
        "melhor_video": melhor[0][0],
        "melhor_rede": melhor[0][1],
        "views_total": int(sum(ultimo.values())),
    }


def _ler():
    try:
        d = json.loads(ARQ.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def _gravar(d):
    ARQ.parent.mkdir(parents=True, exist_ok=True)
    tmp = ARQ.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    tmp.replace(ARQ)


def atualizar(n_videos, historico, gravar=True):
    """Confere os marcos, guarda a data dos que acabaram de ser ganhos e devolve o quadro completo."""
    n = numeros_do_canal(n_videos, historico)
    d = _ler()
    ganhas = d.get("ganhas") if isinstance(d.get("ganhas"), dict) else {}
    vistas = set(d.get("vistas") or [])
    agora = datetime.now().isoformat(timespec="minutes")
    mudou = False
    lista = []
    for mid, tipo, meta, nivel, pts, titulo, frase in MARCOS:
        if mid not in ganhas and n[tipo] >= meta:
            ganhas[mid] = {"data": agora, "valor": n[tipo],
                           **({"video": n["melhor_video"], "rede": n["melhor_rede"]} if tipo == "views" else {})}
            mudou = True
        g = ganhas.get(mid)
        lista.append({"id": mid, "tipo": tipo, "meta": meta, "nivel": nivel, "pontos": pts, "titulo": titulo,
                      "frase": frase, "ganha": bool(g), "data": (g or {}).get("data", ""),
                      "video": (g or {}).get("video", ""), "rede": (g or {}).get("rede", ""),
                      "atual": n[tipo], "nova": bool(g) and mid not in vistas})
    if mudou and gravar:
        d["ganhas"] = ganhas
        d.setdefault("vistas", [])
        _gravar(d)
    proximas = {}
    for tipo in TIPOS:
        falta = next((m for m in lista if m["tipo"] == tipo and not m["ganha"]), None)
        if falta:
            proximas[tipo] = {"id": falta["id"], "titulo": falta["titulo"], "meta": falta["meta"], "atual": n[tipo]}
    return {"lista": lista, "pontos": sum(m["pontos"] for m in lista if m["ganha"]),
            "ganhas": sum(1 for m in lista if m["ganha"]), "total": len(lista),
            "novas": [m["id"] for m in lista if m["nova"]], "proximas": proximas, "numeros": n}


def marcar_vistas(ids):
    """Marca conquistas como já comemoradas (o painel não mostra o parabéns de novo)."""
    validos = {m[0] for m in MARCOS}
    d = _ler()
    vistas = set(d.get("vistas") or [])
    novas = {str(i) for i in (ids or []) if str(i) in validos} - vistas
    if novas:
        d["vistas"] = sorted(vistas | novas)
        d.setdefault("ganhas", {})
        _gravar(d)
    return len(novas)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, str(KIT / "painel"))
    import dados
    q = dados.conquistas()
    print(f"{q['ganhas']} de {q['total']} troféus, {q['pontos']} pontos.")
    for m in q["lista"]:
        print(f"  [{'x' if m['ganha'] else ' '}] {m['titulo']} ({m['nivel']}, {m['pontos']} pontos)")
    for p in q["proximas"].values():
        print(f"Próximo: {p['titulo']} ({p['atual']} de {p['meta']}).")


if __name__ == "__main__":
    main()
