<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Kit da pilha Estúdio

Código para produzir episódios de série animada interativa (o público vota nos comentários e a escolha vira a
próxima parte) do roteiro ao vídeo final 1080x1920, e publicar pela API oficial de cada rede. Roda pelo Claude Code,
pelo Codex ou na mão. Com GPU NVIDIA é mais rápido; sem GPU (Mac, PC comum, nuvem) funciona igual, na CPU.

Instalação: [INSTALAR.md](INSTALAR.md) (Windows, macOS, Linux e nuvem/celular). Conferência: `python verificar.py`.

## Início rápido

```bash
pip install -r requirements.txt
python baixar_fontes.py           # se a pasta fontes/ estiver vazia
python verificar.py
python exemplo/rodar.py           # episódio de demonstração de ~16 s, de ponta a ponta
```

Sai em `trabalho/a_luz_da_casa_7_p1/`: `a_luz_da_casa_7_p1.mp4`, `folha.jpg` (quadros-marco), `qa/qa_grade_0.jpg` (um quadro a
cada 2 s com a zona segura desenhada) e `capa.jpg`.

## Estrutura

```
kit/
  config.exemplo.json     todos os campos (copie para config.json e ajuste)
  config.py               lê a configuração; chaves só por variável de ambiente ou arquivo FORA do kit
  verificar.py            confere o ambiente e diz o que falta
  baixar_fontes.py        fontes OFL das fontes oficiais, com licença
  construir_boneco.py     personagem a partir do molde (VectorCraft ou Skia)
  narrar.py               voz: texto -> mp3 (+ tempos de palavra, se o provedor der)
  alinhar.py              tempo de cada palavra do roteiro (Whisper GPU/CPU ou tempos do provedor)
  masterizar.py           mix -> loudnorm -14 LUFS -> estéreo 48 kHz -> checagem de pico
  qa_grade.py             grade de revisão (1 quadro a cada 2 s), com a zona segura
  capa.py                 capa do episódio (elenco recortado como adesivo sobre o cartão)
  episodio_novo.py        cria a pasta de um episódio a partir dos modelos
  maquina/                núcleo
    motor.py              render Skia GPU -> CPU, encoder NVENC -> QSV -> AMF -> VideoToolbox -> libx264
    rig.py  molde.py      boneco por partes com hierarquia e pivôs; molde de pessoa (cores, roupa, cabelo)
    cinema.py             luz no personagem, foco, correção, vinheta, grão, chicote de câmera
    perspectiva.py        Cam3D, quad, caixa e fila de desenho por profundidade
    som.py                mesa estéreo 48 kHz com ducking, efeitos feitos por código
    legenda.py            legenda palavra a palavra
    tela.py               abertura, selo de ficção, cartão de regra, cartão de voto, apuração, pílula de seguir
    capa.py  alinhamento.py  votos.py  desenho.py
  voz/                    gemini (grátis), elevenlabs, azure, kokoro_local, piper_local, edge_teste (mesma interface);
                          pronuncia.py aplica a base de pronúncia em qualquer voz
  cartelas/               motor de cartelas: vídeo inteiro a partir de um roteiro.json (top 5, quiz, tipografia,
                          faceless, história real, antes e depois, bastidores); exemplo/ e modelos/
  qa/antes_do_render.py   trava única antes do render (disco, gancho, duração do estilo, palavras que a Meta pune,
                          termo em inglês fora da base, emenda em cima de fala, voz x roteiro)
  erros.py                erro em português, com o que fazer
  numeros_pt.py           número em algarismo de volta para extenso (para o alinhamento)
  publicar/               instagram, youtube, tiktok, responder_votos (só API oficial; todos com --seco)
  painel/                 painel no navegador (servidor.py), ícone que abre sem terminal (atalho.py --criar) e
                          conversa com o Claude Code ou o Codex dentro do painel (ia.py, travado por ia_guarda.py)
  personagens/            lola e nico (exemplos prontos, livres para usar)
  modelos/episodio/       roteiro.md, narrador.txt, post.md
  exemplo/                episódio de demonstração (ep.py, trilha.py, rodar.py, episodio.json, mp3 de exemplo, post.json,
                          falas_exemplo.json, comentários de teste do robô)
  falas.py                vozes: uma tomada por fala, cada personagem com a sua voz, com o tempo de cada palavra
  apuracao_video.py       apuração real animada da parte anterior, emendada depois do gancho da parte seguinte
  capa.py --redes         uma capa por rede (a linha de baixo com o CTA de cada uma)
  pacote_redes.py         pacote final: pasta por rede com vídeo + capa + legenda conferida
  boneco3d/               personagem 3D opcional, gerado do 2D, renderizado na GPU pelo Blender (gerar, clipe, rodar)
  placar/                 placar ao vivo: placar.py (APIs oficiais), site/ (página e retorno do TikTok), preparar.py,
                          placar.yml (GitHub Actions) e exemplo/ (respostas gravadas das APIs para teste)
  fontes/                 Anton, Inter, IBM Plex Mono, Archivo Black, Barlow (SIL OFL 1.1, licenças junto)
```

