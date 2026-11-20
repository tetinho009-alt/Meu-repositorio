# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""python -m estudo: transcreve uma referência e tira o raio-x (ver estudo/__init__.py).

Saídas para o painel: linhas "ETAPA: ..." com o andamento e "ESTUDO_OK <id>" no fim.
Códigos: 0 deu certo, 2 a rede bloqueou ou pediu login, 3 falta instalar o estudo, 1 outro erro.
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import estudo as E  # noqa: E402
from estudo import nicho, raiox  # noqa: E402


def estudar(entrada, idioma="auto", modelo="auto", forcar_whisper=False, apagar_entrada=False, cfg=None,
            avisar=None):
    from estudo.transcrever import transcrever
    avisar = avisar or (lambda t: print(f"ETAPA: {t}", flush=True))
    base, plataforma, metodo, meta, segmentos, extra = transcrever(entrada, idioma, avisar, modelo, forcar_whisper, cfg)
    if plataforma == "local":
        base = "arquivo_" + E.slug(Path(entrada).stem)
    ident = E.slug(base, 80).replace("-", "_") if plataforma != "local" else base
    ident = re.sub(r"[^a-z0-9_-]", "", ident.lower()) or "video"
    avisar("Montando o raio-x")
    dur = meta.get("duration") or extra.get("duracao_audio")
    dados = {"id": ident, "quando": datetime.now().isoformat(timespec="seconds"), "plataforma": plataforma,
             "fonte": meta.get("webpage_url") or meta.get("arquivo_nome") or str(entrada), "metodo": metodo,
             **({"extra": extra} if extra else {}), "metadados": meta, "duracao_s": dur, "segmentos": segmentos}
    # Folha de quadros antes do molde: o molde.md manda a IA olhar o visual (estudo/quadros.py).
    from estudo import quadros
    E.pasta_estudo(ident).mkdir(parents=True, exist_ok=True)
    quadros.gerar(entrada, E.pasta_estudo(ident), dur, cfg, avisar)
    E.analisar_e_gravar(dados)
    if apagar_entrada and plataforma == "local":
        try:
            Path(entrada).unlink()
        except OSError:
            pass
    return ident, dados


def main():
    for fluxo in (sys.stdout, sys.stderr):
        fluxo.reconfigure(encoding="utf-8", line_buffering=True)
    ap = argparse.ArgumentParser(prog="python -m estudo", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada", nargs="*", help="link público ou caminho do vídeo; com --nicho, os ids dos estudos")
    ap.add_argument("--idioma", default="auto", help="idioma da fala (auto, pt, en, es...)")
    ap.add_argument("--modelo", default="auto", help="Whisper: auto (placa se der, senão small), small ou large-v3-turbo")
    ap.add_argument("--whisper", action="store_true", help="YouTube: ignora a legenda e ouve o áudio")
    ap.add_argument("--apagar-entrada", action="store_true", help="apaga o arquivo local depois de estudar (painel)")
    ap.add_argument("--buscar", metavar="ASSUNTO", help="lista vídeos públicos do YouTube sobre o assunto")
    ap.add_argument("--curtos", action="store_true", help="na busca, só vídeos de até 4 minutos")
    ap.add_argument("--listar", action="store_true", help="mostra os estudos guardados")
    ap.add_argument("--nicho", action="store_true", help="compara os estudos dados (ou todos) e mostra o padrão")
    a = ap.parse_args()

    import config  # noqa: F401  confere a licença do kit antes de qualquer coisa
    cfg = getattr(config, "CFG", {})

    if a.listar:
        for x in E.listar():
            print(f"{x['id']}: {x['titulo']} | {x.get('duracao_s')} s | 1a fala {x.get('primeira_fala_s')} s | "
                  f"{x.get('viradas_por_min')} viradas/min | {x.get('esqueleto')}")
        return 0
    if a.nicho:
        ids = a.entrada or [x["id"] for x in E.listar()]
        r = nicho.comparar(ids)
        if not r["ok"]:
            print(f"ERRO: {r['msg']}\nO QUE FAZER: estude mais vídeos do mesmo nicho (python -m estudo <link>).")
            return 1
        print(f"Nicho com {r['n']} vídeos.\nO que se repete:\n  - " + "\n  - ".join(r["padroes"]))
        if r["varia"]:
            print("O que varia:\n  - " + "\n  - ".join(r["varia"]))
        if r["contraste"]:
            print("Os mais vistos (descrição, não causa):\n  - " + "\n  - ".join(r["contraste"]))
        print("Molde do nicho: " + raiox.molde_curto(r["molde"]))
        return 0
    try:
        if a.buscar:
            from estudo.transcrever import buscar_youtube
            print(json.dumps(buscar_youtube(a.buscar, curtos=a.curtos), ensure_ascii=False, indent=1))
            return 0
        if len(a.entrada) != 1:
            ap.error("passe um link ou um arquivo")
        ident, d = estudar(a.entrada[0], a.idioma, a.modelo, a.whisper, a.apagar_entrada, cfg)
    except ImportError as e:
        receita = "tempos" if e.name == "faster_whisper" else "estudo"
        print(f"ERRO: falta instalar o estudo de vídeos ({e.name}).\n"
              f"O QUE FAZER: rode `python instalar_recursos.py {receita}` a partir de kit/ (o painel faz sozinho).")
        return 3
    except Exception as e:  # noqa: BLE001
        from estudo.transcrever import Bloqueado, ErroEstudo
        if isinstance(e, Bloqueado):
            print(f"ERRO: {e}\nO QUE FAZER: baixe o vídeo pelo app (salvar ou baixar) e estude o arquivo. "
                  "O estudo não usa login nem cookies.")
            return 2
        if isinstance(e, ErroEstudo):
            print(f"ERRO: {e}\nO QUE FAZER: {e.fazer}")
            return 1
        raise
    r = d["raiox"]
    print(f"ESTUDO_OK {ident}")
    if not r.get("sem_fala"):
        g = r["gancho"]
        print(f"  {d['metadados'].get('title') or ident} | {r['duracao_s']} s | via {d['metodo']}")
        print(f"  gancho: 1a fala {g['primeira_fala_s']} s ({g['tipo_nome']}) | {r['viradas']['por_min']} viradas/min | "
              f"{len(r['perguntas'])} perguntas | {r['palavras_por_min']} palavras/min")
        if d.get("molde"):
            print(f"  esqueleto: {d['molde']['esqueleto']}")
    else:
        print("  O vídeo não tem fala: o raio-x da fala fica vazio.")
    print(f"  {E.pasta_estudo(ident)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
