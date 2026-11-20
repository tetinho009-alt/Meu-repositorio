<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Painel: a parte visual do estúdio

Para quando o usuário diz "abre o painel", "painel", "quero ver no navegador", "configurar pelo painel" ou "onde
vejo os vídeos".

O painel roda só neste computador e mostra o que você fez: vídeos de cada rede com capa e legenda, status da
máquina, canal, redes, jeito dos vídeos, estilos, personagens, ganchos, métricas e chaves. Ele **só mostra e
configura**: mudança de vídeo, roteiro ou cena o usuário continua pedindo no chat.

Ele abre no **modo simples**, feito para quem nunca usou computador direito: uma pergunta ("O que você quer fazer
agora?"), um bloco amarelo com a tarefa recomendada e três linhas com as outras: **Fazer um vídeo** (escolhe o estilo
vendo o exemplo, escreve o assunto e toca em **Mandar pra IA**, que manda o pedido pro chat do painel; sem o chat,
copia e diz onde colar), **Ver meus vídeos** (assistir, baixar o vídeo e a capa, copiar a legenda de cada rede e
pedir uma mudança, que vai pro chat), **Deu um problema** (abre **Está tudo certo?**: quantas coisas faltam, uma
linha por item e o botão **Pedir pra IA arrumar tudo**, que pergunta antes e junta tudo num pedido só; voz paga
faltando, com outra voz funcionando, é um passo em amarelo, não um problema) e
**Arrumar meu canal** (seis perguntas, uma por tela: assunto, nome, quem assiste, grátis ou pago, estilo e redes, com
resposta pronta e "Não sei, escolhe por mim"). No computador, o menu fica fixo do lado esquerdo, com o interruptor
**Simples / Completo** no pé: no simples, o menu mostra só Início, Fazer um vídeo, Meus vídeos, Está tudo certo?,
Conversar com a IA e Falar com o suporte; no completo, aparecem também Meu canal, Redes, Jeito dos vídeos, Estilos
(com **Criar meu estilo**: perguntas uma por tela, o kit sorteia e mostra a folha antes de usar), Personagens,
Ganchos, A voz dos vídeos, Métricas, Aprender e Ajuda (a escolha fica lembrada no navegador). No celular, a barra de
baixo tem Início, Fazer, Vídeos e Problema, e o resto fica em **Mais opções** (topo, à direita), com o mesmo
interruptor. Os ajustes salvam sozinhos ("Salvo agora"), sem botão Salvar.

Na primeira vez, com o canal sem nome, @, assunto ou público, o painel abre direto nas perguntas do canal (dá para
pular com "Fazer isso depois"; ele lembra onde parou). Essas respostas vão para `canal/preferencias.json` pelo
`prefs.salvar`, como qualquer ajuste do painel. A entrevista completa da instalação (`comandos/instalar.md`)
continua sendo sua: o `status:` do `canal/canal.md` só muda por ela.

Se o usuário perguntar onde fala com o suporte: **Mais opções › Sua conta e suporte** (Telegram, e-mail, prazo de
resposta, licença e até quando as atualizações são grátis). A voz fica em **A voz dos vídeos** (comparação grátis ×
paga, conectar a chave e a conta de quantos vídeos cabem no plano).

**Conversar com a IA** (Mais opções) é o chat com o Claude Code ou o Codex do próprio usuário (só aparece a IA
instalada), dentro do painel: cada coisa que a IA faz aparece numa linha, com botão Parar, pedidos prontos e
"Abrir numa janela separada", que abre a IA num terminal na pasta do estúdio. Se a aba fechar no meio, a conversa
volta mostrando que a IA ainda trabalha. Quando o chat está pronto, "Pedir pra IA
arrumar tudo" manda o pedido direto para lá; senão, copia para colar.