## Comandos

Todos rodam a partir da pasta do kit. `--help` em qualquer um mostra as opções.

### Produção

| Comando | O que faz |
|---|---|
| `python verificar.py [--cpu]` | Confere Python, bibliotecas, ffmpeg, encoder, GPU/CPU, fontes, personagens, chaves definidas |
| `python chave.py [--qual azure] [--conferir]` | Janela local para colar a chave da voz (não passa pela conversa); testa, salva fora do kit e mostra o saldo do plano |
| `python -m voz.amostras --frase "..." [--genero masculino] [--idade jovem] [--jeito "animado"] [--provedor kokoro] [--seco]` | A mesma frase em 3 vozes, em `canal/testes-de-voz/`, para escolher ouvindo |
| `python -m voz.amostras --br [--genero G]` / `--adicionar DONO VOICE_ID "Nome"` | Vozes brasileiras da biblioteca (prévia grátis) e pôr uma delas na conta |
| `python cartelas/rodar.py <pasta> [--stills \| --previa] [--voz gemini\|kokoro\|elevenlabs] [--seco] [--cpu] [--blur N]` | Motor de cartelas: do roteiro.json ao pacote das redes escolhidas (`cartelas/LEIA-ME.md`) |
| `python qa/antes_do_render.py <roteiro.json> [--duracao S] [--estilo top5]` | Trava antes do render, avulsa |
| `python chave.py --qual gemini` | Janela da chave grátis do Google AI Studio (voz Gemini TTS) |
| `python baixar_fontes.py` | Baixa as fontes OFL (Google Fonts e release oficial da Inter) |
| `python construir_boneco.py <nome> [--motor auto\|vectorcraft\|skia]` | Gera `personagens/<nome>/partes/*.png` + `partes.json` a partir de `personagem.json` |
| `python episodio_novo.py <pasta> --serie "..." --parte 1 --titulo "..." --pergunta "..." --opcoes A B [--personagem lola]` | Cria a pasta do episódio (roteiro, narrador, post, episodio.json, respostas.json, ep.py, trilha.py, rodar.py) |
| `python narrar.py <narrador.txt> <saida.mp3> [--provedor kokoro\|piper\|azure\|elevenlabs\|edge] [--voz ID]` | Narração numa geração só |
| `python alinhar.py <audio> <narrador.txt> <tempos.json> [--modo whisper\|provedor] [--cpu]` | Tempo de cada palavra do roteiro |
| `python <episodio>/trilha.py --audio PASTA --trabalho PASTA` | Narração na linha do tempo + efeitos estéreo -> `mix.wav` e `linha.json` |
| `python masterizar.py <mix.wav> [mais.wav ...] -o <mix_norm.wav>` | Loudnorm em 2 passadas, estéreo 48 kHz, checa volume e pico |
| `python masterizar.py --verificar <arquivo.wav\|video.mp4>` | Só mede e confere (use no vídeo final) |
| `python <episodio>/ep.py --trabalho PASTA [--cpu] [--stills] [--saida v.mp4]` | Render do episódio (`--stills` = só quadros-marco) |
| `python qa_grade.py <video.mp4> [--passo 2] [--zona]` | Grade de revisão com a zona segura |
| `python capa.py <episodio.json> <capa.jpg> [--arte PNG] [--cpu] [--redes]` | Capa com o elenco recortado; `--redes` faz uma por rede (`_ig`, `_tiktok`, `_youtube`) |
| `python falas.py <falas.json> [--seco] [--refazer]` | Uma tomada por fala, voz de cada personagem, tempo de palavra ao lado de cada mp3 |
| `python falas.py <falas.json> --juntar <pasta> [--pausa 0.35]` | Junta as falas em `narrador.mp3` + `tempos.json` para a trilha |
| `python apuracao_video.py <apuracao.json> --saida a.mp4 [--inserir-em parte2.mp4 --apos S]` | Apuração animada (6,6 s) e, opcional, emendada depois do gancho |
| `python cta_redes.py <video.mp4> [--parte N \| --gancho "..."]` | Só as 3 versões do vídeo com o CTA de cada rede |
| `python pacote_redes.py --nome N (--video v.mp4 \| --videos PASTA) --capa c.jpg [--redes-capa \| --carimbar] --legendas post.json` | Pacote das redes escolhidas, com a legenda de cada rede conferida |
| `python boneco3d/rodar.py <nome> (--previa \| --exemplo \| --clipe fala --tempos T --audio A)` | Personagem 3D: prévia, ou clipe falando pelo tempo de palavra |
| `python <episodio>/rodar.py [--voz kokoro] [--cpu] [--stills]` | Tudo acima em sequência (voz -> tempos -> trilha -> master -> render -> checagem -> grade -> capa) |

