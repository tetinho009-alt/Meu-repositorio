<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Terror e mistério com voto

## O que é

Uma série de suspense em partes: algo que não devia acontecer acontece num lugar comum (condomínio, sítio, metrô),
e o público vota no que a personagem faz. O medo vem do clima e do "quase certo", nunca do sangue. É o formato de
origem do método: séries de terror animadas com voto da parte 2.

## Duração e formato

- Vertical 1080x1920, 60 fps com placa (30 na nuvem).
- **1:50 a 2:10** (clima mais sério: 2:00 a 2:30). Tempo a mais vem de mais viradas, nunca de fala esticada.

## Estrutura do roteiro

| Tempo | Batida |
|---|---|
| 0 a 2 s | Hora exata e ameaça já acontecendo, com texto grande que se entende sem som |
| até 3 s | Uma contradição ("a luz acendeu sozinha; ninguém mora lá faz dez anos") |
| até 15 s | A regra do lugar e a protagonista, apresentados pela história (sem plaquinha de nome) |
| perto dos 10 s (Parte 2 em diante) | O placar real da parte anterior, logo depois do gancho; nunca "PARTE N" nem placar antes |
| a cada 10 a 15 s | Um degrau: "Só que..." |
| a cada 2 a 4 s | Uma imagem nova |
| ~1:50 | A frase calma da ameaça |
| fim | Voto com duas saídas ruins, sem dica de qual é a certa, e uma semente da próxima parte |

## Como é feito no kit

`comandos/novo-video.md` (Formato 1), rig 2D com luz (`kit/maquina/cinema.py`) e, para clima sério, o estilo
desenhado (`metodo/formato-serio.md`, com as travas de pele, mãos e espaço em `kit/qa/`). Série nova:
`comandos/nova-serie.md`. Apuração: `comandos/apurar-votos.md` (vale o número no começo do comentário ou a palavra
da opção; nunca invente número).

## O que precisa

| | Grátis | Recomendado (pago) |
|---|---|---|
| IA | Antigravity ou Codex | Claude Code (Pro) |
| Voz | Gemini TTS com estilo "sussurrado, tenso" ou Kokoro | ElevenLabs, com as tags `[whispers]`, `[slowly]` |
| Visual | o kit | o kit |

## Dificuldade

**Média.** O clima depende de som e luz; o kit já traz os dois por código.

## Regras específicas

- Os 2 primeiros segundos ficam no nível da voz: susto de volume no começo faz a pessoa tirar o som e sair.
- Nenhuma fala repete o gancho; quem volta ao mesmo lugar ganha ângulo novo.
- Ficção declarada no selo do vídeo e na legenda.

## Exemplo de 10 s

`exemplos/estilos/terror-voto/exemplo.mp4` (no painel: tela Estilos), feito no caminho grátis. Para refazer ou usar como ponto de partida: `exemplos/estilos/README.md`.
