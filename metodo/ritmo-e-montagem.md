<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# 06 · Montagem, legenda e render

Carregue depois do som masterizado e da folha de quadros aprovada.

## 1. Especificação do master (serve a todas as redes)

| Item | Valor | Por quê |
|---|---|---|
| Resolução | 1080x1920, vertical | Padrão das redes verticais |
| Quadros | 30 fps | Dentro do aceito pela API do Instagram (23 a 60) |
| Vídeo | H.264, `yuv420p` | Compatível com todo player |
| Áudio | AAC, 48 kHz, **estéreo**, 192 kbps | Mono já ficou mudo em celular |
| Duração | 1:30 a 2:40 na série com voto; os outros estilos na ficha | Ver `metodo/formula-roteiro.md` |
| Tamanho | Até ~50 MB no master; prévia para celular abaixo de 30 MB | Arquivo grande não chega no celular por mensagem |
| Contêiner | MP4 com `-movflags +faststart` | Começa a tocar antes de baixar inteiro |
| Marca d'água | Nenhuma de app | Instagram não recomenda Reels com marca d'água de outro app |

## 2. Caixa segura

Tudo que precisa ser lido fica dentro de **x 120–900, y 280–1420** (em 1080x1920). É a interseção das
interfaces das redes:
- à direita (x > 900) ficam os botões do TikTok e do Shorts;
- embaixo (y > 1420) ficam a legenda do post e o nome do perfil em todas;
- no topo (y < 280) ficam abas e o nome da conta.

Vale para título, cartão "REGRA N", tela de voto, "FICÇÃO" e legenda falada. Cenário e personagem podem ocupar a tela
inteira.

## 3. Legenda falada (texto queimado)

1. **Caixa alta, fonte pesada** (ex.: Inter ExtraBold), ~78 px, no máximo 2 linhas, centralizada.
2. **Posição:** base da legenda no máximo em y ≈ 1420, dentro da caixa segura. Legenda em y ≈ 1640 fica escondida
   pela interface das redes.
3. **Palavra a palavra**, no tempo real da fala (arquivo de tempos da etapa de voz); cada palavra entra com uma
   batida de escala de ~0,16 s.
4. **Contorno escuro de ~12 px + sombra suave logo abaixo.** Sombra deslocada para o lado parece erro.
5. **Palavras-chave na cor de destaque do canal** (a palavra que o público vai repetir).
6. **Fala de personagem** em outra cor ou inclinada, alinhada palavra a palavra como a narração.
7. **Sem legenda durante a tela de voto**: o texto do voto já está na tela.

## 4. Ritmo e transições

- Corte a cada 2 a 4 s; close para emoção, aberto para geografia.
- Plano que fica mais de 4 s ganha push-in lento.
- Transição "chicote" (borrão horizontal de ~0,18 s) nos cortes principais; corte seco no susto.
- Corte casado com a palavra marcada no roteiro, pelo arquivo de tempos.
- Tudo sincroniza ao arquivo de linha do tempo do som (`metodo/som.md`), nunca a tempos digitados.

## 5. Elementos fixos de tela

| Elemento | Quando | Regra |
|---|---|---|
| "USE FONE" | 0 a 2,5 s | No gancho |
| Título "NOME DA SÉRIE" (sem "Parte N") | ~2,5 a 6 s | Com brilho, grande |
| Selo "FICÇÃO" | O vídeo todo, discreto | Ficção declarada; sem "PARTE N" (`metodo/checklist.md`, item A2) |
| Contador da série ("TOQUE 1 DE 7", "NOITE 2") | Do título até o voto | Opcional, reforça a série |
| Cartão "REGRA N" | Meio | 3 a 4 s |
| Pílula "+ SEGUIR @perfil" | No pedido de seguir | Única vez |
| Tela de voto | Últimos 8 a 12 s | Opções nas cores fixas, "VOCÊS DECIDEM" |
| Stickers ou mascote do canal | **Só** no pedido de seguir e no fecho | Sticker em toda cena foi reprovado: polui e tira o medo |

## 6. Render

### Modo agente com GPU NVIDIA (Estúdio)

O kit desenha os quadros e codifica com NVENC. Comando em `kit/README.md`. Se o log não mostrar a GPU em uso, pare e
conserte antes de esperar um render lento.

### Modo nuvem (Claude Code na nuvem, sem GPU)

- O render cai para CPU sozinho (libx264). Funciona, mais lento.
- Episódio de até ~90 s, **um por vez**; gere antes a folha de quadros-marco e só depois o vídeo inteiro.
- O vídeo final volta pela conversa. Gere também a versão de prévia abaixo de 30 MB para abrir no celular.
- O usuário publica pela API (`metodo/publicacao-api.md`) ou baixa e posta pelo app.

### Sem o kit (ffmpeg direto)

Juntar uma sequência de quadros com o áudio:

```
ffmpeg -framerate 30 -i quadros/%05d.png -i mix_norm.wav -c:v libx264 -preset medium -crf 20 -maxrate 6M -bufsize 12M -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 -ac 2 -movflags +faststart -shortest episodio.mp4
```

Com NVIDIA, troque `-c:v libx264 -preset medium -crf 20` por `-c:v h264_nvenc -preset p5 -rc vbr -cq 21`.
Com Intel ou AMD, `h264_qsv` ou `h264_amf`.

Prévia comprimida para o celular:

```
ffmpeg -i episodio.mp4 -c:v libx264 -crf 28 -preset fast -c:a aac -b:a 128k previa.mp4
```


## 7. Grade de conferência (obrigatória antes de qualquer prévia)

Um quadro a cada 2 s, montado numa folha:

```
ffmpeg -i episodio.mp4 -vf "fps=1/2,scale=270:480,tile=9x6" -frames:v 1 grade.jpg
```

Quadro n da folha = segundo 2n. Procure: objeto flutuando, item atrás do muro errado, personagem cortado na borda,
cabelo solto da cabeça, escala errada, cabeça encostando na borda do quadro, legenda fora da caixa segura, tela de
voto parada mais de 15 s.

Pergunta-portão: **"isso parece produção ou protótipo?"** Se protótipo, não vai para prévia.

## 8. Portão da montagem

Mande a prévia ao usuário com a grade. Ele assiste **no celular, de fone**. Só siga com "aprovado". Depois rode o
`metodo/checklist.md` inteiro.
