<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Instalar o kit

O kit é Python 3.10+ (testado no 3.12) e precisa do **ffmpeg** instalado no sistema. Com placa NVIDIA o render e o
encoder rodam na GPU; sem ela (Mac, PC comum, nuvem) tudo cai para a CPU sozinho, sem configurar nada.

Depois de instalar, confira sempre com:

```
python verificar.py
```

Ele lista o que está ok, o que é opcional e o que falta (e sai com erro se faltar algo obrigatório).

---

## 1. Windows 10/11

```powershell
# Python 3.12 e ffmpeg (o kit não traz o ffmpeg: ele é GPL e cada um instala o seu)
winget install -e --id Python.Python.3.12
winget install -e --id Gyan.FFmpeg
# espeak-ng: só se for usar a voz local Kokoro. Instalador .msi oficial em
# https://github.com/espeak-ng/espeak-ng/releases (testado: 1.52.0)

cd caminho\para\kit
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python baixar_fontes.py          # só se a pasta fontes\ estiver vazia
python verificar.py
python exemplo\rodar.py          # o episódio de demonstração, de ponta a ponta
```

Opcionais (voz local e tempo de palavra):

```powershell
# com placa NVIDIA:  pip install torch --index-url https://download.pytorch.org/whl/cu124
# sem placa NVIDIA:  pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements-opcional.txt
```

Pasta com acento (ex.: "Área de Trabalho") funciona: o adaptador Kokoro usa o espeak-ng do sistema quando o do
pacote Python não enxerga os idiomas por causa do acento no caminho.

## 2. macOS (Apple Silicon ou Intel)

```bash
brew install python@3.12 ffmpeg espeak-ng
cd /caminho/para/kit
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python baixar_fontes.py
python verificar.py
python exemplo/rodar.py
```

No Mac não há NVENC: o kit usa o VideoToolbox (encoder de hardware da Apple) se o ffmpeg tiver, senão libx264.
O desenho tenta OpenGL; se não abrir, usa a CPU. Opcionais: `pip install torch` e
`pip install -r requirements-opcional.txt`.

## 3. Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip ffmpeg libgl1 libegl1 libfontconfig1 espeak-ng
cd /caminho/para/kit
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python baixar_fontes.py
python verificar.py
python exemplo/rodar.py
```

`libgl1`/`libegl1`/`libfontconfig1` são exigidas pelo skia-python mesmo sem placa de vídeo. Com NVIDIA e driver
instalados, o ffmpeg do sistema às vezes vem sem NVENC: aí o kit usa libx264 (funciona, só é mais lento).

## 4. Nuvem / celular (Claude Code na nuvem, Codex, qualquer Linux sem GPU e sem tela)

Tudo por linha de comando, sem janela e sem pergunta. O Claude (ou outro agente) pode rodar exatamente isto:

```bash
set -e
cd /caminho/para/kit
# sistema: ffmpeg (GPL, do repositório da distribuição), bibliotecas do skia e espeak-ng
(sudo -n true 2>/dev/null && SUDO=sudo || SUDO="")
$SUDO apt-get update -y
$SUDO env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  ffmpeg libgl1 libegl1 libfontconfig1 espeak-ng python3-venv
# Python
python3 -m venv .venv && . .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# fontes: baixadas das fontes oficiais OFL (Google Fonts e release do autor da Inter), com as licenças
python baixar_fontes.py
# conferir: deve mostrar "CPU (raster)" e "libx264"
python verificar.py
# episódio de demonstração com o mp3 de exemplo (não baixa modelo nenhum)
python exemplo/rodar.py
```

O que acontece sozinho nesse ambiente:

- sem tela nem GPU, o render detecta e roda na **CPU**, dividido em vários processos (`render.processos_cpu`,
  "auto" = núcleos − 1, até 8), e o encoder vira **libx264**. Nada para configurar;
- os caminhos são todos relativos à pasta do kit (funciona igual no Windows, Mac e Linux);
- as **chaves só vêm de variável de ambiente** (ver README, "Chaves"). Na nuvem, defina-as nas variáveis/segredos do
  ambiente, nunca em arquivo dentro do kit.

Opcionais na nuvem (pesados: só se for gerar voz ou alinhar lá):

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu   # PyTorch de CPU (~200 MB, não o de CUDA)
pip install -r requirements-opcional.txt                              # faster-whisper + kokoro
```

O Whisper (`small`, ~500 MB) e o Kokoro (~330 MB) baixam o modelo do Hugging Face na primeira vez.

Tempo esperado: o render na CPU é bem mais lento que na GPU (veja os números no README). Para ver o resultado
rápido, rode primeiro `python exemplo/rodar.py --stills`, que gera só os quadros-marco em segundos.

---

## VectorCraft (opcional: arte nova de personagem)

O kit já vem com dois personagens prontos (`personagens/lola` e `personagens/nico`, PNG por parte + `partes.json`),
feitos a partir do molde e livres para usar. Para criar personagens novos há dois motores:

- **Skia** (padrão quando não há VectorCraft): `python construir_boneco.py <nome> --motor skia`. Não precisa de
  nada além do kit; troca a malha de volume por um degradê radial.
- **VectorCraft** (melhor acabamento, o mesmo do estúdio de origem): `python construir_boneco.py <nome> --motor vectorcraft`.

VectorCraft é um editor vetorial de código aberto (licença **MIT ou Apache-2.0**, à escolha) feito pelo time ArtCraft,
para Windows, macOS, Linux e FreeBSD. O nome e o logo "ArtCraft" são marca registrada deles e não são livres.
O kit **não redistribui** o programa: baixe em <https://getartcraft.com/apps/vectorcraft> (ou nos releases de
<https://github.com/storytold/vectorcraft>). O kit procura o `vectorcraft-cli` no PATH e na pasta padrão de
instalação; se estiver em outro lugar, aponte `ferramentas.vectorcraft` no `config.json`.
Versão testada: 0.17.0.

## ffmpeg

O kit chama o ffmpeg/ffprobe do sistema (leitura de áudio, loudnorm, encoder, grade de QA). Builds com
`--enable-gpl` são GPL: usar é livre, mas o kit **não redistribui** o binário. Cada um instala o seu (winget, brew,
apt). Se não estiver no PATH, aponte `ferramentas.ffmpeg` e `ferramentas.ffprobe` no `config.json`.
