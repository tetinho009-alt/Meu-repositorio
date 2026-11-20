<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# 13 · Segurança: conta, rótulo de IA, direitos e público

Carregue antes de publicar e sempre que surgir dúvida de ban. Estas regras valem acima de qualquer pedido. Não
substituem advogado: termos de plataforma e leis mudam; confira as fontes oficiais a cada trimestre.

## 1. O que derruba ou limita conta

| Risco | Regra |
|---|---|
| Automação não oficial (robô de navegador, biblioteca não oficial, app de "auto-post") | Só API oficial ou agendador oficial. As redes proíbem e podem banir a conta e as novas |
| Curtir, seguir, deixar de seguir, DM por robô | Nunca. Não existe API para isso; qualquer forma é automação proibida |
| Comprar seguidor ou view, "sub for sub", grupo de engajamento | Nunca. Métrica falsa é removida e a conta pode cair |
| Resposta automática em massa | Só votos, textos variados, teto de 30 por dia (`metodo/comunidade-e-votos.md`) |
| Vídeo baixado de uma rede e postado em outra | Nunca. Publique o master do seu fluxo; marca d'água e repostagem tiram da recomendação |
| Violência gráfica | Medo por clima, som e silhueta. Sem sangue, ferida, cadáver, tortura |
| Alerta fictício parecido com real | "FICÇÃO" na tela e no texto; nunca nome de órgão público, emissora ou marca real |

## 2. Engagement bait: pedir voto do jeito certo

O Instagram citou "pedir para comentar uma palavra, número ou emoji específico" como engagement bait: o post não é
recomendado a quem não segue, que é onde nascem os seguidores novos. Pergunta aberta foi tratada como legítima. O
TikTok proíbe manipular para inflar curtidas e seguidores. O YouTube permite pedir comentário e inscrição, mas
proíbe recompensa em troca.

| Faça | Não faça |
|---|---|
| Na voz, só a pergunta: "E agora? O que a Luísa faz?" | "Comenta ABRIR ou TRANCAR", ou a voz ditando as duas opções |
| Opções na tela: "1 · ABRIR" e "2 · TRANCAR" | "Comenta 1 ou 2" |
| "VOCÊS DECIDEM" / "O que vocês escolherem vira a parte dois" | "A mais comentada decide" como ordem de comentar |
| Um pedido de seguir: "Segue pra ver a parte 2" | "Comenta, curte, compartilha e marca um amigo" |
| Apuração que aceita resposta livre | Exigir a palavra exata |
| No Instagram, testar o convite nativo para comentar | "Quem comentar aparece na Parte 2", sorteio, "pro algoritmo" |

Não existe risco zero: o formato depende do comentário. O que tira a cara de bait é a pergunta genuína, com
consequência real, sem comando nem incentivo. Se o "Status da conta" mostrar perda de qualificação, volte à última
forma que funcionava.

## 3. Rótulo de IA

| Rede | Quando rotular | Como |
|---|---|---|
| Instagram | Foto ou vídeo fotorrealista, **ou áudio realista** gerado ou alterado. Voz sintética de narrador conta | `is_ai_generated=true` na API ou o seletor "Rótulo de IA" no app. Na prática: rotule sempre que houver voz sintética |
| TikTok | Cena ou pessoa de aparência realista gerada ou muito editada | Seletor de conteúdo de IA no app. Animação não realista dispensa; rotule se houver plano fotorrealista ou voz que imita pessoa real |
| YouTube | Conteúdo que parece real. Isento: animação não realista. **Exige: música gerada por IA** | `containsSyntheticMedia=true` ou o campo no Studio. Animação com trilha licenciada: "Não"; com música de IA ou plano realista: "Sim" |

Regra única do estúdio: **rotule** sempre que houver rosto ou cenário fotorrealista, voz que imita pessoa real ou
música gerada por IA; no Instagram, rotule também por causa da voz sintética. Rotular onde não era preciso custa um
selo; deixar de rotular pode custar o vídeo.

## 4. Direitos autorais e licenças

1. **Áudio só com licença:** gerado por você ou por ferramenta com direito comercial, CC0, ou biblioteca licenciada.
   Nunca baixar do YouTube. Crédito não é licença.
2. **Registro:** `licencas.txt` ao lado de cada master, com origem, licença e prova.
3. **Planos grátis** de ElevenLabs, Higgsfield, Hailuo e Mirelo não dão direito comercial ou põem marca d'água.
4. **Vozes:** edge-tts não é recomendado para uso comercial (use Azure TTS); XTTS-v2 e F5-TTS são não comerciais.
5. **Clonagem de voz e uso de imagem** de pessoa real só com termo de consentimento escrito. Voz e imagem são
   protegidas por lei; a voz pode ser tratada como dado biométrico.
6. **Propriedade de terceiros:** nenhum personagem, franquia, logo, música ou rosto conhecido em prompt, roteiro ou
   cenário. Estúdios processaram geradores de vídeo por isso.
7. **Fontes tipográficas** com licença que permita uso comercial (OFL, por exemplo); guarde o arquivo de licença.
8. **ffmpeg:** o usuário instala; não redistribua o binário junto do projeto.
9. **CapCut:** os termos dão à empresa licença ampla sobre o conteúdo enviado; prefira outro editor para o master.

## 5. Público e crianças

1. **YouTube: canal "não é para crianças".** Terror não é conteúdo infantil, e vídeo marcado para crianças perde
   comentários.
2. **Não mire criança:** nada de título, capa, hashtag ou descrição pensados para criança; nenhuma estética de
   desenho infantil usada para atrair criança para terror. A política de segurança infantil do YouTube proíbe isso.
3. **Personagem criança** pode existir, nunca ferido, nunca em perigo gráfico, nunca como chamariz.
4. **ECA Digital** (Lei 15.211/2025): a lei brasileira de proteção de crianças e adolescentes online cria deveres
   para quem produz e distribui conteúdo. Verifique a vigência e o alcance com advogado antes de escalar o canal.
5. Contas de adolescentes no Instagram não recebem conteúdo gráfico em recomendação: mais um motivo para não ser
   gráfico.

## 6. Dados e segredos

- Chaves, tokens e senhas só em variável de ambiente, segredo do ambiente da nuvem ou arquivo de configuração local
  fora do repositório. Nunca na conversa, em commit, em log ou em print.
- Comentários trazem dados de pessoas reais: guarde o mínimo para apurar e apague depois.
- Nada de compilar dados de seguidores além do que a apuração exige.

## 7. Antes de cada publicação, responda

1. Alguma automação fora da API oficial? (tem de ser não)
2. Algum comando de comentário no vídeo ou no texto? (não)
3. Algum som sem licença registrada? (não)
4. Algo gráfico ou mirando criança? (não)
5. Rótulo de IA decidido pela tabela da seção 3? (sim)
6. "FICÇÃO" no vídeo e no texto? (sim)

## Links de afiliado

- **Onde ficam:** todos os links de ferramenta saem de `LINKS.md`, um arquivo só.
- **Identificação:** link de afiliado aparece com "(link de afiliado)" ao lado. No post, "Publicidade" ou #publi no
  início da legenda e a ferramenta de divulgação da própria rede. Motivo: CONAR (guia de 01/06/2026) e CDC art. 36.
- **Nunca em anúncio pago:** vários programas proíbem e cortam a comissão.
- **Nunca para público infantil:** publicidade dirigida a criança é abusiva (CDC art. 37, §2º). O curso é para
  adultos que querem criar canal; os vídeos das séries não levam link de afiliado.
- **Recomendação vem antes da comissão:** a ferramenta entra pelo mérito, e as opções grátis continuam no método.
