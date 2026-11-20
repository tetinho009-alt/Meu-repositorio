<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Explicativo 3D: instalar e rodar

O motor do Formato 2 (Explicativo 3D) monta a cena no **Blender** por código, renderiza os quadros no **EEVEE** (o
render em tempo real do Blender, que roda na placa de vídeo) e o resto é o kit de sempre: voz, tempo de palavra,
trilha, masterização, composição com legenda, rótulos e o CTA de cada rede, capa e grade de QA.

Pré-requisito: o kit principal instalado e passando no `python verificar.py` (`kit/INSTALAR.md`). Todos os comandos
abaixo rodam **a partir da pasta `kit/`**, com o ambiente do kit ativado.

## O que é exigido

| Item | Exigência |
|---|---|
| Blender | **5.2 LTS** (testado no 5.2.3). Outra versão até roda, mas o script avisa: não foi testada. Abaixo do 4.2, não roda |
| Placa de vídeo | Qualquer uma com driver atualizado: NVIDIA, AMD, Intel integrada ou Apple M1 em diante. O EEVEE **não roda sem placa** |
| Disco | ~1,5 GB do Blender + ~3 GB de quadros PNG por minuto de vídeo (1,6 MB por quadro; a pasta `quadros/` pode ser apagada depois que os vídeos saírem). Prefira uma pasta de trabalho fora do OneDrive, iCloud ou Dropbox (ver seção 4) |
| Kit | Python do kit com `requirements.txt` instalado (numpy, scipy, Pillow, skia) e ffmpeg |

## 1. Instalar o Blender

### Windows 10/11

```powershell
winget install -e --id BlenderFoundation.Blender --version 5.2.3
```

