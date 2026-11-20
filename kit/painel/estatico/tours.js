/*! © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C */
/* Tour guiado do painel ("Me mostra como usa"), um por tela, mostrado pelo driver.js (vendor/).
   Regra fixa: toda mudança numa tela atualiza o tour dela aqui, no mesmo commit; mudou passo ou alvo, sobe a versao
   (quem já viu o tour antigo vê o novo uma vez). Cada passo aponta para um data-tour="<alvo>" escrito em painel.js
   ou index.html; texto em no máximo 2 frases. O montar.py reprova o pacote se uma tela não tiver tour, se um alvo
   não existir no código ou se um texto passar de 2 frases. Passo cujo alvo não está na tela naquele momento
   (ex.: só aparece com vídeo pronto) fica de fora sozinho. O conteúdo entre as chaves é JSON puro. */
window.TOURS_PAINEL = {
  "telas_sem_tour": {
    "arrumar": "O assistente da primeira vez já é guiado, uma pergunta por tela."
  },
  "telas": {
    "inicio": {
      "versao": 4,
      "passos": [
        {
          "alvo": "fazer",
          "titulo": "Comece por aqui",
          "texto": "Toque aqui para fazer um vídeo. A IA faz o vídeo no seu computador."
        },
        {
          "alvo": "videos",
          "titulo": "Seus vídeos prontos",
          "texto": "Quando a IA termina, o vídeo aparece aqui com a legenda de cada rede."
        },
        {
          "alvo": "problema",
          "titulo": "Se faltar algo",
          "texto": "Aqui o painel mostra o que falta e o botão que resolve."
        },
        {
          "alvo": "menu",
          "titulo": "Todas as telas",
          "texto": "No computador, todas as telas ficam neste menu. Ele fica sempre à vista."
        },
        {
          "alvo": "modo",
          "titulo": "Simples ou completo",
          "texto": "No simples, o menu mostra só o essencial. No completo, aparecem todas as telas."
        },
        {
          "alvo": "mais",
          "titulo": "Todo o resto",
          "texto": "No celular, as outras telas ficam aqui. E este tour também."
        }
      ]
    },
    "fazer": {
      "versao": 3,
      "passos": [
        {
          "alvo": "estilos",
          "titulo": "Escolha o estilo",
          "texto": "Cada um é um jeito de vídeo. Toque num deles e veja um exemplo de 10 segundos."
        },
        {
          "alvo": "assunto",
          "titulo": "Conte o assunto",
          "texto": "Uma frase basta. Pode ser do jeito que você fala."
        },
        {
          "alvo": "molde-fazer",
          "titulo": "Com o formato estudado",
          "texto": "O pedido leva a estrutura do vídeo que você estudou, nunca o texto dele. Toque em Tirar para fazer sem ela."
        },
        {
          "alvo": "copiar",
          "titulo": "O pedido pronto",
          "texto": "O painel monta o pedido pra você. Um toque e ele vai pra IA."
        },
        {
          "alvo": "copiar",
          "titulo": "É isso",
          "texto": "Toque no botão amarelo para começar."
        }
      ]
    },
    "estudar": {
      "versao": 1,
      "passos": [
        {
          "alvo": "estudo-link",
          "titulo": "Cole o link",
          "texto": "Cole aqui o link de um vídeo que deu certo, do YouTube ou do Instagram. Em segundos aparece como ele foi montado."
        },
        {
          "alvo": "estudo-arquivo",
          "titulo": "Ou suba o vídeo",
          "texto": "Se o Instagram ou o TikTok pedirem login, baixe o vídeo pelo app e suba o arquivo aqui. O estudo nunca usa a sua conta."
        },
        {
          "alvo": "estudo-buscar",
          "titulo": "Ache vídeos do nicho",
          "texto": "Escreva o assunto e o painel traz vídeos do YouTube sobre ele. Marque os que quer estudar de uma vez."
        },
        {
          "alvo": "estudo-andamento",
          "titulo": "Estudando",
          "texto": "Aqui aparece o que está sendo feito agora. Pode trocar de tela: o estudo continua."
        },
        {
          "alvo": "estudo-lista",
          "titulo": "Seus estudos",
          "texto": "Cada vídeo estudado fica aqui, com o tempo até a primeira fala e as viradas. Toque num deles para ver o raio-x."
        },
        {
          "alvo": "estudo-comparar",
          "titulo": "Ache o padrão",
          "texto": "Marque 3 ou mais vídeos do mesmo nicho e compare. Um vídeo só mostra um jeito, não um padrão."
        },
        {
          "alvo": "estudo-gancho",
          "titulo": "O gancho",
          "texto": "Quanto tempo o vídeo leva para falar e como ele abre. É o que segura a pessoa nos primeiros segundos."
        },
        {
          "alvo": "estudo-ritmo",
          "titulo": "O ritmo",
          "texto": "Viradas e palavras por minuto, perguntas e chamadas. Serve para comparar vídeos, não é nota."
        },
        {
          "alvo": "estudo-tempo",
          "titulo": "Onde cada coisa acontece",
          "texto": "Os tracinhos são as viradas, perguntas e chamadas. A faixa listrada é trecho longo sem virada, onde a pessoa costuma sair."
        },
        {
          "alvo": "estudo-formula",
          "titulo": "A fórmula",
          "texto": "O esqueleto do vídeo em passos, com o tempo de cada um. Nenhuma frase do vídeo original entra aqui."
        },
        {
          "alvo": "estudo-usar",
          "titulo": "Use no seu vídeo",
          "texto": "Este botão leva o formato para o Fazer um vídeo. A IA escreve um roteiro novo, com as suas palavras."
        },
        {
          "alvo": "estudo-blocos",
          "titulo": "Como ele é dividido",
          "texto": "Cada trecho do vídeo com o que ele faz. Leia para entender o jeito, não para copiar."
        },
        {
          "alvo": "estudo-transcricao",
          "titulo": "A transcrição",
          "texto": "Tudo o que é dito, com o segundo de cada trecho."
        },
        {
          "alvo": "nicho-tabela",
          "titulo": "Lado a lado",
          "texto": "Os vídeos comparados numa tabela: views, duração, gancho e ritmo."
        },
        {
          "alvo": "nicho-padrao",
          "titulo": "O que se repete",
          "texto": "Só entra aqui o que aparece em pelo menos 6 de cada 10 vídeos. O que muda fica separado."
        }
      ]
    },
    "rapido": {
      "versao": 1,
      "passos": [
        {
          "alvo": "rapido-redes",
          "titulo": "Tudo pra postar",
          "texto": "Cada rede tem o vídeo e a capa pra baixar e a legenda pra copiar. Baixe, copie e poste pelo app da rede."
        }
      ]
    },
    "meus": {
      "versao": 2,
      "passos": [
        {
          "alvo": "player",
          "titulo": "Seu vídeo",
          "texto": "Assista antes de postar. Cada rede tem a sua versão."
        },
        {
          "alvo": "redes",
          "titulo": "Escolha a rede",
          "texto": "Toque na rede onde você vai postar agora."
        },
        {
          "alvo": "baixar",
          "titulo": "Baixe o vídeo",
          "texto": "O vídeo e a capa vão pro seu computador."
        },
        {
          "alvo": "legenda",
          "titulo": "A legenda pronta",
          "texto": "Copie e cole na hora de postar."
        },
        {
          "alvo": "mudar",
          "titulo": "Quer mudar algo?",
          "texto": "Escreva o que mudar e mande pra IA."
        }
      ]
    },
    "problema": {
      "versao": 2,
      "passos": [
        {
          "alvo": "resumo",
          "titulo": "O que falta",
          "texto": "Aqui diz quantas coisas faltam pra fazer vídeo."
        },
        {
          "alvo": "arrumar-tudo",
          "titulo": "Um pedido só",
          "texto": "Junta tudo o que falta num pedido para a IA arrumar."
        },
        {
          "alvo": "falta",
          "titulo": "Uma coisa de cada vez",
          "texto": "Cada item tem um botão que resolve."
        },
        {
          "alvo": "pronto",
          "titulo": "O que já está certo",
          "texto": "Toque se quiser ver a lista."
        },
        {
          "alvo": "conferir",
          "titulo": "Arrumou?",
          "texto": "Toque aqui e o painel confere de novo."
        }
      ]
    },
    "voz": {
      "versao": 2,
      "passos": [
        {
          "alvo": "comparar",
          "titulo": "As vozes",
          "texto": "Aqui estão as vozes que o kit usa e quanto cada uma custa."
        },
        {
          "alvo": "paga",
          "titulo": "A voz mais natural",
          "texto": "É paga, direto no site da ElevenLabs. Toque em Conectar se quiser."
        },
        {
          "alvo": "passos",
          "titulo": "Três passos",
          "texto": "Abra o site, crie a chave e cole aqui. Os desenhos mostram onde tocar."
        },
        {
          "alvo": "calculadora",
          "titulo": "Quanto rende",
          "texto": "Escreva os créditos do seu plano e veja quantos vídeos cabem."
        },
        {
          "alvo": "paga",
          "titulo": "Pronto pra começar",
          "texto": "Toque em Conectar."
        }
      ]
    },
    "postar": {
      "versao": 2,
      "passos": [
        {
          "alvo": "rede",
          "titulo": "Escolha a rede",
          "texto": "Os passos mudam pra cada rede."
        },
        {
          "alvo": "jeito-postar",
          "titulo": "Computador ou celular?",
          "texto": "Dá pra postar pelo site da rede ou mandar o vídeo pro celular."
        },
        {
          "alvo": "passos",
          "titulo": "Siga na ordem",
          "texto": "São três passos."
        }
      ]
    },
    "canal": {
      "versao": 1,
      "passos": [
        {
          "alvo": "perfil",
          "titulo": "Seu canal",
          "texto": "É assim que o canal aparece pra quem vê."
        },
        {
          "alvo": "linhas",
          "titulo": "Mudar uma coisa",
          "texto": "Toque em Mudar na linha que quiser. Salva sozinho."
        },
        {
          "alvo": "refazer",
          "titulo": "Recomeçar",
          "texto": "Responda as perguntas de novo, se preferir."
        }
      ]
    },
    "redes": {
      "versao": 1,
      "passos": [
        {
          "alvo": "redes",
          "titulo": "Ligue as redes",
          "texto": "Cada vídeo sai pronto pra cada rede ligada."
        },
        {
          "alvo": "pacote",
          "titulo": "O que vem junto",
          "texto": "Aqui você vê o que sai em cada vídeo."
        },
        {
          "alvo": "horario",
          "titulo": "A hora de postar",
          "texto": "Postar sempre no mesmo horário ajuda quem segue."
        },
        {
          "alvo": "redes",
          "titulo": "Pronto",
          "texto": "Ligue ou desligue tocando no botão. Salva sozinho."
        }
      ]
    },
    "jeito": {
      "versao": 1,
      "passos": [
        {
          "alvo": "previa",
          "titulo": "Veja na hora",
          "texto": "Tudo que você mexe aparece aqui."
        },
        {
          "alvo": "ajustes",
          "titulo": "Os ajustes",
          "texto": "Toque numa opção. Já começa no recomendado."
        },
        {
          "alvo": "recomendado",
          "titulo": "Desfazer",
          "texto": "Se não gostar, volte tudo ao recomendado."
        },
        {
          "alvo": "ajustes",
          "titulo": "Experimente",
          "texto": "Toque em Grande e veja a letra crescer."
        }
      ]
    },
    "estilos": {
      "versao": 2,
      "passos": [
        {
          "alvo": "sentir",
          "titulo": "Comece pelo objetivo",
          "texto": "Escolha o que você quer que a pessoa faça no fim."
        },
        {
          "alvo": "catalogo",
          "titulo": "Os estilos certos acendem",
          "texto": "Toque numa capa para ver o exemplo."
        },
        {
          "alvo": "criar-estilo",
          "titulo": "Um estilo só seu",
          "texto": "Responda umas perguntas e o kit desenha cores e personagens só do seu canal."
        },
        {
          "alvo": "sentir",
          "titulo": "Na dúvida",
          "texto": "Toque em Não sei, me sugere. Mostramos os mais fáceis."
        },
        {
          "alvo": "usar-estilo",
          "titulo": "Gostou?",
          "texto": "Toque em Usar este estilo e o pedido já sai com ele."
        }
      ]
    },
    "personagens": {
      "versao": 1,
      "passos": [
        {
          "alvo": "elenco",
          "titulo": "Quem está na série",
          "texto": "Toque em Usar no próximo vídeo e o pedido já sai com o personagem."
        },
        {
          "alvo": "lugares",
          "titulo": "Onde a história acontece",
          "texto": "Os cenários que a IA já desenha."
        },
        {
          "alvo": "pedir",
          "titulo": "Quer alguém novo?",
          "texto": "Toque aqui e cole o pedido na IA."
        }
      ]
    },
    "ganchos": {
      "versao": 1,
      "passos": [
        {
          "alvo": "ganchos",
          "titulo": "O começo prende",
          "texto": "Os primeiros 3 segundos decidem se a pessoa fica."
        },
        {
          "alvo": "duelo",
          "titulo": "Teste dois",
          "texto": "Escolha dois começos e veja qual segura mais."
        },
        {
          "alvo": "pergunta",
          "titulo": "O fim",
          "texto": "Uma pergunta que qualquer um responde faz comentar."
        },
        {
          "alvo": "testar",
          "titulo": "Pronto",
          "texto": "Toque em Testar estes dois."
        }
      ]
    },
    "videoia": {
      "versao": 1,
      "passos": [
        {
          "alvo": "modelos",
          "titulo": "Os modelos",
          "texto": "Cada modelo tem um preço por minuto de vídeo pronto. O Seedance fala português; os outros usam a voz do narrador do kit."
        },
        {
          "alvo": "contas",
          "titulo": "Ligue uma conta",
          "texto": "Crie a chave no site, cole aqui e toque em Testar e salvar. Quem paga os vídeos é o saldo da sua conta."
        },
        {
          "alvo": "fazer",
          "titulo": "Faça a novelinha",
          "texto": "Com a conta ligada, este botão chama a IA. Ela mostra o custo antes e só gera com o seu ok."
        }
      ]
    },
    "conquistas": {
      "versao": 1,
      "passos": [
        {
          "alvo": "pontos",
          "titulo": "Seus pontos",
          "texto": "Cada troféu vale pontos. Os mais difíceis valem muito mais."
        },
        {
          "alvo": "proxima",
          "titulo": "Os próximos",
          "texto": "Aqui mostra quanto falta para o próximo troféu de vídeos e de views."
        },
        {
          "alvo": "trofeus",
          "titulo": "Sua estante",
          "texto": "Troféu ganho tem o botão Compartilhar. Ele gera uma imagem pronta para postar nos stories."
        }
      ]
    },
    "metricas": {
      "versao": 2,
      "passos": [
        {
          "alvo": "qual-video",
          "titulo": "Escolha o vídeo",
          "texto": "Mostramos primeiro os que faltam anotar."
        },
        {
          "alvo": "numeros",
          "titulo": "Três números",
          "texto": "Copie do app da rede. A conta é com a gente."
        },
        {
          "alvo": "veredito",
          "titulo": "O que mudar",
          "texto": "Aqui diz o que está bom e o que melhorar."
        },
        {
          "alvo": "anotar",
          "titulo": "Anote",
          "texto": "Toque em Anotar números."
        }
      ]
    },
    "aprender": {
      "versao": 1,
      "passos": [
        {
          "alvo": "busca",
          "titulo": "Procure",
          "texto": "Escreva do seu jeito, como “postar no TikTok”."
        },
        {
          "alvo": "trilha",
          "titulo": "Comece por aqui",
          "texto": "Três guias que todo mundo precisa."
        },
        {
          "alvo": "trilha",
          "titulo": "Leia o primeiro",
          "texto": "Toque no guia 1."
        }
      ]
    },
    "ajuda": {
      "versao": 1,
      "passos": [
        {
          "alvo": "busca",
          "titulo": "Conte o que houve",
          "texto": "Escreva o problema do seu jeito."
        },
        {
          "alvo": "perguntas",
          "titulo": "As mais comuns",
          "texto": "Toque numa pergunta para ver a resposta."
        },
        {
          "alvo": "suporte",
          "titulo": "Ainda travado?",
          "texto": "Aqui você fala com a gente."
        }
      ]
    },
    "suporte": {
      "versao": 2,
      "passos": [
        {
          "alvo": "falar",
          "titulo": "Fale com a gente",
          "texto": "Toque em Chamar no Telegram. Gente de verdade responde."
        },
        {
          "alvo": "antes",
          "titulo": "Antes de chamar",
          "texto": "Peça pra IA arrumar tudo ou veja as dúvidas mais comuns."
        },
        {
          "alvo": "licenca",
          "titulo": "Sua licença",
          "texto": "Aqui você vê até quando as atualizações são grátis e para quem esta cópia está licenciada. Versão nova também aparece aqui."
        }
      ]
    },
    "conversar": {
      "versao": 4,
      "passos": [
        {
          "alvo": "ia-escolha",
          "titulo": "Escolha a IA",
          "texto": "Claude Code ou ChatGPT. A que estiver pronta conversa aqui mesmo."
        },
        {
          "alvo": "ia-episodio",
          "titulo": "Seu episódio",
          "texto": "Roteiro, voz e vídeo aparecem aqui. Toque para ler, ouvir e assistir sem sair do painel."
        },
        {
          "alvo": "ia-conversa",
          "titulo": "A conversa",
          "texto": "Peça do seu jeito. Quando a IA perguntar algo, as respostas viram botões: é só tocar."
        },
        {
          "alvo": "ia-atalhos",
          "titulo": "Próximo passo",
          "texto": "Gravar a voz, montar a prévia, fazer o vídeo final e o pacote das redes: um toque e vai direto pra IA."
        },
        {
          "alvo": "ia-mandar",
          "titulo": "Mande",
          "texto": "Escreva e toque em Mandar."
        }
      ]
    },
    "meuestilo": {
      "versao": 1,
      "passos": [
        {
          "alvo": "me-opcoes",
          "titulo": "Uma pergunta por vez",
          "texto": "Toque na resposta mais parecida com o seu canal."
        },
        {
          "alvo": "me-nao-sei",
          "titulo": "Na dúvida",
          "texto": "Toque aqui e o kit escolhe por você."
        },
        {
          "alvo": "me-folha",
          "titulo": "A folha do estilo",
          "texto": "Aqui aparecem as cores e os personagens sorteados."
        },
        {
          "alvo": "me-usar",
          "titulo": "Gostou?",
          "texto": "Toque em Gostei, usar. Se não gostou, sorteie de novo."
        }
      ]
    }
  }
};
