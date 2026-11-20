<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Novo vídeo

Antes de começar, leia `canal/canal.md`, `canal/identidade.md` e `canal/aprendizados.md`. O estilo, o assunto e o
formato estudado que vieram no pedido valem à risca.

### Pedido sem estilo

Quem usa muitas vezes manda só o assunto, sem marcar estilo. Isso não é erro dele e não trava o vídeo: **não
pergunte e não pare**. Escolha pela tabela abaixo, diga em uma linha qual escolheu e por quê ("Fiz como explicativo
3D, porque é uma pergunta de como funciona. Se preferir outro estilo, é só falar.") e siga para o roteiro.

| O assunto é... | Estilo |
|---|---|
| uma pergunta de como ou por que algo funciona (casa, corpo, natureza, ciência, objeto): "um raio entra na minha casa?", "por que o pão cresce" | explicativo 3D (Formato 2), com o objeto do assunto virando personagem (`mascote()`) |
| uma lista, curiosidades, "coisas que..." | top 5 |
| um caso que aconteceu, uma história, uma pessoa ou um lugar real | história real |
| um teste de conhecimento, "você sabe..." | quiz |
| uma transformação, antes e depois | antes e depois |
| ficção com personagem, escolha ou voto ("e se...", "o que ele faz?") | série com voto, só se o pedido falar de ficção, série ou voto |
| não deu para saber | o estilo padrão do canal, se for de cartelas; senão, top 5 |

Com formato estudado e sem estilo: olhe a folha de quadros do estudo. Se a referência é animação com personagem,
fique com o explicativo 3D, se o assunto for uma pergunta, ou com um estilo de cartelas, que já vem com o apresentador.
Copie a estrutura e o ritmo do molde em qualquer estilo. Nunca escolha a série só por causa do formato estudado:
ela depende de desenhar cada cena à mão.

Quando o usuário marca um estilo que não combina com o assunto (uma série para explicar um telhado), faça o estilo
marcado e diga em uma linha qual combinaria mais, sem parar o vídeo.

Abra a ficha do
estilo (`metodo/estilos/`) na etapa de roteiro e siga o caminho do canal (`caminho:` em `canal/canal.md`,
`metodo/caminhos.md`). As lições de `metodo/licoes.md` valem em todos.

## O caminho do vídeo (o padrão)

O usuário manda o assunto (com ou sem estilo) e recebe o vídeo pronto. Você se vira com o resto:

1. **Personagem primeiro.** Rode `python -c "from personagem_novo import personagem_do_canal as p; print(p())"` a
   partir de `kit/`. Se der `None`, o canal ainda não tem personagem: crie um agora, antes do roteiro, com
   `python personagem_novo.py <nome> --descricao "..." --cores '{...}' [--acessorios ...]`, a partir do assunto e
   do jeito do canal (`canal/identidade.md`). Mostre a `folha.png` e pergunte, com dois botões ("Gostei, segue" e
   "Muda o personagem"). É a única pergunta antes do vídeo. Anote o nome em `canal/identidade.md`. Daí em diante, as
   cartelas e a série usam esse personagem sozinhas; no explicativo 3D, o objeto do assunto vira o personagem
   (`mascote()`).
2. **Estilo:** o marcado; sem estilo, a tabela "Pedido sem estilo" abaixo.
3. **Roteiro, voz, imagem e render seguidos**, mostrando cada coisa no chat enquanto anda, sem esperar aprovação,
   exceto o "pode" antes de gasto pago (voz da ElevenLabs, IA de vídeo). Os portões das tabelas de formato valem só
   quando o usuário pedir para aprovar cada etapa.
4. **Conferência antes de entregar (obrigatória).** O pacote das redes e o 3D terminam com a linha `CONFERENCIA
   <arquivo>`. Abra essa folha de 8 quadros e responda às 3 perguntas que vêm embaixo (tem personagem? a imagem muda?
   dá para entender sem som?). Se alguma for não, não entregue: diga em uma linha o que faltou, corrija e rode de
   novo. Sem a linha (outro caminho de render), rode `python qa/conferir_entrega.py <video>`.
5. **Entrega:** o vídeo, a folha de conferência e onde está o pacote, em 3 linhas.

**Todo vídeo tem personagem e imagem que se mexe.** Fundo parado com texto e legenda por cima não é vídeo, é o
erro que mais devolve compra. Se o usuário não deu personagem, você cria um, do jeito de cada formato:

- cartelas: o apresentador já vem ligado (um boneco de `personagens/` que fala junto); escolha o que combina com o
  assunto;
- série: `Boneco("lola")` ou `Boneco("nico")` de `maquina/rig.py` em `cena()`, ou um novo com `construir_boneco.py`;
- explicativo 3D: `mascote()` (o objeto do assunto vira personagem) ou os bichos prontos.

Com formato estudado, abra o `molde.md` e a folha de quadros (`quadros.jpg`, na pasta do estudo) antes do roteiro e
faça o mesmo tipo de visual da referência. Se o estudo não tiver a folha, pergunte ao usuário como é o visual. As
travas do render param o vídeo sem cenário ou sem personagem: desenhe o que falta, nunca contorne.

| Estilo | Siga |
|---|---|
| série com voto (comédia, terror, POV, novela) | Formato 1, abaixo |
| explicativo 3D | Formato 2, abaixo |
| tipografia, top 5, quiz, faceless, história real, antes e depois, bastidores | Formato 3 (cartelas), abaixo |

Cada etapa abaixo tem um **portão**: mostre o resultado e só siga com o "aprovado" do usuário. Carregue o arquivo do
método **na etapa em que ele é usado**, não antes.

## Formato 1 · Episódio de série com votação

Se é a Parte 1 de uma série nova, rode antes `comandos/nova-serie.md`. Se é a Parte 2 em diante, a parte nasce do
voto: apure a anterior (`comandos/apurar-votos.md`), aplique o desfecho que venceu e a marca na bíblia da série e
escreva a partir dele (`metodo/formula-roteiro.md`, seção 7).

**Série POV ("você"):** carregue também `metodo/formato-pov.md` no roteiro, na voz e no visual. Na Parte 1, antes da
voz, entra o portão das 3 aberturas; na etapa visual, as 4 a 6 prévias vêm antes da folha completa.

| # | Etapa | Carregue | Saída | Portão |
|---|---|---|---|---|
| 1 | Roteiro | `metodo/formula-roteiro.md`, `modelos/roteiro-episodio.md`, `exemplos/episodio-comentado.md` | `roteiro.md` + `narrador.txt` (+ `falas.json` se personagem fala), com o gancho no quadro 0 e a pergunta aberta | **Roteiro aprovado** |
| 2 | Voz | `metodo/voz.md` | Narração e falas, uma tomada por fala, com o tempo de cada palavra (`kit/falas.py`) | **Prévia ouvida de fone** |
| 3 | Som | `metodo/som.md` | Mix estéreo 48 kHz a −14 LUFS + licença de cada som | Licenças anotadas |
| 4 | Visual | `metodo/visual.md`, `metodo/identidade-visual-prompts.md` | Personagens (2D ou 3D), cenários, planos | Folha de quadros-marco aprovada (o quadro 0 entre eles) |
| 5 | Montagem | `metodo/ritmo-e-montagem.md` | Vídeo 1080x1920 + grade de conferência; na Parte 2+, a apuração emendada depois do gancho | **Prévia aprovada no celular** |
| 6 | Checklist | `metodo/checklist.md` | Checklist preenchido | Zero item reprovado |
| 7 | Pacote das redes escolhidas | `comandos/publicar.md` | Uma pasta por rede escolhida (IG / TIKTOK / YOUTUBE / KWAI), cada uma com vídeo, capa e legenda da rede | **Confirmação antes de publicar** |

A abertura da Parte 2 em diante mostra o placar **real** logo depois do gancho, nunca antes
(`kit/apuracao_video.py`). Nunca invente número.

### Vozes: uma tomada por fala

Narrador e personagens com voz própria vão num `falas.json` (modelo em `kit/exemplo/falas_elevenlabs.json`): uma
linha por fala, com a voz de quem fala e as tags de direção do eleven_v3 (`[whispers]`, `[nervous]`). Rode a partir
da pasta `kit/`:

```
python falas.py <episodio>/falas.json --seco          # confere vozes e textos sem gastar crédito
python falas.py <episodio>/falas.json                 # grava só as que faltam, uma por vez, com tempo de palavra
python falas.py <episodio>/falas.json --juntar <episodio>/audio   # narrador.mp3 + tempos.json para a trilha
```

Refazer uma fala = apagar só o mp3 dela e rodar de novo. O ElevenLabs devolve o tempo de cada palavra; Kokoro e
Piper passam pelo Whisper sozinhos. Antes de gravar, mostre a estimativa de crédito (cerca de 1 crédito por
caractere) e, depois, o custo real.

### Personagem em 3D (opcional)

O 2D com rig é a base. Quando o plano pede costas, perfil, giro de câmera ou profundidade de verdade, o mesmo
personagem sai em 3D, renderizado na GPU pelo Blender (o mesmo do explicativo 3D), falando pelo tempo de cada palavra:

```
python boneco3d/rodar.py lola --previa       # monta o boneco 3D a partir do 2D e salva uma imagem (10 s)
python boneco3d/rodar.py lola --exemplo      # 8 s da Lola falando a narração de exemplo (~2 min numa RTX 4060)
python boneco3d/rodar.py <nome> --clipe fala --tempos <tempos.json> --audio <voz.mp3>
```

Hoje o 3D cobre personagem de cabelo `longo` e roupa `moletom`; os outros estilos ficam no 2D, e o
gerador avisa. Render longo: rode em segundo plano e avise o tempo esperado (cerca de 14 s de render por segundo de
vídeo numa RTX 4060).

### Chamada falada do comentário fixado

Se `cta.chamada_fixado` estiver preenchida, o narrador diz essa frase uma vez, num ponto natural logo depois do
gancho, nunca em cima de uma virada. Só voz e legenda falada, nada novo desenhado na tela. A mesma frase vai numa
linha da legenda do post de cada rede. Ela só aponta para o fixado: nada de "comenta X".

### Vídeo longo 16:9 (opcional)

Com 3 partes decididas, ofereça uma vez o filme horizontal para o YouTube (`metodo/video-longo.md`). O padrão
continua sendo o vertical.

## Formato 2 · Explicativo 3D

| # | Etapa | Carregue | Saída | Portão |
|---|---|---|---|---|
| 1 | Pesquisa | `metodo/formato-explicativo.md` | O fato explicado em 3 a 5 passos, **com a fonte de cada um** | Fontes conferidas |
| 2 | Roteiro | `metodo/formato-explicativo.md`, `metodo/formula-roteiro.md` | Pergunta-título, o "jeito errado" do boneco, os passos, 2 ou 3 micro-gags com o segundo de cada uma, a revelação e o gancho da próxima parte | **Roteiro aprovado** |
| 3 | Voz e som | `metodo/voz.md`, `metodo/som.md` | Narração com tempo de palavra + mix | **Prévia ouvida de fone** |
| 4 | Cena 3D | `metodo/formato-explicativo.md` (seção 3D), `metodo/visual.md`, `kit/explicativo3d/exemplo/cena.py` (Blender) ou `kit/explicativo3d/web/exemplo/cena.js` (Three.js) | Objeto em corte ou vista explodida, partes com olhos, câmera por passo | Quadros-marco aprovados (`--stills`) |
| 5 | Montagem | `metodo/ritmo-e-montagem.md` | Render (Blender ou Three.js, seção "Motor 3D") + composição: vídeo 1080x1920 + grade | **Prévia aprovada no celular** |
| 6 | Checklist | `metodo/checklist.md` | Checklist preenchido (explicação conferida com a fonte) | Zero item reprovado |
| 7 | Pacote das redes escolhidas | `comandos/publicar.md` | Uma pasta por rede escolhida (a composição já sai com o CTA de cada rede) | **Confirmação antes de publicar** |

Modelos 3D: só de licença CC0 (Quaternius, Kenney), para o vídeo não precisar de crédito. Os da licença CC-BY exigem
o crédito em cada post, então evite. Anote todo modelo novo em `kit/explicativo3d/modelos/FONTES.md`. Explicação
errada vira comentário corrigindo: na dúvida, não afirme.

### Motor 3D (`kit/explicativo3d/`): Blender ou Three.js

O Explicativo 3D tem **dois motores**, com o mesmo roteiro, os mesmos rótulos e a mesma composição:

| Motor | Precisa de | Visual | Onde |
|---|---|---|---|
| **Blender** | Blender 5.2 LTS e placa de vídeo (a integrada serve) | a referência | `kit/explicativo3d/INSTALAR.md`, exemplo em `kit/explicativo3d/exemplo/` |
| **Three.js** | só o processador e o navegador sem janela do Playwright | quase igual (bordas um pouco mais duras) | `kit/explicativo3d/web/LEIA-ME.md`, exemplo em `kit/explicativo3d/web/exemplo/` |

**Escolha do motor, antes da cena 3D (passo 4):**
1. Leia `render.motor_3d` nas preferências do canal. `blender` ou `threejs`: use esse, sem perguntar.
2. `auto` (o padrão): rode `python explicativo3d/ambiente3d.py --teste`.
   - Passou (tem Blender e placa): pergunte uma vez, "Faço no Blender (visual de referência, usa a placa) ou no
     Three.js (quase igual, só processador)?", e grave a resposta em `render.motor_3d`.
   - Falhou, ou a sessão é na nuvem (celular): use o Three.js e diga em uma linha o porquê ("aqui não tem placa de
     vídeo, então vai no Three.js"). Na nuvem o Blender não abre.
3. Three.js pela primeira vez: confira com `python explicativo3d/web/render.py --teste` e, se faltar o navegador,
   instale como diz o `kit/explicativo3d/web/LEIA-ME.md`.

Tempo medido do exemplo de 14 s (60 fps): Blender na RTX 4060, uns 5 min no total; Three.js só no processador, 5 min
33 s num processador de 16 núcleos e uns 8 a 11 min estimados numa máquina de 2 a 4 núcleos, como a da nuvem.

**Blender.** Instalação, tempo de render medido e conferência: `kit/explicativo3d/INSTALAR.md`. Antes do primeiro
vídeo, rode o exemplo (caravela, 14 s) a partir da pasta `kit/`:

```
python explicativo3d/ambiente3d.py --teste          # acha o Blender e mostra a placa que o EEVEE usou
python explicativo3d/exemplo/rodar.py --stills      # 5 quadros-marco, cerca de 1 min
python explicativo3d/exemplo/rodar.py               # o exemplo inteiro: 3 vídeos, capa e grade
python explicativo3d/exemplo/rodar.py --voz elevenlabs   # o mesmo exemplo com a voz do usuário
```

Para um episódio novo, copie `kit/explicativo3d/exemplo/` para uma pasta nova e troque, nesta ordem:
`narrador.txt` (o roteiro aprovado), `episodio.json` (gancho, capa, destaques, rótulos e o CTA de cada rede com o
gancho do próximo vídeo), `cena.py` (o objeto, as partes e os marcos de câmera por palavra) e `trilha.py` (os efeitos
nos marcos). Tudo é marcado por palavra da narração, nunca por segundo. Rode com `--stills` até os quadros-marco
serem aprovados, e só então sem `--stills`.

**O exemplo é do fundo do mar; o seu vídeo não.** Copie o exemplo só pela parte técnica (voz, tempos, câmera,
composição). Cenário, objetos e personagens são novos, do assunto do pedido:

1. **Cenário do assunto.** Raio em casa = sala em corte e tempestade lá fora; geladeira = cozinha; vulcão = montanha
   e céu. Peças prontas: `bloco_comodo`/`blocoComodo` (cômodo em corte com janela), `chao`, `casinha`, `nuvem`, e
   para o resto `caixa`, `esfera`, `tubo` e `blob`. O bloco do oceano, o coral, a alga e os peixes são só para
   assunto de mar.
2. **Fundo do assunto.** Campo `"fundo"` do `episodio.json`: `casa`, `tempestade`, `ceu`, `noite`, `cidade`,
   `espaco`, `laboratorio`, `natureza`, `neutro` ou `mar` (com `"fundo_cores": ["#centro", "#borda"]` para outras
   cores).
3. **Sempre um personagem.** Se o assunto não tem boneco pronto, crie: `mascote(...)` transforma qualquer coisa em
   personagem com olhos, boca, braços e pernas (formas `raio`, `gota`, `bola`, `caixa`); ou ponha `olhos(...)` numa
   peça. O personagem atua em cada marco da fala (cai, leva susto, aponta, foge).
4. **Siga o pedido do usuário à risca**: o assunto, o estilo e o formato estudado que vieram no pedido. Nada do
   exemplo (caravela, oceano, rótulos do exemplo) entra num vídeo que não é sobre isso.

Exemplo pronto fora do mar (raio dentro de casa, com os dois personagens): `kit/explicativo3d/web/exemplo_casa/`.

A trava `explicativo3d/motor/trava_cena.py` roda sozinha antes do render e para com ERRO se faltar o fundo, se a
cena estiver no mar sem o assunto ser de mar, se não houver personagem ou se sobrar a caravela. Não contorne:
corrija a cena. E mostre a folha dos quadros-marco (`folha_stills.jpg`) ao usuário antes do render inteiro; com
cena vazia ou sem personagem, refaça antes de pedir o "aprovado".

**Three.js.** Os mesmos comandos, na pasta `explicativo3d/web/` (`python explicativo3d/web/exemplo/rodar.py
--stills`, depois sem `--stills`). Para um episódio novo, copie `kit/explicativo3d/web/exemplo/`: a cena fica em
`cena.js` em vez de `cena.py`, e o resto (`narrador.txt`, `episodio.json`, `trilha.py`) é igual ao do Blender.

## Formato 3 · Cartelas (sem personagem desenhado)

| # | Etapa | Carregue | Saída | Portão |
|---|---|---|---|---|
| 1 | Pesquisa (estilos com fato) | a ficha do estilo | cada fato com fonte | Fontes conferidas |
| 2 | Roteiro | a ficha do estilo, `kit/cartelas/LEIA-ME.md`, o modelo em `kit/cartelas/modelos/` | `episodios/<nome>/roteiro.json` (+ imagens, se o estilo usa), mostrado como lista de blocos | **Roteiro aprovado** |
| 3 | Visual sem voz | — | `python cartelas/rodar.py <pasta> --stills` (um quadro por bloco) | Folha aprovada |
| 4 | Voz + vídeo + pacote | `metodo/voz.md` | `python cartelas/rodar.py <pasta>` (em segundo plano); na ElevenLabs, antes `--seco` e o "pode" | **Prévia aprovada no celular** |
| 5 | Checklist | `metodo/checklist.md` | Checklist preenchido | Zero item reprovado |

O pacote das redes escolhidas já sai no passo 4 (`trabalho/entregas/<nome>/`). Se uma trava reprovar, leia a linha `ERRO`,
corrija o roteiro e rode de novo: a voz já gravada é reaproveitada.

## Modo agente (você roda comandos)

Os comandos de voz, alinhamento, mix, render, grade e capa estão em `kit/README.md`. Leia esse arquivo antes da
primeira execução e use só os comandos que estão lá. Sem placa NVIDIA o render cai para a CPU sozinho: gere antes
só os quadros-marco (`--stills`) para não esperar à toa. No Explicativo 3D, escolha o motor (seção "Motor 3D")
e use os comandos do `kit/explicativo3d/INSTALAR.md` (Blender) ou do `kit/explicativo3d/web/LEIA-ME.md` (Three.js);
o render é longo nos dois, então rode em segundo plano e avise o usuário do tempo esperado antes de começar.

## Folha de cenas numerada

Na etapa visual, a folha mostra **um quadro por frase do roteiro, numerado** na ordem da narração, para o usuário
pedir troca pelo número ("a 9 ficou estranha, põe o carro rodando na poça"). Antes de mostrar, confira você mesmo
os quadros (personagem fora de cena, texto fora da zona segura, objeto cortado) e diga em uma linha o que é de
propósito ("nas cenas 5 e 6 o personagem não aparece: é o close no pneu").

## Render em segundo plano

O render final roda em segundo plano. Avise quanto tempo leva e, enquanto isso, escreva o texto de postar: **dois
títulos** (um com as palavras que as pessoas digitam na busca, outro que dá curiosidade), a descrição, as hashtags,
o comentário fixado e onde escolher a capa em cada rede. Quando o vídeo sair, confira a duração e alguns quadros
antes de entregar.

## Depois da entrega

1. Registre o vídeo em `canal/historico.md`.
2. **Peça a nota**, numa mensagem só: uma nota de 1 a 5, a cena que mais gostou e a que ficou estranha (pelo número
   da folha) e o que ele mudaria. Grave a nota e as cenas no histórico; o que ele mudaria vira entrada em
   `canal/aprendizados.md` e vale a partir do próximo vídeo. Todo ajuste pedido no caminho também vira entrada.
3. **Combine a volta com os números.** "Postou? Volta em 2 ou 3 dias e me conta como foi: views, curtidas,
   comentários, ou manda o print." Se as redes estão conectadas, leia você mesmo (`comandos/conectar-redes.md`) e
   mostre. Com os números, anote em `canal/historico.md` o que foi melhor que a média e o que foi pior, e escreva a
   regra em `canal/aprendizados.md` quando um padrão se repetir em 3 vídeos ou mais (`metodo/metricas.md`). Vídeo
   que viralizou vira molde: o próximo reaproveita a estrutura dele num assunto novo.
4. Pergunte uma coisa só: "Gero o pacote das redes?" (ou, se já gerou: "Quer agendar a Parte 2?"), com a próxima
   ideia da pauta como sugestão.
