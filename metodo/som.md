<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# 04 · Som

Carregue depois da voz aprovada. Faltar trilha é defeito; som sem licença é risco de bloqueio.

## 1. De onde vem o som (só com licença)

| Origem | Pilha | Licença | Cuidado |
|---|---|---|---|
| Sons feitos por código (drone, toque grave, alerta de dois tons, coração, estalo de lâmpada, notificação, ruído digital) | Todas no modo agente | Sua | Melhor opção: zero risco e assinatura própria |
| Freesound filtrado por **CC0** | Zero, Criador | Livre, sem crédito | CC-BY exige crédito; **CC-BY-NC não serve**. Guarde print da licença |
| Pixabay (sons e música) | Zero, Criador | Pixabay License | Evite faixas com selo "Content ID Registered": geram reivindicação mesmo licenciadas |
| ElevenLabs Sound Effects | Criador, Estúdio | Comercial nos planos pagos | Gerações curtas (~22 a 30 s); confira loop |
| Mirelo (efeito por texto ou sincronizado ao vídeo) | Estúdio | Plano pago; o grátis tem marca d'água | Confirme os termos comerciais antes de vender o vídeo |
| YouTube Audio Library | Todas | Licença do YouTube | Serve ao YouTube; confira o uso fora dele |
| Eleven Music ou outra trilha gerada | Estúdio | Comercial nos pagos, com exclusões | Música gerada por IA exige rótulo no YouTube |

**Nunca:** baixar áudio do YouTube ou de qualquer vídeo, mesmo com crédito na legenda. Crédito não é licença. No
Shorts, vídeo acima de 1 min com qualquer reivindicação fica bloqueado no mundo todo. Acelerar ou filtrar a faixa
não engana a detecção.

**Registro obrigatório:** ao lado do master, um `licencas.txt` com cada som, origem, licença e link ou print. É o
que você mostra numa contestação.

## 2. Camadas do mix

| Camada | Nível relativo | Função |
|---|---|---|
| Voz (narração e falas) | Referência, ganho ×1,1 | Sempre inteligível |
| Cama (drone escuro, sem melodia marcada) | Baixa, ~−20 dB abaixo da voz | Tensão contínua |
| Ambiente (vento, grilos, bairro) | Baixo | Dá lugar à cena |
| Efeitos pontuais (porta, rosnado, notificação) | Médio, no tempo da imagem | Pontuam a ação |
| Stinger (golpe no clímax) | Alto, curto | Susto |
| **Silêncio** | Zero absoluto em tudo | O efeito mais forte do terror: use 1 s no clímax e onde a história pede (vídeo mudo, luz que apaga) |

## 3. Regras de mixagem

1. **Ducking:** quando a voz fala, todo o resto baixa (~60%). Receita usada: envelope da voz (média de 0,1 s) →
   máximo móvel de 0,6 s → suavização de 0,1 s → resto × (1 − 0,6 × fala).
2. **Som que compete com a fala some naquela fala.** Um carro de som tocando enquanto alguém fala vira ruído.
3. **Estéreo é narrativa:** nomes sussurrados entrando um em cada ouvido, notificação alternando lados, voz passando
   de um ouvido pro outro. Por isso o vídeo pede "USE FONE".
4. **Monte a linha do tempo a partir dos tempos da fala**, não de segundos digitados. Gere um arquivo de linha do
   tempo (eventos, início e fim de cada bloco, tempo do voto, tempo do detalhe escondido, cortes). O vídeo sincroniza
   a esse arquivo.
5. **Limitador suave no fim** para não estourar.

## 4. Master (obrigatório)

- **Estéreo, 48 kHz.** Um vídeo em mono ficou mudo em players de celular; desde então tudo sai estéreo.
- **−14 LUFS integrados, pico −1,5 dBTP.**

Comando de referência (ffmpeg, instalado pelo usuário):

```
ffmpeg -i mix.wav -af loudnorm=I=-14:TP=-1.5:LRA=11 -ar 48000 -ac 2 mix_norm.wav
ffmpeg -i mix_norm.wav -af ebur128=peak=true -f null -
```

O segundo comando mostra o volume integrado e o pico; confira antes de montar o vídeo. No modo agente o kit faz as
duas coisas (ver `kit/README.md`).

