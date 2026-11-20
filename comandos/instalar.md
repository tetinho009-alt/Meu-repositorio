<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Instalar: a entrevista da primeira vez

Rode quando `canal/canal.md` tiver `status: nao-configurado`, ou quando o usuário pedir para configurar de novo.

O objetivo é que, ao fim, o estúdio saiba o bastante para fazer vídeos com a cara do canal dele, do jeito que o
método da Temporada Viral ensina. Leva uns 15 minutos.

## Como conduzir

- **Uma pergunta por mensagem.** Sempre com **duas sugestões prontas**, montadas a partir do que ele já respondeu, e
  a saída "escolhe você". No Claude Code (e onde houver ferramenta de pergunta com botões), use os botões; no chat,
  escreva as opções como "a)" e "b)". Ele pode responder com o botão, com a letra ou com um texto do jeito dele.
- **Salve na hora.** Depois de cada resposta, grave em `canal/canal.md` ou `canal/identidade.md` e mostre um cartão
  de uma linha: `Salvo: <o que entendeu>. Falta: <o que vem depois>.` Assim ele vê o canal tomando forma, e nada se
  perde se a conversa cair.
- **Resposta curta? Pergunte o que falta.** Se ele disser só "carro", pergunte que parte, pra quem, em que tom.
  Ensine de passagem: quanto mais detalhe ele der, menos o vídeo sai genérico.
- Se ele não souber, **sugira** e siga. Ninguém trava na instalação.
- Linguagem simples, sem jargão. Termo técnico (terminal, npm, `.env`, chave de API) vem explicado em meia frase.
  Ele pode estar no celular.
- Se ele quiser pular, preencha com as sugestões e marque o que ficou como sugestão.

## Passo 0 · A licença e a máquina (enquanto ele responde)

No modo agente, a primeira pergunta é o e-mail da compra: ative com `python licenca.py <e-mail>` a partir de `kit/`
(seção "Licença" do `CLAUDE.md`). Sem licença ativa, a instalação não segue.

Antes da pergunta seguinte, diga em uma frase que vai conferir o computador enquanto conversam. No modo agente:

1. Rode `python verificar.py` a partir de `kit/` e traduza o resultado numa lista curta, com ✅ pronto, ⏳ instalando
   e ❌ falta, cada item com o tempo esperado ("motor de animação: uns 3 minutos").
2. Instale o que falta (`kit/INSTALAR.md`). Se o sistema pedir permissão, diga que pode aceitar e por quê.
3. Rode o exemplo em segundo plano (`python exemplo/rodar.py --voz kokoro`, ou `--stills` sem placa de vídeo) e,
   quando sair, mostre um quadro: "funcionou de primeira, este é o vídeo de exemplo". Ver funcionando cedo é o que
   segura quem nunca abriu um terminal.

## Onde responder: no painel ou aqui

Assim que a licença e a máquina estiverem prontas, crie o ícone do painel (seção "Depois da entrevista", passo 2) e
pergunte, com dois botões:

a) **No painel (recomendado)**: "Abra o ícone Temporada Viral na área de trabalho: as perguntas do canal aparecem
   lá, uma por tela, com exemplos dos estilos para ver." Rode `python kit/painel/atalho.py --criar`, peça para ele
   abrir o ícone e **não repita as perguntas aqui**: o painel grava nas mesmas preferências. Quando ele voltar, leia
   `python -m prefs` e `canal/canal.md` e siga só com o que o painel não cobre (voz, identidade, preferências de
   produção abaixo), sem perguntar de novo o que já está preenchido.
b) **Aqui na conversa**: siga a entrevista abaixo. O painel não abre as perguntas de novo quando o canal já está
   preenchido.

## A entrevista

0. **O caminho** (`metodo/caminhos.md`). Pergunte antes de tudo, com dois botões:
   a) **Grátis**: Antigravity ou Codex (conta grátis do ChatGPT) e a voz grátis do Google; só no computador, mais
      lento, com limite por dia
   b) **Recomendado**: Claude Code (plano Pro) e a voz da ElevenLabs; mais rápido, voz melhor, funciona no celular
   Se ele já está no Claude Code, sugira o recomendado; se está no Antigravity ou no Codex, o grátis. Grave
   `caminho: gratis` ou `caminho: recomendado` em `canal/canal.md`. Daí em diante, cada passo segue esse caminho
   sem pedir que ele entenda de programação.
