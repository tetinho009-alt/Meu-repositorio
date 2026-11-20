<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Identidade do canal pelo ChatGPT (opcional)

> **Precisa de assinatura paga do ChatGPT.** Gerar imagem não está liberado no plano grátis do Codex, e no site do
> ChatGPT a quantidade de imagens depende do plano. **O caminho grátis do kit faz o mesmo por código**: logo, foto de
> perfil, banner, destaques e modelos, sem gastar nada (`kit/idv/README.md`; veja o resultado em
> `exemplos/canal-pronto/`). Use este arquivo só se você já paga o ChatGPT e quer um mascote com outro traço.

## Como o trabalho se divide

O ChatGPT desenha **só a arte**: o mascote, o símbolo e o fundo do banner. **O kit escreve os textos** (nome do canal,
série, parte, opções do voto) por cima, com as fontes do canal, e monta cada peça na medida certa. Motivo: IA de
imagem ainda erra letra e acento, e o texto precisa cair dentro da área que o app mostra.

Depois de gerar, você (ou a IA do estúdio) tira o fundo verde e põe as artes no `marca.json` do canal:

```
python idv/gerar_idv.py recortar arte_do_chatgpt.png ../canal/idv/mascote/acenando.png
python idv/gerar_idv.py tudo --marca ../canal/idv/marca.json --saida ../canal/idv
```

(a partir de `kit/`; se o mascote tiver verde, peça fundo magenta e rode o recorte com `--chave magenta`).

## Regras que evitam retrabalho

1. **Gere o mascote primeiro** (prompt 1). A primeira imagem boa vira a referência: anexe-a em **todo** prompt
   seguinte e escreva "o mesmo personagem da imagem anexada". Sem isso, cada peça sai com um bicho diferente.
2. **Sem texto na imagem** quando o kit escreve por cima (logo, capa, post, banner). Se aparecer letra, peça de novo
   "sem nenhuma letra, número ou palavra".
3. **Fundo verde chapado `#00FF00`**, uma cor só, sem sombra no chão, sem degradê. Nunca peça "fundo transparente": o
   ChatGPT costuma desenhar um xadrez cinza falso, que não sai no recorte. Mascote com verde no corpo ou na roupa:
   fundo magenta `#FF00FF`.
4. **Figura inteira com folga** de uns 5% em volta. Arte encostada na borda sai cortada (o kit avisa).
5. **Uma imagem por pedido**, no formato pedido: quadrado (1:1), vertical (2:3) ou horizontal (3:2).
6. **Mesmas cores sempre**, pelo código hex. Se o tom mudar, peça "use exatamente as cores [CORES]".
7. Personagem adulto ou bicho; nada sensual, nada de pessoa real, nada de marca ou personagem de outra empresa.

## As lacunas

Troque antes de colar (a IA do estúdio preenche com os dados de `canal/identidade.md`):

- **[NOME]**: o nome do canal (só para dar contexto; ele não é escrito na imagem).
- **[NICHO]**: o assunto e o público, em meia frase ("curiosidades de bichos para adultos curiosos").
- **[CORES]**: 3 ou 4 cores com hex ("lima #C5EE4F, coral #FF6B4A, céu #4FB3FF, fundo tinta #0F1424").
- **[MASCOTE]**: o mascote em uma frase (o que é, cor, um detalhe que só ele tem).

Exemplo preenchido (o canal de `exemplos/canal-pronto/`): [NOME] = Bicho Esquisito; [NICHO] = curiosidades de
bichos para adultos curiosos, tom bem-humorado; [CORES] = lima #C5EE4F, coral #FF6B4A, céu #4FB3FF, fundo tinta
#0F1424; [MASCOTE] = um axolote rosa #F59BB5 de corpo em forma de feijão, três brânquias magenta de cada lado da
cabeça, barriga clara e sorriso largo.

## Os prompts

### 1. Mascote do canal em 4 poses

Primeiro a folha (sem anexo). Depois uma pose por pedido, sempre com a folha anexada.

```
Crie a folha de personagem do mascote do canal [NOME] ([NICHO]): [MASCOTE].
Estilo cartoon de adesivo, cor chapada com uma sombra dura de um lado, contorno fino num tom mais escuro da
própria cor (nunca preto), olhos grandes ovais com um brilho, formas arredondadas e simples, fácil de reconhecer
pequeno. Paleta do canal: [CORES].
Mostre o mascote de corpo inteiro, de frente, em pé, braços soltos, expressão simpática.
Formato vertical 2:3. Fundo verde chapado #00FF00, sem sombra no chão, sem cenário, sem nenhuma letra ou número.
Figura inteira com folga em volta.
```

