<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Ganchos: o primeiro segundo

O gancho é o começo do vídeo: a primeira imagem e a primeira frase. É ali que a pessoa decide, em menos de um
segundo, se passa o dedo ou fica. Num canal real feito com este método, **75% das pessoas saíram nos 10 primeiros
segundos** quando o começo era só explicação (Dia 1 da Cobaia Social, 31/10/2026). O resto do vídeo não importa se o
gancho não segura.

Este arquivo tem as regras, os casos reais e o teste de aberturas. Os moldes prontos de cada estilo ficam em
`kit/prefs/ganchos.json`, e a trava que confere o gancho é `kit/qa/gancho.py`.

## As regras do primeiro segundo

1. **Imagem e texto grande já no quadro 0.** Nada de tela preta, logo, título ou fade de entrada. O primeiro quadro
   já é a imagem mais forte do vídeo (a nojenta, a absurda, a ameaça acontecendo, o resultado pronto).
2. **A voz entra até 0,3 s.** Silêncio no começo parece vídeo travado. A trava para o render se a fala começar
   depois de 0,5 s (preferência "Imagem e texto antes da fala").
3. **O bloco 1 cabe em 3 s** (preferência `ganchos.gancho_max_s`). Na prática, **até 7 palavras**. Passou um pouco,
   a trava avisa; passou mais de 1 s, ela para. Se a ideia não cabe, divida: a primeira frase vai no bloco 1 e a
   contradição vem colada no bloco 2.
4. **Um estranho entende a premissa inteira nesse tempo.** Quem chega pelo Explorar nunca viu o canal. Nunca abra
   com "ontem", "parte 4", "final" ou placar: na parte 2 em diante, o placar entra **depois** do gancho, perto dos
   10 s.
5. **Texto da tela curto**: até 7 palavras, que se leem num relance. Muita gente assiste sem som.
6. **O gancho abre uma lacuna**: uma pergunta na cabeça de quem assiste, que só o vídeo responde.

## O que é lacuna (e o que não é)

A trava procura sinais de lacuna na fala do bloco 1:

| Abre lacuna | Exemplo |
|---|---|
| Pergunta | "Por que todo avião é branco?" |
| Negação ou contradição | "A geladeira não faz frio." |
| Número ou hora | "Meia-noite. O elevador desceu. Ninguém chamou." |
| Apontar para a imagem ("isso", "essa", "olha") | "Seu corpo faz isso. Você nunca reparou." |
| "Ninguém", "nunca", "nada" | "Ninguém sabia que eram irmãos. Nem eles." |
| Virada ("mas", "só que") | "Passou na prova. Só que não fez." |
| "Quase", "falta", "sozinho" | "Quase beijou. Até a porta abrir." |
| Afirmação que surpreende | "Esse peixe anda. Nem é o pior." |

| Não abre lacuna (a trava para) | Por quê |
|---|---|
| "Oi, gente!", "Fala, galera", "Bem-vindos" | Cumprimento gasta o segundo mais caro do vídeo |
| "Neste vídeo eu vou mostrar...", "Hoje vamos falar de..." | Anuncia o vídeo em vez de começar |
| "Vem comigo", "Bora lá" | Pede atenção sem dar motivo |
| "A história do Titanic." | Só descreve o assunto: a pessoa entende do que é e vai embora |
| "Você sabia que..." sozinho | Fraco: diga o fato surpreendente direto, com o número na frente |

Quando a trava reprova, ela explica o motivo e dá o molde para reescrever: **comece pelo que não devia acontecer ou
pela imagem mais forte, com um número ou uma hora e uma contradição.**

## Casos reais

Resultados pessoais, com data. Views dependem de vários fatores; nada aqui é garantia.