Ou baixe o instalador `.msi` do 5.2 LTS em https://www.blender.org/download/lts/5-2/ e instale com as opções padrão.
Ele vai para `C:\Program Files\Blender Foundation\Blender 5.2\` e o kit acha sozinho.

### macOS (Apple Silicon ou Intel)

Baixe o `.dmg` do 5.2 LTS em https://www.blender.org/download/lts/5-2/ (escolha "Apple Silicon" ou "Intel"), abra e
arraste o Blender para **Aplicativos**. O kit acha em `/Applications/Blender.app`. Evite `brew install --cask blender`: instala a versão mais nova, não a LTS.

### Blender em outro lugar

Aponte no `config.json` do kit:

```json
{ "ferramentas": { "blender": "D:/Programas/Blender 5.2/blender.exe" } }
```

ou defina a variável de ambiente `BLENDER` com o caminho do executável.

## 2. Conferir se deu certo

```
python explicativo3d/ambiente3d.py --teste
```

Deu certo quando aparece a versão e a linha `EEVEE OK na placa: <nome da sua placa>`. Se aparecer
`TESTE_FALHOU`, atualize o driver da placa de vídeo. Notebook com duas placas (integrada + NVIDIA): veja qual o
Blender pegou e, se for a integrada, teste a outra com `--gpu-device 1` (e use o mesmo `--gpu-device` no `rodar.py`).

Depois, os quadros-marco do exemplo (5 imagens, menos de 1 min):

```
python explicativo3d/exemplo/rodar.py --stills
```

Abra `trabalho/explicativo3d_caravela/folha_stills.jpg`: a fatia de oceano com a caravela inteira, depois
desmontada em 4 partes com olhos, um coração no meio e de novo o plano aberto.

## 3. Rodar o exemplo inteiro

```
python explicativo3d/exemplo/rodar.py
```

Sai em `trabalho/explicativo3d_caravela/`:

| Arquivo | O que é |
|---|---|
| `IG/01_video.mp4`, `TIKTOK/01_video.mp4`, `YOUTUBE/01_video.mp4` | O mesmo vídeo de 14,4 s com o CTA de cada rede nos últimos 2,2 s |
| `IG/capa.jpg` (e nas outras) | Capa 1080x1920 com a pergunta dentro do recorte 3:4 do grid; `capa_grid_3x4.jpg` mostra como fica no perfil |
| `qa/qa_grade_0.jpg` | Um quadro a cada 2 s com a zona segura desenhada |
| `render.json` | Quadros, segundos de render e a placa usada |
| `cena.blend` | A cena, para abrir no Blender e mexer |

Conferência automática que o `rodar.py` já faz em cada vídeo: áudio estéreo, 48 kHz, −14 LUFS e pico abaixo de
−1 dBTP (`masterizar.py --verificar`). Se algo sair do padrão, ele para com `FALHOU em: ...`.

Com a sua voz no lugar da narração de exemplo: `python explicativo3d/exemplo/rodar.py --voz elevenlabs` (ou `azure`,
`piper`, `kokoro`). Câmera, efeitos, rótulos e legenda se ajustam ao novo ritmo sozinhos.

## 4. Quanto tempo esperar (medido)

Medido num notebook com Intel Core i7-13620H, que tem duas placas: uma NVIDIA RTX 4060 Laptop (8 GB) e a Intel UHD
integrada. Blender 5.2.3, exemplo de 14,4 s = 431 quadros 1080x1920, 8 amostras.

| Placa | Render por quadro | Render do exemplo (431 quadros) | Com `--leve` |
|---|---|---|---|
| NVIDIA RTX 4060 Laptop | 0,39 a 0,60 s (3 medições) | **2 min 50 s a 4 min 20 s** | 0,18 s/quadro (1 min 20 s) |
| Intel UHD integrada (`--gpu-device 1`) | 0,81 s (medido nos primeiros 120 quadros) | **cerca de 6 min** (estimado) | 0,19 s/quadro (1 min 20 s) |

A variação na RTX veio do que mais estava aberto no computador; a medição mais lenta foi com a pasta de trabalho
dentro do OneDrive. Somando o resto (abrir o Blender e montar a cena, ~10 s; trilha e masterização, ~5 s; composição
das 3 versões, ~50 s, na CPU), o `rodar.py` completo levou **5 min na RTX 4060** (medido, pasta local). Os
quadros-marco (`--stills`) levaram 21 s. O `ambiente3d.py --teste` mede um quadro: 0,47 s na RTX 4060.

O que pesa no tempo:
- **Duração do vídeo.** Um explicativo de 60 s tem 1800 quadros: na RTX 4060, 12 a 18 min de render; na Intel
  integrada, ~25 min; com `--leve`, ~6 min em qualquer uma. Some ~3,5 min de composição por minuto de vídeo.
- **Com `--leve` as duas placas empatam:** o gargalo passa a ser a CPU (avaliar a cena e gravar o PNG de cada
  quadro), não a placa.
- **Pasta sincronizada.** São ~3 GB de PNG por minuto de vídeo subindo para a nuvem enquanto o Blender grava.
  Aponte `pastas.trabalho` do `config.json` para uma pasta fora do OneDrive, iCloud ou Dropbox.
- **Primeiro render.** O EEVEE compila os shaders na primeira vez; o primeiro quadro demora mais.
- Placas AMD, Apple M1 em diante e outras NVIDIA não foram medidas. Rode `--stills` e o `ambiente3d.py --teste` e
  compare com a tabela: o teste mostra o tempo de um quadro na sua placa.

Gere sempre os quadros-marco (`--stills`) antes do render longo e rode o render longo em segundo plano.

## 5. Sem placa NVIDIA

- **Placa integrada (Intel, AMD) ou Mac:** funciona igual, só mais devagar (na Intel UHD medida, cerca de 2 vezes
  o tempo da RTX 4060). Para prévia, use `--leve`: renderiza em metade da resolução com 4 amostras e amplia na
  composição. O contorno fica mais fino e a imagem mais macia, bom para aprovar movimento e tempo, não para postar.
  O vídeo final sai sem `--leve`; deixe rodando em segundo plano.
- **Sem placa nenhuma** (servidor na nuvem sem GPU, máquina virtual, celular): o EEVEE não abre e o
  `ambiente3d.py --teste` falha. Use o **motor Three.js** (`explicativo3d/web/LEIA-ME.md`): a mesma cena, desenhada
  pelo processador, com visual quase igual.
- O encoder de vídeo é o do kit (NVENC, Quick Sync, AMF, VideoToolbox ou libx264): sem NVIDIA ele escolhe sozinho.
  `--cpu` força o libx264.

## 6. Estrutura

```
explicativo3d/
  ambiente3d.py      acha o Blender, confere a versão e testa a placa (--teste)
  motor/
    base3d.py        materiais toon, contorno de nanquim, ajuste do EEVEE (roda dentro do Blender)
    kit3d.py         cenário: fatia de oceano em corte, coral, alga, anêmona, estrela, pedra, bolha, feixe de luz,
                     peixes CC0 com material da paleta e câmera vertical com luz presa nela
    bichos3d.py      caravela-portuguesa em 4 partes com olhos (desmonta), olhos cartoon, chinelo
    tempos.py        marcos por palavra da narração e a legenda palavra a palavra (Python puro)
    som3d.py         marimba, bolha, estalo de encaixe, brilho, água, cama musical e mix com ducking
    compor.py        fundo, gancho, legenda, rótulos ligados ao 3D e o CTA de cada rede; as 3 versões numa passada
    capa.py          capa com a pergunta no recorte 3:4
  modelos/           peixes Quaternius (CC0) + FONTES.md com a licença
  fontes/            Fredoka (SIL OFL 1.1) + licença
  exemplo/           episódio de 14 s: roteiro.md, narrador.txt, episodio.json, cena.py, trilha.py, rodar.py
                     e a narração de exemplo (Kokoro, Apache-2.0)
```

Licenças: o código do motor é parte do kit. Modelos CC0 (ver `modelos/FONTES.md`), fonte OFL (`fontes/Fredoka-OFL.txt`),
efeitos e trilha gerados por código (sem direito de terceiros). A única voz é a do seu provedor; a de exemplo é do
Kokoro (Apache-2.0).
