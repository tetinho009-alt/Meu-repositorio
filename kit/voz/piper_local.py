# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Piper local (rápido, roda bem em CPU). Precisa do executável `piper` (pip install piper-tts) e de um modelo
.onnx + .onnx.json de voz pt-BR (ex.: pt_BR-faber-medium, em huggingface.co/rhasspy/piper-voices).

ATENÇÃO À LICENÇA: cada voz do Piper tem a licença do conjunto de dados dela (está no MODEL_CARD ao lado do
modelo). Confira antes de usar comercialmente.
Não devolve tempo de palavra: rode alinhar.py depois.
"""
import shutil
import subprocess
import tempfile
from pathlib import Path

from config import caminho

from .base import ErroVoz, ResultadoVoz, Voz


class Piper(Voz):
    nome = "piper"

    def sintetizar(self, texto, voz, saida):
        modelo = voz or self.cfg.get("modelo")
        if not modelo:
            raise ErroVoz("Piper: informe o modelo .onnx (--voz caminho/pt_BR-faber-medium.onnx ou voz.piper.modelo)")
        modelo = caminho(modelo)
        if not modelo.is_file():
            raise ErroVoz(f"Piper: modelo não encontrado: {modelo}")
        exe = shutil.which(self.cfg.get("executavel", "piper")) or self.cfg.get("executavel")
        if not exe or not Path(exe).exists() and not shutil.which(exe):
            raise ErroVoz("Piper: executável não encontrado (pip install piper-tts)")
        with tempfile.TemporaryDirectory() as tmp:
            wav = Path(tmp) / "piper.wav"
            r = subprocess.run([exe, "--model", str(modelo), "--output_file", str(wav)], input=texto.encode("utf-8"),
                               capture_output=True)
            if r.returncode or not wav.is_file():
                raise ErroVoz(f"Piper falhou: {r.stderr.decode('utf-8', 'replace')[-500:]}")
            self.para_mp3(wav, saida)
        return ResultadoVoz(Path(saida), None, self.nome, modelo.stem)
