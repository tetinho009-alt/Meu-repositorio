<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Motion graphics e tipografia cinética

## O que é

O texto é o vídeo: cada palavra entra no instante em que a voz fala, com tamanho, cor e brilho, num fundo escuro
que nunca para (luzes da marca, partículas, câmera que aproxima). Serve para uma ideia forte, um conselho, uma
quebra de crença ("não é o prompt, é a pergunta").

## Duração e formato

Vertical 1080x1920, 60 fps. **20 a 40 s.** Sem legenda embaixo: o texto grande já é a legenda.

## Estrutura do roteiro

| Tempo | Batida |
|---|---|
| 0 a 2 s | A frase que derruba uma crença, já em movimento |
| 2 a 25 s | 4 a 7 frases curtas, uma por bloco, cada uma com 1 palavra-chave em destaque |
| fim | A frase-resumo e uma pergunta aberta ou "segue pra ver a parte 2" |

Uma frase por bloco, de 3 a 8 palavras na tela. A voz pode falar mais que a tela, nunca menos.

## Como é feito no kit

Motor de cartelas, estilo `tipografia` (`kit/cartelas/modelos/tipografia.json`). Blocos `gancho`, `texto` e `fim`.
`"legenda": false` (já é o padrão do estilo). Com placa de vídeo, `"blur": 4` dá o borrão de movimento.

## O que precisa

| | Grátis | Recomendado (pago) |
|---|---|---|
| IA | Antigravity ou Codex | Claude Code (Pro) |
| Voz | Gemini TTS | ElevenLabs |
| Visual | o motor de cartelas | igual |

## Dificuldade

**Baixa.** O trabalho é escrever frases curtas que valem um print.

## Exemplo de 10 s

`exemplos/estilos/tipografia/exemplo.mp4` (no painel: tela Estilos), feito no caminho grátis. Para refazer ou usar como ponto de partida: `exemplos/estilos/README.md`.
