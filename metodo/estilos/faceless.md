<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Faceless narrado com imagens

## O que é

Uma narração sobre um assunto (mistério, lugar, objeto, curiosidade histórica) com imagens que trocam a cada 2 a
4 s, zoom lento em cada uma, texto curto e legenda. Ninguém aparece: "faceless" quer dizer sem rosto do dono do
canal.

## Duração e formato

Vertical 1080x1920. **45 a 80 s.**

## Estrutura do roteiro

| Tempo | Batida |
|---|---|
| 0 a 3 s | A imagem mais estranha + a frase que promete a explicação |
| 3 a 15 s | O contexto em duas frases |
| 15 s ao fim | 3 a 5 viradas ("só que..."), cada uma com imagem nova |
| fim | A revelação e uma pergunta aberta |

## Como é feito no kit

Motor de cartelas, estilo `faceless` (`kit/cartelas/modelos/faceless.json`): um bloco `imagem` por frase, com o
nome do arquivo da imagem na pasta do episódio. Imagem que falta aparece marcada na prévia e trava o render final.

## De onde vêm as imagens

| | Grátis | Recomendado (pago) |
|---|---|---|
| Imagens | fotos suas; bancos com licença de uso comercial sem crédito (Pexels, Pixabay: confira a licença de cada foto no dia); domínio público de verdade (acervos que dizem "domínio público" na página da obra) | gerador de imagem pago (ChatGPT com o Codex, ou a API de imagem do Google, perto de US$ 0,04 por imagem) |
| Voz | Gemini TTS ou Kokoro | ElevenLabs |
| IA | Antigravity ou Codex | Claude Code (Pro) |

Nunca use imagem de busca do Google sem licença, print de filme ou foto de pessoa real identificável sem
autorização.

## Dificuldade

**Baixa**, se as imagens existem. O trabalho é achar ou gerar imagens boas.

## Exemplo de 10 s

`exemplos/estilos/faceless/exemplo.mp4` (no painel: tela Estilos), feito no caminho grátis. Para refazer ou usar como ponto de partida: `exemplos/estilos/README.md`.
