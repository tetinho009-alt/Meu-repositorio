<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# IA de vídeo: novelinha de fruta e outros vídeos gerados

Vídeo em que cada cena é gerada por uma IA de vídeo (Seedance, Kling ou MiniMax), com a conta do próprio usuário.
O formato mais pedido é a **novelinha de fruta**: frutas com rosto vivendo um drama de novela (traição, herança,
casamento, segredo de família), com gancho no fim de cada episódio.

Ferramenta: `kit/video_ia.py`. A conta se liga no painel, tela **IA de vídeo** (fal.ai ou Higgsfield). A chave nunca
passa pelo chat.

## Dinheiro primeiro (regra que não se pula)

1. Cada clipe é cobrado do saldo do usuário, por segundo. Antes de gerar, rode
   `python video_ia.py custo --modelo <m> --segundos <s>` para cada cena e mostre a soma num quadro curto:
   cenas, segundos, custo por cena e total. Diga que costuma sair o dobro, porque sempre há cena para refazer.
2. Só gere depois do "pode" do usuário, e passe o teto de cada clipe em `--ate-usd`. O script recusa sozinho se o
   orçamento passar do teto. Nunca suba o teto por conta própria.
3. Comece por **uma cena** e mostre o resultado antes de gerar as outras.
4. Se o envio cair no meio ("a internet caiu no envio"), **não reenvie**: peça ao usuário para conferir no site da
   conta se o pedido entrou. Reenviar pode cobrar duas vezes.
5. Gasto do mês: `python video_ia.py gastos` (aparece também no painel).

## Qual modelo

| Modelo | Quando usar | Fala |
|---|---|---|
| `seedance` | Novelinha com diálogo. Aceita várias imagens de referência: as frutas ficam iguais em todas as cenas | Português, com a boca sincronizada |
| `kling` | Cena de ação ou de movimento bonito, a partir de uma imagem | Só inglês ou chinês: deixe o áudio desligado e use a voz do narrador do kit |
| `minimax` | Testar o roteiro gastando pouco | Sem fala: voz do narrador do kit |

`python video_ia.py modelos` mostra os preços atuais e quais contas estão ligadas.

## O padrão da novelinha das frutas

No catálogo de estilos é o **Novela de frutas** (`metodo/estilos/novela-frutas.md`, a ficha curta). Esta seção é o padrão
completo.

É o formato que viraliza no Brasil: besteirol e bobagem de novela, com frutas de corpo humano falando português.
Os episódios são curtos e seriados. Siga este padrão, a não ser que o usuário peça outro.

### Visual

- **3D de cinema**, no acabamento de filme de animação: luz quente, fundo desfocado, pele com brilho. Nada de
  desenho chapado.
- **Corpo humano adulto, cabeça de fruta**. O rosto é desenhado na própria fruta, com olho grande, sobrancelha
  expressiva e boca que fala. A **pele do corpo tem a textura da fruta**: escama de abacaxi no braço, semente de
  morango no ombro, casca de banana no pescoço.
- **Personagens atraentes, de propósito**: o macho musculoso, peitoral e braço marcados, galã; a fêmea linda,
  curvilínea e sarada, de barriga definida, maquiada, cabelo e unha feitos. Roupa justa de academia, vestido de festa,
  biquíni e sunga na praia ou na piscina: tudo isso pode, como em qualquer filme ou novela. É o charme da trend: corpo
  bonito com cara de fruta. O público dessas novelinhas é adulto e gosta do galã e da gostosa da história.
- **Roupa e acessório brasileiros**, que dão o personagem: regata, conjunto de academia, conjunto de moletom, chinelo,
  correntinha de ouro, argola grande, óculos escuros, unha feita, cílio e batom na personagem.
- **Cenário brasileiro de verdade**: rua de comunidade com caixa d'água e fio de poste, cozinha com café e pão de
  queijo, academia de bairro, sala com sofá, cerveja e salgadinho, salão de beleza, churrasco na laje.
- **Na tela**: o título fixo em cima ("FRUTAL EP. 01 | Quem é a Melância?") e o nome do personagem na primeira vez
  que ele aparece. Notificação de celular, conversa de WhatsApp e foto vazada entram como inserto: é o gatilho de
  metade das tramas.

### Elenco fixo

O elenco é a série. Monte de 3 a 6 frutas no primeiro episódio e guarde em `canal/novelinha/elenco.md`, com nome,
fruta, personalidade, roupa e o caminho da imagem. Use os mesmos personagens e as mesmas imagens em todo episódio.

- **Nome com trocadilho**, no aumentativo ou no diminutivo: Moranguete, Bananildo, Abacaxita, Pimentudo, Limãozão,
  Melância, Uvinha, Abacatudo.
- **Um papel por fruta**, fácil de lembrar: a ciumenta, o safado que sempre é pego, o personal convencido, a
  patricinha que ficou rica, o sogro, a outra, o fofoqueiro que observa da janela.