### Publicação (só API oficial; `--seco` monta e mostra os pedidos sem enviar nada)

| Comando | O que faz |
|---|---|
| `python -m publicar.instagram --video ep.mp4 --legenda post.txt [--capa-url URL \| --capa-ms 1500] [--sem-rotulo-ia] [--seco]` | Reel: container -> envio do arquivo (resumable) -> status -> publicar -> link |
| `python -m publicar.instagram --video-url URL --legenda post.txt [--seco]` | Igual, com o vídeo já hospedado numa URL pública |
| `python -m publicar.youtube autorizar` | Uma vez, num computador com navegador: gera o YT_REFRESH_TOKEN |
| `python -m publicar.youtube enviar --video ep.mp4 --titulo "..." --descricao desc.txt [--tags a,b] [--privacidade private] [--publicar-em 2026-11-03T22:00:00Z] [--sintetico\|--nao-sintetico] [--seco]` | Short por `videos.insert` (madeForKids falso; mídia sintética configurável) |
| `python -m publicar.tiktok --video ep.mp4 [--seco]` | Envia para a caixa de entrada/rascunho do app; o dono publica no TikTok |
| `python -m publicar.responder_votos --respostas respostas.json [--seco] [--comentarios-exemplo arq.json]` | Sugere a resposta de cada voto no IG, para colar à mão; só envia com `--sei-o-risco` (não recomendado) |
| `python -m publicar.responder_votos --status` | Mostra quantas respostas saíram hoje |
| `python -m publicar.responder_votos --manual respostas_manuais.json [--seco]` | Confere as respostas aprovadas pelo dono e mostra o que colar; só envia com `--sei-o-risco` |
| `python -m publicar.ig_token --status \| --renovar` | Idade do token do Instagram; renova e grava no arquivo de segredos |
| `python placar/placar.py --episodios E --saida placar/site/placar.json` | Placar ao vivo: votos e métricas do Instagram, TikTok e YouTube pelas APIs oficiais (o Kwai ainda não entra) |
| `python placar/placar.py --episodios E --so SLUG --detalhe apuracao.json` | Apuração de um episódio para o vídeo seguinte |
| `python placar/placar.py --episodios E --tiktok-link` / `--tiktok-codigo C` | Autoriza a leitura do TikTok uma vez |
| `python placar/preparar.py <pasta-do-repositorio>` | Monta o site do placar para o GitHub Pages (`placar/LEIA-ME.md`) |

