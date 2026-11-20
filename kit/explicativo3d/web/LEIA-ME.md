<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Explicativo 3D sem placa de vídeo (Three.js)

Este é o segundo caminho de render do Explicativo 3D. Ele monta a mesma cena num navegador sem janela (Chromium) com
Three.js e grava os mesmos quadros que o Blender grava. O resto do kit não muda: voz, trilha, masterização,
composição com legenda e rótulos, CTA de cada rede, capa e grade de QA.

## Quando usar cada um

| Situação | Use |
|---|---|
| Computador com placa de vídeo e Blender instalado | **Blender** (`explicativo3d/exemplo/rodar.py`). É o visual de referência. |
| Sessão do Claude Code na nuvem (Linux, sem placa) | **Three.js** (`explicativo3d/web/exemplo/rodar.py`). O Blender não abre lá. |
| Computador sem Blender, ou sem placa | **Three.js**. Roda em qualquer CPU. |

O Three.js imita o visual do Blender: o mesmo sombreado toon de 3 tons, o mesmo contorno de nanquim, a mesma paleta,
a mesma câmera e os mesmos rótulos. A diferença está nos detalhes (ver "Diferenças para o Blender").

## Instalar

Pré-requisito: o kit principal instalado (`kit/INSTALAR.md`). Todos os comandos rodam **a partir da pasta `kit/`**.

### Windows e Mac

```
python -m pip install playwright
python -m playwright install --only-shell chromium
```

O segundo comando baixa, uma vez só, o Chromium sem janela que o kit usa (cerca de 290 MB depois de instalado; sem
o `--only-shell` ele baixa também o Chromium completo, mais 450 MB que o kit não usa). Nada é baixado na hora do
render: o Three.js já vem dentro do kit, em `web/vendor/`.

### Linux da nuvem (Claude Code na nuvem)

```
python -m pip install playwright
python -m playwright install --only-shell --with-deps chromium
```

O `--with-deps` instala as bibliotecas do sistema que o Chromium pede (precisa de `sudo` ou de rodar como root).

Se a rede da nuvem bloquear o download do Playwright, use o Chromium do sistema:

```
sudo apt-get install -y chromium
python explicativo3d/web/exemplo/rodar.py --chromium /usr/bin/chromium
```

Também vale a variável `X3D_CHROMIUM=/usr/bin/chromium`. Sem nada disso, o script procura sozinho um Chromium,
Chrome ou Edge instalado quando falta o navegador do Playwright.

## Conferir se deu certo

```
python explicativo3d/web/render.py --teste
```

Deu certo quando aparece `TESTE_OK` e a linha `WebGL: ... SwiftShader ...`. SwiftShader é o desenho 3D feito pela
CPU, o mesmo da nuvem.

## Rodar

```
python explicativo3d/web/exemplo/rodar.py --stills    # 5 quadros-marco para conferir
python explicativo3d/web/exemplo/rodar.py             # o exemplo inteiro
```

Sai em `trabalho/explicativo3d_caravela_web/`, com os mesmos arquivos do caminho do Blender: `IG/01_video.mp4`,
`TIKTOK/01_video.mp4`, `YOUTUBE/01_video.mp4`, a capa de cada rede, `qa/qa_grade_0.jpg` e `render.json`.

Outras opções:

- `--leve`: metade da resolução, para aprovar movimento e tempo. O vídeo final sai sem `--leve`.
- `--placa gpu`: usa a placa de vídeo, se houver. O padrão é a CPU, igual à nuvem.
- `--chromium CAMINHO`: usa um Chromium do sistema.
- `--so-compor`, `--voz`, `--cpu`: iguais aos do `rodar.py` do Blender.

## Quanto tempo esperar (medido)

Medido em 16/11/2026 num notebook com Intel Core i7-13620H (16 threads) e NVIDIA RTX 4060 Laptop, Chromium 159 do
Playwright, Three.js r187. Exemplo de 14,4 s a 60 quadros por segundo (o padrão do kit) = 863 quadros 1080x1920,
pasta de trabalho fora do OneDrive. "CPU" é o SwiftShader, o mesmo desenho por CPU que a nuvem usa.

| Como | Por quadro | Render do exemplo (863 quadros) | Com `--leve` |
|---|---|---|---|
| CPU, 16 threads (este notebook) | 0,28 s | **4 min 2 s** (medido) | 0,16 s/quadro (2 min 20 s, medido) |
| CPU limitada a 4 núcleos (parecido com uma máquina pequena da nuvem) | 0,54 s (medido nos primeiros 240 quadros) | **cerca de 7 a 8 min** (estimado) | não medido |
| CPU limitada a 2 núcleos | 0,71 s (medido nos primeiros 240 quadros) | **cerca de 10 min** (estimado) | não medido |
| Placa de vídeo (`--placa gpu`, RTX 4060) | 0,05 s | **43 s** (medido) | 0,02 s/quadro (19 s, medido) |

