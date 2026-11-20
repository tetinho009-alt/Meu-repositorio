<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Apurar votos

A apuração é real: lida dos comentários pelas APIs oficiais, com a mesma regra em todo lugar (o placar do site, o
vídeo da parte seguinte e o robô de respostas). Detalhe da regra em `metodo/comunidade-e-votos.md`.

## A regra

- Vale o número da opção ("2", "2222") ou a palavra dela entre as 3 primeiras ("abre", "abria a porteira").
- Um voto por perfil em cada rede: quem votou duas vezes conta a primeira.
- Só conta comentário feito dentro da janela de votação (48 h depois de postar).
- Comentário com as duas opções não conta. "Não abre" conta como a outra opção só se a série tiver a regra `nega`.
- Comentário do próprio perfil (fixado, aviso) não conta.
- **Placar oficial só com 10 votos ou mais.** Com menos, a parte seguinte mostra só a opção que venceu, sem número.

## Como apurar (modo agente, a partir da pasta `kit/`)

1. Confira se o episódio está no kit/placar/episodios.json (modelo em `kit/placar/exemplo/episodios.json`) com as
   opções, as palavras de cada uma, a data de publicação e o link de cada rede.
2. **TikTok:** a API oficial não entrega o texto dos comentários. Peça ao usuário para copiar os comentários do
   TikTok Studio para um `.txt` (um por linha; "@usuario: texto" deixa contar um voto por perfil) e aponte o arquivo
   em `tiktok_comentarios` no episódio.
3. Rode a apuração do episódio:

   ```
   python placar/placar.py --episodios placar/episodios.json --so <slug> --detalhe trabalho/apuracao_<slug>.json
   ```

   Ela lê Instagram (`IG_ACCESS_TOKEN`) e YouTube (`YT_API_KEY`) pelas APIs e o `.txt` do TikTok, e imprime o placar
   por rede. Sem as chaves, a rede que falta fica de fora e o comando avisa: nunca complete número na mão.
4. Mostre ao usuário o placar por rede, o total, a opção que venceu e a marca que ela liga na bíblia
   (`series/<serie>/SERIE.md`). Em empate, o desempate é decisão da história: proponha e peça aprovação.
5. Registre em `canal/historico.md`: a pergunta, a opção que venceu, os votos por rede e a data da apuração.
6. **A apuração é a última coisa renderizada.** Produza e aprove a parte seguinte inteira primeiro; só minutos
   antes de postar releia o placar (passo 3), gere a apuração e emende. A hora da leitura que aparece na tela é a
   desse último passo. Gere a apuração animada para abrir a parte seguinte (6,6 s, som por código). `--comentarios` põe embaixo uma faixa
   com comentários reais, só o texto e sem @: mostre a lista ao usuário antes e tire o que identifica alguém.

   ```
   python apuracao_video.py trabalho/apuracao_<slug>.json --saida trabalho/apuracao_<slug>.mp4
   ```

   Depois que o vídeo da parte seguinte estiver pronto, emende a apuração logo depois do gancho (o segundo em que o
   bloco 0 da narração termina, no `linha.json` do episódio):

   ```
   python apuracao_video.py trabalho/apuracao_<slug>.json --saida trabalho/apuracao_<slug>.mp4 \
                            --inserir-em <parte2>.mp4 --apos <segundos>
   ```

7. Pergunte uma coisa só: "Começo a Parte N+1 com o desfecho que venceu?" (`comandos/novo-video.md`).

## Sem o modo agente

O usuário cola os comentários de cada rede no chat (ou manda prints). Conte com a regra acima, rede por rede, e mostre
a contagem com os comentários que ficaram de fora e o motivo. Na parte seguinte, a apuração vira uma tela no editor
com os números exatos.

Nunca invente número de voto. O público confere, e o placar falso destrói a confiança na série. A apuração privada
(`--detalhe`) tem só o texto dos comentários, sem @; apague quando a série acabar.
