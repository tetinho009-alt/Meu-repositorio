<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# 05 · Visual: dois caminhos

Carregue para criar personagens, cenários e planos. Identidade visual e prompts de imagem estão em
`metodo/identidade-visual-prompts.md`; código em `kit/README.md`.

| Caminho | Pilha | Força | Limite |
|---|---|---|---|
| A. Animação por código | Estúdio (Criador com HyperFrames) | Mesmo boneco do EP1 ao EP20, custo por vídeo zero | Exige o motor pronto (o `kit/`) |
| B. Vídeo generativo | Qualquer, como complemento | Planos impossíveis de desenhar (céu, criatura ao longe) | Caro e inconsistente em personagem |

A regra que vale nos dois: **continuidade**. Série no ar usa os personagens do EP1 exatamente iguais. Personagem que
muda de rosto entre episódios faz o público achar que é outra série.

## A. Animação por código (o diferencial)

A IA escreve o código que desenha cada quadro. Não é motor 3D: é desenho 2D com câmera em perspectiva, o que dá cara
de animação cara com custo de código.

### A1. Boneco 2D com rig

1. **Partes separadas:** cada personagem é um conjunto de imagens transparentes, uma por parte: cabeça, cabelo (e
   cabelo de trás), tronco, quadril, braço e antebraço de cada lado, pernas, pés, olhos, íris, pálpebras,
   sobrancelhas e uma boca por visema (A, E, I, O, U, M, F, repouso).
2. **Rig:** uma árvore que diz quem é pai de quem e onde fica o pivô de cada parte (o antebraço gira no cotovelo e
   segue o braço; o braço segue o tronco). Mexeu o tronco, tudo que é do corpo vai junto.
3. **Pose:** para cada parte, `{rot, dx, dy, sx, sy}`. Mais chaves globais: visema da boca, piscar, olhar (x, y),
   inclinação do corpo, sorriso.
4. **Animação:** interpole poses-chave com curva de aceleração (ease), nunca linear.
5. **Personagem = configuração sobre um molde.** Um molde base desenha todas as partes; cada personagem é uma
   configuração de poucas linhas (pele, cabelo e estilo, roupa e tipo, calçado, íris, acessório). Isso garante o
   mesmo traço no elenco inteiro e o mesmo boneco em todo episódio.
6. **Mão que segura objeto vem do rig:** calcule a posição e o ângulo da palma a partir da pose e prenda o objeto
   ali; redesenhe o antebraço por cima do objeto. Objeto posto "perto da mão" flutua, e isso já derrubou episódio.
7. **Vida:** respiração (escala do tronco de 1 a 2%), piscar irregular a cada 2 a 5 s, micro-movimento. Boneco
   parado parece imagem travada.
8. **Boca:** visema só durante a fala, sincronizado aos tempos das palavras; fecha entre frases.
9. **Ameaça:** o mesmo boneco com olhos totalmente negros, sorriso largo demais, cabeça torta, postura rígida, sem
   piscar. Reaproveitar o elenco mantém o traço e assusta mais, porque é alguém que o público já viu.

Limitação conhecida: boneco feito só de frente. Multidão sempre vem na direção da câmera, nunca de costas.

### A2. Cenário em perspectiva por código

1. **Câmera pinhole:** um ponto no mundo `(X, Y, Z)` vai para a tela em `x = f·X/Z + cx`, `y = f·Y/Z + cy`. Mover a
   câmera (descer sobre o bairro, avançar no corredor) é mudar a posição dela e reprojetar.
