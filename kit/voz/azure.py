# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Azure AI Speech (TTS neural). Uso comercial coberto pelos termos do Azure na conta do próprio cliente.

Chave: AZURE_SPEECH_KEY; região em voz.azure.regiao. Com o SDK (`pip install azure-cognitiveservices-speech`) os
tempos de palavra vêm do próprio serviço (WordBoundary); sem o SDK usa a API REST e os tempos saem do alinhar.py.
Ritmo e tom: use SSML (<prosody rate="-5%">) no texto, não acelere o áudio depois.
"""
from pathlib import Path
from xml.sax.saxutils import escape

import requests

from config import segredo

from .base import ErroVoz, ResultadoVoz, Voz


class Azure(Voz):
    nome = "azure"
    precisa_chave = "azure_speech"

    def __init__(self):
        super().__init__()
        self.chave = segredo("azure_speech")
        self.regiao = self.cfg.get("regiao", "brazilsouth")

    def ssml(self, texto, voz):
        if texto.lstrip().startswith("<speak"):
            return texto
        return (f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="pt-BR">'
                f'<voice name="{voz}">{escape(texto)}</voice></speak>')

    def sintetizar(self, texto, voz, saida):
        voz = voz or self.cfg.get("voz", "pt-BR-AntonioNeural")
        saida = Path(saida)
        try:
            import azure.cognitiveservices.speech as sdk  # noqa: F401
            return self._sdk(texto, voz, saida)
        except ImportError:
            return self._rest(texto, voz, saida)

    def _rest(self, texto, voz, saida):
        url = f"https://{self.regiao}.tts.speech.microsoft.com/cognitiveservices/v1"
        r = requests.post(url, data=self.ssml(texto, voz).encode("utf-8"), timeout=300, headers={
            "Ocp-Apim-Subscription-Key": self.chave, "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-48khz-192kbitrate-mono-mp3", "User-Agent": "maquina-series-kit"})
        if r.status_code != 200:
            raise ErroVoz(f"Azure HTTP {r.status_code}: {r.text[:300]}")
        self.para_mp3(r.content, saida, entrada_raw=["-f", "mp3", "-i", "-"])
        return ResultadoVoz(saida, None, self.nome, voz)

    def _sdk(self, texto, voz, saida):
        import azure.cognitiveservices.speech as sdk

        conf = sdk.SpeechConfig(subscription=self.chave, region=self.regiao)
        conf.set_speech_synthesis_output_format(sdk.SpeechSynthesisOutputFormat.Audio48Khz192KBitRateMonoMp3)
        tmp = saida.with_suffix(".azure.mp3")
        sint = sdk.SpeechSynthesizer(speech_config=conf, audio_config=sdk.audio.AudioOutputConfig(filename=str(tmp)))
        palavras = []

        def limite(ev):
            if ev.boundary_type == sdk.SpeechSynthesisBoundaryType.Word:
                ini = ev.audio_offset / 1e7
                palavras.append((ev.text, ini, ini + ev.duration.total_seconds()))

        sint.synthesis_word_boundary.connect(limite)
        res = sint.speak_ssml_async(self.ssml(texto, voz)).get()
        if res.reason != sdk.ResultReason.SynthesizingAudioCompleted:
            raise ErroVoz(f"Azure: {res.reason} {getattr(res, 'cancellation_details', '')}")
        del sint
        self.para_mp3(tmp, saida)
        tmp.unlink(missing_ok=True)
        return ResultadoVoz(saida, palavras or None, self.nome, voz)