1. **Nome e @.** Como o canal se chama e qual é o @? Sem nome, ofereça 5 com @ curto, sem acento, e lembre de
   conferir se o mesmo @ está livre no Instagram, no TikTok e no YouTube, e reservar os três no mesmo dia.
2. **Estilo.** Mostre o catálogo (`metodo/estilos/README.md`) em no máximo 6 linhas, filtrado pelo caminho dele
   (no grátis, sem os estilos que dependem de imagem gerada), e pergunte o que ele quer que a pessoa sinta no fim.
   Dois botões vindos do nicho, por exemplo:
   a) **Série com votação**: história em partes, a galera escolhe o que acontece (o formato do caso real)
   b) **Top 5 ou quiz**: rápido de fazer, bom para o primeiro vídeo (`comandos/modo-rapido.md`)
   Grave o estilo (ou os estilos) em `canal/canal.md` (`estilos:`).
3. **Do geral pro específico: nicho, série, primeiro vídeo.** Peça as três camadas numa resposta só: o assunto do
   canal e pra quem é (idade, o que a pessoa já sabe), uma série dentro dele, e um exemplo de vídeo. Exemplos:
   - série: "terror de bairro pra quem cresceu em cidade do interior; série 'O Poço do Quintal'; EP1: o poço que responde
     quando alguém chama";
   - explicativo: "veículos por dentro, pra curiosos de 14 a 45 anos; série 'o que ninguém te explicou na
     autoescola'; vídeo: por que o pneu tem esses desenhos?".
   Pergunte também o lugar e o cotidiano que o público reconhece (condomínio, sítio, laje, metrô, praia).
4. **Tom da narração.** Como o canal fala, e o que ele **não** quer. Exemplos: "sério, sussurrado, misterioso, sem
   susto barato" · "amigo contando uma curiosidade, com comparação do dia a dia, sem tom de professor nem gíria
   forçada". Peça a lista do que evitar: ela vale tanto quanto a do que fazer.
5. **Personagem e lugar padrão.** Descreva do jeito que quiser (idade, cabelo, roupa, um detalhe marcante) ou "cria
   pra mim", e o cenário onde os vídeos acontecem quando o roteiro não pede outro. Regras que você aplica sem
   perguntar: adulto ou adolescente, nada que pareça criança como chamariz, cabelo feminino longo ou coque.
6. **Estilo visual** (o Atlas de Estilos), uma linha cada:
   a) **Noite de Bairro**: escuro, coral e azul-céu, luz de poste (terror e suspense urbano)
   b) **VHS Achado**: granulado, cores lavadas, data no canto
   c) **Neon Urbano**: noite azul e rosa, reflexo de chuva
   d) **Aquário Toon** (explicativo): 3D fofo, contorno preto, cores chapadas, fundo azul-petróleo
   e) **Papel e Lápis**: claro, traço de caderno, cores de marca-texto
   Só para série: ofereça também o **estilo desenhado próprio**, sorteado só para o canal (papel, tinta, cor, jeito
   dos personagens, fontes e capa). Se ele quiser, rode `comandos/criar-estilo.md` agora e volte para a pergunta 7
   depois do "aprovado" na folha.
7. **A marca registrada.** Uma coisa que todo vídeo do canal tem e os outros não. Exemplos: "todo vídeo abre com um
   fato que parece mentira e termina com o personagem tentando e dando errado" · "toda parte termina com a mesma
   frase do vigia e o relógio de quantos dias faltam". Explique por quê: quando o formato encher de cópia, é isso que
   faz o público reconhecer o canal.
8. **Capa e cor.** Como é a capa (padrão de série: personagem grande, nome da série gigante e a pergunta do voto;
   padrão de explicativo: a pergunta curta em cima, o objeto aberto no meio, o personagem com cara de choque) e a
   cor do canal. Logo: se ele não tem, diga que o kit de identidade faz um (`kit/idv/`) e que dá pra fazer depois.
