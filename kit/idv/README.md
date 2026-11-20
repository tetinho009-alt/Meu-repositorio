<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# kit/idv · Gerador de identidade visual

Um script, um arquivo de marca. `gerar_idv.py` lê o `marca.json` e desenha a identidade visual inteira do canal
com Skia: logos, foto de perfil, banner do YouTube, capas de destaque, modelos para preencher, a prancha do manual, o
`MANUAL_IDV.md` e uma prancha de conferência. Mudou a cor ou o nome? Edita o JSON e roda de novo.

É o caminho grátis da identidade: tudo por código, sem IA de imagem. Um canal pronto feito com ele (marca, mascote
desenhado por código e todas as peças) está em `exemplos/canal-pronto/`. Quem preferir desenhar a arte no ChatGPT
(precisa de assinatura) usa `modelos/prompts-chatgpt-identidade.md` e traz as imagens para cá.

## O visual

Os modelos usam o mesmo sistema da capa do episódio (`kit/maquina/capa.py`), o "cartão e adesivo": fundo liso com
listras diagonais discretas na cor da série, cartão inclinado com retícula de pontos, o mascote (ou o elenco) como
adesivo com borda clara e sombra dura, selo redondo com o número da parte, texto alinhado à esquerda e as opções do
voto como etiquetas nas cores das opções. Fonte de cartaz no título (`fontes.titulo`, Archivo Black) e fonte de apoio
nos rótulos (`fontes.mono`, Barlow Bold).

## O que sai

| Pasta | Peças |
|---|---|
| `logo/` | principal ilustrado (se houver), principal vetorial (PNG + SVG), mono branco e preto (PNG + SVG), ícone quadrado 1024 e 512 (PNG + SVG), símbolo transparente, ícone mono branco e preto |
| `perfil/` | `perfil_1080.png`, feita para o recorte em círculo (Instagram, TikTok, YouTube, Kwai) |
| `youtube/` | banner 2560x1440, banner com as áreas marcadas (TV, desktop, tablet, celular), marca d'água 150x150 |
| `destaques/` | uma capa de destaque 1080x1920 por série + as extras (`destaques_extra`) |
| `modelos/exemplo/` | capa de episódio 1080x1920 (e a versão com os recortes 3:4, 4:5 e 1:1 da grade), post de feed 1080x1350, card "Parte X já está no ar", card de resultado da votação (sempre com o carimbo de demonstração), capa de playlist 16:9 (3840x2160 se a arte tiver 1000 px ou mais de altura; senão 1920x1080, para não amolecer o traço) |
| `modelos/variantes/` | peças de demonstração listadas em `variantes_demo` no marca.json |
| raiz | `manual_idv.png`, `MANUAL_IDV.md`, `conferencia.jpg` |

## Instalar

Usa o mesmo Python do kit (skia-python, numpy, glfw, Pillow). As fontes são as do kit: se faltar alguma, rode
`python baixar_fontes.py` a partir de `kit/`. No marca.json basta o nome do arquivo (`"ArchivoBlack-Regular.ttf"`):
se ele não estiver ao lado do JSON, o gerador procura em `kit/fontes/`. As três fontes são livres (SIL Open Font
License 1.1): podem ir em peça comercial, desde que não sejam vendidas sozinhas.

## Rodar

Copie `marca.exemplo.json` para a pasta da sua marca como `marca.json`, preencha e rode, a partir de `kit/`:

```
python idv/gerar_idv.py tudo --marca ../canal/idv/marca.json --saida ../canal/idv
```

O exemplo roda sem nenhuma arte: com `"icone": "inicial"`, o símbolo é a primeira letra do nome num quadrado da cor
de destaque, e os cartões dos modelos levam o ícone. Serve para conferir cores e textos antes de ter mascote.

### Uma peça por vez (modelos para preencher)