Nada no kit curte, segue ou manda DM. Teste a seco do robô, sem token e sem rede:
`python -m publicar.responder_votos --respostas exemplo/respostas.json --seco --comentarios-exemplo exemplo/comentarios_exemplo.json`

## Chaves (nunca na conversa nem na pasta do kit)

O jeito fácil para a voz: `python chave.py`. Ele abre uma página só neste computador, o usuário cola a chave lá, o
kit testa, grava em `~/.temporada-viral/segredos.json` e aponta `segredos.arquivo` para esse arquivo. Para as
outras chaves, use variável de ambiente ou o mesmo arquivo de segredos.

| Variável | Para quê |
|---|---|
| `GEMINI_API_KEY` | voz grátis do Google (Gemini TTS) |
| `ELEVENLABS_API_KEY` | voz ElevenLabs |
| `AZURE_SPEECH_KEY` | voz Azure (região em `voz.azure.regiao`) |
| `IG_ACCESS_TOKEN` | token longo da conta profissional do Instagram (publicar e responder) |
| `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN` | OAuth do YouTube |
| `TIKTOK_ACCESS_TOKEN` | OAuth do TikTok (escopo `video.upload`) |
| `YT_API_KEY` | chave de leitura do YouTube (placar e apuração) |
| `TT_CLIENT_KEY`, `TT_CLIENT_SECRET`, `TT_REFRESH_TOKEN` | Display API do TikTok (views no placar); o refresh é gravado pelo `--tiktok-codigo` |

Alternativa local: um JSON `{"VARIAVEL": "valor"}` FORA da pasta do kit, apontado em `segredos.arquivo` (o kit
recusa arquivo de segredos dentro da própria pasta). `MAQUINA_CONFIG=/caminho/config.json` usa outra configuração.

## Regras de qualidade embutidas no código

- **Zona segura** (`zona_segura`): texto importante em x 120–900, y 280–1250; a legenda pode descer até a borda
  `legenda_y_max` = 1420 (a faixa de baixo e a direita são cobertas pela interface do TikTok, Reels e Shorts).
  `qa_grade.py --zona` desenha essas linhas em cada quadro.
- **Áudio**: sempre estéreo 48 kHz, −14 LUFS integrados, pico −1,5 dBTP (`masterizar.py` falha se sair disso).
- **Voto**: duas opções, cores fixas (opção 1 coral, opção 2 azul-céu, em `cores` do config), número e palavra valem. Na tela: "VOCÊS DECIDEM"
  e "A ESCOLHA DA GALERA VIRA A PARTE N". Nunca "comente a palavra" nem "curte e compartilha" (engagement bait).
- **Ficção declarada** no selo do vídeo e no post.
- **Personagem com luz** (`cinema.iluminado`), objeto na mão pelo rig (`Boneco.mao`), tudo em cena ordenado por
  profundidade (`perspectiva.Cena`), boca só fala na fala, piscada irregular, respiração.
- **Voz**: narração numa geração só; nunca acelerar áudio pronto; ElevenLabs um pedido por vez, com intervalo e
  espera exponencial no 429.

## Render: GPU e CPU

| Máquina | Render | Encoder | Exemplo de 19 s |
|---|---|---|---|
| RTX 4060 Laptop (Windows) | GPU (OpenGL) | h264_nvenc | 23 a 45 s de render (13 a 25 quadros/s) |
| Mesma máquina com `--cpu` | CPU (raster), 8 processos | libx264 | ~11 min (0,9 quadro/s) |

