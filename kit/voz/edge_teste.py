# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""edge-tts: NÃO COMERCIAL / SÓ TESTE.

Usa um serviço da Microsoft sem licença comercial clara. Serve para rascunho de ritmo, nunca para vídeo publicado.
Bloqueado por padrão: só roda com voz.permitir_nao_comercial = true no config.json. Para produção use Azure (o
mesmo motor de vozes, com contrato), ElevenLabs ou uma voz local (Kokoro/Piper).
"""
import asyncio
from pathlib import Path

from .base import ErroVoz, ResultadoVoz, Voz


class EdgeTeste(Voz):
    nome = "edge"
    rotulo = "edge-tts"
    comercial = False

    def sintetizar(self, texto, voz, saida):
        try:
            import edge_tts
        except ImportError as e:
            raise ErroVoz("edge-tts não instalado (pip install edge-tts)") from e
        print("AVISO: edge-tts é só para teste; não publique este áudio.", flush=True)
        voz = voz or self.cfg.get("voz", "pt-BR-AntonioNeural")
        saida = Path(saida)
        tmp = saida.with_suffix(".edge.mp3")
        palavras = []

        async def roda():
            com = edge_tts.Communicate(texto, voz, rate=self.cfg.get("taxa", "+0%"), boundary="WordBoundary")
            with open(tmp, "wb") as f:
                async for ch in com.stream():
                    if ch["type"] == "audio":
                        f.write(ch["data"])
                    elif ch["type"] == "WordBoundary":
                        ini = ch["offset"] / 1e7
                        palavras.append((ch["text"], ini, ini + ch["duration"] / 1e7))

        asyncio.run(roda())
        self.para_mp3(tmp, saida)
        tmp.unlink(missing_ok=True)
        return ResultadoVoz(saida, palavras or None, self.nome, voz)