```
O mesmo personagem da imagem anexada, sem mudar cor, proporção, traço nem detalhes.
Pose: [acenando, sorrindo | surpreso, boca em O, braços para cima | apontando para a direita, sorriso | com uma
lupa perto do olho, cara de quem investiga].
Corpo inteiro, de frente. Formato vertical 2:3. Fundo verde chapado #00FF00, sem sombra no chão, sem cenário, sem
nenhuma letra ou número. Figura inteira com folga em volta.
```

Salve como `acenando.png`, `surpreso.png`, `apontando.png` e `lupa.png`, tire o fundo com o `recortar` e ponha os
caminhos em `mascote.poses` no `marca.json`.

### 2. Logo (o símbolo)

O nome do canal o kit escreve ao lado do símbolo, na fonte do canal. Do ChatGPT vem só o busto do mascote.

```
O mesmo personagem da imagem anexada, só da cintura para cima, de frente, sorrindo, olhando para a câmera.
Ícone de canal: forma simples e forte, que continue reconhecível em 32 pixels. Sem mudar cor, proporção nem traço.
Formato quadrado 1:1, o busto ocupando 80% da imagem e cortado reto na base. Fundo verde chapado #00FF00, sem
nenhuma letra ou número.
```

Recorte e ponha o caminho em `logo.icone` no `marca.json`: busto de base reta sai encostado no pé do ícone e da foto
de perfil.

### 3. Foto de perfil

Pode usar direto (o kit também faz a dele a partir do símbolo). O app recorta em círculo: nada importante nos cantos.

```
O mesmo personagem da imagem anexada, só da cintura para cima, de frente, sorrindo, olhando para a câmera.
Fundo de uma cor só, chapada: [primeira cor de CORES]. O rosto no centro, ocupando uns 60% da imagem, com folga
para o recorte em círculo. Sem nenhuma letra, número ou moldura. Formato quadrado 1:1.
```

Confira em tamanho de app: reduza a imagem para 40 px e veja se ainda dá para saber quem é.

### 4. Banner do YouTube (2560x1440, com área segura)

O YouTube mostra a imagem inteira só na TV. No computador aparece uma faixa de 2560x423 no meio; no celular, só a
área segura de **1546x423 no centro**. Do ChatGPT vem só o fundo, com o centro calmo; o nome entra pelo kit.

```
Fundo para banner de canal do YouTube do canal [NOME] ([NICHO]), formato horizontal 16:9.
Estilo cartoon de adesivo, cores chapadas da paleta [CORES]. O mesmo personagem da imagem anexada aparece duas
vezes, pequeno, nas pontas esquerda e direita, dentro da faixa do meio da altura.
O retângulo central (60% da largura e 30% da altura) fica liso, de uma cor só e sem nenhum desenho: é onde entra o
nome do canal. Em cima e embaixo, só textura suave da cor de fundo. Sem nenhuma letra, número ou logo.
```

Salve como `banner_fundo.png` na pasta da marca, ponha `"banner_fundo": "banner_fundo.png"` no `marca.json` e rode o
gerador: ele amplia o fundo para 2560x1440, escreve o nome dentro da área segura e gera também a versão com as áreas
marcadas, para conferir.

### 5. Capas de destaque do Instagram

Uma por destaque (por série, "Comece aqui", "Resultados"). O Instagram recorta um círculo no centro.

```
O mesmo personagem da imagem anexada, corpo inteiro, [pose ou objeto que representa o destaque, ex.: segurando
um troféu | acenando | com uma lupa]. Sem mudar cor, proporção nem traço.
Formato quadrado 1:1, figura no centro ocupando 70% da imagem, com folga para o recorte em círculo. Fundo verde
chapado #00FF00, sem nenhuma letra ou número.
```

Recorte e monte cada capa com a cor do destaque:
`python idv/gerar_idv.py modelo destaque --marca ../canal/idv/marca.json --arte destaque_x.png --cor "#C5EE4F" --saida destaque_x.png`.

### 6. Capa de episódio (1080x1920, com o recorte 3:4)

