<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Quiz e escolha

## O que é

Perguntas com 2 a 4 opções e uma contagem de 3 segundos para a pessoa responder na cabeça antes da revelação.
Variante "escolha": duas opções sem resposta certa ("você aguentaria 1 mês sem celular ou sem doce?"), que vira
conversa nos comentários.

## Duração e formato

Vertical 1080x1920. **30 a 55 s.** Três a cinco perguntas por vídeo, cada uma com uns 10 s.

## Estrutura do roteiro

| Tempo | Batida |
|---|---|
| 0 a 3 s | O desafio ("só 1 em cada 10 acerta as três") |
| por pergunta | a pergunta falada, as opções na tela, contagem de 3 s, a revelação com o porquê em meia frase |
| fim | "Quantas você acertou?" (pergunta aberta, não isca) |

Fato do quiz com fonte, como no top 5. Na variante escolha, nada de opção que ofenda um grupo.

## Como é feito no kit

Motor de cartelas, estilo `quiz` (`kit/cartelas/modelos/quiz.json`): bloco `quiz` (com `opcoes`, `certa` a partir
de 0 e `contagem`) seguido de um bloco `revela`. Na escolha sem resposta certa, use `"certa": -1`.

## O que precisa

| | Grátis | Recomendado (pago) |
|---|---|---|
| IA | Antigravity ou Codex | Claude Code (Pro) |
| Voz | Gemini TTS ou Kokoro | ElevenLabs |
| Visual | o motor de cartelas | igual |

## Dificuldade

**Baixa.**

## Exemplo de 10 s

`exemplos/estilos/quiz/exemplo.mp4` (no painel: tela Estilos), feito no caminho grátis. Para refazer ou usar como ponto de partida: `exemplos/estilos/README.md`.
