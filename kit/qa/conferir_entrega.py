# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Conferência antes de entregar: 8 quadros do vídeo pronto numa folha, para a IA olhar antes de dizer "pronto".

Uso (da pasta kit/):
    python qa/conferir_entrega.py <video.mp4>

Grava <pasta do vídeo>/conferencia.jpg e imprime as 3 perguntas que a IA responde olhando a folha. Se alguma der
"não", o vídeo não vai para o usuário: a IA corrige e roda de novo. Veio de um comprador que recebeu vídeos em todos
os estilos só com fundo e texto (17/11/2026): as travas de cada motor pegam o grosso, e esta é a última olhada.
"""
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
if str(KIT) not in sys.path:
    sys.path.insert(0, str(KIT))

N = 8
PERGUNTAS = [
    "aparece um personagem (boneco, mascote ou o objeto com olhos) em pelo menos 6 dos 8 quadros?",
    "a imagem muda de um quadro para o outro (cenário, objeto, pose), e não é o mesmo fundo com texto trocando?",
    "dá para entender do que é o vídeo só olhando, sem som?",
]


def duracao(video):
    from config import ffprobe
    r = subprocess.run([ffprobe(), "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def folha(video):
    from config import ffmpeg
    dur = duracao(video)
    if dur <= 1:
        raise SystemExit(f"ERRO: o vídeo {video} está vazio ou não abriu.\nO QUE FAZER: rode o render de novo.")
    saida = Path(video).parent / "conferencia.jpg"
    # margem proporcional: num vídeo de 5 s, cortar 2,5 s do fim tirava justamente a resposta
    ini, fim = min(0.5, dur * 0.05), dur - min(2.5, dur * 0.12)
    filtro = f"trim=start={ini}:end={fim},setpts=PTS-STARTPTS,fps={N}/{fim - ini:.3f},scale=240:-2,tile={N // 2}x2:padding=6:color=white"
    r = subprocess.run([ffmpeg(), "-v", "error", "-y", "-i", str(video), "-vf", filtro, "-frames:v", "1", "-q:v", "3",
                        str(saida)], capture_output=True, text=True)
    if r.returncode or not saida.is_file():
        raise SystemExit(f"ERRO: não consegui tirar os quadros do vídeo ({r.stderr.strip()[:200]}).\n"
                         "O QUE FAZER: confira se o arquivo abre e rode de novo.")
    return saida


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    arq = folha(sys.argv[1])
    print(f"CONFERENCIA {arq}")
    print("OBRIGATÓRIO ANTES DE ENTREGAR: abra a folha acima e responda, olhando os quadros:")
    for i, p in enumerate(PERGUNTAS, 1):
        print(f"  {i}. {p}")
    print("Se alguma resposta for não, NÃO entregue: diga ao usuário em uma linha o que faltou, corrija (personagem, "
          "cenário ou animação) e rode de novo. Se as três forem sim, mostre a folha ao usuário junto com o vídeo.")


if __name__ == "__main__":
    main()
