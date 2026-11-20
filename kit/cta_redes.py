# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Gera uma versão do vídeo por rede escolhida, com o CTA certo nos últimos segundos.

O corpo do vídeo é o mesmo em todas; muda só a chamada final. Ela entra DEPOIS do voto, nunca junto: o último quadro
congela escurecido e desfocado por alguns segundos e o cartão da rede aparece por cima (não precisa renderizar de
novo). O áudio ganha o mesmo tempo com fade, sem cortar a narração.

    Instagram  SEGUE PRA VER A PARTE 2
    TikTok     SEGUE PRA NÃO PERDER A PARTE 2
    YouTube    SE INSCREVE PRA VER A PARTE 2
    Kwai       SEGUE PRA VER A PARTE 2

As redes saem das preferências do canal (prefs: redes.escolhidas; sem preferências, Instagram, TikTok e YouTube
Shorts). O YouTube longo (16:9) não sai aqui: é o filme da série (filme_longo.py, metodo/video-longo.md).

Uso:
    python cta_redes.py <video.mp4> [--parte 1] [--gancho "COMO O ESGOTO FUNCIONA"] [--segundos 2.6] [--saida PASTA]
                        [--redes instagram,tiktok,youtube_shorts,kwai]

--parte N   série: a chamada pede a parte N+1 (padrão: 1, então "PARTE 2").
--gancho    explicativo: troca "A PARTE N" pelo gancho do próximo vídeo ("SEGUE PRA VER COMO O ESGOTO FUNCIONA").
--cauda     NÃO RECOMENDADO (a Meta rebaixa vídeo com cauda). Desligada por padrão: o vídeo termina no card da rede.
            Com --cauda "TEXTO", entra depois do CTA um segundo cartão chamando para o SEU produto ou serviço;
            --cauda sem texto usa `cta.frase` do config.json. O jeito recomendado de falar do produto é uma vez, só na
            voz, no meio do vídeo (metodo/engajamento.md, seção 3).
            Série no estilo desenhado de clima sombrio ou melancólico nunca leva cauda (metodo/formato-serio.md).
Saída: <saida>/INSTAGRAM, TIKTOK, YOUTUBE, KWAI (só as escolhidas), cada uma com 0N_<nome>_<rede>.mp4 (padrão:
pasta do vídeo).
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import skia

KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(KIT))

from config import CFG, cor as cor_cfg, ffmpeg, ffprobe  # noqa: E402
from maquina.desenho import CX_SEGURO, LARG_SEGURA, H, W, caber, cheio, quebrar, texto_c  # noqa: E402

PADRAO = ("instagram", "tiktok", "youtube_shorts")
LONGO = "youtube_longo"
# rede -> (pasta do cta_redes, sufixo dos arquivos). O sufixo "youtube" é o mesmo de capa.py --redes.
VERTICAIS = {"instagram": ("INSTAGRAM", "ig"), "tiktok": ("TIKTOK", "tiktok"),
             "youtube_shorts": ("YOUTUBE", "youtube"), "kwai": ("KWAI", "kwai")}
# Cópia mínima de prefs/esquema.json (redes_detalhe), usada só quando as preferências não carregam.
DETALHE_PADRAO = {
    "instagram": {"rotulo": "Instagram (Reels)", "pasta": "IG", "cta": "SEGUE PRA VER {alvo}", "hashtags_max": 5,
                  "legenda_max": 2200},
    "tiktok": {"rotulo": "TikTok", "pasta": "TIKTOK", "cta": "SEGUE PRA NÃO PERDER {alvo}", "hashtags_max": 5,
               "legenda_max": 2200},
    "youtube_shorts": {"rotulo": "YouTube Shorts", "pasta": "YOUTUBE", "cta": "SE INSCREVE PRA VER {alvo}",
                       "hashtags_max": 3, "legenda_max": 5000},
    "youtube_longo": {"rotulo": "YouTube (vídeo longo 16:9)", "pasta": "YOUTUBE_LONGO",
                      "cta": "SE INSCREVE PRA VER {alvo}", "hashtags_max": 3, "legenda_max": 5000},
    "kwai": {"rotulo": "Kwai", "pasta": "KWAI", "cta": "SEGUE PRA VER {alvo}", "hashtags_max": 5, "legenda_max": 2000},
}