O `rodar.py` completo na CPU de 16 threads levou **5 min 33 s** (medido): render 4 min 5 s, composição das 3 versões
1 min 11 s (na CPU), trilha e masterização 12 s, conferências, QA e capa 5 s. Os quadros-marco (`--stills`) levaram
6 s. A 30 quadros por segundo (`render.fps` no `config.json`) o render cai pela metade.

Para comparar: o Blender EEVEE na mesma RTX 4060 faz 0,39 a 0,60 s por quadro (tabela do `INSTALAR.md`). Ou seja,
na CPU o Three.js fica no mesmo tempo do Blender na placa, e na placa fica cerca de 10 vezes mais rápido.

O que pesa no tempo:
- **Núcleos da CPU.** O SwiftShader usa todos. Na nuvem, com 2 a 4 núcleos, conte 2 a 3 vezes o tempo deste notebook.
- **Duração do vídeo.** Um explicativo de 60 s a 60 q/s tem 3600 quadros: cerca de 17 min com 16 threads e 30 a 35
  min com 4 núcleos. Use `--leve` para aprovar e deixe o final rodando em segundo plano.
- **Antisserrilhado.** O MSAA 4x (bordas lisas) dobra o custo na CPU. Ele fica ligado: sem ele o contorno serrilha.
- **Pasta sincronizada.** Os quadros PNG somam ~1,5 GB por minuto de vídeo; deixe a pasta de trabalho fora do OneDrive,
  iCloud ou Dropbox. A pasta `quadros/` pode ser apagada depois que os vídeos saírem.

## Fazer um episódio novo

Copie `web/exemplo/cena.js` e troque a cena. O arquivo exporta duas funções:

- `montar(THREE, kit, dados)`: monta tudo e devolve `{ duracao }`. `dados` traz o `tempos` da narração e o
  `episodio` (o episodio.json).
- `quadro(t)`: põe cada coisa no lugar do instante `t`. O mesmo `t` tem de dar sempre o mesmo quadro: nada de relógio
  nem de `Math.random()` sem semente (use `aleatorio(semente)` do motor).

Os rótulos são registrados com `kit.rotulo('NOME', objeto, [x, y, z])`; o nome tem de bater com o `episodio.json`.
As peças prontas estão em `motor3d.js` (toon, contorno, blob, tubo, câmera, peixes GLB), `cenario3d.js` (fatia de
oceano, coral, alga, anêmona, estrela, pedra, feixe) e `bichos3d.js` (caravela, olhos, chinelo). Elas usam as mesmas
medidas do motor do Blender, com Z para cima.

Para rodar uma cena sua:

```
python explicativo3d/web/render.py PASTA/cena.js --tempos PASTA/audio/tempos.json --episodio PASTA/episodio.json --saida PASTA
```

## Diferenças para o Blender

Iguais: enquadramento, movimentos de câmera, tempos marcados pela fala, rótulos, paleta, os 3 tons do toon, a luz
presa na câmera, o contorno de nanquim e a fatia de oceano com cáustica na areia.

Diferentes:
- **Bordas.** O Blender usa 8 amostras; aqui é MSAA 4x. A borda fica um pouco mais dura, sem serrilhar.
- **Formas sorteadas.** Coral, alga, seixos, tentáculos e filhotes usam sorteio com semente. O sorteio do navegador
  não é o do Python: as formas têm o mesmo estilo e tamanho, mas não são idênticas às do Blender (o coral do exemplo,
  por exemplo, sai com os galhos mais juntos).
- **Nado dos peixes.** Aqui o nado roda na velocidade do arquivo GLB. No Blender ele fica mais lento a 60 q/s (o
  arquivo é importado a 24 q/s).
- **Metaball.** A superfície orgânica (coral, caravela, coração) é refeita pelo motor do navegador, com o mesmo campo
  e a mesma resolução do Blender. A malha é parecida, não a mesma; peças muito finas (a crista da caravela) mostram
  as mesmas falhas nos dois.
- **O que não existe aqui:** o arquivo `cena.blend` para abrir e mexer. Para ajustar a cena, edite o `cena.js`.

## Estrutura

```
web/
  render.py        abre o Chromium sem janela, pede quadro a quadro e grava quadros/, etiquetas.json e render.json
  pagina.html      página que o render.py abre (mapa de importação do Three.js)
  pagina.js        monta a cena e entrega cada quadro ao render.py
  motor3d.js       toon, contorno de nanquim, paleta, blob (metaball), tubo, peixes GLB, câmera e rótulos
  cenario3d.js     fatia de oceano em corte e o cenário (porta do kit3d.py)
  bichos3d.js      caravela em 4 partes com olhos e chinelo (porta do bichos3d.py)
  exemplo/         cena.js (a caravela) e rodar.py (o exemplo de ponta a ponta)
  vendor/          Three.js r187 (three.module.js, three.core.js e 3 addons), licença MIT em vendor/LICENSE
```

Licenças: Three.js sob MIT (`vendor/LICENSE`, copyright dos autores do three.js). Modelos CC0 e fonte OFL como no
resto do Explicativo 3D.
