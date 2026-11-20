<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Exemplo comentado · A Balsa das Duas · Parte 1 · "Ninguém desceu"

Série de demonstração, escrita para este pacote: não foi publicada e não tem números de alcance. Serve para mostrar o
método aplicado do começo ao fim (ficha, beats com tempo, arquivos, portões) e os erros que ele pega antes de ir ao
ar. Use como referência de estrutura; a história é livre para você mudar, mas o ponto é criar a sua.

## 1. Ficha

| Item | Valor |
|---|---|
| Série | Mistério no litoral, 5 episódios, cada um termina num voto |
| Frase da série | "Toda noite, às duas, a balsa atraca vazia. Quem sobe nela não volta igual." |
| Gancho fixo | A buzina da balsa no escuro, antes de qualquer imagem |
| Lugar | Vila de pescador com um píer de madeira e uma balsa velha que não devia mais funcionar |
| Duração-alvo | 74 s (episódio curto de demonstração; a série de verdade mira 1:45 a 2:20) |
| Arquivo | 1080x1920, 60 fps, H.264, AAC 48 kHz, -14 LUFS |
| Voto | 1 · SOBE (cor 1) · 2 · FICA NO PÍER (cor 2) |
| Personagens | Nina (protagonista, 19 anos, filha do balseiro), Seu Lauro (o balseiro, sumido há um mês) |

Sementes plantadas neste episódio: o boné do pai pendurado do lado de DENTRO da cabine; a âncora que está seca;
um vulto na janela da cabine por 6 quadros.

## 2. Beat a beat, com tempos

| Tempo (s) | Beat | Tela | Som | Por que este beat existe |
|---|---|---|---|---|
| 0,0–2,0 | Gancho | Preto; texto grande "ELA NÃO DEVIA ESTAR AQUI" | Buzina grave, longe, e mais nada | Gancho no quadro 0: texto e som dizem o que não devia acontecer, antes da primeira imagem |
| 2,0–7,5 | Evento-assinatura | A balsa surge da neblina, luzes acesas, sem ninguém no convés; título "A BALSA DAS DUAS · Parte 1" | Motor parado; só a água batendo | A promessa da série cumprida em 5 s |
| 7,5–15,0 | Situação | Nina no píer, de lanterna | "Meu pai sumiu com essa balsa faz um mês. Hoje ela voltou." | Narração só depois do impacto |
| 15,0–22,0 | Semente | Close no boné do pai do lado de dentro do vidro da cabine | "O boné dele tá lá dentro. Ele nunca tirava esse boné." | Planta o mistério sem explicar |
| 22,0–29,0 | Escalada | Nina encosta na rampa; a âncora está seca, com areia | "A âncora tá seca. Como se nunca tivesse tocado a água." | Detalhe concreto que o público confere e comenta |
| 29,0–30,2 | Silêncio | A luz da cabine apaga | **Silêncio absoluto** | O corte do som assusta mais que um estrondo |
| 30,2–38,0 | Relance | A luz volta; por 6 quadros um vulto de boné na janela | Rangido da madeira | Rápido demais para ter certeza: motivo para rever |
| 38,0–45,0 | Regra | Placa velha no píer: "BALSA DAS 2H · SÓ IDA" | "Na vila todo mundo sabe a regra. A balsa das duas é só de ida." | A regra da série vira cartão fixo |
| 45,0–48,0 | Pedido de seguir | Pílula "+ SEGUIR" | "Segue pra saber o que tem na cabine." | Um pedido só, no meio do vídeo, com o público preso |
| 48,0–58,0 | Clímax | A rampa desce sozinha até os pés de Nina | Buzina perto, alta, e corte seco pro silêncio | Sem nada gráfico: o convite assusta mais que a ameaça |
| 58,0–64,0 | Virada pessoal | Uma voz de dentro da cabine | "Nina... sobe." | A ameaça chega na protagonista pelo nome |
| 64,0–74,0 | Voto | Nina pequena no píer; tela "VOCÊS DECIDEM" a partir de 65 s | "O que a Nina faz? Sobe na balsa ou fica no píer? O que vocês escolherem vira a parte dois." | Pergunta aberta, narrada, com as duas opções em cor; 9 s de tela de voto |

## 3. Arquivos do episódio

```
series/a_balsa_das_duas/
  SERIE.md                 bíblia: regra, mistério e resposta, 5 episódios, sementes e finais
  ep1/
    roteiro.md             tabela Plano | Narração | Som | Na tela, com as sementes
    falas.json             uma tomada por fala (narradora e a voz da cabine)
    audio/                 tomadas, tempos por palavra, narrador.mp3, mix
    quadros/ folha_ep1.jpg folha de quadros-marco
    qa_grade.jpg           grade de 2 s
    capa_ig.jpg capa_tiktok.jpg capa_youtube.jpg
    legenda.txt            texto do post de cada rede
```

## 4. O que o método pegou antes de publicar

Na primeira versão do roteiro e da montagem, estes pontos não passaram nos portões:

| Primeira versão | Como ficou | Por quê |
|---|---|---|
| "Comenta SOBE ou FICA que a mais votada vira a parte 2" | "O que a Nina faz? Sobe na balsa ou fica no píer?" + tela "VOCÊS DECIDEM" | Pedir para comentar uma palavra específica é isca de engajamento; as redes rebaixam |
| "Segue, curte e compartilha" no fim | Um pedido só, o de seguir, no meio | Vários pedidos juntos também é isca |
| Música de um vídeo do YouTube "com crédito" | Trilha e efeitos gerados por código | Crédito não é licença; no Shorts, uma reivindicação bloqueia o vídeo |
| Legenda falada perto do pé da tela | Base da legenda acima da faixa da interface | Os botões das três redes cobrem a faixa de baixo |
| 96 s | 74 s | episódio curto de demonstração; numa série de verdade, mais viradas levam a 1:45 a 2:20 |
| A fala "Nina... sobe." cortada no "e" | A tomada inteira, até o fim do som | O fim da fala é o fim do som, não da palavra; o `qa/voz.py` reprova o corte seco |
| Nina andando com as duas mãos atrás das costas | Braço solto, mão do lado de fora da coxa | O `qa/maos.py` reprova mão dentro da silhueta do corpo |
| A neblina e o galho do primeiro plano parados enquanto a câmera desce | Primeiro plano ancorado no mundo (`ref`) | O `qa/espaco.py` reprova o que fica grudado na tela com a câmera andando |

## 5. O que fica de lição

1. **Grade de 2 s antes de qualquer prévia.** Objeto flutuando, mão no lugar errado e ordem de desenho aparecem na
   grade em 1 minuto; no ar, custam um vídeo apagado.
2. **Um portão por vez.** Roteiro aprovado antes da voz, voz aprovada antes da animação: refazer roteiro depois da
   animação custa o dobro.
3. **Sementes anotadas no `SERIE.md`.** O boné, a âncora seca e o vulto só funcionam se voltarem nos episódios
   seguintes.

## 6. O voto e os números

Este é um exemplo de demonstração: não há placar nem métricas. No seu canal, registre aqui o placar real, a opção
vencedora e como ela entrou na Parte 2, e acompanhe as métricas de `metodo/metricas.md`. Resultado de um perfil não
garante resultado de outro: o que o exemplo mostra é o processo.
