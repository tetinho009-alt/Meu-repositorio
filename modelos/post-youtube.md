<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Post · YouTube Shorts

Regras em `metodo/capa-e-post.md`. Título até 100 caracteres; descrição até 5.000; até 3 hashtags.

## Título

```
[Série] · Parte [N]: [gancho em pergunta] | Terror animado
```

Exemplo (71 caracteres):

```
O Último Ônibus · Parte 1: quem é o oitavo passageiro? | Terror animado
```

## Descrição

```
[Sinopse em 2 a 3 frases, sem contar o fim.]

Se fosse você: [ação 1] ou [ação 2]? A escolha da maioria vira a Parte [N+1].

Playlist da série: [Série] · série de terror interativa
[Placar e episódios: link, se houver]

Ficção · personagens e lugar inventados.
Áudio: [título] · [autor] · [licença ou YouTube Audio Library]

#[genero] #[tema] #[genero2]
```

Exemplo preenchido:

```
Meia-noite e quarenta, o último ônibus da linha 1047. A Tati contou sete passageiros. Quando olhou de novo, eram oito. E a colega que disse estar no mesmo ônibus tinha saído às seis.

Se fosse você: descia no ponto ou ficava no ônibus? A escolha da maioria vira a Parte 2.

Playlist da série: O Último Ônibus · série de terror interativa

Ficção · personagens e lugar inventados.
Áudio: trilha e efeitos gerados para a série · licença comercial do plano.

#terror #historiadeterror #suspense
```

## Campos no envio (API) ou no Studio

- `categoryId`: 1 (Filmes e animação) ou 24 (Entretenimento).
- `selfDeclaredMadeForKids=false` (público "não é para crianças").
- `containsSyntheticMedia`: "Sim" se houver plano realista ou música gerada por IA; animação com trilha licenciada:
  "Não" (`metodo/seguranca.md`).
- `privacyStatus=private` + `publishAt` para agendar na mesma hora das outras redes.

## No Studio, depois de subir

- Quadro de capa forte.
- Vídeo relacionado: a parte seguinte, quando existir.
- Comentário fixado com a pergunta do voto e, depois, o placar.
- Adicionar à playlist da série.
- Uma hora depois: aba de direitos autorais sem reivindicação.