- **Imagem de referência de cada um**: de frente, corpo inteiro, fundo liso, vertical, com a roupa do personagem.
  Pedido base para a IA de imagem, trocando o que está entre colchetes:
  `Cinematic 3D animated character, full body, front view, plain light background, vertical. An adult [woman/man] with an athletic [curvy/muscular] human body and a [strawberry] as the head, the face drawn on the fruit with big expressive eyes, [long eyelashes and lipstick]. The skin has the [strawberry] texture. Wearing [a pink tracksuit, gold chains, big hoop earrings, white sneakers]. Attractive, confident pose, comedic.`
- Se a IA de vídeo errar o personagem, a culpa costuma ser da imagem: refaça a imagem antes de gastar com vídeo.

### Roteiro do episódio

- **De 10 a 35 s**, com **2 a 5 cenas** de 4 a 8 s. Curto e seriado ganha de longo.
- **A 1ª fala vem no 1º segundo** e já é o conflito ("Amor, quem é Melância?"). Sem apresentação.
- **Diálogo curto em português**, no máximo 12 palavras por cena de 5 s, com o jeito de falar do personagem ("Oxi,
  morangão!", "Que isso, sogrão?"). O `seedance` faz a boca falar certo.
- **Flerte, cantada e ciúme de novela** valem e rendem comentário: a fruta que se acha a mais bonita do bairro, o
  galã que todo mundo quer, a vizinha que provoca a ciumenta.
- **Uma situação de besteirol por episódio**: o Bananildo pego pela notificação, o personal Pimentudo que dá em cima
  da aluna, a Moranguete que ficou rica e voltou na comunidade, o sogro que acha o genro forte demais.
- **Fim em gancho ou na piada**: a cara de culpa, o "Eu sabia!", o Limão de óculos escuros espiando da janela. A
  pergunta do próximo episódio vira o voto (ver `metodo/comunidade-e-votos.md`).
- A CTA do canal pode virar fala de personagem ("Quer saber meu segredo? Me inscrevi no canal!"), uma vez a cada
  poucos episódios, nunca em todos.

### O limite

Atraente pode; o que corta o alcance é o **enquadramento sexual**, não o corpo bonito. A linha:

- **Pode**: corpo sarado e curvilíneo, roupa justa, biquíni e sunga na praia, maquiagem, pose confiante, flerte,
  cantada, beijo rápido de novela.
- **Não pode**: nudez, roupa transparente, câmera fechada em bunda, peito ou virilha, rebolado ou gesto sexual, cena
  de cama, fala de sexo. Nenhuma fruta com cara ou corpo de criança. Assédio, violência e humilhação de mulher não
  são piada.
- O motivo é alcance. O Instagram não recomenda a quem não segue o conteúdo "sexualmente sugestivo" (o exemplo
  oficial é roupa transparente), e quem repete perde a recomendação da conta inteira por um tempo. O TikTok tira esse
  conteúdo do Para Você. A câmera em plano médio ou de corpo inteiro, com a piada no rosto, resolve.
- No pedido para a imagem e para o vídeo, descreva o corpo e a roupa ("attractive", "gorgeous", "handsome",
  "muscular", "curvy", "fit", "bikini", "fitted gym outfit") em vez de pedir clima ("sexy", "sensual", "seductive").
  O pedido descritivo dá o mesmo personagem bonito e passa mais na moderação; se uma cena for recusada, tire primeiro
  as palavras de clima.
- **Nunca** use nome de programa ou marca famosa ("Love Island", nome de novela) no título, na fala ou na capa. Não
  cole meme, vídeo nem foto de terceiros no meio do episódio: é direito autoral e derruba o vídeo.

### A música

- **Besteirol e humor**: a trilha do saxofone da trend (busque "BATIDA FUNK MEDLEY" no som do aplicativo),
  começando **no saxofone**, sem o teclado do começo, do primeiro ao último segundo.
- **Novela triste** (traição que dói, despedida, a fruta chorando na chuva): "Kamin", de EMIN com JONY, do começo ao
  fim.
- A música fica **baixa embaixo da fala**: o diálogo precisa ser entendido.

As duas são músicas comerciais, lançadas por gravadora ou distribuidora e registradas no reconhecimento automático de
direitos autorais do YouTube, do Instagram e do TikTok. Por isso:

1. **Não** baixe a música do YouTube nem de site de download para colar no vídeo. A rede reconhece, silencia o áudio
   ou bloqueia o vídeo, e o vídeo perde o vínculo com a página do som, que é o que leva à trend.
2. **O caminho certo** é montar o vídeo **só com as falas** e pôr a música **dentro do aplicativo**, na hora de
   postar:
   - No TikTok e no Instagram, toque em "Adicionar som", busque a música, arraste o trecho para o ponto certo (no
     sax, no caso da trend) e baixe o volume do som para a fala aparecer.
   - No Shorts, use "Som" e faça o mesmo.
   - Escreva esse passo a passo no pacote das redes do episódio, com o nome da música e o ponto de início.
3. Se o usuário tiver o arquivo da música **com licença** (comprou ou é dele), dá para colar no vídeo todo, mixado
   embaixo da fala, começando em `<inicio>` segundos e com 1 s de saída suave no fim (`<dur>` é a duração do vídeo):
   `ffmpeg -i video.mp4 -ss <inicio> -i musica.mp3 -filter_complex "[1:a]volume=0.25,afade=t=out:st=<dur-1>:d=1[m];[0:a][m]amix=inputs=2:duration=first:normalize=0[a]" -map 0:v -map "[a]" -c:v copy -c:a aac video_com_musica.mp4`
   Nunca suba esse arquivo com música de terceiro sem licença.

## Passo a passo

1. **Elenco (só no 1º episódio da série):** monte o elenco fixo (ver "Elenco fixo"), gere a imagem de cada fruta
   na IA de imagem que o usuário tiver (ver "Imagens" em `metodo/estilos/novela-anime.md`) ou use uma imagem dele.
   Mostre as imagens e espere o "aprovado". Guarde em `canal/novelinha/elenco/<nome>.png` e anote em
   `canal/novelinha/elenco.md`. Essas mesmas imagens vão em **todas** as cenas de **todos** os episódios: é isso que
   mantém o rosto igual.
2. **Episódio:** escreva em cenas, uma linha por cena: onde, quem, o que acontece, a fala e a duração; mais o título
   fixo da tela e a música (besteirol ou triste). Mostre ao usuário e espere o "aprovado". Guarde em
   `canal/novelinha/ep<NN>.md`, para o próximo episódio continuar a história.
3. **Orçamento:** o quadro do "Dinheiro primeiro", com o "pode" do usuário.
4. **Pedido de cada cena** em `kit/trabalho/<episodio>/cenas/cena01.txt`, em inglês simples para a imagem e a fala em
   português entre aspas. No `seedance`, cite as referências como `@Image1`, `@Image2` na ordem das `--imagem`.
   Exemplo:
   `Vertical 9:16, cinematic 3D animation, warm light, cozy Brazilian kitchen at breakfast. @Image1 (Moranguete, gorgeous strawberry-headed woman) looks at her phone, then raises an eyebrow at @Image2 (Bananildo, banana-headed man), who starts sweating, guilty face. Medium shot, comedic. She says in Brazilian Portuguese: "Amor, quem é Melância?"`

   A moderação recusa até briga de desenho: "slams", "shouts angrily", "hits". Faça o drama pela **cara**
   (sobrancelha levantada, suor de culpa, boca aberta, olhar de lado, lágrima de novela) e escreva "comedic". Recusa da moderação não é cobrada, mas atrasa: no teste de 16/11 um pedido com "slams the table and
   shouts" voltou recusado, e a versão com susto e mão no peito passou.

   O vídeo só faz o gesto que o corpo da imagem permite: no teste, uma fruta sem braço com "hand on her chest" ganhou
   uma bolha no lugar da mão. Com o elenco de corpo humano, isso não acontece.
5. **Gerar:** uma cena por vez,
   `python video_ia.py gerar --modelo seedance --prompt-arquivo trabalho/<ep>/cenas/cena01.txt --imagem ../canal/novelinha/elenco/moranguete.png --imagem ../canal/novelinha/elenco/bananildo.png --segundos 6 --saida trabalho/<ep>/clipes/cena01.mp4 --ate-usd 1.50`
6. **Conferir cada clipe** antes de seguir: extraia 3 quadros com o ffmpeg (início, meio, fim) e olhe. Rosto
   diferente, fruta errada, mão a mais ou fala cortada: diga ao usuário o que saiu errado e quanto custa refazer.
   Refaça só aquela cena, com o ok dele.
7. **Montar:** junte os clipes com o ffmpeg (corte seco, mesma resolução), ponha o título fixo e a legenda queimada
   do kit e, no `kling` ou no `minimax`, as falas na voz do kit (`metodo/voz.md`). A música entra no aplicativo, na
   hora de postar (ver "A música"). Termine no pacote das redes (`comandos/publicar.md`), com o nome da música e o
   ponto de início.
8. **Rótulo de IA ligado** ao postar em todas as redes (`metodo/seguranca.md`), e "história fictícia" na legenda.

## Erros comuns

| Erro | O que fazer |
|---|---|
| "Nenhuma conta de IA de vídeo ligada" | Mande o usuário para o painel, tela IA de vídeo |
| "Esse clipe custa ... e o teto autorizado é ..." | Mostre o custo e peça o ok; não aumente o teto sozinho |
| "Saldo insuficiente" | O usuário coloca saldo no site da conta |
| "a moderação recusou a cena" | Reescreva a cena sem violência ou conteúdo adulto; não é cobrado |
| Rosto muda entre cenas | Use o `seedance` com as mesmas imagens de referência em todas as cenas, na mesma ordem |
