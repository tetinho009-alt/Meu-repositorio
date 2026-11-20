<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Bastidores e tela

## O que é

Mostrar como você faz o que faz: prints e gravações de tela, com texto que entra no tempo da voz, num fundo escuro
com brilho. Bom para quem ensina, vende serviço ou quer mostrar o processo do próprio canal.

## Duração e formato

Vertical 1080x1920, 60 fps. **30 a 55 s.**

## Estrutura do roteiro

Estrutura de série de streaming:

| Tempo | Batida |
|---|---|
| 0 a 3 s | Abertura fria: o resultado já na tela, sem título |
| 3 a 4 s | Vinheta curta com o nome do quadro ("BASTIDORES") |
| 4 s ao fim | O processo em 3 a 5 passos, um print por passo, com uma pergunta de retenção no meio |
| fim | "Segue pra ver o próximo bastidor" |

O que importa fica no meio da tela (entre a altura 500 e 1450 de 1920). Nada parado: o fundo e o print se mexem.

## Como é feito no kit

Motor de cartelas, estilo `bastidores` (`kit/cartelas/modelos/bastidores.json`): cada print é um bloco `imagem`
(PNG da tela, salvo na pasta do episódio), com `rotulo` para o passo ("PASSO 2"). Gravação de tela em vídeo não
entra nesta versão: tire prints dos momentos-chave.

## O que precisa

| | Grátis | Recomendado (pago) |
|---|---|---|
| Prints | a tecla de print do computador ou do celular | igual |
| Voz | Gemini TTS ou a sua voz gravada (mp3 por bloco) | ElevenLabs |
| IA | Antigravity ou Codex | Claude Code (Pro) |

## Dificuldade

**Baixa.**

## Regra

Nada de número de venda, renda ou "ganhe dinheiro" na tela ou na voz. Resultado só com data e "resultado pessoal".

## Exemplo de 10 s

`exemplos/estilos/bastidores/exemplo.mp4` (no painel: tela Estilos), feito no caminho grátis. Para refazer ou usar como ponto de partida: `exemplos/estilos/README.md`.
