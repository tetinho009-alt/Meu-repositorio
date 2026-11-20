<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Estudar vídeos de referência

Viu um vídeo que deu certo e quer entender por quê? O estúdio transcreve, tira o raio-x e devolve a fórmula: o
esqueleto do vídeo, com os tempos, para você usar no seu com as suas palavras.

No painel, abra **Estudar vídeos**. Pela IA, a partir de `kit/`:

```
python -m estudo <link do YouTube ou do Instagram, ou o caminho do vídeo>
python -m estudo --buscar "assunto" --curtos
python -m estudo --listar
python -m estudo --nicho
```

## De onde vem o texto

| Vídeo | Como o estúdio transcreve | Quanto leva |
|---|---|---|
| YouTube com legenda (quase todos) | a legenda do próprio vídeo, no idioma falado | uns 5 segundos |
| Arquivo do computador, Instagram ou YouTube sem legenda | o Whisper, no seu computador | segundos por minuto de vídeo |

O Whisper usa a placa de vídeo NVIDIA quando ela está pronta (modelo maior, acerta nome e gíria). Sem ela, roda no
processador com um modelo menor, que funciona em qualquer notebook. Na primeira vez ele baixa o modelo (uns 460 MB,
ou 1,6 GB com placa) e o painel instala sozinho o que falta.

**Instagram e TikTok** às vezes não deixam baixar sem login. O estudo só abre conteúdo público e nunca usa login,
cookies ou a sua conta. Quando bloquear, baixe o vídeo pelo app (Salvar ou Baixar) e suba o arquivo.

## O que o raio-x mostra

- **Gancho:** quanto tempo até a primeira palavra e o que é dito nos 3 primeiros segundos. Acima de 1,5 s, a
  abertura é muda e depende só da imagem.
- **Viradas:** palavras de contraste e revelação ("mas", "só que", "de repente", "ninguém"), por minuto e onde caem.
  Trecho de mais de 15 s sem virada é onde a pessoa costuma sair.
- **Perguntas e chamadas:** em que segundo o vídeo pergunta algo a quem assiste ou pede para seguir, comentar,
  salvar ou ir ao link.
- **Palavras por minuto:** o ritmo da fala.
- **Blocos:** o vídeo dividido pelo que cada trecho faz (gancho, contexto, virada, item de lista, pergunta,
  chamada).
- **A fórmula:** os blocos viram um molde, com tempo e tamanho, sem nenhuma frase do original.

São contas sobre o texto falado: contam palavra, não entendem a imagem. Servem para comparar vídeos entre si, não
como nota.

## Estudo de nicho

Estude 3 ou mais vídeos do mesmo assunto e compare. O painel põe tudo lado a lado (views, likes, duração, gancho,
viradas, ritmo, formato) e mostra o que se repete em pelo menos 6 de cada 10. Um vídeo sozinho mostra um jeito de
fazer, não um padrão. Quando há views, ele também conta como os mais vistos diferem dos outros: isso descreve esses
vídeos, não garante resultado.

## Usar o formato num vídeo seu (para a IA)

O botão **Usar este formato** leva o molde para o "Fazer um vídeo". O pedido chega dizendo "siga o formato que
estudei" e aponta o arquivo do molde: o `molde.md` dentro de `canal/estudos/<id>/` (ou, no estudo de nicho, o
nicho.md da pasta canal/estudos). Ao receber esse pedido:

1. Leia o molde inteiro antes do roteiro.
2. Siga a estrutura: a ordem dos blocos, o tipo de gancho, onde caem as viradas e a pergunta, o ritmo.
3. Ajuste os tempos à duração do estilo escolhido (série de 1:30 a 2:40, explicativo de 40 a 65 s): mantenha as
   proporções (em % do vídeo), não os segundos exatos.
4. **Nunca copie frase, piada, bordão ou sequência de fatos do vídeo de referência**, nem abra a transcrição dele
   para "se inspirar no texto". O assunto e as palavras são do canal do usuário. Se o usuário pedir para regravar o
   texto de outro criador, explique em uma frase que isso é cópia (direito autoral e risco nas redes) e ofereça o
   molde.
5. As regras do kit continuam valendo por cima do molde: gancho no quadro 0, pergunta aberta sem isca de
   engajamento (`metodo/engajamento.md`) e as travas de `kit/qa/`.
