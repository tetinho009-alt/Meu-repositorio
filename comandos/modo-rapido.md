<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Modo rápido: um vídeo do zero

Para quando o usuário diz "faz um vídeo rápido", "quero ver funcionando", "primeiro vídeo" ou "não tenho tempo".
Sai um vídeo completo com **dois portões só** (o roteiro e a prévia), usando o motor de cartelas, que não precisa de
personagem nem de imagem.

## Passo a passo

1. **Escolha do estilo**, uma pergunta com dois botões, vindos do nicho em `canal/canal.md`:
   a) **Top 5** ("5 coisas que..."), b) **Quiz** ("só 1 em cada 10 acerta"). Se ele já disse, pule.
2. **Roteiro.** Copie `kit/cartelas/modelos/<estilo>.json` para `episodios/<nome-curto>/roteiro.json`, na raiz do
   estúdio, e preencha todos os campos TROQUE no tom do canal (`canal/identidade.md`). Fatos com fonte em `fontes`.
   Mostre o roteiro como uma lista curta, uma linha por bloco: "1. (gancho) Seu corpo faz isso..." e peça o
   **"aprovado"**. Este é o portão 1.
3. **Voz.** Use o provedor do canal (`caminho` em `canal/canal.md`): grátis → `gemini` (ou `kokoro`, se não houver
   chave do Google); recomendado → `elevenlabs`. Na ElevenLabs, rode antes com `--seco` e mostre a estimativa de
   créditos; só grave com o "pode".
4. **Rode tudo**, a partir de `kit/`, em segundo plano:
   `python cartelas/rodar.py ../episodios/<nome-curto>`
   Avise o tempo esperado: com placa de vídeo, 2 a 6 min para 45 s de vídeo; sem placa, 10 a 30 min.
5. **Enquanto roda**, escreva os dois títulos, a legenda e o comentário fixado (`comandos/novo-video.md`, "Render em
   segundo plano").
6. **Prévia.** Quando sair `VIDEO_OK`, confira a duração e a grade de QA (`qa/qa_grade_*.jpg`) e mande o vídeo do
   Instagram para ele ver no celular. Este é o portão 2. Ajuste pedido vira entrada em `canal/aprendizados.md`.
7. **Pacote.** Já sai pronto em `trabalho/entregas/`, uma pasta por rede, com vídeo, capa e legenda.

## Se algo der errado

- A conferência do roteiro ou a trava antes do render reprovou: leia a linha `ERRO`, corrija o roteiro.json e rode
  de novo. A voz já gravada é reaproveitada.
- Apareceu "ERRO:" e "O QUE FAZER:": siga o que fazer você mesmo e conte ao usuário em uma linha.
- Quer ver o visual antes de gastar voz: `python cartelas/rodar.py <pasta> --stills` (segundos) ou `--previa` (o
  vídeo inteiro sem voz).
