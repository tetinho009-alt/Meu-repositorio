<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Motor de cartelas

Faz o vídeo inteiro a partir de um `roteiro.json`, sem personagem desenhado: tipografia cinética, top 5, quiz,
faceless com imagens, história real, antes e depois e bastidores (`metodo/estilos/`). Fundo escuro com brilho, texto
que entra no tempo da voz, legenda palavra por palavra, efeitos e trilha feitos por código, pacote das 3 redes.

## Rodar (a partir de `kit/`)

```
python cartelas/rodar.py cartelas/exemplo            # o exemplo (top 5 com quiz), voz do config
python cartelas/rodar.py <pasta> --stills            # um quadro por bloco, em segundos (folha.jpg)
python cartelas/rodar.py <pasta> --previa            # o vídeo inteiro sem voz, para ver o ritmo
python cartelas/rodar.py <pasta> --voz gemini        # voz grátis do Google
python cartelas/rodar.py <pasta> --voz elevenlabs --seco   # custo da voz, sem gravar
```

Medido numa RTX 4060 de notebook: 45 s de vídeo a 60 fps em 58 s de render; o pacote das 3 redes leva uns 3 min.
Sem placa de vídeo, o render vai para a CPU em vários processos, sozinho.

A saída fica em `trabalho/<nome>/` (vídeo, `folha.jpg`, `qa/`, `capa.jpg`, `linha.json`, `audio/`) e o pacote em
`trabalho/entregas/<nome>/`. Para refazer a voz de um bloco, apague o mp3 dele em `audio/` e rode de novo.

## O roteiro.json

```json
{
  "estilo": "top5",                     // um dos estilos de metodo/estilos/ (define a faixa de duração)
  "nome": "corpo_p1",                   // nome dos arquivos (opcional; padrão: o título)
  "titulo": "5 coisas que...",
  "capa": "Frase da capa", "capa_destaque": ["NUNCA"], "capa_rotulo": "TOP 5",
  "parte": 1, "proximo": "o assunto da parte 2",   // o CTA de cada rede ("SEGUE PRA VER ...")
  "voz": {"provedor": "gemini", "voz": "Charon"},  // gemini, kokoro, elevenlabs, azure, piper
  "tema": {"fundo": "#0F1424", "destaque": "#FF6B4A", "destaque2": "#4FB3FF", "destaque3": "#C5EE4F"},
  "fontes": ["fonte de cada fato"],     // vai na legenda do post
  "post": {"texto": "...", "hashtags": ["#a"], "titulo_youtube": "...", "comentario_fixado": "..."},
  "legenda": true, "blur": 0, "fps": 60, "clima": "leve", "musica": true,
  "apresentador": {"personagem": "nico", "lado": "e", "altura": 470},  // ligado por padrão; false desliga
  "amostra": false,                     // true só nos exemplos de 10 s (faixa de 8 a 15 s na trava)
  "teste": false,                       // true no vídeo de teste de ~5 s (faixa de 3 a 9 s): sem pacote, leve no PC
  "blocos": [ ... ]
}
```

O apresentador vem ligado por padrão: todo vídeo de cartelas tem um personagem do kit (`personagens/<nome>`, o Nico se o roteiro não disser outro) no canto de baixo, falando com a voz. Escolha o personagem que combina com o assunto e o estilo estudado. Só desligue (`"apresentador": false`) se o usuário pedir um vídeo sem personagem. Ele fala com a voz: boca
palavra a palavra, piscada, respiração e um gesto por bloco (susto no gancho, aponta no item, pula na revelação,
acena no voto e no fim). A legenda de baixo desliga sozinha, porque o texto grande já mostra a fala. Exemplos com e
sem apresentador em `exemplos/estilos/`.

Comentários `//` acima são só explicação: o arquivo de verdade é JSON puro (veja `cartelas/modelos/`).

### Blocos

Cada bloco é uma frase da voz e uma "cartela" na tela. Campos comuns: `tipo`, `fala` (o que a voz diz, com número
por extenso), `tela` (o texto grande, curto, em algarismo), `destaque` (palavras da tela com brilho), `rotulo`
(etiqueta pequena acima, ex. "PASSO 2"), `pausa` (segundos depois da fala; padrão 0,35).

| tipo | Para quê | Campos próprios |
|---|---|---|
| `gancho` | o primeiro bloco: a frase que prende em 3 s | |
| `texto` | uma frase com texto cinético | |
| `item` | item de lista com número grande | `numero` |
| `quiz` | pergunta com opções e contagem | `opcoes` (2 a 4), `certa` (0, 1...; -1 = sem resposta certa), `contagem` (s) |
| `revela` | a resposta do quiz anterior, com a certa acesa | |
| `imagem` | imagem de tela inteira com zoom lento | `imagem` (arquivo na pasta do episódio) |
| `antes_depois` | cortina do antes para o depois | `antes`, `depois` (arquivos) |
| `cta` | cartão "segue pra ver..." dentro do vídeo | |
| `voto` | o voto da parte 2, opção 1 e opção 2 nas cores do tema (`opcao1`, `opcao2`) | `opcoes` (2) |
| `fim` | a última frase (pergunta aberta) | |

### Desenho do assunto (obrigatório)

Todo bloco de conteúdo (`gancho`, `texto`, `item`, `fim`) pode ter `"desenho": "mel.png"`: um PNG transparente do
assunto, que entra com um salto e fica flutuando acima do texto (no `item`, no lugar do número grande, que sobe e
diminui). Pelo menos metade dos blocos de conteúdo precisa mostrar o assunto (desenho ou imagem), senão a trava para
o render: cartela só com texto é vídeo genérico. Desenhe por código (Skia ou PIL, traço limpo, cores do tema, 800 px
de largura) ou use os visuais de `estilos_visuais/`; um desenho por bloco, do que a frase fala.

Imagens: JPG ou PNG em pé (1080x1920 é o ideal; outras são cortadas para cobrir a tela). Imagem que falta aparece
marcada no `--stills` e no `--previa`, e trava o render final.

## As travas (não contorne)

- Conferência do roteiro: tipo de bloco, opções do quiz e do voto, imagens, palavras que a Meta pune, isca de
  engajamento, termo em inglês fora da base de pronúncia, espaço em disco.
- Antes do render: duração na faixa do estilo, gancho em até 3 s, emenda de áudio em cima de fala, voz igual ao
  roteiro (85% ou mais das palavras).
- Depois: volume do vídeo (-14 LUFS, pico até -1,5 dBTP), grade de QA com a zona segura, legenda de cada rede
  conferida pelo `pacote_redes.py`.
