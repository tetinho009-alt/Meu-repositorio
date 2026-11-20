<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Curiosidades e top 5

## O que é

Uma contagem regressiva de fatos curtos ("5 coisas que o seu corpo faz e você nunca reparou"), um por bloco, com o
número grande na tela. O número 1 é o mais forte e pode virar um teste rápido (quiz) para a pessoa responder antes
da revelação.

## Duração e formato

Vertical 1080x1920. **35 a 55 s.** Cada item com 5 a 8 s.

## Estrutura do roteiro

| Tempo | Batida |
|---|---|
| 0 a 3 s | A promessa, com a palavra que dá curiosidade em destaque ("...e você NUNCA reparou") |
| 3 a 40 s | Itens do 5 ao 2: o número, o fato em uma frase e, se precisar, meia frase de explicação |
| 40 a 50 s | O número 1: o mais surpreendente, de preferência como teste com 2 opções e contagem de 3 s |
| fim | Pergunta aberta ("qual desses você não sabia?") e o gancho da parte 2 no pacote |

**Todo fato com fonte**, listada em `fontes` no roteiro (vai na legenda). Número na tela em algarismo ("100 MIL"),
na voz por extenso ("cem mil").

## Como é feito no kit

Motor de cartelas, estilo `top5`. O exemplo pronto é um top 5 com teste no fim: `python cartelas/rodar.py
cartelas/exemplo`, a partir de `kit/`. Modelo em branco: `kit/cartelas/modelos/top5.json`.

## O que precisa

| | Grátis | Recomendado (pago) |
|---|---|---|
| IA | Antigravity ou Codex (pesquisa e roteiro) | Claude Code (Pro) |
| Voz | Gemini TTS ou Kokoro | ElevenLabs |
| Visual | o motor de cartelas, sem imagem nenhuma | igual |

## Dificuldade

**Baixa.** É o estilo mais rápido do kit e o melhor para o primeiro vídeo (`comandos/modo-rapido.md`).

## Exemplo de 10 s

`exemplos/estilos/top5/exemplo.mp4` (no painel: tela Estilos), feito no caminho grátis. Para refazer ou usar como ponto de partida: `exemplos/estilos/README.md`.