def detalhes():
    """{rede: detalhe} do esquema das preferências (ou a cópia mínima acima)."""
    try:
        from prefs import esquema
        return {**DETALHE_PADRAO, **esquema()["redes_detalhe"]}
    except Exception:  # noqa: BLE001
        return dict(DETALHE_PADRAO)


def escolhidas(ids=None):
    """[(id, detalhe)] na ordem do esquema. `ids`: lista ou texto "instagram,kwai"; vazio = preferências do canal."""
    det = detalhes()
    if isinstance(ids, str):
        ids = [x.strip().lower() for x in ids.split(",") if x.strip()]
    if not ids:
        try:
            from prefs import redes
            ids = [r for r, _d in redes()]
        except Exception:  # noqa: BLE001
            ids = list(PADRAO)
        ids = ids or list(PADRAO)
    fora = [r for r in ids if r not in det]
    if fora:
        raise SystemExit(f"ERRO: rede que não existe: {', '.join(fora)}\n"
                         f"O QUE FAZER: use uma ou mais destas, separadas por vírgula: {', '.join(det)}")
    return [(r, det[r]) for r in det if r in ids]


def redes_cta(ids=None):
    """((PASTA, sufixo, modelo do CTA), ...) das redes verticais escolhidas. O YouTube longo fica de fora."""
    return tuple((*VERTICAIS[r], d["cta"]) for r, d in escolhidas(ids) if r in VERTICAIS)


def aviso_longo(ids):
    """Linha em português para quando o YouTube longo está entre as redes."""
    if LONGO in [r for r, _d in escolhidas(ids)]:
        return ("YouTube longo: o filme em 16:9 não sai neste pacote. Quando a série tiver 3 partes ou mais, ele sai "
                "pelo filme_longo.py (passo a passo em metodo/video-longo.md).")
    return None


try:
    REDES = redes_cta()
except SystemExit:  # preferência inválida: segue com as 3 redes de sempre
    REDES = redes_cta(PADRAO)


def texto_cta(modelo, parte, gancho):
    alvo = gancho.upper() if gancho else f"A PARTE {parte + 1}"
    # Um pedido só, e nunca "reposta", "curte" ou "comenta X": as redes rebaixam isca de engajamento.
    return modelo.format(alvo=alvo)


def desenha_cta(texto, perfil, saida):
    """PNG transparente 1080x1920 com o cartão do CTA dentro da zona segura."""
    sup = skia.Surface.MakeRaster(skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kUnpremul_AlphaType))
    c = sup.getCanvas()
    c.clear(skia.Color4f(0, 0, 0, 0))
    larg = LARG_SEGURA - 40
    f = caber("titulo", texto, 92, larg - 80, minimo=48)
    linhas = quebrar(texto, f, larg - 80)
    alt_linha = f.getSize() * 1.12
    alto = 70 + alt_linha * len(linhas) + (70 if perfil else 20)
    y0 = H * 0.30
    r = skia.Rect.MakeXYWH(CX_SEGURO - larg / 2, y0, larg, alto)
    c.drawRoundRect(r.makeOffset(8, 10), 40, 40, cheio((0, 0, 0), 150))
    c.drawRoundRect(r, 40, 40, cheio(cor_cfg("destaque")))
    y = y0 + 40 + f.getSize()
    for ln in linhas:
        texto_c(c, ln, CX_SEGURO, y, f, (255, 255, 255))
        y += alt_linha
    if perfil:
        texto_c(c, perfil, CX_SEGURO, y + 20, caber("mono", perfil, 44, larg - 80, minimo=24), (255, 255, 255), 230)
    sup.makeImageSnapshot().save(str(saida), skia.kPNG)


def duracao(video):
    r = subprocess.run([ffprobe(), "-v", "error", "-show_entries", "format=duration", "-of", "json", str(video)],
                       capture_output=True, text=True, check=True)
    return float(json.loads(r.stdout)["format"]["duration"])


