# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Exemplo fora do mar (raio dentro de casa, 5 s) no Three.js, a partir da pasta do kit:

    python explicativo3d/web/exemplo_casa/rodar.py --stills   # 5 quadros-marco
    python explicativo3d/web/exemplo_casa/rodar.py            # IG, TIKTOK e YOUTUBE, capa e grade

Mostra o que todo episódio fora do mar precisa: cenário do assunto (sala em corte), fundo do assunto ("tempestade"
no episodio.json), personagens criados com mascote() e trilha com os efeitos nos marcos da fala. Para um episódio
novo, copie esta pasta e troque narrador.txt, episodio.json, cena.js e trilha.py. Rótulo que fica até o fim da fala:
use "FIM" no lugar da palavra final.
"""
import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
WEB = AQUI.parent
X3D = WEB.parent
KIT = X3D.parent
EXEMPLO = X3D / "exemplo"  # so a trilha vem do exemplo
sys.path.insert(0, str(KIT))
sys.path.insert(0, str(X3D / "motor"))

from config import CFG, pasta  # noqa: E402
from tempos import Tempos  # noqa: E402

PY = sys.executable
REDES = ("IG", "TIKTOK", "YOUTUBE")


def passo(nome, cmd):
    print(f"\n== {nome}", flush=True)
    t0 = time.perf_counter()
    r = subprocess.run([str(c) for c in cmd], cwd=str(KIT))
    if r.returncode:
        raise SystemExit(f"FALHOU em: {nome}")
    dt = time.perf_counter() - t0
    print(f"   ({dt:.1f} s)", flush=True)
    return dt


def montar_spec(ep, tp, trab):
    """spec.json do compor.py: legenda, rótulos e CTA marcados pelas palavras da narração."""
    q = tp.quando
    rotulos = [[nome, q(ini), (tp.fim + 0.4) if fim == "FIM" else q(fim) - 0.1, *estilo] for nome, ini, fim, *estilo in ep["rotulos"]]
    perfil = CFG.get("perfil", "")
    spec = {
        "quadros": "quadros",
        "etiquetas": "etiquetas.json",
        "audio": "audio/mix_norm.wav",
        "duracao": round(tp.fim + 0.4 + ep["cta_segundos"], 3),
        "gancho": ep["gancho"],
        "legenda": tp.legenda(ep.get("destaques", [])),
        "rotulos": rotulos,
        "cta": {"inicio": round(tp.fim + 0.4, 3), "perfil": "" if perfil in ("", "@seu_perfil") else perfil},
        "versoes": {rede: {"saida": f"{rede}/01_video.mp4", **ep["ctas"][rede]} for rede in REDES},
        "fundo": ep.get("fundo", "mar"),
        "fundo_cores": ep.get("fundo_cores"),
    }
    arq = trab / "spec.json"
    arq.write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
    return arq


def folha(pngs, saida, ep=None):
    from PIL import Image

    import compor as C
    larg = 270
    out = Image.new("RGB", (larg * len(pngs), larg * 16 // 9))
    bg = C.fundo((ep or {}).get("fundo", "mar"), (ep or {}).get("fundo_cores"))
    for i, p in enumerate(pngs):
        im = Image.alpha_composite(bg, Image.open(p).convert("RGBA").resize((C.W, C.H)))
        out.paste(im.convert("RGB").resize((larg, larg * 16 // 9)), (i * larg, 0))
    out.save(saida, quality=88)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--voz", help="provedor para narrar de novo: kokoro, piper, azure, elevenlabs")
    ap.add_argument("--voz-id", help="voz do provedor (padrão: a do config)")
    ap.add_argument("--stills", action="store_true", help="só os quadros-marco")
    ap.add_argument("--leve", action="store_true", help="navegador em metade da resolução (prévia)")
    ap.add_argument("--placa", choices=("software", "gpu"), default="software",
                    help="software = CPU (igual à nuvem sem placa); gpu = placa de vídeo, se houver")
    ap.add_argument("--chromium", help="caminho de um Chromium/Chrome do sistema (no lugar do do Playwright)")
    ap.add_argument("--cpu", action="store_true", help="encoder de vídeo na CPU (libx264)")
    ap.add_argument("--so-compor", action="store_true",
                    help="reaproveita os quadros já renderizados (mudou só texto, legenda ou CTA)")
    ap.add_argument("--trabalho", help="pasta de saída")
    a = ap.parse_args()

    t_inicio = time.perf_counter()
    ep = json.loads((AQUI / "episodio.json").read_text(encoding="utf-8"))
    trab = Path(a.trabalho) if a.trabalho else pasta("trabalho") / f"{ep['pasta']}_web"
    aud = trab / "audio"
    aud.mkdir(parents=True, exist_ok=True)

    if a.voz:
        extra = ["--voz", a.voz_id] if a.voz_id else []
        passo("voz", [PY, KIT / "narrar.py", AQUI / "narrador.txt", aud / "narrador.mp3", "--provedor", a.voz, *extra])
        palavras = aud / "narrador.palavras.json"
        modo = ["--modo", "provedor"] if palavras.is_file() else []
        passo("tempos de palavra", [PY, KIT / "alinhar.py", aud / "narrador.mp3", AQUI / "narrador.txt",
                                    aud / "tempos.json", *modo])
    elif not (a.so_compor and (aud / "tempos.json").is_file()):
        for arq in ("narrador.mp3", "tempos.json"):
            shutil.copy2(AQUI / "audio" / arq, aud / arq)
    tp = Tempos(aud / "tempos.json")
    # Trava da cena (fundo do assunto, cenário e personagem) antes de gastar o render: ver motor/trava_cena.py.
    import trava_cena
    trava_cena.conferir(ep, (AQUI / "narrador.txt").read_text(encoding="utf-8"), AQUI / "cena.js")

    cena = [PY, WEB / "render.py", AQUI / "cena.js", "--tempos", aud / "tempos.json", "--saida", trab,
            "--episodio", AQUI / "episodio.json", "--fps", CFG["render"]["fps"],
            "--largura", CFG["render"]["largura"], "--altura", CFG["render"]["altura"], "--placa", a.placa,
            *(["--leve"] if a.leve else []), *(["--chromium", a.chromium] if a.chromium else [])]
    if a.stills:
        q = tp.quando
        marcos = [0.3, q("entrar") + 0.3, q("casa") + 0.4, q("fiação") + 0.3, tp.fim + 0.6]
        passo("quadros-marco no navegador", cena + ["--stills", ",".join(f"{m:.2f}" for m in marcos)])
        pngs = sorted((trab / "stills").glob("still_*.png"))
        folha(pngs, trab / "folha_stills.jpg", ep)
        print(f"\nSTILLS_OK {trab / 'folha_stills.jpg'}")
        return

    passo("trilha", [PY, AQUI / "trilha.py", "--audio", aud])
    passo("masterização", [PY, KIT / "masterizar.py", aud / "mix.wav", "-o", aud / "mix_norm.wav"])
    if a.so_compor:
        if not (trab / "render.json").is_file():
            raise SystemExit("--so-compor precisa de um render anterior completo nesta pasta")
        t_render = None
    else:
        t_render = passo("cena no navegador (render)", cena)
    spec = montar_spec(ep, tp, trab)
    passo("composição das 3 versões", [PY, X3D / "motor" / "compor.py", spec, *(["--cpu"] if a.cpu else [])])
    for rede in REDES:
        passo(f"áudio do vídeo {rede}", [PY, KIT / "masterizar.py", "--verificar", trab / rede / "01_video.mp4"])
    passo("grade de QA", [PY, KIT / "qa_grade.py", trab / "IG" / "01_video.mp4", "--zona", "--saida", trab / "qa"])
    passo("capa", [PY, X3D / "motor" / "capa.py", trab / "quadros" / "q_0001.png", trab / "IG" / "capa.jpg",
                   *ep["capa"]])
    for rede in REDES[1:]:
        shutil.copy2(trab / "IG" / "capa.jpg", trab / rede / "capa.jpg")

    info = json.loads((trab / "render.json").read_text(encoding="utf-8"))
    print(f"\nRender: {info['quadros']} quadros em {info['segundos']} s = {info['s_por_quadro']} s/quadro "
          f"({info.get('placa', '?')})" + (f"; navegador com abertura e montagem: {t_render:.0f} s" if t_render else ""))
    print(f"Total: {time.perf_counter() - t_inicio:.0f} s")
    passo("conferência antes de entregar", [PY, KIT / "qa" / "conferir_entrega.py", trab / "IG" / "01_video.mp4"])
    print(f"EXEMPLO_OK {trab}")


if __name__ == "__main__":
    main()