8a. **A identidade do canal** (logo, foto de perfil, banner do YouTube, capas de destaque e os modelos de capa e
   post). Mostre em uma frase o exemplo pronto (`exemplos/canal-pronto/`, a folha `conferencia.jpg`) e pergunte,
   com dois botões:
   a) **O kit faz de graça (recomendado)**: escreva `canal/idv/marca.json` a partir de `kit/idv/marca.exemplo.json`
      com as respostas dele (nome, @, cores da pergunta 8, séries, mascote ou a inicial do nome) e rode, a partir de
      `kit/`, `python idv/gerar_idv.py tudo --marca ../canal/idv/marca.json --saida ../canal/idv` (com `--cpu` se
      não houver placa de vídeo). Sem mascote, o símbolo é a inicial do canal; para ter um, desenhe-o por código no
      estilo do kit, como o do exemplo (`exemplos/canal-pronto/mascote/desenhar_mascote.py`). Mostre a
      `conferencia.jpg` e só siga com o "aprovado".
   b) **Prefiro o ChatGPT (precisa de assinatura)**: mostre os prompts de `modelos/prompts-chatgpt-identidade.md`
      já preenchidos com o canal ([NOME], [NICHO], [CORES], [MASCOTE]), um bloco por peça, e diga onde salvar as
      imagens. Quando ele trouxer as artes, recorte o fundo (`python idv/gerar_idv.py recortar ...`), ponha-as no
      `canal/idv/marca.json` e rode o mesmo gerador. Avise que o plano grátis do ChatGPT e do Codex não gera essas
      imagens.
   Se ele quiser deixar para depois, siga: a identidade pode ser feita a qualquer hora ("faz a identidade do meu
   canal").
8b. **As redes.** Em quais vai postar: Instagram, TikTok, YouTube Shorts, YouTube longo (o filme horizontal da
   série) e Kwai. Uma, várias ou todas: o pacote sai só para as marcadas, cada uma com o seu CTA, a sua legenda e os
   seus limites. Sugestão: Instagram, TikTok e YouTube Shorts.
9. **Assinatura do fim (CTA).** O que a pessoa deve fazer no último segundo: seguir pra ver a parte 2, votar, mandar
   pra um amigo. Uma frase só. Se ele vende ou divulga alguma coisa, a chamada vai uma vez, só na voz, no meio
   do vídeo (`roteiro.cta_meio` e `roteiro.cta_meio_frase` nas preferências, ex.: "aprenda a fazer vídeos assim pelo
   link na bio"; `metodo/engajamento.md`, seção 3). O fim é o card da rede, sem cauda de produto. Nunca "comenta X":
   pergunta aberta, sempre.
10. **A voz.** Primeiro como ele imagina (homem ou mulher, idade, energia). Depois a ferramenta:
    a) **ElevenLabs** (a melhor em pt-BR; o plano grátis serve pra testar, mas não libera uso comercial; o Starter
       custa uns US$ 6 por mês) — caminho recomendado
    b) **Voz grátis do Google** (Gemini TTS, pelo Google AI Studio): natural em português, aceita estilo
       ("sussurrado", "animado"), limite por dia, não pede cartão — caminho grátis. Ligue com `python chave.py --qual
       gemini` (janela no navegador: ele entra com a conta do Google, clica em "Get API key" e cola lá). Avise que,
       no plano grátis, o Google usa o texto enviado para melhorar os produtos dele.
    c) **Kokoro, no computador** (licença Apache-2.0, pode monetizar): sem internet e sem limite, um degrau abaixo
    Programas grátis de voz com janela (como o VoiceStudio) servem pra testar, mas o modelo padrão deles costuma ter
    licença não comercial: não recomende pra canal que vai monetizar sem conferir a licença de cada modelo.

    **Ligar a ElevenLabs, nesta ordem:**
    1. **Por permissão (sem chave), se a IA tiver o conector.** No Claude, o conector oficial da ElevenLabs fica em
       Configurações → Conectores: ele toca em Conectar, entra na conta da ElevenLabs e autoriza. Se as ferramentas
       do conector já aparecem pra você, ele já está ligado: não peça mais nada. Veja o fluxo em `metodo/voz.md`
       (seção "Voz pelo conector").
    2. **Pela janela da chave**, quando não há conector (Codex, ChatGPT, Gemini) ou quando o kit precisa gravar
       sozinho em segundo plano: rode `python chave.py` a partir de `kit/` (em segundo plano: ele espera até 30
       minutos). Diga que vai abrir uma janelinha no navegador com o passo a passo, que a chave é como uma senha e
       que ele cola lá, não na conversa. Quando sair `CHAVE_SALVA`, conte o saldo em minutos de narração e a data em
       que renova.

    **3 amostras com uma frase no tom do canal**, pra ele escolher ouvindo (custa uns 250 créditos; mostre antes):
    - pelo conector: busque vozes em português (`languages: ["pt"]`, e o sotaque brasileiro quando a busca oferecer)
      com o gênero, a idade e o jeito pedidos, e gere a frase em 3 vozes;
    - pela chave: `python -m voz.amostras --frase "<frase do canal>" --genero <g> --idade <i> --jeito "<3 palavras>"`;
      `--br` traz vozes brasileiras da biblioteca com prévia grátis; `--provedor gemini` ou `--provedor kokoro`
      gravam as grátis (sem custo).
    Avise que muitas vozes são gringas falando português: se o sotaque incomodar, mostre as brasileiras. Grave a
    escolhida (o voice_id) em `voz` no `kit/config.json` e em `canal/canal.md`.
    Se ele colar uma chave na conversa por engano: peça que apague essa chave no site, crie outra e use a janela.