Toda tela tem o tour guiado **Me mostra como usa** (abre sozinho só no Início e no Fazer um vídeo; nas outras, o link
no topo da tela pisca de leve na primeira visita; também fica em Mais opções). Os passos ficam em `kit/painel/estatico/tours.js`: quem muda uma tela do painel
atualiza o tour dela no mesmo commit e sobe a `versao`.

Os guias do kit também ficam dentro dele, na área **Aprender** (começar, caminhos, chave da voz, estilos, ganchos,
engajamento, publicar, métricas, segurança e ajuda), com busca e "Comece por estes 3". Quando o usuário perguntar
"como faço X", além de responder, diga onde está o guia no painel. A chave grátis do Google e a da ElevenLabs têm um
passo a passo próprio do painel (`kit/painel/guias/chaves.md`).

Na tela **Estilos**, cada estilo mostra o vídeo-exemplo de 10 s quando existir
`exemplos/estilos/<id-do-estilo>/exemplo.mp4` (com `capa.jpg` ao lado, opcional), onde o id é o nome da ficha em
`metodo/estilos/`. Sem o arquivo, aparece "exemplo em breve".

## Abrir

O caminho normal do usuário é o **ícone Temporada Viral** (área de trabalho e menu Iniciar; no Mac, o app em
Aplicativos e na Mesa): dois cliques abrem o painel no navegador, sem janela de terminal. Se o painel já estiver
aberto, o ícone só mostra a mesma página de novo. O ícone nasce na instalação (`comandos/instalar.md`); se ele não
existir ou o usuário pedir "cria o ícone do painel", rode a partir da pasta do estúdio, com o mesmo Python do kit:
`python kit/painel/atalho.py --criar` (para tirar: `--remover`).

Quando você mesmo abre o painel:

1. A partir da **pasta do estúdio** (não de `kit/`), rode em segundo plano:
   `python kit/painel/servidor.py --sem-navegador`
2. Leia a linha `PAINEL_URL:` da saída e mande o link ao usuário em uma frase: "O painel está aberto: <link>. Só
   funciona neste computador." O link tem um código de acesso: não publique, não mande para ninguém. Se o painel já
   estava aberto, a saída traz o link dele e o comando termina na hora.
3. O painel se fecha sozinho uns 3 minutos depois que a última aba dele fecha (e nunca no meio de uma resposta da
   IA). Para deixar aberto direto, use `--sem-desligar`. Os erros dele ficam em `trabalho/painel.log`, sem código,
   chave nem e-mail.
4. Reserva, sem o ícone: dois cliques em **ABRIR-PAINEL** na pasta do estúdio (Windows: `ABRIR-PAINEL.bat`; Mac:
   `ABRIR-PAINEL.command`; se o Mac recusar, rode `chmod +x ABRIR-PAINEL.command` uma vez). Esse abre uma janela de
   texto que precisa ficar aberta.

Sem licença ativa, o painel mostra só a página de licença, no visual do painel: quem nunca ativou escreve o e-mail
da compra e toca em **Ativar**; licença cancelada mostra a mensagem do site e o contato do suporte. Não tente contornar (`CLAUDE.md`, "Licença").

## Conversar com a IA pelo painel

O painel conversa com o **Claude Code** e com o **Codex** (o CLI do ChatGPT) do próprio usuário. O Antigravity não
tem CLI e fica de fora. Dois jeitos:

- **Abrir a IA aqui**: abre o CLI de verdade numa janela de terminal, já na pasta do estúdio, com as aprovações do
  próprio CLI. Serve para tudo, inclusive entrar na conta pela primeira vez, instalar o que falta e publicar.
- **Chat do painel**: o mesmo CLI sem janela, preso à pasta do estúdio. Lá a IA lê e edita os arquivos do estúdio
  (menos o código do kit), roda `python` dos scripts do kit, `ffmpeg` e `ffprobe`, e cada ação aparece na tela
  ("Rodou: python kit/cartelas/rodar.py ..."). Não instala nada, não abre site, não publica, não apaga e não sai da
  pasta: o que ficar fora disso é recusado na hora, e a IA diz para usar o **Abrir a IA aqui**. No Codex, os
  comandos do chat rodam sem internet (a voz paga ou grátis precisa do **Abrir a IA aqui**).