Medido com a máquina dividida com outros renders; numa máquina livre os dois ficam mais rápidos.

A regra é sempre a mesma, sem configurar nada:

- **PC com placa de vídeo:** desenha na GPU (Skia sobre OpenGL) e grava no encoder da placa (NVENC na NVIDIA), num
  processo só. No notebook com duas placas, o desenho vai para a dedicada (a NVIDIA), não para a integrada.
- **Nuvem, celular ou PC sem placa:** desenha na CPU, em partes paralelas (um processo por núcleo, cada x264 com 1
  thread) juntadas sem recodificar, e grava no libx264.
- **OpenGL de software** (llvmpipe, SwiftShader, "GDI Generic", área de trabalho remota) conta como sem placa.
- **Placa que existe e não desenha** (glfw faltando, driver velho): o render avisa e o `python verificar.py` reprova.
  Corrija antes do render longo; senão um vídeo de 2 min, que leva poucos minutos na GPU, vira dezenas na CPU.
- **Vídeos gravados ao mesmo tempo** (as versões por rede do explicativo) usam no máximo `render.sessoes_gpu`
  encoders da placa (padrão 3): placa comum recusa sessões de NVENC além do limite do driver, e outros programas
  abertos também gastam sessão. As que passam do limite vão para o libx264. Nunca rode vários renders na placa ao
  mesmo tempo: um por vez é mais rápido que três disputando.

Sem GPU o desenho na CPU é várias vezes mais lento. Para não esperar à toa:

- `--stills` gera só os quadros-marco (segundos) para conferir antes de renderizar tudo;
- na CPU o vídeo é dividido entre processos (`render.processos_cpu`, "auto" = núcleos − 1, até 16) e juntado sem
  recodificar;
- `render.escala_cpu: 0.5` no `config.json` desenha em 540x960 e amplia para 1080x1920 (no teste, render 2x mais rápido;
  imagem mais macia): bom para prévia na nuvem, não para o master final.

## Licenças de terceiros

| Item | Licença / observação |
|---|---|
| skia-python / Skia | BSD-3-Clause |
| glfw (pyGLFW) / GLFW | MIT / zlib |
| numpy, scipy | BSD-3-Clause |
| Pillow | MIT-CMU (HPND) |
| requests | Apache-2.0 |
| ffmpeg | GPL nos builds completos: **não vem no kit**, cada um instala |
| Fontes Anton, Inter, IBM Plex Mono, Archivo Black, Barlow | SIL Open Font License 1.1 (textos em `fontes/*-OFL.txt`) |
| faster-whisper / modelo Whisper | MIT / MIT |
| Kokoro-82M | Apache-2.0 (o mp3 de exemplo foi gerado com ele, voz `pm_alex`) |
| espeak-ng | GPL-3.0 (instalado pelo usuário, usado pelo Kokoro em pt-BR) |
| Piper | cada voz tem a licença do seu conjunto de dados: confira antes de usar comercialmente |
| edge-tts | **só teste**: serviço sem licença comercial; bloqueado por padrão (`voz.permitir_nao_comercial`) |
| ElevenLabs, Azure | uso comercial conforme o plano/contrato da conta do cliente (plano grátis do ElevenLabs não é comercial) |
| Gemini TTS (Google AI Studio) | termos da API do Gemini na conta do cliente: o Google não reivindica o áudio gerado; no plano grátis, usa o texto enviado para melhorar os produtos dele |
| VectorCraft | MIT ou Apache-2.0; marca ArtCraft não é livre; não vem no kit (ver INSTALAR.md) |
| Personagens `lola` e `nico`, cenário e trilha do exemplo | feitos para o kit a partir do molde e de efeitos por código; livres para usar |

Áudio de terceiros "só com crédito" (YouTube) não tem licença: o kit não usa e não ensina a baixar.
