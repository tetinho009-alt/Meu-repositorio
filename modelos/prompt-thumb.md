<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Prompt de thumb forte (capa)

Dois caminhos para a capa de cada vídeo:

1. **Automático e grátis:** `python kit/capa.py <episodio.json> <saida.jpg> --redes` monta as 3 capas com o elenco
   do episódio e o CTA de cada rede. Bom para postar todo dia.
2. **Capa forte com IA de imagem** (ChatGPT, Gemini ou outra): para o vídeo que você quer empurrar (o primeiro da
   série, o vídeo de vendas, o que está viralizando). A IA desta pasta preenche o prompt abaixo com os dados do canal
   (`canal/identidade.md`) e do episódio, e você cola na IA de imagem junto com a imagem do seu personagem/mascote.

## Regras que fazem a thumb funcionar

- **Uma ideia só**, lida em 1 segundo: um número grande, ou uma pergunta curta. No máximo 4 a 6 palavras.
- **Número verdadeiro**, com o tempo junto ("+40 MIL VIEWS EM 27H"). Número inventado derruba a confiança e o canal.
- **Rosto com expressão exagerada** (susto, surpresa, curiosidade) olhando para o objeto do vídeo.
- **Objeto do desejo** na frente: dinheiro, o bicho, a peça aberta, o celular com o vídeo.
- **Contraste forte**: fundo escuro, texto claro com contorno grosso, 2 ou 3 cores no máximo.
- **Texto grande à esquerda**, personagem à direita. Nada importante no canto de baixo à direita (o YouTube põe a
  duração ali).
- Sem logo de rede social, sem marca de terceiros, sem rosto de pessoa real.

## Prompt (preencha os [campos])

```
Crie uma thumbnail [16:9 (1280x720) para YouTube | 9:16 (1080x1920) para Reels, TikTok e Shorts], estilo
[estilo do canal, ex.: cartoon de sticker com contorno preto grosso | 3D estilo animação], com o MESMO personagem
da imagem anexada ([descrição curta do personagem]).

Composição:
- Fundo: [cor escura do canal] com raios de sol em [cor 1] e [cor 2] saindo de trás do personagem.
- Esquerda (40% da largura), texto empilhado, fonte cartoon bem grossa, contorno preto grosso e sombra dura:
  "[LINHA 1, o número ou a pergunta]" em [cor de destaque], enorme
  "[LINHA 2]" em branco
  "[LINHA 3]" em [segunda cor], enorme
  e embaixo uma etiqueta inclinada com borda preta escrito "[TEMPO OU PROVA, ex.: EM 27H]"
- Centro: [o objeto do vídeo: 3 celulares mostrando a série | o bicho aberto por dentro | ...].
- Direita: o personagem [expressão exagerada], [ação, ex.: segurando uma lupa], olhando para o centro.
- Na frente: [objeto do desejo, ex.: um maço de notas com cinta amarela e moedas].

Regras: o texto tem de estar escrito exatamente assim, grande e legível no celular. Nenhum outro texto, logo ou
marca. Cores chapadas e saturadas.
```

Se a IA de imagem errar alguma letra, peça de novo com "sem nenhum texto, deixa os 40% da esquerda livres" e escreva
o texto por cima com `kit/capa.py --arte <imagem.png>` ou em qualquer editor.

## Exemplos de texto

| Formato | Linha 1 | Linha 2 | Linha 3 | Etiqueta |
|---|---|---|---|---|
| Série (prova) | +40 MIL | VIEWS | VÍDEOS DE IA | EM 27H |
| Série (gancho) | NÃO RESPONDA | — | A VOZ DE CIMA | PARTE 1 |
| Explicativo 3D | POR DENTRO | DE UMA | CARAVELA | NÃO É ÁGUA-VIVA |
| Vídeo de vendas | VÍDEOS 3D | QUE EXPLICAM | TUDO | COM IA |
