<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Exemplo · "Isso não é uma água-viva" (14 s)

Versão curta de demonstração do Explicativo 3D. Mostra o fluxo inteiro (pergunta na tela, objeto desmontado,
uma parte por palavra, micro-gag, remontagem, volta ao plano do começo e CTA de cada rede) em menos de 15 s.
Um explicativo de verdade tem de 40 a 65 s (`metodo/formato-explicativo.md`).

## Narração (`narrador.txt`, um bloco por linha)

| s | Fala | Tela |
|---|---|---|
| 0,0 | Isso não é uma água-viva. | Plano aberto da fatia de oceano; gancho "ISSO NÃO É UMA ÁGUA-VIVA" até 2 s |
| 2,5 | A caravela-portuguesa é um condomínio de bichinhos grudados. | A câmera chega perto; em "condomínio" as 4 partes se soltam (cada uma com olhos) |
| 6,8 | Um boia, um caça, um come... e um namora. | Cada parte quica na sua palavra e ganha o rótulo; coração no "namora" |
| 9,8 | E sozinho, nenhum deles sobrevive. | A digestão se afasta e murcha no "sozinho"; tudo encaixa de volta no "sobrevive" |
| 12,2 | (cartão de CTA, 2,2 s) | A câmera volta ao plano do começo (o replay emenda); CTA da rede por cima |

Micro-gag: o peixe-palhaço chega perto dos tentáculos e, no "caça", dá meia-volta e foge. Sem efeito, sem seta.
Achado no corte: um chinelo enterrado na areia, visível só no plano aberto.

CTA (o "PARTE 2" do formato série vira o gancho do próximo vídeo, "POR QUE ELA QUEIMA MESMO MORTA"):

| Rede | Cartão |
|---|---|
| Instagram | SEGUE PRA VER POR QUE ELA QUEIMA MESMO MORTA · selo SEGUIR |
| TikTok | SEGUE PRA NÃO PERDER POR QUE ELA QUEIMA MESMO MORTA · selo SEGUIR |
| YouTube | SE INSCREVE PRA VER POR QUE ELA QUEIMA MESMO MORTA · selo INSCREVER-SE |

## Fatos e fontes

- A caravela-portuguesa (*Physalia physalis*) não é água-viva: é um sifonóforo, uma colônia de indivíduos
  especializados (zooides) que só vivem juntos. Fontes:
  [NOAA Ocean Service](https://oceanservice.noaa.gov/facts/portuguese-man-o-war.html),
  [GBIF](https://www.gbif.org/species/144101866).
- Os quatro "empregos": flutuar (pneumatóforo, a boia), caçar (dactilozooides, os tentáculos), digerir
  (gastrozooides) e reproduzir (gonozooides). Fonte: [encyclopedia.pub](https://encyclopedia.pub/entry/31497).
- "Bichinhos grudados" é simplificação: os zooides são clones que brotam de um mesmo embrião. A fala não diz que são
  bichos de espécies diferentes, e isso evita o comentário corrigindo.
- Gancho do próximo vídeo: morta na areia, ela ainda queima, porque os nematocistos continuam ativos. Fonte:
  [SOBRASA](https://sobrasa.org/new_sobrasa/arquivos/recomendacoes/LESOES%20POR%20AGUAS-VIVAS_Recomendacao_SOBRASA.pdf).

## Voz

A narração que vem no kit (`audio/narrador.mp3`) foi gerada com o Kokoro (Apache-2.0, voz `pm_alex`), um dos
provedores do kit. Para usar a sua voz: `python explicativo3d/exemplo/rodar.py --voz elevenlabs` (ou `azure`,
`piper`, `kokoro`). Como tudo é marcado por palavra, câmera, efeitos, rótulos e legenda se ajustam sozinhos ao novo
ritmo. Se trocar o texto, mantenha as palavras usadas como marco (`caravela`, `condomínio`, `boia`, `caça`,
`come`, `namora`, `sozinho`, `sobrevive`) ou troque os marcos em `cena.py`, `trilha.py` e `episodio.json`.
