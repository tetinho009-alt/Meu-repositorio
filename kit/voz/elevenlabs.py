# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""ElevenLabs pela API direta (endpoint with-timestamps: áudio + tempo de cada caractere).

Chave: variável de ambiente ELEVENLABS_API_KEY (nunca no código nem no config).
Ritmo (lição real: pedido em rajada dá 429 e cada nova tentativa prolonga o bloqueio):
- UM pedido por vez, inclusive entre processos (trava em arquivo na pasta de trabalho);
- intervalo mínimo entre pedidos (`voz.elevenlabs.intervalo_min_s`, guardado em arquivo: vale entre execuções);
- 429/5xx: espera exponencial com sorteio (respeita Retry-After), até `max_tentativas`; erro 4xx de outro tipo para.
Plano grátis do ElevenLabs não dá direito comercial: confira o seu plano e os termos de cada voz da biblioteca.
Pronúncia: antes do envio, os termos em inglês viram a grafia de `voz/pronuncia.json` (só no texto da voz; a legenda
segue o texto original, alinhada pelas palavras ouvidas). Desliga com `voz.elevenlabs.pronuncia: false`.
"""
import base64
import json
import os
import random
import re
import time
from contextlib import contextmanager
from pathlib import Path

from config import pasta, segredo

from .base import ErroVoz, ResultadoVoz, Voz

API = "https://api.elevenlabs.io/v1/text-to-speech/{voz}/with-timestamps"
PRONUNCIA = Path(__file__).with_name("pronuncia.json")


def falado(texto):
    """Troca os termos em inglês pela grafia que a voz pronuncia certo (base do kit + trocas do canal)."""
    from .pronuncia import aplicar
    return aplicar(texto)


@contextmanager
def _um_por_vez(arquivo, velho_s=1800):
    """Trava simples por arquivo: só um pedido ao ElevenLabs por vez nesta máquina."""
    while True:
        try:
            fd = os.open(arquivo, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            break
        except FileExistsError:
            try:
                if time.time() - os.path.getmtime(arquivo) > velho_s:  # trava esquecida por processo morto
                    os.remove(arquivo)
                    continue
            except OSError:
                pass
            print("ElevenLabs: outro pedido em andamento; esperando 10 s...", flush=True)
            time.sleep(10)
    try:
        yield
    finally:
        try:
            os.remove(arquivo)
        except OSError:
            pass


class ElevenLabs(Voz):
    nome = "elevenlabs"
    precisa_chave = "elevenlabs"

    def __init__(self):
        super().__init__()
        self.chave = segredo("elevenlabs")
        base = pasta("trabalho")
        self.trava = base / ".elevenlabs.trava"
        self.estado = base / ".elevenlabs_estado.json"

    def _espera_intervalo(self):
        minimo = float(self.cfg.get("intervalo_min_s", 20))
        try:
            ultimo = json.loads(self.estado.read_text(encoding="utf-8")).get("ultimo", 0)
        except (OSError, ValueError):
            ultimo = 0
        falta = ultimo + minimo - time.time()
        if falta > 0:
            print(f"ElevenLabs: respeitando intervalo mínimo, esperando {falta:.0f} s...", flush=True)
            time.sleep(falta)

    def _marca(self):
        self.estado.write_text(json.dumps({"ultimo": time.time()}), encoding="utf-8")

    def montar_pedido(self, texto, voz):
        voz = voz or self.cfg.get("voz")
        if not voz:
            raise ErroVoz("ElevenLabs: informe o voice_id (--voz) ou voz.elevenlabs.voz no config.json")
        if self.cfg.get("pronuncia", True):
            texto = falado(texto)
        modelo = self.cfg.get("modelo", "eleven_v3")
        corpo = {"text": texto, "model_id": modelo, "language_code": self.cfg.get("idioma", "pt")}
        ajuste = {}
        if self.cfg.get("estabilidade") is not None:
            est = float(self.cfg["estabilidade"])
            # O eleven_v3 só aceita 0 (criativo), 0,5 (natural) e 1 (robusto)
            ajuste["stability"] = min((0.0, 0.5, 1.0), key=lambda x: abs(x - est)) if "v3" in modelo else est
        if self.cfg.get("emocao") is not None and "v3" not in modelo:
            ajuste["style"] = float(self.cfg["emocao"])
        if ajuste:
            corpo["voice_settings"] = ajuste
        return dict(url=API.format(voz=voz), params={"output_format": self.cfg.get("formato", "mp3_44100_128")},
                    json=corpo)

    def sintetizar(self, texto, voz, saida):
        import requests

        pedido = self.montar_pedido(texto, voz)
        tentativas = int(self.cfg.get("max_tentativas", 6))
        base_s = float(self.cfg.get("espera_base_s", 30))
        with _um_por_vez(self.trava):
            for k in range(tentativas):
                self._espera_intervalo()
                r = requests.post(pedido["url"], params=pedido["params"], json=pedido["json"],
                                  headers={"xi-api-key": self.chave, "Accept": "application/json"}, timeout=300)
                self._marca()
                if r.status_code == 200:
                    break
                if r.status_code == 429 or r.status_code >= 500:
                    ra = r.headers.get("Retry-After")
                    espera = max(float(ra) if ra and ra.replace(".", "").isdigit() else 0, base_s * 2 ** k)
                    espera *= random.uniform(1.0, 1.3)
                    print(f"ElevenLabs: HTTP {r.status_code}; nova tentativa em {espera:.0f} s ({k + 1}/{tentativas})",
                          flush=True)
                    time.sleep(espera)
                    continue
                raise ErroVoz(f"ElevenLabs HTTP {r.status_code}: {r.text[:300]}")
            else:
                raise ErroVoz("ElevenLabs: limite de tentativas; espere alguns minutos antes de tentar de novo.")
        dados = r.json()
        saida = Path(saida)
        saida.parent.mkdir(parents=True, exist_ok=True)
        bruto = base64.b64decode(dados["audio_base64"])
        self.para_mp3(bruto, saida, entrada_raw=["-f", "mp3", "-i", "-"])
        al = dados.get("alignment") or dados.get("normalized_alignment")
        palavras = None
        if al:
            from maquina.alinhamento import palavras_de_caracteres
            palavras = palavras_de_caracteres(al["characters"], al["character_start_times_seconds"],
                                              al["character_end_times_seconds"])
        return ResultadoVoz(saida, palavras, self.nome, pedido["url"].split("/")[-2])
