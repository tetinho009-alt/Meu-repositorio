# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Interface comum dos adaptadores de voz."""
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from config import CFG, ffmpeg


class ErroVoz(RuntimeError):
    pass


@dataclass
class ResultadoVoz:
    audio: Path
    palavras: list = field(default=None)   # [(palavra, ini, fim)] ou None
    provedor: str = ""
    voz: str = ""


class Voz:
    """Adaptador: `sintetizar(texto, voz, saida_mp3)` -> ResultadoVoz.

    Regra de gravação: a narração inteira numa geração só (timbre e ritmo contínuos); as pausas entre blocos são
    decididas na trilha, não no TTS. Nunca acelerar voz pronta com atempo: ajuste o ritmo na síntese.
    """
    nome = ""
    rotulo = ""               # nome para mensagens (padrão: nome)
    comercial = True          # False = serviço sem licença comercial clara (só teste)
    precisa_chave = None      # nome lógico do segredo (config.SEGREDOS) ou None

    def __init__(self):
        self.cfg = CFG["voz"].get(self.nome, {})
        if not self.comercial and not CFG["voz"].get("permitir_nao_comercial"):
            raise ErroVoz(f"{self.rotulo or self.nome}: só para teste, sem licença comercial; use Azure, Piper/Kokoro ou ElevenLabs. "
                          "(Para testar mesmo assim: voz.permitir_nao_comercial = true no config.json; nunca publique.)")

    def sintetizar(self, texto, voz, saida):
        raise NotImplementedError

    # utilitário comum: qualquer áudio -> mp3 48 kHz mono 192 kbps
    @staticmethod
    def para_mp3(origem, saida, entrada_raw=None):
        saida = Path(saida)
        saida.parent.mkdir(parents=True, exist_ok=True)
        cmd = [ffmpeg(), "-v", "error", "-y"]
        cmd += entrada_raw if entrada_raw else ["-i", str(origem)]
        cmd += ["-ar", "48000", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "192k", str(saida)]
        subprocess.run(cmd, check=True, input=origem if entrada_raw else None)
        return saida
