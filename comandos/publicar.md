<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Publicar: o pacote das redes escolhidas

Todo vídeo termina aqui, nos dois formatos. O estúdio entrega **uma pasta por rede escolhida** (`redes.escolhidas`
nas preferências: Instagram, TikTok, YouTube Shorts, Kwai), com tudo o que aquela rede precisa: o vídeo com o CTA
dela, a capa dela e a legenda dela. O usuário só posta.

## A estrutura

```
<nome>/
  01_IG/
    01_<nome>_ig.mp4                 vídeo com o CTA do Instagram
    01_<nome>_capa.jpg               capa com o CTA do Instagram (1080x1920, título dentro do recorte 3:4 do grid)
    01_<nome>_legenda.md / .txt      legenda pronta para colar (o .txt é o que a API usa) + o que ligar ao publicar
  02_TIKTOK/
    02_<nome>_tiktok.mp4             vídeo com o CTA do TikTok
    02_<nome>_capa.jpg               capa com o CTA do TikTok
    02_<nome>_legenda.md / .txt      legenda + texto do comentário fixado
  03_YOUTUBE/
    03_<nome>_youtube.mp4            vídeo com o CTA do YouTube
    03_<nome>_capa.jpg               capa com o CTA do YouTube
    03_<nome>_titulo_descricao.md / .txt
```

Só as redes escolhidas ganham pasta. Com o Kwai, entra `04_KWAI/` (vídeo, capa e legenda do Kwai; sem capa ou
legenda própria, ele usa as do TikTok). O YouTube longo (16:9) não sai aqui: é o filme da série, feito quando há 3
partes ou mais (`metodo/video-longo.md`).

Os números (01, 02, 03) seguem a ordem de postagem. Quando houver mais de um vídeo na semana, use `--numero` para o
número do vídeo entrar na frente do nome e a pasta ficar na ordem certa.

## O CTA de cada rede (vídeo e capa)

| Rede | Na tela, no fim do vídeo e na capa | Por quê |
|---|---|---|
| Instagram | "SEGUE PRA VER A PARTE 2" | Seguir é o que o Instagram mais recompensa |
| TikTok | "SEGUE PRA NÃO PERDER A PARTE 2" | Pedir repost ou curtida conta como isca e rebaixa o vídeo |
| YouTube | "SE INSCREVE PRA VER A PARTE 2" | A palavra do YouTube é "inscrever", não "seguir" |
| Kwai | "SEGUE PRA VER A PARTE 2" | Mesmo vertical do TikTok; o público é parecido |

No explicativo, troque "PARTE 2" pelo gancho do próximo vídeo ("SEGUE PRA VER COMO O ESGOTO FUNCIONA"), em todas as
redes. O CTA só promete a parte 2 se ela sair em até 24 h.

**Só esse pedido por vídeo.** O voto é uma pergunta aberta na história, nunca "comenta X ou Y"; o CTA final é um só,
seguir ou inscrever, e entra depois do voto, nunca junto.

## Produto: só na voz, no meio (sem cauda)

Nenhum vídeo leva cauda de produto: o fim é o card de chamada da rede. Se o usuário vende alguma coisa (curso,
serviço, loja), a chamada entra **uma vez, só na voz, no meio do vídeo** (`roteiro.cta_meio` nas preferências;
`metodo/engajamento.md`, seção 3).

O kit ainda tem a opção `python cta_redes.py <video> --parte N --cauda "TEXTO"`, um cartão de produto depois do card
da rede. **Não recomendado: a Meta rebaixa.** Vem desligada e só entra se alguém pedir com `--cauda`.

## Capa forte (opcional)

As capas do pacote saem automáticas do `kit/capa.py --redes`. Para o vídeo que você quer empurrar (o primeiro da
série, o que está viralizando, o vídeo de vendas), ofereça uma capa forte com IA de imagem: preencha o prompt de
`modelos/prompt-thumb.md` com os dados do canal e do episódio e entregue pronto para o usuário colar no ChatGPT ou no
Gemini, junto com a imagem do personagem.

## A legenda de cada rede

Escreva a legenda de cada rede escolhida num `post.json` (modelo em `kit/exemplo/post.json`), com os modelos
`modelos/post-instagram.md`, `modelos/post-tiktok.md` e `modelos/post-youtube.md` e as regras de
`metodo/capa-e-post.md`. O kit confere tudo antes de montar o pacote e recusa a legenda que quebra regra.

| | Instagram | TikTok | YouTube |
|---|---|---|---|
| Título | não tem | não tem | até 100 caracteres: série + parte + gancho |
| Texto | ~400 caracteres | 2 a 3 linhas | ~500 caracteres na descrição |
| Hashtags | até 5 | 3 a 5 | até 3 |
| Extra | rótulo de IA se a voz for sintética realista | comentário fixado com o dia da Parte 2 | marcar "Não é conteúdo para crianças" |

O Kwai segue o TikTok (até 5 hashtags, até 2.000 caracteres). Sem o bloco `kwai` no `post.json`, o kit usa o do
TikTok.

O kit recusa: "comenta", "curte", "compartilha", "marca alguém"; link no comentário fixado; hashtags acima do
limite; título acima de 100 caracteres; texto sem "Ficção" (série) nem "Fonte" (explicativo). Avisa quando as
opções do voto não aparecem no texto.

