# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Apuração REAL da parte anterior, animada, para abrir a parte seguinte logo depois do gancho.

Lê a apuração gerada pelo placar (`placar/placar.py --so <slug> --detalhe apuracao.json`) e renderiza ~6,5 s:
a tela racha, cada lado enche na proporção dos votos, os números sobem e o carimbo do vencedor. Com --comentarios,
comentários reais passam embaixo (só o texto, sem @, sem emoji): use só com texto que não identifica ninguém e
confira a lista antes (metodo/comunidade-e-votos.md, "Dados de pessoas"). Som feito por código. Com menos votos que o mínimo (10), mostra só a opção que
venceu, sem número: placar com 4 votos vira piada nos comentários.

Uso:
    python apuracao_video.py <apuracao.json> --saida apuracao.mp4 [--comentarios] [--cpu]
    python apuracao_video.py <apuracao.json> --saida apuracao.mp4 --inserir-em parte2.mp4 --apos 2.4

--inserir-em/--apos: emenda a apuração dentro do vídeo da parte seguinte, depois do gancho (o segundo em que o
gancho termina). Gera <parte2>_com_apuracao.mp4. Planeje no roteiro uma pausa da narração nesse ponto.
Nunca edite o número à mão: se a apuração estiver errada, corrija a fonte e gere de novo.
"""
import argparse
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(KIT))

import skia  # noqa: E402

from config import CFG, ffmpeg, ffprobe  # noqa: E402

FPS = int(CFG["render"]["fps"])  # o mesmo do episódio: 60 na GPU, 30 na CPU
from maquina import som as S  # noqa: E402
from maquina import tela as T  # noqa: E402
from maquina.desenho import CX_SEGURO, H, W, caber, cheio, ease, fonte, texto_c  # noqa: E402
from maquina.motor import escolher_encoder, renderizar  # noqa: E402

DUR = 6.6


def carrega(arq):
    d = json.loads(Path(arq).read_text(encoding="utf-8"))
    if "votos" not in d:  # arquivo com vários episódios: exige um só
        raise SystemExit("gere a apuração de um episódio só: placar.py --so <slug> --detalhe apuracao.json")
    if not d.get("votos") or len(d["opcoes"]) != 2:
        raise SystemExit("apuração sem votos lidos (ou com mais de 2 opções): nada a mostrar")
    return d


def quadro_comentarios(c, t, coms):
    """Duas faixas de comentários reais passando embaixo das barras."""
    if not coms:
        return
    f = fonte("texto", 30)
    k = ease((t - 0.6) / 0.5)
    for pista in range(2):
        lista = coms[pista::2] or coms
        larg = [f.measureText(x) + 44 for x in lista]
        ciclo = sum(larg) + 24 * len(lista)
        x = W - ((t * (170 + 40 * pista) + pista * 260) % ciclo)
        y = 1300 + pista * 68
        for txt, lg in zip(lista * 3, larg * 3):
            if x > W:
                break
            if x + lg > 0:
                c.drawRoundRect(skia.Rect.MakeXYWH(x, y, lg, 54), 27, 27, cheio((26, 22, 40), 220 * k))
                c.drawString(txt, x + 22, y + 37, f, cheio((230, 226, 255), 255 * k))
            x += lg + 24


def quadro_sem_numero(c, t, d, vence):
    """Menos votos que o mínimo: só a escolha da galera, sem número."""
    c.drawRect(skia.Rect.MakeWH(W, H), cheio((6, 6, 10)))
    k = ease((t - 0.3) / 0.5)
    texto_c(c, f"PARTE {d['parte']} · RESULTADO", CX_SEGURO, 520, fonte("titulo", 40), (200, 196, 230), 255 * k)
    texto_c(c, d["pergunta"].upper(), CX_SEGURO, 620, caber("titulo", d["pergunta"].upper(), 70, 760, minimo=34),
            (255, 255, 255), 255 * k)
    kv = ease((t - 1.2) / 0.35)
    if kv > 0:
        rot = next(o["rotulo"] for o in d["opcoes"] if o["id"] == vence).upper()
        quique = 1 + 0.25 * math.exp(-(t - 1.2) * 7) * math.cos((t - 1.2) * 20)
        c.save()
        c.translate(CX_SEGURO, 900)
        c.rotate(-4)
        c.scale(kv * quique, kv * quique)
        texto_c(c, "A GALERA ESCOLHEU", 0, -40, fonte("titulo", 52), (255, 255, 255))
        texto_c(c, rot, 0, 70, caber("titulo", rot, 120, 720, minimo=50), T.OPCOES[int(vence) - 1])
        c.restore()
    kp = ease((t - 2.6) / 0.3)
    texto_c(c, f"A PARTE {d['parte'] + 1} COMEÇA AGORA", CX_SEGURO, 1228, fonte("titulo", 52), (255, 255, 255), 255 * kp)


def trilha(saida, oficial):
    m = S.Mesa(DUR)
    m.poe(0.0, S.impacto(), ganho=0.7)
    if oficial:
        m.poe(0.5, S.subida(2.6, 50, 180))
        m.poe(4.4, S.impacto())
        m.poe(5.4, S.estalo(), ganho=0.8)
    else:
        m.poe(1.2, S.impacto())
        m.poe(2.6, S.estalo(), ganho=0.8)
    m.gravar(saida)
    norm = Path(saida).with_name("apuracao_norm.wav")
    subprocess.run([sys.executable, str(KIT / "masterizar.py"), str(saida), "-o", str(norm)], check=True,
                   capture_output=True)
    return norm


def duracao(video):
    r = subprocess.run([ffprobe(), "-v", "error", "-show_entries", "format=duration", "-of", "json", str(video)],
                       capture_output=True, text=True, check=True)
    return float(json.loads(r.stdout)["format"]["duration"])


def inserir(clipe, video, apos, cpu=False):
    """Vídeo = [0, apos] + apuração + [apos, fim], com o áudio junto (reencoda uma vez)."""
    destino = Path(video).with_name(Path(video).stem + "_com_apuracao.mp4")
    enc = escolher_encoder(cpu)
    filtro = (f"[0:v]trim=0:{apos},setpts=PTS-STARTPTS,fps={FPS},format=yuv420p[v0];"
              f"[0:a]atrim=0:{apos},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo[a0];"
              f"[1:v]fps={FPS},format=yuv420p,setpts=PTS-STARTPTS[v1];"
              f"[1:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a1];"
              f"[0:v]trim={apos},setpts=PTS-STARTPTS,fps={FPS},format=yuv420p[v2];"
              f"[0:a]atrim={apos},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo[a2];"
              f"[v0][a0][v1][a1][v2][a2]concat=n=3:v=1:a=1[v][a]")
    venc = ["-c:v", "libx264", "-crf", "18", "-preset", "medium"] if enc == "libx264" else ["-c:v", enc, "-b:v", "8M"]
    subprocess.run([ffmpeg(), "-v", "error", "-y", "-i", str(video), "-i", str(clipe), "-filter_complex", filtro,
                    "-map", "[v]", "-map", "[a]", *venc, "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", str(destino)], check=True)
    return destino


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("apuracao")
    ap.add_argument("--saida", required=True)
    ap.add_argument("--minimo", type=int, default=10)
    ap.add_argument("--comentarios", action="store_true", help="faixa com comentários reais (só texto, sem @)")
    ap.add_argument("--inserir-em")
    ap.add_argument("--apos", type=float, help="segundo em que o gancho termina (com --inserir-em)")
    ap.add_argument("--cpu", action="store_true")
    a = ap.parse_args()
    if a.inserir_em and a.apos is None:
        ap.error("--inserir-em precisa de --apos")
    d = carrega(a.apuracao)
    ids = [o["id"] for o in d["opcoes"]]
    votos = [int(d["votos"].get(k, 0)) for k in ids]
    total = sum(votos)
    oficial = total >= a.minimo
    vence = ids[0] if votos[0] > votos[1] else ids[1] if votos[1] > votos[0] else None
    if not vence:
        raise SystemExit("empate ou nenhum voto: decida o desempate no roteiro (ver comandos/apurar-votos.md)")
    rotulos = [o["rotulo"] for o in d["opcoes"]]
    coms = [x for x in d.get("comentarios_tela", []) if all(ord(ch) < 0x2000 for ch in x) and len(x) <= 60][:24]
    coms = coms if a.comentarios else []

    def quadro(c, t):
        if oficial:
            T.apuracao(c, t, 0.0, d["pergunta"], rotulos, votos, parte=int(d["parte"]))
            quadro_comentarios(c, t, coms)
        else:
            quadro_sem_numero(c, t, d, vence)

    saida = Path(a.saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        audio = trilha(Path(tmp) / "apuracao.wav", oficial)
        renderizar(quadro, DUR, saida, audio=audio, cpu=a.cpu, marcos=[0.4, 2.0, 4.8, 6.2],
                   pasta_quadros=saida.parent / "quadros_apuracao")
    print(f"APURACAO_OK {saida} ({'oficial' if oficial else 'sem número'}: {dict(zip(rotulos, votos))})")
    if a.inserir_em:
        print(f"EMENDADO {inserir(saida, a.inserir_em, a.apos, a.cpu)} (duração {duracao(a.inserir_em) + DUR:.1f} s)")


if __name__ == "__main__":
    main()
