<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# 10 · Comunidade: apuração, respostas e placar

Carregue com "apurar votos" e no dia de cada publicação.

## 1. Regras de contagem

Escreva as palavras aceitas de cada opção **antes** de publicar (na bíblia ou no arquivo do episódio).

| Regra | Exemplo | Por quê |
|---|---|---|
| Número no começo conta | "1", "2 sem dúvida" | Forma mais rápida de responder |
| Palavra da opção ou variação conta | "abre", "abria", "abre a porteira" = ABRIR; "tranca", "deixa trancada" = TRANCAR | O público responde como fala; não exigir palavra exata tira a cara de bait |
| Forma curta com 4+ letras conta | "TRANC" = TRANCAR | Erro de digitação não anula voto |
| Sem acento e sem diferença de maiúscula | "silencio" = SILÊNCIO | Normalização |
| Letra estilizada conta | Fontes "bonitas" de teclado | Normalize (NFKD) antes de comparar |
| Citar as duas opções não conta | "1 ou 2, sei lá" | Ambíguo |
| Negação clara inverte | "não abre" = TRANCAR (com a regra `nega` do episódio; sem ela, fica de fora) | Leia a frase, não só a palavra |
| **Um voto por perfil** | Vale o primeiro comentário de voto | Evita voto em série |
| Voto em resposta a outro comentário conta | — | Ainda é a escolha da pessoa |
| Só vale dentro da janela (48 h depois de postar) | — | Voto atrasado não muda nada |

**Placar oficial só com 10 votos ou mais.** Abaixo disso, a opção vencedora decide, mas não se mostra número. Nunca
estime nem invente placar.

## 2. Como apurar

Tutorial para o usuário, com os três jeitos (API oficial, copiar e colar, enquete) e o que nunca fazer:
`metodo/contar-votos.md`.


- **Instagram e YouTube:** leitura de comentários pela API oficial, com a regra acima já no código
  (`kit/placar/placar.py`, ver `comandos/apurar-votos.md`) ou à mão.
- **TikTok:** a Display API não entrega o texto dos comentários. Copie os comentários do TikTok Studio para um `.txt`
  e o kit conta com a mesma regra. A leitura pela API for Business depende de aprovação da TikTok, sem prazo.
- Some todas as redes em que o episódio saiu. Registre no arquivo do episódio: total por rede, total por opção,
  ambíguos descartados.
- Empate: decide a opção que o protagonista menos faria (é a que surpreende) e diga isso no episódio seguinte.
- Sem API de leitura: o usuário cola os comentários (sem @ de ninguém) ou manda prints, e você conta pelas regras acima.

## 3. Depois da apuração

1. Story ou post curto com o resultado (Instagram) e comentário fixado atualizado em todas.
2. Desfecho vencedor e marca na bíblia.
3. O episódio seguinte abre com o gancho e, logo depois, o placar real animado (`kit/apuracao_video.py`;
   `metodo/formato-serie.md`, seção 5).
4. Opcional: bônus "E se vocês tivessem escolhido...?" (até 60 s).

## 4. Respostas a comentários

Responder dá vida à série. Robô respondendo demais é spam. Regras:

**À mão (o recomendado, todas as redes):** na primeira hora depois de publicar, responda à mão, no app, os primeiros
comentários. É o que mais vale.

**Pela API: não recomendado.** A Meta trata resposta automática como robô e pode rebaixar ou travar a conta. O
`kit/publicar/responder_votos.py` (só Instagram) lê os votos e **sugere** a resposta de cada um, para você colar à
mão; só envia de verdade com `--sei-o-risco`. Se usar mesmo assim, ele segue estes limites:
- só responde comentário que é voto;
- no máximo metade dos votos, sorteada;
- 1 resposta por pessoa por vídeo;
- no máximo 3 por rodada e **30 por dia**;
- só comentários dos últimos 7 dias;
- textos variados no clima da série (4 a 6 por episódio), nunca o mesmo texto duas vezes seguidas;
- espera aleatória de 4 a 11 s entre respostas;
- só das 9h à 1h (conta que responde de madrugada parece robô), rodando a cada 30 min;
- qualquer erro da API para tudo até a próxima rodada.

**Nunca:** curtir comentário por robô (não existe na API; robô clicando é automação não oficial), seguir de volta
por robô, mandar DM automática, responder igual em massa.

Exemplos de resposta no clima (sem comando, sem prometer nada):
- "A Luísa ouviu você."
- "Corajoso. Ou ingênuo. Na sexta a gente descobre."
- "Anotado. A porteira também ouviu."

## 5. Dados de pessoas

Comentário traz nome e @ de pessoas reais. Guarde só o necessário para contar (id do perfil para a regra de um voto),
apague depois da apuração e nunca publique lista de quem votou. Nunca use comentário de alguém em vídeo sem
autorização.

## 6. Página de placar (opcional)

Uma página simples com as séries, os episódios em ordem, "Assistir no Instagram" e o placar de cada voto ajuda quem
chega pelo meio. Não precisa de player: o vídeo fica nas redes. Série que sai do ar sai inteira da página.

## Site é opcional

Para começar, não precisa de site. O voto acontece nos comentários e a apuração pode ser manual ou feita pela IA lendo os
comentários. Quando quiser uma página de placar:
1. **Grátis:** o kit traz o placar pronto (`kit/placar/`): a página lê os votos e as views do Instagram, do TikTok e do
   YouTube pelas APIs oficiais (o Kwai ainda não entra) a cada 30 minutos e fica no GitHub Pages, sem servidor.
   Passo a passo em `kit/placar/LEIA-ME.md`.
2. **Depois, se o canal crescer:** domínio próprio e hospedagem (ver `LINKS.md`). Fica mais profissional, mas não é
   requisito.

Não trave o primeiro episódio esperando site.
