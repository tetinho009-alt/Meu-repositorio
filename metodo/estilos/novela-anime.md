<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Novela anime (romance e drama)

## O que é

Uma novela em capítulos no visual de anime: triângulo amoroso, uma injustiça clara, vingança lenta e uma pequena
vitória da protagonista em toda parte. O público vota no caminho do próximo capítulo. Funciona como "motion comic":
imagens paradas de boa qualidade, com câmera, paralaxe e cortes rápidos, e uma narradora "amiga da fofoca".

## Duração e formato

Vertical 1080x1920. **2:00 a 2:30**, em 12 a 15 quadros (cenas).

## Estrutura do roteiro

| Tempo | Batida |
|---|---|
| 0 a 3 s | Abertura no momento mais quente (quase-beijo, grito, tapa na mesa) |
| 3 a 5 s | Cartela "TRÊS DIAS ANTES" |
| até 30 s | A protagonista, o poder dela (ex.: memória fotográfica) e a injustiça |
| meio | Um rico à vista e um escondido; uma vitória pequena dela |
| fim | Volta ao momento da abertura, e o voto entre dois caminhos (escritos antes, para os dois existirem de verdade) |

Narradora com no máximo uma gíria por fala. Contato físico (abraço, beijo) só como cena inteira gerada, nunca
montando dois recortes.

## Como é feito no kit

1. **Imagens:** a IA escreve os pedidos de imagem (`modelos/prompt-thumb.md` serve de base): a heroína de corpo
   inteiro primeiro; depois as expressões com a heroína anexada; cenários vazios; cenas de contato inteiras. Fundo
   verde puro (#00FF00) para recortar; pedir "fundo transparente" faz a IA desenhar um xadrez falso.
2. **Montagem:** cada cena vira um bloco `imagem` no motor de cartelas (`kit/cartelas/LEIA-ME.md`), com zoom lento,
   texto e legenda; o voto é o bloco `voto`.

Nesta versão o kit **não** anima boca e piscada em cima da imagem gerada. Fica como motion comic, que é o que dá para
garantir em qualquer computador.

## O que precisa

| | Grátis | Recomendado (pago) |
|---|---|---|
| Imagens | **não há caminho grátis estável.** Os geradores grátis mudam de limite e de termos toda semana, e a API de imagem do Google não tem plano grátis | ChatGPT com o Codex (gerador de imagem da conta) ou a API de imagem do Google, perto de US$ 0,04 por imagem |
| Voz | Gemini TTS (voz feminina, estilo "fofoqueira animada") | ElevenLabs |
| IA | Antigravity ou Codex | Claude Code (Pro) |

Uma parte gasta umas 40 a 50 imagens. Diga isso antes de começar.

## Dificuldade

**Alta.** Manter o rosto igual entre as imagens é o trabalho todo.

## Exemplo de 10 s

`exemplos/estilos/novela-anime/exemplo.mp4` (no painel: tela Estilos), feito no caminho grátis. Para refazer ou usar como ponto de partida: `exemplos/estilos/README.md`.
