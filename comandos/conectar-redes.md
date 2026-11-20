<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Conectar redes

Guia do passo "Conectar redes". É **opcional**: sem ele, o estúdio entrega as 3 pastas e o usuário posta pelo app.
Conectar serve para três coisas:

- **publicar pela API** (Instagram e YouTube; no TikTok, mandar para os rascunhos do app);
- **ler views e comentários** para apurar os votos e alimentar o placar do site (`kit/placar/LEIA-ME.md`);
- **ler os votos e sugerir as respostas** (só no Instagram), para colar à mão (seção "Robô de respostas");
  responder pela API não é recomendado.

## Como conduzir

- **Uma rede por vez**, na ordem que o usuário quiser. Sugestão: YouTube (10 min, sem aprovação) → Instagram
  (20 min) → TikTok (o mais demorado).
- Antes de cada parte, mostre a tabela "qual conta usar" daquela rede. Quase todo erro de conexão é conta errada.
- **Nenhuma chave passa pelo chat.** O usuário guarda cada chave sozinho (ver "Onde guardar as chaves") e só te
  avisa "salvei a X". Se ele colar uma chave na conversa, peça que revogue e gere outra.
- Menus mudam com frequência. Se algo não bater, peça print da tela **sem chave aparecendo** e adapte.
- Ao fim de cada rede, marque o checklist em `canal/canal.md` (seção Pendências).

## Onde guardar as chaves

| Onde o estúdio roda | Onde a chave fica |
|---|---|
| Claude Code no computador | Num arquivo `segredos.json` **fora desta pasta**, na pasta do usuário, apontado no `config.json` do kit (campo `segredos.arquivo`; o `config.json` é uma cópia de `kit/config.exemplo.json`), ou como variável de ambiente. O kit recusa arquivo de segredos dentro da própria pasta |
| Claude Code na nuvem (repositório no GitHub) | Como segredo do ambiente da nuvem, nas configurações do ambiente |

Formato do `segredos.json`: `{"IG_ACCESS_TOKEN": "...", "YT_API_KEY": "...", "TT_CLIENT_KEY": "..."}`. Ele nunca vai
para a nuvem, para o git ou para um print. O kit grava nele sozinho o que se renova (token do Instagram, acesso do
TikTok), por isso o placar e o robô precisam dele no computador.

Placar no GitHub (site): as chaves vão como segredo do repositório (**Settings → Secrets and variables → Actions**).
O comando `python placar/placar.py --gh-segredos <usuario>/<repositorio>` copia do `segredos.json` sem mostrar
nenhuma.

Antes de começar qualquer rede, ative a **verificação em duas etapas** na conta Google, na conta Meta e na conta
TikTok usadas.

---

## Parte 1 · YouTube

### Qual conta usar

| Onde | Conta |
|---|---|
| Google Cloud | A **conta Google dona do canal** do usuário |
| YouTube Studio | O canal do usuário |

### 1A · Ler views e comentários (chave de API, 10 minutos, sem aprovação)

1. Entre em https://console.cloud.google.com com a conta Google dona do canal.
2. No seletor de projeto (no topo), clique em **Novo projeto**, dê o nome do canal e selecione o projeto.
3. Abra **APIs e serviços → Biblioteca**, procure **YouTube Data API v3** e clique em **Ativar**.
4. Abra **APIs e serviços → Credenciais → Criar credenciais → Chave de API**. Copie a chave, **sem colar no chat**.
5. Clique em **Editar chave de API**:
   - **Restrições de API:** "Restringir chave", marcando só a YouTube Data API v3;
   - **Salvar**.
6. Guarde como `YT_API_KEY`: `python chave.py --qual youtube` abre a página que testa e guarda, sem a chave passar
   pelo chat.

A chave **só lê dados públicos**: views, curtidas e comentários dos vídeos públicos. Ela não posta e não mexe no
canal. A cota grátis é de 10 mil unidades por dia; ler o placar a cada 30 minutos usa poucas dezenas. Vídeo marcado
como "conteúdo para crianças" fica sem comentários na API (e sem voto): marque sempre "Não é conteúdo para crianças".