```
python idv/gerar_idv.py modelo capa --marca marca.json --serie serie_1 --parte 2 ^
    --subtitulo "nome da parte" --pergunta "abrir ou trancar?" --linha "você decide a parte 3" ^
    --arte elenco.png --saida capa_p2.jpg

python idv/gerar_idv.py modelo capa ... --guia --saida capa_p2_guia.jpg      (marca os recortes da grade)
python idv/gerar_idv.py modelo post --marca marca.json --serie serie_1 --parte 1 --subtitulo "título do post" --texto "Duas frases de contexto." --saida post.jpg
python idv/gerar_idv.py modelo parte --marca marca.json --serie serie_1 --parte 2 --linha "assista no perfil" --saida parte2.jpg
python idv/gerar_idv.py modelo resultado --marca marca.json --serie serie_1 --parte 1 --pergunta "abrir ou trancar?" --opcoes "ABRIR=62" "TRANCAR=38" --votos 214 --saida resultado.jpg
python idv/gerar_idv.py modelo playlist --marca marca.json --serie serie_1 --subtitulo "série interativa · temporada 1" --linha "você decide cada parte" --saida playlist.jpg
python idv/gerar_idv.py modelo destaque --marca marca.json --serie serie_1 --saida destaque.png
```

`--serie` puxa nome, cor e pose do marca.json; `--titulo`, `--cor` e `--arte` sobrescrevem. Textos viram
maiúsculas sozinhos. A pergunta no formato "A OU B?" vira duas etiquetas (A na cor `opcao1`, B na `opcao2`); outro
formato sai como texto. `--arte` aceita qualquer PNG com fundo transparente (o elenco recortado do episódio, por
exemplo); sem ela, entra a pose do mascote da série. `--demo` no resultado carimba "DEMONSTRAÇÃO · NÚMEROS
FICTÍCIOS": use sempre que os números não forem a apuração real.

### Arte feita no ChatGPT (fundo verde)

Arte gerada em IA de imagem vem com fundo chapado (peça verde `#00FF00`; nunca "transparente", que costuma vir com um
xadrez desenhado). Tire o fundo antes de usar:

```
python idv/gerar_idv.py recortar mascote_ia.png ../canal/idv/mascote/acenando.png
python idv/gerar_idv.py recortar mascote_ia.png saida.png --chave magenta     (personagem verde: fundo #FF00FF)
```

## Trocar logo, cores e fontes

Tudo no `marca.json`. Caminhos podem ser absolutos ou relativos à pasta do próprio JSON.

- **Logo ilustrado** (`logo.ilustrado`): PNG com fundo transparente, o maior que você tiver. Entra no banner e na
  prancha. Deixe `null` se não houver: o banner usa o logo vetorial.
- **Nome do logo** (`logo.linhas`): uma linha por item. As linhas são esticadas para a mesma largura, então a
  palavra curta fica maior.
- **Símbolo** (`logo.icone`): `"inicial"` (letra do nome) ou o caminho de um PNG transparente. Com PNG, as versões
  mono saem como silhueta tingida e o SVG leva a imagem embutida, não vetor. **Busto** (PNG com a base cortada reta,
  como `exemplos/canal-pronto/mascote/rosto.png`) sai encostado no pé do ícone e da foto de perfil, como quem
  aparece de baixo para cima.
- **Cores** (`cores`): `fundo` é o fundo de todas as peças; `destaque` é o que se lê primeiro (nome no logo, fundo
  do ícone, etiqueta "JÁ ESTÁ NO AR", "VENCEU"); `acento` tinge o banner; `opcao1` e `opcao2` são as cores do voto
  (as mesmas do `kit/config.json`); `texto` é o texto e a borda do adesivo; `contorno` é o traço em volta do nome no
  logo. `paleta_doc` é só a documentação que vai para o manual.
- **Cor de cada série** (`series[].cor`): tinge as listras do fundo, o cartão, o rótulo em versal e o disco do
  destaque. A cor do texto das etiquetas (claro ou escuro) é escolhida sozinha pelo contraste.
- **Fontes** (`fontes`): `titulo`, `mono`, `texto` e `logo`, cada uma um `.ttf`. Fonte larga demais encolhe sozinha
  para caber; confira a prancha de conferência depois de trocar.
- **Mascote** (`mascote.poses`): nome da pose e caminho do PNG transparente. As séries e os modelos escolhem a pose
  pelo nome. `banner_poses` põe duas poses nas laterais do banner.
- **Fundo pronto do banner** (`banner_fundo`, opcional): uma imagem sem texto (feita no ChatGPT, por exemplo) no
  lugar das listras; o gerador escreve o nome por cima, numa faixa escura dentro da área segura.
