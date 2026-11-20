<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# 03 · Voz

Carregue depois do roteiro aprovado.

## 1. Opções por pilha

| Pilha | Ferramenta | Qualidade em pt-BR | Licença comercial | Tempo por palavra |
|---|---|---|---|---|
| Zero | **Gemini TTS** (`gemini-3.8-flash-tts`, Google AI Studio, plano grátis com limite por dia) | Boa a muito boa, aceita estilo ("sussurrado", "animado") | O Google não reivindica o áudio; no plano grátis ele usa o texto enviado para melhorar os produtos dele (conferido em 06/11/2026) | Não; o `alinhar.py` (Whisper) faz |
| Zero | **Azure AI Speech F0** (vozes neurais Antonio, Francisca, Thalita) | Boa, pouca emoção | Sim, com conta Azure (confirmar o F0 nos termos atuais) | Sim (evento WordBoundary) |
| Zero | Kokoro-82M (`pf_dora`, `pm_alex`) | Média, prosódia irregular | Sim (Apache-2.0) | Não; alinhar com o roteiro |
| Zero | Piper `pt_BR-faber` | Baixa a média, robótica para drama | Verificar a licença da voz | Não; alinhar |
| Criador | **ElevenLabs Starter** (US$ 6, 30 mil créditos) | Excelente, aceita tags de emoção | Sim a partir do Starter | Sim (endpoint com timestamps) |
| Estúdio | **ElevenLabs Creator** (US$ 22, 121 mil créditos) | Excelente | Sim | Sim |

**Fora do pacote:**
- **edge-tts**: usa um serviço do navegador Edge sem autorização comercial clara e pode parar sem aviso. Para as
  mesmas vozes com licença, use o Azure TTS.
- **XTTS-v2 e F5-TTS pt-BR**: licença não comercial.
- **Plano grátis da ElevenLabs**: não dá direito comercial.
- **Programas de voz local com janela (ex.: VoiceStudio)**: o programa pode ser livre, mas o modelo de voz padrão
  costuma ter licença não comercial (CC-BY-NC). Só para teste, a menos que a licença de cada modelo usado permita.

## 1a. Como ligar a voz

1. **Conector da ElevenLabs (por permissão, sem chave)**: quando a IA tem o conector oficial ligado (no Claude:
   Configurações → Conectores → ElevenLabs → Conectar, e o usuário autoriza na tela da ElevenLabs). Nada de chave
   no computador.
2. **Janela da chave** (`python chave.py`): quando não há conector (Codex, ChatGPT, Gemini) ou quando o kit precisa
   gravar sozinho em lote, como no `falas.py`.
3. **Voz grátis do Google (Gemini TTS)**: `python chave.py --qual gemini` abre a janela; o usuário entra no Google
   AI Studio com a conta do Google, clica em "Get API key" e cola a chave lá. Vozes: Charon (grave), Orus (firme),
   Puck (animada), Kore (feminina firme), Aoede (feminina leve), Leda (feminina jovem). O jeito de falar vai em
   `voz.gemini.estilo` no `kit/config.json` (nunca no texto, que é lido palavra por palavra). Quando o limite do dia
   acaba, o kit espera e tenta de novo; se não voltar, troque para o Kokoro naquele vídeo.
4. **Kokoro no computador**: grátis e comercial, sem internet e sem limite, para quem não quer depender do Google.

### Voz pelo conector

1. Busque a voz com a ferramenta de listar vozes do conector: idioma `pt`, sotaque brasileiro quando houver, e o
   gênero, a idade e o jeito do canal. Grave o voice_id escolhido em `kit/config.json` (`voz.elevenlabs.voz`) e em
   `canal/canal.md`: é a mesma voz até o fim da série.
2. Antes de gerar, peça a estimativa de créditos (a geração tem a opção de só estimar) e mostre ao usuário.
3. Gere **uma tomada por fala**, com o mesmo modelo e as mesmas tags de direção do personagem, e só 1 variação por
   fala (variação extra custa crédito). Para as amostras da instalação, aí sim 3 variações ou 3 vozes.
4. Espere a geração terminar pela ferramenta de status e salve cada mp3 na pasta `audio/` do episódio com o nome da
   fala (`01_narrador.mp3`, `02_julia.mp3`), na ordem do `falas.json`. Se o conector não devolver o arquivo para
   baixar, mostre o link da geração ao usuário e passe para a janela da chave neste episódio.
5. O conector não devolve o tempo de cada palavra: rode `python alinhar.py` em cada fala (seção 4, item 2) antes da
   trilha.