Teste: `python placar/placar.py --episodios placar/episodios.json --so <slug> --detalhe trabalho/teste.json` mostra os
votos lidos do YouTube.

### 1B · Publicar Shorts pela API (OAuth, opcional)

Só no modo agente. Comandos em `kit/README.md` e detalhes em `metodo/publicacao-api.md`.

1. No mesmo projeto, abra **APIs e serviços → Tela de consentimento OAuth**. Tipo **Externo**. Preencha o nome e o
   e-mail. Em **Usuários de teste**, adicione o e-mail dono do canal.
2. Crie a credencial **ID do cliente OAuth**, do tipo **App para computador**. Guarde o ID e o segredo como
   `YT_CLIENT_ID` e `YT_CLIENT_SECRET`.
3. Rode `python -m publicar.youtube autorizar` num computador com navegador. Faça login com a conta dona do canal e
   autorize. O kit gera o `YT_REFRESH_TOKEN`; guarde junto com os outros.
4. **Publique o app em produção:** **Tela de consentimento → Publicar app**. Em modo de teste, o token expira em 7
   dias e o vídeo pode subir como privado.

Checklist YouTube:
- [ ] `YT_API_KEY` salva (ler)
- [ ] `YT_CLIENT_ID`, `YT_CLIENT_SECRET` e `YT_REFRESH_TOKEN` salvos, com o app em produção (publicar, opcional)

---

## Parte 2 · Instagram (publicar, ler e responder comentários)

Usa a **API do Instagram com login do Instagram** (graph.instagram.com). Não precisa de página do Facebook.

### Qual conta usar

| Onde | Conta |
|---|---|
| App do Instagram (celular) | O **@ do canal**, convertido em **conta profissional** (Criador ou Empresa) |
| Meta for Developers | A conta Meta (Facebook) do **dono do canal**, que vira desenvolvedor. O app fica nela |
| Autorização do token | O **@ do canal**, logado no Instagram |

### Passo a passo

1. **No celular, no @ do canal:** abra **Configurações → Tipo de conta e ferramentas → Mudar para conta
   profissional**. Escolha **Criador** e a categoria "Criador de vídeos digitais" ou "Entretenimento".
2. Entre em https://developers.facebook.com com a conta Meta do dono e aceite virar desenvolvedor. Ative a
   verificação em duas etapas, se pedir.
3. **Meus apps → Criar app.** Caso de uso: **Gerenciar mensagens e conteúdo no Instagram** (o nome do menu pode
   mudar; o que importa é o produto **Instagram**). Dê o nome do canal ao app.
4. No painel do app, abra **Instagram → Configuração da API com login do Instagram**:
   - adicione o @ do canal como **testador do Instagram** (em **Funções do app**) e aceite o convite no Instagram:
     **Configurações → Apps e sites → Convites de testador**;
   - em **Gerar tokens de acesso**, clique em **Adicionar conta** e entre com o @ do canal;
   - autorize as permissões abaixo.

     | Permissão | Para quê |
     |---|---|
     | `instagram_business_basic` | Ler o perfil e os vídeos |
     | `instagram_business_content_publish` | Publicar Reels |
     | `instagram_business_manage_comments` | Ler e responder os comentários dos votos |
5. Copie o **token** gerado e guarde como `IG_ACCESS_TOKEN` com `python chave.py --qual instagram` (testa e mostra o
   @ conectado). É um token longo, que vale 60 dias.
6. **Renovar antes de vencer:** o token longo vale 60 dias e é renovado por
   `refresh_access_token?grant_type=ig_refresh_token`, desde que ainda esteja válido e tenha pelo menos 24 h. No modo
   agente, o kit renova sozinho depois de 45 dias e grava o novo no `segredos.json` (`python -m publicar.ig_token
   --status` mostra a idade; `--renovar` força). Com a chave só em variável de ambiente, ele avisa e você gera outro
   no passo 4. Se passar de 60 dias, gere outro no passo 4.

