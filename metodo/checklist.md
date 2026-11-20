<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# 12 · Checklist: portão de qualidade

Rode inteiro antes de capa, post e publicação. **Um item reprovado volta para a etapa dele**; não se publica "quase".
Cada regra nasceu de um episódio real reprovado, apagado ou refeito. Confira cada item na grade de 2 s, nos
quadros-marco e no áudio, e mostre ao usuário os itens com evidência (tempo do vídeo).

O que dá para conferir por código já vem conferido pela trava antes do render (`kit/qa/antes_do_render.py`). As
lições por trás de cada item estão em `metodo/licoes.md`. Os estilos de cartela (`metodo/estilos/`) usam só as
seções que valem para eles (sem personagem, a seção B não se aplica).

## A. Roteiro e história

1. [ ] Quadro 0 já é a anomalia, com texto grande e voz dizendo o que não devia acontecer, sem título antes. *O
   quadro 0 é a miniatura e a decisão de quem rola o feed.*
2. [ ] Nada de "PARTE N", "FINAL" ou placar nos primeiros segundos; o placar da parte anterior entra depois do
   gancho, perto dos 10 s. *Quem chega de fora pula o que parece continuação; um episódio que abriu com "Parte 4" teve
   45% de pulo.*
3. [ ] Lugar e cotidiano reconhecíveis pelo seu público. *Premissa genérica foi reprovada; o familiar assusta mais.*
4. [ ] Nada copiado de outro canal: história, personagem, música, frase ou assinatura de tela. *Cópia é não original
   para a plataforma e para o público.*
5. [ ] Cartão "REGRA N" com a regra nova. *Regra vira conversa e cobrança de coerência.*
6. [ ] Ameaça mostrada só até onde a tabela de revelação permite. *Mostrar cedo mata a curiosidade da série.*
7. [ ] Semente do mistério plantada e anotada na bíblia. *Pista sem registro é esquecida no episódio que paga.*
8. [ ] Desfecho do voto anterior aplicado e coerente com a marca. *O público confere se o voto valeu.*
9. [ ] Roteiro aprovado pelo usuário antes da voz. *Voz gerada antes da aprovação é crédito jogado fora.*

## B. Personagens

10. [ ] Elenco igual ao do EP1 (rosto, cabelo, roupa, cores). *Personagem que muda parece outra série.*
11. [ ] Personagem com roupa, cabelo e pele; objetos com acabamento. *Boneco simples demais lê como protótipo.*
12. [ ] Cabelo preso à cabeça e coerente com o personagem; nada de mecha solta balançando como mola. *Cabelo errado
    já derrubou um episódio publicado.*
13. [ ] Escala certa: adulto ≈ 0,8 da porta, criança ≈ 0,55, objeto na escala da mão. *Escala errada denuncia o
    cenário.*
14. [ ] Animal no traço do elenco, cabeça ligada ao corpo, patas proporcionais. *Bicho com cabeça solta foi
    reprovado.*
15. [ ] Ameaça com os traços fixos da bíblia (olho, sorriso, postura) e nada gráfico. *Reconhecível sem sangue.*
16. [ ] Multidão vindo na direção da câmera, nunca de costas (se o boneco só tem vista de frente). *Boneco de frente
    andando "de costas" quebra a ilusão.*
16a. [ ] Pele e tecido: suor, lágrima e sujeira ficam NA PELE e seguem a cabeça (desenhados com a matriz da parte
    `cabeca` do rig, testa abaixo da linha do cabelo, e o cabelo redesenhado por cima). Gota de suor com a ponta em
    cima e redonda embaixo, cor da pele com brilho pequeno, nunca losango branco. Coberta e roupa de cama envolvem o
    corpo com volume e dobras, a borda abraça a cintura, os braços ficam por cima e o tecido afunda onde algo apoia;
    no close a coberta para no peito. *Suor solto parece purpurina; coberta chapada parece um bloco colado.*

## C. Cena e câmera

