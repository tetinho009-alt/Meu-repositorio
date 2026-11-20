# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Voz do Google (Gemini TTS) pela API do Google AI Studio: a voz grátis de melhor qualidade em pt-BR.

Modelo padrão: gemini-3.8-flash-tts (plano grátis na documentação oficial de 06/11/2026: entrada e saída "Free of
charge"; no plano grátis o Google usa o conteúdo enviado para melhorar os produtos dele). O Google não reivindica a
propriedade do áudio gerado, e os termos pedem uso profissional ou de negócio, que é o caso de um canal.
Os limites do plano grátis são por dia e por minuto, mostrados no painel do AI Studio: o kit espera e tenta de novo.

Chave: GEMINI_API_KEY (crie em aistudio.google.com, botão "Get API key"; pela janela: `python chave.py --qual gemini`).
Vozes prontas: Kore, Puck, Charon, Fenrir, Aoede, Orus, Leda, Zephyr e outras (30 no total). O idioma é detectado
pelo texto; o `estilo` (voz.gemini.estilo) diz o jeito de falar sem ser lido em voz alta.
Não devolve tempo de palavra: o alinhar.py (Whisper) faz isso depois.
"""
import base64
import time
from pathlib import Path

import requests

from config import segredo

from .base import ErroVoz, ResultadoVoz, Voz

URL = "https://generativelanguage.googleapis.com/v1beta/interactions"


def _acha_audio(no):
    """Procura o último bloco de áudio (base64) na resposta, onde quer que a API o coloque."""
    achado = None
    if isinstance(no, dict):
        if no.get("type") == "audio" and isinstance(no.get("data"), str):
            achado = no["data"]
        for v in no.values():
            achado = _acha_audio(v) or achado
    elif isinstance(no, list):
        for v in no:
            achado = _acha_audio(v) or achado
    return achado


class Gemini(Voz):
    nome = "gemini"
    rotulo = "Gemini TTS (Google AI Studio)"
    precisa_chave = "GEMINI_API_KEY"
    _ultimo = 0.0

    def __init__(self):
        super().__init__()
        self.chave = segredo("GEMINI_API_KEY", obrigatorio=False)
        if not self.chave:
            raise ErroVoz("falta a chave do Google AI Studio. Rode `python chave.py --qual gemini` (a partir de kit/) e "
                          "cole a chave na janela que abrir. É grátis: aistudio.google.com, botão Get API key.")

    def sintetizar(self, texto, voz, saida):
        voz = voz or self.cfg.get("voz", "Charon")
        modelo = self.cfg.get("modelo", "gemini-3.8-flash-tts")
        estilo = self.cfg.get("estilo", "narrador brasileiro, sotaque do Brasil, voz firme e natural, ritmo de conversa")
        corpo = {
            "model": modelo,
            "input": [{"type": "user_input", "content": [{
                "type": "text", "text": texto,
                "annotations": [{"type": "speech_metadata", "style": estilo}]}]}],
            "response_format": {"type": "audio"},
            "generation_config": {"speech_config": [{"voice": voz}]},
        }
        dados = self._pedido(corpo)
        b64 = _acha_audio(dados)
        if not b64:
            raise ErroVoz("o Google respondeu sem áudio. Confira o nome da voz (voz.gemini.voz) e tente de novo.")
        saida = Path(saida)
        self.para_mp3(base64.b64decode(b64), saida, entrada_raw=["-i", "-"])
        return ResultadoVoz(saida, None, self.nome, voz)

    def _pedido(self, corpo):
        intervalo = float(self.cfg.get("intervalo_min_s", 7))
        espera = float(self.cfg.get("espera_base_s", 20))
        for tentativa in range(int(self.cfg.get("max_tentativas", 6))):
            falta = Gemini._ultimo + intervalo - time.time()
            if falta > 0:
                time.sleep(falta)
            Gemini._ultimo = time.time()
            try:
                r = requests.post(URL, json=corpo, timeout=300,
                                  headers={"x-goog-api-key": self.chave, "Content-Type": "application/json"})
            except requests.RequestException as e:
                if tentativa >= 2:
                    raise ErroVoz(f"sem conexão com o Google ({type(e).__name__}). Confira a internet e rode de novo.") from e
                time.sleep(espera)
                continue
            if r.status_code == 200:
                return r.json()
            if r.status_code in (429, 500, 503):
                print(f"Google ocupado ou limite do plano grátis (HTTP {r.status_code}); esperando "
                      f"{espera:.0f} s antes de tentar de novo", flush=True)
                time.sleep(espera)
                espera = min(espera * 2, 300)
                continue
            if r.status_code in (401, 403):
                raise ErroVoz("o Google recusou a chave. Crie outra em aistudio.google.com e rode "
                              "`python chave.py --qual gemini`.")
            raise ErroVoz(f"Google HTTP {r.status_code}: {r.text[:300]}")
        raise ErroVoz("o limite do plano grátis do Google acabou por agora. Tente de novo mais tarde (o limite é por "
                      "dia) ou use a voz local: --provedor kokoro.")
