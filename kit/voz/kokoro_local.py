# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Kokoro-82M local (Apache-2.0), vozes pt-BR: pm_alex, pm_santa (masculinas), pf_dora (feminina).

Roda na GPU se houver CUDA, senão na CPU. O modelo (~330 MB) baixa sozinho do Hugging Face na primeira vez, ou
aponte voz.kokoro.pasta_modelo para uma pasta com config.json + kokoro-v1_0.pth (+ voices/). Para pt-BR o Kokoro
usa o espeak-ng (instale pelo gerenciador do sistema, ver INSTALAR.md).
Não devolve tempo de palavra em pt-BR: rode alinhar.py depois.
"""
from pathlib import Path

import numpy as np

from config import caminho

from .base import ErroVoz, ResultadoVoz, Voz

REPO = "hexgrad/Kokoro-82M"


_ESPEAK_SISTEMA = [  # (biblioteca, pasta de dados) do espeak-ng instalado no sistema
    (r"C:\Program Files\eSpeak NG\libespeak-ng.dll", r"C:\Program Files\eSpeak NG\espeak-ng-data"),
    ("/usr/lib/x86_64-linux-gnu/libespeak-ng.so.1", "/usr/lib/x86_64-linux-gnu/espeak-ng-data"),
    ("/usr/lib/aarch64-linux-gnu/libespeak-ng.so.1", "/usr/lib/aarch64-linux-gnu/espeak-ng-data"),
    ("/opt/homebrew/lib/libespeak-ng.dylib", "/opt/homebrew/share/espeak-ng-data"),
    ("/usr/local/lib/libespeak-ng.dylib", "/usr/local/share/espeak-ng-data"),
]


def _garante_espeak(idioma="pt-br"):
    """O espeak-ng que vem no pacote Python às vezes não enxerga nenhum idioma (ex.: Windows com acento no caminho
    da pasta, como "Área de Trabalho"). Nesse caso usa o espeak-ng instalado no sistema."""
    from phonemizer.backend import EspeakBackend
    from phonemizer.backend.espeak.wrapper import EspeakWrapper

    try:
        EspeakBackend(idioma)
        return
    except RuntimeError:
        pass
    for lib, dados in _ESPEAK_SISTEMA:
        if Path(lib).is_file() and Path(dados).is_dir():
            EspeakWrapper.set_library(lib)
            EspeakWrapper.set_data_path(dados)
            try:
                EspeakBackend(idioma)
                print(f"Kokoro: usando o espeak-ng do sistema ({lib})", flush=True)
                return
            except RuntimeError:
                continue
    raise ErroVoz(f"espeak-ng sem o idioma {idioma}. Instale o espeak-ng do sistema (ver INSTALAR.md).")


class Kokoro(Voz):
    nome = "kokoro"

    def _pipeline(self):
        try:
            import torch
            from kokoro import KModel, KPipeline
            import misaki.espeak  # noqa: F401  (configura o espeak do pacote; a correção abaixo vem depois)
        except ImportError as e:
            raise ErroVoz("Kokoro não instalado: pip install -r requirements-opcional.txt (ver INSTALAR.md)") from e
        _garante_espeak()
        disp = "cuda" if torch.cuda.is_available() else "cpu"
        pasta_m = self.cfg.get("pasta_modelo")
        if pasta_m:
            p = caminho(pasta_m)
            modelo = KModel(repo_id=REPO, config=str(p / "config.json"), model=str(p / "kokoro-v1_0.pth"))
        else:
            modelo = KModel(repo_id=REPO)
        modelo = modelo.to(disp).eval()
        return KPipeline(lang_code=self.cfg.get("idioma", "p"), repo_id=REPO, model=modelo), disp

    def sintetizar(self, texto, voz, saida):
        voz = voz or self.cfg.get("voz", "pm_alex")
        pipe, disp = self._pipeline()
        pasta_m = self.cfg.get("pasta_modelo")
        arq_voz = caminho(pasta_m) / "voices" / f"{voz}.pt" if pasta_m else None
        ref = str(arq_voz) if arq_voz and arq_voz.is_file() else voz
        partes = []
        pausa = np.zeros(int(24000 * 0.35), dtype=np.float32)  # respiro curto entre linhas; a trilha decide o resto
        for r in pipe(texto, voice=ref, speed=float(self.cfg.get("velocidade", 1.0)), split_pattern=r"\n+"):
            if r.audio is not None:
                partes += [r.audio.detach().cpu().numpy().astype(np.float32), pausa]
        if not partes:
            raise ErroVoz("Kokoro não gerou áudio")
        pcm = np.concatenate(partes)
        self.para_mp3(pcm.tobytes(), Path(saida), entrada_raw=["-f", "f32le", "-ar", "24000", "-ac", "1", "-i", "-"])
        print(f"Kokoro: voz {voz} em {disp}", flush=True)
        return ResultadoVoz(Path(saida), None, self.nome, voz)
