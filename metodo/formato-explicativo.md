<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# 15 · Vídeo explicativo e micro-gags

Carregue este arquivo quando o usuário quiser vídeo **explicativo** ("como funciona X", "e se X acontecesse") em vez de
série interativa, ou quando for planejar os momentos engraçados de qualquer vídeo.

## Dois formatos, o mesmo motor

| Formato | Pergunta que move | O que prende | Fim |
|---|---|---|---|
| Série interativa | "O que a personagem faz?" | Mistério e a escolha | Voto: a escolha da galera vira a próxima parte |
| Explicativo / "e se" | "Como funciona X?" / "E se X?" | Curiosidade e as gags | Pergunta aberta: "e na sua casa, já viu isso?" |

Os dois usam os mesmos personagens, a mesma voz, a mesma legenda palavra a palavra e as mesmas regras de segurança
(`metodo/seguranca.md`).

## Estrutura do explicativo (40 a 65 s; a trava aceita 30 a 75)

1. **Quadro 0:** a pergunta na voz e na tela ao mesmo tempo, com o objeto em close, como "Como a caixa d'água sabe
   a hora de parar de encher?". Nada de pergunta só na tela antes da voz: a trava do gancho reprova.
2. **Até 5 s:** o boneco tenta e erra, o jeito "errado" e engraçado de pensar.
3. **5–40 s:** a explicação em 3 a 5 passos, um plano por passo, com o objeto em corte, vista explodida ou dentro do
   cano.
4. **No meio:** 2 ou 3 micro-gags (abaixo).
5. **Final:** a revelação em uma frase e uma pergunta aberta para comentar em palavras próprias. Nunca "comenta X".

Pesquise o fato antes de explicar. Explicação errada vira comentário corrigindo e desmoraliza o canal.

## Micro-gags: o gancho que faz comentar sem pedir

Uma micro-gag é uma bobeira **discreta** que o boneco faz no meio de uma ação séria, sem nenhum destaque na tela. Quem
nota comenta ("ele tá rebolando kkkk"), quem não notou volta para ver, e isso gera comentário e replay, os dois sinais
mais fortes do algoritmo. Exemplo real: um canal viralizou porque o boneco, enquanto pescava, parecia estar rebolando.

Regras:
- **Discreta.** De 1 a 2 s, sem efeito sonoro de piada, sem seta, sem zoom. Se a tela aponta, deixa de ser
  descoberta.
- **Em ação séria.** A graça vem do contraste: a narração explica a física e o quadril balança no ritmo.
- **Posição:** uma entre 8 e 15 s (onde a retenção costuma cair) e outra perto do fim. No máximo 3 por vídeo.
- **Nunca no rosto em fala importante,** porque atrapalha entender a explicação.
- **No terror:** só gag de tensão, como o boneco do fundo que mudou de lugar ou o rosto no mato. Nada engraçado que
  quebre o medo.
- **Nada sexualizado.** O "rebolado" é bobo e cartoon, não sensual. Personagem criança nunca faz gag de dança de
  quadril.

Biblioteca de gags. No motor 3D do kit o "boneco" é o próprio objeto: cada parte tem olhos e quica, murcha ou foge
na palavra dela (gag de objeto vivo, como no exemplo da caravela). As gags de corpo da tabela valem para o
personagem 2D ou para um boneco 3D que você modelar e animar por código no mesmo esquema:

| Gag | O que o boneco faz | Onde funciona |
|---|---|---|
| rebolado | O quadril balança no ritmo enquanto faz a tarefa | Pescando, esperando, cozinhando |
| cabeça no beat | A cabeça marca o ritmo da trilha por 4 tempos | Explicação longa |
| piscadinha | Olha para a câmera, pisca e volta | Logo depois de uma frase "séria" |
| disfarça | Percebe que está sendo filmado e assobia | Depois de um erro do boneco |
| dancinha de 1 s | Um passinho curto quando ninguém olha | Transição entre passos |
| objeto vivo | Um objeto do cenário reage (a torneira "olha") | Explicativo de casa e objetos |

## 3D: modelar por código, marcar por palavra

O motor está em `kit/explicativo3d/` (instalação, tempo de render medido e conferência em
`kit/explicativo3d/INSTALAR.md`). Exige o Blender 5.2 LTS e uma placa de vídeo; a integrada serve, mais devagar.
O exemplo pronto é a caravela-portuguesa desmontada em 14 s, nas 3 versões de CTA. Rode a partir da pasta `kit/`:

```
python explicativo3d/exemplo/rodar.py --stills   # 5 quadros-marco para aprovar
python explicativo3d/exemplo/rodar.py            # IG, TIKTOK e YOUTUBE com o CTA de cada rede, capa e grade
```

- **Cenário e personagem do assunto, nunca os do exemplo.** O exemplo é do fundo do mar. Raio em casa pede sala em
  corte com tempestade; geladeira pede cozinha. Escolha o `"fundo"` do `episodio.json` pelo assunto e ponha pelo
  menos um personagem com olhos (`mascote(...)` cria um de qualquer coisa). Detalhes e peças prontas em
  `comandos/novo-video.md`, seção do Explicativo 3D; a trava `motor/trava_cena.py` confere antes do render.
- **Cena por código.** Nada é modelado à mão: o cenário (fatia do mundo em corte, coral, alga, pedra, luz) e o objeto
  (cada parte num vazio próprio, para desmontar) saem de `motor/kit3d.py` e `motor/bichos3d.py`; peixes prontos
  só de modelo CC0 (`kit/explicativo3d/modelos/FONTES.md`). O episódio é um `cena.py` que monta, anima e renderiza
  (`blender -b -P cena.py`), e o `cena.blend` fica salvo para quem quiser abrir no Blender.
- **Tudo marcado por palavra.** Câmera, desmontagem, quique de cada parte, efeito sonoro, rótulo e legenda vêm do
  `tempos.json` da narração, nunca de segundo fixo. Trocou a voz, o vídeo se reajusta.
- **Rótulo ligado ao 3D.** O nome de cada parte entra na palavra dela, preso ao ponto da peça por um traço, e
  segue a peça quando a câmera anda.
- **Replay.** O último plano repete o primeiro, para o vídeo emendar quando a rede repete.
- **CTA da rede no fim,** com o gancho do próximo vídeo no lugar de "parte 2" (`comandos/publicar.md`). As 3
  versões saem numa passada só.
- **Velocidade:** EEVEE na placa de vídeo, sombreamento chapado (toon) e contorno, sem sombra nem raytracing. Gere os
  quadros-marco antes do render longo. Sem placa nenhuma (servidor sem GPU, celular), use o motor Three.js
  (`kit/explicativo3d/web/`), que desenha pelo processador.
- O 3D vale quando o plano pede objeto em corte, vista explodida, giro de câmera ou costas e lado. O 2D continua mais
  rápido para close de rosto e fala.
