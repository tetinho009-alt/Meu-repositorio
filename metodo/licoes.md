<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Lições que viraram regra

Cada regra aqui custou um vídeo refeito ou alcance perdido em canais reais. Valem para todo estilo. As que dá para
conferir por código estão na trava antes do render (`kit/qa/antes_do_render.py`); as outras são portões seus.

## Retenção

1. **O vídeo se explica em 3 segundos para um estranho.** No caso real, 75% das pessoas saíram em 10 s quando os 10
   s iniciais eram só explicação. Abra com a imagem mais forte (nojenta, absurda, a ameaça acontecendo) e uma frase
   que conta a premissa inteira.
2. **Nunca abrir com "ontem", "parte 4", "final" ou placar.** Quem chega de fora não sabe o que é. Na parte 2 em
   diante, o placar entra **depois** do gancho, perto dos 10 s.
3. **Uma frase, uma imagem.** Imagem nova a cada 2 a 4 s. Nada parado: câmera que aproxima devagar, tranco de zoom
   no corte, partículas no fundo.
4. **Pergunta aberta no meio.** O ponto de maior retenção é logo depois de uma pergunta sem resposta. É ali que vai
   a chamada do produto, se houver (uma vez, só na voz, ligada ao tema).
5. **Fim visual.** O episódio termina numa imagem que dá vontade de saber o próximo, não numa frase de resumo.
6. **Montagem de conserto e mecânica repetida derrubam.** Três cenas iguais seguidas (ex.: flexão, flexão,
   flexão) é onde a curva cai.

## Voto da parte 2

7. **Voto entre dois problemas diferentes**, nunca entre dois jeitos de fazer a mesma coisa.
8. **O que venceu dá certo e fica.** O "quase" do fim vem de outro problema. Desfazer o que a galera escolheu
   frustra quem votou.
9. **Os dois caminhos existem antes do voto.** Escreva os dois para não precisar inventar depois.
10. **Placar real.** Nunca invente número de votos.

## Duração

11. Série com voto: **1:30 a 2:40** (miras 1:45 a 2:20). Acima de 3 min, o Instagram não recomenda para quem não
    segue. Os outros estilos têm a faixa na ficha (`metodo/estilos/README.md`).
12. **Tempo a mais vem de história** (mais viradas, mais respiro), nunca de fala esticada ou áudio desacelerado.

## Personagens e cenas

13. **Corpo primeiro, roupa por cima.** Todo boneco tem anatomia normal (coxa, joelho, braço que afina, cintura)
    e a roupa presa ao corpo; a forma da blusa nunca faz papel de tronco. Nada sensualizado: o público tem menor de
    idade.
14. **Pose nova passa por uma folha de 6 a 8 quadros em sequência** antes do render. Confira cotovelo (dobra para
    trás), joelho, braço erguido (o antebraço não pode inverter) e o tamanho da cabeça.
15. **Still de cada cena nova antes do render.** Render é caro; quadro parado mostra o erro em segundos.
16. **Cenário novo com o mesmo capricho dos antigos** (objetos, textura, sombra e luz) ou reaproveite um bom.
17. **Brilho de 4 pontas grande** atrás de gente vira sol de desenho infantil e lembra símbolo político. Use halo
    redondo.

## Voz

18. **Pronúncia:** termo em inglês passa pela base (`kit/voz/pronuncia.json`, aplicada sozinha em toda voz). Termo
    que não está na base sai da fala: reescreva ("aplicativo" em vez de "app") e mostre o nome só na tela.
19. **Número por extenso na fala**, em algarismo na tela.
20. **Nunca cortar no meio da palavra.** O kit grava uma tomada por bloco (cartelas) ou corta na pausa real
    (séries), apara a -50 dB com folga e rampa, e trava o render se uma emenda cair em cima de fala.
21. **Transcreva antes do render.** A voz às vezes engole ou repete um trecho; a trava compara a voz com o roteiro e
    avisa abaixo de 85% de semelhança. Ouça as emendas de fone: a transcrição não acusa estalo.
22. **Voz escolhida no episódio 1 vale até o fim da série.** Voz provisória não vai ao ar.

## Imagem e render

23. **Fundo escuro, cor da marca só como brilho**, palavra-chave com brilho, conteúdo no meio da tela (fora da
    faixa de cima, da de baixo e da coluna da direita, que a interface das redes cobre).
24. **60 fps com placa de vídeo, 30 na nuvem.** Borrão de movimento (blur por subquadros) só com placa.
25. **Disco:** confira o espaço antes do render (a trava para abaixo de 5 GB e avisa abaixo de 30 GB). Depois do
    vídeo aprovado, apague quadros e testes do episódio; nunca o roteiro, o áudio aprovado ou o vídeo final.

## Redes (o que derruba a distribuição)

26. Nada de "ganhe dinheiro", "renda extra", "lucre", "fature", "fique rico", promessa de views ou de seguidores,
    na tela, na voz, na legenda ou na capa.
27. Nada de isca: "comenta QUERO", "manda pra 5 amigos", "marca alguém", "me chama na DM". O voto que decide a
    história é legítimo; o pedido sem ligação com o conteúdo, não.
28. Nenhum link, domínio ou @ de outra conta na legenda, no comentário fixado ou na capa. Marca d'água de outro
    aplicativo também derruba.
29. Rótulo de IA ligado quando a voz é sintética. No máximo 2 posts por dia na mesma conta.

## Gasto

30. **Toda geração paga só com o "pode" do usuário**, depois de mostrar a estimativa. Nada de teste, amostra ou
    tomada extra que ele não pediu. Roteiro conferido antes da voz: voz gerada em cima de roteiro errado é crédito
    jogado fora.
