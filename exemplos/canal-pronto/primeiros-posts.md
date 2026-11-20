<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Primeiros posts do Bicho Esquisito (exemplo)

Três ideias para abrir o canal, no formato do kit: a linha da pauta (igual a `canal/pauta.md`) e o roteiro de cada
uma no formato do motor de cartelas (`kit/cartelas/modelos/`). Para fazer de verdade, copie o roteiro para uma pasta
de trabalho como `roteiro.json`, ponha a voz do seu canal no campo `voz` e rode, a partir de `kit/`,
`python cartelas/rodar.py <pasta>`.

**Todo fato tem fonte, e a fonte é conferida antes de gravar** (regra do kit: `metodo/licoes.md`). As fontes abaixo
são o ponto de partida da pesquisa, não dispensam a conferência.

## A pauta

| ★ | Formato | Ideia (premissa ou pergunta de título) | Escolha do EP1 / gancho | Status |
|---|---|---|---|---|
| ★ | quiz com voto (série Bicho ou Lenda?) | Parte 1 · O peixe que anda: um bicho que vive com cara de filhote existe ou é invenção? | gancho: "Tem um bicho no México que passa a vida inteira com cara de filhote." Voto: BICHO ou LENDA; a resposta sai na parte 2 | ideia |
| ★ | top 5 | 5 bichos que parecem inventados (e existem) | gancho: "Esses cinco bichos parecem mentira. Nenhum é." O número 1 vira teste | ideia |
| | quiz | Verdade ou lenda: quase ninguém acerta as três | gancho: "Quase ninguém acerta as três. Vamos ver você." | ideia |

Por que nessa ordem: a parte 1 da série abre a pergunta que traz a pessoa de volta (a resposta só sai na parte 2); o
top 5 é o mais rápido de fazer e testa a voz e a legenda; o quiz é o que mais rende comentário de "acertei".

## 1. Bicho ou Lenda? Parte 1 · O peixe que anda

- **Estilo:** quiz e escolha (`metodo/estilos/quiz.md`), com o bloco de voto no fim. **Duração:** 30 a 40 s.
- **Gancho (0 a 3 s):** texto grande "CARA DE FILHOTE A VIDA TODA" e a voz contando o absurdo, sem dizer o nome do
  bicho.
- **Capa:** a do exemplo (`exemplos/canal-pronto/modelos/exemplo/capa_episodio.jpg`): o Bubi surpreso, BICHO ou LENDA nas etiquetas.
- **Parte 2 (a resposta):** existe. É o axolote, que não é peixe: é um anfíbio, parente da salamandra. Vive nos
  canais de Xochimilco, na Cidade do México, e está criticamente ameaçado na natureza.

```json
{
  "estilo": "quiz",
  "titulo": "Bicho ou lenda? O peixe que anda",
  "capa": "BICHO OU LENDA?",
  "capa_rotulo": "PARTE 1",
  "parte": 1,
  "proximo": "a resposta: bicho ou lenda",
  "fontes": [
    "IUCN Red List: Ambystoma mexicanum (axolote), Criticamente em Perigo",
    "Haas e Whited (2017), Trends in Genetics: regeneração dos membros do axolote"
  ],
  "post": {
    "texto": "Ele anda no fundo do lago, sorri o tempo todo e passa a vida com cara de filhote. Existe ou é invenção? A resposta sai na parte 2.",
    "hashtags": ["#curiosidades", "#bichos", "#bichooulenda"]
  },
  "blocos": [
    {"tipo": "gancho", "fala": "Tem um bicho no México que passa a vida inteira com cara de filhote.",
     "tela": "CARA DE FILHOTE A VIDA TODA", "destaque": ["A VIDA TODA"]},
    {"tipo": "texto", "fala": "Chamam ele de peixe que anda, porque ele caminha no fundo do lago.",
     "tela": "O PEIXE QUE ANDA", "destaque": ["ANDA"]},
    {"tipo": "texto", "fala": "Ele tem umas plumas cor-de-rosa dos lados da cabeça, e é por elas que respira.",
     "tela": "RESPIRA POR PLUMAS", "destaque": ["PLUMAS"]},
    {"tipo": "texto", "fala": "E se perde uma pata, faz uma pata nova.",
     "tela": "PERDEU A PATA? FAZ OUTRA", "destaque": ["FAZ OUTRA"]},
    {"tipo": "voto", "fala": "E aí: esse bicho existe ou é invenção da internet?",
     "tela": "BICHO OU LENDA?", "opcoes": ["BICHO", "LENDA"]},
    {"tipo": "fim", "fala": "A resposta sai na parte dois.", "tela": "A RESPOSTA SAI NA PARTE 2",
     "destaque": ["PARTE 2"]}
  ]
}
```

## 2. 5 bichos que parecem inventados (e existem)

- **Estilo:** curiosidades e top 5 (`metodo/estilos/top5.md`). **Duração:** 40 a 55 s.
- **Gancho (0 a 3 s):** "5 BICHOS QUE PARECEM MENTIRA" com "MENTIRA" em destaque.
- **O número 1 é teste:** a pessoa chuta antes da revelação, com a contagem de 3 s.