O app fica em **modo de desenvolvimento**. Para usar na **própria** conta, como testador, não precisa de revisão da
Meta. Revisão só é necessária para publicar em contas de terceiros.

### O que a API faz com o token

| Ação | Como |
|---|---|
| Publicar Reel | Cria o container (`media_type=REELS`, legenda e capa) → envia o vídeo do computador (envio "resumable", não precisa hospedar) → espera o status `FINISHED` → `media_publish` → devolve o link. No kit: `python -m publicar.instagram --video ... --legenda ...` (`--seco` mostra sem enviar) |
| Ler comentários | `/{id-do-video}/comments?fields=id,text,timestamp,username` |
| Sugerir respostas aos votos | `python -m publicar.responder_votos` (só sugere; enviar exige `--sei-o-risco`, não recomendado) |
| Rótulo de IA | Pedido na publicação. Se a API recusar, marque no app |

Limites que importam:
- **Capa:** não muda pela API depois de publicado. Escolha antes (`--capa-url` ou `--capa-ms`).
- **Volume:** existe limite diário de posts pela API. Com 3 vídeos por dia, sobra folga.
- **Nada de robô** para curtir, seguir ou mandar DM. É isso que derruba conta, e o kit não faz.

Checklist Instagram:
- [ ] @ do canal em conta profissional
- [ ] App criado na Meta, com o @ como testador e o convite aceito
- [ ] `IG_ACCESS_TOKEN` salvo, com as 3 permissões
- [ ] Teste a seco: `python -m publicar.instagram --video exemplo.mp4 --legenda legenda.txt --seco`

---

## Parte 3 · TikTok

O TikTok separa as coisas em produtos diferentes. **Comece pela 3C hoje**, porque é a que depende de aprovação.

| Quero | Produto | Aprovação |
|---|---|---|
| Views, curtidas e **número** de comentários | Display API (Login Kit) | Funciona já, em sandbox |
| **Texto** dos comentários (para apurar votos) | TikTok API for Business | Precisa de app aprovado |
| Mandar o vídeo para os rascunhos do app | Content Posting API | Sem auditoria, só rascunho ou privado: o dono publica pelo app |

**Precisa de site:** as APIs do TikTok pedem um endereço https **do próprio usuário**, para o retorno do login e
para verificar o domínio. O kit traz esse site pronto: a página do placar (`kit/placar/site/index.html`) e a página
de retorno (`kit/placar/site/tiktok_retorno.html`), publicadas de graça no GitHub Pages (`kit/placar/LEIA-ME.md`).
Use um repositório com o nome `<seu-usuario>.github.io`: o arquivo de verificação do TikTok precisa ficar na raiz.

**Os votos do TikTok são contados no computador:** a Display API dá views e curtidas, mas não o texto dos
comentários. O usuário copia os comentários do TikTok Studio para um `.txt` e o kit conta com a mesma regra
(`comandos/apurar-votos.md`). A API for Business (3C) entrega o texto, mas depende de aprovação da TikTok sem prazo;
até lá, o `.txt` resolve.

### Qual conta usar

| Onde | Conta |
|---|---|
| TikTok for Developers | A **conta de desenvolvedor**, com o e-mail do projeto. O app fica nela |
| App do TikTok (celular) | O **@ do canal**: vira conta comercial e autoriza o acesso |
| TikTok API for Business | Uma conta **TikTok For Business** com o **mesmo e-mail do projeto** |

### 3A · Views e curtidas (Display API)

1. Entre em https://developers.tiktok.com, abra **Manage apps → Connect an app** e crie um app novo com o nome do
   canal. No tipo do app, marque **Other** ("Login with TikTok, Share Kit, Content Posting API, or others"). **Não
   marque Mini game nem Mini drama:** esses tipos não têm Login Kit nem Display API, e o tipo não muda depois (seria
   preciso criar outro app).