11. **A máquina e o bolso.** Onde vai produzir (computador com placa NVIDIA, computador comum, só celular) e quanto
    quer gastar por mês (nada, até uns R$ 150, o que precisar). Com a placa, ajuste `render.fps` no
    `kit/config.json`: NVIDIA 60 fps; o resto 30 fps. Pelas duas respostas, escolha a pilha
    (`metodo/pilhas-e-ferramentas.md`) e diga qual e por quê, em uma frase. A dica que vale aqui: comece com o que
    tem e reinvista nas ferramentas quando o canal der o primeiro dinheiro.
12. **Como ele quer que você trabalhe.**
    a) **Etapa por etapa**: roteiro, folha de cenas e vídeo, cada um com a opinião dele (recomendado nos 3 ou 4
       primeiros vídeos, enquanto você aprende o gosto dele)
    b) **Direto ao vídeo**: você faz tudo e mostra o vídeo pronto; se algo não agradar, refaz
    Grave em `canal/canal.md` (`modo:`). Quantos vídeos por semana ele consegue aprovar com calma? (para começar: 2
    a 3)

## Depois da entrevista

1. Mude `status` para `configurado` em `canal/canal.md` e grave as respostas também nas preferências, pelo módulo
   `prefs` (a partir de `kit/`): nome, @, nicho, público, tom, caminho, estilo padrão, redes escolhidas e voz. É o
   mesmo arquivo que o painel mostra (`comandos/painel.md`).
2. **Crie o ícone do painel**, rodando a partir da pasta do estúdio, com o mesmo Python do kit:
   `python kit/painel/atalho.py --criar`. Ele põe o ícone **Temporada Viral** na área de trabalho e no menu
   Iniciar (no Mac, o app em Aplicativos e na Mesa), que abre o painel sem janela de terminal. Diga em uma frase:
   "Criei o ícone Temporada Viral na sua área de trabalho: dois cliques abrem o painel." Se der `ERRO:`, siga o
   `O QUE FAZER:` e conte que o ABRIR-PAINEL da pasta continua funcionando.
3. Escreva em `canal/pauta.md` **10 ideias iniciais** no nicho dele:
   - série: 10 premissas de uma linha, cada uma com a escolha do EP1;
   - explicativo: 10 perguntas de título.
   Marque as 3 mais fortes e diga por quê em meia linha.
4. Mostre o resumo em no máximo 12 linhas e diga como o estúdio aprende: tudo o que ele pedir ou opinar fica em
   `canal/historico.md` e `canal/aprendizados.md`, e vale para todos os vídeos seguintes. Se o primeiro vídeo não
   sair perfeito, o segundo já sai melhor.
5. Diga os atalhos: "sempre X" ou "nunca X" vira regra do canal; "não entendi" ou "deu erro" e você explica passo a
   passo (`comandos/ajuda.md`).
6. Termine com uma pergunta só, com as duas ideias mais fortes como botões:
   - estilo de cartela (top 5, quiz, tipografia...): "Faço o primeiro vídeo agora?" (`comandos/modo-rapido.md`)
   - série: "Qual vai ser a primeira série?" (`comandos/nova-serie.md`)
   - explicativo: "Qual vai ser o primeiro vídeo?" (`comandos/novo-video.md`)
   - se as contas ainda não existem: "Antes, quer montar os perfis nas redes?" (`metodo/plataformas.md`)
7. Conectar as redes é opcional e pode vir depois do primeiro vídeo (`comandos/conectar-redes.md`). Ofereça só se o
   usuário estiver no modo agente e quiser publicar pela API, apurar votos ou ler as views sozinho. Sem isso, ele
   posta pelo app e cola os comentários e os números.
