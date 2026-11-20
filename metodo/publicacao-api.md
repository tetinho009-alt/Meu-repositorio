<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# 09 · Publicação

Carregue com "publicar". Sempre peça confirmação do usuário antes de publicar: publicar é irreversível na prática
(apagar e republicar zera o alcance).

## 1. Matriz: o que é seguro em cada rede

| Ação | Instagram | TikTok | YouTube |
|---|---|---|---|
| Publicar | **API oficial** (Graph API, Reels) ou Meta Business Suite | **Agendador do TikTok Studio** ou envio para o rascunho pela API (o dono finaliza no app) | **API oficial** (`videos.insert`) ou YouTube Studio |
| Agendar | Meta Business Suite; pela API, publicar no horário | TikTok Studio, até 10 dias antes | `privacyStatus=private` + `publishAt` |
| Rótulo de IA | `is_ai_generated` | No app | `status.containsSyntheticMedia` |
| Responder comentário | API, com limites (`metodo/comunidade-e-votos.md`) | Manual | API, com limites |
| Curtir, seguir, DM por robô | **Proibido** | **Proibido** | **Proibido** |
| Bibliotecas não oficiais, robô de navegador, "auto-post" sem API | **Proibido** | **Proibido** | **Proibido** |

Por que o TikTok fica no agendador: app de uso próprio não passa na auditoria de publicação direta, e sem auditoria
todo post sai privado. O envio para rascunho é o caminho oficial que funciona.

## 2. Segredos

- Tokens e chaves ficam em variável de ambiente ou no arquivo de configuração local do kit, **fora do repositório**
  (nomes em `kit/README.md`).
- No modo nuvem, cadastre como segredos do ambiente da nuvem do Claude Code.
- Nunca cole token na conversa, em commit, em log ou em print. Se vazou, revogue e gere outro.

## 3. Instagram (Graph API)

Pré-requisitos (uma vez):
1. Conta profissional (criador).
2. App próprio no painel de desenvolvedores da Meta, com o produto Instagram e as permissões de publicar conteúdo e
   gerenciar comentários. Para a própria conta, o modo de desenvolvimento com você como testador costuma bastar;
   para contas de terceiros, revisão do app (confira no painel da Meta: a tela muda com frequência).
3. Token de longa duração. Ele expira (~60 dias) e pode ser renovado antes de vencer; agende a renovação.

Fluxo por vídeo:
1. **O vídeo precisa estar numa URL pública** (a API baixa o arquivo). Qualquer armazenamento com link público
   direto serve. Use **nome novo a cada versão** (`serie_p1_v2.mp4`): CDN guarda a versão velha por dias.
2. Criar o contêiner: `POST /<IG_USER_ID>/media` com `media_type=REELS`, `video_url`, `caption`, `share_to_feed=true`,
   `cover_url` (capa 9:16) e `is_ai_generated` conforme `metodo/seguranca.md`.
3. Consultar `GET /<CONTAINER_ID>?fields=status_code` a cada ~10 s até `FINISHED` (desista após ~10 min e investigue).
4. Publicar: `POST /<IG_USER_ID>/media_publish` com `creation_id`.
5. Pegar o link: `GET /<MEDIA_ID>?fields=permalink`.

Limites: 100 publicações por API a cada 24 h; Reels de 3 s a 15 min, até 300 MB, até 25 Mbps.
No kit: comando de publicação em `kit/README.md` (`python -m publicar.instagram`).

Sem API: Meta Business Suite no computador, Reels, legenda, capa, agendar.

## 4. YouTube (Data API)

Pré-requisitos (uma vez):
1. Projeto no Google Cloud com a YouTube Data API ativada e credencial OAuth.
2. **Publique o app OAuth em "Produção".** Em "Testing", o token de atualização expira em 7 dias e a publicação para
   de funcionar sem aviso.
3. Canal com público "não é para crianças".

Por vídeo, `videos.insert` com:
- `snippet.title` (até 100 caracteres), `snippet.description`, `snippet.categoryId` 1 (Filmes e animação) ou 24
  (Entretenimento);
- `status.privacyStatus=private` + `status.publishAt` (horário em UTC) para agendar;
- `status.selfDeclaredMadeForKids=false`;
- `status.containsSyntheticMedia` conforme `metodo/seguranca.md`.

Depois, no Studio: quadro de capa, vídeo relacionado (parte seguinte), comentário fixado.
Cota: bucket próprio de uploads por dia + 10.000 unidades para o resto; escrita em playlist e comentário ≈ 50
unidades. Folga de sobra para 3 vídeos por semana.
No kit: `python -m publicar.youtube enviar`.

## 5. TikTok

Caminho padrão: **TikTok Studio no computador**, agendamento até 10 dias antes. Post agendado não se edita: apaga e
reenvia.

Caminho por API (só modo agente): envio para a caixa de rascunhos (escopo `video.upload`); o dono abre o app,
confere capa e texto e publica. Se o app de uso próprio é aprovado para esse escopo: (confira no painel do TikTok: a tela muda com frequência).
No kit: `python -m publicar.tiktok`.

Sem publicação direta por API de app próprio: sai privado.

## 6. Ordem do dia de publicação

1. Master final aprovado, checklist zerado, `licencas.txt` ao lado.
2. **Confirmação do usuário**, com o resumo: vídeo, capa, texto por rede, horário, rótulo de IA.
3. Instagram na hora marcada.
4. YouTube agendado para a mesma hora (pode subir na véspera).
5. TikTok agendado no Studio para a mesma hora (e o Kwai, se estiver entre as redes).
6. Na primeira hora: responder comentários à mão nas três.
7. Uma hora depois: conferir a aba de direitos autorais do YouTube Studio e o "Status da conta" do Instagram.
8. Registrar os três links no arquivo do episódio.

## 7. Apagar e republicar

Só quando o defeito é grave (erro visual evidente, áudio mudo). Republicar com nome de arquivo novo. No Instagram, a
capa de um Reel já publicado se troca no app, sem republicar.