2. Preencha:
   - **ícone:** a foto de perfil do canal;
   - **categoria:** Entertainment;
   - **descrição:** "Mostra no meu site as visualizações e curtidas dos meus próprios vídeos.";
   - **links:** termos e privacidade do site do usuário;
   - **plataforma:** Web, com o endereço do site.
3. **Verifique o domínio** pelo arquivo que o TikTok gerar: ponha o arquivo em `kit/placar/site/`, rode o
   `preparar.py` de novo e publique; depois clique em **Verify**.
4. **App review:** não envie para revisão. Ela só serve para o app ir para produção; para ler a própria conta, o
   sandbox basta e não precisa de aprovação. Deixe a seção em branco e clique em **Save** para salvar o resto.
5. Em **Add products**, adicione **Login Kit**. Em **Redirect URI**, coloque a página de retorno do site:
   `https://<seu-usuario>.github.io/tiktok_retorno.html`. Ela só mostra o código para copiar e não envia nada.
6. Em **Scopes**, marque `user.info.basic` e `video.list`.
7. Ative o **Sandbox**. Em **Target users**, adicione o @ do canal e aceite o convite pelo app do TikTok.
8. Copie o **Client key** e o **Client secret** e guarde como `TT_CLIENT_KEY` e `TT_CLIENT_SECRET`.
9. Autorize **uma vez**, logado no @ do canal (precisa do `segredos.json` configurado, porque o kit grava o acesso
   nele e nada aparece na tela):

   ```
   python placar/placar.py --episodios placar/episodios.json --tiktok-link     (abra o link e clique em Autorizar)
   python placar/placar.py --episodios placar/episodios.json --tiktok-codigo <código que o site mostrou>
   ```

   A partir daí o acesso se renova sozinho por 365 dias (`TT_REFRESH_TOKEN`).

### 3B · Rascunho no app (Content Posting API, opcional)

Mesmo app, produto **Content Posting API**, escopo `video.upload`. Guarde o token como `TIKTOK_ACCESS_TOKEN`. O
`python -m publicar.tiktok` manda o vídeo para a caixa de rascunhos e o dono publica pelo app. Detalhes em
`metodo/publicacao-api.md`.

### 3C · Texto dos comentários (API for Business)

1. **No celular, no @ do canal:** abra **Perfil → ☰ → Configurações e privacidade → Conta → Mudar para Conta
   Comercial**, com a categoria Entretenimento. É grátis. Ela perde parte das músicas comerciais, o que não importa,
   porque o estúdio usa só áudio próprio.
2. Entre em https://business-api.tiktok.com, clique em **Become a Developer** e crie ou entre numa conta **TikTok
   For Business** com o e-mail do projeto.
3. Cadastre o desenvolvedor com o site e esta descrição: "Criador de conteúdo. Leio os comentários dos meus próprios
   vídeos para apurar a votação da minha série."
4. Abra **My Apps → Create new**:
   - **nome:** "<canal> Votos";
   - **descrição:** "Leitura dos comentários dos vídeos da minha própria conta para contar os votos da série. Não
     publico, não respondo em massa e não coleto dados de terceiros.";
   - **redirect:** uma página de retorno do site;
   - **permissões:** **só** as de TikTok Accounts, leitura de vídeos e de comentários. Sem anúncios e sem
     publicação: quanto menos permissão, mais rápida a aprovação.
5. Envie para revisão. A TikTok não informa prazo.
6. Depois de aprovado, guarde o **App ID** e o **Secret** como `TTB_APP_ID` e `TTB_SECRET` e autorize o @ uma vez.

Checklist TikTok:
- [ ] @ do canal em conta comercial
- [ ] App de desenvolvedor (tipo Other) com Login Kit, escopos e sandbox; `TT_CLIENT_KEY` e `TT_CLIENT_SECRET`
      salvos e autorização feita (`TT_REFRESH_TOKEN`) (views)
