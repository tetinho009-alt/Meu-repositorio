<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Contar os votos no Instagram, no TikTok e no YouTube

Tutorial para quem faz série com voto nos comentários. Há três jeitos de contar, todos dentro das regras das redes:

| Jeito | Redes | Trabalho | Quando usar |
|---|---|---|---|
| **A. Pela API oficial** (automático) | Instagram e YouTube | 10 a 30 min uma vez, depois nada | Série que vai durar; mais de uns 100 comentários por vídeo |
| **B. Copiar e colar** (a IA conta) | Todas, inclusive o TikTok | 2 a 5 min por vídeo | TikTok sempre; começo de canal; quem não quer criar chave |
| **C. Enquete nos stories** | Só Instagram | 1 min | Termômetro rápido com quem já segue |

A regra de contagem é a mesma nos três (detalhe em `metodo/comunidade-e-votos.md`): um voto por perfil, vale o número
ou a palavra da opção, só dentro de 48 h depois de postar, e placar com número só a partir de 10 votos. **Nunca invente
número**: o público confere.

## Como pedir o voto sem ser punido

- Diga a regra e só: "Vale um voto por pessoa. A palavra que mais gente escolher vira o próximo episódio."
- **Nunca** peça: "marca alguém", "compartilha", "manda pro amigo", "comenta várias vezes", "só sai se tiver X
  comentários". Isso é isca de engajamento: o vídeo some da recomendação para quem não segue, que é de onde vem o
  alcance.
- Desempate é decisão sua, não de quem comentou mais vezes.

---

## A. Pela API oficial (Instagram e YouTube)

O estúdio lê os comentários com a chave da **sua** conta e conta sozinho. Nada é postado, curtido ou respondido.

### A1. YouTube (10 minutos, grátis, sem cartão)

1. A partir da pasta `kit/`, rode `python chave.py --qual youtube`. Abre uma página neste computador com os passos e
   o campo para colar a chave.
2. Siga os três passos da página: criar um projeto no Google Cloud com a conta dona do canal, ativar a **YouTube Data
   API v3** e criar uma **Chave de API** restrita a ela.
3. Cole a chave e clique em salvar. A página testa na hora e guarda a chave fora da pasta do kit.

A chave só lê o que já é público e não vence. A cota grátis é de 10 mil unidades por dia, e cada página de até 100
comentários gasta 1: sobra muito. Vídeo marcado como "conteúdo para crianças" fica sem comentários na API; marque
sempre "Não é conteúdo para crianças" (e não faça série com voto para criança).

### A2. Instagram (30 minutos uma vez, renova sozinho)

Precisa de **conta profissional** (Criador ou Empresa). Não precisa de página no Facebook nem de revisão da Meta,
porque o app só lê a sua própria conta.

1. Rode `python chave.py --qual instagram`. A página mostra os passos:
   - no app do Instagram: **Configurações → Tipo de conta e ferramentas → Mudar para conta profissional → Criador**;
   - em developers.facebook.com: **Criar app**, com o caso de uso do Instagram;
   - no app: **Instagram → Configuração da API com login do Instagram**, adicione o @ como testador e aceite o
     convite no Instagram (**Configurações → Apps e sites → Convites de testador**);
   - em **Gerar tokens de acesso**: **Adicionar conta**, entre com o @ e autorize. As permissões que importam são
     `instagram_business_basic` e `instagram_business_manage_comments` (sem esta, a API não mostra quem comentou e
     não dá para contar um voto por pessoa).
2. Cole o token e salve. A página testa e mostra o @ conectado.

O token vale 60 dias. O estúdio renova sozinho depois de 45 dias (`python -m publicar.ig_token --status` mostra a
idade). Se passar dos 60 dias, gere outro no mesmo lugar.

Passo a passo completo, com publicar pela API e o TikTok: `comandos/conectar-redes.md`.

### A3. Contar

Com as chaves salvas, peça à IA "apura os votos do episódio X". Ela roda o `kit/placar/placar.py`, que lê o Instagram
e o YouTube, junta o `.txt` do TikTok (jeito B) e mostra o placar por rede e o total (`comandos/apurar-votos.md`).

---

## B. Copiar e colar (qualquer rede, e o único jeito no TikTok)

**Por que o TikTok é diferente:** a API que o TikTok libera para criador mostra views e curtidas, mas não o texto dos
comentários. A API de comentários é só para pesquisador acadêmico aprovado, e a API for Business depende de
aprovação sem prazo. Serviços que prometem "puxar os comentários do TikTok" raspam o site e violam os termos: não
use.

### No TikTok

1. No computador, abra o **TikTok Studio** no navegador, já logado no seu @, e vá em **Comentários**.
2. Escolha o vídeo do episódio e role até o fim da lista, para carregar todos.
3. Selecione a lista com o mouse, copie e cole num arquivo de texto (`kit/trabalho/tiktok_<episodio>.txt`). Pode
   colar do jeito que vier: a IA arruma no formato "@usuario: texto", um por linha.
4. Diga à IA "colei os comentários do TikTok do episódio X". Ela conta com a mesma regra e soma às outras redes.

O nome de quem comentou é o que garante um voto por pessoa. Ele fica só no seu computador e é apagado depois da
apuração.

### No Instagram ou no YouTube, sem chave

- Abra os comentários do vídeo, copie e cole no chat, ou mande prints da lista inteira.
- A IA conta e mostra o placar, com os comentários que ficaram de fora e o motivo (duas opções no mesmo comentário,
  voto repetido, fora do prazo).
- Acima de uns 200 comentários, os prints viram trabalho demais: vale criar a chave (jeito A).

---

## C. Enquete nos stories (Instagram)

A figurinha **Enquete** dos stories conta sozinha, com número oficial do Instagram.

- Bom para: termômetro rápido, desempate, ou uma votação extra entre episódios.
- Limite: só vota quem viu o story, ou seja, quem já segue. Não ajuda o Reel a alcançar gente nova; o voto nos
  comentários do Reel ajuda.
- **Não some** a enquete com os comentários do mesmo episódio: a mesma pessoa pode votar nos dois. Use um ou outro, e
  diga antes qual vale.

---

## O que nunca fazer

| Nunca | Por quê |
|---|---|
| Extensão, robô ou programa que entra na sua conta e rola os comentários sozinho | É automação não oficial. As redes tratam como robô e travam ou derrubam a conta |
| Site ou serviço que "raspa" comentários (de qualquer rede) | Viola os termos das redes, e você entrega dados de quem comentou a terceiros |
| Dar a sua senha a qualquer ferramenta | A API oficial nunca pede senha; quem pede senha é golpe ou robô |
| Responder, curtir ou apagar comentário por robô | Mesmo pela API, resposta automática é tratada como robô. Responda à mão |
| Publicar a lista de quem votou | Nome e @ são dados pessoais. Mostre só os números, e comentário só o texto, sem @ |
| Placar inventado, arredondado ou com menos de 10 votos | Quem votou confere. Placar falso acaba com a série |
