# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Constrói um personagem a partir do molde: um PNG transparente por parte + partes.json (posições, RIG e medidas).

Uso:
    python construir_boneco.py <nome> [--motor auto|vectorcraft|skia] [--saida PASTA]

Entrada: `personagens/<nome>/personagem.json` = {"descricao": "...", "molde": {cores e estilos do molde}}.
Motores:
- vectorcraft: arte no VectorCraft por CLI, sem janela (malha de volume + contorno de espessura variável) e salva
  também o `<nome>.vectorcraft` editável. É o padrão de qualidade do estúdio. Precisa do VectorCraft instalado.
- skia: desenha as mesmas partes em SVG pelo Skia, sem programa externo (degradê radial no lugar da malha e
  contorno de espessura fixa). Funciona em qualquer máquina, inclusive na nuvem.
- auto: VectorCraft se estiver instalado, senão Skia.
"""
import argparse
import json
import math
import re
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(KIT))

from config import ferramenta, pasta  # noqa: E402
from maquina import molde  # noqa: E402

ESCALA = 2.0          # pixels por unidade do mundo nos PNGs
PAD = 24.0            # folga em volta da parte (contorno e malha)
PASSO = 1400.0        # distância entre pranchetas no documento do VectorCraft

_TOK = re.compile(r"[MLCQHVAZ]|-?\d+(?:\.\d+)?", re.I)
_EIXOS = {"M": (0, 1), "L": (0, 1), "C": (0, 1, 0, 1, 0, 1), "Q": (0, 1, 0, 1), "H": (0,), "V": (1,),
          "A": (None, None, None, None, None, 0, 1), "Z": ()}


def _percorre(d, dx=0.0):
    """Desloca x por dx e devolve (d novo, bbox). Só comandos absolutos, como os do molde."""
    toks = _TOK.findall(d)
    out, xs, ys, i, cmd = [], [], [], 0, None
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t.upper()
            out.append(cmd)
            i += 1
            continue
        for e in _EIXOS[cmd]:
            v = float(toks[i])
            if e == 0:
                xs.append(v)
                v += dx
            elif e == 1:
                ys.append(v)
            out.append(f"{v:.1f}" if e is not None else toks[i])
            i += 1
    return " ".join(out), (min(xs), min(ys), max(xs), max(ys))


def bbox_parte(elems):
    x0 = y0 = 1e9
    x1 = y1 = -1e9
    for e in elems:
        _, (a, b, c, d) = _percorre(e["d"])
        x0, y0, x1, y1 = min(x0, a), min(y0, b), max(x1, c), max(y1, d)
    return x0 - PAD, y0 - PAD, x1 + PAD, y1 + PAD


# ---------------------------------------------------------------- motor VectorCraft

def _passos_vc(elems, dx):
    s = []
    for e in elems:
        d, _ = _percorre(e["d"], dx)
        if e["fill"]:
            if e["volume"]:
                # Base chapada por baixo: a malha aproxima a forma por dentro e deixaria a borda sem cor.
                s += [{"command": "path.create", "params": {"d": d}},
                      {"command": "paint.setFill", "params": {"color": e["fill"]}},
                      {"command": "paint.setStroke", "params": {"none": True}}]
            s += [{"command": "path.create", "params": {"d": d}},
                  {"command": "paint.setFill", "params": {"color": e["fill"]}},
                  {"command": "paint.setStroke", "params": {"none": True}}]
            if e["volume"]:
                s.append({"command": "object.mesh.create", "params": {"rows": 4, "cols": 4, "appearance": "center",
                                                                      "highlight": e["volume"]}})
            if e["opacidade"] < 1:
                s.append({"command": "transparency.set", "params": {"opacity": round(e["opacidade"] * 100)}})
        if e["contorno"]:
            s += [{"command": "path.create", "params": {"d": d}},
                  {"command": "paint.setFill", "params": {"none": True}},
                  {"command": "paint.setStroke", "params": {"color": molde.TINTA}},
                  {"command": "stroke.set", "params": {"weight": e["contorno"], "join": "round", "cap": "round"}}]
        if e["traco"]:
            s += [{"command": "path.create", "params": {"d": d}},
                  {"command": "paint.setFill", "params": {"none": True}},
                  {"command": "paint.setStroke", "params": {"color": e["traco"]}},
                  {"command": "stroke.set", "params": {"weight": e["peso"], "join": "round", "cap": "round",
                                                        "profile": e["perfil"] or "uniform"}}]
    return s


def construir_vectorcraft(nome, partes, destino, exe):
    passos, mapa = [], {}
    for k, (parte, elems) in enumerate(partes.items()):
        x0, y0, x1, y1 = bbox_parte(elems)
        dx = k * PASSO
        rect = dict(x=x0 + dx, y=y0, width=x1 - x0, height=y1 - y0)
        if k == 0:
            passos.append({"command": "file.new", "params": {"width": 400, "height": 400, "units": "Pixels",
                                                             "backgroundContents": "transparent", "name": nome}})
            passos.append({"command": "artboard.setProps", "params": {"index": 0, "name": parte, **rect}})
        else:
            passos.append({"command": "artboard.new", "params": {"name": parte, **rect}})
        passos += _passos_vc(elems, dx)
        mapa[parte] = dict(indice=k, x=x0, y=y0, w=x1 - x0, h=y1 - y0)
    passos.append({"command": "file.saveAs", "params": {"path": str(destino / f"{nome}.vectorcraft")}})
    passos.append({"command": "document.export", "params": {"path": str(destino / "partes" / "p.png"), "format": "png",
                                                             "useArtboards": True, "scale": ESCALA,
                                                             "background": "transparent"}})
    script = destino / "build.jsonl"
    script.write_text("\n".join(json.dumps(p, ensure_ascii=False) for p in passos), encoding="utf-8")
    r = subprocess.run([exe, "run", "--commands", str(script)], capture_output=True, text=True, encoding="utf-8")
    erros = [ln for ln in (r.stdout or "").splitlines() if '"error"' in ln]
    if r.returncode or erros:
        raise RuntimeError("VectorCraft falhou:\n" + ("\n".join(erros[:10]) or (r.stderr or "")[-2000:]))
    for f in sorted((destino / "partes").glob("p-*.png")):  # o exportador numera as pranchetas
        sufixo = f.stem[2:]
        alvo = next((p for p, m in mapa.items() if sufixo in (str(m["indice"] + 1), p)), None)
        if alvo:
            f.replace(destino / "partes" / f"{alvo}.png")
    script.unlink(missing_ok=True)
    return mapa


# ---------------------------------------------------------------- motor Skia (SVG)

def _hex(rgb):
    return "#%02X%02X%02X" % tuple(int(max(0, min(255, v))) for v in rgb)


def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _svg_parte(elems, x0, y0, w, h):
    defs, corpo = [], []
    for i, e in enumerate(elems):
        d = e["d"]
        if e["fill"]:
            op = f' fill-opacity="{e["opacidade"]:.2f}"' if e["opacidade"] < 1 else ""
            corpo.append(f'<path d="{d}" fill="{e["fill"]}"{op}/>')
            if e["volume"]:
                base = _rgb(e["fill"])
                k = e["volume"] / 100.0
                claro = _hex(tuple(v + (255 - v) * k * 0.9 for v in base))
                escuro = _hex(tuple(v * (1 - k * 0.55) for v in base))
                defs.append(f'<radialGradient id="g{i}" cx="0.42" cy="0.36" r="0.72">'
                            f'<stop offset="0" stop-color="{claro}"/><stop offset="0.55" stop-color="{e["fill"]}"/>'
                            f'<stop offset="1" stop-color="{escuro}"/></radialGradient>')
                corpo.append(f'<path d="{d}" fill="url(#g{i})"{op}/>')
        if e["contorno"]:
            corpo.append(f'<path d="{d}" fill="none" stroke="{molde.TINTA}" stroke-width="{e["contorno"]}" '
                         f'stroke-linejoin="round" stroke-linecap="round"/>')
        if e["traco"]:
            peso = e["peso"] * (0.8 if e["perfil"] in ("lens", "taperEnd") else 1.0)
            corpo.append(f'<path d="{d}" fill="none" stroke="{e["traco"]}" stroke-width="{peso:.1f}" '
                         f'stroke-linejoin="round" stroke-linecap="round"/>')
    pw, ph = math.ceil(w * ESCALA), math.ceil(h * ESCALA)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{pw}" height="{ph}" viewBox="{x0:.1f} {y0:.1f} {w:.1f} {h:.1f}">'
            f'<defs>{"".join(defs)}</defs>{"".join(corpo)}</svg>'), pw, ph


def construir_skia(nome, partes, destino):
    import skia

    mapa = {}
    for k, (parte, elems) in enumerate(partes.items()):
        x0, y0, x1, y1 = bbox_parte(elems)
        svg, pw, ph = _svg_parte(elems, x0, y0, x1 - x0, y1 - y0)
        dados = svg.encode("utf-8")
        dom = skia.SVGDOM.MakeFromStream(skia.MemoryStream(dados, True))
        if dom is None:
            raise RuntimeError(f"SVG inválido na parte {parte}")
        sup = skia.Surface.MakeRaster(skia.ImageInfo.Make(pw, ph, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType))
        c = sup.getCanvas()
        c.clear(skia.Color(0, 0, 0, 0))
        dom.setContainerSize(skia.Size(pw, ph))
        dom.render(c)
        sup.makeImageSnapshot().save(str(destino / "partes" / f"{parte}.png"))
        mapa[parte] = dict(indice=k, x=x0, y=y0, w=x1 - x0, h=y1 - y0)
    return mapa


# ---------------------------------------------------------------- principal

def construir(nome, motor="auto", saida=None):
    origem = pasta("personagens") / nome
    cfg = json.loads((origem / "personagem.json").read_text(encoding="utf-8"))
    destino = Path(saida) if saida else origem
    (destino / "partes").mkdir(parents=True, exist_ok=True)
    for velho in (destino / "partes").glob("*.png"):
        velho.unlink()
    partes = molde.montar(cfg.get("molde", {}))
    exe = ferramenta("vectorcraft")
    if motor == "auto":
        motor = "vectorcraft" if exe else "skia"
    if motor == "vectorcraft":
        if not exe:
            raise SystemExit("VectorCraft não encontrado (ferramentas.vectorcraft no config.json ou vectorcraft-cli no PATH).")
        mapa = construir_vectorcraft(nome, partes, destino, exe)
    else:
        mapa = construir_skia(nome, partes, destino)
    info = dict(nome=nome, motor=motor, escala=ESCALA, cx=molde.CX, chao=molde.CHAO, boca_y=molde.BOCA_Y,
                pose_base=cfg.get("pose_base", {}), partes=mapa,
                rig=[[p, pai, [round(v, 2) for v in piv]] for p, pai, piv in molde.RIG])
    (destino / "partes.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    faltam = [p for p in mapa if not (destino / "partes" / f"{p}.png").is_file()]
    if faltam:
        raise SystemExit(f"partes sem PNG: {faltam}")
    print(f"BONECO_OK {nome}: {len(mapa)} partes, motor {motor}, em {destino}")
    return destino


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("nome")
    ap.add_argument("--motor", default="auto", choices=["auto", "vectorcraft", "skia"])
    ap.add_argument("--saida", help="pasta de saída (padrão: a do personagem)")
    a = ap.parse_args()
    construir(a.nome, a.motor, a.saida)


if __name__ == "__main__":
    main()