6. Cada geração pelo conector cria um fluxo no painel da ElevenLabs do usuário. É normal; avise uma vez.
- Modelos que soaram com sotaque de Portugal ou intensos demais em testes reais (Qwen3-TTS, Chatterbox) não são
  recomendados para narração pt-BR.

## 2. Direção de voz

| Papel | Direção | Por quê |
|---|---|---|
| Narrador | Grave, contido, pausado, sem teatralidade | Terror narrado que interpreta demais vira paródia |
| Ameaça que imita alguém | Calorosa, mas com pausa no lugar errado, sussurro, calma demais | O medo vem do quase certo |
| Idoso / relógio da série | Rouco, sussurrado, lento | Cria a marca sonora do "Faltam N" |
| Alerta de sistema | Neutra, com filtro de alto-falante de celular no mix | Soa como celular de verdade |
| Nomes sussurrados | 2 vozes, uma em cada ouvido | O fone vira parte da história |
| Narrador do POV ("você") | O mesmo grave e contido, sem adjetivo de gênero; uma voz extra no máximo, escolhida em 3 testes (`metodo/formato-pov.md`, seção 5) | Quem assiste é o protagonista |

Tags no ElevenLabs (v3 em diante): `[slowly]`, `[softly]`, `[whispers]`, `[pause]`, `[long pause]`, `[raspy]`.
As tags vão no texto enviado à geração, nunca no `narrador.txt`.

## 3. Regras de gravação

1. **Uma tomada por fala, cada personagem com a sua voz** (`kit/falas.py`): é o jeito do estúdio real no ElevenLabs.
   Refazer uma fala não mexe nas outras e cada mp3 já vem com o tempo de cada palavra. Mantenha a mesma voz, o mesmo
   modelo e as mesmas tags de direção do personagem em todas as falas dele.
2. **Narração longa e contínua** (um narrador lendo vários blocos seguidos, ou voz local como Kokoro): numa geração
   só, depois cortada pelos tempos (`kit/narrar.py` + `kit/alinhar.py`). Se o ElevenLabs der 429 no meio, junte o que
   falta num pedido só e corte depois pelo tempo de palavra.
3. **Ritmo se ajusta na síntese**, nunca acelerando o áudio pronto (atempo): acelerar depois deixa a voz metálica.
4. **Pausas entre blocos (0,4 a 1,6 s) se decidem na montagem do som**, não na voz. Dá controle fino sem regravar.
5. **Escolha a voz no EP1 e trave.** Trocar voz ou motor no meio da série quebra a continuidade igual a trocar o
   boneco.
6. **Estime antes de gerar.** Narração de 80 s ≈ 1.200 caracteres ≈ 1.200 créditos na ElevenLabs; um episódio com
   personagens fica em ~1.300 a 2.000 créditos com 1 regravação.
7. **Um pedido por vez.** Pedidos seguidos geram erro 429 (limite) e cada nova tentativa prolonga o bloqueio. Depois
   de um 429, espere alguns minutos antes de tentar de novo. No modo agente o kit faz essa espera (ver
   `kit/README.md`).
8. **Confira que nenhuma tag foi lida em voz alta.** Transcreva o áudio e compare com o texto; "colchete sussurra"
   falado é defeito comum.
9. **Voz provisória não vai ao ar.** Se a voz boa não chegou, espere; publicar com a provisória e trocar depois
   quebra a série.
10. **Não clone voz de pessoa real** sem termo de consentimento escrito. Vozes de figuras públicas são bloqueadas
    pelas próprias ferramentas e a voz é protegida por lei.

## 4. Tempo de cada palavra (para a legenda)

Do melhor para o pior:
1. Timestamps do próprio TTS (ElevenLabs com timestamps, Azure WordBoundary).
2. Alinhamento forçado com o texto do roteiro (o texto é conhecido, não precisa adivinhar).
3. Transcrição com faster-whisper ou WhisperX, alinhada por sequência ao texto do roteiro, para a legenda usar a
   grafia do roteiro e não a do reconhecimento.

Saída esperada: lista `{bloco, palavra, ini, fim}` em segundos. A montagem sincroniza tudo a esse arquivo, nunca a
tempos digitados à mão.

Falas de personagem também precisam de tempo por palavra; distribuir a legenda em tempo uniforme fica fora de
sincronia.

## 5. Portão da voz

Junte narração e falas num arquivo de prévia (normalizado em −16 LUFS), mande ao usuário e peça que ouça **de fone**.
Só siga com "aprovado". Registre no `roteiro.md` qual voz, modelo e take foram usados; sem isso o EP2 sai com outra
voz.
