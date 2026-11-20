<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Criar o estilo do canal

O estilo desenhado do kit é **recorte de papel colorido**: cada coisa na tela é uma peça de papel recortada à mão,
com a fibra do papel, um fio claro na borda do corte e a sombra dura de uma peça sobre a outra; o cenário é um
diorama em camadas. O que muda de canal para canal é sorteado a partir de 7 respostas: a caixa de papéis (as cores),
o jeito do corte, a textura do papel, a sombra, o corpo e o rosto do elenco, as fontes e a capa. Cada canal sai com
uma cara própria, que ninguém mais tem. Vale do EP1 até o fim da série (regra 8 do CLAUDE.md).

## 1. As perguntas

Faça uma pergunta por vez, com as opções numa linha cada. Aceite a resposta do jeito que o usuário falar e traduza
para a opção mais próxima. Se ele disser "tanto faz", escolha você e avise qual foi.

Liste as perguntas e as opções com:

```
python -m estilo_desenhado.estilo --perguntas
```

(rode da pasta `kit/`). São estas: clima, lugar, corte do papel, temperatura das cores, proporção dos personagens, o
que assusta (ou move) a história e textura do papel.

Grave as respostas em `trabalho/estilo/respostas.json`, uma chave por pergunta:

```json
{"clima": "sombrio", "lugar": "sertao", "recorte": "tesoura", "cor": "fria",
 "proporcao": "alongado", "ameaca": "criatura", "textura": "fibra"}
```

Respostas antigas (de antes do papel: `traco`, `papel_velho`, `vhs`, `dessaturada`...) são aceitas e viram a opção
mais próxima.

## 2. O sorteio

```
python -m estilo_desenhado.estilo --respostas trabalho/estilo/respostas.json
python -m estilo_desenhado.folha
```

O primeiro grava `kit/estilo.json` (com a semente, para repetir depois) e baixa as fontes do estilo. O segundo gera a
folha de prévia em `trabalho/estilo/folha.jpg`, com a caixa de papéis, o elenco de corpo inteiro e a ficha.

O que o sorteio decide, sempre dentro do mundo do papel:

- **caixa de papéis**: 5 papéis coloridos vivos da temperatura pedida (azul-petróleo, vinho, mostarda, verde-musgo,
  terracota...), o papel escuro do recorte (preto-azulado, preto-esverdeado ou vinho bem escuro), o papel claro das
  etiquetas e a cor que grita (destaque e as duas cores do voto);
- **corte**: tesoura, rasgado, picote ou estilete, e o quanto a borda foge da linha;
- **sombra projetada**: o lado, a distância e a força (dura, nunca borrada);
- **textura**: quanto de fibra, se tem pintinhas (reciclado) e quanto as camadas de neblina deixam passar (seda);
- **elenco**: três personagens (protagonista, adulto e idoso) com rosto redondo, oval ou em gota, olho de papel
  recortado, de botão ou em fenda, cabelo cortado na tesoura, roupas tiradas da caixa de papéis;
- **cenário**: quanto as cores viram papel da caixa, quanto a casa entorta (papel dobrado), o primeiro plano do
  plano aberto (capim de papel ou nada), o lado e o tamanho da lua;
- **fontes e capa**: letra gorda que parece recortada; capa em etiqueta, colagem ou faixa rasgada.

## 3. Portão: a folha

Mostre a folha e pergunte se ficou com a cara do canal. As saídas:

- **"sorteia de novo"**: rode o primeiro comando de novo, sem `--semente`. As respostas continuam as mesmas.
- **"muda X"** (por exemplo, "quero mais colorido"): ajuste a resposta que corresponde, grave o JSON e sorteie de novo.
- **"aprovado"**: o estilo fica. Anote em `canal/identidade.md` a linha
  `Estilo: semente <N>, <clima> · <corte> · <cor> · <proporção> · <textura>`.

O elenco da folha (três personagens, com nome e papel) é o elenco de partida. O usuário pode trocar nomes e roupas na
bíblia da série. Rosto e proporção seguem o estilo.

A ameaça do estilo é **o Rasgado**: uma silhueta alta arrancada de uma folha escura, borda rasgada com o branco da
fibra aparecendo, dois buracos recortados no lugar dos olhos com luz atrás e, quando "sorri", um rasgo torto
(`from estilo_desenhado.ameaca import Rasgado`; `Vulto` continua funcionando como nome antigo).

## Regras

- Não troque o estilo no meio de uma série. Estilo novo é série nova.
- O sorteio fica sempre dentro do mundo do papel recortado, com cores vivas. Isso é proposital: o canal tem de ter cara própria. Não tente
  forçar esse visual mexendo no `estilo.json` à mão.
- Os nomes do elenco também saem de uma lista própria, feita para não repetir personagem de canal conhecido. Se o
  usuário trocar um nome na bíblia, tudo bem: o nome é dele.
- Estilo gravado antes do recorte de papel (sem `"mundo": "papel"` no `estilo.json`) é refeito sozinho com as mesmas
  respostas e a mesma semente: o motor só desenha papel. Para fixar, rode o sorteio de novo com `--semente`.
- Episódio no estilo desenhado segue `metodo/formato-serio.md` (travas antes da prévia; clima sombrio ou melancólico
  termina sem cauda).
- Sem internet, o estilo é gravado e as fontes baixam depois (rode o primeiro comando de novo com internet).
