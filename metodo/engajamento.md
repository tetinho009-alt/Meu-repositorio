<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Engajamento: voto, comentário, horário e números

O gancho faz a pessoa ficar (`metodo/ganchos.md`). Este arquivo cuida do resto: o que faz ela comentar, voltar
amanhã e mandar para alguém, sem cair nas regras que fazem a rede esconder o vídeo (`metodo/licoes.md`, itens 26 a
29). Os valores entre parênteses são preferências do canal, que você muda no painel ou na conversa.

## 1. O voto da próxima parte

O fim de cada episódio de série é uma **pergunta aberta** na voz. As duas saídas aparecem só no cartão de voto, na
tela:

- Bom: na voz, "E amanhã, ele resolve o quê primeiro?"; na tela, "1 · BARRIGA" e "2 · OLHO".
- Bom: na voz, "E agora? O que ela faz?"; na tela, "1 · ABRE A PORTA" e "2 · FOGE PELA JANELA".
- Ruim: "Comenta BARRIGA ou OLHO." / "Comenta 1 ou 2." / a voz falando as duas opções ("ela abre a porta ou foge
  pela janela?"). Ditar a escolha vira isca, e a Meta rebaixa.

Regras do voto:
1. **Dois problemas diferentes**, nunca dois jeitos de fazer a mesma coisa.
2. **Os dois caminhos existem antes do voto**: escreva os dois para não precisar inventar depois.
3. **O que venceu dá certo e fica.** Desfazer o que a galera escolheu frustra quem votou.
4. **Placar real**: a parte seguinte abre com o resultado verdadeiro, logo depois do gancho (nunca antes).
5. As mesmas duas palavras do voto aparecem no cartão de voto, na capa e na legenda (na voz, nunca).

(Preferência `roteiro.tipo_voto`: "pergunta_aberta" ou "sem_voto".)

## 2. Uma virada a cada 15 segundos

A curva de retenção cai onde nada muda. A cada 15 s no máximo (`roteiro.viradas_max_s`), algo vira: um "só que...",
"mas", "até que", "de repente", um item novo, uma revelação. No motor de cartelas, a trava avisa o trecho que passou
do limite. Três cenas iguais seguidas (a mesma mecânica repetida) também derrubam a curva.

## 3. A chamada no meio (só se você vende algo)

Se o canal tem um produto ou serviço (`roteiro.cta_meio` ligado), o vídeo ganha **uma** fala no meio, com a frase de
`roteiro.cta_meio_frase` (ex.: "aprenda a fazer vídeos assim pelo link na bio"):

1. **Uma vez só**, e **só na voz**: nada na tela, na legenda ou no comentário fixado.
2. **Ligada ao tema** do episódio.
3. **Logo depois de uma pergunta aberta** (ex.: depois de "qual dos três?" e antes da resposta). É o ponto de maior
   retenção do vídeo. Nunca depois de uma resolução, quando a pessoa já tem o que queria.
4. **Sem domínio, sem @, sem preço e sem "curso".**
5. Depois de postar, olhe o Status da conta por 48 h. Se aparecer aviso ou o alcance cair muito, tire a fala.

Sem produto, não tem chamada no meio: o vídeo inteiro é história.

## 4. O fim: um "quase"

O episódio termina com algo que **quase** dá errado (`roteiro.fechamento_quase`), numa imagem, não numa frase de
resumo. O "quase" vem de outro problema, nunca do que acabou de ser resolvido. É ele que faz a pessoa seguir para ver
a próxima parte. Depois do voto, o cartão de cada rede pede para seguir (o kit coloca sozinho, um por rede).

## 5. Legenda que puxa comentário

A legenda repete a pergunta do vídeo em forma aberta, ligada ao conteúdo:

- Bom: "Ela devia ter aberto a porta? Amanhã sai a parte 3. Ficção · narração com voz sintética."
- Bom (explicativo): "Qual desses você não sabia? Fonte: ..."
- Ruim: "Comenta QUERO", "manda pra 5 amigos", "marca alguém", "curte e compartilha", "me chama na DM".

Sempre: "Ficção" (série) ou "Fonte" (explicativo) no texto, rótulo de IA ligado com voz sintética, nenhum link,
domínio ou @ de outra conta. O pacote confere isso sozinho e para se achar isca.

## 6. Compartilhamento: nunca pedir

Pedir para compartilhar, ou prometer algo em troca ("se chegar a X envios..."), tira o vídeo da recomendação para
quem não segue. O que faz alguém mandar para um amigo é **identificação** ("todo mundo tem um amigo assim") e um
episódio que **se explica sozinho** para quem nunca viu a série. Se quiser usar o número de envios na história,
conte só o que já aconteceu, com o número real do episódio anterior.

## 7. Quando postar

- **Constância vale mais que o horário perfeito.** Poste no mesmo horário todo dia (`redes.horario`, recomendado
  entre 18h e 21h): quem segue aprende a esperar o próximo.
- **No máximo 2 posts por dia na mesma conta.**
- Partes de uma série em dias seguidos: o voto esfria em 48 h.
- As redes saem do pacote numeradas na ordem de postagem (`redes.escolhidas`).

## 8. O que medir e o que muda no próximo

Espere 2 dias (`metricas.dias_para_medir`): número de poucas horas engana. Abra o painel da rede (Insights do
Instagram, Estatísticas do TikTok, YouTube Studio) e anote, de preferência com o filtro "não seguidores":

| Número | Onde | O que ele diz | Se estiver ruim, no próximo episódio |
|---|---|---|---|
| Pulados (ou "deslizaram") | Insights do Reel | Se o gancho segurou | Reescreva o bloco 1 (`metodo/ganchos.md`) e teste outra abertura |
| Curva de retenção | Insights do Reel | Onde as pessoas saem | Queda perto dos 10 s: mostre o resultado ou a transformação nos 3 a 5 s. Queda no meio: ponha uma virada antes desse ponto |
| Tempo médio | Insights do Reel | Se a história segura | Abaixo de 30% da duração: corte o trecho que arrasta e a cena repetida |
| Compartilhamentos | Insights do Reel | Se quem não segue entende e se identifica | Episódio que se explica em 3 s e um momento de identificação; nunca pedir |
| Comentários | Insights do Reel | Se a pergunta pegou | Pergunta aberta mais cedo, no meio; voto com duas saídas claras |
| Salvamentos | Insights do Reel | Se vale rever | Em explicativo, top 5 e quiz: um número, uma lista ou um passo a passo para guardar |
| Curtidas | Insights do Reel | Se entregou a satisfação prometida | Mostre a vitória com a imagem, não só com a fala |

Para anotar e receber as sugestões, a partir da pasta `kit/`:

```
python metricas.py --episodio parte_2 --rede instagram --registrar --pulados 32,4 --compartilhamentos 0,1 --comentarios 0,2
```

Os números ficam em `canal/metricas.json`, com a data, e `python metricas.py --historico` mostra todos.

### Referência de um canal real

Resultado pessoal de um canal feito com este método (Cobaia Social, série de comédia com voto no Instagram). Views
dependem de vários fatores; os números servem de bússola, não de meta garantida.

| Data | Vídeo | Número | Leitura |
|---|---|---|---|
| 31/10/2026, 1 h no ar | Dia 1 (2:05) | A curva caiu para 25% até os 10 s; tempo médio de 34 s | O começo era só explicação. Daí veio a regra de mostrar a transformação nos 3 a 5 s |
| 02/11/2026, 3 h no ar | Dia 6 | Pulados 32,4%, curtidas 10,2%, salvamentos 0,8% (o painel marcou "melhor que o normal") | O gancho funcionou |
| 02/11/2026, 3 h no ar | Dia 6 | Compartilhamentos 0,1% e comentários 0,2% ("pior que o normal") | "Dia 6 de 7" não se sustentava sozinho para quem não seguia. A temporada 2 passou a abrir com a premissa inteira em 3 s |
| 05/11/2026 | Temporada 2, ep. 2 | Tempo médio de 1 min 14 s; 11,7 mil comentários em 7 h | O voto em pergunta aberta virou o comentário |
| 06/11/2026 | Temporada 2, "o queixo ganhou o voto" | 54 mil comentários | Os comentários são o voto |

Uma regra para ler qualquer número: **não tire conclusão de um vídeo só.** Compare com a média dos seus 3 últimos e
mude uma coisa por vez.