17. [ ] Todo objeto desenhado na ordem da própria profundidade. *Item atrás do muro errado derrubou um episódio.*
18. [ ] Objeto na mão preso à mão pelo rig. *Celular flutuando derrubou um episódio.*
19. [ ] Ao mexer o corpo, tudo que é do corpo vai junto. *Parte que fica parada denuncia o recorte.*
20. [ ] Nada atravessando grade, portão ou parede. *Personagem "bugado" atrás do portão foi apontado na hora.*
21. [ ] Pé no chão com sombra de contato; pé de apoio não desliza. *Pé flutuando tira o peso do personagem.*
22. [ ] Luz motivada: borda acesa só do lado da fonte, personagem nunca mais claro que a fonte. *Luz incoerente parece
    colagem.*
23. [ ] Sem tangente: cabeça e mão longe da borda do quadro e de batentes (~1/10 da tela). *Encostar na borda dá
    sensação de erro.*
24. [ ] Cenário cheio e com textura, lugar reconhecível. *Fundo vazio com dois objetos não passa.*
25. [ ] Corte a cada 2 a 4 s; plano parado com push-in. *Plano parado demais perde o público.*
26. [ ] Plano gerado por IA (se houver) com a paleta da série e sem marca d'água. *Plano destoante denuncia a
    colagem.*

## D. Animação

27. [ ] Ninguém parado: respiração, piscar irregular a cada 2 a 5 s, micro-movimento. *Boneco estático parece imagem
    travada.*
28. [ ] Boca só se mexe durante a fala e fecha entre frases. *Boca fora de tempo é o erro mais visível.*
29. [ ] Olhar com alvo: os dois olhos no mesmo ponto; cabeça segue com 3 a 5 quadros de atraso. *Olhar perdido mata
    a atuação.*
30. [ ] Pose assimétrica, expressão pela sobrancelha, reação 4 a 6 quadros depois do estímulo. *Simetria e reação
    instantânea parecem robô.*
31. [ ] Movimento com ease, nada linear. *Linear parece máquina.*

## E. Voz e áudio

32. [ ] Voz em pt-BR nativo, sem sotaque de outro país nem intensidade caricata. *Vozes assim foram reprovadas de
    cara.*
33. [ ] Voz igual à do EP1 (mesmo modelo, mesma voz). *Troca de voz quebra a série.*
34. [ ] Nenhuma tag de direção lida em voz alta. *Defeito comum, pego só ouvindo ou transcrevendo.*
35. [ ] Ritmo ajustado na síntese, sem áudio acelerado depois. *Acelerar deixa a voz metálica.*
36. [ ] Prévia de voz ouvida pelo usuário de fone. *Defeito de voz não aparece no alto-falante do notebook.*
37. [ ] Trilha presente do começo ao fim. *Faltar trilha foi apontado como defeito.*
38. [ ] Ducking: música e efeitos baixam quando a voz fala; som que compete com uma fala some naquela fala. *Fala
    encoberta perde a história.*
39. [ ] Silêncio total de ~1 s no clímax. *Silêncio é o susto mais forte.*
40. [ ] Master **estéreo 48 kHz**. *Mono ficou mudo no celular.*
41. [ ] −14 LUFS integrados, pico −1,5 dBTP, conferido por medição. *Volume errado faz a rede baixar ou distorcer.*
42. [ ] Cada som com licença registrada em `licencas.txt`; nada baixado do YouTube. *Crédito não é licença; Short
    com reivindicação acima de 1 min é bloqueado.*

## F. Tela, legenda e marca

43. [ ] Todo texto importante dentro de x 120–900, y 280–1420. *Fora disso a interface das redes cobre.*
44. [ ] Legenda palavra a palavra, caixa alta, até 2 linhas, contorno e sombra logo abaixo. *Sombra deslocada foi
    apontada como bug.*
