<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# 00 · Começar: modo, pilha e entrevista

Carregue na primeira conversa e sempre que o usuário disser "nova série" sem perfil registrado.

## 1. Diga o modo em uma frase

| Modo | Sinal | Frase para o usuário |
|---|---|---|
| Agente | Você roda comandos num computador do usuário | "Eu escrevo, gero a voz, monto e publico; você aprova em cada portão." |
| Nuvem | Claude Code na nuvem (app do Claude ou claude.ai/code), aberto num repositório do GitHub; é o caminho de quem está só no celular | "Faço tudo daqui, com render na CPU da nuvem (mais lento). Um episódio por vez, até ~90 s." |

### Só no celular

O caminho é o modo nuvem (abaixo): o usuário abre o Claude Code na nuvem pelo app do Claude, num repositório do
GitHub, e o kit chega pelo instalador público `andrefranceschini/temporada-viral-instalador`, com a senha da área
de membros (passo a passo em `celular/COMECE-AQUI.md`). Precisa do plano Pro do Claude. Sem plano pago, não há
caminho pelo celular: o grátis é o Antigravity no computador.

Se você não roda comandos (ChatGPT ou Gemini no chat, Claude.ai sem Code), não guie montagem manual em editor: diga
ao usuário que o estúdio precisa de Claude Code, Codex ou Antigravity e mostre o `LEIA-ME.md`.

### Modo nuvem

O kit já está no repositório (instalado pelo instalador ou enviado pelo usuário). Os vídeos prontos ficam no
repositório, uma pasta por rede, e o usuário baixa pelo celular.

1. A máquina da nuvem **não tem GPU**. O kit detecta e renderiza na CPU (ver `kit/README.md`). Um vídeo de 80 s
   leva mais tempo que no PC com placa NVIDIA; planeje um episódio por sessão.
2. Chaves entram como variáveis ou segredos do ambiente da nuvem, nunca na conversa:
   - ElevenLabs (voz e efeitos);
   - Meta (token do Instagram);
   - Google (credencial OAuth do YouTube).
   Os nomes exatos das variáveis estão em `kit/README.md`.
3. O vídeo final volta pela conversa. O usuário publica pela API (`metodo/publicacao-api.md`) ou baixa no celular e
   posta pelo app ou agendador.
4. Recomendação: episódio de até ~90 s, render em CPU, um episódio por vez, prévia comprimida abaixo de 30 MB.

## 2. Escolha a pilha

| Etapa | Zero (R$ 0) | Criador (≈ R$ 143/mês) | Estúdio (≈ R$ 355 a 795/mês) |
|---|---|---|---|
| Roteiro e orquestração | Antigravity ou Codex (os dois começam grátis, no computador) | Claude Code (Pro) | Claude Code (Pro ou Max) |
| Voz | **Gemini TTS** (grátis, com limite por dia), Kokoro ou Azure F0 | ElevenLabs Starter (US$ 6) | ElevenLabs Creator (US$ 22) |
| Efeitos e trilha | Freesound **CC0** + Pixabay (conferir Content ID) | Idem | Mirelo Creator (€ 20) + sons por código |
| Visual | Kit 2D na CPU (`kit/`) | HyperFrames ou Remotion + imagens geradas | Python + Skia com rig próprio na GPU (`kit/`) |
| Legenda com tempo | Alinhamento com o texto do roteiro ou faster-whisper | Timestamps da ElevenLabs | Timestamps ou alinhamento forçado |
| Render | ffmpeg libx264 (ou QSV/AMF) | ffmpeg (NVENC se houver) | ffmpeg NVENC |
| Publicação | Meta Business Suite, TikTok Studio, YouTube Studio | Idem ou Buffer Free | API do Instagram e do YouTube; TikTok pelo Studio |

Premissas de custo: 13 vídeos por mês, 80 s cada, ~1.200 caracteres de narração por vídeo, câmbio de cálculo
US$ 1 = R$ 5,50 e € 1 = R$ 6,20 (out/2026). Confira os preços no dia em que assinar. A Pilha Zero custa em tempo
(estimativa de 3 a 5 h por vídeo) e em qualidade de voz.

A Pilha Zero é o caminho grátis e a Criador é o recomendado, descritos do começo ao fim em `metodo/caminhos.md`.

Regra de escolha:
- sem cartão internacional ou sem orçamento: Zero;
- quer voz boa e não tem GPU NVIDIA: Criador;
- tem placa NVIDIA e quer o resultado mais consistente: Estúdio.

## 3. Entrevista (faça em blocos de 3 perguntas)

Bloco A, o projeto:
1. Que gênero? (terror, suspense, mistério, drama sobrenatural). Exemplos do pacote são terror ficção.
2. Que lugar e que cotidiano o público vai reconhecer? (laje da periferia, sítio, metrô, condomínio, escola não).
3. Já tem nome e @? Estão livres em todas as redes que você vai usar?

Bloco B, a operação:
4. Quantas horas por semana você tem?
5. Quais redes: Instagram, TikTok, YouTube Shorts, YouTube longo, Kwai (recomendado: Instagram, TikTok e Shorts,
   mesmo vídeo)?
6. Equipamento: PC com placa NVIDIA, PC comum, só celular?

Bloco C, contas e limites:
7. Orçamento mensal para ferramentas?
8. Você é maior de 18 anos e dono das contas? (exigido para monetização nas redes)
9. Já existe perfil com público? Que tipo de conteúdo ele recebe hoje?

## 4. Registre o perfil do projeto

Escreva e peça confirmação:

```
PERFIL DO PROJETO
Modo: agente | nuvem
Pilha: zero | criador | estudio
Gênero e lugar: ...
Nome e @: ...
Redes: IG, TikTok, Shorts
Cadência inicial: 2 episódios por semana, 1 série (ver modelos/calendario-semanal.md)
Horas por semana: ...
Orçamento: ...
Pendências: reservar @, criar contas profissionais, chaves como segredo
```

## 5. Primeiros passos depois do perfil

1. "montar perfis" (`metodo/plataformas.md`) se as contas não estão prontas. Reserve o mesmo @ em todas no mesmo dia.
2. Identidade visual e prompts de imagem: `metodo/identidade-visual-prompts.md`.
3. "nova série": `metodo/formato-serie.md` e o template da bíblia.

Primeiro episódio em 1 dia é possível com a série já aprovada. Na nuvem, conte mais tempo de render.
