<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Placar ao vivo (site de votação)

Uma página que mostra o placar de cada episódio com os votos lidos dos comentários do Instagram e do YouTube (e do
TikTok, ver abaixo), contagem regressiva da votação e as visualizações somadas das 3 redes. Tudo pelas APIs oficiais.
É opcional: sem site, a apuração funciona do mesmo jeito no computador (`comandos/apurar-votos.md`).

## Como funciona

```
placar.py (a cada 30 min, no GitHub)  ->  lê as APIs oficiais  ->  site/placar.json  ->  site/index.html mostra
```

- **Instagram:** comentários de cada reel (votos), curtidas e, com a permissão de insights, views e salvamentos.
- **YouTube:** comentários de cada Short (votos), views e curtidas, com a chave de leitura (`YT_API_KEY`).
- **TikTok:** views, curtidas e compartilhamentos pela Display API. **A API não entrega o texto dos comentários**
  (só o número), então o voto do TikTok é contado no computador: copie os comentários do TikTok Studio para um
  `.txt` (um por linha; "@usuario: texto" conta um voto por perfil), rode a apuração e ponha só o resultado no
  episódio, em `"tiktok_votos": {"1": 12, "2": 30}`. O texto com o @ das pessoas não vai para o site.
- A regra do voto é uma só, a de `maquina/votos.py`: número ou palavra, um voto por perfil em cada rede, só dentro da
  janela (48 h), placar oficial a partir de 10 votos. Se uma rede falhar, o site mantém a última leitura boa dela e
  avisa; nunca inventa número.
- A página não mostra @ nem comentário de ninguém. Só números.

## 1. Os seus episódios

Copie `placar/exemplo/episodios.json` para `placar/episodios.json` e troque pelos seus. Para cada episódio: `slug`,
`serie`, `parte`, `titulo`, `pergunta`, `publicado` (data e hora da postagem, com fuso, ex.: `2026-11-01T22:00:00-03:00`),
`opcoes` (id, rótulo, cor e as palavras que valem, as mesmas do `respostas.json` do robô), `nega` (opcional: "não
entra" vale como a outra opção) e `links` (o link de cada rede, colado depois de postar). Em `canal.site`, o
endereço do site (passo 2).

Teste sem chave e sem internet:

```
python placar/placar.py --episodios placar/exemplo/episodios.json --exemplo placar/exemplo/api_exemplo.json --saida placar/site/placar.json
python -m http.server 8931 --directory placar/site        # abra http://127.0.0.1:8931
```

## 2. Hospedar de graça no GitHub Pages (recomendado)

Não precisa de servidor nem de PHP: o GitHub roda o `placar.py` a cada 30 min e publica a página.

1. Crie uma conta no GitHub e um repositório **público** chamado `<seu-usuario>.github.io` (o endereço vira
   `https://<seu-usuario>.github.io`). O repositório fica fora da pasta do kit e não leva chave nenhuma.
2. Monte a pasta do repositório: `python placar/preparar.py <pasta-do-repositorio>` e envie para o GitHub (GitHub
   Desktop ou `git push`). Rode o `preparar.py` de novo sempre que mudar o `episodios.json`.
3. No repositório: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
4. Cadastre as chaves em **Settings → Secrets and variables → Actions** (nomes: `IG_ACCESS_TOKEN`, `YT_API_KEY`,
   `TT_CLIENT_KEY`, `TT_CLIENT_SECRET`, `TT_REFRESH_TOKEN`). Pelo terminal, sem mostrar nenhuma:
   `python placar/placar.py --gh-segredos <seu-usuario>/<seu-usuario>.github.io` (precisa do `gh` logado).
5. **Actions → placar → Run workflow** para a primeira publicação. Depois ele roda sozinho a cada 30 minutos.

Domínio próprio (opcional): em **Settings → Pages → Custom domain**, siga a instrução do GitHub para o DNS.

## 3. Outro jeito: qualquer hospedagem de site estático

Rode no seu computador (agendado, ver `comandos/conectar-redes.md`, "Agendar") e envie a pasta `placar/site/` para a
hospedagem (Hostinger, Netlify, Cloudflare Pages):

```
python placar/placar.py --episodios placar/episodios.json --saida placar/site/placar.json
```

## Renovação das chaves

- **Instagram:** o token vale 60 dias. Dentro do kit, o `placar.py` renova sozinho depois de 45 dias e grava no
  arquivo de segredos. No GitHub não há onde gravar: renove no computador (`python -m publicar.ig_token --renovar`)
  e rode `--gh-segredos` de novo, uma vez a cada mês e meio.
- **TikTok:** autorize uma vez (`--tiktok-link`, depois `--tiktok-codigo`). O acesso se renova sozinho por 365 dias;
  se o TikTok trocar o refresh token, o `placar.py` avisa no log do Actions e você repete a autorização.
- **YouTube:** a chave de leitura não vence. Cota grátis: 10 mil unidades por dia; a cada 30 min o placar gasta
  poucas dezenas.

## Limites que importam

- Não rode mais vezes que a cada 30 min: o placar não fica mais certo e você gasta limite de API.
- A Display API do TikTok só funciona para contas que autorizaram o app (a sua). No sandbox, só usuários de teste.
- Nada aqui posta, curte, segue ou responde. Responder é à mão; o `publicar/responder_votos.py` só sugere as respostas (envio pela API não recomendado).