## Como gerar o pacote (modo agente, a partir da pasta `kit/`)

Renderize o episódio **uma vez** (comece pela folha de quadros-marco, `--stills`, para gastar o render completo só
depois de aprovado). O corpo do vídeo é o mesmo em todas as redes; muda só o CTA do fim e a linha da capa.

**Série:**

```
python capa.py <episodio>/episodio.json <trabalho>/capa.jpg --redes
python pacote_redes.py --nome <serie>_p<N> --video <video.mp4> --parte <N> --capa <trabalho>/capa.jpg --redes-capa \
                       --legendas <episodio>/post.json --episodio <episodio>/episodio.json
```

**Explicativo 3D** (a composição já sai com o CTA de cada rede em IG/, TIKTOK/ e YOUTUBE/):

```
python pacote_redes.py --nome <tema> --videos <trabalho>/<pasta-do-episodio> --gancho "<PRÓXIMO VÍDEO>" \
                       --capa <trabalho>/<pasta-do-episodio>/IG/capa.jpg --carimbar --legendas <episodio>/post.json
```

`--carimbar` põe a faixa com o CTA de cada rede embaixo de uma capa única (serve para qualquer capa). Sem
`--redes-capa` nem `--carimbar`, a mesma capa vai para todas e o kit avisa. O pacote sai em
`<trabalho>/entregas/<nome>/`. Para só as versões do vídeo (uma por rede escolhida), sem capa nem legenda:
`python cta_redes.py <video.mp4> --parte <N>`.

## Cópia para postar do celular

Se o usuário vai mandar o vídeo para o celular (WhatsApp, Telegram, chat da IA), o envio costuma aceitar no máximo
30 MB. Gere uma cópia abaixo de 29 MB para TikTok e YouTube, sem mexer na original:

```
ffmpeg -i video.mp4 -c:v hevc_nvenc -b:v 2.2M -tag:v hvc1 -c:a copy video_celular.mp4
```

Sem placa NVIDIA, troque `hevc_nvenc` por `libx265`. Confira o tamanho antes de entregar.

## Link com UTM no YouTube

No YouTube o link é clicável na descrição, e é ali que ele vai. Sempre com UTM, para saber de onde veio cada
clique:
`https://seusite.com/?utm_source=youtube&utm_medium=descricao&utm_campaign=<canal>&utm_content=<serie>`
O comentário fixado não leva URL em rede nenhuma (`metodo/licoes.md`, regra 28). No Instagram, no TikTok e no Kwai,
o link fica só na bio.

## Portão antes de entregar

- [ ] As opções do voto são as mesmas na capa, no vídeo e em todas as legendas.
- [ ] Nenhuma frase de isca ("comenta", "curte", "compartilha", "marca alguém").
- [ ] "Ficção" no vídeo e no texto (série) ou fonte citada (explicativo).
- [ ] Crédito de áudio com a licença.
- [ ] Hashtags dentro do limite de cada rede.
- [ ] Rótulo de IA indicado conforme `metodo/seguranca.md`.
- [ ] Áudio estéreo, 48 kHz, −14 LUFS (o kit confere sozinho no modo agente).

## Publicar de verdade

- **Manual (padrão):** o usuário abre cada pasta no celular e posta pelo app. É o caminho mais simples e sem risco.
- **Pela API oficial:** só no modo agente, só com as contas conectadas (`comandos/conectar-redes.md`) e **só depois da
  confirmação explícita do usuário para aquele vídeo**. Publicação não se desfaz pela API. Sempre `--seco` antes.

  | Rede | Comando (a partir de `kit/`) | O que faz |
  |---|---|---|
  | Instagram | `python -m publicar.instagram --video 01_IG/<...>_ig.mp4 --legenda 01_IG/<...>_legenda.txt --capa-ms 0` | Reel pela Graph API. A capa não muda depois de publicado: `--capa-ms 0` usa o quadro 0 (o gancho); para a capa do pacote, `--capa-url` com ela hospedada (ou troque no app) |
  | YouTube | `python -m publicar.youtube enviar --video 03_YOUTUBE/<...>.mp4 --titulo "..." --descricao 03_YOUTUBE/<...>.txt` | Short pela Data API (sobe privado por padrão; `--privacidade public` ou `--publicar-em`) |
  | TikTok | `python -m publicar.tiktok --video 02_TIKTOK/<...>_tiktok.mp4` | Manda para os rascunhos do app (app sem auditoria não publica direto); o dono escreve a legenda e publica no app |

## Depois de postar

1. Registre em `canal/historico.md` a data e o link de cada rede.
2. Cole os links no episódio em kit/placar/episodios.json (crie a partir de `kit/placar/exemplo/episodios.json`), que
   alimenta a apuração e o placar do site, e no `respostas.json` do robô.
3. Responda à mão os primeiros comentários. Para ver a resposta sugerida de cada voto (só Instagram):
   `comandos/conectar-redes.md`, "Robô de respostas". Responder pela API não é recomendado.
4. Na hora de fechar o voto (48 h): `comandos/apurar-votos.md`.