2. **Desenho do fundo para a frente:** ordene **todo** item (muro, caixa d'água, poste, gente) pela profundidade e
   desenhe do mais longe para o mais perto. Item fora da ordem aparece atrás do muro errado; esse erro já derrubou
   episódio.
3. **Bonecos no cenário:** escala proporcional a `f/Z`; pé no chão com sombra de contato; quem está atrás de mureta
   é recortado por ela.
4. **Escala:** adulto ≈ 0,8 da altura da porta, criança ≈ 0,55; objeto na escala da mão.
5. **Luz motivada:** cena quase toda no escuro, iluminada por uma fonte que existe (fresta de porta, abajur, tela de
   celular, poste). O personagem escurece do lado oposto à luz e ganha borda acesa do lado da fonte; nunca fica mais
   claro que a fonte.
6. **Pós em todo quadro:** correção de cor leve, vinheta, grão de filme.
7. **Padrão de plano:** aberto no cenário em perspectiva para geografia; close 2D com o fundo desfocado para emoção.
8. **Direção de arte real:** lugar reconhecível e cheio (caixa d'água, varal, fios, antena). Fundo vazio com dois
   objetos parece protótipo.
9. **Telas de celular desenhadas pelo código**, sem copiar a interface de app real.

### A3. Render

O código desenha cada quadro (biblioteca 2D como Skia), envia por pipe ao ffmpeg e o ffmpeg codifica. Com placa
NVIDIA, desenho e codificação vão para a GPU; sem ela, CPU, mais lento. No modo nuvem a nuvem não tem GPU: o kit
usa a CPU sozinho.

Antes do render completo, gere a **folha de quadros-marco** (um quadro por plano) e peça aprovação. Corrigir na folha
custa segundos; corrigir no vídeo custa um render.

Alternativas para quem não usa o kit:
- **HyperFrames** (HTML/CSS/JS para MP4, Apache-2.0, roda na CPU): a IA escreve HTML muito bem. Bom para Zero e
  Criador.
- **Remotion** (React): grátis para pessoa física e empresa de até 3 pessoas; acima disso, licença paga.

### A4. Extra opcional: 3D com Blender

**Opcional. Nenhuma etapa obrigatória depende disto.** O padrão continua sendo o boneco 2D com rig e o cenário em
perspectiva por código, que roda até sem GPU. Considere o Blender só depois de dominar o 2D.

Quando vale: planos que o boneco 2D de frente não faz, como personagem de costas, de lado ou câmera girando em volta
dele.

Como funciona:
1. **Modelo 3D a partir da arte 2D do boneco**, por ferramenta de imagem para 3D:

   | Ferramenta | Licença comercial |
   |---|---|
   | Higgsfield | Só nos planos pagos (verificar o plano) |
   | Tripo | Verificar |
   | Meshy | Verificar |
   | Hunyuan3D | Verificar (licença própria com restrições por região e escala) |

   Leia os termos antes de usar o modelo num vídeo vendido ou monetizado.
2. **Esqueleto automático** (auto-rig) no modelo. Pode falhar em corpo chibi de cabeça grande; conte com ajuste
   manual de pesos.
3. **Render por linha de comando:** `blender -b cena.blend -P script.py`, com Cycles ou EEVEE na GPU. O script
   posiciona câmera e poses e exporta os quadros, que entram na mesma montagem (`metodo/ritmo-e-montagem.md`).
4. **Continuidade:** o modelo 3D precisa bater com o boneco 2D (cores, proporção, cabelo, roupa). Se não bater, o
   público vê dois personagens.

Custo real: dias de ajuste até o 3D ficar no padrão do 2D. No modo nuvem e em PC sem GPU, o Blender roda na CPU,
mas fica bem lento: planeje só planos curtos ou deixe para o computador com placa.

## B. Vídeo generativo: só plano de inserção

Use para 2 a 5 s que o código não desenha bem: céu se abrindo, relógio em close fotográfico, corredor, criatura ao
longe na neblina.

| Ferramenta | Observação |
|---|---|
| Higgsfield (agrega vários modelos) | Plano grátis sem direito comercial |
| Kling 3.0 | Boa consistência por referência; créditos expiram no mês |
| Veo 3.1 (Gemini API) | ~US$ 0,10 a 0,40 por segundo; 80 s no Fast ≈ US$ 8 sem nenhuma regravação |
| Runway, Hailuo | Planos pagos; grátis com marca d'água ou sem uso comercial |

Sora foi descontinuado em 2026: não use.

Por que não fazer a série inteira assim: 13 vídeos por mês com regravação passam de R$ 1.400 só em geração e o
personagem não fica igual entre episódios.

Regras:
1. Nunca para o protagonista falando. Personagem gerado muda de rosto entre planos.
2. Plano pago com direito comercial; nada de marca d'água.
3. Nada que lembre personagem, franquia ou rosto de terceiros no prompt; há processos de estúdios contra geradores.
4. Plano **realista** gerado por IA exige rótulo de IA em todas as redes (`metodo/seguranca.md`).
5. Gradue o plano gerado para a paleta da série (escuro, vinheta, grão) para não destoar.

## Portão do visual

- [ ] Personagens iguais aos do EP1 (rosto, cabelo, roupa, cores).
- [ ] Folha de quadros-marco aprovada.
- [ ] Nenhum objeto flutuando ou atrás do muro errado.
- [ ] Nada gráfico.
