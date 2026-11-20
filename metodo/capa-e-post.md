<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# 07 · Capa e texto do post

Carregue depois do checklist aprovado. Templates prontos: `modelos/post-instagram.md`, `modelos/post-tiktok.md`,
`modelos/post-youtube.md`.

## 1. Capa

| Item | Regra | Por quê |
|---|---|---|
| Formato | JPEG 1080x1920, até 8 MB | Limite do `cover_url` do Instagram |
| Área útil | O essencial no quadrado central e dentro de x 120–900 | O grid do perfil corta a capa; o resto some |
| Elenco | Personagens recortados, grandes, com a luz da série | Capa só com frase chapada foi reprovada: não vende a série |
| Nome da série | Gigante, com o mesmo brilho da abertura | Quem procura a série reconhece no grid |
| "PARTE N · título" | Pílula acima ou abaixo do nome | Ordem da série no grid |
| Pergunta do voto | Na cor de destaque, com **as mesmas opções da tela** ("ABRIR OU TRANCAR?") | Capa com opções diferentes confunde a apuração |
| Linha de apoio | "USE FONE · VOCÊS DECIDEM A PARTE 2" | Reforça o formato |
| Criança | Nunca como chamariz da capa | Política do YouTube contra atrair criança para conteúdo adulto |

Capa por rede:
- **Instagram:** imagem própria (`cover_url`) ou um quadro do vídeo. Capa de Reel já publicado não muda pela API:
  troca-se no app (Editar > Capa).
- **TikTok:** um quadro do vídeo (`video_cover_timestamp_ms` na API ou escolha no app). Escolha um quadro forte (o
  sorriso no zoom, a silhueta).
- **Shorts:** quadro escolhido no app do YouTube. Por isso o vídeo precisa de um quadro que funcione como capa.

Prompts de arte da capa: `metodo/identidade-visual-prompts.md`. No kit, comando de capa em `kit/README.md`.

## 2. Texto do post: regras comuns

1. **Primeira linha = série + parte.** "O Sítio · Parte 1 · 'Quem chama na porteira'". Quem acompanha série busca
   por isso.
2. **Duas a quatro frases de sinopse**, sem contar o fim, terminando no gancho.
3. **A pergunta do voto como pergunta aberta**, com as opções como escolha da história: "Se fosse você: abria a
   porteira ou deixava trancada?" Feche com "A escolha da maioria vira a Parte 2." Nunca "comenta X ou Y".
4. **Um pedido por post.** Nunca "comenta, curte, compartilha e marca".
5. **Sem incentivo:** nada de "quem comentar aparece na Parte 2" ou sorteio.
6. **"Ficção · personagens e lugar inventados."**
7. **Crédito de áudio com a licença:** "Áudio: [título] · [autor] · [licença]". Sem "YouTube" como fonte.
8. **"Assiste de fone."** opcional. Emoji no texto do post é escolha do canal; um no título basta.

## 3. O que muda por rede

| | Instagram | TikTok | YouTube Shorts |
|---|---|---|---|
| Título | Não tem | Não tem | Até 100 caracteres: série + parte + gancho + "Terror animado" |
| Texto | Até 2.200 caracteres; use ~400 | Curto: 2 a 3 linhas | Descrição até 5.000; use ~500, com playlist e link |
| Hashtags | **Máximo 5** | 3 a 5 específicas | Até 3 (aparecem sobre o título) |
| Rótulo de IA | `is_ai_generated` quando houver voz sintética realista | Quando houver cena realista | `containsSyntheticMedia` quando houver cena realista ou música de IA |
| Extra | Pode testar o convite nativo para comentar (`is_comment_prompt_used`) | Comentário fixado com "Parte 2 sai [dia] às [hora]" | Comentário fixado com a pergunta; "vídeo relacionado" aponta para a parte seguinte |

Hashtags: específicas do gênero e da série (`#terror #historiadeterror #suspense #animacao` + uma da série). `#shorts`
é desnecessário. Hashtag que mira criança é proibida.

## 4. Portão

- [ ] Opções da capa = opções do vídeo = opções do texto.
- [ ] Nenhuma frase de comando no voto.
- [ ] "Ficção" no texto.
- [ ] Crédito de áudio com licença.
- [ ] Hashtags dentro do limite da rede.
