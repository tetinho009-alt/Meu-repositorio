<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Canal pronto de exemplo: Bicho Esquisito

**Isto é um exemplo.** Um canal inventado (@bichoesquisito, curiosidades de bichos para adultos curiosos, tom
bem-humorado) com a identidade inteira já feita pelo kit, para você ver aonde chega antes de fazer a sua. Não poste
estas peças como se fossem do seu canal: o nome, o @ e o mascote são só de demonstração.

## Para fazer o seu

Escolha um dos dois jeitos. Os dois chegam no mesmo tipo de pasta que esta.

- **Grátis (recomendado):** diga à IA **"faz a identidade do meu canal"**. Ela preenche um `marca.json` com o nome,
  as cores e o mascote do seu canal e roda o gerador do kit (`kit/idv/README.md`). Tudo por código, sem gastar nada.
- **Pelo ChatGPT (precisa de assinatura paga do ChatGPT):** use os prompts de
  `modelos/prompts-chatgpt-identidade.md`. O ChatGPT desenha o mascote e as artes; o kit escreve os textos por cima e
  monta as peças nas medidas certas.

## O que tem aqui

| Pasta ou arquivo | O que é |
|---|---|
| `marca.json` | A marca do canal: nome, @, cores, fontes, mascote, séries e os textos de exemplo. É a única fonte: o resto sai dela. |
| `mascote/` | O Bubi, um axolote desenhado só por código (`desenhar_mascote.py`), em 5 poses + o busto do ícone. |
| `logo/` | Logo colorido e de uma cor só (PNG e SVG), ícone quadrado, símbolo solto. |
| `perfil/perfil_1080.png` | Foto de perfil para todas as redes (feita para o recorte em círculo). |
| `youtube/` | Banner 2560x1440, banner com as áreas de cada tela marcadas, marca d'água 150x150. |
| `destaques/` | Capas de destaque do Instagram (uma por série + "Comece aqui" e "Resultados"). |
| `./modelos/exemplo/` | Capa de episódio (e a versão com o recorte 3:4 da grade), post de feed, card de parte nova, card de resultado do voto (números de demonstração), capa de playlist. |
| `manual_idv.png` e `MANUAL_IDV.md` | O manual da marca: logo, paleta, fontes, mascote, faça e não faça. |
| `conferencia.jpg` | Todas as peças numa folha, a foto de perfil em tamanho de app e o banner como aparece no celular. |
| `bio.md` | Bio pronta para Instagram, TikTok, YouTube e Kwai, dentro do limite de cada um. |
| `primeiros-posts.md` | As 3 primeiras ideias de vídeo, com o gancho e o roteiro no formato do kit. |

Para gerar tudo de novo (depois de mudar o `marca.json`), a partir de `kit/`:

```
python idv/gerar_idv.py tudo --marca ../exemplos/canal-pronto/marca.json --saida ../exemplos/canal-pronto
```
