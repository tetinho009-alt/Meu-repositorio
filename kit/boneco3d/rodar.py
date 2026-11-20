# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Personagem 3D (opcional): o mesmo boneco do 2D, montado em 3D no Blender e renderizado na GPU (EEVEE).

O 2D com rig continua sendo a base da série. O 3D serve para o que o 2D não faz: costas, perfil, giro de câmera e
plano com profundidade de verdade. O boneco 3D é gerado por código a partir do 2D (sem IA de 3D e sem modelo
baixado): corpo liso com sombra em 3 tons, contorno de nanquim, o rosto com os olhos e as bocas do próprio 2D e um
esqueleto para animar.

Uso (a partir da pasta do kit; precisa do Blender 5.2 LTS, o mesmo do explicativo 3D):
    python boneco3d/rodar.py <nome> --previa                 # monta o boneco e salva uma imagem de conferência
    python boneco3d/rodar.py <nome> --exemplo                # o personagem falando os 8 s iniciais da narração
    python boneco3d/rodar.py <nome> --clipe fala --tempos <tempos.json> --audio <voz.mp3> [--ate 12]
    python boneco3d/rodar.py <nome> --clipe teste|gag [--rapido]

Saída em <kit>/trabalho/boneco3d/<nome>/ (blend, quadros e mp4). O 3D só cobre o molde antigo de pessoa (cabelo
"longo" e roupa "moletom"). O estilo cápsula do kit (nico, lola) ainda não tem versão 3D: o gerador avisa e para.
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
KIT = AQUI.parent
sys.path.insert(0, str(KIT))
sys.path.insert(0, str(KIT / "explicativo3d"))

from ambiente3d import blender_ok, comando  # noqa: E402

AVISO_CAPSULA = ("ERRO: o 3D do personagem ainda não suporta o estilo cápsula (o molde de personagem do kit).\n"
                 "O QUE FAZER: faça a cena no rig 2D (kit/maquina), que tem todas as poses; costas e giro de câmera "
                 "ficam para quando o 3D ganhar o estilo cápsula.")


def estilo_suportado():
    """O gerador 3D foi feito para o molde antigo de pessoa; com o molde cápsula ele para com aviso claro."""
    from maquina import molde
    if getattr(molde, "ESTILO", "") == "capsula":
        raise SystemExit(AVISO_CAPSULA)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("nome", help="personagem em personagens/<nome>")
    ap.add_argument("--previa", action="store_true")
    ap.add_argument("--exemplo", action="store_true", help="fala da narração de exemplo do kit")
    ap.add_argument("--clipe", choices=["teste", "gag", "pose_gag", "fala"])
    ap.add_argument("--tempos")
    ap.add_argument("--audio")
    ap.add_argument("--ate", type=float)
    ap.add_argument("--rapido", action="store_true", help="8 amostras de antialias (prévia)")
    ap.add_argument("--saida")
    ap.add_argument("--gpu-device", type=int)
    a = ap.parse_args()
    estilo_suportado()
    exe, _ = blender_ok()
    if a.exemplo:
        a.clipe, a.ate = "fala", a.ate or 8.0
        a.tempos = a.tempos or str(KIT / "exemplo" / "audio" / "tempos.json")
        a.audio = a.audio or str(KIT / "exemplo" / "audio" / "narrador.mp3")
    if not (a.previa or a.clipe):
        ap.error("escolha --previa, --exemplo ou --clipe")
    t0 = time.perf_counter()
    if a.clipe:
        args = [a.nome, a.clipe]
        for chave, valor in (("--tempos", a.tempos), ("--audio", a.audio), ("--ate", a.ate), ("--saida", a.saida)):
            if valor:
                args += [chave, str(Path(valor).resolve()) if chave != "--ate" else valor]
        if a.rapido:
            args.append("--rapido")
        cmd = comando(exe, AQUI / "clipe.py", args, a.gpu_device)
    else:
        cmd = comando(exe, AQUI / "gerar.py", [a.nome, "--previa"], a.gpu_device)
    r = subprocess.run(cmd, cwd=str(KIT))
    if r.returncode:
        raise SystemExit("BONECO3D_FALHOU (veja a mensagem acima)")
    print(f"BONECO3D_OK em {time.perf_counter() - t0:.0f} s -> {KIT / 'trabalho' / 'boneco3d' / a.nome}")


if __name__ == "__main__":
    main()