A capa é 1080x1920, mas a grade do perfil do Instagram mostra só o miolo 3:4 (y de 240 a 1680). O kit põe o título,
a parte e as opções do voto dentro desse miolo; do ChatGPT vem a arte do episódio.

```
O mesmo personagem da imagem anexada, corpo inteiro, [a cena do episódio em meia frase, ex.: assustado olhando
para um bicho estranho no fundo do lago], expressão exagerada que se entende em 1 segundo.
Formato vertical 2:3, figura ocupando a imagem com folga, pés na base. Fundo verde chapado #00FF00, sem cenário,
sem nenhuma letra ou número.
```

Recorte e monte: `python idv/gerar_idv.py modelo capa --marca ../canal/idv/marca.json --serie <id> --parte 1
--subtitulo "nome da parte" --pergunta "A ou B?" --linha "a resposta sai na parte 2" --arte cena.png --saida capa.jpg`
(com `--guia` sai a versão com os recortes marcados). Para a capa forte de um vídeo só, com texto feito pela IA de
imagem, use `modelos/prompt-thumb.md`.

### 7. Post de feed (1080x1350)

```
O mesmo personagem da imagem anexada, corpo inteiro, [a ação do post, ex.: segurando uma lupa e olhando
desconfiado]. Sem mudar cor, proporção nem traço.
Formato vertical 2:3, figura inteira com folga. Fundo verde chapado #00FF00, sem cenário, sem nenhuma letra ou
número.
```

Recorte e monte: `python idv/gerar_idv.py modelo post --marca ../canal/idv/marca.json --serie <id> --subtitulo
"título do post" --texto "duas frases de contexto" --arte post.png --saida post.jpg`.

## Onde rodar os prompts

### No ChatGPT (site ou app)

1. Entre com a conta paga e abra uma conversa nova (uma conversa por canal: a referência fica à mão).
2. No prompt 1, cole o texto e envie. Nos seguintes, **anexe a imagem do mascote** (clipe ou "+") antes de colar.
3. Gostou? Baixe o PNG (clique na imagem e no botão de baixar) e salve com o nome sugerido na pasta da marca, por
   exemplo na pasta canal/idv/arte do estúdio.
4. Não gostou de um detalhe? Responda na mesma conversa dizendo **o que muda e o que fica igual** ("mesma pose, só
   a boca mais aberta"), em vez de pedir tudo de novo.
5. Com as artes salvas, diga à IA do estúdio: "usa essas artes na identidade do canal". Ela recorta, preenche o
   `marca.json` e roda o gerador.

### No Codex CLI (a IA de código da OpenAI, no terminal)

Conferido em 06/11/2026 na versão 0.166 do Codex e na documentação da OpenAI (learn.chatgpt.com, página "Image
generation", e developers.openai.com/codex/pricing).

- **Plano:** entre com `codex login` usando a conta do ChatGPT **paga**. No plano grátis o Codex não gera imagem.
  Cada imagem gasta o limite de uso do plano de 3 a 5 vezes mais rápido que uma mensagem comum.
- **Jeito interativo (o mais simples):** abra o terminal na pasta do estúdio, rode `codex` e escreva o pedido
  começando com `$imagegen`, que chama a ferramenta de imagem. Exemplo:

  ```
  $imagegen <cole aqui o prompt 1 preenchido>. Salve o PNG em canal/idv/arte/mascote_folha.png
  ```

  Para anexar a referência, abra o Codex já com ela: `codex -i canal/idv/arte/mascote_folha.png`.
- **Um pedido sem conversa (bom para a IA do estúdio rodar sozinha):**

  ```
  codex exec -i canal/idv/arte/mascote_folha.png --skip-git-repo-check -s workspace-write '$imagegen <prompt da pose>. Salve o PNG em canal/idv/arte/acenando.png'
  ```

  Ponha o `-i` (anexo) **antes** do texto do pedido: ele aceita vários arquivos e, depois do texto, engoliria o
  pedido como se fosse mais uma imagem. Sem pedir para salvar na pasta, a imagem fica em
  `~/.codex/generated_images/`. Use aspas simples em volta do pedido (no PowerShell e no Terminal do Mac), senão o
  `$imagegen` vira variável e some.
- Depois, o mesmo caminho do ChatGPT: recortar o fundo e rodar o gerador.