Se você for a IA do chat do painel: um comando por vez, sem `&&`; o que o kit manda rodar "a partir de `kit/`" vai em
duas chamadas (`cd kit` e depois o comando). Ação recusada com "FORA DO PERMITIDO" não se contorna: explique ao
usuário e indique o **Abrir a IA aqui**.

Se o CLI não estiver instalado ou não tiver entrado na conta, o painel mostra o passo a passo ("Abra a IA aqui uma
vez e entre com sua conta"). O contrato da API dessa parte fica no topo de `kit/painel/ia.py`.

## Celular e nuvem

Na nuvem não há navegador no mesmo computador. Gere a versão só para ver:
`python kit/painel/servidor.py --estatico`
Ela grava `painel.html` na pasta do estúdio, com tudo dentro de um arquivo só, sem nenhuma ação. Mande o arquivo
ao usuário e diga que, para mudar algo, ele pede no chat.

## O que o painel grava (e você lê)

| Onde | O quê | O que você faz |
|---|---|---|
| `canal/preferencias.json` | ajustes do canal (redes, voz, legenda, render, ganchos, roteiro), pelo `prefs.salvar` | lê antes de **todo** episódio: `python -m prefs`, a partir de `kit/` |
| `canal/canal.md` | só a linha `caminho:` do topo, quando o usuário troca o caminho no painel | segue o caminho escrito ali |
| `canal/pedidos.md` | pedidos de mudança deixados em Meus vídeos ("o vídeo todo" ou o número de uma cena), com o episódio | lê antes do próximo episódio, faz o pedido e marca `[x]`; pedido que vira regra entra em `canal/aprendizados.md` |
| `canal/pronuncia.json` | trocas de pronúncia do canal (vale antes da base do kit) | a voz já aplica sozinha (`kit/voz/pronuncia.py`) |
| pasta canal/ (logo e mascote) | imagens enviadas no painel, apontadas em `canal.logo` e `canal.mascote` | usa no fim do vídeo e no perfil |
| `canal/metricas.json` | números anotados por episódio e rede | usa nas sugestões do próximo vídeo |
| arquivo de segredos fora do kit | chaves coladas em "A voz dos vídeos" (pelo `kit/chave.py`) | nunca leia o valor; só confira se a chave existe |
| `canal/` e `canais/` | troca de canal ou canal novo pelo botão "Trocar de canal" (pelo `kit/canais`, o mesmo do `python -m canais`) | leia o `canal/` em uso de novo; canal novo segue para `comandos/instalar.md` |

O painel relê os arquivos a cada poucos segundos: o que você muda (vídeo novo em `trabalho/entregas/`, preferência
gravada pelo `prefs.salvar`, folha de cenas) aparece sozinho na tela do usuário. Ajuste que o usuário pedir no
chat ("legenda maior", "só Instagram e Kwai") você grava pelo `prefs.salvar`, e o painel mostra igual.

## Se algo der errado

- "Abra o painel pelo ícone": o navegador abriu o endereço sem o código. O código vale 7 dias e fica guardado no
  navegador e em `trabalho/painel.codigo.json`; o ícone abre o painel já liberado.
- A página não abre: o processo parou (ou se fechou sozinho, sem uso). Dois cliques no ícone, ou rode de novo e
  mande o link novo (o painel tenta usar a mesma porta). O motivo, se foi erro, está em `trabalho/painel.log`.
- "Está tudo certo?" mostra o que falta: o pedido único ("Arruma o meu estúdio: 1) ...") e o de cada item chegam
  no chat; resolva pelo `kit/INSTALAR.md` e `python verificar.py`, a partir de `kit/`.