45. [ ] Legenda some durante a tela de voto. *Texto em cima de texto ninguém lê.*
46. [ ] Sticker ou mascote só no pedido de seguir e no fecho. *Sticker em toda cena foi reprovado.*
47. [ ] "FICÇÃO" no selo do vídeo e em todo alerta na tela; nenhum nome de órgão público ou emissora real.
    *Alerta fictício parecido com real é desinformação.*
48. [ ] Cores das opções iguais às do canal em todos os episódios. *Cor trocada confunde quem acompanha.*

## G. Voto

49. [ ] Duas opções curtas e opostas, mostradas na tela com número e palavra. *Três opções dividem; sem número fica
    lento de responder.*
50. [ ] Pergunta aberta como escolha da história; nenhum "comenta X ou Y", "curte", "compartilha", "marca".
    *Comando é engagement bait e tira o vídeo da recomendação.*
51. [ ] Fecho com "VOCÊS DECIDEM" ou "O que vocês escolherem vira a parte dois". *Diz o que o voto faz sem mandar
    comentar.*
52. [ ] Um único pedido de seguir, antes do clímax, separado do voto. *Pedido duplo ou colado ao voto vira
    manipulação.*
53. [ ] Tela de voto entre 8 e 12 s, nunca mais de 15. *Tela parada longa derruba a retenção.*
54. [ ] Palavras aceitas de cada opção escritas antes de publicar. *Apuração sem regra prévia é contestada.*
54a. [ ] Apuração renderizada por último: o episódio inteiro fica pronto antes, e só minutos antes de postar a
    contagem é relida, renderizada e emendada, com a hora dessa leitura na tela. *Número velho na tela é contestado
    nos comentários.*
54b. [ ] Chamada falada do comentário fixado (se `cta.chamada_fixado` estiver preenchida): uma fala curta do
    narrador logo depois do gancho, nunca em cima de uma virada, só voz e legenda, e a mesma frase numa linha da
    legenda do post de cada rede. *Aponta para o fixado sem pedir comentário.*

## H. Público e segurança

55. [ ] Nada gráfico: sem sangue, ferida, corpo, tortura; quem é levado some. *Gráfico sai do For You e ganha
    restrição de idade.*
56. [ ] Criança em cena nunca ferida nem ameaçada de forma gráfica; nada infantil em título, capa ou hashtag.
    *Política de segurança infantil do YouTube e ECA Digital.*
57. [ ] Religião e deficiência tratadas com respeito. *Ofensa vira denúncia.*
58. [ ] Rótulo de IA decidido pela tabela de `metodo/seguranca.md`. *Sem rótulo onde é exigido, o vídeo pode ser
    removido.*

## I. Arquivo final

59. [ ] 1080x1920, 60 fps com placa de vídeo (30 sem placa ou na nuvem), H.264, AAC 48 kHz estéreo, `+faststart`,
    na faixa do estilo (série com voto: 1:30 a 2:40; os outros na ficha do estilo). Cauda, cartões e trechos emendados na mesma taxa do episódio. *Especificação comum a todas as redes.*
60. [ ] Sem marca d'água de app. *Instagram não recomenda vídeo com marca de outro app.*
61. [ ] Grade de 2 s revista: nada flutuando, nada cortado, nada atrás do muro errado. *É onde os erros aparecem
    juntos.*
62. [ ] Prévia vista pelo usuário no celular, de fone. *O público assiste assim.*
63. [ ] "Parece produção ou protótipo?" Resposta: produção. *Protótipo publicado custa o alcance do episódio.*

## J. Antes de publicar

64. [ ] Opções da capa = opções da tela = opções do texto. *Divergência confunde a apuração.*
65. [ ] Texto por rede dentro dos limites (hashtags: IG 5, TikTok 3 a 5, YouTube 3). *Excesso é ignorado ou
    penalizado.*
66. [ ] Arquivo com nome novo se for nova versão. *Cache serve a versão velha.*
67. [ ] Confirmação explícita do usuário para publicar. *Publicação é irreversível na prática.*