def video_rede(video, destino, texto, perfil=None, segundos=2.6):
    """Uma versão do vídeo com o CTA da rede: o último quadro congela escurecido e o cartão aparece por cima."""
    video, destino = Path(video), Path(destino)
    t0, s = duracao(video), segundos
    fim = t0 + s
    destino.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        png = Path(tmp) / "cta.png"
        desenha_cta(texto, perfil, png)
        filtro = (f"[0:v]tpad=stop_mode=clone:stop_duration={s:.3f},"
                  f"eq=brightness=-0.22:enable='gte(t,{t0:.3f})',boxblur=14:enable='gte(t,{t0:.3f})'[base];"
                  f"[1:v]format=rgba,fade=t=in:st={t0:.3f}:d=0.3:alpha=1[cta];"
                  f"[base][cta]overlay=0:0:enable='gte(t,{t0:.3f})'[v];"
                  f"[0:a]apad=pad_dur={s:.3f},afade=t=out:st={fim - 0.6:.3f}:d=0.6[a]")
        subprocess.run([ffmpeg(), "-v", "error", "-y", "-i", str(video), "-loop", "1", "-t", f"{fim:.3f}", "-i", str(png),
                        "-filter_complex", filtro, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18",
                        "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                        "-ac", "2", "-t", f"{fim:.3f}", "-movflags", "+faststart", str(destino)], check=True)
    return destino


def perfil_cfg(perfil=None):
    perfil = perfil or CFG.get("perfil")
    return perfil if perfil and perfil != "@seu_perfil" else None


def serie_seria():
    """Estilo desenhado com clima sombrio ou melancólico: o episódio termina no CTA da rede, sem cauda de produto."""
    if CFG.get("estilo") != "desenhado":
        return False
    from estilo_desenhado.estilo import carregar
    return carregar().get("respostas", {}).get("clima") in ("sombrio", "melancolico")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--parte", type=int, default=1)
    ap.add_argument("--gancho")
    ap.add_argument("--segundos", type=float, default=2.6)
    ap.add_argument("--perfil", default=CFG.get("perfil"))
    ap.add_argument("--saida")
    ap.add_argument("--cauda", nargs="?", const=CFG.get("cta", {}).get("frase") or "", default=None,
                    help="NÃO RECOMENDADO (a Meta rebaixa): cartão do seu produto depois do CTA. Desligada por padrão; "
                         "sem texto, usa cta.frase do config.json")
    ap.add_argument("--cauda-segundos", type=float, default=3.0)
    ap.add_argument("--redes", help="redes separadas por vírgula (padrão: as escolhidas nas preferências)")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if a.cauda and serie_seria():
        print("série de clima sério: sem cauda no fim do vídeo; a chamada do produto vai só na voz, no meio")
        a.cauda = None
    if a.cauda == "":
        print("--cauda sem texto e cta.frase vazia no config.json: o vídeo termina no card da rede, sem cauda")
        a.cauda = None
    if a.cauda:
        print("AVISO: cauda de produto não é recomendada (a Meta rebaixa). O jeito recomendado é falar do produto uma "
              "vez, só na voz, no meio do vídeo (metodo/engajamento.md, seção 3).")
    video = Path(a.video).resolve()
    saida = Path(a.saida) if a.saida else video.parent
    redes = redes_cta(a.redes) if a.redes else REDES
    if aviso_longo(a.redes):
        print(aviso_longo(a.redes))
    if not redes:
        raise SystemExit("ERRO: nenhuma rede vertical escolhida.\n"
                         "O QUE FAZER: marque Instagram, TikTok, YouTube Shorts ou Kwai nas preferências (ou use --redes).")
    for i, (pasta, sufixo, modelo) in enumerate(redes, 1):
        texto = texto_cta(modelo, a.parte, a.gancho)
        destino = video_rede(video, saida / pasta / f"{i:02d}_{video.stem}_{sufixo}.mp4", texto, perfil_cfg(a.perfil),
                             a.segundos)
        if a.cauda:
            # Cauda do produto: o mesmo truque do CTA aplicado de novo, depois dele (voto -> CTA da rede -> cauda).
            com_cauda = destino.with_name(destino.stem + "_cauda.mp4")
            video_rede(destino, com_cauda, a.cauda.upper(), perfil_cfg(a.perfil), a.cauda_segundos)
            com_cauda.replace(destino)
        print(f"{pasta:<9} {texto}  ->  {destino}")
    print("CTA_OK")


if __name__ == "__main__":
    main()