```json
{
  "estilo": "top5",
  "titulo": "5 bichos que parecem inventados (e existem)",
  "capa": "PARECEM MENTIRA",
  "capa_rotulo": "TOP 5",
  "parte": 1,
  "proximo": "5 bichos que aguentam o impossível",
  "fontes": [
    "Australian Museum: fichas do peixe-bolha e do ornitorrinco",
    "Smithsonian Ocean: polvo (três corações, sangue azul)",
    "Grutter e outros (2011), Biology Letters: o casulo de muco do peixe-papagaio",
    "Jönsson e outros (2008), Current Biology: tardígrados expostos ao espaço na missão FOTON-M3"
  ],
  "post": {
    "texto": "Cinco bichos que parecem invenção e existem de verdade. O número 1 aguentou ficar solto no espaço. Qual desses você não sabia?",
    "hashtags": ["#curiosidades", "#bichos", "#top5"]
  },
  "blocos": [
    {"tipo": "gancho", "fala": "Esses cinco bichos parecem mentira. Nenhum é.",
     "tela": "5 BICHOS QUE PARECEM MENTIRA", "destaque": ["MENTIRA"]},
    {"tipo": "item", "numero": 5, "fala": "Número cinco. O peixe-bolha só tem essa cara de geleia fora d'água. Lá no fundo do mar, ele tem forma de peixe normal.",
     "tela": "PEIXE-BOLHA"},
    {"tipo": "item", "numero": 4, "fala": "Número quatro. O ornitorrinco é mamífero, bota ovo, e o macho tem um esporão com veneno na pata de trás.",
     "tela": "ORNITORRINCO"},
    {"tipo": "item", "numero": 3, "fala": "Número três. O polvo tem três corações e sangue azul.",
     "tela": "POLVO"},
    {"tipo": "item", "numero": 2, "fala": "Número dois. Antes de dormir, o peixe-papagaio se enrola num saco de muco, tipo um mosquiteiro.",
     "tela": "PEIXE-PAPAGAIO"},
    {"tipo": "quiz", "fala": "E o número um. Qual desses bichos sobreviveu solto no espaço?",
     "tela": "QUEM SOBREVIVEU NO ESPAÇO?", "opcoes": ["TARDÍGRADO", "BARATA", "FORMIGA"], "certa": 0, "contagem": 3},
    {"tipo": "revela", "fala": "O tardígrado. Cientistas mandaram tardígrados secos para fora de uma nave, e parte deles voltou viva."},
    {"tipo": "fim", "fala": "Qual desses você não sabia?", "tela": "QUAL DESSES VOCÊ NÃO SABIA?", "destaque": ["NÃO"]}
  ]
}
```

## 3. Verdade ou lenda: quase ninguém acerta as três

- **Estilo:** quiz e escolha (`metodo/estilos/quiz.md`). **Duração:** 30 a 45 s.
- **Gancho (0 a 3 s):** o desafio, "QUASE NINGUÉM ACERTA AS TRÊS". Número no desafio ("só 1 em cada 10") só
  depois que o canal medir de verdade (enquete ou comentários): número inventado derruba a confiança.

```json
{
  "estilo": "quiz",
  "titulo": "Verdade ou lenda: quase ninguém acerta as três",
  "capa": "VERDADE OU LENDA?",
  "capa_rotulo": "QUIZ",
  "fontes": [
    "San Diego Zoo Wildlife Alliance: ficha do avestruz (não enterra a cabeça)",
    "Huffard, Boneka e Full (2005), Science: polvos que andam em dois braços",
    "San Diego Zoo Wildlife Alliance: ficha do camelo (a corcova guarda gordura)"
  ],
  "post": {
    "texto": "Três coisas que todo mundo já ouviu sobre bicho. Uma é verdade, duas são lenda. Quantas você acertou?",
    "hashtags": ["#quiz", "#curiosidades", "#bichos"]
  },
  "blocos": [
    {"tipo": "gancho", "fala": "Quase ninguém acerta as três. Vamos ver você.",
     "tela": "QUASE NINGUÉM ACERTA AS TRÊS", "destaque": ["AS TRÊS"]},
    {"tipo": "quiz", "fala": "O avestruz enterra a cabeça na areia quando tem medo.",
     "tela": "O AVESTRUZ ENTERRA A CABEÇA?", "opcoes": ["VERDADE", "LENDA"], "certa": 1, "contagem": 3},
    {"tipo": "revela", "fala": "Lenda. Ele abaixa a cabeça para virar os ovos no ninho, que é um buraco no chão. De longe, parece que enterrou."},
    {"tipo": "quiz", "fala": "Existe polvo que anda em duas pernas no fundo do mar.",
     "tela": "POLVO QUE ANDA EM DUAS PERNAS?", "opcoes": ["VERDADE", "LENDA"], "certa": 0, "contagem": 3},
    {"tipo": "revela", "fala": "Verdade. Alguns polvos andam em dois braços, disfarçados de alga ou de coco."},
    {"tipo": "quiz", "fala": "O camelo guarda água na corcova.",
     "tela": "ÁGUA NA CORCOVA?", "opcoes": ["VERDADE", "LENDA"], "certa": 1, "contagem": 3},
    {"tipo": "revela", "fala": "Lenda. A corcova é gordura, a reserva de energia dele."},
    {"tipo": "fim", "fala": "Quantas você acertou?", "tela": "QUANTAS VOCÊ ACERTOU?", "destaque": ["QUANTAS"]}
  ]
}
```

## Depois de postar

Anote cada vídeo em `canal/historico.md` com a nota que você der e, dois ou três dias depois, os números. O que der
certo vira regra em `canal/aprendizados.md`.