- **Textos dos modelos de exemplo** (`exemplo`, opcional): `serie`, `titulo`, `subtitulo`, `pergunta`, `linha`,
  `post_titulo`, `texto`, `resultado_pergunta`, `opcoes`, `votos`, `playlist_kicker`, `playlist_linha`. Sem ele, os
  modelos saem com "NOME DA SÉRIE" e "OPÇÃO A OU OPÇÃO B?".

## Arte com buraco de recorte

Arte feita por IA e recortada por remoção de fundo automática às vezes chega com um buraco no alfa dentro da figura
(um pedaço do olho apagado). Some no fundo escuro e aparece no cartão colorido. Com `"limpar_adesivos": true` no
marca.json, o gerador preenche esse buraco ao carregar o logo ilustrado e as poses (a arte de episódio passada em
`--arte` nunca é alterada; os arquivos de origem também não).

Sempre, em todo adesivo, ele põe 8 px de margem transparente antes de escalar e **avisa quando a arte encosta na
borda do arquivo** ("AVISO ...: arte encosta na borda do arquivo"). Quer dizer que o recorte cortou a figura (uma
ponta de mão, um fio de cabelo): margem não recupera o que falta. Exporte a arte de novo com folga.

## Sem placa de vídeo: render na CPU

Por padrão o script desenha na GPU (contexto OpenGL de uma janela oculta: nada aparece na tela). Sem placa de vídeo,
em máquina virtual, servidor sem tela ou na nuvem, rode com `--cpu`:

```
python idv/gerar_idv.py tudo --marca marca.json --saida IDV --cpu
```

O desenho é o mesmo nos dois caminhos; a CPU só demora mais (o canal de exemplo inteiro sai em menos de um minuto).
Se a GPU falhar, o script para e diz para usar `--cpu`: ele nunca troca de caminho sozinho, para você saber em qual
rodou (a prancha de conferência também diz).

## Medidas usadas e de onde vieram

Conferidas em 28/10/2026.

| Peça | Medida | Fonte |
|---|---|---|
| Banner do YouTube | 2560x1440 recomendado; mínimo 2048x1152 (16:9); área segura 1235x338 no tamanho mínimo, que em 2560x1440 dá 1546x423; até 6 MB | [YouTube Help: Manage your channel branding](https://support.google.com/youtube/answer/10456525) e [Channel banner & profile picture tips](https://support.google.com/youtube/answer/12950272) |
| Marca d'água do YouTube | mínimo 150x150, quadrada, menos de 1 MB | [YouTube Help: Manage your channel branding](https://support.google.com/youtube/answer/10456525) |
| Foto de perfil do YouTube | exibida a 98x98, até 15 MB; o gerador faz 1080x1080 e serve para todas as redes | [YouTube Help: Manage your channel branding](https://support.google.com/youtube/answer/10456525) |
| Miniatura / capa de playlist | 16:9, recomendado 3840x2160, largura mínima 640; 2 MB pelo celular, 50 MB pelo computador. O gerador só sobe para 4K se a arte aguentar | [YouTube Help: Add custom thumbnails](https://support.google.com/youtube/answer/72431) |
| Capa de Reels | 1080x1920; desde 2025 a grade do perfil mostra o miolo 3:4 (1080x1440), não mais 1:1 | Sem página oficial do Instagram. Guias: [Hopper HQ](https://help.hopperhq.com/en/articles/10907941-instagram-s-vertical-grid), [Planoly](https://planoly.com/blog/guide-to-instagrams-new-vertical-grid) |
| Post de feed | 1080x1350 (4:5); na grade 3:4 perde cerca de 34 px de cada lado | Mesmas fontes acima |
| Capa de destaque | 1080x1920, recortada em círculo no centro | Sem página oficial; prática corrente |

O Instagram e o TikTok não publicam essas medidas em página oficial, e a grade 3:4 é recente. Antes de usar um
pacote de capas, suba uma capa como privada e confira no app.

## Limitações conhecidas

- O SVG sai sem degradê de efeito: é a versão chapada do logo, que é o que se quer em vetor. Ícone em PNG vai
  embutido como imagem no SVG.
- Mascote e logo ilustrado são imagens. Ampliar além do tamanho original amolece o traço. Para peças grandes
  (banner, capa 4K), tenha as poses em 1000 px ou mais.
- O texto é desenhado sem kerning (o Skia sem shaper não aplica o ajuste entre pares de letras). Em Archivo Black
  quase não aparece; em fonte serifada, aparece.