- **A mesma abertura em todo episódio** (série de comédia com voto, Cobaia Social, out-nov/2026). Toda parte abre
  com a promessa e a realidade lado a lado, numa frase curta, sempre igual. Quem nunca viu entende em 2 s; quem
  segue reconhece no primeiro quadro. No seu canal, crie a sua frase fixa no mesmo molde (ex.: "O anúncio
  prometia isso. Chegou isso."), sem copiar a de outro canal.
- **O erro do Dia 1** (31/10/2026): os 10 s iniciais eram só explicação (a frase do problema, a tela dividida, o
  chat). A curva caiu para 25% em 10 s. Depois disso, o antes e depois ou a imagem nojenta passou a abrir o episódio,
  nos 3 a 5 primeiros segundos.
- **O episódio mais visto do perfil** (Cobaia Social, temporada 2, ep. 1, 04/11/2026; 610 mil views no painel do
  Instagram em 06/11/2026). Abertura: as duas imagens lado a lado, o número despencando na tela ("de 92% para 3%")
  e um evento **hoje**, com hora marcada e alguém da família de testemunha. O fim também é visual (um botão voando
  na medalha do sogro), não uma frase.
- **O "1,3 milhão"**: não foi um vídeo só. Foi o perfil inteiro da Cobaia Social, cerca de 1,3 milhão de views em 9
  Reels, em 4 dias e 10 horas, começando do zero (print de 05/11/2026). Os ganchos que puxaram esse número são os
  três acima.
- **Terror com voto** (canal real de terror com voto, out-nov/2026): hora exata, a ameaça já acontecendo e uma contradição até
  3 s ("a luz acendeu sozinha; ninguém mora lá faz dez anos"), com texto que se entende sem som.

## Teste de aberturas (A/B)

Antes da voz, a IA propõe **3 aberturas** diferentes (preferência `ganchos.variacoes_ab`, de 1 a 5), cada uma vinda
de um molde diferente do estilo. Cada proposta traz o quadro 0 (o que aparece), a fala e o texto da tela. Você
escolhe uma; a trava confere a escolhida.

Como testar sem enganar a si mesmo:
1. **Uma mudança por vez.** Troque só o gancho e mantenha o resto do formato igual por 2 ou 3 episódios.
2. **Meça o mesmo número**: os "pulados" (ou "deslizaram") do painel da rede, 2 dias depois de postar.
3. **O gancho que ganhou vai para "Meus ganchos"** (preferência `ganchos.biblioteca_extra`). A IA passa a usar os
   seus moldes primeiro.
4. Se a rede oferecer um teste próprio (o "Reel de teste" do Instagram, que mostra o vídeo primeiro para quem não
   segue), use para comparar duas aberturas do mesmo episódio.

## Moldes por estilo

Os moldes completos (molde, por que funciona, de onde veio e 2 ou 3 exemplos curtos) estão em
`kit/prefs/ganchos.json`, para os 13 estilos. Resumo:

| Estilo | Molde principal |
|---|---|
| Série 2D com voto | Promessa contra realidade, lado a lado; evento hoje com testemunha; o nojento no quadro 0 |
| Terror com voto | Hora exata + ameaça acontecendo + contradição até 3 s |
| POV | "Você" num lugar comum, e algo que não devia acontecer |
| Explicativo 3D | A pergunta do dia a dia com o objeto em corte; a resposta errada desmentida |
| Novela anime | O momento mais quente congelado um segundo antes; o segredo com a pessoa errada ouvindo |
| Novela de frutas | A acusação com a prova na mão na primeira fala; o bebê com a cara de outra fruta; a testemunha na fresta da porta |
| Tipografia | A frase que derruba uma crença; um número exato e estranho |
| Faceless | A imagem mais estranha do tema; a pergunta que ninguém pensou |
| Top 5 | A promessa com "nunca" ou "ninguém"; o item mais estranho primeiro |
| História real | O momento mais estranho sem explicar; o fim primeiro |
| Antes e depois | O antes mais feio + "dá pra salvar isso?"; o número do esforço |
| Bastidores | O resultado já na tela; o erro que custou caro |
| Quiz | O desafio com a taxa de acerto; a pergunta direto |

Os exemplos são para entender o molde. Escreva o seu gancho a partir do nicho do canal.

## Conferir um gancho

A partir da pasta `kit/`:

```
python qa/gancho.py "Seu corpo faz isso. Você nunca reparou." --tela "VOCÊ NUNCA REPAROU"
```

Sem `--dur`, o tempo é estimado pelo ritmo médio da fala. No motor de cartelas a conferência é automática: antes da
voz (tempo estimado, para não gastar voz com gancho fraco) e depois da voz (tempo real).
