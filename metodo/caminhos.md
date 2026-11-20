<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Os dois caminhos: grátis e recomendado

O usuário escolhe o caminho **no começo da instalação** (`comandos/instalar.md`, pergunta 0) e pode trocar quando
quiser ("muda pro caminho pago"). Você grava a escolha em `canal/canal.md` (`caminho: gratis` ou `caminho:
recomendado`) e segue sem pedir que ele entenda de programação. Todo estilo do catálogo (`metodo/estilos/`) diz o
que muda em cada caminho.

## Resumo

| | **Grátis** | **Recomendado (pago)** |
|---|---|---|
| Onde | só no computador | computador ou celular (nuvem) |
| IA que monta o vídeo | **Antigravity** (a IA grátis do Google) ou **Codex** (vem na conta grátis do ChatGPT) | Claude Code (plano Pro do Claude, US$ 20 por mês) |
| Voz | **Gemini TTS** pelo Google AI Studio (plano grátis, com limite por dia); sem internet, **Kokoro** no computador | **ElevenLabs** (Starter, US$ 6 por mês, ou acima) |
| Imagens geradas por IA | não há caminho grátis estável; os estilos grátis não dependem de imagem gerada | Codex (conta do ChatGPT) ou a API de imagem do Google |
| Render | o computador (placa de vídeo ajuda; sem ela, mais lento) | igual, ou a nuvem (mais lenta) |
| Tempo por vídeo | 2 a 5 h, com mais espera | 1 a 2 h |

Preços conferidos em 06/11/2026. Confira no dia em que assinar.

## Caminho grátis, do começo ao fim

1. **Computador com Windows ou Mac.** No celular não há caminho grátis: a IA precisa rodar comandos.
2. **Instale o Antigravity ou o Codex** (`LEIA-ME.md`, "Jeitos de abrir") e abra a pasta do estúdio nele. Os
   dois começam de graça: o Antigravity com a conta do Google, o Codex com a conta grátis do ChatGPT. Os dois leem o
   `AGENTS.md`, que é a mesma entrada do Claude Code.
3. **Diga "oi".** A IA ativa a licença, instala o que falta (`python verificar.py`, a partir de `kit/`) e faz a
   entrevista.
4. **A voz grátis:**
   - **Gemini TTS (recomendada no grátis):** a IA roda `python chave.py --qual gemini`, abre uma janela no
     navegador, e o usuário entra no Google AI Studio com a conta do Google, clica em "Get API key" e cola a chave na
     janela. Não pede cartão. A voz é natural em português e aceita estilo ("sussurrado", "animado").
   - **Kokoro (sem internet, sem limite):** instalado pelo `kit/INSTALAR.md`. Um degrau abaixo na naturalidade.
   - No plano grátis, o Google usa o texto enviado para melhorar os produtos dele. Para quem não quer isso, o
     caminho é o Kokoro ou o plano pago.
5. **Escolha um estilo que não depende de imagem gerada:** top 5, quiz, tipografia, história real, série 2D,
   terror com voto, explicativo 3D, ou faceless e antes/depois com as suas fotos.
6. **Primeiro vídeo:** `comandos/modo-rapido.md`.
7. **Postar:** pelo app de cada rede, com o pacote das redes escolhidas que o kit gera (uma pasta por rede).

Limites do grátis que você conta ao usuário com honestidade:
- a voz do Google tem limite por dia; quando acaba, o kit espera e tenta de novo, ou troca para o Kokoro;
- o Antigravity e o Codex grátis têm limite de uso (o do Codex grátis é pequeno e a OpenAI não publica o número);
  um vídeo pode precisar de duas sessões, ou de alternar entre os dois;
- sem placa de vídeo, o render leva de 3 a 10 vezes mais.

## Caminho recomendado, do começo ao fim

1. **Plano Pro do Claude** e o app do Claude no computador (aba Code), ou o Claude Code na nuvem pelo celular
   (`celular/COMECE-AQUI.md`).
2. **Abra a pasta e diga "oi".** Licença, instalação e entrevista, igual ao grátis.
3. **Voz ElevenLabs:** pelo conector oficial (Configurações → Conectores, sem chave) ou pela janela da chave
   (`python chave.py`). Três amostras para escolher ouvindo (`python -m voz.amostras`). Uma voz por personagem.
4. **Imagens geradas** (só nos estilos que pedem: novela anime, faceless sem fotos próprias): Codex com a conta do
   ChatGPT, ou a API de imagem do Google. A IA mostra antes quantas imagens vai gerar.
5. **Primeiro vídeo:** `comandos/modo-rapido.md`, depois o estilo do canal.

## Gasto: regra do estúdio

Antes de qualquer geração paga (voz da ElevenLabs, imagem paga), a IA mostra a estimativa (a voz custa cerca de 1
crédito por caractere; um episódio de 2 min com personagens fica em 1.500 a 2.500 créditos) e só gera com o "pode"
do usuário. Nada de teste, amostra ou tomada extra que ele não pediu.
