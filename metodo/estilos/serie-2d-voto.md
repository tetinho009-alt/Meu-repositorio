<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Série animada 2D com voto (comédia)

## O que é

Uma série de desenho em que cada episódio resolve um pedaço do problema do personagem e termina num voto: o público
escolhe nos comentários o que acontece no próximo. É o formato do caso real da Temporada Viral: uma série de
comédia sobre um rapaz que usou uma foto de IA num aplicativo de namoro, com um defeito consertado por episódio. A
série teve 2.015.763 visualizações e +5.560 seguidores em 30 dias (painel do Instagram, 06/11/2026, resultado
pessoal).

## Duração e formato

- Vertical 1080x1920, 60 fps com placa de vídeo (30 fps na nuvem).
- **1:30 a 2:40**, mirando **1:45 a 2:20** de narração. Acima de 3 min o Instagram não recomenda para quem não segue.

## Estrutura do roteiro

| Tempo | Batida | O que faz |
|---|---|---|
| 0 a 3 s | Gancho fixo | Uma frase que explica a premissa inteira para quem nunca viu, com imagem nojenta ou absurda no quadro 0. Ex.: "Faltam 7 dias para a prova. Ela ainda não sabe dirigir." A mesma estrutura de abertura em todo episódio vira marca |
| 3 a 15 s | Prazo e risco | O que acontece se ele não consertar, e em quanto tempo ("faltam 5 dias para o almoço"). Nunca abrir com resumo de "ontem" |
| 15 a 45 s | O voto anterior vira ação | O que a galera escolheu começa a ser consertado, com um personagem da família de testemunha |
| ~meio | Pergunta aberta + chamada | No ponto de maior retenção, uma pergunta sem resposta ("qual dos três?") e, se o canal vende algo, a chamada falada uma vez, ligada ao tema |
| meio ao fim | Conserto absurdo | A virada irônica; o conserto dá certo e **fica** (nunca desfazer o que acabou de ser consertado) |
| últimos 15 s | O "quase" | Outro defeito quase põe tudo a perder. O fim é visual, não uma frase |
| fim | Voto | "Amanhã ele resolve qual: X ou Y?", entre dois problemas diferentes, nunca dois jeitos de fazer a mesma coisa |

Humor na situação, nunca no corpo de ninguém (público geral, com criança assistindo).

## Como é feito no kit

O caminho do `comandos/novo-video.md` (Formato 1), com o rig 2D (`kit/maquina/`), o estilo desenhado próprio
(`comandos/criar-estilo.md`) e a apuração real do voto (`comandos/apurar-votos.md`). Comece pelo exemplo:
`python exemplo/rodar.py --stills` a partir de `kit/`, e crie o episódio com `python episodio_novo.py`.

Portões obrigatórios (`metodo/licoes.md`): roteiro aprovado → voz ouvida de fone → folha de quadros-marco → **folha
de 6 a 8 quadros de toda pose nova** → still de cada cena nova → render.

## O que precisa

| | Grátis | Recomendado (pago) |
|---|---|---|
| IA que monta | Antigravity ou Codex (conta grátis do ChatGPT), no computador | Claude Code (plano Pro) |
| Voz | Gemini TTS (plano grátis do Google AI Studio) ou Kokoro no computador | ElevenLabs Starter ou acima, uma voz por personagem |
| Desenho e render | o kit, por código (sem gerador de imagem) | igual |
| Tempo por episódio | 3 a 5 h | 1 a 2 h |

## Dificuldade

**Média.** O roteiro é o que mais pesa; o desenho sai do kit, mas pose nova pede conferência quadro a quadro.

## Erros que já custaram episódio

- Cotovelo dobrando para a frente e braço erguido invertido: confira na folha de quadros.
- Cenário novo improvisado e pobre: reaproveite os cenários caprichados ou faça o novo com o mesmo detalhe.
- Brilho de 4 pontas grande atrás de personagem: vira sol de desenho infantil (ou símbolo político). Use halo redondo.
- Abrir o episódio com "ontem..." ou "parte 4": quem chega de fora pula.

## Exemplo de 10 s

`exemplos/estilos/serie-2d-voto/exemplo.mp4` (no painel: tela Estilos), feito no caminho grátis. Para refazer ou usar como ponto de partida: `exemplos/estilos/README.md`.