- [ ] App Business pedido → aprovado; `TTB_APP_ID` e `TTB_SECRET` salvos (comentários)
- [ ] Até a aprovação sair: votos do TikTok pelo `.txt` copiado do TikTok Studio

---

## Robô de respostas (Instagram)

Responder comentário pela API **não é recomendado**: a Meta trata resposta automática como robô e pode rebaixar ou
travar a conta. O recomendado é responder à mão, no app. O `kit/publicar/responder_votos.py` ajuda nisso: lê os
comentários que são voto e mostra a resposta sugerida para cada um, para você colar à mão. Sem `--sei-o-risco`, nada
é enviado.

Só com `--sei-o-risco` ele responde de verdade, com estas travas, todas no código:

| Trava | Valor (config.json, `respostas`) |
|---|---|
| Só responde comentário que é voto, com texto variado (nunca o mesmo duas vezes seguidas) | `respostas.json` do episódio |
| Respostas por rodada / por dia (somando tudo) | 3 / 30 |
| Só uma fração dos votos (sorteio fixo) e uma vez por pessoa por vídeo | 50% |
| Pausa entre respostas | 4 a 11 s |
| Horário de gente: não responde de madrugada | 9h à 1h |
| Só comentários dos últimos dias | 7 dias |
| Para no primeiro erro da API (429, limite) e só tenta na rodada seguinte | sempre |

Nada de curtir, seguir ou mandar DM: não existe na API oficial para isso e é o que derruba conta. Comentário que não é
voto (pergunta, teoria) só recebe resposta escrita e aprovada pelo dono:
`python -m publicar.responder_votos --manual respostas_manuais.json` (modelo em `kit/exemplo/respostas_manuais.json`)
confere cada comentário e mostra o que colar; com `--sei-o-risco`, envia uma por vez, com 60 a 150 s entre elas.

Teste a seco, sem token e sem rede:
`python -m publicar.responder_votos --respostas exemplo/respostas.json --seco --comentarios-exemplo exemplo/comentarios_exemplo.json`

### Agendar

Não agende o robô de respostas: a sugestão serve na hora em que você vai responder, e o envio automático não é
recomendado. O que pode rodar a cada 30 minutos é o placar no computador, se ele não estiver no GitHub:

- Windows (Agendador de Tarefas), num terminal comum:
  `schtasks /Create /SC MINUTE /MO 30 /TN "Placar" /TR "cmd /c cd /d C:\caminho\do\kit && python placar\placar.py --episodios placar\episodios.json --saida placar\site\placar.json"`
- macOS ou Linux (`crontab -e`):
  `*/30 * * * * cd /caminho/do/kit && python3 placar/placar.py --episodios placar/episodios.json --saida placar/site/placar.json`

`python -m publicar.responder_votos --status` mostra quantas respostas saíram hoje (só conta as enviadas com
`--sei-o-risco`).

---

### Dúvida de suporte nos comentários

Quando alguém pergunta algo que não é voto (link, compra, "como faz"), responda **no fio do comentário da pessoa,
marcando o @ dela**, uma vez por pessoa e por assunto. Nunca um comentário solto no vídeo, nunca resposta
automática igual para todo mundo. Guarde quem já recebeu, para mandar a segunda resposta quando o assunto
resolver ("Liberado!", "Já está no ar").

## O que o usuário te manda

Só avisos, nunca chaves:
- "salvei a YT_API_KEY" · "salvei as chaves do YouTube e publiquei o app"
- "salvei o IG_ACCESS_TOKEN"
- "salvei TT_CLIENT_KEY e TT_CLIENT_SECRET" e "aceitei o convite do sandbox" (depois, a autorização com `--tiktok-link`)
- "pedi o Business" e, depois, "Business aprovado, salvei TTB_APP_ID e TTB_SECRET"

Depois de cada aviso, teste a conexão a seco (sem publicar nada) e mostre o resultado: o nome do canal e o número
de vídeos que a API enxerga.
