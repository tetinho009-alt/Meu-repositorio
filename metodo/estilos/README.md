<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Catálogo de estilos

Cada estilo tem uma ficha com o que é, um exemplo real, a duração, a estrutura do roteiro, como o kit faz, o que
precisa nos dois caminhos (grátis e recomendado) e o nível de dificuldade. Os dois caminhos estão em
`metodo/caminhos.md`, e as regras que valem para todos, em `metodo/licoes.md`.

Carregue a ficha **só do estilo escolhido**, na etapa de roteiro. As durações abaixo são as mesmas que a trava
antes do render confere (`kit/qa/antes_do_render.py`).

| Estilo | Ficha | Duração ideal | Motor do kit | Dificuldade | Grátis de ponta a ponta? |
|---|---|---|---|---|---|
| Série animada 2D com voto (comédia) | `metodo/estilos/serie-2d-voto.md` | 1:45 a 2:20 | rig 2D (`kit/maquina/`) | média | sim |
| Terror e mistério com voto | `metodo/estilos/terror-voto.md` | 1:45 a 2:15 | rig 2D + estilo desenhado | média | sim |
| Série em "você" (POV) | `metodo/estilos/pov.md` | 1:50 a 2:20 | rig 2D | média | sim |
| Explicativo 3D | `metodo/estilos/explicativo-3d.md` | 40 a 65 s | Blender ou Three.js (`kit/explicativo3d/`) | alta | sim (Blender com placa de vídeo; Three.js sem placa e na nuvem) |
| Novela anime (romance e drama) | `metodo/estilos/novela-anime.md` | 2:00 a 2:30 | cartelas com imagens geradas | alta | não: as imagens pedem IA de imagem paga |
| Novela de frutas (besteirol com IA de vídeo) | `metodo/estilos/novela-frutas.md` | 10 a 35 s | IA de vídeo (`kit/video_ia.py`) | média | não: cada cena é paga na conta de IA de vídeo |
| Motion graphics e tipografia cinética | `metodo/estilos/tipografia.md` | 20 a 40 s | cartelas (`kit/cartelas/`) | baixa | sim |
| Faceless narrado com imagens | `metodo/estilos/faceless.md` | 45 a 80 s | cartelas | baixa | sim, com fotos próprias ou de banco livre |
| Curiosidades e top 5 | `metodo/estilos/top5.md` | 35 a 55 s | cartelas | baixa | sim |
| História real narrada | `metodo/estilos/historia-real.md` | 60 a 110 s | cartelas | média | sim |
| Antes e depois | `metodo/estilos/antes-depois.md` | 20 a 40 s | cartelas | baixa | sim, com as suas fotos |
| Bastidores e tela | `metodo/estilos/bastidores.md` | 30 a 55 s | cartelas com prints | baixa | sim |
| Quiz e escolha | `metodo/estilos/quiz.md` | 30 a 55 s | cartelas | baixa | sim |

## Visuais extras por código

Além dos estilos acima, o kit desenha 14 visuais por código, sem IA de imagem e sem crédito:
- low poly e console antigo dos anos 2000;
- POV realista de apocalipse;
- stickman e sticker;
- pixel art 16 bits e TV de tubo;
- voxel e diorama isométrico;
- backrooms em VHS;
- mangá e anime cel;
- recorte de papel e massinha.

Cada um sai em 10 s para testar o visual antes de virar série, ou para servir de abertura e gancho. Como rodar e
adaptar: `kit/estilos_visuais/README.md`.

## Como escolher (a pergunta que a IA faz)

Pergunte o que o canal quer que a pessoa sinta no fim, com duas sugestões vindas do nicho dele:

- **"Quero que ela volte amanhã"** → série com voto (comédia, terror, POV ou novela). Dá mais trabalho por vídeo e é
  o que mais segura seguidor, porque cada parte deixa uma pergunta aberta.
- **"Quero que ela aprenda e salve"** → explicativo 3D, top 5, história real ou faceless.
- **"Quero que ela comente e mande pra alguém"** → quiz, antes e depois.
- **"Quero mostrar o meu trabalho"** → bastidores e tela.

Para começar rápido, sem nada instalado além do kit: **top 5**, **quiz** ou **tipografia**. Saem num episódio de
poucos minutos de render e testam a voz, a legenda e o pacote das redes (`comandos/modo-rapido.md`).

## O que todo estilo tem em comum

1. **Gancho em até 3 segundos**, com texto grande na tela e a voz dizendo algo que não devia acontecer, ou uma
   promessa clara. Quem não entende o vídeo em 3 s pula, e quem chega de fora não sabe o que é "ontem".
2. **Uma frase, uma imagem.** Imagem nova a cada 2 a 4 s; nada parado.
3. **Fim com pergunta aberta ou com o voto**, nunca com "comenta X" sem ligação com a história.
4. **Pacote das redes escolhidas** com o CTA de cada rede (`comandos/publicar.md`).

## Ver antes de escolher

Cada estilo tem um exemplo de 10 s feito no caminho grátis em `exemplos/estilos/<estilo>/exemplo.mp4`, e o painel mostra todos na tela Estilos.
A identidade de um canal inteiro já pronta (logo, foto de perfil, banner, destaques, bio e os 3 primeiros posts) está
em `exemplos/canal-pronto/`.
