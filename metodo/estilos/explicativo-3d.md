<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Explicativo 3D

## O que é

Uma pergunta do dia a dia ("como a caixa d'água sabe a hora de parar?") respondida com o objeto em corte, em 3D de
desenho com contorno preto, e um boneco que faz uma micro-piada discreta. Termina com o gancho do próximo vídeo.

## Duração e formato

Vertical 1080x1920. **40 a 65 s** (aceita 30 a 75).

## Estrutura do roteiro

| Tempo | Batida |
|---|---|
| 0 a 3 s | A pergunta-título na voz e na tela já no quadro 0, com o objeto aparecendo |
| 3 a 10 s | O "jeito errado": o que todo mundo acha (o boneco faz isso) |
| 10 a 50 s | 3 a 5 passos, cada um com a câmera indo para a parte certa do objeto, com 2 ou 3 micro-piadas no meio |
| fim | A revelação em uma frase e o gancho do próximo vídeo ("e quando falta água?"), que vira o CTA de cada rede |

Cada passo tem **fonte conferida** antes do roteiro. Na dúvida, não afirme: explicação errada vira comentário
corrigindo.

## Como é feito no kit

`comandos/novo-video.md` (Formato 2), `kit/explicativo3d/INSTALAR.md` (Blender) e
`kit/explicativo3d/web/LEIA-ME.md` (Three.js). Rode o exemplo (`python
explicativo3d/exemplo/rodar.py --stills`, a partir de `kit/`) e copie a pasta do exemplo para o episódio novo.
Modelos 3D só de licença CC0 (Quaternius, Kenney), anotados em `kit/explicativo3d/modelos/FONTES.md`.

## O que precisa

| | Grátis | Recomendado (pago) |
|---|---|---|
| IA | Antigravity ou Codex | Claude Code (Pro) |
| Voz | Gemini TTS ou Kokoro | ElevenLabs |
| 3D | Blender 5.2 LTS (grátis), com placa de vídeo; ou Three.js (grátis), sem placa | igual |
| Máquina | com placa: Blender ou Three.js; sem placa ou na nuvem: Three.js | igual |

**Dois motores.** Blender é o visual de referência e precisa de placa de vídeo. Three.js desenha a mesma cena só com
o processador, com visual quase igual, e é o único que roda na nuvem (celular). A escolha segue a preferência
`render.motor_3d` (tela Jeito dos vídeos); no automático, a IA pergunta quando os dois funcionam e usa o Three.js
quando não há placa. Detalhes em `comandos/novo-video.md`, seção "Motor 3D".

## Dificuldade

**Alta.** Montar a cena 3D de um objeto novo leva tempo; a pesquisa também.

## Exemplo de 10 s

`exemplos/estilos/explicativo-3d/exemplo.mp4` (no painel: tela Estilos), feito no caminho grátis. Para refazer ou usar como ponto de partida: `exemplos/estilos/README.md`.
