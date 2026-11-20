/* Painel do Temporada Viral: telas montadas a partir de /api/estado (ou dos dados embutidos na versão estática).
   Visual e disposição: entrega/painel-direcao/DIRECAO.md. Os passos do tour guiado ficam em tours.js. */
(function () {
  "use strict";

  try { console.info("© 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html · TVK-2026-AF-CC02968C"); } catch (e) { /* sem console */ }
  var D0 = window.PAINEL_DADOS || null;
  var ESTATICO = !!(D0 && D0.estatico);
  var metaToken = document.querySelector('meta[name="painel-token"]');
  var TOKEN = metaToken ? metaToken.content : "";
  /* Ícone da marca: o servidor embute o arquivo na página (meta painel-icone); sem isso, vem de /static. */
  var metaIcone = document.querySelector('meta[name="painel-icone"]');
  var ICONE = (D0 && D0.icone) || (metaIcone && /^data:image\//.test(metaIcone.content) ? metaIcone.content : "/static/icone-256.png");
  var RESERVA_ICONE = "/static/mascote.png";
  /* Imagem que não carrega (painel aberto por um servidor antigo ou a versão só para ver): o ícone vira o mascote
     antigo e as ilustrações somem sem deixar o quadrado quebrado. */
  function trocarImagemQuebrada(img) {
    if (!img) return;
    /* Ilustração nova que ainda não chegou: cai no mascote do site. */
    if (img.dataset.reservaSrc && !img.dataset.trocou) { img.dataset.trocou = "1"; img.src = img.dataset.reservaSrc; return; }
    if (img.dataset.reserva) return;
    img.dataset.reserva = "1";
    if (/icone-256\.png$/.test(img.getAttribute("src") || "")) { ICONE = RESERVA_ICONE; img.src = RESERVA_ICONE; return; }
    if (img.closest(".ilustra, .marca, .cara")) img.style.visibility = "hidden";
  }
  document.addEventListener("error", function (ev) { if (ev.target && ev.target.tagName === "IMG") trocarImagemQuebrada(ev.target); }, true);
  var MARCA = "/static/marca/";
  function ilustra(nome, classe, alt) {
    return '<img class="ilustra ' + (classe || "") + '" src="' + MARCA + nome + '.webp" alt="' + esc(alt || "") + '" decoding="async">';
  }
  /* Cena do mascote feita para a tela (estatico/ilustracoes/<nome>.webp); enquanto o arquivo não existir, usa o
     mascote do site indicado em `reserva`. */
  function ilustracao(nome, reserva, classe) {
    return '<img class="ilustra ' + (classe || "") + '" src="/static/ilustracoes/' + nome + '.webp" data-reserva-src="' + MARCA + reserva + '.webp" alt="" decoding="async">';
  }

  var E = D0;
  var assinatura = E ? E.assinatura : "";
  var main = document.getElementById("conteudo");
  var lateral = document.getElementById("lateral");
  var topo = document.getElementById("topo");
  var barra = document.getElementById("barra");
  var gaveta = document.getElementById("gaveta");
  /* Modo simples (padrão: menu só com o essencial) ou completo (menu com todas as telas), lembrado neste navegador. */
  var COMPLETO = !!lerLocal("completo", false);
  /* Assistente do canal: passo e respostas ficam guardados para continuar de onde parou. */
  var mago = lerLocal("mago", null);
  var assuntoVideo = "";
  var redePostar = "instagram";
  var abaEpisodio = {};
  var estiloPerfil = null;
  var ultimoSaldo = null;
  var chaveSalva = {};
  var vozConectar = "";
  var objetivo = "";
  var ganchosEscolhidos = [];
  var perguntaFim = "";
  var redeMetricas = "";
  var epMetricas = "";
  var detalheRede = {};
  var editandoLinha = "";

  /* Telas: id -> [nome no menu, ícone, tela-mãe do "voltar"]. As antigas (comece, status, potencializar, videos)
     viraram apelidos das novas: links velhos e o que a IA escrever continuam abrindo a tela certa. */
  var TELAS = {
    inicio: ["Início", "casa", ""], fazer: ["Fazer um vídeo", "claquete", "inicio"], meus: ["Meus vídeos", "play", "inicio"],
    metricas: ["Métricas", "grafico", "inicio"], canal: ["Meu canal", "tv", "inicio"], redes: ["Redes", "rede", "canal"],
    jeito: ["Jeito dos vídeos", "ajuste", "canal"], estilos: ["Estilos", "grade", "inicio"], personagens: ["Personagens", "pessoa", "inicio"],
    ganchos: ["Ganchos", "anzol", "inicio"], voz: ["A voz", "som", "inicio"], problema: ["Tudo certo?", "socorro", "inicio"],
    aprender: ["Aprender", "livro", "inicio"], ajuda: ["Ajuda", "ajuda", "inicio"], postar: ["Como postar", "rede", "meus"],
    suporte: ["Conta e suporte", "conta", "inicio"], conversar: ["Conversar com a IA", "balao", "inicio"], arrumar: ["Arrumar meu canal", "tv", "inicio"],
    meuestilo: ["Criar meu estilo", "lapis", "estilos"], rapido: ["Postar rápido", "baixar", "inicio"],
    estudar: ["Estudar vídeos", "lupa", "inicio"], conquistas: ["Conquistas", "trofeu", "inicio"],
    videoia: ["IA de vídeo", "claquete", "inicio"]
  };
  var APELIDOS = { comece: "inicio", status: "problema", potencializar: "voz", videos: "meus", "criar-estilo": "meuestilo" };
  /* Grupos do menu completo e do "Mais opções". */
  var GRUPOS = [
    ["", ["inicio", "fazer", "estudar", "meus", "rapido", "problema"]],
    ["Meu canal", ["canal", "redes", "jeito", "estilos", "personagens", "ganchos"]],
    ["Mais", ["voz", "videoia", "metricas", "conquistas", "aprender", "ajuda"]],
    ["Você", ["suporte", "conversar"]]
  ];
  var ATALHOS = [["inicio", "Início", "casa"], ["fazer", "Fazer", "claquete"], ["meus", "Vídeos", "play"], ["problema", "Problema", "socorro"]];

  /* Estilos: nome curto, para que serve (2 a 4 palavras) e o que o exemplo mostra (uma frase). */
  var ESTILO_CURTO = {
    "serie-2d-voto": ["Série com voto", "a galera vota", "A história para num suspense e quem assiste vota o que acontece na parte 2."],
    "terror-voto": ["Terror com voto", "medo sem sangue", "Um mistério que dá frio na barriga e termina numa escolha de quem assiste."],
    "pov": ["Série em você", "quem vê é o herói", "Quem assiste vira o personagem e decide o próximo passo."],
    "novela-anime": ["Novela anime", "romance e drama", "Romance em desenho, com triângulo amoroso e voto no fim."],
    "novela-frutas": ["Novela de frutas", "besteirol com IA de vídeo", "Frutas com corpo de gente num drama besta de novela, feito cena por cena na IA de vídeo."],
    "explicativo-3d": ["Explicativo 3D", "uma pergunta, uma resposta", "Uma pergunta do dia a dia respondida com o objeto aberto em 3D."],
    "top5": ["Top 5 curiosidades", "o mais fácil", "Cinco curiosidades rápidas sobre o assunto, da menor para a maior."],
    "quiz": ["Quiz", "quem assiste responde", "Uma pergunta por vez, e a pessoa tenta acertar antes da resposta."],
    "historia-real": ["História real", "aconteceu mesmo", "Um caso de verdade contado do começo ao fim."],
    "antes-depois": ["Antes e depois", "com as suas fotos", "Mostra a diferença entre o antes e o depois com as suas fotos."],
    "bastidores": ["Bastidores", "mostra como você faz", "Mostra o seu jeito de fazer, passo a passo."],
    "tipografia": ["Frase na tela", "palavra por palavra", "As palavras aparecem no ritmo da voz, sem precisar de imagem."],
    "faceless": ["Narrado sem rosto", "voz e imagens", "Uma voz conta e as imagens passam, sem ninguém aparecer."]
  };
  var ORDEM_ESTILOS = Object.keys(ESTILO_CURTO);
  var OBJETIVOS = [
    ["volta", "Que volte amanhã", ["serie-2d-voto", "terror-voto", "pov", "novela-anime", "novela-frutas"]],
    ["salva", "Que aprenda e salve", ["explicativo-3d", "top5", "historia-real", "faceless"]],
    ["comenta", "Que comente e mande pra alguém", ["quiz", "tipografia", "antes-depois"]],
    ["trabalho", "Que veja meu trabalho", ["bastidores", "antes-depois"]]
  ];
  var FACEIS = ["top5", "quiz", "tipografia"];
  /* Estilos com animação pronta (motor de cartelas): o "escolhe por mim" só cai num destes, nunca num estilo em que
     a IA precisa desenhar a cena do zero (3D, série com personagem, novela). */
  var SEGUROS = ["top5", "quiz", "tipografia", "faceless", "historia-real", "antes-depois", "bastidores"];
  function estiloSeguro() {
    var p = valor("roteiro", "estilo_padrao");
    return SEGUROS.indexOf(p) >= 0 && estiloPorId(p) ? p : "top5";
  }

  /* Redes: selo de sigla (nunca o logotipo oficial), nome curto e o porquê em uma linha. */
  var REDES = {
    instagram: ["IG", "ig", "Instagram", "Onde a série com voto mais cresce."],
    tiktok: ["TT", "tt", "TikTok", "Leva o vídeo pra quem não te conhece."],
    youtube_shorts: ["YT", "yt", "YouTube Shorts", "O vídeo segue aparecendo por meses."],
    youtube_longo: ["YT", "tt", "YouTube (vídeo longo)", "Junta as partes num filme deitado."],
    kwai: ["KW", "kw", "Kwai", "Mesmo vídeo do TikTok, outro público."]
  };
  function nomeRede(r) { return (REDES[r] || [0, 0, r])[2]; }
  /* Glifos das redes: ícones monocromáticos do projeto simple-icons (CC0), cópia em vendor/simple-icons. */
  var GLIFOS = {
    instagram: "M7.0301.084c-1.2768.0602-2.1487.264-2.911.5634-.7888.3075-1.4575.72-2.1228 1.3877-.6652.6677-1.075 1.3368-1.3802 2.127-.2954.7638-.4956 1.6365-.552 2.914-.0564 1.2775-.0689 1.6882-.0626 4.947.0062 3.2586.0206 3.6671.0825 4.9473.061 1.2765.264 2.1482.5635 2.9107.308.7889.72 1.4573 1.388 2.1228.6679.6655 1.3365 1.0743 2.1285 1.38.7632.295 1.6361.4961 2.9134.552 1.2773.056 1.6884.069 4.9462.0627 3.2578-.0062 3.668-.0207 4.9478-.0814 1.28-.0607 2.147-.2652 2.9098-.5633.7889-.3086 1.4578-.72 2.1228-1.3881.665-.6682 1.0745-1.3378 1.3795-2.1284.2957-.7632.4966-1.636.552-2.9124.056-1.2809.0692-1.6898.063-4.948-.0063-3.2583-.021-3.6668-.0817-4.9465-.0607-1.2797-.264-2.1487-.5633-2.9117-.3084-.7889-.72-1.4568-1.3876-2.1228C21.2982 1.33 20.628.9208 19.8378.6165 19.074.321 18.2017.1197 16.9244.0645 15.6471.0093 15.236-.005 11.977.0014 8.718.0076 8.31.0215 7.0301.0839m.1402 21.6932c-1.17-.0509-1.8053-.2453-2.2287-.408-.5606-.216-.96-.4771-1.3819-.895-.422-.4178-.6811-.8186-.9-1.378-.1644-.4234-.3624-1.058-.4171-2.228-.0595-1.2645-.072-1.6442-.079-4.848-.007-3.2037.0053-3.583.0607-4.848.05-1.169.2456-1.805.408-2.2282.216-.5613.4762-.96.895-1.3816.4188-.4217.8184-.6814 1.3783-.9003.423-.1651 1.0575-.3614 2.227-.4171 1.2655-.06 1.6447-.072 4.848-.079 3.2033-.007 3.5835.005 4.8495.0608 1.169.0508 1.8053.2445 2.228.408.5608.216.96.4754 1.3816.895.4217.4194.6816.8176.9005 1.3787.1653.4217.3617 1.056.4169 2.2263.0602 1.2655.0739 1.645.0796 4.848.0058 3.203-.0055 3.5834-.061 4.848-.051 1.17-.245 1.8055-.408 2.2294-.216.5604-.4763.96-.8954 1.3814-.419.4215-.8181.6811-1.3783.9-.4224.1649-1.0577.3617-2.2262.4174-1.2656.0595-1.6448.072-4.8493.079-3.2045.007-3.5825-.006-4.848-.0608M16.953 5.5864A1.44 1.44 0 1 0 18.39 4.144a1.44 1.44 0 0 0-1.437 1.4424M5.8385 12.012c.0067 3.4032 2.7706 6.1557 6.173 6.1493 3.4026-.0065 6.157-2.7701 6.1506-6.1733-.0065-3.4032-2.771-6.1565-6.174-6.1498-3.403.0067-6.156 2.771-6.1496 6.1738M8 12.0077a4 4 0 1 1 4.008 3.9921A3.9996 3.9996 0 0 1 8 12.0077",
    tiktok: "M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z",
    youtube_shorts: "m18.931 9.99-1.441-.601 1.717-.913a4.48 4.48 0 0 0 1.874-6.078 4.506 4.506 0 0 0-6.09-1.874L4.792 5.929a4.504 4.504 0 0 0-2.402 4.193 4.521 4.521 0 0 0 2.666 3.904c.036.012 1.442.6 1.442.6l-1.706.901a4.51 4.51 0 0 0-2.369 3.967A4.528 4.528 0 0 0 6.93 24c.725 0 1.437-.174 2.08-.508l10.21-5.406a4.494 4.494 0 0 0 2.39-4.192 4.525 4.525 0 0 0-2.678-3.904ZM9.597 15.19V8.824l6.007 3.184z",
    youtube_longo: "M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"
  };
  function selo(r, pequeno) {
    var x = REDES[r] || [String(r).slice(0, 2).toUpperCase(), "tt"];
    var g = GLIFOS[r];
    return '<span class="rede ' + x[1] + (pequeno ? " pq" : "") + '" aria-hidden="true">' +
      (g ? '<svg class="glifo" viewBox="0 0 24 24" focusable="false"><path d="' + g + '"/></svg>' : esc(x[0])) + "</span>";
  }
  /* Chaves do kit/metricas.py: porcentagens como a rede mostra (ex.: 32,4). Contagem bruta vira porcentagem aqui. */
  var CAMPOS_METRICAS = [
    ["views", "Visualizações", "No vídeo, toque em Ver insights."],
    ["pulados_pct", "Pularam no começo (%)", "Nos insights: “taxa de pulados”."],
    ["comentarios", "Comentários", "É o número embaixo do balãozinho."],
    ["compartilhamentos", "Compartilhamentos", "O número embaixo do aviãozinho."],
    ["salvamentos", "Salvamentos", "Nos insights: “salvamentos”."],
    ["curtidas", "Curtidas", "O número embaixo do coração."],
    ["tempo_medio_s", "Tempo médio assistido (segundos)", "Nos insights: “tempo médio de visualização”."],
    ["duracao_s", "Duração do vídeo (segundos)", "Ex.: 105 para 1:45."],
    ["retencao_queda_s", "Segundo em que a curva cai", "No gráfico de retenção, onde a linha despenca."]
  ];
  var CONTA_VIRA_PCT = { comentarios: "comentarios_pct", compartilhamentos: "compartilhamentos_pct", salvamentos: "salvamentos_pct", curtidas: "curtidas_pct" };
  var ROTULO_METRICA = { views: "visualizações", pulados_pct: "pularam no começo", comentarios_pct: "comentaram", compartilhamentos_pct: "compartilharam",
    salvamentos_pct: "salvaram", curtidas_pct: "curtiram", tempo_medio_s: "tempo médio assistido", duracao_s: "duração", retencao_queda_s: "a curva cai em" };

  /* ------------------------------------------------------------ ícones (traço 2,5, pontas redondas, quadro 24) */
  var ICONES = {
    casa: '<path d="M3.5 11 12 4l8.5 7"/><path d="M5.5 9.5V20h13V9.5"/><path d="M10 20v-5.5h4V20"/>',
    claquete: '<rect x="3.5" y="9" width="17" height="11" rx="2.5"/><path d="M3.5 9 19 4.5l1 3.2"/><path d="m8.5 7.6 2.2 1.4M13.5 6.1l2.2 1.5"/>',
    play: '<rect x="3" y="4.5" width="18" height="15" rx="3.5"/><path d="M10 9v6l5-3z" fill="currentColor"/>',
    tocar: '<path d="M8 5.5v13l10.5-6.5z" fill="currentColor"/>',
    pausa: '<path d="M8.5 5.5v13M15.5 5.5v13"/>',
    socorro: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5v5.5"/><path d="M12 16.5v.01"/>',
    tv: '<rect x="3" y="7.5" width="18" height="12.5" rx="3"/><path d="m8.5 3.5 3.5 4 3.5-4"/><path d="M16.5 12v.01M16.5 15.5v.01"/>',
    voltar: '<path d="M19 12H5.5"/><path d="m11 6-6 6 6 6"/>',
    seguir: '<path d="M5 12h13.5"/><path d="m13 6 6 6-6 6"/>',
    copiar: '<rect x="8.5" y="8.5" width="11.5" height="11.5" rx="2.5"/><path d="M15.5 8.5V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v7.5a2 2 0 0 0 2 2h2.5"/>',
    abrir: '<path d="M13.5 4H20v6.5"/><path d="M20 4 11 13"/><path d="M17 14v4a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2h4"/>',
    baixar: '<path d="M12 4v11"/><path d="m7 10.5 5 5 5-5"/><path d="M4.5 19.5h15"/>',
    certo: '<path d="m5 12.5 4.5 4.5L19 7.5" stroke-width="3"/>',
    mais: '<path d="M4.5 7h15M4.5 12h15M4.5 17h15"/>',
    abaixo: '<path d="m6 9.5 6 6 6-6" stroke-width="2.75"/>',
    lado: '<path d="m9.5 6 6 6-6 6" stroke-width="2.75"/>',
    lapis: '<path d="M15 5.5 18.5 9"/><path d="M4.5 19.5 5.5 15 16 4.5a2 2 0 0 1 3 0l.5.5a2 2 0 0 1 0 3L9 18.5z"/>',
    som: '<path d="M4 9.5h3.5L12 5.5v13l-4.5-4H4z"/><path d="M15.5 9a4 4 0 0 1 0 6M18 6.5a7.5 7.5 0 0 1 0 11"/>',
    mudo: '<path d="M4 9.5h3.5L12 5.5v13l-4.5-4H4z"/><path d="m16 9.5 5 5M21 9.5l-5 5"/>',
    atualizar: '<path d="M19.5 12a7.5 7.5 0 1 1-2.2-5.3"/><path d="M19.5 4.5v4.5H15"/>',
    fechar: '<path d="M6.5 6.5l11 11M17.5 6.5l-11 11"/>',
    trofeu: '<path d="M8 4h8v5a4 4 0 0 1-8 0z"/><path d="M8 6H5v1.5A3 3 0 0 0 8 10.5M16 6h3v1.5a3 3 0 0 1-3 3"/><path d="M12 13v3.5M8.5 20h7M9.5 16.5h5V20h-5z"/>',
    lupa: '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.5 15.5 5 5"/>',
    pasta: '<path d="M3.5 7.5a2 2 0 0 1 2-2h4l2 2.5h7a2 2 0 0 1 2 2V18a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2z"/>',
    grafico: '<path d="M4 20h16"/><path d="M7 16.5v-4M12 16.5V7.5M17 16.5v-7"/>',
    rede: '<rect x="6.5" y="3" width="11" height="18" rx="2.5"/><path d="M10.5 6h3"/><path d="M12 16.8c-2-1.3-2.9-2.3-2.9-3.4a1.45 1.45 0 0 1 2.9-.5 1.45 1.45 0 0 1 2.9.5c0 1.1-.9 2.1-2.9 3.4z"/>',
    ajuste: '<path d="M4 8h9M17 8h3M4 16h3M11 16h9"/><circle cx="15" cy="8" r="2.2"/><circle cx="9" cy="16" r="2.2"/>',
    grade: '<rect x="4" y="4" width="6.5" height="6.5" rx="1.5"/><rect x="13.5" y="4" width="6.5" height="6.5" rx="1.5"/><rect x="4" y="13.5" width="6.5" height="6.5" rx="1.5"/><rect x="13.5" y="13.5" width="6.5" height="6.5" rx="1.5"/>',
    pessoa: '<circle cx="12" cy="8" r="3.8"/><path d="M4.5 20.5c.8-4 3.7-6.3 7.5-6.3s6.7 2.3 7.5 6.3"/>',
    anzol: '<path d="M14 3.5v11a4.5 4.5 0 0 1-9 0V12"/><path d="m5 12 2.5 2"/><circle cx="14" cy="3.5" r=".01"/>',
    livro: '<path d="M12 7c-2-1.5-5-2-8-1.6v13c3-.4 6 .1 8 1.6 2-1.5 5-2 8-1.6v-13c-3-.4-6 .1-8 1.6z"/><path d="M12 7v13"/>',
    ajuda: '<circle cx="12" cy="12" r="8.5"/><path d="M9.6 9.6a2.5 2.5 0 1 1 3.4 2.3c-.6.3-1 .8-1 1.5v.4"/><path d="M12 16.8v.01"/>',
    balao: '<path d="M4 6.5a2.5 2.5 0 0 1 2.5-2.5h11A2.5 2.5 0 0 1 20 6.5v8a2.5 2.5 0 0 1-2.5 2.5H11l-4.5 3.5V17A2.5 2.5 0 0 1 4 14.5z"/>',
    conta: '<rect x="3.5" y="5" width="17" height="14" rx="2.5"/><circle cx="9" cy="11" r="2.2"/><path d="M5.8 16.2c.5-1.6 1.7-2.4 3.2-2.4s2.7.8 3.2 2.4M14.5 10h3.5M14.5 13.5h2.5"/>',
    aviso: '<path d="M10.3 4.6a2 2 0 0 1 3.4 0l7 12.2A2 2 0 0 1 19 19.8H5a2 2 0 0 1-1.7-3z"/><path d="M12 9.5v4"/><path d="M12 16.8v.01"/>',
    chave: '<circle cx="8" cy="12" r="4"/><path d="M12 12h8.5M17.5 12v3M20.5 12v2.2"/>',
    estrela: '<path d="m12 4 2.4 5 5.4.7-4 3.8 1 5.4L12 16.3 7.2 18.9l1-5.4-4-3.8 5.4-.7z"/>',
    sair: '<path d="M14 4h4a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-4"/><path d="M10 8l-4 4 4 4M6 12h10"/>'
  };
  function icone(nome, classe) {
    return '<svg class="ic' + (classe ? " " + classe : "") + '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">' + (ICONES[nome] || "") + "</svg>";
  }

  /* ------------------------------------------------------------ utilidades */
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function lerLocal(k, padrao) {
    try { var v = localStorage.getItem("tvpainel." + k); return v ? JSON.parse(v) : padrao; } catch (e) { return padrao; }
  }
  function gravarLocal(k, v) {
    try { localStorage.setItem("tvpainel." + k, JSON.stringify(v)); } catch (e) { /* sem armazenamento: segue sem lembrar */ }
  }
  function midia(k) {
    if (!k) return "";
    if (ESTATICO) return k.indexOf("~t/") === 0 ? "" : k.split("/").map(encodeURIComponent).join("/");
    return "/midia?c=" + encodeURIComponent(k);
  }
  function api(metodo, caminho, corpo, bruto) {
    var op = { method: metodo, credentials: "same-origin", headers: { "X-Painel-Token": TOKEN } };
    if (corpo !== undefined) {
      if (bruto) { op.body = corpo; op.headers["Content-Type"] = "application/octet-stream"; }
      else { op.body = JSON.stringify(corpo); op.headers["Content-Type"] = "application/json"; }
    }
    return fetch(caminho, op).then(function (r) {
      return r.json().catch(function () { return { ok: false, msg: "Resposta inválida do painel." }; }).then(function (j) {
        if (r.status === 403 && j && j.bloqueado) { location.reload(); }
        return j;
      });
    }).catch(function () {
      return { ok: false, msg: "Não deu pra falar com o kit. Feche o painel e abra de novo pelo ícone." };
    });
  }
  /* Aviso que some sozinho: pílula areia embaixo, só para confirmar ação (ou contar um erro). */
  function toast(msg, tipo) {
    var caixa = document.getElementById("toasts");
    var t = document.createElement("div");
    t.className = "aviso" + (tipo ? " " + tipo : "");
    t.innerHTML = icone(tipo === "erro" || tipo === "aviso" ? "aviso" : "certo") + "<span></span>";
    t.lastChild.textContent = msg;
    caixa.appendChild(t);
    setTimeout(function () { t.classList.add("saindo"); setTimeout(function () { t.remove(); }, 220); }, tipo === "erro" ? 7000 : 3000);
  }
  /* Botão em estado "feito" por 2 s (turquesa + particípio) e de volta. */
  function feito(botao, texto) {
    if (!botao) return;
    var r = botao.querySelector(".rotulo");
    if (!r) return;
    if (!botao.dataset.rotulo) botao.dataset.rotulo = r.textContent;
    r.textContent = texto; botao.classList.add("e-feito");
    clearTimeout(botao._t);
    botao._t = setTimeout(function () { r.textContent = botao.dataset.rotulo; botao.classList.remove("e-feito"); }, 2000);
  }
  function copiar(texto, botao, aviso) {
    var ok = function () {
      toast(aviso || "Copiado. Agora cole no chat da IA.");
      feito(botao, botao && botao.classList.contains("gigante") ? "Copiado!" : "Copiado");
    };
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(texto).then(ok, function () { copiarVelho(texto) && ok(); });
    } else if (copiarVelho(texto)) { ok(); }
  }
  function copiarVelho(texto) {
    var ta = document.createElement("textarea");
    ta.value = texto; ta.setAttribute("readonly", ""); ta.style.position = "fixed"; ta.style.opacity = "0";
    document.body.appendChild(ta); ta.select();
    var ok = false;
    try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
    ta.remove();
    if (!ok) toast("Não consegui copiar: selecione o texto e use Ctrl+C.", "aviso");
    return ok;
  }
  /* Botão: classe "" (principal, sol), "secundario" ou "gigante". */
  function botao(rotulo, attrs, classe, ic) {
    var base = /(^|\s)discreto(\s|$)/.test(classe || "") ? "" : "botao";
    return '<button type="button" class="' + (base + (classe ? " " + classe : "")).trim() + '" ' + (attrs || "") + ">" + (ic ? icone(ic) : "") + '<span class="rotulo">' + esc(rotulo) + "</span></button>";
  }
  function botaoCopiar(texto, rotulo, classe, aviso) {
    /* Pedido pra IA: com o chat do painel pronto, o botão manda direto (copiar e colar só sem o chat). */
    if (/chat da IA/i.test(aviso || "") && !ESTATICO && iaPronta()) {
      var rot = /^copiar\b/i.test(rotulo || "") ? "Mandar pra IA" : rotulo;
      return botao(rot, 'data-acao="ia-pedir" data-texto="' + esc(texto) + '"', classe === undefined ? "secundario" : classe, "seguir");
    }
    return botao(rotulo || "Copiar", 'data-acao="copiar" data-texto="' + esc(texto) + '"' + (aviso ? ' data-aviso="' + esc(aviso) + '"' : ""), classe === undefined ? "secundario" : classe, "copiar");
  }
  function link(rotulo, href, classe, ic, extra) {
    return '<a class="' + (classe || "discreto") + '" href="' + esc(href) + '"' + (extra || "") + ">" + (ic ? icone(ic) : "") + "<span>" + esc(rotulo) + "</span></a>";
  }
  function salvoHtml() { return '<span class="salvo" aria-live="polite" hidden>' + icone("certo") + "Salvo agora</span>"; }
  function mostrarSalvo() {
    var s = main.querySelector(".salvo");
    if (!s) { toast("Salvo. A IA usa isso a partir do próximo vídeo."); return; }
    s.hidden = false; s.classList.remove("some"); void s.offsetWidth;
    clearTimeout(mostrarSalvo.t);
    mostrarSalvo.t = setTimeout(function () { s.classList.add("some"); }, 2600);
  }
  /* Lista suspensa própria (no lugar do <select>): botão + lista na paleta, teclado completo (setas, Home, End,
     Enter, Esc, letra). A lista usa position: fixed para nunca ser cortada. O valor fica num input escondido com o
     `name`, então os formulários leem e salvam do mesmo jeito. op: {id, nome, opcoes: [[valor, texto, detalhe,
     capa]], valor, rotuloId, descr, dis, acaoMudar}. */
  function suspensa(op) {
    var atual = op.opcoes.filter(function (o) { return String(o[0]) === String(op.valor); })[0] || op.opcoes[0] || ["", ""];
    var lid = op.id + "-lista";
    var capa = function (src) { return src ? '<img class="capinha" src="' + esc(src) + '" alt="" loading="lazy">' : ""; };
    return '<div class="suspensa">' +
      '<input type="hidden"' + (op.nome ? ' name="' + esc(op.nome) + '"' : "") + ' value="' + esc(atual[0]) + '"' + (op.acaoMudar ? ' data-acao-mudar="' + esc(op.acaoMudar) + '"' : "") + ">" +
      '<button type="button" class="suspensa-botao" id="' + esc(op.id) + '" aria-haspopup="listbox" aria-expanded="false" aria-controls="' + lid + '"' +
      (op.rotuloId ? ' aria-labelledby="' + op.rotuloId + " " + op.id + '"' : "") + (op.descr ? ' aria-describedby="' + op.descr + '"' : "") + (op.dis ? " disabled" : "") + ">" +
      '<span class="suspensa-capa">' + capa(atual[3]) + '</span><span class="nome suspensa-texto">' + esc(atual[1]) + "</span>" + icone("abaixo") + "</button>" +
      '<ul class="suspensa-lista" id="' + lid + '" role="listbox" tabindex="-1"' + (op.rotuloId ? ' aria-labelledby="' + op.rotuloId + '"' : "") + " hidden>" +
      op.opcoes.map(function (o, i) {
        return '<li role="option" id="' + lid + "-" + i + '" data-valor="' + esc(o[0]) + '" data-texto="' + esc(o[1]) + '"' + (o[3] ? ' data-capa="' + esc(o[3]) + '"' : "") + ' aria-selected="' + (String(o[0]) === String(atual[0])) + '">' +
          capa(o[3]) + '<span class="nome">' + esc(o[1]) + (o[2] ? "<small>" + esc(o[2]) + "</small>" : "") + "</span>" + icone("certo", "visto") + "</li>";
      }).join("") + "</ul></div>";
  }
  var susp = null;
  function opcoesSusp() { return susp ? susp.lista.querySelectorAll('[role="option"]') : []; }
  function posicionarSuspensa() {
    if (!susp) return;
    var r = susp.botao.getBoundingClientRect(), l = susp.lista;
    var cel = window.innerWidth <= 760;
    var alto = Math.min(312, l.scrollHeight + 6);
    var embaixo = window.innerHeight - r.bottom - (cel ? 84 : 12);
    var praCima = embaixo < alto + 8 && r.top > embaixo;
    l.style.left = Math.max(8, r.left) + "px";
    l.style.width = Math.min(r.width, window.innerWidth - 16) + "px";
    l.style.top = praCima ? Math.max(8, r.top - alto - 8) + "px" : (r.bottom + 8) + "px";
  }
  function abrirSuspensa(raiz) {
    fecharSuspensa(false);
    var b = raiz.querySelector(".suspensa-botao"), lista = raiz.querySelector(".suspensa-lista");
    var ops = lista.querySelectorAll('[role="option"]'), sel = 0;
    ops.forEach(function (o, k) { if (o.getAttribute("aria-selected") === "true") sel = k; });
    susp = { raiz: raiz, botao: b, lista: lista, ativo: sel, busca: "", quando: 0 };
    lista.hidden = false; b.setAttribute("aria-expanded", "true"); raiz.classList.add("aberta");
    posicionarSuspensa();
    lista.focus({ preventScroll: true });
    marcarAtivo();
  }
  function marcarAtivo() {
    var ops = opcoesSusp(), o = ops[susp.ativo];
    ops.forEach(function (x, k) { x.classList.toggle("ativo", k === susp.ativo); });
    if (!o) return;
    susp.lista.setAttribute("aria-activedescendant", o.id);
    var l = susp.lista;
    if (o.offsetTop < l.scrollTop) l.scrollTop = o.offsetTop;
    else if (o.offsetTop + o.offsetHeight > l.scrollTop + l.clientHeight) l.scrollTop = o.offsetTop + o.offsetHeight - l.clientHeight;
  }
  function fecharSuspensa(focar) {
    if (!susp) return;
    var s = susp; susp = null;
    s.lista.hidden = true; s.botao.setAttribute("aria-expanded", "false"); s.raiz.classList.remove("aberta");
    s.lista.removeAttribute("aria-activedescendant");
    if (focar) s.botao.focus();
  }
  function escolherSuspensa(k) {
    var s = susp, o = opcoesSusp()[k];
    if (!o) return;
    var input = s.raiz.querySelector('input[type="hidden"]');
    var mudou = input.value !== o.dataset.valor;
    opcoesSusp().forEach(function (x) { x.setAttribute("aria-selected", String(x === o)); });
    s.raiz.querySelector(".suspensa-texto").textContent = o.dataset.texto;
    s.raiz.querySelector(".suspensa-capa").innerHTML = o.dataset.capa ? '<img class="capinha" src="' + esc(o.dataset.capa) + '" alt="">' : "";
    input.value = o.dataset.valor;
    fecharSuspensa(true);
    if (mudou) { input.dispatchEvent(new Event("input", { bubbles: true })); input.dispatchEvent(new Event("change", { bubbles: true })); }
  }
  function teclaSuspensa(ev) {
    var t = ev.target;
    if (!susp && t.classList && t.classList.contains("suspensa-botao") && ["ArrowDown", "ArrowUp", "Enter", " "].indexOf(ev.key) >= 0) {
      ev.preventDefault(); abrirSuspensa(t.closest(".suspensa")); return;
    }
    if (!susp || t !== susp.lista) return;
    var n = opcoesSusp().length, k = ev.key;
    if (k === "ArrowDown") susp.ativo = Math.min(n - 1, susp.ativo + 1);
    else if (k === "ArrowUp") susp.ativo = Math.max(0, susp.ativo - 1);
    else if (k === "Home") susp.ativo = 0;
    else if (k === "End") susp.ativo = n - 1;
    else if (k === "PageDown") susp.ativo = Math.min(n - 1, susp.ativo + 6);
    else if (k === "PageUp") susp.ativo = Math.max(0, susp.ativo - 6);
    else if (k === "Enter" || k === " ") { ev.preventDefault(); escolherSuspensa(susp.ativo); return; }
    else if (k === "Escape") { ev.preventDefault(); ev.stopImmediatePropagation(); fecharSuspensa(true); return; }
    else if (k === "Tab") { fecharSuspensa(false); return; }
    else if (k.length === 1 && !ev.ctrlKey && !ev.metaKey && !ev.altKey) {
      /* Digitar a letra pula para a opção que começa com ela (várias letras seguidas formam a palavra). */
      var agora = Date.now();
      susp.busca = (agora - susp.quando < 700 ? susp.busca : "") + semAcento(k);
      susp.quando = agora;
      var ops = opcoesSusp(), ini = susp.busca.length === 1 ? susp.ativo + 1 : susp.ativo;
      for (var i = 0; i < n; i++) {
        var j = (ini + i) % n;
        if (semAcento(ops[j].dataset.texto).indexOf(susp.busca) === 0) { susp.ativo = j; break; }
      }
    } else return;
    ev.preventDefault();
    marcarAtivo();
  }
  window.addEventListener("resize", function () { if (susp) posicionarSuspensa(); });
  window.addEventListener("scroll", function () { if (susp) posicionarSuspensa(); }, true);

  function bonito(nome) {
    var t = String(nome || "").replace(/^\d{2}_/, "").replace(/[_-]+/g, " ").replace(/\bep\s*(\d+)\b/i, ", parte $1").replace(/\s+,/g, ",").trim();
    return t.charAt(0).toUpperCase() + t.slice(1);
  }
  function num(v) { return String(v).replace(".", ","); }
  function num1(v) { return String(Math.round(v)).replace(/\B(?=(\d{3})+(?!\d))/g, "."); }
  function igual(a, b) { return JSON.stringify(a) === JSON.stringify(b); }
  function semAcento(s) { return String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); }
  function slug(t) { return semAcento(t).replace(/[^a-z0-9]+/g, "").slice(0, 24); }
  function slugTraco(t) { return semAcento(t).replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, ""); }
  function P() { return (E && E.prefs) || {}; }
  function valor(secao, campo) { var v = P().valores || {}; return v[secao] ? v[secao][campo] : undefined; }
  function meta(secao, campo) { var s = (P().esquema || {}).secoes || {}; return s[secao] && s[secao].campos[campo]; }
  function recomendado(secao, campo) { var m = meta(secao, campo); return m ? m.recomendado : ""; }
  function rotuloOpcao(v) { var r = P().rotulos || {}; return r[String(v)] || String(v); }
  function estilosLista() {
    var l = ((E && E.estilos && E.estilos.lista) || []).slice();
    l.sort(function (a, b) {
      var ia = ORDEM_ESTILOS.indexOf(a.id), ib = ORDEM_ESTILOS.indexOf(b.id);
      return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib);
    });
    return l;
  }
  function estiloPorId(id) { return estilosLista().filter(function (x) { return x.id === id; })[0] || null; }
  function nomeEstilo(id) { var c = ESTILO_CURTO[id]; if (c) return c[0]; var x = estiloPorId(id); return x ? x.nome : id; }
  function serveEstilo(x) { var c = ESTILO_CURTO[x.id]; return c ? c[1] : String(x.resumo || "").split(/[.,;]/)[0]; }
  function fraseEstilo(x) { var c = ESTILO_CURTO[x.id]; return c ? c[2] : String(x.resumo || ""); }
  function textoValor(m, v) {
    if (m.tipo === "booleano") return v ? "Sim" : "Não";
    if (m.tipo === "escolha") return m.opcoes && (m.opcoes.indexOf("top5") >= 0) ? nomeEstilo(v) : rotuloOpcao(v);
    if (m.tipo === "multi") return (v || []).map(rotuloOpcao).join(", ");
    if (m.tipo === "lista") return (v || []).length ? v.join(", ") : "vazio";
    if (m.tipo === "numero") return num(v);
    return String(v);
  }
  function urlExemplo(id, tipo) {
    if (ESTATICO) return "exemplos/estilos/" + encodeURIComponent(id) + "/" + (tipo === "video" ? "exemplo.mp4" : "capa.jpg");
    return "/exemplo?e=" + encodeURIComponent(id) + "&f=" + tipo;
  }
  function capaEstilo(x) { return x && x.exemplo && x.exemplo.capa ? urlExemplo(x.id, "capa") : ""; }
  function capaEp(ep) { return ((ep.redes || [])[0] || {}).capa || ep.capa_base || ""; }
  function dataBr(iso) { var m = /^(\d{4})-(\d{2})-(\d{2})/.exec(String(iso || "")); return m ? m[3] + "/" + m[2] + "/" + m[1] : ""; }
  function dataDoQuando(q) { var m = /^(\d{2})\/(\d{2})\/(\d{4})(?:\s+(\d{2}):(\d{2}))?/.exec(q || ""); return m ? new Date(+m[3], +m[2] - 1, +m[1], +(m[4] || 0), +(m[5] || 0)) : null; }
  /* "hoje às 18:37", "ontem", "há 3 dias" */
  function quandoHumano(q, curto) {
    var d = dataDoQuando(q);
    if (!d) return q || "";
    var hoje = new Date(); hoje.setHours(0, 0, 0, 0);
    var dia = new Date(d); dia.setHours(0, 0, 0, 0);
    var dias = Math.round((hoje - dia) / 864e5);
    var hora = String(d.getHours()).padStart(2, "0") + ":" + String(d.getMinutes()).padStart(2, "0");
    if (dias <= 0) return curto ? "hoje" : "hoje às " + hora;
    if (dias === 1) return curto ? "ontem" : "ontem às " + hora;
    if (dias < 7) return "há " + dias + " dias";
    if (dias < 14) return "há 1 semana";
    return curto ? "há " + Math.floor(dias / 7) + " semanas" : "em " + q.slice(0, 5);
  }
  function mesesAte(iso) {
    var d = new Date(String(iso || "") + "T23:59:59");
    if (isNaN(d)) return null;
    var dias = Math.ceil((d - Date.now()) / 864e5);
    if (dias < 0) return "terminou";
    if (dias < 60) return dias === 1 ? "falta 1 dia" : "faltam " + dias + " dias";
    return "faltam " + Math.round(dias / 30.44) + " meses";
  }
  /* Atualizações: 12 meses a partir da compra; quem levou o "Atualizações para Sempre" não tem prazo. */
  function textoAtualizacoes(c) {
    if (c.atualizacoes_sempre) return "Atualizações para sempre";
    var f = mesesAte(c.atualizacoes_ate);
    if (f === "terminou") return "Atualizações grátis terminaram";
    return f ? "Atualizações grátis: " + f : "Atualizações em dia";
  }
  function nVideosProntos() { return (E.episodios || []).filter(function (x) { return x.pronto; }).length; }
  /* Tira caminho de arquivo e comando do texto que a pessoa lê (o pedido completo continua indo para a IA). */
  function limparCaminhos(t) {
    return String(t || "")
      .replace(/\s*\((?:[^()]*?(?:kit\/|\.py\b|\.md\b|\.json\b|python )[^()]*?)\)/g, "")
      .replace(/,?\s*a partir de kit\/?/g, "")
      .replace(/`?(?:[\w.~-]+\/)+([\w.-]+?)\.(?:md|py|json|txt|jpg|png|mp4)`?/g, function (m, b) { return "«" + b.replace(/[_-]+/g, " ") + "»"; })
      .replace(/[ \t]{2,}/g, " ").trim();
  }
  function assuntoCurto() { return String(valor("canal", "nicho") || "").split(/,|;| e curiosidades| explicad/)[0].trim(); }

  /* ------------------------------------------------------------ estado e atualização */
  function carregar() {
    if (ESTATICO) return Promise.resolve();
    return fetch("/api/estado", { credentials: "same-origin", headers: { "X-Painel-Token": TOKEN } })
      .then(function (r) {
        if (r.status === 403) { location.reload(); throw new Error("bloqueado"); }
        return r.json();
      }).then(function (j) { E = j; assinatura = j.assinatura; agendarComemoracao(); });
  }
  function editando() {
    var a = document.activeElement;
    if (tourAtivo) return true;
    if (main.querySelector("[data-sujo]")) return true;
    if (telaAtual() === "arrumar" && mago) return true;
    if (editandoLinha) return true;
    return !!(a && main.contains(a) && /INPUT|TEXTAREA|SELECT/.test(a.tagName) && a.type !== "range");
  }
  /* Dados novos chegam calados enquanto a pessoa digita, responde as perguntas ou vê o tour; a tela se atualiza
     quando ela para. O aviso "A IA mudou alguma coisa" só aparece quando há mudança não salva que seria perdida. */
  var redesenharDepois = false;
  function conferirMudancas() {
    if (ESTATICO || document.hidden) return;
    if (redesenharDepois && !editando()) { redesenharDepois = false; redesenhar(); }
    fetch("/api/assinatura", { credentials: "same-origin", headers: { "X-Painel-Token": TOKEN } })
      .then(function (r) { if (r.status === 403) { location.reload(); return null; } return r.json(); })
      .then(function (j) {
        if (!j || j.assinatura === assinatura) return;
        if (main.querySelector("[data-sujo]")) { document.getElementById("aviso-ia").hidden = false; return; }
        if (editando()) { carregar(); redesenharDepois = true; return; }
        recarregarTela();
      }).catch(function () { /* painel fechado: tenta de novo no próximo ciclo */ });
  }
  /* Sinal de vida: o servidor desliga sozinho quando nenhuma aba do painel está aberta. Enquanto a rota não existir
     (servidor antigo), o 404 é ignorado. */
  function sinalDeVida() {
    if (ESTATICO) return;
    fetch("/api/vivo", { method: "POST", credentials: "same-origin", headers: { "X-Painel-Token": TOKEN, "Content-Type": "application/json" }, body: "{}" })
      .catch(function () { /* sem servidor ou rota ainda não existe: nada a fazer */ });
  }
  function recarregarTela() {
    document.getElementById("aviso-ia").hidden = true;
    /* No chat, a IA mexe em arquivos o tempo todo: só atualiza os dados, sem refazer a conversa (ela pulava pro topo).
       Nas outras telas, redesenha guardando rolagem e detalhes abertos. */
    return carregar().then(function () { if (telaAtual() !== "conversar") redesenhar(); });
  }
  function telaAtual() {
    var id = (location.hash || "").replace("#", "").split("/")[0];
    id = APELIDOS[id] || id;
    return TELAS[id] ? id : "inicio";
  }
  function subRota() { return decodeURIComponent(location.hash.split("/").slice(1).join("/") || ""); }

  /* ------------------------------------------------------------ status em português de gente */
  /* Ordem: o que impede de fazer vídeo vem primeiro. */
  var PRIORIDADE = ["python", "bibliotecas", "ffmpeg", "voz", "canal", "fontes", "render", "disco", "versao"];
  function gb(det) { var m = /(\d+)\s*GB/.exec(det || ""); return m ? m[1] : "?"; }
  /* Título, porquê e ação de cada item da checagem, sem termo técnico (que fica em "Detalhes para a IA"). */
  function humano(i) {
    var ok = i.estado === "ok" || i.estado === "opcional";
    var acao = null;
    if (i.acao && i.acao.tipo === "ir") acao = i.acao.tela === "canal" ? { href: precisaMago() ? "#arrumar" : "#canal", rotulo: "Responder as perguntas" } : { href: "#voz", rotulo: "Ligar a voz" };
    if (i.acao && i.acao.tipo === "prefs") acao = { mudancas: i.acao.mudancas, rotulo: "Deixar mais leve" };
    var h = { titulo: i.titulo, porque: i.detalhe, curto: i.titulo, acao: acao };
    var ffm = /ffmpeg/.test(i.detalhe || "");
    if (i.id === "render" && i.caso === "gpu" && (i.medida || {}).dedicada) h.curto = "Placa de vídeo boa";
    var txt = {
      python: ["Falta um programa no computador", "O kit precisa do Python novo. A IA instala pra você.", "Programa do kit"],
      bibliotecas: ["Faltam peças do programa", "Sem elas o vídeo não sai. A IA instala pra você.", "Peças do programa"],
      ffmpeg: ["Falta o gravador de vídeo", "Sem ele o vídeo não é gravado. A IA instala pra você.", "Gravador de vídeo"],
      render: {
        sem_placa: ["O vídeo vai demorar mais", "O computador não tem placa de vídeo própria. Funciona, só demora.", "Placa de vídeo"],
        cpu_com_placa: ["A placa de vídeo está parada", "O computador tem placa, mas o vídeo sai mais devagar. A IA arruma.", "Placa de vídeo"],
        falha: ["A placa de vídeo não respondeu", "A IA confere e arruma pra você.", "Placa de vídeo"]
      }[i.caso] || [ffm ? "Não deu pra testar o vídeo" : "A placa de vídeo não respondeu", "A IA confere e arruma pra você.", "Placa de vídeo"],
      disco: i.estado === "falta" ? ["Quase sem espaço no computador", "Sobram só " + gb(i.detalhe) + " GB. A IA apaga os testes velhos.", "Espaço livre"]
        : ["Pouco espaço no computador", "Sobram " + gb(i.detalhe) + " GB. Cada vídeo usa uns 5 GB enquanto é feito.", "Espaço livre"],
      fontes: ["Faltam as letras do vídeo", "A IA baixa as letras do kit.", "Letras"],
      versao: ["Não achei a versão do kit", "A IA confere qual versão você tem.", "Versão"],
      voz: i.estado === "aviso" && ((i.medida || {}).prontas || []).length ? ["Deixar a voz mais natural", "Hoje o vídeo sai com a voz " + i.medida.prontas[0] + ", que já funciona. A do Google é grátis e soa mais natural.", "Voz"]
        : i.estado === "aviso" ? ["A voz escolhida não está ligada", "Coloque a chave dela ou troque de voz.", "Voz"]
        : ["A voz do vídeo não está ligada", "Sem voz, o vídeo sai mudo. A voz grátis do Google leva 2 minutos e não pede cartão.", "Voz"],
      canal: [valor("canal", "nome") ? "Faltam respostas sobre o canal" : "O canal ainda não tem nome", "São perguntas rápidas, com resposta pronta.", "Canal"],
      licenca: ["Licença", "", "Licença"]
    }[i.id];
    if (txt) { if (!ok) { h.titulo = txt[0]; h.porque = txt[1]; } h.curto = txt[2]; }
    if (i.id === "voz" && !ok && !acao) h.acao = { href: "#voz", rotulo: "Ligar a voz grátis" };
    if (i.id === "voz" && !ok && h.acao && h.acao.href) h.acao.rotulo = ((i.medida || {}).prontas || []).length ? "Deixar a voz melhor" : "Ligar a voz grátis";
    if (i.id === "disco" && !h.acao && i.pedir) h.rotuloPedir = "Pedir pra IA liberar";
    return h;
  }
  /* Itens que pedem atenção, já na ordem: os que impedem o vídeo e depois os avisos. */
  function pendencias() {
    var st = E.status || { itens: [] };
    var ordem = function (a, b) { return PRIORIDADE.indexOf(a.id) - PRIORIDADE.indexOf(b.id); };
    /* Voz: sem a escolhida, mas com outra que já funciona (ex.: Kokoro), é um passo, não um problema. */
    var vozBloqueia = function (i) { return i.id === "voz" && i.estado !== "ok" && !((i.medida || {}).prontas || []).length; };
    var bloq = st.itens.filter(function (i) { return i.estado === "falta" || (i.estado === "aviso" && vozBloqueia(i)); }).sort(ordem);
    var avisos = st.itens.filter(function (i) { return i.estado === "aviso" && !vozBloqueia(i); }).sort(ordem);
    /* "depende": a placa existe, mas o teste espera as peças do programa; não é um problema à parte. */
    var prontos = st.itens.filter(function (i) { return i.estado === "ok" || i.estado === "opcional" || i.estado === "depende"; });
    var emb = function (i) { return { item: i, h: humano(i) }; };
    return { bloqueiam: bloq.map(emb), avisos: avisos.map(emb), prontos: prontos.map(emb),
      conferindo: st.itens.some(function (i) { return i.estado === "conferindo"; }), rodando: st.rodando, quando: st.quando };
  }
  /* Um pedido só para a IA arrumar tudo o que falta e o que pode melhorar, na ordem certa (peças do programa antes
     do teste do vídeo, depois a voz). O mesmo botão vai mandar direto para o chat do painel quando ele existir. */
  function pedidoUnico(pend) {
    pend = pend || pendencias();
    var itens = pend.bloqueiam.concat(pend.avisos).filter(function (p) { return p.item.id !== "canal"; });
    if (!itens.length) return { texto: "", n: 0 };
    var partes = itens.map(function (p) {
      var t = String(p.item.pedir || "").trim().replace(/[.;]+$/, "");
      if (!t) t = "resolve isto: " + p.h.titulo.toLowerCase() + " (" + (p.item.detalhe || p.item.titulo) + ")";
      return t.charAt(0).toLowerCase() + t.slice(1);
    });
    return { n: itens.length, texto: "Arruma o meu estúdio do Temporada Viral: " + partes.map(function (t, i) { return (i + 1) + ") " + t; }).join("; ") +
      ". Depois confere o computador de novo (python verificar.py, a partir de kit/) e me diz em uma frase se ficou tudo pronto." };
  }
  function botaoArrumarTudo(classe, attrs) {
    var t = pedidoUnico();
    if (!t.texto || ESTATICO) return "";
    return botao("Pedir pra IA arrumar tudo", 'data-acao="pedir-ia" data-n="' + t.n + '" data-texto="' + esc(t.texto) + '"' + (attrs || ""), classe, "seguir");
  }
  var CAMPOS_BASE = ["nome", "arroba", "nicho", "publico"];
  /* O canal ainda não respondeu o básico: o painel abre direto nas perguntas. */
  /* O assistente ocupa a tela inteira (modo foco) só enquanto está em andamento. */
  function magoAberto() { return !ESTATICO && !(mago && mago.fim) && ((mago && mago.r) || precisaMago()); }
  function precisaMago() {
    return (P().faltando || []).some(function (f) { return f[0] === "canal" && CAMPOS_BASE.indexOf(f[1]) >= 0; });
  }

  /* ------------------------------------------------------------ moldura: topo, menu completo, barra, Mais opções */
  function avatarHtml(c) {
    var inicial = ((c && c.nome) || "?").trim().charAt(0).toUpperCase() || "?";
    return '<span class="avatar" aria-hidden="true">' + (c && c.logo ? '<img src="' + esc(midia(c.logo)) + '" alt="">' : esc(inicial)) + "</span>";
  }
  function renderTopo(atual) {
    var c = E.canal || {};
    var marca = '<a class="marca" href="#inicio" aria-label="Temporada Viral, ir para o início"><img class="inteira" src="' + MARCA + 'logo-360.webp" alt="" width="104" height="54">' +
      '<img class="cabeca" src="' + esc(ICONE) + '" alt="" width="44" height="44"></a>';
    if (atual === "arrumar" && magoAberto()) {
      topo.innerHTML = marca + '<div class="direita">' + (ESTATICO ? "" : '<a class="discreto claro" href="#inicio" data-acao="mago-depois">Fazer isso depois</a>') + "</div>";
      return;
    }
    topo.innerHTML = marca + '<div class="direita">' +
      '<a class="canal-atual" href="#canal" aria-label="Meu canal: ' + esc(c.nome || "sem nome ainda") + '">' + avatarHtml(c) +
      '<span class="canal-nome"><b>' + esc(c.nome || "Seu canal") + "</b><span>" + esc(c.arroba ? "@" + c.arroba : "ainda sem @") + "</span></span></a>" +
      '<button type="button" class="discreto claro sem-linha" data-acao="gaveta-abrir" aria-haspopup="dialog" aria-controls="gaveta" data-tour="mais">' + icone("mais") +
      '<span class="so-pc">Mais opções</span><span class="so-cel">Mais</span></button></div>';
  }
  function contaProblemas() { return pendencias().bloqueiam.length; }
  var COR_ITEM = { inicio: "sol", fazer: "sol", estudar: "turquesa", meus: "turquesa", rapido: "rosa", problema: "rosa", metricas: "turquesa", canal: "rosa", redes: "rosa", jeito: "rosa",
    estilos: "rosa", personagens: "rosa", ganchos: "rosa", voz: "areia", aprender: "areia", ajuda: "areia", suporte: "turquesa", conversar: "turquesa" };
  var NOME_LONGO = { problema: "Está tudo certo?", voz: "A voz dos vídeos", personagens: "Personagens", suporte: "Conta e suporte" };
  function nomeItem(id) { return id === "suporte" && !COMPLETO ? "Falar com o suporte" : (NOME_LONGO[id] || TELAS[id][0]); }
  function seloItem(id) {
    if (id === "rapido") { var nr = (E.episodios || []).filter(function (x) { return x.pronto && (x.redes || []).length; }).length; if (nr) return '<span class="selo-item rosa" aria-label="' + nr + ' pra postar">' + nr + "</span>"; }
    if (id === "meus") { var nv = nVideosProntos(); if (nv) return '<span class="selo-item turquesa" aria-label="' + nv + ' prontos">' + nv + "</span>"; }
    if (id === "problema") {
      var pend = pendencias(), n = pend.bloqueiam.length, np = pend.avisos.length;
      if (n) return '<span class="selo-item rosa" aria-label="' + (n === 1 ? "falta 1 coisa" : "faltam " + n + " coisas") + '">' + n + "</span>";
      if (np) return '<span class="selo-item sol" aria-label="' + (np === 1 ? "falta 1 passo" : "faltam " + np + " passos") + '">' + np + "</span>";
    }
    return "";
  }
  function itemNav(id, atual, comSeta) {
    var t = TELAS[id], ativo = id === atual || (TELAS[atual] && TELAS[atual][2] === id && GRUPOS.every(function (g) { return g[1].indexOf(atual) < 0; }));
    return '<li><a class="item-nav' + (ativo ? " ativo" : "") + '" href="#' + id + '"' + (ativo ? ' aria-current="page"' : "") + ">" +
      '<span class="ic-item ' + (COR_ITEM[id] || "areia") + '">' + icone(t[1]) + '</span><span class="nome-item">' + esc(nomeItem(id)) + "</span>" +
      seloItem(id) + (comSeta ? icone("lado", "seta-item") : "") + "</a></li>";
  }
  /* Interruptor dos dois modos, no pé do menu lateral e na gaveta. */
  function seletorModo() {
    return '<div class="seletor-modo" data-tour="modo"><span class="seletor-modo-rotulo" id="modo-rot">Menu</span>' +
      '<div class="segmentos cheio" role="radiogroup" aria-labelledby="modo-rot">' +
      '<button type="button" role="radio" aria-checked="' + !COMPLETO + '" aria-pressed="' + !COMPLETO + '" data-acao="modo" data-modo="simples">Simples</button>' +
      '<button type="button" role="radio" aria-checked="' + COMPLETO + '" aria-pressed="' + COMPLETO + '" data-acao="modo" data-modo="completo">Completo</button></div></div>';
  }
  var GRUPOS_SIMPLES = [["", ["inicio", "fazer", "estudar", "meus", "videoia", "conquistas", "rapido", "problema"]], ["Ajuda", ["conversar", "suporte"]]];
  function gruposNav(atual, comSeta) {
    return (COMPLETO ? GRUPOS : GRUPOS_SIMPLES).map(function (g) {
      return '<section class="grupo-nav">' + (g[0] ? '<h3 class="grupo-nav-nome">' + esc(g[0]) + "</h3>" : "") +
        '<ul class="cartao-nav">' + g[1].map(function (id) { return itemNav(id, atual, comSeta); }).join("") + "</ul></section>";
    }).join("");
  }
  /* Cartão do canal (pé do menu lateral e topo da gaveta): avatar, nome, @ e o botão de trocar de canal. */
  function cartaoCanal(classe) {
    var c = E.canal || {}, ca = E.canais || { disponivel: false };
    var trocar = ca.disponivel && !ESTATICO ? '<button type="button" class="botao secundario mini" data-acao="canais"' + (classe === "no-menu" ? ' aria-label="Trocar de canal">Trocar' : ">Trocar canal") + "</button>"
      : link("Mudar", "#canal", "botao secundario mini");
    return '<div class="cartao-canal ' + (classe || "") + '">' + '<a class="cartao-canal-link" href="#canal" aria-label="Meu canal: ' + esc(c.nome || "sem nome ainda") + '">' + avatarHtml(c) +
      '<span class="canal-nome"><b>' + esc(c.nome || "Seu canal") + "</b><span>" + esc(c.arroba ? "@" + c.arroba : "ainda sem @") + "</span></span></a>" + trocar + "</div>";
  }
  function linhaConta() {
    var c = E.conta || {};
    if (!c.ativa) return "";
    var ate = dataBr(c.atualizacoes_ate);
    return '<a class="linha-conta-nav" href="#suporte">' + icone("certo") + "<span>Licença vitalícia · ativa</span></a>";
  }
  function renderLateral(atual) {
    /* O menu é refeito a cada troca de tela: guarda a rolagem dele para não voltar ao topo a cada clique. */
    var rolaAntes = lateral.querySelector(".lateral-rola"), topoMenu = rolaAntes ? rolaAntes.scrollTop : 0;
    lateral.innerHTML = '<a class="marca-lateral" href="#inicio" aria-label="Temporada Viral, ir para o início"><img src="' + MARCA + 'logo-360.webp" alt="" width="132" height="69"></a>' +
      '<nav class="lateral-rola" aria-label="Todas as telas" data-tour="menu">' + gruposNav(atual, false) + "</nav>" +
      '<div class="lateral-pe">' + seletorModo() + cartaoCanal("no-menu") + linhaConta() +
      (ESTATICO ? '<p class="meta selo-estatico">Só para ver · gerado em ' + esc(E.gerado_em) + "</p>" : "") + "</div>";
    var rola = lateral.querySelector(".lateral-rola");
    if (rola) rola.scrollTop = topoMenu;
  }
  function renderBarra(atual) {
    var n = contaProblemas();
    barra.innerHTML = ATALHOS.map(function (a) {
      var conta = a[0] === "problema" && n ? '<span class="conta" aria-label="' + (n === 1 ? "falta 1 coisa" : "faltam " + n + " coisas") + '">' + n + "</span>" : "";
      return '<a href="#' + a[0] + '"' + (a[0] === atual ? ' aria-current="page"' : "") + '><span class="bolha">' + icone(a[2]) + "</span>" + esc(a[1]) + conta + "</a>";
    }).join("");
  }
  /* Mais opções (só no celular e em tela estreita): cabeçalho com o cartão do canal, uma lista que rola e o pé. */
  function renderGaveta() {
    gaveta.innerHTML = '<div class="gaveta-topo"><div class="gaveta-titulo"><h2 class="bloco-titulo" id="gaveta-titulo">Mais opções</h2>' +
      '<button type="button" class="fechar" data-acao="gaveta-fechar" aria-label="Fechar">' + icone("fechar") + "</button></div>" + cartaoCanal("na-gaveta") + "</div>" +
      '<nav class="gaveta-rola" aria-label="Todas as telas">' + gruposNav(telaAtual(), true) + "</nav>" +
      '<div class="gaveta-pe">' + seletorModo() + linhaConta() + '<div class="gaveta-rodape"><button type="button" class="discreto mini" data-acao="tour">' + icone("ajuda") + "<span>Me mostra como usa</span></button>" +
      '<span class="meta">Temporada Viral ' + esc(E.versao || "") + "</span></div></div>";
    var rola = gaveta.querySelector(".gaveta-rola");
    rola.addEventListener("scroll", function () { gaveta.classList.toggle("rolou", rola.scrollTop > 2); }, { passive: true });
  }
  function abrirGaveta() {
    if (!gaveta) return;
    renderGaveta();
    if (gaveta.showModal) gaveta.showModal(); else gaveta.setAttribute("open", "");
    var ativo = gaveta.querySelector(".item-nav.ativo"), rola = gaveta.querySelector(".gaveta-rola");
    if (ativo && rola && ativo.offsetTop + ativo.offsetHeight > rola.clientHeight) rola.scrollTop = ativo.offsetTop - 24;
    document.body.classList.add("com-gaveta");
    var b = topo.querySelector('[data-acao="gaveta-abrir"]'); if (b) b.setAttribute("aria-expanded", "true");
  }
  function fecharGaveta() {
    if (!gaveta || !gaveta.open) return;
    if (gaveta.close) gaveta.close(); else gaveta.removeAttribute("open");
  }
  if (gaveta) {
    gaveta.addEventListener("close", function () {
      document.body.classList.remove("com-gaveta");
      var b = topo.querySelector('[data-acao="gaveta-abrir"]'); if (b) { b.setAttribute("aria-expanded", "false"); b.focus(); }
    });
    gaveta.addEventListener("click", function (ev) { if (ev.target === gaveta) fecharGaveta(); });
  }

  /* ------------------------------------------------------------ partes comuns das telas */
  /* Linha do "← Início" (ou da tela-mãe), com o "Me mostra como usa" pequeno no fim quando a tela tem tour. */
  function voltarLinha(tela, extraDireita) {
    var mae = TELAS[tela] ? TELAS[tela][2] : "inicio";
    return '<div class="voltar-linha">' + (mae ? link(TELAS[mae][0] === "Início" ? "Início" : TELAS[mae][0], "#" + mae, "discreto claro sem-linha voltar", "voltar") : "<span></span>") +
      '<span class="voltar-direita">' + (extraDireita || "") + (temTour(tela) ? '<button type="button" class="discreto mini" data-acao="tour">Me mostra como usa</button>' : "") + "</span></div>";
  }
  function cabeca(titulo, apoio, direita, classe) {
    return '<div class="cabeca' + (classe ? " " + classe : "") + '"><div class="cabeca-texto"><h1 class="titulo">' + titulo + "</h1>" + (apoio ? '<p class="lead">' + apoio + "</p>" : "") + "</div>" + (direita || "") + "</div>";
  }
  function vazio(imgHtml, frase, acaoHtml, apoio) {
    return '<div class="vazio" data-tour="vazio">' + imgHtml + '<h2 class="titulo menor">' + esc(frase) + "</h2>" +
      (apoio ? '<p class="lead">' + esc(apoio) + "</p>" : "") + '<div class="acoes-centro">' + (acaoHtml || "") + "</div></div>";
  }
  function esqueleto(n) {
    var out = '<div class="esqueleto" aria-hidden="true">';
    for (var i = 0; i < n; i++) out += '<span style="width:' + [92, 74, 84, 60][i % 4] + '%"></span>';
    return out + "</div>";
  }
  function recolhe(titulo, resumo, corpo, attrs, aberto) {
    return '<details class="recolhe"' + (attrs || "") + (aberto ? " open" : "") + '><summary><b>' + titulo + "</b><span>" + esc(resumo || "") + "</span>" + icone("abaixo") + '</summary><div class="recolhe-corpo">' + corpo + "</div></details>";
  }

  /* ------------------------------------------------------------ campos das preferências (salvam sozinhos) */
  function controle(secao, campo, m, v, id, dis) {
    var nome = secao + "." + campo;
    var desc = ' aria-describedby="' + id + '-exp ' + id + '-erro"';
    var d = dis ? " disabled" : "";
    if (m.tipo === "texto_longo") return '<textarea class="entrada" rows="2" id="' + id + '" name="' + nome + '" maxlength="' + (m.max || 1500) + '"' + desc + d + ">" + esc(v) + "</textarea>";
    if (m.tipo === "arroba") return '<div class="com-prefixo"><span aria-hidden="true">@</span><input class="entrada" type="text" id="' + id + '" name="' + nome + '" value="' + esc(v) + '" maxlength="30" autocomplete="off" autocapitalize="none" autocorrect="off" spellcheck="false"' + desc + d + "></div>";
    if (m.tipo === "texto") return '<input class="entrada" type="text" id="' + id + '" name="' + nome + '" value="' + esc(v) + '" maxlength="' + (m.max || 300) + '"' + desc + d + ">";
    if (m.tipo === "numero") {
      var passo = (m.max - m.min) <= 1 ? 0.05 : ((m.max - m.min) <= 5 ? 0.5 : 1);
      return '<div class="numero-linha"><input type="range" min="' + m.min + '" max="' + m.max + '" step="' + passo + '" value="' + esc(v) + '" data-espelho="' + id + '" aria-label="' + esc(m.rotulo) + '" tabindex="-1"' + d + '>' +
        '<input class="entrada" type="number" inputmode="decimal" id="' + id + '" name="' + nome + '" min="' + m.min + '" max="' + m.max + '" step="' + passo + '" value="' + esc(v) + '"' + desc + d + "></div>";
    }
    if (m.tipo === "booleano") return '<label class="alternador"><input type="checkbox" class="alternador-caixa" id="' + id + '" name="' + nome + '"' + (v ? " checked" : "") + desc + d + '><span class="trilho" aria-hidden="true"></span><span class="palavra">' + (v ? "Sim" : "Não") + "</span></label>";
    if (m.tipo === "cor") return '<div class="cor-linha"><input type="color" value="' + esc(v) + '" data-espelho="' + id + '" aria-label="Escolher a cor"' + d + '><input class="entrada" type="text" id="' + id + '" name="' + nome + '" value="' + esc(v) + '" maxlength="7"' + desc + d + "></div>";
    if (m.tipo === "lista") return '<textarea class="entrada" rows="3" id="' + id + '" name="' + nome + '" data-lista="1" placeholder="Um por linha"' + desc + d + ">" + esc((v || []).join("\n")) + "</textarea>";
    /* Uma opção só não é escolha: vira texto informativo, fora do formulário. */
    if (m.tipo === "escolha" && m.opcoes.length === 1) return '<p class="valor-fixo" id="' + id + '">' + esc(rotuloOpcao(m.opcoes[0])) + "</p>";
    if (m.tipo === "escolha" || m.tipo === "multi") {
      var tipoInput = m.tipo === "multi" ? "checkbox" : "radio";
      if (m.tipo === "escolha" && m.opcoes.length > 4) {
        var extra = secao === "roteiro" && campo === "estilo_padrao" && !dis ? [["__criar", "Criar meu estilo"]] : [];
        return suspensa({ id: id, nome: nome, valor: v, dis: dis, rotuloId: id + "-rot", descr: id + "-exp",
          opcoes: m.opcoes.map(function (o) { return [o, textoValor(m, o)]; }).concat(extra) });
      }
      return '<div class="segmentos de-radio" id="' + id + '">' + m.opcoes.map(function (o) {
        var marcado = m.tipo === "multi" ? (v || []).indexOf(o) >= 0 : String(o) === String(v);
        return '<label><input type="' + tipoInput + '" name="' + nome + '" value="' + esc(o) + '"' + (marcado ? " checked" : "") + d + "><span>" + esc(rotuloOpcao(o)) + "</span></label>";
      }).join("") + "</div>";
    }
    if (m.tipo === "imagem") {
      var tipoImg = campo === "logo" ? "logo" : "mascote";
      return '<div class="imagem-campo"><div class="previa-img">' + (v ? '<img src="' + esc(midia(v)) + '" alt="' + esc(m.rotulo) + ' atual">' : '<span class="meta">sem imagem</span>') + "</div>" +
        '<input type="hidden" name="' + nome + '" id="' + id + '" value="' + esc(v) + '">' +
        (dis ? "" : '<label class="botao secundario">' + icone("baixar") + '<span class="rotulo">Escolher imagem</span><input type="file" class="arquivo-escondido" accept="' + (tipoImg === "logo" ? "image/png,image/jpeg,image/webp" : "image/png,image/webp") + '" data-upload="' + tipoImg + '"></label>') + "</div>";
    }
    return '<input class="entrada" type="text" id="' + id + '" name="' + nome + '" value="' + esc(v) + '"' + desc + d + ">";
  }
  function campoHtml(secao, campo) {
    var m = meta(secao, campo);
    if (!m) return "";
    var v = valor(secao, campo);
    var id = "f-" + secao + "-" + campo;
    var grupo = m.tipo === "escolha" && m.opcoes.length <= 4 || m.tipo === "multi";
    var lista = m.tipo === "escolha" && m.opcoes.length > 4;
    var rotulo = grupo || lista || m.tipo === "booleano" ? '<span class="rotulo" id="' + id + '-rot">' + esc(m.rotulo) + "</span>" : '<label class="rotulo" for="' + id + '">' + esc(m.rotulo) + "</label>";
    var rec = m.recomendado;
    var vazioRec = rec === "" || rec === null || (Array.isArray(rec) && !rec.length);
    var mudou = !vazioRec && m.tipo !== "imagem" && !igual(v, rec) && !(m.tipo === "escolha" && String(v) === String(rec));
    var nota = mudou ? '<span class="mudou">Você mudou. <button type="button" class="discreto mini" data-acao="campo-rec" data-secao="' + secao + '" data-campo="' + campo + '">Voltar pra ' + esc(textoValor(m, rec)) + "</button></span>" : "";
    var corpo = rotulo + controle(secao, campo, m, v, id, ESTATICO) +
      '<p class="ajuda" id="' + id + '-exp">' + esc(m.explica) + "</p>" + nota +
      '<p class="erro-msg" id="' + id + '-erro" hidden></p>';
    if (grupo) corpo = '<div role="group" aria-labelledby="' + id + '-rot">' + corpo + "</div>";
    return '<div class="campo" data-campo="' + campo + '" data-tipo="' + m.tipo + '">' + corpo + "</div>";
  }
  /* Bloco de uma seção (ou parte dela). Salva sozinho a cada mudança. */
  function formSecao(secao, op) {
    op = op || {};
    var sec = ((P().esquema || {}).secoes || {})[secao];
    if (!sec) return "";
    var campos = op.campos || Object.keys(sec.campos);
    return '<form class="form-prefs" data-secao="' + secao + '" data-campos="' + esc(campos.join(",")) + '" id="' + (op.ancora || "form-" + secao) + '" novalidate>' +
      (op.titulo === false ? "" : '<h3 class="bloco-titulo">' + esc(op.titulo || sec.titulo) + "</h3>") +
      '<div class="campos">' + campos.map(function (c) { return (op.custom && op.custom[c]) ? op.custom[c]() : campoHtml(secao, c); }).join("") + "</div></form>";
  }
  function lerCampo(form, secao, campo, m) {
    var nome = secao + "." + campo;
    var els = form.querySelectorAll('[name="' + nome + '"]');
    if (!els.length) return undefined;
    if (m.tipo === "booleano") return els[0].checked;
    if (m.tipo === "multi") return Array.prototype.filter.call(els, function (e) { return e.checked; }).map(function (e) { return e.value; });
    if (m.tipo === "escolha") {
      if (els[0].type === "hidden") return els[0].value;
      var marcado = Array.prototype.filter.call(els, function (e) { return e.checked; })[0];
      return marcado ? marcado.value : undefined;
    }
    if (m.tipo === "lista") return els[0].value.split("\n").map(function (s) { return s.trim(); }).filter(Boolean);
    if (m.tipo === "numero") return els[0].value === "" ? "" : Number(String(els[0].value).replace(",", "."));
    return els[0].value;
  }
  function mudancasDoForm(form) {
    var secao = form.dataset.secao;
    var mud = {};
    form.dataset.campos.split(",").forEach(function (c) {
      var m = meta(secao, c);
      if (!m || m.tipo === "imagem") return;
      var v = lerCampo(form, secao, c, m);
      if (v === undefined) return;
      var atual = valor(secao, c);
      var comparavel = m.tipo === "escolha" ? String(v) === String(atual) : igual(v, atual);
      if (!comparavel) mud[c] = v;
    });
    var r = {};
    if (Object.keys(mud).length) r[secao] = mud;
    return r;
  }
  function mostrarErros(raiz, erros) {
    raiz.querySelectorAll(".campo").forEach(function (c) {
      c.classList.remove("erro");
      var p = c.querySelector(".erro-msg"); if (p) { p.hidden = true; p.textContent = ""; }
    });
    var soltos = [];
    (erros || []).forEach(function (msg) {
      var achou = false;
      raiz.querySelectorAll(".campo[data-campo]").forEach(function (el) {
        var form = el.closest("[data-secao]");
        var m = form && meta(form.dataset.secao, el.dataset.campo);
        if (!achou && m && msg.indexOf(m.rotulo + ":") === 0) {
          el.classList.add("erro");
          var p = el.querySelector(".erro-msg"); p.hidden = false; p.innerHTML = icone("aviso") + "<span></span>"; p.lastChild.textContent = msg.slice(m.rotulo.length + 1).trim();
          achou = true;
        }
      });
      if (!achou) soltos.push(msg);
    });
    if (soltos.length) toast(soltos.join(" "), "erro");
  }
  /* Salva e atualiza os dados sem pular a tela. foco: seletor do controle que deve continuar com o foco. */
  function salvarPrefs(mudancas, raiz, foco) {
    if (ESTATICO) return Promise.resolve({ ok: false });
    return api("POST", "/api/prefs", { mudancas: mudancas }).then(function (r) {
      if (!r.ok) {
        if (raiz) mostrarErros(raiz, r.erros || [r.msg]); else toast((r.erros || [r.msg]).join(" "), "erro");
        return r;
      }
      (r.avisos || []).forEach(function (a) { toast("Atenção: " + a, "aviso"); });
      return carregar().then(function () {
        if (raiz) raiz.removeAttribute("data-sujo");
        if (!editando()) redesenhar(foco); else redesenharDepois = true;
        mostrarSalvo();
        return r;
      });
    });
  }

  /* ------------------------------------------------------------ telas */
  var T = {};

  /* Início: uma tarefa recomendada (bloco sol, uma ação só) e as outras três em linhas iguais. */
  T.inicio = function () {
    var pend = pendencias(), falta = pend.bloqueiam.length, passos = pend.avisos.length, nv = nVideosProntos(), eps = E.episodios || [];
    var rec = precisaMago() ? "arrumar" : (falta ? "problema" : "fazer");
    var canalHref = precisaMago() ? "#arrumar" : "#canal";
    var PRINC = {
      fazer: ["Fazer um vídeo", "Escolha o estilo, conte o assunto e mande o pedido pra IA.", ilustra("tv-notebook"), "#fazer", ' data-tour="fazer"'],
      arrumar: ["Arrumar meu canal", "Seis perguntas rápidas, com resposta pronta. Leva 2 minutos.", ilustra("tv-apontando"), "#arrumar", ' data-tour="canal"'],
      problema: ["Deu um problema", (falta === 1 ? "Falta 1 coisa" : "Faltam " + falta + " coisas") + " pra fazer vídeo. Cada uma se arruma num toque.", ilustracao("erro", "tv-cade"), "#problema", ' data-tour="problema"']
    }[rec];
    var principal = '<a class="principal" href="' + PRINC[3] + '"' + PRINC[4] + '><span class="raios" aria-hidden="true"></span>' + PRINC[2] +
      "<h2>" + esc(PRINC[0]) + "</h2><p>" + esc(PRINC[1]) + '</p><span class="vai" aria-hidden="true">' + icone("seguir") + "</span></a>";
    var capas = eps.map(capaEp).filter(Boolean).slice(0, 3);
    var primeiroPasso = passos ? pend.avisos[0].h.titulo : "";
    var problema = falta ? ["Deu um problema", falta === 1 ? "Falta 1 coisa. Veja qual." : "Faltam " + falta + " coisas. Veja quais.", "rosa", "rosa"]
      : (passos ? ["Está tudo certo?", (passos === 1 ? "Falta 1 passo: " : "Faltam " + passos + " passos. O primeiro: ") + primeiroPasso.charAt(0).toLowerCase() + primeiroPasso.slice(1), "sol", "areia"]
        : ["Está tudo certo?", pend.conferindo ? "Conferindo o computador…" : "Está tudo pronto.", "", "turquesa"]);
    var LINHAS = {
      fazer: ["#fazer", "areia", "claquete", "Fazer um vídeo", "Escolha o estilo e mande o pedido", "", ' data-tour="fazer"'],
      meus: ["#meus", "turquesa", "play", "Ver meus vídeos", nv ? (nv === 1 ? "1 pronto pra postar" : nv + " prontos pra postar") : (eps.length ? "A IA está fazendo o primeiro" : "Nenhum vídeo ainda"), "", ' data-tour="videos"'],
      problema: ["#problema", problema[3], "socorro", problema[0], problema[1], problema[2], ' data-tour="problema"'],
      canal: [canalHref, "areia", "tv", "Arrumar meu canal", "Nome, assunto e onde postar", "", ' data-tour="canal"']
    };
    var ordem = ["fazer", "meus", "problema", "canal"].filter(function (id) { return id !== rec && !(rec === "arrumar" && id === "canal"); }).slice(0, 3);
    var linhas = ordem.map(function (id) {
      var l = LINHAS[id];
      var fim = id === "meus" ? (capas.length ? '<span class="miniaturas n' + capas.length + '" aria-hidden="true">' + capas.map(function (c) { return '<img src="' + esc(midia(c)) + '" alt="" loading="lazy">'; }).join("") + "</span>"
        : '<span class="miniaturas vazia" aria-hidden="true">' + ilustracao("vazio-videos", "tv-notebook") + "</span>") : icone("lado", "seta");
      return '<a class="escolha" href="' + l[0] + '"' + l[6] + '><span class="circulo" style="background:var(--' + l[1] + ')">' + icone(l[2]) + "</span>" +
        '<span class="texto"><strong>' + esc(l[3]) + "</strong><small" + (l[5] ? ' class="' + l[5] + '"' : "") + ">" + esc(l[4]) + "</small></span>" + fim + "</a>";
    }).join("");
    var anotacao = !eps.length && rec === "fazer" ? '<div class="anotacao" aria-hidden="true"><span class="mao">comece por aqui</span>' +
      '<svg viewBox="0 0 64 54" fill="none" stroke="#FFD23F" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8c22-2 42 8 48 38"/><path d="m41 37 11 11 9-13"/></svg></div>' : "";
    var com = E.conta && E.conta.comunidade ? String(E.conta.comunidade) : "";
    var comunidade = com ? '<a class="escolha comunidade" href="' + esc(com) + '" target="_blank" rel="noopener noreferrer" data-tour="comunidade">' +
      '<span class="circulo" style="background:var(--turquesa)">' + icone("balao") + '</span><span class="texto"><strong>Entrar na comunidade</strong>' +
      "<small>Grupo no Telegram de quem usa a Temporada Viral: mostre seus vídeos, troque dicas e cresça junto</small></span>" + icone("lado", "seta") + "</a>" : "";
    return cabeca("O que você quer fazer agora?", '<span class="so-pc">Aqui você escolhe e confere. Quem faz o vídeo é a IA, no seu computador.</span>') +
      '<div class="grade-inicio">' + anotacao + principal + '<nav class="lista" aria-label="Outras tarefas">' + linhas + "</nav></div>" + comunidade +
      '<div class="tambem"><span class="meta">Também dá pra:</span>' + link("Deixar a voz melhor", "#voz") + link("Ver como postar", "#postar") +
      link("Anotar os números de um vídeo", "#metricas") + '<button type="button" class="discreto" data-acao="tour">Me mostra como usa</button></div>';
  };

  /* Fazer um vídeo: 1 estilo, exemplo tocando, 2 assunto, 3 pedido pronto para copiar. */
  function estiloDoFormato(f) {
    var t = semAcento(f || "");
    var x = estilosLista().filter(function (e) { var n = semAcento(e.nome), c = semAcento(nomeEstilo(e.id)); return t && (n.indexOf(t) >= 0 || t.indexOf(c) >= 0 || t.replace(/\s/g, "") === e.id); })[0];
    return x ? x.id : "";
  }
  /* Ideias: da pauta do canal; sem pauta, sugestões feitas com o assunto e o estilo do canal. */
  function listaIdeias() {
    var da = (E.ideias || []).map(function (x) { return { texto: x.ideia, estilo: estiloDoFormato(x.formato) }; });
    if (da.length) return da.slice(0, 3);
    var a = assuntoCurto();
    if (!a) return [];
    var padrao = valor("roteiro", "estilo_padrao") || "top5";
    var por = {
      top5: "5 coisas sobre " + a + " que quase ninguém conhece", quiz: "Quanto você sabe sobre " + a + "?",
      "historia-real": "A história real mais estranha sobre " + a, tipografia: "3 coisas sobre " + a + " que parecem mentira",
      "antes-depois": "Antes e depois: " + a, faceless: "O que ninguém te contou sobre " + a
    };
    return [padrao, "quiz", "historia-real", "top5", "tipografia"].filter(function (id, i, l) { return por[id] && l.indexOf(id) === i && estiloPorId(id); })
      .slice(0, 3).map(function (id) { return { texto: por[id], estilo: id }; });
  }
  function fraseVideo(est) {
    var assunto = assuntoVideo.trim().replace(/\s+/g, " ") || "um assunto do meu canal";
    var com = personagemVideo ? " com o personagem " + personagemVideo : "";
    var base = (est ? "faz um vídeo no estilo " + nomeEstilo(est.id).toLowerCase() : "faz um vídeo") + com + " sobre " + assunto;
    /* Sem estilo marcado o pedido sai do mesmo jeito: a IA escolhe pela tabela do comandos/novo-video.md e avisa. */
    if (!est) base += ". Não marquei estilo: escolha você o que combina com o assunto" + (moldeVideo ? " e com o vídeo que estudei" : "") +
      " (tabela \"Pedido sem estilo\" em comandos/novo-video.md), me diga qual em uma linha e já siga.";
    if (!moldeVideo || !moldeVideo.curto) return base;
    /* Formato estudado (tela Estudar vídeos): só a estrutura, nunca o texto do vídeo de referência. */
    return base + ". Siga o formato que estudei (" + moldeVideo.titulo + "): a estrutura, o ritmo e o tipo de visual, ajustando à duração do estilo e sem copiar nenhuma frase do vídeo de referência: " +
      moldeVideo.curto + (moldeVideo.arquivo ? " O molde completo está em " + moldeVideo.arquivo + ": abra antes do roteiro e olhe a folha de quadros do vídeo que ele indica." : "") +
      " O visual tem que ser do mesmo tipo da referência (personagem, cenário, movimento), nunca fundo parado só com texto.";
  }
  /* Quadros do vídeo para escolher a cena: um a cada trecho igual, desenhados num canvas a partir do próprio vídeo. */
  function montarCenas(g) {
    if (!g || g.dataset.pronto || !g.dataset.cenas) return;
    g.dataset.pronto = "1";
    var v = document.createElement("video");
    v.muted = true; v.preload = "auto"; v.playsInline = true; v.src = g.dataset.cenas;
    var tempos = [], k = 0, saida = [];
    var falhou = function () {
      g.innerHTML = '<p class="cenas-carregando">Não deu pra separar as cenas. Escreva no pedido em que parte do vídeo está.</p>';
      var h = g.closest("form").querySelector('[name="trecho"]'); if (h) h.remove();
    };
    v.addEventListener("error", falhou);
    v.addEventListener("loadedmetadata", function () {
      var d = v.duration || 0;
      if (!d || !isFinite(d)) return falhou();
      var n = Math.max(4, Math.min(12, Math.round(d / 8)));
      for (var i = 0; i < n; i++) tempos.push(Math.min(d - 0.1, (i + 0.5) * d / n));
      v.currentTime = tempos[0];
    });
    v.addEventListener("seeked", function () {
      var c = document.createElement("canvas");
      c.width = 108; c.height = 192;
      try { c.getContext("2d").drawImage(v, 0, 0, c.width, c.height); } catch (e) { return falhou(); }
      saida.push([c, tempos[k]]);
      k++;
      if (k < tempos.length) { v.currentTime = tempos[k]; return; }
      g.innerHTML = "";
      saida.forEach(function (q, i) {
        var b = document.createElement("button");
        b.type = "button"; b.className = "cena-video"; b.setAttribute("role", "radio"); b.setAttribute("aria-checked", "false"); b.setAttribute("aria-pressed", "false");
        b.dataset.acao = "cena-video"; b.dataset.t = fmtSeg(q[1]);
        b.setAttribute("aria-label", "Cena " + (i + 1) + ", perto de " + fmtSeg(q[1]));
        b.appendChild(q[0]);
        var r = document.createElement("span"); r.textContent = fmtSeg(q[1]); b.appendChild(r);
        g.appendChild(b);
      });
      v.removeAttribute("src"); v.load();
    });
  }
  function fmtSeg(s) { s = Math.max(0, Math.floor(s || 0)); return Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0"); }
  /* Player próprio (tocar, tempo, barra, som), igual no exemplo e no vídeo pronto. */
  function playerHtml(src, poster, op) {
    op = op || {};
    var mudo = !!op.mudo;
    return '<div class="exemplo player-proprio' + (op.classe ? " " + op.classe : "") + '"' + (op.attrs || "") + ">" +
      '<video src="' + esc(src) + '"' + (poster ? ' poster="' + esc(poster) + '"' : "") + " playsinline preload=\"metadata\"" + (mudo ? " muted" : "") + (op.auto ? " autoplay loop" : "") +
      ' aria-label="' + esc(op.rotulo || "Vídeo") + '"></video>' +
      '<div class="controles"><button type="button" class="ctl" data-acao="player-tocar" aria-label="' + (op.auto ? "Pausar" : "Tocar") + '">' + icone(op.auto ? "pausa" : "tocar") + "</button>" +
      '<span class="t-atual">0:00</span><input type="range" class="barrinha" min="0" max="1000" value="0" aria-label="Posição do vídeo"><span class="t-total">' + esc(op.total || "0:00") + "</span>" +
      '<button type="button" class="ctl" data-acao="player-som" aria-label="' + (mudo ? "Ligar o som" : "Tirar o som") + '">' + icone(mudo ? "mudo" : "som") + "</button></div></div>";
  }
  T.fazer = function () {
    var lista = estilosLista();
    var est = estiloPorId(subRota());
    var padrao = estiloSeguro();
    var itens = lista.map(function (x) {
      var marcado = est && x.id === est.id;
      var capa = capaEstilo(x);
      return '<li class="estilo-item"><button type="button" class="opcao" role="radio" aria-checked="' + !!marcado + '" aria-pressed="' + !!marcado + '" data-acao="escolher-estilo" data-id="' + esc(x.id) + '">' +
        '<span class="capa-item">' + (capa ? '<img src="' + esc(capa) + '" alt="" loading="lazy">' : '<span class="sem-capa" aria-hidden="true"></span>') +
        (FACEIS.indexOf(x.id) >= 0 ? '<span class="facil">Fácil</span>' : "") + "</span>" +
        '<span class="texto"><strong>' + esc(nomeEstilo(x.id)) + "</strong><small>" + esc(x.duracao) + (FACEIS.indexOf(x.id) >= 0 ? ' <span class="etiqueta">Fácil</span>' : "") + "</small></span>" +
        '<span class="marcador">' + (marcado ? icone("certo") : "") + "</span></button>" +
        (marcado && x.exemplo && x.exemplo.video ? '<button type="button" class="ver" data-acao="exemplo" data-id="' + esc(x.id) + '" aria-label="Ver o exemplo de ' + esc(nomeEstilo(x.id)) + '">' + icone("tocar") + "</button>" : "") + "</li>";
    }).join("");
    var exemplo;
    if (est && est.exemplo && est.exemplo.video) {
      exemplo = playerHtml(urlExemplo(est.id, "video"), capaEstilo(est), { mudo: true, auto: true, rotulo: "Exemplo do estilo " + nomeEstilo(est.id), total: "0:10" }) +
        '<p class="exemplo-legenda"><b>' + esc(nomeEstilo(est.id)) + '.</b> <span class="apoio">' + esc(fraseEstilo(est)) + "</span></p>";
    } else if (est) {
      exemplo = '<div class="exemplo exemplo-vazio">' + (capaEstilo(est) ? '<img src="' + esc(capaEstilo(est)) + '" alt="">' : '<span class="meta">exemplo em breve</span>') + "</div>" +
        '<p class="exemplo-legenda"><b>' + esc(nomeEstilo(est.id)) + '.</b> <span class="apoio">' + esc(fraseEstilo(est)) + "</span></p>";
    } else {
      exemplo = '<div class="exemplo exemplo-vazio">' + ilustra("tv-apontando") + '<p class="apoio">Toque num estilo para ver um exemplo de 10 segundos.</p></div>';
    }
    var ideias = listaIdeias();
    var ideiasHtml = ideias.length ? '<div class="ideias"><span class="meta">Sem ideia? Toque numa:</span>' + ideias.map(function (x) {
      return '<button type="button" class="ideia" data-acao="ideia" data-texto="' + esc(x.texto) + '" data-estilo="' + esc(x.estilo) + '">' + esc(x.texto) + "</button>";
    }).join("") + "</div>" : "";
    /* Uma ação principal: mandar o pedido pro chat da IA do painel; sem o chat, copiar e dizer onde colar. */
    var pronta = iaPronta() && !ESTATICO;
    /* Sem estilo marcado o pedido sai igual: a IA escolhe o estilo pelo assunto e diz qual. */
    var acao = pronta
      ? botao("Mandar pra IA", 'data-acao="mandar-pedido" data-id="' + esc(est ? est.id : "") + '"', "gigante largo", "seguir")
      : botao("Copiar o pedido", 'data-acao="copiar-frase" data-id="' + esc(est ? est.id : "") + '"', "gigante largo", "copiar");
    var depois = (est ? "" : '<p class="apoio">Não marcou estilo? Tudo bem: a IA escolhe o que combina com o assunto e te diz qual.</p>') + (pronta
      ? '<p class="apoio">O pedido vai pro chat da IA aqui no painel. Ela faz o vídeo no seu computador e ele aparece em Meus vídeos.</p>' +
        '<button type="button" class="discreto mini" data-acao="copiar-frase" data-id="' + esc(est ? est.id : "") + '">Só copiar o pedido</button>'
      : '<p class="apoio">Depois cole no chat da IA (Claude Code ou Codex) e mande. Quando ficar pronto, o vídeo aparece em Meus vídeos.</p>' +
        link("Conversar com a IA aqui no painel", "#conversar", "discreto mini"));
    return '<div class="cabeca cabeca-fazer">' + link("Início", "#inicio", "discreto claro sem-linha so-pc voltar", "voltar") + '<h1 class="titulo">Fazer um vídeo</h1>' +
      '<span class="voltar-direita so-pc"><button type="button" class="discreto mini" data-acao="tour">Me mostra como usa</button></span></div>' +
      '<div class="grade-fazer">' +
      '<section class="col-estilos" data-tour="estilos"><h2 class="bloco-titulo"><span class="n">1</span>Escolha o estilo</h2>' +
      (est ? "" : '<a class="discreto mini nao-sei" href="#fazer/' + esc(padrao) + '">Não sei, escolhe por mim</a>') +
      '<ul class="estilos" role="radiogroup" aria-label="Estilo">' + itens + "</ul></section>" +
      '<section class="col-exemplo" aria-label="Exemplo do estilo"><h2 class="bloco-titulo so-pc" aria-hidden="true" style="visibility:hidden">Exemplo</h2>' + exemplo + "</section>" +
      '<section class="pedido"><div class="campo" data-tour="assunto"><h2 class="bloco-titulo"><span class="n">2</span><label for="assunto-video">Sobre o que é o vídeo?</label></h2>' +
      '<textarea id="assunto-video" class="entrada" rows="2" data-acao-mudar="assunto" maxlength="300" placeholder="Ex.: o bicho que dorme de olho aberto">' + esc(assuntoVideo) + "</textarea>" +
      '<p class="ajuda">Uma frase basta. Ex.: 5 bichos que parecem de mentira.</p>' +
      (moldeVideo || ESTATICO ? "" : link("Viu um vídeo que deu certo? Estude o formato dele", "#estudar", "discreto mini", "lupa")) + "</div>" +
      '<div class="pilha" data-tour="copiar"><h2 class="bloco-titulo"><span class="n">3</span>' + (pronta ? "Mande o pedido pra IA" : "Copie o pedido e cole na IA") + "</h2>" +
      (moldeVideo ? '<p class="com-personagem com-molde" data-tour="molde-fazer">' + icone("lupa") + "<span>Com o formato de <b>" + esc(moldeVideo.titulo) + '</b></span><button type="button" class="discreto mini" data-acao="tirar-molde">Tirar</button></p>' : "") +
      (personagemVideo ? '<p class="com-personagem">' + icone("pessoa") + "<span>Com o personagem <b>" + esc(personagemVideo) + '</b></span><button type="button" class="discreto mini" data-acao="tirar-personagem">Tirar</button></p>' : "") +
      '<p class="folha" id="frase-ia">' + esc(fraseVideo(est)) + "</p>" +
      '<div class="fixa-copiar">' + acao + "</div>" + depois + "</div>" + ideiasHtml + "</section></div>";
  };

  /* Meus vídeos: player, abas por rede e os três passos para postar. */
  function nomeArquivo(ep, rede) { return (slugTraco(bonito(ep.nome)) || "video") + "-" + rede + ".mp4"; }
  function horaPostar() {
    var hora = String(valor("redes", "horario") || "").replace(/,?\s*no mesmo horário todo dia\.?$/i, "").trim();
    if (!hora) return "";
    var horas = (hora.match(/(\d{1,2})\s*h/g) || []).map(function (h) { return parseInt(h, 10); });
    var quando = horas.length && new Date().getHours() >= horas[horas.length - 1] ? "amanhã" : "hoje";
    return "Melhor hora: " + quando + ", " + hora + ".";
  }
  /* Postar rápido: tudo de todas as redes numa tela só, pra baixar e copiar sem procurar. */
  T.rapido = function () {
    var eps = E.episodios || [];
    var titulo = cabeca("Postar rápido", "Baixe o vídeo e a capa e copie a legenda de cada rede. Depois é só postar pelo app.", "", "cabeca-rapido");
    if (!eps.length) {
      return voltarLinha("rapido") + titulo + vazio(ilustracao("vazio-videos", "tv-notebook", "vazio-ilustra"), "Nenhum vídeo pronto ainda", link("Fazer um vídeo", "#fazer", "botao gigante", "claquete"), "Quando a IA montar o pacote das redes, ele aparece aqui pronto pra postar.");
    }
    var lista = eps.filter(function (x) { return x.pronto && (x.redes || []).length; });
    if (!lista.length) lista = eps;
    var idx = Number(subRota());
    if (subRota() === "" || !(idx >= 0 && idx < lista.length)) idx = 0;
    var ep = lista[idx];
    var escolha = lista.length > 1 ? '<div class="rapido-eps" role="group" aria-label="Qual vídeo">' + lista.slice(0, 6).map(function (x, i) {
      return '<a class="ideia' + (i === idx ? " ativo" : "") + '" href="#rapido/' + i + '"' + (i === idx ? ' aria-current="true"' : "") + ">" + esc(bonito(x.nome)) + "</a>";
    }).join("") + "</div>" : "";
    var redes = ep.redes || [];
    var corpo;
    if (!redes.length) {
      var pedido = "gera o pacote das redes escolhidas do vídeo " + ep.nome + " (vídeo, capa e legenda de cada rede)";
      corpo = '<section class="plano rapido-falta" data-tour="rapido-redes"><h2 class="bloco-titulo">Falta montar o pacote das redes</h2>' +
        '<p class="apoio">O vídeo ' + esc(bonito(ep.nome)) + " já existe, mas ainda não tem a capa e a legenda de cada rede.</p>" +
        (ESTATICO ? "" : botao("Pedir pra IA montar o pacote", 'data-acao="ia-pedir" data-texto="' + esc(pedido) + '"', "gigante", "seguir")) + "</section>";
    } else {
      corpo = '<div class="rapido-grade" data-tour="rapido-redes">' + redes.map(function (r) {
        var nr = r.rede === "youtube_shorts" ? "YouTube Shorts" : (r.rede === "youtube_longo" ? "YouTube longo" : nomeRede(r.rede));
        var base = slugTraco(bonito(ep.nome)) || "video";
        var capa = r.capa ? '<img class="rapido-capa" src="' + esc(midia(r.capa)) + '" alt="Capa do ' + esc(nr) + '" loading="lazy">' : '<div class="rapido-capa sem">sem capa</div>';
        var botoes = (r.video && midia(r.video) ? '<a class="botao" href="' + esc(midia(r.video)) + '" download="' + esc(nomeArquivo(ep, r.rede)) + '">' + icone("baixar") + '<span class="rotulo">Baixar vídeo</span></a>' : "") +
          (r.capa ? '<a class="botao secundario" href="' + esc(midia(r.capa)) + '" download="' + esc(base + "-capa-" + r.rede + ".jpg") + '">' + icone("baixar") + '<span class="rotulo">Baixar capa</span></a>' : "");
        var textos = "";
        if (r.titulo) textos += '<p class="rapido-rotulo">Título</p><p class="folha folha-titulo">' + esc(r.titulo) + "</p>" + botaoCopiar(r.titulo, "Copiar o título", "secundario", "Título copiado. Agora cole no app.");
        if (r.legenda) textos += '<p class="rapido-rotulo">' + (r.titulo ? "Descrição" : "Legenda") + '</p><p class="folha folha-legenda rapido-legenda">' + esc(r.legenda) + "</p>" + botaoCopiar(r.legenda, r.titulo ? "Copiar a descrição" : "Copiar a legenda", "", "Legenda copiada. Agora cole no app.");
        if (r.fixado) textos += '<p class="rapido-rotulo">Comentário para fixar</p><p class="folha">' + esc(r.fixado) + "</p>" + botaoCopiar(r.fixado, "Copiar o comentário", "secundario", "Comentário copiado.");
        return '<article class="rapido-rede"><header class="rapido-topo">' + selo(r.rede, true) + "<h2>" + esc(nr) + "</h2></header>" +
          '<div class="rapido-meio">' + capa + '<div class="rapido-botoes">' + botoes + "</div></div>" + (textos || '<p class="apoio">Sem legenda nesta rede.</p>') + "</article>";
      }).join("") + "</div>";
    }
    return voltarLinha("rapido") + titulo + escolha + corpo;
  };
  T.meus = function () {
    var eps = E.episodios || [];
    if (!eps.length) {
      return voltarLinha("meus") + vazio(ilustracao("vazio-videos", "tv-notebook", "vazio-ilustra"), "Nenhum vídeo pronto ainda", link("Fazer um vídeo", "#fazer", "botao gigante", "claquete"), "Quando a IA terminar, ele aparece aqui.");
    }
    var idx = Number(subRota());
    if (subRota() === "" || !(idx >= 0 && idx < eps.length)) idx = Math.max(0, eps.findIndex(function (x) { return x.pronto; }));
    var ep = eps[idx];
    var redes = ep.redes || [];
    var aba = Math.min(abaEpisodio[ep.nome] || 0, Math.max(0, redes.length - 1));
    var r = redes[aba];
    var src = r ? r.video : ep.video_base, capa = r ? r.capa : ep.capa_base;
    var deitado = r && r.rede === "youtube_longo";
    var player = src ? playerHtml(midia(src), capa ? midia(capa) : "", { classe: "player" + (deitado ? " deitado" : ""), rotulo: "Vídeo " + bonito(ep.nome), attrs: ' data-tour="player"' })
      : '<div class="exemplo player exemplo-vazio" data-tour="player">' + (capa ? '<img src="' + esc(midia(capa)) + '" alt="Capa do vídeo">' : '<span class="meta">sem vídeo ainda</span>') + "</div>";
    var abas = redes.length ? '<div class="segmentos redes-abas cheio" role="tablist" aria-label="Rede" data-tour="redes">' + redes.map(function (x, i) {
      var nome = x.rede === "youtube_shorts" ? "Shorts" : (x.rede === "youtube_longo" ? "YT longo" : esc(nomeRede(x.rede)));
      return '<button type="button" role="tab" aria-selected="' + (i === aba) + '" aria-pressed="' + (i === aba) + '" data-acao="aba" data-ep="' + esc(ep.nome) + '" data-i="' + i + '">' + selo(x.rede, true) + "<span>" + nome + "</span></button>";
    }).join("") + "</div>" : "";
    var passos;
    if (r) {
      var nr = nomeRede(r.rede);
      var baixarVideo = r.video && midia(r.video) ? '<a class="botao" href="' + esc(midia(r.video)) + '" download="' + esc(nomeArquivo(ep, r.rede)) + '">' + icone("baixar") + '<span class="rotulo">Baixar vídeo</span></a>' : '<p class="apoio">O vídeo desta rede ainda não saiu.</p>';
      var capaRede = r.capa ? '<div class="capa-rede"><img src="' + esc(midia(r.capa)) + '" alt="Capa do ' + esc(nr) + '" loading="lazy">' +
        '<a class="discreto mini" href="' + esc(midia(r.capa)) + '" download="' + esc(slugTraco(bonito(ep.nome)) + "-capa-" + r.rede + ".jpg") + '">' + icone("baixar") + "<span>Baixar capa</span></a></div>" : "";
      var textos = "";
      if (r.titulo) textos += '<p class="folha folha-titulo">' + esc(r.titulo) + "</p>" + botaoCopiar(r.titulo, "Copiar o título", "secundario", "Título copiado. Agora cole no app.");
      if (r.legenda) textos += '<p class="folha folha-legenda">' + esc(r.legenda) + "</p>" + botaoCopiar(r.legenda, r.titulo ? "Copiar a descrição" : "Copiar a legenda", "secundario", "Legenda copiada. Agora cole no app.");
      var mais = [];
      if (r.fixado) mais.push('<div class="mais-item"><p class="meta">Comentário para fixar</p><p class="folha">' + esc(r.fixado) + "</p>" + botaoCopiar(r.fixado, "Copiar o comentário", "secundario", "Comentário copiado.") + "</div>");
      if (r.ao_publicar_html) mais.push('<div class="mais-item md">' + r.ao_publicar_html + "</div>");
      if (!ESTATICO && r.caminho) mais.push('<div class="mais-item">' + botao("Abrir a pasta", 'data-acao="abrir" data-caminho="' + esc(r.caminho) + '"', "secundario", "pasta") + "</div>");
      passos = '<div class="plano passos-postar">' +
        '<div class="passo" data-tour="baixar"><span class="n">1</span><div><h2>Baixe o vídeo</h2><div class="corpo corpo-baixar">' + baixarVideo + capaRede + "</div></div></div>" +
        '<div class="passo" data-tour="legenda"><span class="n">2</span><div><h2>' + (r.titulo ? "Copie o título e a descrição" : "Copie a legenda") + '</h2><div class="corpo">' + (textos || '<p class="apoio">Sem legenda nesta rede.</p>') + "</div></div></div>" +
        '<div class="passo"><span class="n">3</span><div><h2>Poste no ' + esc(nr) + '</h2><div class="corpo">' +
        '<a class="discreto" href="#postar" data-acao="ir-postar" data-rede="' + esc(r.rede) + '">Como postar</a>' +
        (horaPostar() ? '<p class="meta">' + esc(horaPostar()) + "</p>" : "") + "</div></div></div>" +
        (mais.length ? recolhe("Mais", "Comentário para fixar e o que conferir antes de publicar", mais.join(""), ' data-mais-video="1"') : "") + "</div>";
    } else {
      var baixarBase = src ? '<a class="botao" href="' + esc(midia(src)) + '" download="' + esc((slugTraco(bonito(ep.nome)) || "video") + ".mp4") + '">' + icone("baixar") + '<span class="rotulo">Baixar vídeo</span></a>' : "";
      var baixarCapa = capa ? '<a class="discreto mini" href="' + esc(midia(capa)) + '" download="' + esc((slugTraco(bonito(ep.nome)) || "video") + "-capa.jpg") + '">' + icone("baixar") + "<span>Baixar capa</span></a>" : "";
      passos = '<div class="plano passos-postar">' + (baixarBase ? '<div class="passo" data-tour="baixar"><span class="n">1</span><div><h2>Baixe o vídeo</h2><div class="corpo corpo-baixar">' + baixarBase + baixarCapa + "</div></div></div>" : "") +
        '<p class="apoio">' + (ep.pronto ? "Este vídeo saiu sem a pasta de cada rede: a legenda e a capa de cada uma aparecem aqui quando a IA montar o pacote das redes." : "A IA ainda está terminando: a legenda e a versão de cada rede aparecem aqui quando ela acabar.") + "</p></div>";
    }
    var peds = (E.pedidos || []).filter(function (p) { return p.episodio === ep.nome; });
    var listaPeds = peds.length ? '<ul class="lista-pedidos">' + peds.map(function (p) {
      return '<li class="' + (p.feito ? "feito" : "") + '">' + icone(p.feito ? "certo" : "atualizar") + "<span><b>" + (p.feito ? "Feito" : "Esperando a IA") + ".</b> " +
        esc(limparCaminhos(String(p.texto).replace(/·\s*episódio\s*`[^`]+`\s*·\s*/, "").replace(/`/g, ""))) + "</span></li>";
    }).join("") + "</ul>" : "";
    /* Pedido de mudança: o vídeo todo ou uma cena (pelo número da folha de cenas), em linguagem de gente. */
    var mudar = ESTATICO ? "" : '<section class="plano mudar" id="mudar-' + idx + '" data-tour="mudar"><h2 class="bloco-titulo">Quer mudar alguma coisa?</h2>' +
      '<form class="pedido-cena" data-form="pedido" data-ep="' + esc(ep.nome) + '" data-nome="' + esc(bonito(ep.nome)) + '">' +
      '<div class="campo"><span class="rotulo" id="onde-' + idx + '">Onde?</span><div class="segmentos" role="radiogroup" aria-labelledby="onde-' + idx + '">' +
      '<button type="button" role="radio" aria-checked="true" aria-pressed="true" data-acao="mudar-onde" data-onde="todo">O vídeo todo</button>' +
      '<button type="button" role="radio" aria-checked="false" aria-pressed="false" data-acao="mudar-onde" data-onde="cena">Uma cena</button></div></div>' +
      '<div class="campo campo-cena" hidden>' + (ep.folha ? '<label for="pc-n-' + idx + '">Qual cena?</label>' : '<span class="rotulo">Qual cena?</span>') +
      (ep.folha ? '<button type="button" class="folha-cenas" data-acao="ampliar" data-src="' + esc(ep.folha) + '" data-titulo="As cenas do vídeo"><img src="' + esc(midia(ep.folha)) + '" alt="As cenas do vídeo, numeradas" loading="lazy"><span class="meta">Toque para ver as cenas maiores</span></button>' : "") +
      (ep.folha ? '<input class="entrada numero curto" type="number" inputmode="numeric" id="pc-n-' + idx + '" name="cena" min="1" max="400" placeholder="1">' +
        '<p class="ajuda">O número que aparece no canto de cada cena.</p>'
        : '<div class="cenas-video" role="radiogroup" aria-labelledby="pc-n-' + idx + '" data-cenas="' + esc(src ? midia(src) : "") + '"><p class="cenas-carregando">Separando as cenas do vídeo…</p></div>' +
        '<input type="hidden" name="trecho" value=""><p class="ajuda" id="pc-n-' + idx + '">Toque na cena que você quer mudar.</p>') + "</div>" +
      '<div class="campo"><label for="pc-t-' + idx + '">O que mudar?</label><textarea class="entrada" rows="2" id="pc-t-' + idx + '" name="texto" maxlength="600" placeholder="Ex.: a legenda está rápida demais"></textarea><p class="erro-msg" hidden></p></div>' +
      botao(iaPronta() ? "Mandar pra IA" : "Guardar o pedido", 'data-acao="pedido-enviar"', iaPronta() ? "" : "secundario", iaPronta() ? "seguir" : "lapis") +
      '<p class="ajuda">' + (iaPronta() ? "O pedido vai pro chat da IA aqui no painel." : "A IA faz a mudança da próxima vez que você conversar com ela.") + "</p></form>" + listaPeds + "</section>";
    var outrosEps = eps.map(function (x, i) { return [x, i]; }).filter(function (p) { return p[1] !== idx; });
    var outros = outrosEps.length ? '<section class="outros" aria-label="Outros vídeos"><h2 class="bloco-titulo">Outros vídeos</h2><ul>' + outrosEps.map(function (p) {
      var x = p[0], c = capaEp(x);
      return '<li><a class="opcao" href="#meus/' + p[1] + '" aria-pressed="false">' + (c ? '<img src="' + esc(midia(c)) + '" alt="" loading="lazy">' : '<span class="sem-capa" aria-hidden="true"></span>') +
        '<span class="texto"><strong>' + esc(bonito(x.nome)) + "</strong>" + (x.pronto ? "<small>Pronto · " + esc(quandoHumano(x.quando, true)) + "</small>" : '<small class="fazendo">A IA está fazendo</small>') + "</span></a></li>";
    }).join("") + "</ul></section>" : "";
    return voltarLinha("meus") + '<div class="grade-videos' + (outros ? "" : " sem-outros") + '"><div class="col-player">' + player + "</div>" +
      '<section class="info"><h1 class="titulo">' + esc(bonito(ep.nome)) + "</h1>" +
      '<p class="estado">' + (ep.pronto ? "<b>Pronto pra postar</b> · feito " + esc(quandoHumano(ep.quando)) : '<b class="fazendo">A IA está fazendo</b> · ' + esc(quandoHumano(ep.quando))) + "</p>" +
      (ESTATICO ? "" : '<div class="acoes acoes-video">' + link("Fazer um vídeo novo", "#fazer", "botao secundario", "claquete") +
        botao("Ver a conversa deste vídeo", 'data-acao="ia-conversa-video" data-ep="' + esc(ep.nome) + '"', "discreto", "balao") + "</div>") +
      abas + passos + mudar + "</section>" + outros + "</div>";
  };

  /* Está tudo certo? (Deu um problema): quantas coisas faltam, uma linha por item, uma ação por linha. */
  function acaoPendencia(p, classe) {
    var a = p.h.acao, i = p.item, c = "botao" + (classe ? " " + classe : "");
    if (!ESTATICO && a && a.href) return '<a class="' + c + '" href="' + esc(a.href) + '"><span class="rotulo">' + esc(a.rotulo) + "</span>" + icone("seguir") + "</a>";
    if (!ESTATICO && a && a.mudancas) return '<button type="button" class="' + c + '" data-acao="corrigir" data-mudancas="' + esc(JSON.stringify(a.mudancas)) + '"><span class="rotulo">' + esc(a.rotulo) + "</span></button>";
    if (i.pedir) return botaoCopiar(i.pedir, p.h.rotuloPedir || "Copiar pedido", classe || "", "Pedido copiado. Agora cole no chat da IA.");
    return "";
  }
  function linhaPendencia(p, classe, attrs) {
    var i = p.item;
    var det = '<details class="detalhes-ia"><summary>Ver detalhes</summary><p class="meta">' + esc(i.titulo) + ": " + esc(i.detalhe) + "</p>" +
      (i.pedir && (p.h.acao || !p.h.rotuloPedir) ? botaoCopiar(i.pedir, "Copiar pedido", "discreto", "Pedido copiado. Agora cole no chat da IA.") : "") + "</details>";
    return '<li class="pendencia"' + (attrs || "") + '><div class="texto"><h2>' + esc(p.h.titulo) + "</h2><p>" + esc(p.h.porque) + "</p>" + det + "</div>" + acaoPendencia(p, classe) + "</li>";
  }
  function textoPronto(i) {
    var t = { python: "instalado", ffmpeg: "instalado", bibliotecas: "instaladas", fontes: "prontas", licenca: "ativa", canal: "tudo respondido" }[i.id];
    if (i.id === "versao") return "versão " + (E.versao || "");
    if (i.id === "disco" && i.medida) return num1(i.medida.livre_gb) + " GB livres";
    return t || i.detalhe;
  }
  /* Mostradores: os números do computador viram desenho (barra do disco, anel do canal). */
  function anel(feitos, total, rotulo) {
    var c = 2 * Math.PI * 18, pct = total ? feitos / total : 0;
    return '<svg class="anel" viewBox="0 0 44 44" role="img" aria-label="' + esc(rotulo) + '"><circle class="anel-fundo" cx="22" cy="22" r="18"/>' +
      '<circle class="anel-cheio' + (pct >= 1 ? " completo" : "") + '" cx="22" cy="22" r="18" stroke-dasharray="' + (pct * c).toFixed(1) + " " + c.toFixed(1) + '" transform="rotate(-90 22 22)"/>' +
      '<text x="22" y="26.5" text-anchor="middle">' + feitos + "/" + total + "</text></svg>";
  }
  function mostradores() {
    var itens = (E.status || {}).itens || [];
    var por = {}; itens.forEach(function (i) { por[i.id] = i; });
    var cards = [];
    var d = por.disco && por.disco.medida;
    if (d) {
      var usado = Math.max(0, Math.min(100, (1 - d.livre_gb / d.total_gb) * 100));
      var estado = d.livre_gb < d.minimo_gb ? "falta" : (d.livre_gb < d.alerta_gb ? "aviso" : "ok");
      cards.push('<div class="mostrador ' + estado + '"><p class="meta">Espaço livre</p><p class="valor">' + num1(d.livre_gb) + " GB</p>" +
        '<div class="medidor" role="img" aria-label="' + num1(d.livre_gb) + " GB livres de " + num1(d.total_gb) + ' GB"><i style="width:' + usado.toFixed(1) + '%"></i></div>' +
        '<p class="meta">de ' + num1(d.total_gb) + " GB" + (estado === "ok" ? "" : " · bom ter mais de " + d.alerta_gb + " GB") + "</p></div>");
    }
    var ca = por.canal && por.canal.medida;
    if (ca) cards.push('<div class="mostrador ' + (ca.feitos >= ca.total ? "ok" : "falta") + '"><p class="meta">Canal</p>' + anel(ca.feitos, ca.total, ca.feitos + " de " + ca.total + " respostas do canal") +
      '<p class="meta">' + (ca.feitos >= ca.total ? "Tudo respondido" : "Faltam " + (ca.total - ca.feitos) + " respostas") + "</p></div>");
    var r = por.render;
    if (r) {
      var m = r.medida || {};
      var rapido = r.caso === "gpu" && m.dedicada;
      cards.push('<div class="mostrador ' + (r.estado === "depende" ? "espera" : r.estado) + '"><p class="meta">Placa de vídeo</p><p class="valor menor">' +
        esc(m.placa ? (rapido ? "Boa (" : "") + m.placa.replace(/^NVIDIA\s+/i, "").replace(/^(GeForce|Radeon)\s+/i, "").replace(/\s*(Laptop GPU|Graphics)$/i, "") + (rapido ? ")" : "") : "Sem placa própria") + "</p>" +
        '<p class="meta">' + (rapido ? "O vídeo sai rápido" : r.caso === "depende" ? "Testa depois das peças do programa" : r.caso === "sem_placa" ? "Sai pelo processador, mais devagar" : r.estado === "conferindo" ? "Conferindo…" : "A IA confere a placa") + "</p></div>");
    }
    var v = por.voz && por.voz.medida;
    if (v) cards.push('<div class="mostrador ' + (v.pronta ? "ok" : "falta") + '"><p class="meta">Voz</p><p class="valor menor">' + esc(String(v.provedor || "").replace(/\s*\(.*\)$/, "")) + "</p>" +
      '<p class="meta">' + (v.pronta ? "Pronta para narrar" : "Falta a chave") + "</p></div>");
    var c = E.conta || {};
    if (c.ativa) cards.push('<div class="mostrador ok"><p class="meta">Licença</p><p class="valor menor">Ativa</p><p class="meta">' + esc(textoAtualizacoes(c)) + "</p></div>");
    return cards.length ? '<div class="mostradores">' + cards.join("") + "</div>" : "";
  }
  T.problema = function () {
    var pend = pendencias();
    var n = pend.bloqueiam.length, np = pend.avisos.length;
    var titulo, apoio, imagem, extra = "";
    if (n) {
      titulo = (n === 1 ? "Falta" : "Faltam") + " <em>" + n + (n === 1 ? " coisa" : " coisas") + "</em>";
      apoio = n === 1 ? "O resto está pronto. Arrume isto e já dá pra fazer vídeo." : "Comece pela primeira. Cada uma tem um botão que resolve.";
      imagem = ilustracao("erro", "tv-cade", "cabeca-ilustra");
    } else if (pend.conferindo) {
      titulo = "Conferindo o computador"; apoio = "Leva uns segundos.";
      imagem = ilustracao("carregando", "tv-frente", "cabeca-ilustra");
      extra = esqueleto(3);
    } else if (np) {
      titulo = (np === 1 ? "Falta" : "Faltam") + ' <em class="passo">' + np + (np === 1 ? " passo" : " passos") + "</em>";
      apoio = "Já dá pra fazer vídeo. " + (np === 1 ? "Este passo deixa o vídeo melhor." : "Estes passos deixam o vídeo melhor.");
      imagem = ilustracao("tudo-pronto", "tv-notebook", "cabeca-ilustra");
    } else {
      titulo = '<span class="pronto">Está tudo pronto</span>';
      apoio = "Pode fazer o seu vídeo.";
      imagem = ilustracao("tudo-pronto", "tv-notebook", "cabeca-ilustra");
      extra = '<div class="acoes-linha">' + link("Fazer um vídeo", "#fazer", "botao gigante") + "</div>";
    }
    var tudo = botaoArrumarTudo(n ? "" : "secundario", ' data-tour="arrumar-tudo"');
    var lista = function (itens, primeiro) {
      return '<ul class="pendencias">' + itens.map(function (p, k) { return linhaPendencia(p, k === 0 && primeiro && !tudo ? "" : "secundario", k === 0 ? ' data-tour="falta"' : ""); }).join("") + "</ul>";
    };
    return voltarLinha("problema") +
      '<div class="cabeca"><div class="cabeca-texto"><h1 class="titulo" data-tour="resumo">' + titulo + '</h1><p class="lead">' + esc(apoio) + "</p>" +
      (tudo ? '<div class="acoes-linha arrumar-tudo">' + tudo + '<span class="meta">Um pedido só, com tudo o que falta.</span></div>' : "") + "</div>" + imagem + "</div>" + extra +
      (n ? lista(pend.bloqueiam, true) : (np ? lista(pend.avisos, false) : "")) +
      (pend.conferindo && n ? '<p class="meta conferindo-linha">Conferindo as peças do programa…</p>' : "") +
      (n && np ? '<section class="grupo"><h2 class="bloco-titulo">Bom arrumar, mas não impede</h2>' +
        '<ul class="pendencias">' + pend.avisos.map(function (p) { return linhaPendencia(p, "secundario"); }).join("") + "</ul></section>" : "") +
      '<details class="recolhe grupo lista-pronta" data-tour="pronto"><summary><b class="cor-pronto">Pronto (' + pend.prontos.length + ")</b><span>" +
      esc(pend.prontos.length + (pend.prontos.length === 1 ? " coisa já está certa" : " coisas já estão certas")) + "</span>" + icone("abaixo") + "</summary>" +
      '<div class="recolhe-corpo"><ul class="lista-pronto">' + pend.prontos.map(function (p) {
        return "<li>" + icone(p.item.estado === "depende" ? "atualizar" : "certo") + "<span><b>" + esc(p.h.curto) + "</b> " + esc(p.item.estado === "depende" ? limparCaminhos(p.item.detalhe) : textoPronto(p.item)) + "</span></li>";
      }).join("") + "</ul></div></details>" +
      (mostradores() ? '<section class="grupo"><h2 class="bloco-titulo">Seu computador</h2>' + mostradores() + "</section>" : "") +
      '<div class="rodape">' + (ESTATICO ? "" : '<button type="button" class="botao secundario" data-acao="verificar" data-tour="conferir"' + (pend.rodando ? " disabled" : "") + ">" +
        (pend.rodando ? '<span class="girando" aria-hidden="true"></span>' : icone("atualizar")) + '<span class="rotulo">' + (pend.rodando ? "Conferindo" : "Já arrumei: conferir de novo") + "</span></button>") +
      '<span class="meta">' + (pend.quando ? "Conferido " + esc(quandoHumano(pend.quando)) : "Ainda não conferido") + "</span></div>";
  };

  /* ------------------------------------------------------------ assistente do canal (uma pergunta por tela) */
  var PASSOS_MAGO = ["assunto", "nome", "publico", "caminho", "estilo", "redes"];
  var ASSUNTOS = [["Bichos esquisitos", "bichos esquisitos e curiosidades da natureza"], ["Histórias de mistério", "histórias reais de mistério"],
    ["Comédia do dia a dia", "comédia do dia a dia em família"], ["Curiosidades do mundo", "curiosidades do mundo, explicadas em 1 minuto"],
    ["Dinheiro e trabalho", "dicas de dinheiro para quem está começando"]];
  var NOMES_ASSUNTO = {
    "bichos esquisitos e curiosidades da natureza": ["Bicho Esquisito", "Natureza Maluca", "Bicho de Outro Mundo"],
    "histórias reais de mistério": ["Caso Sem Fim", "Mistério de Bolso", "Arquivo Estranho"],
    "comédia do dia a dia em família": ["Família Sem Filtro", "Casa Caótica", "Rindo de Nervoso"],
    "curiosidades do mundo, explicadas em 1 minuto": ["Mundo em 1 Minuto", "Curioso Demais", "Você Sabia Disso"],
    "dicas de dinheiro para quem está começando": ["Dinheiro Sem Drama", "Bolso Cheio", "Primeiro Salário"]
  };
  var PUBLICOS = [["Adultos de 18 a 35 anos", "adultos de 18 a 35 anos, curiosos, que assistem no celular"],
    ["Adultos de 35 a 60 anos", "adultos de 35 a 60 anos, que assistem no celular"], ["Adultos de todas as idades", "público geral adulto, de todas as idades"]];
  function titulo3(t) {
    var pequenas = ["de", "da", "do", "das", "dos", "e", "em", "a", "o"];
    return String(t || "").split(/\s+/).filter(Boolean).map(function (p, i) { p = p.toLowerCase(); return i && pequenas.indexOf(p) >= 0 ? p : p.charAt(0).toUpperCase() + p.slice(1); }).join(" ");
  }
  /* Três nomes prontos para o assunto escolhido (os do assunto pronto, ou montados a partir do que a pessoa escreveu). */
  function nomesSugeridos(nicho) {
    if (NOMES_ASSUNTO[nicho]) return NOMES_ASSUNTO[nicho].slice();
    var palavras = String(nicho || "").replace(/[,.;:!?].*$/, "").split(/\s+/).filter(function (p) { return p.length > 2 && ["para", "com", "que", "sobre", "dicas"].indexOf(p.toLowerCase()) < 0; });
    if (!palavras.length) return ["Canal Curioso", "Vídeo do Dia", "Mundo em 1 Minuto"];
    var base = titulo3(palavras.slice(0, 2).join(" "));
    var um = titulo3(palavras[0]);
    return [base, um + " em 1 Minuto", "Mundo " + (/^[aeiou]/i.test(um) ? "de " : "de ") + um];
  }
  function salvarMago() { gravarLocal("mago", mago); }
  function iniciarMago() {
    if (mago && mago.r) return;
    var v = P().valores || { canal: {}, roteiro: {}, redes: {} };
    /* O estilo começa vazio: a pessoa escolhe (ou toca em "escolhe por mim"). Na 1ª vez abre com as boas-vindas. */
    mago = { passo: precisaMago() ? -1 : 0, r: { nome: v.canal.nome || "", arroba: v.canal.arroba || "", arrobaMexido: !!v.canal.arroba, nicho: v.canal.nicho || "",
      publico: v.canal.publico || "", caminho: v.canal.caminho || "", estilo: "", redes: (v.redes.escolhidas || []).slice() }, outro: {} };
    salvarMago();
  }
  /* Preenche o que falta com o recomendado (do passo `de` em diante). */
  function completarMago(de) {
    var r = mago.r;
    PASSOS_MAGO.slice(de).forEach(function (p) {
      if (p === "assunto" && !r.nicho) r.nicho = ASSUNTOS[3][1];
      if (p === "nome" && !r.nome) { r.nome = nomesSugeridos(r.nicho)[0]; r.arroba = slug(r.nome); r.arrobaMexido = false; }
      if (p === "publico" && !r.publico) r.publico = PUBLICOS[0][1];
      if (p === "caminho" && !r.caminho) r.caminho = recomendado("canal", "caminho") || "gratis";
      if (p === "estilo" && !r.estilo) r.estilo = recomendado("roteiro", "estilo_padrao") || "top5";
      if (p === "redes" && !r.redes.length) r.redes = (recomendado("redes", "escolhidas") || ["instagram"]).slice();
    });
  }
  function opcaoMago(rotulo, detalhe, valorOp, atual, acao, marcadorIc) {
    var marcado = valorOp === atual;
    return '<button type="button" class="opcao" role="radio" aria-checked="' + marcado + '" aria-pressed="' + marcado + '" data-acao="' + acao + '" data-valor="' + esc(valorOp) + '">' +
      '<span class="texto"><strong>' + esc(rotulo) + "</strong>" + (detalhe ? "<small>" + esc(detalhe) + "</small>" : "") + "</span>" +
      '<span class="marcador">' + (marcado ? icone("certo") : (marcadorIc ? icone(marcadorIc) : "")) + "</span></button>";
  }
  T.arrumar = function () {
    if (mago && mago.fim) {
      return '<div class="mago-fim">' + ilustra("tv-rede", "fim-ilustra") + '<h1 class="titulo">Pronto!</h1><p class="lead">Seu canal está arrumado. Agora é fazer o primeiro vídeo.</p>' +
        '<div class="acoes">' + link("Fazer meu primeiro vídeo", "#fazer", "botao gigante", "", ' data-acao="mago-sair"') + "</div>" +
        '<p class="meta">Para abrir depois, clique duas vezes no ícone Temporada Viral na área de trabalho.</p>' +
        link("Voltar ao início", "#inicio", "discreto", "", ' data-acao="mago-sair"') + "</div>";
    }
    if (ESTATICO) return voltarLinha("arrumar") + cabeca("Arrumar meu canal", "Na versão só para ver não dá para mudar o canal. Peça no chat da IA.");
    if (!(mago && mago.r) && !precisaMago()) {
      var cv = P().valores && P().valores.canal || {};
      return voltarLinha("arrumar") + '<section class="mago-fim canal-pronto">' + ilustra("tv-rede", "fim-ilustra") + '<h1 class="titulo">Seu canal já está pronto</h1>' +
        '<p class="lead">' + esc(cv.nome || "O canal") + (cv.arroba ? " (@" + esc(cv.arroba) + ")" : "") + " já tem nome, assunto e público. Dá pra mudar cada um em Meu canal.</p>" +
        '<div class="acoes">' + link("Fazer um vídeo", "#fazer", "botao gigante", "claquete") + botao("Refazer as perguntas", 'data-acao="refazer"', "secundario", "atualizar") + "</div>" +
        link("Ver meu canal", "#canal", "discreto") + "</section>";
    }
    iniciarMago();
    if (mago.passo < 0) {
      return '<section class="pergunta boas-vindas" id="mago" aria-labelledby="mago-titulo">' + ilustracao("ideias", "tv-apontando", "boas-ilustra") +
        '<h1 class="titulo" id="mago-titulo">Oi! Vamos deixar o canal com a sua cara</h1>' +
        '<p class="lead">São 6 perguntas rápidas, com resposta pronta. Dá pra mudar tudo depois.</p>' +
        '<div class="acoes">' + botao("Começar", 'data-acao="mago-comecar"', "gigante", "seguir") + "</div></section>";
    }
    var p = mago.passo, r = mago.r, etapa = PASSOS_MAGO[p], corpo = "", titulo = "", apoio = "";
    mago.outro = mago.outro || {};
    if (etapa === "assunto") {
      var outroA = mago.outro.assunto || (r.nicho && !ASSUNTOS.some(function (x) { return x[1] === r.nicho; }));
      titulo = "Sobre o que é o seu canal?"; apoio = "Toque no assunto mais parecido. Dá pra escrever o seu.";
      corpo = '<div class="respostas" role="radiogroup" aria-label="Assunto">' + ASSUNTOS.map(function (x) { return opcaoMago(x[0], "", x[1], outroA ? "" : r.nicho, "mago-assunto"); }).join("") +
        opcaoMago("Escrever outro assunto", "Do jeito que você falaria", "__outro", outroA ? "__outro" : "", "mago-assunto", "lapis") + "</div>" +
        '<div class="campo campo-outro"' + (outroA ? "" : " hidden") + '><label for="mg-nicho">Qual é o assunto?</label><textarea id="mg-nicho" class="entrada" rows="2" data-mago="nicho" maxlength="300" placeholder="Ex.: receitas de bolo caseiro">' + esc(outroA ? r.nicho : "") + "</textarea>" +
        '<p class="erro-msg" hidden></p></div>';
    } else if (etapa === "nome") {
      var sug = nomesSugeridos(r.nicho);
      if (r.nome && sug.indexOf(r.nome) < 0 && !mago.outro.nome) sug.unshift(r.nome);
      sug = sug.slice(0, 4);
      var outroN = !!mago.outro.nome;
      titulo = "Como vai se chamar seu canal?";
      apoio = '<span class="so-pc">Separamos ' + sug.length + " nomes para um canal de " + esc(assuntoMago(r.nicho)) + ". </span>Toque no que mais gostar.";
      corpo = '<div class="respostas" role="radiogroup" aria-label="Nome do canal">' + sug.map(function (n) { return opcaoMago(n, "@" + slug(n), n, outroN ? "" : r.nome, "mago-nome"); }).join("") +
        opcaoMago("Escrever outro nome", "Você digita e a gente monta o @", "__outro", outroN ? "__outro" : "", "mago-nome", "lapis") + "</div>" +
        '<div class="campo campo-outro"' + (outroN ? "" : " hidden") + '><label for="mg-nome">Nome do canal</label>' +
        '<input type="text" id="mg-nome" class="entrada" data-mago="nome" maxlength="60" value="' + esc(outroN ? r.nome : "") + '" placeholder="Ex.: Bicho Esquisito" autocomplete="off">' +
        '<p class="ajuda">Seu @ vai ser <b id="mg-arroba-ver">@' + esc(r.arroba || slug(r.nome) || "…") + '</b> <button type="button" class="discreto mini" data-acao="mago-mudar-arroba">Mudar o @</button></p>' +
        '<p class="erro-msg" hidden></p></div>' +
        '<div class="campo campo-arroba" hidden><label for="mg-arroba">@ do canal</label><div class="com-prefixo"><span aria-hidden="true">@</span><input type="text" id="mg-arroba" class="entrada" data-mago="arroba" maxlength="30" value="' + esc(r.arroba) + '" spellcheck="false" autocomplete="off" autocapitalize="none"></div><p class="ajuda">Sem espaço e sem acento.</p></div>';
    } else if (etapa === "publico") {
      var outroP = mago.outro.publico || (r.publico && !PUBLICOS.some(function (x) { return x[1] === r.publico; }));
      titulo = "Quem vai assistir?"; apoio = "Pense em quem você quer que veja.";
      corpo = '<div class="respostas" role="radiogroup" aria-label="Quem assiste">' + PUBLICOS.map(function (x) { return opcaoMago(x[0], "", x[1], outroP ? "" : r.publico, "mago-publico"); }).join("") +
        opcaoMago("Escrever quem assiste", "", "__outro", outroP ? "__outro" : "", "mago-publico", "lapis") + "</div>" +
        '<div class="campo campo-outro"' + (outroP ? "" : " hidden") + '><label for="mg-publico">Quem assiste?</label><textarea id="mg-publico" class="entrada" rows="2" data-mago="publico" maxlength="300">' + esc(outroP ? r.publico : "") + "</textarea><p class=\"erro-msg\" hidden></p></div>";
    } else if (etapa === "caminho") {
      titulo = "Grátis ou pago?"; apoio = "Os dois fazem os mesmos vídeos. Dá pra trocar depois.";
      corpo = '<div class="respostas" role="radiogroup" aria-label="Caminho">' + opcaoMago("Grátis", "Não paga nada. Só no computador e demora mais.", "gratis", r.caminho, "mago-caminho") +
        opcaoMago("Recomendado (pago)", "Paga a voz ElevenLabs (a partir de US$ 6 por mês) e o plano da IA, Claude Pro (US$ 20 por mês). O resto é grátis.", "recomendado", r.caminho, "mago-caminho") + "</div>";
    } else if (etapa === "estilo") {
      titulo = "Que tipo de vídeo?"; apoio = "Toque no play para ver um exemplo de 10 segundos.";
      corpo = '<ul class="catalogo catalogo-mago" role="radiogroup" aria-label="Estilo">' + estilosLista().map(function (x) {
        var marcado = x.id === r.estilo, capa = capaEstilo(x);
        return '<li class="' + (marcado ? "acende" : "") + '"><button type="button" class="capa-estilo" role="radio" aria-checked="' + marcado + '" data-acao="mago-estilo" data-id="' + esc(x.id) + '">' +
          '<span class="moldura">' + (capa ? '<img src="' + esc(capa) + '" alt="" loading="lazy">' : "") + (marcado ? '<span class="marcador">' + icone("certo") + "</span>" : "") + "</span><b>" + esc(nomeEstilo(x.id)) + "</b><span>" + esc(x.duracao) + "</span></button>" +
          (x.exemplo && x.exemplo.video ? '<button type="button" class="ver" data-acao="exemplo" data-id="' + esc(x.id) + '" aria-label="Ver o exemplo de ' + esc(nomeEstilo(x.id)) + '">' + icone("tocar") + "</button>" : "") + "</li>";
      }).join("") + '<li class="criar-estilo"><button type="button" class="capa-estilo" data-acao="mago-criar-estilo"><span class="moldura">' + ilustra("tv-apontando", "figura-criar") + "</span>" +
        "<b>Criar meu estilo</b><span>cores e personagens só seus</span></button></li></ul>";
    } else {
      titulo = "Onde você vai postar?"; apoio = "Pode ligar mais de uma. Cada vídeo sai pronto pra cada rede.";
      var rec = recomendado("redes", "escolhidas") || [];
      var todas = (meta("redes", "escolhidas") || { opcoes: Object.keys(REDES) }).opcoes;
      var linhaRede = function (o) {
        var lig = r.redes.indexOf(o) >= 0;
        return '<li><button type="button" class="opcao linha-rede" role="switch" aria-checked="' + lig + '" data-acao="mago-rede" data-valor="' + esc(o) + '">' + selo(o) +
          '<span class="texto"><strong>' + esc(nomeRede(o)) + "</strong><small>" + esc((REDES[o] || [])[3] || "") + "</small></span>" +
          '<span class="alternador" aria-hidden="true"><span class="trilho"></span><span class="palavra">' + (lig ? "Sim" : "Não") + "</span></span></button></li>";
      };
      var outrasR = todas.filter(function (o) { return rec.indexOf(o) < 0; });
      corpo = '<div class="grupos-redes"><h2 class="grupo-titulo">Recomendadas <span class="etiqueta">recomendado</span></h2><ul class="lista-redes">' +
        todas.filter(function (o) { return rec.indexOf(o) >= 0; }).map(linhaRede).join("") + "</ul>" +
        (outrasR.length ? '<h2 class="grupo-titulo">Outras</h2><ul class="lista-redes">' + outrasR.map(linhaRede).join("") + "</ul>" : "") + "</div>";
    }
    var ultimo = p === PASSOS_MAGO.length - 1;
    return '<div class="passos-mago"><button type="button" class="discreto claro sem-linha" data-acao="mago-voltar">' + icone("voltar") + "<span>Voltar</span></button>" +
      '<div class="trilho6" aria-hidden="true">' + PASSOS_MAGO.map(function (x, i) { return '<i class="' + (i < p ? "feito" : (i === p ? "atual" : "")) + '"></i>'; }).join("") + "</div>" +
      '<span class="conta">Passo ' + (p + 1) + " de " + PASSOS_MAGO.length + "</span></div>" +
      '<section class="pergunta" id="mago" aria-labelledby="mago-titulo"><h1 class="titulo" id="mago-titulo">' + esc(titulo) + '</h1><p class="lead">' + apoio + "</p>" + corpo +
      '<p class="erro-msg msgs-mago" role="alert" hidden></p>' +
      '<div class="acoes acoes-mago">' + botao(ultimo ? "Terminar" : "Continuar", 'data-acao="mago-seguir"', "gigante") +
      botao("Não sei, escolhe por mim", 'data-acao="mago-nao-sei"', "secundario") + "</div></section>" +
      '<aside class="lado-mago" aria-hidden="true"><span class="mao">dá pra mudar depois</span>' +
      '<svg class="seta" viewBox="0 0 70 60" fill="none" stroke="#FFD23F" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8c22-4 44 6 52 30"/><path d="m48 32 10 8 6-12"/></svg>' + ilustra("tv-apontando") + "</aside>";
  };
  function assuntoMago(nicho) { var a = ASSUNTOS.filter(function (x) { return x[1] === nicho; })[0]; return (a ? a[0] : String(nicho || "").split(/[,.;]/)[0]).toLowerCase(); }
  function magoLer() {
    var box = document.getElementById("mago");
    if (!box || !mago) return;
    box.querySelectorAll("[data-mago]").forEach(function (el) { if (!el.closest("[hidden]")) mago.r[el.dataset.mago] = el.value; });
    var ar = main.querySelector("#mg-arroba");
    if (ar && !ar.closest("[hidden]")) mago.r.arroba = ar.value;
    if (!mago.r.arrobaMexido) mago.r.arroba = slug(mago.r.nome);
    mago.r.arroba = String(mago.r.arroba || "").replace(/^@/, "").toLowerCase();
    salvarMago();
  }
  function magoIr(passo) {
    mago.passo = Math.max(0, Math.min(PASSOS_MAGO.length - 1, passo));
    salvarMago(); render(); window.scrollTo(0, 0);
    var el = main.querySelector('#mago .opcao[aria-pressed="true"], #mago .opcao, #mago .capa-estilo, #mago .botao'); if (el) el.focus({ preventScroll: true });
  }
  function magoMsg(t) {
    var m = main.querySelector(".campo-outro:not([hidden]) .erro-msg") || main.querySelector(".msgs-mago");
    main.querySelectorAll(".erro-msg").forEach(function (x) { if (x !== m) { x.hidden = true; } });
    main.querySelectorAll(".campo-outro").forEach(function (c) { c.classList.toggle("erro", !!t && c.contains(m)); });
    if (!m) return;
    m.hidden = !t; m.innerHTML = t ? icone("aviso") + "<span></span>" : "";
    if (t) m.lastChild.textContent = t;
  }
  function magoValido() {
    var r = mago.r, etapa = PASSOS_MAGO[mago.passo];
    if (etapa === "assunto" && String(r.nicho || "").trim().length < 3) return mago.outro.assunto ? "Escreva pelo menos 3 letras." : "Toque num assunto.";
    if (etapa === "nome" && String(r.nome || "").trim().length < 3) return mago.outro.nome ? "Escreva pelo menos 3 letras." : "Toque num nome.";
    if (etapa === "nome" && r.arroba && !/^[a-z0-9._]{1,30}$/.test(r.arroba)) return "O @ só aceita letras sem acento, números, ponto e traço baixo.";
    if (etapa === "publico" && String(r.publico || "").trim().length < 3) return mago.outro.publico ? "Escreva pelo menos 3 letras." : "Toque em quem vai assistir.";
    if (etapa === "caminho" && !r.caminho) return "Toque em Grátis ou Recomendado.";
    if (etapa === "estilo" && !r.estilo) return "Toque num estilo.";
    if (etapa === "redes" && !r.redes.length) return "Ligue pelo menos uma rede.";
    return "";
  }
  function magoAvancar() {
    var erro = magoValido();
    if (erro) { magoMsg(erro); return; }
    if (mago.passo === PASSOS_MAGO.length - 1) { magoTerminar(); return; }
    magoIr(mago.passo + 1);
  }
  function magoTerminar() {
    var r = mago.r;
    completarMago(0);
    var canal = { nicho: r.nicho, publico: r.publico, caminho: r.caminho, nome: r.nome.trim(), arroba: r.arroba || slug(r.nome) };
    var mud = { canal: canal, roteiro: { estilo_padrao: r.estilo }, redes: { escolhidas: r.redes } };
    magoMsg("");
    api("POST", "/api/prefs", { mudancas: mud }).then(function (res) {
      if (!res.ok) { magoMsg((res.erros || [res.msg]).join(" ")); return; }
      mago = { fim: true }; gravarLocal("mago", null); gravarLocal("magoPulado", false);
      recarregarTela().then(function () { window.scrollTo(0, 0); toast("Canal salvo. A IA usa isso a partir do próximo vídeo."); });
    });
  }
  function magoEscolha(b, campo, chaveOutro) {
    var caixa = main.querySelector(".campo-outro");
    main.querySelectorAll("#mago .respostas .opcao").forEach(function (x) {
      var m = x === b; x.setAttribute("aria-pressed", String(m)); x.setAttribute("aria-checked", String(m));
      var mk = x.querySelector(".marcador"); if (mk) mk.innerHTML = m ? icone("certo") : (x.dataset.valor === "__outro" ? icone("lapis") : "");
    });
    magoMsg("");
    if (b.dataset.valor === "__outro") {
      mago.outro[chaveOutro] = true; mago.r[campo] = ""; salvarMago();
      if (caixa) { caixa.hidden = false; var c = caixa.querySelector("input, textarea"); c.value = ""; c.focus(); }
      return;
    }
    mago.outro[chaveOutro] = false;
    if (caixa) caixa.hidden = true;
    var ca = main.querySelector(".campo-arroba"); if (ca) ca.hidden = true;
    mago.r[campo] = b.dataset.valor;
    if (campo === "nome") { mago.r.arroba = slug(b.dataset.valor); mago.r.arrobaMexido = false; }
    salvarMago();
  }

  /* ------------------------------------------------------------ a voz dos vídeos */
  var VOZES = [
    ["gemini", "Google", "Voz grátis", "Grátis", "com limite por dia", "Fala bem em português. Se o limite do dia acabar, o kit espera e tenta de novo.", "GEMINI_API_KEY", "turquesa"],
    ["kokoro", "Kokoro", "Voz grátis sem internet", "Grátis", "sem limite", "Funciona sem internet e não manda o texto pra ninguém. Soa mais robótica.", "", "areia"],
    ["elevenlabs", "ElevenLabs", "Voz paga", "Plano mensal", "a partir do Starter", "A voz mais natural, com emoção. Libera uso comercial dos vídeos.", "elevenlabs", "sol"]
  ];
  var CHAVES = {
    elevenlabs: ["a ElevenLabs", "https://elevenlabs.io/app/developers/api-keys", "Entre no site da ElevenLabs e assine o plano."],
    GEMINI_API_KEY: ["a voz grátis do Google", "https://aistudio.google.com/app/apikey", "Entre no Google AI Studio com a sua conta do Google."],
    OPENAI_API_KEY: ["a OpenAI (imagens)", "https://platform.openai.com/api-keys", "Entre no site da OpenAI e coloque crédito na conta."]
  };
  function calcTexto(cred) {
    cred = Number(String(cred || "").replace(/\./g, "").replace(",", "."));
    if (!cred) return '<p>Dá mais ou menos</p><p class="grande">? vídeos</p><p class="apoio">Escreva os créditos do seu plano acima.</p>';
    var a = Math.floor(cred / 2500), b = Math.floor(cred / 1500);
    return "<p>Dá mais ou menos</p><p class=\"grande\">" + (b < 1 ? "menos de 1 vídeo" : (a === b ? a : a + " a " + b) + (b === 1 ? " vídeo" : " vídeos")) + "</p>" +
      '<p class="apoio">de 2 minutos por mês. Cada um gasta de 1.500 a 2.500 créditos.</p>';
  }
  /* Telas esquemáticas do site da chave (desenho do painel, não print de terceiros): onde fica cada botão. */
  function telaEsquema(endereco, corpo) {
    return '<div class="tela-esq" aria-hidden="true"><div class="esq-barra"><i></i><i></i><i></i><span>' + esc(endereco) + '</span></div><div class="esq-corpo">' + corpo + "</div></div>";
  }
  var GUIAS_CHAVE = {
    GEMINI_API_KEY: [
      ["Abra o Google AI Studio e entre com a sua conta do Google. Lá, toque em “Get API key”.",
        telaEsquema("aistudio.google.com", '<span class="esq-logo">Google AI Studio</span><span class="esq-menu"><i></i><i></i></span><span class="esq-botao destaque">Get API key</span>')],
      ["Toque em “Create API key” e copie o código que aparece. Ele começa com AIza.",
        telaEsquema("aistudio.google.com", '<span class="esq-botao destaque">Create API key</span><span class="esq-chave">AIza••••••••••••<b>copiar</b></span>')],
      ["Cole aqui embaixo. A gente testa antes de salvar.", ""]
    ],
    elevenlabs: [
      ["Entre no site da ElevenLabs e assine o plano. Depois abra “API Keys”.",
        telaEsquema("elevenlabs.io", '<span class="esq-logo">ElevenLabs</span><span class="esq-menu"><i></i><i></i></span><span class="esq-botao destaque">API Keys</span>')],
      ["Toque em “Create API key” e copie o código que aparece.",
        telaEsquema("elevenlabs.io", '<span class="esq-botao destaque">Create API key</span><span class="esq-chave">sk_••••••••••••<b>copiar</b></span>')],
      ["Cole aqui embaixo. A gente testa antes de salvar.", ""]
    ],
    OPENAI_API_KEY: [
      ["Entre no site da OpenAI e coloque crédito na conta. Depois abra “API keys”.", ""],
      ["Toque em “Create new secret key” e copie o código.", ""],
      ["Cole aqui embaixo. A gente testa antes de salvar.", ""]
    ]
  };
  T.voz = function () {
    var ch = E.chaves || {};
    var prov = valor("voz", "provedor") || "gemini";
    var atualVoz = VOZES.filter(function (v) { return v[0] === prov; })[0] || VOZES[0];
    var pronta = !atualVoz[6] || !!ch[atualVoz[6]];
    /* Uma ação principal: ligar a voz em uso se ela não funciona; senão, conectar a paga. */
    var principal = !pronta ? prov : (!ch.elevenlabs && prov !== "elevenlabs" ? "elevenlabs" : "");
    var alvoChave = vozConectar || (!pronta && atualVoz[6] ? atualVoz[6] : (ch.GEMINI_API_KEY ? "elevenlabs" : "GEMINI_API_KEY"));
    var linhas = VOZES.map(function (v) {
      var emUso = v[0] === prov, temChave = !v[6] || !!ch[v[6]];
      var acao;
      if (emUso && temChave) acao = '<span class="em-uso">' + icone("certo") + "Em uso agora</span>";
      else if (!temChave) acao = botao("Conectar", 'data-acao="voz-conectar" data-chave="' + v[6] + '"', principal === v[0] ? "" : "secundario");
      else acao = botao("Usar esta", 'data-acao="voz-usar" data-id="' + v[0] + '"', "secundario");
      var attrs = v[0] === "elevenlabs" ? ' data-tour="paga"' : "";
      return '<div class="linha' + (emUso ? " atual" : "") + '" role="row"' + attrs + '><div class="quem" role="cell"><span class="icone-voz" style="background:var(--' + v[7] + ')">' + icone("som") + "</span>" +
        "<div><b>" + esc(v[1]) + "</b><small>" + esc(emUso && !temChave ? "Escolhida, falta a chave" : v[2]) + "</small></div></div>" +
        '<div class="preco' + (v[3] === "Grátis" ? " gratis" : "") + '" role="cell">' + esc(v[3]) + "<small>" + esc(v[4]) + "</small></div>" +
        '<p class="ganha" role="cell">' + esc(v[5]) + '</p><div class="acao" role="cell">' + acao + "</div></div>";
    }).join("");
    var k = CHAVES[alvoChave] || CHAVES.elevenlabs, nomeChave = CHAVES[alvoChave] ? alvoChave : "elevenlabs";
    var tem = !!ch[nomeChave], fim = chaveSalva[nomeChave];
    var guia = GUIAS_CHAVE[nomeChave];
    var passosHtml = guia.map(function (g, n) {
      var extra = n === 0 ? '<a class="discreto" href="' + k[1] + '" target="_blank" rel="noopener noreferrer">' + icone("abrir") + '<span>Abrir o site</span><span class="so-leitor"> (abre em outra aba)</span></a>' : "";
      if (n === 2) {
        extra = ESTATICO ? '<p class="apoio">Na versão só para ver não dá para salvar. Abra o painel no computador.</p>' :
          '<form class="campo" data-form="chave" data-nome="' + nomeChave + '"><div class="chave"><label class="so-leitor" for="ch-' + nomeChave + '">Chave de ' + esc(k[0]) + "</label>" +
          '<input class="entrada" type="password" id="ch-' + nomeChave + '" name="valor" autocomplete="off" spellcheck="false" autocapitalize="off" placeholder="' + (tem ? "cole a chave nova aqui" : "cole a chave aqui") + '">' +
          botao("Testar e salvar", 'data-acao="chave-enviar"', "secundario") + '</div><p class="ajuda msg-chave" aria-live="polite"></p></form>';
      }
      return '<li><span class="n">' + (n + 1) + "</span><div><p>" + esc(g[0]) + "</p>" + (g[1] || "") + extra + "</div></li>";
    }).join("");
    var conectar = '<section class="conectar" id="conectar" data-tour="passos"><h2 class="bloco-titulo">Conectar ' + esc(k[0]) + "</h2>" +
      (tem ? '<p class="salvo-chave">' + icone("certo") + "Chave salva" + (fim ? " (termina em …" + esc(fim) + ")" : "") + ". Já funciona. Dá pra trocar abaixo.</p>" : "") +
      "<ol>" + passosHtml + "</ol>" +
      '<p class="seguranca">A chave é como uma senha: fica só neste computador. Nunca cole a chave no chat da IA.</p>' +
      '<button type="button" class="discreto mini" data-acao="tutorial" data-id="chaves">Ver o passo a passo completo</button></section>';
    /* A conta de quantos vídeos cabem só faz sentido para a ElevenLabs. */
    var mostraCalc = nomeChave === "elevenlabs" || prov === "elevenlabs";
    var limite = ultimoSaldo && ultimoSaldo.limite ? num1(ultimoSaldo.limite) : "";
    var calc = mostraCalc ? '<aside class="plano calculadora" data-tour="calculadora"><h2 class="bloco-titulo">Quantos vídeos cabem no plano?</h2>' +
      '<div class="campo"><label for="calc-cred">Créditos do seu plano por mês</label><input id="calc-cred" class="entrada numero" inputmode="numeric" autocomplete="off" placeholder="30.000" value="' + esc(limite) + '" data-acao-mudar="calc">' +
      '<p class="ajuda">Está na página do plano, no site da ElevenLabs.</p></div><div class="resultado" id="calc-res" aria-live="polite">' + calcTexto(limite) + "</div></aside>" : "";
    var outras = true ? recolhe("Outras chaves", "Imagens geradas, só para novela anime e narrado sem rosto; e trocar as chaves salvas",
      '<ul class="lista-chaves">' + [["OPENAI_API_KEY", "OpenAI", "Imagens geradas, só nos estilos novela anime e narrado sem rosto."], ["GEMINI_API_KEY", "Google", "A voz grátis."], ["elevenlabs", "ElevenLabs", "A voz paga."]].map(function (x) {
        return "<li><div><b>" + esc(x[1]) + "</b><span>" + esc(x[2]) + "</span></div><span class=\"meta\">" + (ch[x[0]] ? "Chave salva" : "Sem chave") + "</span>" +
          (ESTATICO ? "" : botao(ch[x[0]] ? "Trocar" : "Colocar", 'data-acao="voz-conectar" data-chave="' + x[0] + '"', "secundario")) + "</li>";
      }).join("") + "</ul>") : "";
    return voltarLinha("voz") + cabeca("A voz dos vídeos", (pronta ? (prov === "elevenlabs" ? "Seus vídeos falam com a voz paga, a mais natural." : "Seus vídeos já falam com a voz grátis. A paga soa mais natural.") : "A voz escolhida ainda não está ligada. Conecte e pronto."), ilustracao("voz", "tv-frente", "cabeca-ilustra pequena")) +
      '<div class="comparar" role="table" aria-label="Vozes" data-tour="comparar"><div class="linha cab" role="row"><span role="columnheader">Voz</span><span role="columnheader">Quanto custa</span><span role="columnheader">O que você ganha</span><span role="columnheader"><span class="so-leitor">Ação</span></span></div>' + linhas + "</div>" +
      '<div class="baixo' + (calc ? "" : " so-conectar") + '">' + conectar + calc + "</div>" + outras;
  };

  /* ------------------------------------------------------------ como postar (o vídeo está no computador) */
  var POSTAR = {
    instagram: ["https://www.instagram.com/", "Clique em “Criar” (o + do menu), escolha o vídeo baixado, cole a legenda e clique em “Compartilhar”.", "Toque no +, escolha Reel e o vídeo, cole a legenda e toque em Compartilhar."],
    tiktok: ["https://www.tiktok.com/upload", "Escolha o vídeo baixado, cole a legenda e clique em “Publicar”.", "Toque no +, depois em Carregar, escolha o vídeo, cole a legenda e toque em Postar."],
    youtube_shorts: ["https://studio.youtube.com/", "Clique em “Criar” e depois em “Enviar vídeos”, escolha o vídeo, cole o título e a descrição e publique. Vídeo em pé de até 3 minutos vira Short sozinho.", "Toque no +, depois em Short, escolha o vídeo, cole o título e a legenda e toque em Enviar."],
    youtube_longo: ["https://studio.youtube.com/", "Clique em “Criar” e depois em “Enviar vídeos”, escolha o vídeo, cole o título e a descrição e publique.", "Toque no +, depois em Enviar um vídeo, escolha o vídeo, cole o título e a descrição e publique."],
    kwai: ["", "", "Toque no botão de câmera, escolha o vídeo na galeria, cole a legenda e toque em Publicar."]
  };
  var modoPostar = "pc";
  function videoParaPostar(rede) {
    var eps = (E.episodios || []).filter(function (x) { return x.pronto; });
    for (var i = 0; i < eps.length; i++) {
      var r = (eps[i].redes || []).filter(function (x) { return x.rede === rede; })[0];
      if (r) return { ep: eps[i], r: r };
    }
    return null;
  }
  T.postar = function () {
    var escolhidas = valor("redes", "escolhidas") || [];
    var redes = Object.keys(POSTAR).filter(function (r) { return escolhidas.indexOf(r) >= 0; });
    if (!redes.length) redes = ["instagram", "tiktok", "youtube_shorts"];
    if (redes.indexOf(redePostar) < 0) redePostar = redes[0];
    var dados = POSTAR[redePostar], nr = nomeRede(redePostar);
    var semPc = !dados[0];
    var modo = semPc ? "cel" : modoPostar;
    var v = videoParaPostar(redePostar);
    var pegar = v ? '<div class="acoes">' + (v.r.video && midia(v.r.video) ? '<a class="botao secundario" href="' + esc(midia(v.r.video)) + '" download="' + esc(nomeArquivo(v.ep, redePostar)) + '">' + icone("baixar") + '<span class="rotulo">Baixar o vídeo</span></a>' : "") +
      (v.r.legenda ? botaoCopiar(v.r.legenda, v.r.titulo ? "Copiar a descrição" : "Copiar a legenda", "secundario", "Legenda copiada.") : "") +
      (v.r.titulo ? botaoCopiar(v.r.titulo, "Copiar o título", "secundario", "Título copiado.") : "") + "</div>" +
      '<p class="meta">Do vídeo “' + esc(bonito(v.ep.nome)) + "”. Outro vídeo? " + link("Escolha em Meus vídeos", "#meus", "discreto mini") + "</p>"
      : '<p class="apoio">Ainda não tem vídeo pronto pro ' + esc(nr) + ". " + link("Fazer um vídeo", "#fazer", "discreto mini") + "</p>";
    var passos;
    if (modo === "pc") {
      passos = [
        ["Baixe o vídeo e copie a legenda.", pegar],
        ["Abra o site do " + nr + " e entre na sua conta.", '<a class="botao" href="' + dados[0] + '" target="_blank" rel="noopener noreferrer">' + icone("abrir") + '<span class="rotulo">Abrir o ' + esc(nr) + '</span><span class="so-leitor"> (abre o site em outra aba)</span></a>'],
        [dados[1], ""]
      ];
    } else {
      passos = [
        ["Baixe o vídeo e copie a legenda.", pegar],
        ["Mande o vídeo e a legenda pro seu celular.",
          '<div class="acoes"><a class="botao" href="https://web.whatsapp.com/" target="_blank" rel="noopener noreferrer">' + icone("abrir") + '<span class="rotulo">Abrir o WhatsApp Web</span><span class="so-leitor"> (abre em outra aba)</span></a>' +
          '<a class="botao secundario" href="https://drive.google.com/" target="_blank" rel="noopener noreferrer">' + icone("abrir") + '<span class="rotulo">Abrir o Google Drive</span><span class="so-leitor"> (abre em outra aba)</span></a></div>' +
          '<p class="ajuda">No WhatsApp: abra a conversa com você mesmo (procure o seu nome), anexe o vídeo, cole a legenda e mande. No celular, abra a conversa e salve o vídeo.</p>' +
          '<p class="ajuda">No Drive: arraste o vídeo pra dentro. No celular, abra o app do Drive e baixe.</p>'],
        ["No app do " + nr + ": " + dados[2].charAt(0).toLowerCase() + dados[2].slice(1), ""]
      ];
    }
    return voltarLinha("postar") + cabeca("Como postar", "O vídeo está no seu computador. Escolha a rede e o jeito de postar.") +
      '<div class="segmentos redes-postar" role="radiogroup" aria-label="Rede" data-tour="rede">' + redes.map(function (r) {
        return '<button type="button" role="radio" aria-checked="' + (r === redePostar) + '" aria-pressed="' + (r === redePostar) + '" data-acao="postar-rede" data-rede="' + r + '">' + selo(r, true) + "<span>" + esc(nomeRede(r)) + "</span></button>";
      }).join("") + "</div>" +
      '<div class="jeito-postar" data-tour="jeito-postar"><span class="rotulo">Como você quer postar?</span>' + (semPc ? '<p class="apoio">O ' + esc(nr) + " só posta pelo app do celular.</p>" :
        '<div class="segmentos" role="radiogroup" aria-label="Jeito de postar">' + [["pc", "Pelo computador"], ["cel", "Mandar pro celular"]].map(function (m) {
          return '<button type="button" role="radio" aria-checked="' + (m[0] === modo) + '" aria-pressed="' + (m[0] === modo) + '" data-acao="postar-modo" data-modo="' + m[0] + '">' + esc(m[1]) + "</button>";
        }).join("") + "</div>") + "</div>" +
      '<ol class="passos-grandes" data-tour="passos">' + passos.map(function (t, i) {
        return '<li><span class="n" aria-hidden="true">' + (i + 1) + '</span><div class="frase"><p>' + esc(t[0]) + "</p>" + (t[1] || "") + "</div></li>";
      }).join("") + "</ol>" +
      '<ul class="dicas"><li>Poste ' + esc(String(valor("redes", "horario") || "sempre no mesmo horário").replace(/,?\s*no mesmo horário todo dia\.?$/i, "")) + ", no mesmo horário todo dia.</li><li>Se a rede perguntar, marque que o vídeo foi feito com IA.</li></ul>";
  };

  /* ------------------------------------------------------------ sua conta e suporte */
  /* Perguntas curtas que resolvem antes de chamar alguém (Sua conta e Ajuda). */
  var FAQ_CURTA = [
    ["A voz não sai", "Veja se a voz em uso está ligada. A grátis do Google leva 2 minutos e não pede cartão.", "link", "Ver a voz", "#voz"],
    ["O vídeo não fica pronto", "Peça no chat da IA para ela conferir e continuar de onde parou. Se der erro, ela lê e arruma.", "copiar", "Copiar pedido", "o vídeo não terminou: confere o que aconteceu e continua de onde parou"],
    ["Não sei postar", "Baixe o vídeo em Meus vídeos e poste pelo app da rede. Leva 1 minuto.", "link", "Ver como postar", "#postar"]
  ];
  function faqHtml(lista, attrs) {
    return '<div class="perguntas"' + (attrs || "") + ">" + lista.map(function (q) {
      var acao = q[2] === "link" ? link(q[3], q[4], "botao secundario", "seguir") : botaoCopiar(q[4], q[3], "secundario", "Pedido copiado. Agora cole no chat da IA.");
      return '<details class="recolhe pergunta-item" data-busca="' + esc(semAcento(q[0] + " " + q[1])) + '"><summary><b>' + esc(q[0]) + "</b><span></span>" + icone("abaixo") + '</summary><div class="recolhe-corpo"><p>' + esc(q[1]) + "</p>" + acao + "</div></details>";
    }).join("") + "</div>";
  }
  T.suporte = function () {
    var c = E.conta || { ativa: false, suporte: {} };
    var sup = c.suporte || {};
    var email = sup.email || "contato@temporadaviral.com";
    var corpo = "Versão do kit: " + (E.versao || "?") + "\nE-mail da compra: " + (c.email || "?") + "\n\nO que aconteceu:\n";
    var mailto = "mailto:" + email + "?subject=" + encodeURIComponent("Suporte Temporada Viral " + (E.versao || "")) + "&body=" + encodeURIComponent(corpo);
    var tg = sup.telegram ? String(sup.telegram) : "";
    var resposta = "Respondemos " + (sup.resposta || "em até 12 horas, do meio-dia à meia-noite") + ".";
    var ate = dataBr(c.atualizacoes_ate), falta = mesesAte(c.atualizacoes_ate), desde = dataBr(c.desde);
    var barraAt = "";
    if (c.desde && c.atualizacoes_ate) {
      var ini = new Date(c.desde + "T00:00:00").getTime(), fimT = new Date(c.atualizacoes_ate + "T23:59:59").getTime();
      var resta = Math.max(0, Math.min(100, Math.round((fimT - Date.now()) / (fimT - ini) * 100)));
      barraAt = '<div class="medidor" role="progressbar" aria-label="Tempo de atualizações que ainda resta" aria-valuemin="0" aria-valuemax="100" aria-valuenow="' + resta + '"><i style="width:' + resta + '%"></i></div>';
    }
    var selo = c.ativa ? '<p class="selo-licenca">' + icone("certo") + "<span><b>Licença ativa</b>" + (c.email ? "<small>Compra feita com " + esc(c.email) + "</small>" : "") + "</span></p>" : "";
    var falar = '<div class="acoes falar" data-tour="falar">' +
      (tg ? link("Chamar no Telegram", tg, "botao gigante", "balao", ' target="_blank" rel="noopener noreferrer"') + link("Mandar e-mail", mailto, "botao secundario", "abrir")
        : link("Mandar e-mail", mailto, "botao gigante", "abrir")) + "</div>" +
      '<p class="apoio">' + esc(resposta) + ' <span class="meta">E-mail: ' + esc(email) + "</span></p>" +
      (c.comunidade ? '<p class="apoio">Quer trocar ideia com quem também usa? ' + link("Entrar na comunidade", c.comunidade, "discreto", "balao", ' target="_blank" rel="noopener noreferrer"') + "</p>" : "");
    var conta = c.ativa ? '<section class="plano licenca" data-tour="licenca"><h2 class="bloco-titulo">Sua licença</h2>' +
      (c.atualizacoes_sempre ? '<p class="linha-conta"><b>Atualizações para sempre</b><small>Toda versão nova chega pra você, sem prazo.</small></p>'
        : falta === "terminou" ? '<p class="linha-conta"><b>As atualizações grátis terminaram em ' + esc(ate) + "</b><small>O kit continua funcionando. As versões novas vêm com o Atualizações para Sempre.</small></p>" +
          (c.oferta_sempre ? link("Quero as atualizações para sempre", c.oferta_sempre, "botao secundario", "estrela", ' target="_blank" rel="noopener noreferrer"') : "")
        : ate ? '<p class="linha-conta"><b>Atualizações grátis até ' + esc(ate) + "</b>" + (falta ? "<small>" + esc(falta) + "</small>" : "") + "</p>" + barraAt +
          '<p class="meta">Depois disso, as versões novas vêm com o Atualizações para Sempre.' + (c.oferta_sempre ? " " + link("Ver como garantir", c.oferta_sempre, "discreto mini", "", ' target="_blank" rel="noopener noreferrer"') : "") + "</p>"
        : '<p class="linha-conta"><b>Atualizações em dia</b></p>') +
      '<p class="linha-conta">Você está na versão <b>' + esc(E.versao || "?") + "</b></p>" + link("Ver o que mudou", "#aprender/novidades", "discreto mini") +
      (c.copia && c.copia.codigo ? '<p class="linha-conta copia-licenciada" data-tour="copia">' + icone("certo") + "<span><b>Cópia licenciada para " + esc(c.copia.email_mascarado || "você") +
        "</b><small>Código da compra " + esc(c.copia.codigo) + (c.copia.data ? " · baixada em " + esc(dataBr(c.copia.data) || c.copia.data) : "") + ". Uso pessoal: não compartilhe a pasta.</small></span></p>" : "") +
      (E.atualizacao && E.atualizacao.nova ? '<div class="acoes-linha versao-nova">' +
        botao(E.atualizacao.liberada && !E.atualizacao.nuvem ? "Atualizar para a " + E.atualizacao.nova.numero : "Ver a versão " + E.atualizacao.nova.numero,
          'data-acao="atualizar-abrir"', E.atualizacao.liberada ? "" : "secundario", "seguir") + "</div>" : "") +
      (desde ? '<p class="meta">Cliente desde ' + esc(desde) + ".</p>" : "") + "</section>" : "";
    var tudo = botaoArrumarTudo("secundario");
    var antes = '<section class="plano antes" data-tour="antes"><h2 class="bloco-titulo">Antes de chamar, tenta isto</h2>' +
      (tudo ? '<div class="acoes-linha">' + tudo + '<span class="meta">Um pedido só, com tudo o que falta no computador.</span></div>' : '<p class="ok-linha">' + icone("certo") + "<span>O computador está pronto pra fazer vídeo.</span></p>") +
      faqHtml(FAQ_CURTA) + "</section>";
    return voltarLinha("suporte") +
      '<div class="topo-suporte">' + ilustracao("suporte", "tv-frente", "suporte-ilustra") + '<div class="cabeca-texto"><h1 class="titulo">Falar com a gente</h1>' + selo + falar + "</div></div>" +
      '<div class="grade-conta">' + antes + conta + "</div>";
  };

  /* ------------------------------------------------------------ conversar com a IA (chat embutido) */
  var IA_NOMES = { claude: ["Claude Code", "A IA da Anthropic"], codex: ["ChatGPT (Codex)", "A IA da OpenAI"] };
  var IA_ATALHOS = [["Faz um vídeo rápido", "faz um vídeo rápido pra eu ver funcionando"], ["Arruma o que falta", ""], ["Confere o computador", "confere o meu computador (python verificar.py, a partir de kit/) e me diz em uma frase se está tudo pronto"]];
  var iaEstado = null, iaCarregando = null, iaVigia = null;
  var iaCli = lerLocal("iaCli", "claude");
  var iaConversas = lerLocal("iaConversas", {});
  var iaRascunho = "";
  var iaPendente = "";
  function conversaDe(cli) { if (!iaConversas[cli]) iaConversas[cli] = { id: null, msgs: [] }; return iaConversas[cli]; }
  var paginaSaindo = false;
  window.addEventListener("pagehide", function () { paginaSaindo = true; guardarConversas(true); });
  var guardarTimer = null;
  function guardarConversas(ja) {
    var gravar = function () {
      var copia = {};
      Object.keys(iaConversas).forEach(function (k) {
        var c = iaConversas[k];
        copia[k] = { id: c.id, rodando: !!c.rodando, rodada: c.rodada || null, inicio: c.inicio || null, estimativa: c.estimativa || null, atualizado: c.atualizado || null, msgs: c.msgs.slice(-40).map(function (m) { return { quem: m.quem, texto: m.texto, partes: m.partes, acoes: m.acoes, erro: m.erro, passos: m.passos, nota: m.nota, arquivosRodada: m.arquivosRodada }; }) };
      });
      gravarLocal("iaConversas", copia);
    };
    clearTimeout(guardarTimer);
    if (ja) gravar(); else guardarTimer = setTimeout(gravar, 800);
  }
  function iasInstaladas() { return ["claude", "codex"].filter(function (k) { return iaEstado && iaEstado[k] && iaEstado[k].instalado; }); }
  function carregarIA(forcar) {
    if (ESTATICO) return Promise.resolve(null);
    if (iaCarregando && !forcar) return iaCarregando;
    iaCarregando = fetch("/api/ia/estado" + (forcar ? "?forcar=1" : ""), { credentials: "same-origin", headers: { "X-Painel-Token": TOKEN } })
      .then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; })
      .then(function (j) {
        iaEstado = j && (j.claude || j.codex) ? j : null;
        var inst = iasInstaladas();
        if (inst.length && inst.indexOf(iaCli) < 0) iaCli = inst[0];
        if (iaEstado && !(iaEstado[iaCli] || {}).chat) { var outro = iaCli === "claude" ? "codex" : "claude"; if ((iaEstado[outro] || {}).chat) iaCli = outro; }
        retomarConversas();
        iaCarregando = null;
        return iaEstado;
      });
    return iaCarregando;
  }
  /* Conversa que estava rodando quando a página fechou: mostra que a IA ainda trabalha e confere até ela terminar. */
  function retomarConversas() {
    var algum = false;
    Object.keys(iaConversas).forEach(function (k) {
      var c = iaConversas[k];
      if (!c.rodando || c.ctrl || c.recuperando) return;
      var e = iaEstado && iaEstado[k];
      var ultimo = c.msgs[c.msgs.length - 1];
      if (c.rodada && ultimo && ultimo.quem === "ia") { recuperarIA(k, c, { quem: "ia", texto: "", acoes: [] }, 0, c.msgs.length - 1); return; }
      if (e && e.ocupado) { algum = true; c.retomada = true; if (ultimo && ultimo.quem === "ia") ultimo.nota = "A IA ainda está trabalhando nisso. Quando ela terminar, aparece aqui."; }
      else {
        c.rodando = false; c.retomada = false;
        if (ultimo && ultimo.quem === "ia") {
          ultimo.nota = "A IA terminou enquanto o painel estava fechado. Pergunte aqui: “o que você fez?”.";
          (ultimo.acoes || []).forEach(function (a) { if (a.estado === "rodando") a.estado = "ok"; });
        }
        guardarConversas(true);
      }
    });
    clearTimeout(iaVigia);
    if (algum) iaVigia = setTimeout(function () { carregarIA(true).then(function () { desenharChat(); }); }, 5000);
    desenharChat();
  }
  function iaPronta() { return !!(iaEstado && iaEstado[iaCli] && iaEstado[iaCli].chat); }
  function estadoIAFrase(e) {
    if (!e) return ["Conferindo…", ""];
    if (e.chat) return [e.ocupado ? "Trabalhando agora" : "Pronta pra conversar", "ok"];
    if (e.logado === false) return ["Falta entrar na conta", "falta"];
    return [limparCaminhos(e.aviso) || "Ainda não conversa por aqui", "falta"];
  }
  /* Nomes de arquivo citados pela IA viram link que abre no próprio painel. O mapa vem dos arquivos do episódio
     (Seu episódio) e dos arquivos desta resposta; nome que não está no mapa fica como texto. */
  var RE_ARQ_TEXTO = /`?((?:[A-Za-z]:)?(?:[\w.~-]+[\\\/])*([\w.-]+\.(?:mp4|mov|webm|mp3|wav|png|jpe?g|webp|gif|srt|txt|md)))`?/gi;
  function mapaArquivos(m) {
    var mapa = { caminhos: [], nomes: {} };
    var poe = function (c, nome) {
      if (!c) return;
      nome = (nome || c.split("/").pop()).toLowerCase();
      mapa.caminhos.push(c);
      mapa.nomes[nome] = mapa.nomes[nome] && mapa.nomes[nome] !== c ? "?" : c;
    };
    (iaEps || []).forEach(function (e) { (e.arquivos || []).forEach(function (a) { poe(a.c, a.nome); }); });
    if (m) {
      (m.acoes || []).forEach(function (a) { (a.arquivos || []).forEach(function (r) { poe(r); }); });
      (m.arquivosRodada || []).forEach(function (r) { poe(r); });
    }
    return mapa;
  }
  function acharArquivo(caminho, nome, mapa) {
    var cam = caminho.replace(/\\/g, "/").toLowerCase();
    var achado = mapa.caminhos.filter(function (c) {
      var semRaiz = c.replace(/^~t\//, "").toLowerCase();
      return cam === c.toLowerCase() || cam.slice(-semRaiz.length - 1) === "/" + semRaiz;
    })[0];
    if (achado) return achado;
    var porNome = mapa.nomes[nome.toLowerCase()];
    return porNome && porNome !== "?" ? porNome : null;
  }
  function textoIA(t, mapa) {
    var links = [];
    t = String(t || "");
    if (mapa) {
      t = t.replace(RE_ARQ_TEXTO, function (tudo, caminho, nome) {
        var c = acharArquivo(caminho, nome, mapa);
        if (!c) return tudo;
        links.push({ c: c, nome: nome });
        return "\u0001" + (links.length - 1) + "\u0002";
      });
    }
    var html = esc(limparCaminhos(t)).replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>").replace(/`([^`]+)`/g, "<b>$1</b>");
    return html.replace(/\u0001(\d+)\u0002/g, function (_, k) {
      var l = links[Number(k)];
      var ext = (l.nome.split(".").pop() || "").toLowerCase();
      var ic = /^(mp4|mov|webm)$/.test(ext) ? "claquete" : /^(mp3|wav)$/.test(ext) ? "som" : /^(png|jpe?g|webp|gif)$/.test(ext) ? "estrela" : "livro";
      return '<button type="button" class="link-arquivo" data-acao="ia-arquivo" data-c="' + esc(l.c) + '" title="Abrir ' + esc(l.nome) + '">' + icone(ic) + "<span>" + esc(l.nome) + "</span></button>";
    });
  }
  function resumoAcao(t) {
    t = String(t || "");
    if (/^Rodou:\s*(python|py)\b/i.test(t)) return "Rodou um programa do kit";
    return limparCaminhos(t);
  }
  function chatHtml() {
    var c = conversaDe(iaCli);
    if (!c.msgs.length) {
      return '<div class="chat-vazio">' + ilustracao("ideias", "tv-notebook", "chat-ilustra") + '<p class="lead">Peça do seu jeito, como faria com uma pessoa.</p>' +
        '<p class="meta">A IA trabalha aqui no seu computador, dentro da pasta do estúdio.</p></div>';
    }
    return c.msgs.map(function (m, k) {
      if (m.quem === "eu") return '<div class="balao eu"><p>' + esc(m.texto) + "</p></div>";
      var mapa = mapaArquivos(m);
      var acaoLi = function (a) {
        var ic = { rodando: '<span class="girando" aria-hidden="true"></span>', ok: icone("certo"), erro: icone("aviso"), recusado: icone("fechar") }[a.estado] || "";
        var rot = { rodando: "rodando", ok: "feito", erro: "deu erro", recusado: "não permitido aqui" }[a.estado] || a.estado;
        return '<li class="acao-ia ' + esc(a.estado) + '"><span class="estado-acao" title="' + esc(rot) + '">' + ic + '<span class="so-leitor">' + esc(rot) + ": </span></span>" +
          '<span class="resumo-acao">' + esc(resumoAcao(a.resumo)) + "</span>" +
          (a.detalhe ? '<details data-id="' + esc(a.id) + '"><summary>ver detalhe</summary><pre>' + esc(a.detalhe) + "</pre></details>" : "") + "</li>";
      };
      var ultimo = k === c.msgs.length - 1;
      var miolo = "";
      if (m.partes && m.partes.length) {
        var porId = {};
        (m.acoes || []).forEach(function (a) { porId[a.id] = a; });
        var lista = "";
        m.partes.forEach(function (p) {
          if (p.t === "acao") { if (porId[p.id]) lista += acaoLi(porId[p.id]); return; }
          var tx = String(p.texto || "").trim();
          if (!tx) return;
          if (lista) { miolo += '<ul class="acoes-ia">' + lista + "</ul>"; lista = ""; }
          miolo += "<p>" + textoIA(tx, mapa) + "</p>";
        });
        if (lista) miolo += '<ul class="acoes-ia">' + lista + "</ul>";
      } else {
        var acoes = (m.acoes || []).map(acaoLi).join("");
        var texto = String(m.texto || "").trim();
        miolo = (acoes ? '<ul class="acoes-ia">' + acoes + "</ul>" : "") + (texto ? "<p>" + textoIA(texto, mapa) + "</p>" : "");
      }
      if (ultimo && !c.rodando) {
        var falaFim = m.partes && m.partes.length ? (m.partes.filter(function (p) { return p.t === "texto"; }).pop() || {}).texto : m.texto;
        var ops = opcoesIA(falaFim);
        if (ops.length) miolo += '<div class="respostas-ia"><p class="arquivos-ia-titulo">Responder com um clique</p><div class="respostas-ia-lista">' +
          ops.map(function (o) { return '<button type="button" class="resposta-ia" data-acao="ia-resposta" data-texto="' + esc(o.envio) + '">' + esc(o.rot) + "</button>"; }).join("") + "</div></div>";
      }
      /* Arquivos que a IA gravou nesta resposta: no fim do balão, para abrir sem procurar na pasta. */
      var arqs = [];
      (m.acoes || []).forEach(function (a) { (a.arquivos || []).forEach(function (r) { if (arqs.indexOf(r) < 0) arqs.push(r); }); });
      (m.arquivosRodada || []).forEach(function (r) { if (arqs.indexOf(r) < 0) arqs.push(r); });
      if (arqs.length) {
        miolo += '<div class="arquivos-ia"><p class="arquivos-ia-titulo">Arquivos desta resposta</p><div class="arquivos-ia-lista">' + arqs.map(function (r) {
          var ext = (r.split(".").pop() || "").toLowerCase();
          var ic = /^(mp4|mov|webm)$/.test(ext) ? "claquete" : /^(mp3|wav)$/.test(ext) ? "som" : /^(png|jpe?g|webp|gif)$/.test(ext) ? "estrela" : "livro";
          return '<button type="button" class="arquivo-ia" data-acao="ia-arquivo" data-c="' + esc(r) + '" title="' + esc(r) + '">' + icone(ic) + "<span>" + esc(r.split("/").pop()) + "</span></button>";
        }).join("") + "</div></div>";
      }
      if (c.rodando && ultimo && !m.nota) miolo += statusIAHtml();
      var corpo = miolo +
        (m.nota ? '<p class="nota-ia">' + (c.rodando && ultimo ? '<span class="girando" aria-hidden="true"></span>' : icone("certo")) + "<span>" + esc(m.nota) + "</span></p>" : "") +
        (m.erro ? '<p class="erro-msg">' + icone("aviso") + "<span>" + esc(limparCaminhos(m.erro)) + "</span></p>" +
          (m.passos && m.passos.length ? '<ol class="passos-ia">' + m.passos.map(function (p) { return "<li>" + esc(limparCaminhos(p)) + "</li>"; }).join("") + "</ol>" : "") : "");
      return '<div class="balao ia">' + corpo + "</div>";
    }).join("");
  }
  /* "A IA está trabalhando": cronômetro e previsão, atualizados a cada segundo sem redesenhar o chat. */
  function statusIAHtml() {
    return '<div class="trabalhando-ia" role="status"><span class="girando" aria-hidden="true"></span><div><p><b>A IA está trabalhando</b> <span class="cronometro" data-cronometro></span></p>' +
      '<p class="previsao" data-previsao></p></div></div>';
  }
  function tempoTexto(ms) {
    var s = Math.max(0, Math.round(ms / 1000)), m = Math.floor(s / 60);
    return m ? m + " min " + ("0" + (s % 60)).slice(-2) + " s" : s + " s";
  }
  function atualizarStatusIA() {
    var c = conversaDe(iaCli);
    var cron = document.querySelector("#chat-log [data-cronometro]"), prev = document.querySelector("#chat-log [data-previsao]");
    if (!cron || !c.rodando) return;
    var agora = Date.now(), passou = agora - (c.inicio || agora);
    cron.textContent = "há " + tempoTexto(passou);
    var txt;
    if (c.estimativa) {
      var resta = c.estimativa.min * 60000 - (agora - c.estimativa.desde);
      txt = resta > 0 ? "Previsão: falta uns " + (resta >= 60000 ? Math.ceil(resta / 60000) + " min" : tempoTexto(resta)) + ". Pode deixar o painel aberto."
        : "Passou um pouco da previsão, mas ela continua trabalhando. Não feche o painel.";
    } else txt = passou > 45000 ? "Voz e vídeo levam alguns minutos. Pode deixar o painel aberto: a resposta aparece aqui." : "";
    if (prev) { prev.textContent = txt; prev.hidden = !txt; }
  }
  setInterval(atualizarStatusIA, 1000);
  var chatAgendado = false;
  function desenharChatLogo() {
    if (chatAgendado) return;
    chatAgendado = true;
    requestAnimationFrame(function () { chatAgendado = false; desenharChat(); });
  }
  function desenharChat() {
    var log = document.getElementById("chat-log");
    if (!log) return;
    /* Redesenho sem pulo: guarda a rolagem e os detalhes abertos; só segue o fim se a pessoa já estava no fim. */
    var perto = log.scrollHeight - log.scrollTop - log.clientHeight < 60;
    var topo = log.scrollTop;
    var abertos = {};
    Array.prototype.forEach.call(log.querySelectorAll("details[open][data-id]"), function (d) { abertos[d.getAttribute("data-id")] = true; });
    log.innerHTML = chatHtml();
    Array.prototype.forEach.call(log.querySelectorAll("details[data-id]"), function (d) { if (abertos[d.getAttribute("data-id")]) d.open = true; });
    log.scrollTop = perto ? log.scrollHeight : topo;
    atualizarStatusIA();
    var c = conversaDe(iaCli);
    var mandar = document.querySelector('[data-acao="ia-mandar"]'), parar = document.querySelector('[data-acao="ia-parar"]');
    if (mandar) mandar.disabled = !!c.rodando || !iaPronta();
    // Parar aparece também quando outro pedido roda (outra conversa ou a página recarregada): sem isso, o aviso
    // "clique em Parar" ficava sem botão.
    if (parar) parar.hidden = !(c.rodando || (iaEstado && iaEstado[iaCli] && iaEstado[iaCli].ocupado));
  }
  function aplicarEventoIA(c, resp, ev) {
    if (ev.tipo === "inicio") { if (ev.conversa) c.id = ev.conversa; if (ev.rodada) c.rodada = ev.rodada; }
    else if (ev.tipo === "texto") {
      resp.texto += ev.texto || "";
      if (!resp.partes) resp.partes = [];
      var ult = resp.partes[resp.partes.length - 1];
      if (ult && ult.t === "texto") ult.texto += ev.texto || ""; else resp.partes.push({ t: "texto", texto: ev.texto || "" });
      var fala = resp.partes[resp.partes.length - 1].texto.slice(-400);
      var mm = fala.match(/(\d{1,3})(?:\s*(?:a|e|ou|-)\s*(\d{1,3}))?\s*(?:min\b|minutos?)/i);
      if (mm) {
        var nmin = Number(mm[2] || mm[1]);
        if (nmin > 0 && nmin <= 240 && (!c.estimativa || c.estimativa.trecho !== mm[0])) c.estimativa = { min: nmin, desde: Date.now(), trecho: mm[0] };
      }
    }
    else if (ev.tipo === "acao") {
      var a = resp.acoes.filter(function (x) { return x.id === ev.id; })[0];
      if (a) { a.estado = ev.estado; if (ev.resumo) a.resumo = ev.resumo; if (ev.detalhe) a.detalhe = ev.detalhe; if (ev.arquivos && ev.arquivos.length) a.arquivos = ev.arquivos; }
      else { resp.acoes.push({ id: ev.id, estado: ev.estado, resumo: ev.resumo, detalhe: ev.detalhe, arquivos: ev.arquivos || null }); if (!resp.partes) resp.partes = []; resp.partes.push({ t: "acao", id: ev.id }); }
    } else if (ev.tipo === "erro") {
      resp.erro = ev.mensagem || "A IA não respondeu."; resp.passos = ev.passos || [];
      if (ev.ocupado) carregarIA(true).then(function () { desenharChat(); });
    }
    else if (ev.tipo === "arquivos") resp.arquivosRodada = ev.arquivos || [];
    else if (ev.tipo === "fim" && ev.conversa) c.id = ev.conversa;
  }
  function encerrarIA(c, resp) {
    c.rodando = false; c.ctrl = null; c.recuperando = false; c.retomada = false; c.atualizado = Date.now();
    if (!resp.texto && !resp.acoes.length && !resp.erro) resp.erro = "A IA parou sem responder.";
    (resp.acoes || []).forEach(function (a) { if (a.estado === "rodando") a.estado = "ok"; });
    guardarConversas(true); desenharChat(); carregarIA(true); carregarEps();
  }
  /* A conexão caiu ou o painel reabriu: busca no servidor o resto da resposta (a IA continua no computador).
     trocar: posição da mensagem a substituir quando os eventos chegarem (reabertura, que refaz do começo). */
  function recuperarIA(cli, c, resp, desde, trocar) {
    var rodada = c.rodada;
    c.rodando = true; c.recuperando = true;
    if (!c.inicio) c.inicio = Date.now();
    var falhas = 0;
    var passo = function () {
      fetch("/api/ia/eventos?cli=" + encodeURIComponent(cli) + "&desde=" + desde, { credentials: "same-origin", headers: { "X-Painel-Token": TOKEN } })
        .then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; })
        .then(function (j) {
          if (!j) { if (++falhas < 20) { setTimeout(passo, 3000); return; } }
          if (!j || j.rodada !== rodada) {
            var ult = c.msgs[c.msgs.length - 1];
            if (trocar != null && ult && ult.quem === "ia") { ult.nota = "A IA terminou enquanto o painel estava fechado. Pergunte aqui: “o que você fez?”."; encerrarIA(c, ult); }
            else encerrarIA(c, resp);
            return;
          }
          falhas = 0;
          if (trocar != null) { c.msgs[trocar] = resp; trocar = null; }
          (j.eventos || []).forEach(function (ev) { aplicarEventoIA(c, resp, ev); });
          desde += (j.eventos || []).length;
          guardarConversas(); desenharChatLogo();
          if (j.fim && desde >= j.total) encerrarIA(c, resp);
          else setTimeout(passo, 1500);
        });
    };
    passo();
  }
  /* texto: o que vai para a IA (pode ter caminho de arquivo); mostrar: a versão limpa que aparece no balão. */
  function mandarIA(texto, mostrar) {
    texto = String(texto || "").trim();
    var cli = iaCli, c = conversaDe(cli);
    if (!texto || c.rodando) return;
    if (!iaPronta()) { toast("Esta IA ainda não conversa por aqui. Veja os passos ou abra numa janela separada.", "aviso"); return; }
    c.msgs.push({ quem: "eu", texto: mostrar || limparCaminhos(texto) });
    var resp = { quem: "ia", texto: "", acoes: [] };
    c.msgs.push(resp); c.rodando = true; c.inicio = Date.now(); c.estimativa = null; c.atualizado = Date.now();
    iaRascunho = "";
    var caixa = document.getElementById("chat-texto"); if (caixa) caixa.value = "";
    guardarConversas(true);
    desenharChat();
    var log = document.getElementById("chat-log"); if (log) log.scrollTop = log.scrollHeight;
    var ctrl = window.AbortController ? new AbortController() : null;
    c.ctrl = ctrl; c.rodada = null;
    var recebidos = 0, viuFim = false, caiu = false;
    var evento = function (ev) {
      if (ev.tipo === "inicio" && ev.rodada) recebidos = 0;
      if (c.rodada || ev.rodada) recebidos++;
      if (ev.tipo === "fim") viuFim = true;
      aplicarEventoIA(c, resp, ev);
      guardarConversas();
      desenharChatLogo();
    };
    fetch("/api/ia/mensagem", { method: "POST", credentials: "same-origin", signal: ctrl ? ctrl.signal : undefined,
      headers: { "X-Painel-Token": TOKEN, "Content-Type": "application/json" }, body: JSON.stringify({ cli: cli, texto: texto, conversa: c.id || null }) })
      .then(function (r) {
        if (r.status === 403) { location.reload(); return null; }
        if (!r.ok || !r.body) { resp.erro = "O painel não conseguiu falar com a IA agora."; return null; }
        var leitor = r.body.getReader(), dec = new TextDecoder(), buf = "";
        var ler = function () {
          return leitor.read().then(function (x) {
            if (x.done) return null;
            buf += dec.decode(x.value, { stream: true });
            var blocos = buf.split(/\r?\n\r?\n/);
            buf = blocos.pop();
            blocos.forEach(function (bl) {
              bl.split(/\r?\n/).forEach(function (l) { if (l.indexOf("data:") === 0) { try { evento(JSON.parse(l.slice(5).trim())); } catch (e) { /* linha incompleta */ } } });
            });
            return ler();
          });
        };
        return ler();
      })
      .catch(function (e) { if (!(e && e.name === "AbortError")) caiu = true; })
      .then(function () {
        /* Página fechando no meio: a IA continua no computador e a resposta volta quando o painel reabrir. */
        if (paginaSaindo) return;
        c.ctrl = null;
        /* A conexão caiu antes do fim: busca o resto da resposta no servidor em vez de perder o que a IA disse. */
        if (!viuFim && c.rodada) { recuperarIA(cli, c, resp, recebidos); return; }
        if (caiu && !viuFim) resp.erro = "A conversa caiu. Tente de novo.";
        encerrarIA(c, resp);
      });
  }
  /* "a) aprovado, pode gravar" / "b) troca a voz": cada opção da IA vira um botão que manda a resposta. */
  function opcoesIA(t) {
    var ops = [], vistos = {};
    String(t || "").split(/\r?\n/).forEach(function (l) {
      var mm = l.match(/^\s*(?:[-*•]\s*)?\**\(?([a-eA-E])\)\**\s*(.+)$/);
      /* "Abertura A: ...", "Opção 2: ...": vira botão com o nome da opção. */
      var mo = !mm && l.match(/^\s*(?:[-*•]\s*)?\**((?:Abertura|Opção|Opcao|Versão|Versao|Gancho|Capa|Final)\s+[A-E1-5])\b\**\s*[:.)—–-]/i);
      if (mo) {
        var nomeOp = mo[1].replace(/\s+/g, " ");
        if (!vistos[nomeOp.toLowerCase()]) { vistos[nomeOp.toLowerCase()] = true; ops.push({ rot: nomeOp, envio: nomeOp }); }
        return;
      }
      if (!mm) return;
      var letra = mm[1].toLowerCase(), resto = mm[2];
      var negrito = resto.match(/\*\*([^*]{2,120})\*\*/);
      var aspas = resto.match(/^\W{0,3}["“]([^"”]{2,140})["”]/);
      var rot = negrito ? negrito[1] : aspas ? aspas[1] : resto.replace(/\*\*/g, "").split(/[:(—–]| - /)[0];
      rot = rot.replace(/^["“]|["”]$/g, "").replace(/[:.,;]\s*$/, "").trim();
      if (rot.length > 90) rot = rot.slice(0, 87).trim() + "…";
      if (rot && !vistos[letra]) { vistos[letra] = true; ops.push({ rot: rot, envio: letra + ") " + rot }); }
    });
    return ops.length >= 2 ? ops.slice(0, 5) : [];
  }
  /* Seu episódio: os arquivos da produção (roteiro, voz, vídeo) para abrir, ouvir e assistir sem sair do painel. */
  var iaEps = null, iaEpSel = lerLocal("iaEp", "");
  var EP_GRUPOS = [["video", "Vídeos"], ["audio", "Áudio"], ["texto", "Roteiro e textos"], ["imagem", "Imagens"], ["falas", "Falas separadas"]];
  function carregarEps() {
    if (ESTATICO) return;
    fetch("/api/ia/episodios", { credentials: "same-origin", headers: { "X-Painel-Token": TOKEN } })
      .then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; })
      .then(function (j) {
        if (!j) return;
        var novo = j.episodios || [], mudou = JSON.stringify(novo) !== JSON.stringify(iaEps);
        iaEps = novo;
        if (mudou) desenharEp();
      });
  }
  setInterval(function () { if (telaAtual() === "conversar" && !document.hidden) carregarEps(); }, 6000);
  function epAtual() {
    if (!iaEps || !iaEps.length) return null;
    return iaEps.filter(function (e) { return e.id === iaEpSel; })[0] || iaEps[0];
  }
  function nomeEp(e) {
    var serie = e.serie.replace(/[-_]+/g, " ").replace(/^./, function (x) { return x.toUpperCase(); });
    var n = (e.ep.match(/\d+/) || [""])[0];
    return serie + (n ? " · Parte " + n : "");
  }
  function epHtml() {
    var topo = '<section class="ep-ia" id="ep-ia" data-tour="ia-episodio"><h2 class="bloco-titulo">Seu episódio</h2>';
    if (!iaEps) return topo + esqueleto(1) + "</section>";
    var ep = epAtual();
    if (!ep) return topo + '<p class="meta">Quando a IA fizer o roteiro, a voz e o vídeo, os arquivos aparecem aqui para você ler, ouvir e assistir.</p></section>';
    var chips = iaEps.length > 1 ? '<div class="ep-escolha" role="group" aria-label="Episódio">' + iaEps.slice(0, 4).map(function (e) {
      return '<button type="button" class="ideia' + (e.id === ep.id ? " ativo" : "") + '" aria-pressed="' + (e.id === ep.id) + '" data-acao="ia-ep" data-ep="' + esc(e.id) + '">' + esc(nomeEp(e)) + "</button>";
    }).join("") + "</div>" : '<p class="ep-nome">' + esc(nomeEp(ep)) + "</p>";
    var grupos = EP_GRUPOS.map(function (g) {
      var lista = ep.arquivos.filter(function (a) { return a.grupo === g[0]; });
      if (!lista.length) return "";
      var repetidos = {};
      lista.forEach(function (a) { repetidos[a.nome] = (repetidos[a.nome] || 0) + 1; });
      var botoes = lista.map(function (a) {
        var ic = { video: "claquete", audio: "som", falas: "som", imagem: "estrela" }[a.grupo] || "livro";
        /* Mesmo nome em pastas diferentes: mostra a pasta para dar pra saber qual é qual. */
        var partes = a.c.split("/").slice(0, -1);
        var raiz = a.c.indexOf("~t/") === 0 ? "trabalho" : a.c.indexOf("kit/") === 0 ? "kit" : "estúdio";
        var iEp = -1;
        partes.forEach(function (p, i) { if (/^(ep|parte|p)\d+$/i.test(p)) iEp = i; });
        var sub = iEp >= 0 ? partes.slice(iEp + 1).join("/") : "";
        var onde = repetidos[a.nome] > 1 ? ' <small class="arquivo-pasta">' + esc(raiz + (sub ? " · " + sub : "")) + "</small>" : "";
        return '<button type="button" class="arquivo-ia" data-acao="ia-arquivo" data-c="' + esc(a.c) + '" title="' + esc(a.c) + '">' + icone(ic) + "<span>" + esc(a.nome) + onde + "</span></button>";
      }).join("");
      if (g[0] === "falas") return '<details class="ep-grupo" data-ep-falas><summary>' + esc(g[1]) + " (" + lista.length + ")</summary><div class=\"arquivos-ia-lista\">" + botoes + "</div></details>";
      return '<div class="ep-grupo"><p class="arquivos-ia-titulo">' + esc(g[1]) + '</p><div class="arquivos-ia-lista">' + botoes + "</div></div>";
    }).join("");
    return topo + chips + grupos + "</section>";
  }
  function desenharEp() {
    var el = document.getElementById("ep-ia");
    if (el) { var aberto = !!el.querySelector("details[data-ep-falas][open]"); el.outerHTML = epHtml(); if (aberto) { var d = document.querySelector("#ep-ia details[data-ep-falas]"); if (d) d.open = true; } }
    var at = document.getElementById("atalhos-ia");
    if (at) at.outerHTML = atalhosHtml();
  }
  var IA_PASSOS = [["Gravar a voz", "grava a voz deste episódio agora. Antes, diga em uma frase quanto tempo leva e quanto custa."],
    ["Montar a prévia", "monta a folha de quadros e a prévia deste episódio e me mostra os arquivos aqui no chat"],
    ["Fazer o vídeo final", "faz o vídeo final deste episódio e me mostra aqui no chat"],
    ["Pacote das redes", "gera o pacote das redes escolhidas deste episódio (vídeo, capa e legenda de cada rede)"]];
  function atalhosHtml() {
    var ep = epAtual();
    if (ep) {
      return '<div class="atalhos-ia" id="atalhos-ia" data-tour="ia-atalhos"><span class="meta">Próximo passo:</span>' + IA_PASSOS.map(function (a) {
        return '<button type="button" class="ideia" data-acao="ia-atalho" data-texto="' + esc(a[1] + " (episódio " + ep.id + ")") + '" data-mostrar="' + esc(a[0]) + '">' + esc(a[0]) + "</button>";
      }).join("") + "</div>";
    }
    var tudo = pedidoUnico();
    return '<div class="atalhos-ia" id="atalhos-ia" data-tour="ia-atalhos"><span class="meta">Pedidos prontos:</span>' + IA_ATALHOS.map(function (a) {
      var t = a[1] || tudo.texto;
      return t ? '<button type="button" class="ideia" data-acao="ia-atalho" data-texto="' + esc(t) + '" data-mostrar="' + esc(a[0]) + '"' + (a[1] ? "" : ' data-n="' + tudo.n + '"') + ">" + esc(a[0]) + "</button>" : "";
    }).join("") + "</div>";
  }
  /* Conversas anteriores do estúdio, de qualquer lugar (painel, terminal, Claude Desktop): abrir e continuar. */
  function quandoTexto(seg) {
    var d = new Date(seg * 1000), hoje = new Date();
    var hora = ("0" + d.getHours()).slice(-2) + ":" + ("0" + d.getMinutes()).slice(-2);
    if (d.toDateString() === hoje.toDateString()) return "hoje, " + hora;
    return ("0" + d.getDate()).slice(-2) + "/" + ("0" + (d.getMonth() + 1)).slice(-2) + ", " + hora;
  }
  /* Conversa mais nova feita fora do painel (terminal, Claude Desktop): avisa e deixa abrir com um toque. */
  function checarConversaNova() {
    var caixa = document.getElementById("ia-mais-nova");
    if (!caixa || ESTATICO || iaCli !== "claude") return;
    var c = conversaDe("claude");
    if (c.rodando) { caixa.hidden = true; return; }
    fetch("/api/ia/conversas", { credentials: "same-origin", headers: { "X-Painel-Token": TOKEN } })
      .then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; })
      .then(function (j) {
        var nova = j && (j.conversas || [])[0];
        var caixa2 = document.getElementById("ia-mais-nova");
        if (!caixa2) return;
        var mostrar = nova && nova.id !== c.id && nova.quando * 1000 > (c.atualizado || 0) + 5000;
        caixa2.hidden = !mostrar;
        if (mostrar) caixa2.innerHTML = icone("atualizar") + '<p><b>Tem uma conversa mais nova, feita fora do painel.</b> <span>' + esc(nova.titulo) + "</span></p>" +
          botao("Abrir essa conversa", 'data-acao="ia-abrir-conversa" data-id="' + esc(nova.id) + '"', "secundario mini", "seguir");
      });
  }
  function abrirHistoricoIA() {
    abrirJanela("Conversas anteriores", '<p class="meta">Carregando…</p>', "", "janela-historico");
    fetch("/api/ia/conversas", { credentials: "same-origin", headers: { "X-Painel-Token": TOKEN } })
      .then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; })
      .then(function (j) {
        var lista = (j && j.conversas) || [];
        var atual = conversaDe("claude").id;
        var corpo = lista.length ? '<p class="meta">Todas as conversas desta pasta: as do painel, as do terminal e as do Claude Desktop. Abra uma para ler e continuar de onde parou.</p><ul class="historico-ia">' + lista.map(function (x) {
          return '<li><button type="button" class="historico-item' + (x.id === atual ? " atual" : "") + '" data-acao="ia-abrir-conversa" data-id="' + esc(x.id) + '"><b>' + esc(x.titulo) + "</b><small>" + esc(quandoTexto(x.quando)) + " · " + x.pedidos + (x.pedidos === 1 ? " pedido" : " pedidos") + (x.id === atual ? " · aberta agora" : "") + "</small></button></li>";
        }).join("") + "</ul>" : '<p class="lead">Ainda não tem conversa salva nesta pasta.</p>';
        if (document.getElementById("janela").open) abrirJanela("Conversas anteriores", corpo, "", "janela-historico");
      });
  }
  function abrirConversaIA(id) {
    fetch("/api/ia/conversa?id=" + encodeURIComponent(id), { credentials: "same-origin", headers: { "X-Painel-Token": TOKEN } })
      .then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; })
      .then(function (j) {
        if (!j || !j.ok) { toast((j && j.msg) || "Não consegui abrir essa conversa.", "aviso"); return; }
        iaCli = "claude"; gravarLocal("iaCli", iaCli);
        iaConversas.claude = { id: j.id, msgs: j.msgs, rodando: false, atualizado: Date.now() };
        guardarConversas(true); fecharJanela();
        if (telaAtual() !== "conversar") location.hash = "#conversar"; else redesenhar();
        setTimeout(function () { var log = document.getElementById("chat-log"); if (log) log.scrollTop = log.scrollHeight; }, 60);
        toast("Conversa aberta. Escreva para continuar de onde parou.");
      });
  }
  function abrirArquivoIA(rel) {
    var pasta = rel.split("/").slice(0, -1).join("/");
    var pe = botao("Abrir a pasta", 'data-acao="abrir" data-caminho="' + esc(pasta) + '"', "secundario", "abrir") + botao("Fechar", 'data-acao="fechar-janela"', "");
    fetch("/api/ia/arquivo?c=" + encodeURIComponent(rel), { credentials: "same-origin", headers: { "X-Painel-Token": TOKEN } })
      .then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; })
      .then(function (j) {
        if (!j || !j.ok) { toast((j && j.msg) || "Não achei esse arquivo.", "aviso"); return; }
        var url = midia(rel), corpo;
        if (j.tipo === "texto") corpo = '<pre class="arquivo-texto">' + esc(j.texto) + "</pre>";
        else if (/^video/.test(j.mime)) corpo = '<video class="arquivo-midia" controls playsinline preload="metadata" src="' + url + '"></video>';
        else if (/^audio/.test(j.mime)) corpo = '<audio class="arquivo-midia" controls preload="metadata" src="' + url + '"></audio>';
        else corpo = '<img class="arquivo-midia" alt="" src="' + url + '">';
        abrirJanela(j.nome, corpo + '<p class="meta">' + esc(rel) + "</p>", pe, "janela-arquivo");
      });
  }
  function pararIA() {
    var c = conversaDe(iaCli);
    // Pelo programa, não pela conversa: só roda um pedido por vez, e o que roda pode ser de outra conversa.
    api("POST", "/api/ia/parar", { cli: iaCli }).then(function (r) {
      toast(r.msg || "A IA parou.", r.ok ? "" : "aviso");
      if (c.retomada) { c.rodando = false; c.retomada = false; guardarConversas(true); }
      carregarIA(true).then(function () { desenharChat(); });
    });
    if (c.ctrl) c.ctrl.abort();
  }
  /* Mandar um pedido pronto pro chat do painel; sem o chat, copiar e dizer onde colar. */
  function pedirIA(texto, botaoEl, mostrar) {
    if (!ESTATICO && iaPronta() && !conversaDe(iaCli).rodando) {
      if (telaAtual() !== "conversar") location.hash = "#conversar";
      setTimeout(function () { mandarIA(texto, mostrar); }, 80);
      return;
    }
    if (iaPronta() && conversaDe(iaCli).rodando) { toast("A IA ainda está trabalhando no pedido anterior. Espere ela terminar.", "aviso"); return; }
    copiar(texto, botaoEl, "Pedido copiado. Cole no chat da IA (Claude Code ou Codex) e mande.");
  }
  /* "Pedir pra IA arrumar tudo": a mesma confirmação curta em toda tela. */
  function confirmarArrumar(texto, n, botaoEl) {
    if (!iaPronta() || ESTATICO) { pedirIA(texto, botaoEl); return; }
    iaPendente = texto;
    abrirJanela("Pedir pra IA arrumar", '<p class="lead">Vou pedir para a IA arrumar ' + (n === 1 ? "1 coisa" : n + " coisas") + ". Usa a sua conta da IA. Continuar?</p>",
      botao("Continuar", 'data-acao="arrumar-ok"', "", "seguir") + botao("Agora não", 'data-acao="fechar-janela"', "secundario"), "janela-confirma");
  }
  /* Chat e coluna da esquerda vão até o pé da tela: mede onde a grade começa e guarda em --ia-topo (o CSS desconta). */
  function ajustarAlturaIA() {
    var g = document.querySelector(".grade-ia");
    if (!g) return;
    var topo = g.getBoundingClientRect().top + (window.scrollY || 0);
    document.documentElement.style.setProperty("--ia-topo", Math.round(topo) + "px");
  }
  window.addEventListener("resize", function () { if (telaAtual() === "conversar") ajustarAlturaIA(); });
  T.conversar = function () {
    if (ESTATICO) {
      return voltarLinha("conversar") + vazio(ilustracao("ideias", "tv-notebook", "vazio-ilustra"), "A conversa fica no painel do computador", link("Fazer um vídeo", "#fazer", "botao gigante", "claquete"), "Na versão só para ver não dá pra conversar com a IA.");
    }
    if (!iaEstado) carregarIA().then(function () { if (telaAtual() === "conversar" && !editando()) redesenhar(); });
    var c = conversaDe(iaCli);
    var inst = iasInstaladas();
    var lado;
    if (!iaEstado) {
      lado = '<aside class="lado-ia"><section data-tour="ia-escolha"><h2 class="bloco-titulo">Sua IA</h2>' + esqueleto(1) + "</section></aside>";
    } else if (!inst.length) {
      var p = (iaEstado.claude && iaEstado.claude.passos) || [];
      lado = '<aside class="lado-ia"><section class="plano passos-ia-box" data-tour="ia-escolha"><h2 class="bloco-titulo menor">Instale a IA pra conversar aqui</h2>' +
        (p.length ? '<ol class="passos-ia">' + p.map(function (x) { return "<li>" + esc(limparCaminhos(x)) + "</li>"; }).join("") + "</ol>" : '<p class="apoio">Instale o Claude Code ou o Codex e entre na sua conta.</p>') +
        botao("Já instalei: conferir de novo", 'data-acao="ia-conferir"', "secundario", "atualizar") + "</section></aside>";
    } else {
      var escolhas = inst.length > 1 ? '<div class="respostas" role="radiogroup" aria-label="Qual IA">' + inst.map(function (k) {
        var f = estadoIAFrase(iaEstado[k]), m = k === iaCli;
        return '<button type="button" class="opcao ia-opcao" role="radio" aria-checked="' + m + '" aria-pressed="' + m + '" data-acao="ia-escolher" data-cli="' + k + '">' +
          '<span class="texto"><strong>' + esc(IA_NOMES[k][0]) + '</strong><small class="' + f[1] + '">' + esc(f[0]) + "</small></span>" +
          '<span class="marcador">' + (m ? icone("certo") : "") + "</span></button>";
      }).join("") + "</div>" : (function () {
        var f = estadoIAFrase(iaEstado[iaCli]);
        return '<div class="sua-ia"><strong>' + esc(IA_NOMES[iaCli][0]) + '</strong><small class="' + f[1] + '">' + esc(f[0]) + "</small></div>";
      })();
      var e = iaEstado[iaCli];
      var passos = e && !e.chat && (e.passos || []).length ? '<div class="plano passos-ia-box"><h2 class="bloco-titulo menor">Para conversar por aqui</h2><ol class="passos-ia">' +
        e.passos.map(function (x) { return "<li>" + esc(limparCaminhos(x)) + "</li>"; }).join("") + "</ol>" + botao("Já fiz: conferir de novo", 'data-acao="ia-conferir"', "secundario", "atualizar") + "</div>" : "";
      lado = '<aside class="lado-ia"><section data-tour="ia-escolha"><h2 class="bloco-titulo">' + (inst.length > 1 ? "Qual IA?" : "Sua IA") + "</h2>" + escolhas + "</section>" + passos +
        epHtml() +
        '<details class="abrir-ia" data-tour="ia-abrir"><summary>Avançado: abrir a IA numa janela própria</summary>' + botao("Abrir numa janela separada", 'data-acao="ia-abrir"', "secundario largo", "abrir") +
        '<p class="meta">Só para instalar programas. O vídeo inteiro se faz aqui no chat.</p></details></aside>';
    }
    if (!iaEps) carregarEps();
    setTimeout(checarConversaNova, 300);
    setTimeout(ajustarAlturaIA, 0);
    var atalhos = atalhosHtml();
    var nomeIa = IA_NOMES[iaCli] ? IA_NOMES[iaCli][0] : "IA";
    var conversa = '<section class="chat" aria-label="Conversa com ' + esc(nomeIa) + '" data-tour="ia-conversa">' +
      '<div class="chat-topo"><b>' + esc(nomeIa) + "</b><span class=\"chat-topo-acoes\">" +
      (iaCli === "claude" && !c.rodando ? '<button type="button" class="discreto mini" data-acao="ia-historico" data-tour="ia-historico">Conversas anteriores</button>' : "") +
      (c.msgs.length && !c.rodando ? '<button type="button" class="discreto mini" data-acao="ia-nova">Começar outra conversa</button>' : "") + "</span></div>" +
      '<div class="ia-mais-nova" id="ia-mais-nova" hidden></div>' +
      '<div class="chat-log" id="chat-log" aria-live="polite">' + chatHtml() + "</div>" + atalhos +
      '<form class="chat-escrever" data-form="ia"><label class="so-leitor" for="chat-texto">Sua mensagem</label>' +
      '<textarea class="entrada" id="chat-texto" rows="2" maxlength="8000" placeholder="Escreva o que você quer…" data-acao-mudar="ia-rascunho">' + esc(iaRascunho) + "</textarea>" +
      '<div class="chat-botoes">' + botao("Parar", 'data-acao="ia-parar"' + (c.rodando ? "" : " hidden"), "secundario", "pausa") +
      botao("Mandar", 'data-acao="ia-mandar" data-tour="ia-mandar"' + (c.rodando || !iaPronta() ? " disabled" : ""), "", "seguir") + "</div></form></section>";
    return '<div class="voltar-linha voltar-ia">' + link("Início", "#inicio", "discreto claro sem-linha voltar", "voltar") + '<h1 class="titulo titulo-ia">Conversar com a IA</h1>' +
      '<span class="voltar-direita"><button type="button" class="discreto mini" data-acao="tour">Me mostra como usa</button></span></div>' + '<div class="grade-ia">' + lado + conversa + "</div>";
  };

  /* ------------------------------------------------------------ meu canal */
  function bioCanal() {
    var n = String(valor("canal", "nicho") || "").trim();
    if (!n) return "Vídeo novo todo dia.";
    return n.charAt(0).toUpperCase() + n.slice(1).replace(/[.\s]+$/, "") + ". Vídeo novo todo dia.";
  }
  function linhaCanal(campo, rotulo, texto, editor) {
    var aberto = editandoLinha === campo;
    return '<div class="def-linha' + (aberto ? " aberta" : "") + '" data-linha="' + campo + '"><dt>' + esc(rotulo) + "</dt>" +
      (aberto ? '<dd class="editor">' + editor + "</dd>" : '<dd><span class="valor">' + esc(texto || "—") + "</span>" +
        (ESTATICO ? "" : '<button type="button" class="discreto mini" data-acao="linha-mudar" data-campo="' + campo + '" aria-label="Mudar ' + esc(rotulo) + '">Mudar</button>') + "</dd>") + "</div>";
  }
  function editorTexto(secao, campo, longo) {
    var m = meta(secao, campo) || {}, v = valor(secao, campo) || "", id = "ed-" + campo;
    var caixa = longo ? '<textarea class="entrada" rows="2" id="' + id + '" data-linha-campo="' + secao + "." + campo + '" maxlength="' + (m.max || 300) + '">' + esc(v) + "</textarea>"
      : (m.tipo === "arroba" ? '<div class="com-prefixo"><span aria-hidden="true">@</span><input class="entrada" type="text" id="' + id + '" data-linha-campo="' + secao + "." + campo + '" value="' + esc(v) + '" maxlength="30" autocomplete="off" autocapitalize="none" spellcheck="false"></div>'
        : '<input class="entrada" type="text" id="' + id + '" data-linha-campo="' + secao + "." + campo + '" value="' + esc(v) + '" maxlength="' + (m.max || 60) + '" autocomplete="off">');
    return '<label class="so-leitor" for="' + id + '">' + esc(m.rotulo || campo) + "</label>" + caixa + '<p class="erro-msg" hidden></p>' +
      (m.tipo === "arroba" ? '<div class="arroba-resultado" aria-live="polite"></div>' : "") +
      '<div class="acoes-linha">' + botao("Pronto", 'data-acao="linha-salvar" data-secao="' + secao + '" data-campo="' + campo + '"', "secundario", "certo") +
      (m.tipo === "arroba" ? '<button type="button" class="discreto mini" data-acao="arroba">Conferir se está livre</button>' : "") +
      '<button type="button" class="discreto mini" data-acao="linha-cancelar">Cancelar</button></div>';
  }
  T.canal = function () {
    var c = E.canal || {};
    var nome = valor("canal", "nome"), arroba = valor("canal", "arroba"), padrao = valor("roteiro", "estilo_padrao");
    var redes = valor("redes", "escolhidas") || [];
    var capas = (E.episodios || []).map(capaEp).filter(Boolean).map(midia).slice(0, 6);
    var ca = E.canais || {};
    var perfil = '<aside class="perfil" data-tour="perfil"><div class="celular-perfil">' + avatarHtml(c).replace('class="avatar"', 'class="avatar grande"') +
      "<b>" + esc(nome || "Seu canal") + "</b><span>" + esc(arroba ? "@" + arroba : "ainda sem @") + "</span><p>" + esc(bioCanal()) + "</p>" +
      '<div class="redes-perfil">' + redes.map(function (r) { return selo(r, true); }).join("") + "</div>" +
      (capas.length ? '<div class="grade-perfil">' + capas.map(function (s) { return '<img src="' + esc(s) + '" alt="" loading="lazy">'; }).join("") +
        new Array((3 - capas.length % 3) % 3 + 1).join('<span class="vaga" aria-hidden="true"></span>') + "</div>"
        : '<div class="perfil-vazio">' + ilustracao("vazio-videos", "tv-notebook") + "<span>Seus vídeos aparecem aqui.</span></div>") + "</div>" +
      '<p class="meta">É assim que o canal aparece pra quem vê.</p>' +
      (ca.disponivel && !ESTATICO ? '<button type="button" class="discreto" data-acao="canais">Trocar de canal</button>' : "") + "</aside>";
    var estilo = suspensa({ id: "ed-estilo", rotuloId: "rot-estilo", acaoMudar: "estilo-padrao", valor: padrao, dis: ESTATICO,
      opcoes: estilosLista().map(function (x) { return [x.id, nomeEstilo(x.id), x.duracao, capaEstilo(x)]; }).concat(ESTATICO ? [] : [["__criar", "Criar meu estilo", "cores e personagens só seus", ""]]) });
    var linhas = '<dl class="def-linhas" data-tour="linhas">' +
      linhaCanal("nome", "Nome", nome, editorTexto("canal", "nome")) +
      linhaCanal("arroba", "@", arroba ? "@" + arroba : "", editorTexto("canal", "arroba")) +
      linhaCanal("nicho", "Assunto", valor("canal", "nicho"), editorTexto("canal", "nicho", true)) +
      linhaCanal("publico", "Quem assiste", valor("canal", "publico"), editorTexto("canal", "publico", true)) +
      '<div class="def-linha"><dt id="rot-estilo">Estilo padrão</dt><dd>' + estilo + "</dd></div></dl>";
    return voltarLinha("canal") + cabeca("Meu canal", "Nome, assunto e onde postar. Muda quando quiser, salva sozinho.", salvoHtml() + '<span class="placa-canal" aria-hidden="true">' + ilustracao("canal", "tv-frente") + "<span>" + esc(nome || "Seu canal") + "</span></span>") +
      '<div class="grade-canal">' + perfil + '<div class="lado-canal">' + linhas +
      '<div class="acoes-linha">' + (ESTATICO ? "" : botao("Refazer as perguntas", 'data-acao="refazer" data-tour="refazer"', "secundario", "atualizar")) +
      link("Redes", "#redes") + link("Jeito dos vídeos", "#jeito") + "</div>" +
      recolhe("Logo e mascote", "O logo aparece redondo no fim do vídeo e no perfil", formSecao("canal", { campos: ["logo", "mascote"], titulo: false, ancora: "form-canal-imagens" })) +
      recolhe("Cores do canal", "As cores das palavras em destaque e do fundo", formSecao("canal", { campos: ["cor_destaque", "cor_destaque2", "cor_destaque3", "cor_fundo", "idioma"], titulo: false, ancora: "form-canal-cores" })) +
      (true ? recolhe("Grátis ou pago", "O caminho do canal: muda a IA e a voz", formSecao("canal", { campos: ["caminho"], titulo: false, ancora: "form-canal-caminho" })) : "") +
      "</div></div>";
  };

  /* ------------------------------------------------------------ redes */
  var HORARIOS = [["De manhã", "entre 7h e 9h, no mesmo horário todo dia"], ["No almoço", "entre 11h e 13h, no mesmo horário todo dia"], ["À noite, das 18h às 21h", "entre 18h e 21h, no mesmo horário todo dia"]];
  function detalhesRede(r) {
    var d = ((P().esquema || {}).redes_detalhe || {})[r] || {};
    var s = Number(d.duracao_max_s || 0);
    var dur = s >= 120 ? Math.round(s / 60) + " minutos" : s + " segundos";
    var cta = String(d.cta || "").replace("{alvo}", "a parte 2").toLowerCase();
    var l = [];
    if (s) l.push("Vídeo de até " + dur + (d.formato === "16:9" ? ", deitado, para ver na TV e no computador." : "."));
    if (d.hashtags_max) l.push("Até " + d.hashtags_max + " hashtags.");
    if (d.legenda_max) l.push("Legenda de até " + Number(d.legenda_max).toLocaleString("pt-BR") + " letras.");
    if (cta) l.push("No fim, a voz chama: “" + cta.charAt(0).toUpperCase() + cta.slice(1) + "”.");
    return l;
  }
  T.redes = function () {
    var escolhidas = valor("redes", "escolhidas") || [];
    var rec = recomendado("redes", "escolhidas") || [];
    var opcoes = (meta("redes", "escolhidas") || { opcoes: Object.keys(REDES) }).opcoes;
    var linha = function (r) {
      var lig = escolhidas.indexOf(r) >= 0, aberto = !!detalheRede[r];
      var btnDet = '<button type="button" class="discreto" data-acao="rede-detalhe" data-rede="' + r + '" aria-expanded="' + aberto + '" aria-controls="det-' + r + '">' + (aberto ? "Esconder detalhes" : "Ver detalhes") + "</button>";
      return '<li><div class="opcao linha-rede' + (lig ? " ligada" : "") + '">' + selo(r) +
        '<span class="texto"><strong>' + esc(nomeRede(r)) + "</strong><small>" + esc(REDES[r][3]) + "</small>" +
        '<span class="so-cel">' + btnDet.replace('class="discreto"', 'class="discreto mini"') + "</span></span>" +
        '<span class="so-pc">' + btnDet + "</span>" +
        '<button type="button" class="alternador" role="switch" aria-checked="' + lig + '" aria-label="Postar no ' + esc(nomeRede(r)) + '" data-acao="rede-ligar" data-rede="' + r + '"' + (ESTATICO ? " disabled" : "") + '><span class="trilho" aria-hidden="true"></span><span class="palavra">' + (lig ? "Sim" : "Não") + "</span></button></div>" +
        '<ul class="detalhe-rede" id="det-' + r + '"' + (aberto ? "" : " hidden") + ">" + detalhesRede(r).map(function (t) { return "<li>" + esc(t) + "</li>"; }).join("") + "</ul></li>";
    };
    var recs = opcoes.filter(function (r) { return rec.indexOf(r) >= 0; }), outras = opcoes.filter(function (r) { return rec.indexOf(r) < 0; });
    var lista = '<div class="grupos-redes" data-tour="redes"><h2 class="grupo-titulo">Recomendadas <span class="etiqueta">recomendado</span></h2><ul class="lista-redes">' + recs.map(linha).join("") + "</ul>" +
      (outras.length ? '<h2 class="grupo-titulo">Outras</h2><ul class="lista-redes">' + outras.map(linha).join("") + "</ul>" : "") + "</div>";
    var hora = valor("redes", "horario") || "";
    var algum = HORARIOS.some(function (h) { return h[1] === hora; });
    var horario = '<section class="horario" data-tour="horario"><h2 class="bloco-titulo">Que horas você costuma postar?</h2><div class="linha">' +
      '<div class="segmentos" role="radiogroup" aria-label="Horário">' + HORARIOS.map(function (h) {
        return '<button type="button" role="radio" aria-checked="' + (h[1] === hora) + '" aria-pressed="' + (h[1] === hora) + '" data-acao="ajuste" data-secao="redes" data-campo="horario" data-valor="' + esc(JSON.stringify(h[1])) + '">' + esc(h[0]) + "</button>";
      }).join("") + '</div><span class="mao so-pc">o que mais dá certo</span></div>' +
      (!algum && hora ? '<p class="meta">Agora: ' + esc(hora) + ".</p>" : "") + "</section>";
    var fora = opcoes.filter(function (r) { return escolhidas.indexOf(r) < 0; }).map(nomeRede);
    var pacote = '<aside class="plano pacote" data-tour="pacote"><h2 class="bloco-titulo">Cada vídeo vai sair com</h2><ul>' + escolhidas.map(function (r) {
      var d = ((P().esquema || {}).redes_detalhe || {})[r] || {};
      var yt = /^youtube/.test(r);
      return "<li>" + selo(r) + "<div><b>Pasta do " + esc(nomeRede(r)) + "</b><span>" + (yt ? "Vídeo, capa, título e descrição" : "Vídeo, capa e legenda com até " + (d.hashtags_max || 5) + " hashtags") + "</span></div></li>";
    }).join("") + "</ul>" + (fora.length ? '<p class="fora">' + esc(fora.join(" e ").replace(/ e (?=.* e )/g, ", ")) + (fora.length === 1 ? " fica" : " ficam") + " de fora até você ligar.</p>" : "") + "</aside>";
    return voltarLinha("redes") + cabeca("Onde você vai postar?", "Ligue as redes. Cada vídeo sai pronto pra cada uma, com a legenda certa.", salvoHtml() + ilustracao("redes", "tv-rede", "cabeca-ilustra pequena")) +
      '<div class="grade-redes"><div>' + lista + horario +
      recolhe("Hashtags em todo vídeo", "As que entram sempre, além das do assunto", formSecao("redes", { campos: ["hashtags_fixas"], titulo: false })) + "</div>" + pacote + "</div>";
  };

  /* ------------------------------------------------------------ jeito dos vídeos */
  var AJUSTES = [
    ["Tamanho da letra", "O texto que aparece na tela", "legenda", "tamanho", [["Pequena", 52], ["Média", 64], ["Grande", 78]]],
    ["Qual voz fala", "Grátis ou paga", "voz", "provedor", [["Google", "gemini"], ["Kokoro", "kokoro"], ["ElevenLabs", "elevenlabs"]]],
    ["Tempo pra prender", "Quando o assunto fica claro", "ganchos", "gancho_max_s", [["2 s", 2], ["3 s", 3], ["5 s", 5]]],
    ["Como o vídeo termina", "O que a pessoa faz no fim", "roteiro", "tipo_voto", [["Pergunta", "pergunta_aberta"], ["Só termina", "sem_voto"]]],
    ["Chamada no meio", "Uma frase pedindo pra seguir", "roteiro", "cta_meio", [["Não", false], ["Sim", true]]]
  ];
  function ajusteLinha(a) {
    var v = valor(a[2], a[3]), rec = recomendado(a[2], a[3]);
    var recRot = (a[4].filter(function (o) { return String(o[1]) === String(rec); })[0] || [])[0];
    var mudou = rec !== undefined && rec !== "" && String(v) !== String(rec) && recRot;
    var faltaChave = a[3] === "provedor" && v !== "kokoro" && !((E.chaves || {})[v === "gemini" ? "GEMINI_API_KEY" : "elevenlabs"]);
    return '<li class="ajuste"><div class="nome"><b>' + esc(a[0]) + "</b><span>" + esc(a[1]) + "</span>" +
      (mudou ? '<span class="mudou">Você mudou. <button type="button" class="discreto mini" data-acao="campo-rec" data-secao="' + a[2] + '" data-campo="' + a[3] + '">Voltar pra ' + esc(recRot) + "</button></span>" : "") +
      (faltaChave ? '<span class="mudou">Falta ligar esta voz. ' + link("Ligar", "#voz", "discreto mini") + "</span>" : "") + "</div>" +
      '<div class="controle"><div class="segmentos" role="radiogroup" aria-label="' + esc(a[0]) + '">' + a[4].map(function (o) {
        var marcado = String(o[1]) === String(v);
        return '<button type="button" role="radio" aria-checked="' + marcado + '" aria-pressed="' + marcado + '" data-acao="ajuste" data-secao="' + a[2] + '" data-campo="' + a[3] + '" data-valor="' + esc(JSON.stringify(o[1])) + '"' + (ESTATICO ? " disabled" : "") + ">" + esc(o[0]) + "</button>";
      }).join("") + "</div>" + (a[3] === "tamanho" && a[4].every(function (o) { return String(o[1]) !== String(v); }) ? '<span class="meta">Agora: ' + esc(num(v)) + "</span>" : "") + "</div></li>";
  }
  function previaJeito() {
    var tam = Number(valor("legenda", "tamanho")) || 64, ativa = valor("legenda", "ativa") !== false;
    var cor = valor("legenda", "cor") || "#FFFFFF", dest = valor("legenda", "cor_destaque") || "#FFD23F";
    var est = estiloPorId(valor("roteiro", "estilo_padrao")) || estilosLista()[0];
    var capa = est ? capaEstilo(est) : "";
    var g = Number(valor("ganchos", "gancho_max_s")) || 3, voto = valor("roteiro", "tipo_voto");
    var a = assuntoCurto() || "o seu assunto";
    var frase = "Ninguém te contou isso sobre " + '<em style="color:' + esc(dest) + '">' + esc(a) + "</em>";
    return '<div class="previa" data-tour="previa"><div class="celular">' + (capa ? '<img src="' + esc(capa) + '" alt="">' : "") + '<span class="tempo">0:01</span>' +
      (ativa ? '<p class="letra" style="font-size:' + Math.round(tam * 0.5) + "px;color:" + esc(cor) + '">' + frase + "</p>" : '<p class="letra sem">sem texto na tela</p>') + "</div>" +
      '<div class="lado-previa"><div class="linha-tempo" aria-label="Como o vídeo anda"><span class="g" style="flex:' + g + '">Começo</span><span class="m" style="flex:' + Math.max(10, 20 - g) + '">Meio</span><span class="f" style="flex:3">Fim</span></div>' +
      '<p class="meta">Prende em até ' + num(g) + " s, segura no meio e termina " + (voto === "sem_voto" ? "com a frase do fim." : "numa pergunta.") + "</p></div></div>";
  }
  function pronunciaHtml() {
    var pr = E.pronuncia || { trocas: [], fora_da_fala: [], base: [] };
    var linha = function (t, i) {
      return '<tr><td><input class="entrada" type="text" aria-label="Palavra, linha ' + (i + 1) + '" data-pron="termo" data-padrao="' + esc(t.padrao || "") + '" value="' + esc(t.termo) + '" maxlength="60"' + (ESTATICO ? " disabled" : "") + "></td>" +
        '<td><input class="entrada" type="text" aria-label="Como a voz fala, linha ' + (i + 1) + '" data-pron="grafia" value="' + esc(t.grafia) + '" maxlength="80"' + (ESTATICO ? " disabled" : "") + "></td>" +
        "<td>" + (ESTATICO ? "" : '<button type="button" class="discreto mini" data-acao="pron-remover">Tirar</button>') + "</td></tr>";
    };
    return '<section class="pronuncia" id="pronuncia" aria-labelledby="pron-titulo"><h3 class="bloco-titulo" id="pron-titulo">Como a voz fala cada palavra</h3>' +
      '<p class="ajuda">Palavra que a voz fala errado: escreva como deve soar. Só muda a voz; a legenda continua com a grafia normal.</p>' +
      '<table class="tabela-pron"><thead><tr><th scope="col">Palavra</th><th scope="col">Como a voz fala</th><th scope="col"><span class="so-leitor">Ação</span></th></tr></thead><tbody id="pron-linhas">' +
      pr.trocas.map(linha).join("") + "</tbody></table>" +
      (ESTATICO ? "" : '<button type="button" class="discreto" data-acao="pron-adicionar">' + icone("lapis") + "<span>Pôr outra palavra</span></button>") +
      '<div class="campo"><label for="pron-fora">O que nunca falar (só aparece na tela)</label><textarea class="entrada" rows="3" id="pron-fora" data-pron="fora"' + (ESTATICO ? " disabled" : "") + ">" + esc((pr.fora_da_fala || []).join("\n")) + "</textarea>" +
      '<p class="ajuda">Um por linha. Nomes que a voz não deve dizer.</p></div><div class="msgs-pron"></div>' +
      recolhe("As palavras que o kit já conhece (" + (pr.base || []).length + ")", "A base de pronúncia que vem com o kit",
        '<div class="tabela"><table><thead><tr><th>Palavra</th><th>Como a voz fala</th></tr></thead><tbody>' + (pr.base || []).map(function (b) { return "<tr><td>" + esc(b[0]) + "</td><td>" + esc(b[1]) + "</td></tr>"; }).join("") + "</tbody></table></div>") + "</section>";
  }
  T.jeito = function () {
    var lista = estilosLista();
    if (!estiloPerfil) estiloPerfil = valor("roteiro", "estilo_padrao");
    var est = estiloPorId(estiloPerfil) || lista[0] || null;
    var perfil = est ? '<div class="campo"><span class="rotulo" id="sel-estilo-rot">Ver como cada estilo é montado</span>' +
      suspensa({ id: "sel-estilo", rotuloId: "sel-estilo-rot", acaoMudar: "perfil", valor: est.id, opcoes: lista.map(function (x) { return [x.id, nomeEstilo(x.id), x.duracao, capaEstilo(x)]; }) }) + "</div>" +
      '<div class="md estrutura">' + (est.estrutura_html || "") + "</div>" : "";
    var mais = formSecao("canal", { campos: ["tom", "nunca", "marca_registrada", "assinatura"], titulo: "Jeito de falar", ancora: "form-jeito-voz" }) +
      pronunciaHtml() + formSecao("roteiro") + formSecao("ganchos") + formSecao("voz") + formSecao("legenda") + formSecao("visual") + formSecao("capa") + formSecao("audio") + formSecao("render") +
      '<section class="perfil-estilo">' + perfil + "</section>";
    return voltarLinha("jeito", ESTATICO ? "" : '<button type="button" class="discreto" data-acao="jeito-rec" data-tour="recomendado">Voltar ao recomendado</button>') +
      cabeca("O jeito dos vídeos", "Mexa e veja na hora como fica. Tudo já começa no recomendado.", salvoHtml()) +
      '<div class="grade-jeito">' + previaJeito() + '<div><ul class="ajustes" data-tour="ajustes">' + AJUSTES.map(ajusteLinha).join("") + "</ul>" +
      recolhe("Mais ajustes", "Pronúncia de palavras, o que nunca falar, a frase do fim, cores, capa, som e mais", '<div class="mais-ajustes">' + mais + "</div>", ' id="mais-ajustes"', /^form-|pronuncia/.test(subRota())) + "</div></div>";
  };

  /* ------------------------------------------------------------ estilos */
  function palavrasDificuldade(d) {
    d = semAcento(d);
    if (/facil|baixa/.test(d)) return "Fácil de fazer";
    if (/media/.test(d)) return "Dá um pouco de trabalho";
    if (/alta|dificil/.test(d)) return "Mais trabalhoso";
    return d;
  }
  function estiloDetalhe(x) {
    var padrao = valor("roteiro", "estilo_padrao");
    var ex = x.exemplo || {};
    var visual = ex.video ? playerHtml(urlExemplo(x.id, "video"), capaEstilo(x), { mudo: true, auto: true, rotulo: "Exemplo do estilo " + nomeEstilo(x.id), total: "0:10" })
      : '<div class="exemplo exemplo-vazio">' + (capaEstilo(x) ? '<img src="' + esc(capaEstilo(x)) + '" alt="">' : '<span class="meta">exemplo em breve</span>') + "</div>";
    var gratis = String(x.gratis || "");
    return '<div class="voltar-linha">' + link("Os estilos", "#estilos", "discreto claro sem-linha voltar", "voltar") + '<span class="voltar-direita"><button type="button" class="discreto mini" data-acao="tour">Me mostra como usa</button></span></div>' +
      '<div class="grade-detalhe">' + visual + '<div class="detalhe-texto"><h1 class="titulo">' + esc(nomeEstilo(x.id)) + '</h1><p class="lead">' + esc(fraseEstilo(x)) + "</p>" +
      (x.resumo && x.resumo !== fraseEstilo(x) ? '<p class="apoio">' + esc(String(x.resumo).split(/(?<=\.)\s/).slice(0, 2).join(" ")) + "</p>" : "") +
      '<dl class="ficha-curta"><div><dt>Duração</dt><dd>' + esc(x.duracao) + "</dd></div><div><dt>Dificuldade</dt><dd>" + esc(palavrasDificuldade(x.dificuldade)) + "</dd></div>" +
      (gratis ? "<div><dt>Dá pra fazer grátis?</dt><dd>" + esc(gratis.charAt(0).toUpperCase() + gratis.slice(1)) + "</dd></div>" : "") + "</dl>" +
      '<div class="acoes-linha">' + link("Usar este estilo", "#fazer/" + x.id, "botao gigante", "", ' data-tour="usar-estilo"') + "</div>" +
      '<p class="meta">Todo vídeo sai com legenda, capa e versão pra cada rede.</p>' +
      '<div class="acoes-linha"><button type="button" class="discreto mini" data-acao="ficha" data-id="' + esc(x.id) + '">Ver a ficha completa</button>' +
      (x.id === padrao ? '<span class="meta">É o estilo padrão do seu canal.</span>' : (ESTATICO ? "" : '<button type="button" class="discreto mini" data-acao="usar-estilo" data-id="' + esc(x.id) + '">Deixar como padrão do canal</button>')) + "</div></div></div>";
  }
  T.estilos = function () {
    var x = estiloPorId(subRota());
    if (x) return estiloDetalhe(x);
    var lista = estilosLista();
    var acesos = objetivo === "facil" ? FACEIS : ((OBJETIVOS.filter(function (o) { return o[0] === objetivo; })[0] || [])[2] || null);
    var sentir = '<section class="sentir" data-tour="sentir"><h2>O que você quer que a pessoa faça no fim?</h2><div class="respostas" role="radiogroup" aria-label="Objetivo">' +
      OBJETIVOS.map(function (o) {
        var m = objetivo === o[0];
        return '<button type="button" class="opcao" role="radio" aria-checked="' + m + '" aria-pressed="' + m + '" data-acao="objetivo" data-id="' + o[0] + '"><span class="texto"><strong>' + esc(o[1]) + '</strong></span><span class="marcador">' + (m ? icone("certo") : "") + "</span></button>";
      }).join("") + '</div><button type="button" class="discreto" data-acao="objetivo" data-id="facil" aria-pressed="' + (objetivo === "facil") + '">Não sei, me sugere</button></section>';
    var criar = ESTATICO ? "" : '<li class="criar-estilo"><a href="#meuestilo" data-acao="criar-estilo" data-tour="criar-estilo"><span class="moldura">' + ilustra("tv-apontando", "figura-criar") + "</span>" +
      "<b>Criar meu estilo</b><span>100% do seu jeito</span></a></li>";
    var catalogo = '<ul class="catalogo" data-tour="catalogo">' + criar + lista.map(function (s) {
      var cl = acesos ? (acesos.indexOf(s.id) >= 0 ? "acende" : "apagado") : "";
      var capa = capaEstilo(s);
      return '<li class="' + cl + '"><a href="#estilos/' + esc(s.id) + '"><span class="moldura">' + (capa ? '<img src="' + esc(capa) + '" alt="" loading="lazy">' : "") +
        (FACEIS.indexOf(s.id) >= 0 ? '<span class="facil">Fácil</span>' : "") + "</span><b>" + esc(nomeEstilo(s.id)) + "</b><span>" + esc(s.duracao) + "</span></a></li>";
    }).join("") + "</ul>";
    return voltarLinha("estilos") + cabeca("Os " + lista.length + " estilos", "") + '<div class="grade-estilos">' + sentir + catalogo + "</div>";
  };

  /* ------------------------------------------------------------ criar meu estilo (o estilo desenhado do canal) */
  /* As perguntas vêm do estilo.py instalado (/api/estilo-proprio); aqui só ganham palavra de gente e uma amostra. */
  var meuEstilo = lerLocal("meuEstilo", null);
  var EP = null, epVigia = null;
  var PERGUNTA_AMIGA = {
    clima: ["Qual é o clima das histórias?", "É o que a pessoa sente vendo o vídeo."],
    lugar: ["Onde as histórias acontecem?", "Vira o cenário mais comum dos vídeos."],
    recorte: ["Como é o corte do papel?", "Todo desenho é papel recortado. Muda só a borda."],
    traco: ["Como é o traço do desenho?", "É o jeito da linha em volta de tudo."],
    cor: ["Que cores combinam com o canal?", "O kit sorteia uma caixa de papéis nessa linha."],
    proporcao: ["Como são os personagens?", "Vale pro elenco inteiro da série."],
    ameaca: ["O que move a história?", "É o que deixa a pessoa curiosa até o fim."],
    textura: ["Qual é a textura do papel?", "O acabamento que aparece em tudo."]
  };
  var OPCAO_AMIGA = {
    clima: { sombrio: "Suspense", melancolico: "Emocionante", absurdo: "Engraçado", nostalgico: "Nostálgico" },
    lugar: { interior_90: "Interior, anos 90", cidade_hoje: "Cidade grande, hoje", litoral: "Litoral", sertao: "Sertão", futuro_proximo: "Daqui a alguns anos" },
    recorte: { tesoura: "Tesoura", rasgado: "Rasgado à mão", picote: "Picotado", estilete: "Estilete" },
    traco: { nanquim: "Nanquim", lapis: "Lápis", caneta: "Caneta", pincel: "Pincel" },
    cor: { fria: "Frias", quente: "Quentes", sobria: "Escuras", destaque: "Uma cor gritando", dessaturada: "Apagadas" },
    proporcao: { cabecudo: "Cabeçudos", alongado: "Compridos", realista: "Como gente", arredondado: "Fofos" },
    ameaca: { criatura: "Uma criatura", presenca: "Uma presença", objeto: "Um objeto estranho", pessoa: "Uma pessoa" },
    textura: { fibra: "Com fibra", cartolina: "Cartolina lisa", seda: "Papel de seda", reciclado: "Reciclado", papel_velho: "Papel velho", vhs: "Fita VHS", pelicula: "Película", limpo: "Limpo" }
  };
  var CORES_AMOSTRA = {
    fria: ["#1F6984", "#223E77", "#5C7B2D", "#267366", "#812232"], quente: ["#83212E", "#AE4329", "#CC671E", "#E0AC29", "#1F657A"],
    sobria: ["#22404F", "#5E2632", "#536534", "#405777", "#9F7C38"], destaque: ["#202932", "#3F4A5A", "#567281", "#2B3450", "#D31730"],
    dessaturada: ["#5A6670", "#7D8790", "#8E7F72", "#6C7A6A", "#A39C8E"],
    sombrio: ["#101820", "#22334A", "#5E2632"], melancolico: ["#405777", "#8FA3B8", "#C9B8A0"], absurdo: ["#E0AC29", "#FF4F8B", "#2FD3C4"], nostalgico: ["#CC671E", "#E8C27A", "#6C8A5A"]
  };
  /* Amostra desenhada de cada opção (quando ajuda a escolher): papéis da cor, borda do corte, corpo do personagem, textura. */
  function amostraEstilo(q, o) {
    var sw = function (lista) { return '<span class="amostra-papeis">' + lista.map(function (c, i) { return '<i style="background:' + c + ";transform:rotate(" + ((i % 2 ? 1 : -1) * (2 + i)) + 'deg)"></i>'; }).join("") + "</span>"; };
    if ((q === "cor" || q === "clima") && CORES_AMOSTRA[o]) return sw(CORES_AMOSTRA[o]);
    var borda = { tesoura: "M4 30 L20 28 L36 31 L52 28 L68 30 L84 29 L96 30", rasgado: "M4 30 l6-5 5 7 6-8 4 9 7-6 5 5 6-7 5 8 7-6 5 6 6-5 5 6 6-4", picote: "M4 30 l4-6 4 6 4-6 4 6 4-6 4 6 4-6 4 6 4-6 4 6 4-6 4 6 4-6 4 6 4-6 4 6 4-6 4 6 4-6 4 6 4-6 4 6",
      estilete: "M4 30 L96 30", nanquim: "M4 30 C30 20 60 40 96 30", lapis: "M4 31 L96 29", caneta: "M4 30 L96 30", pincel: "M4 30 C25 22 45 38 70 26 S90 34 96 30" }[o];
    if (q === "recorte" || q === "traco") {
      return borda ? '<svg class="amostra-svg" viewBox="0 0 100 60" aria-hidden="true"><path d="' + borda + ' L96 56 L4 56 Z" fill="#FF7A3D" stroke="#041419" stroke-width="2.5" stroke-linejoin="round"/>' +
        '<path d="' + borda + '" fill="none" stroke="#FFF4DE" stroke-width="1.5" transform="translate(0 2)" opacity=".7"/></svg>' : "";
    }
    if (q === "proporcao") {
      var corpo = { cabecudo: [26, 14, 18, 22], alongado: [11, 10, 34, 12], realista: [14, 12, 28, 16], arredondado: [17, 18, 22, 24] }[o];
      if (!corpo) return "";
      var cab = corpo[0], larg = corpo[3], alt = corpo[2], cy = 56 - alt - cab;
      return '<svg class="amostra-svg" viewBox="0 0 100 60" aria-hidden="true"><rect x="' + (50 - larg / 2) + '" y="' + (56 - alt) + '" width="' + larg + '" height="' + alt + '" rx="' + (o === "arredondado" ? larg / 2 : 5) + '" fill="#2FD3C4" stroke="#041419" stroke-width="2.5"/>' +
        '<circle cx="50" cy="' + cy + '" r="' + cab / 2 + '" fill="#FFD7B5" stroke="#041419" stroke-width="2.5"/></svg>';
    }
    if (q === "textura") return '<span class="amostra-textura t-' + esc(o) + '" aria-hidden="true"></span>';
    return "";
  }
  function rotuloEstilo(q, o) { return (OPCAO_AMIGA[q] && OPCAO_AMIGA[q][o]) || bonito(o); }
  /* Resposta 100% livre: o sorteio do kit só conhece as opções prontas, então a pergunta vai como "auto" para ele e o
     texto da pessoa segue para a IA, que ajusta o estilo do jeito descrito. */
  var EXEMPLO_LIVRE = {
    clima: "Ex.: tenso, mas com uma piada no meio", lugar: "Ex.: uma cidade pequena do interior de Minas",
    recorte: "Ex.: borda ondulada, como tesoura de picotar", traco: "Ex.: linha grossa e tremida, como giz de cera",
    cor: "Ex.: roxo, verde-limão e preto", proporcao: "Ex.: baixinhos, cabeça grande e olhos enormes",
    ameaca: "Ex.: um vizinho que sabe demais", textura: "Ex.: folha de caderno com pauta azul"
  };
  function livreDe(q) { return (meuEstilo && meuEstilo.livre && meuEstilo.livre[q]) || ""; }
  function respostaEstilo(q, v) { return livreDe(q) ? "do meu jeito: " + livreDe(q) : (v && v !== "auto" ? rotuloEstilo(q, v) : ""); }
  function livreEstilo(q, me) {
    var t = livreDe(q);
    return '<div class="me-livre' + (t ? " marcado" : "") + '"><label for="me-livre">' + icone("lapis") + "<span><b>Do meu jeito</b><small>Nenhuma combina? Escreva como você quer.</small></span></label>" +
      '<div class="me-livre-linha"><textarea class="entrada" id="me-livre" rows="2" maxlength="240" placeholder="' + esc(EXEMPLO_LIVRE[q] || "Escreva do seu jeito") + '">' + esc(t) + "</textarea>" +
      botao("Usar o que eu escrevi", 'data-acao="me-livre" data-q="' + esc(q) + '"', "secundario", "certo") + "</div></div>";
  }
  function temLivre() { return !!(meuEstilo && meuEstilo.livre && Object.keys(meuEstilo.livre).some(function (k) { return meuEstilo.livre[k]; })); }
  function carregarEstiloProprio() {
    return api("GET", "/api/estilo-proprio").then(function (r) { EP = r && r.perguntas ? r : { disponivel: false, perguntas: [] }; return EP; });
  }
  function salvarMeuEstilo() { gravarLocal("meuEstilo", meuEstilo); }
  function vigiarSorteio() {
    clearTimeout(epVigia);
    epVigia = setTimeout(function () {
      carregarEstiloProprio().then(function (r) {
        if (telaAtual() === "meuestilo") redesenhar();
        if (r.sorteio && r.sorteio.rodando) vigiarSorteio();
      });
    }, 1200);
  }
  function pedidoEstiloIA() {
    var r = (meuEstilo && meuEstilo.r) || {};
    var partes = (EP && EP.perguntas || []).map(function (q) {
      var v = r[q.id], t = livreDe(q.id);
      return q.id + ": " + (t ? "do meu jeito, \"" + t.replace(/"/g, "'") + "\"" : (v && v !== "auto" ? v : "você escolhe"));
    });
    return "cria o estilo desenhado do meu canal (comandos/criar-estilo.md) com estas respostas: " + partes.join("; ") +
      (meuEstilo && meuEstilo.nome ? ". Nome do estilo: " + meuEstilo.nome : "") +
      (temLivre() ? ". As respostas \"do meu jeito\" não estão nas opções prontas: sorteie o resto e ajuste a paleta, o traço e o elenco para ficarem exatamente como eu descrevi" : "") +
      ". Me mostra a folha antes de gravar.";
  }
  function acaoIAEstilo(rotulo) {
    var t = pedidoEstiloIA();
    return iaPronta() ? botao(rotulo || "Mandar pra IA criar", 'data-acao="ia-pedir" data-texto="' + esc(t) + '"', "", "seguir")
      : botaoCopiar(t, "Copiar o pedido pra IA", "", "Pedido copiado. Agora cole no chat da IA.");
  }
  function progressoEstilo(i, n) {
    return '<div class="me-progresso"><span class="meta">Pergunta ' + (i + 1) + " de " + n + '</span><span class="me-barra" role="progressbar" aria-valuemin="0" aria-valuemax="' + n + '" aria-valuenow="' + (i + 1) + '"><i style="width:' + Math.round((i + 1) / n * 100) + '%"></i></span></div>';
  }
  T.meuestilo = function () {
    var volta = voltarLinha("meuestilo");
    if (ESTATICO) return volta + cabeca("Criar meu estilo", "Na versão só para ver não dá. Peça no chat da IA: cria o estilo do meu canal.");
    if (!EP) {
      carregarEstiloProprio().then(function () { if (telaAtual() === "meuestilo") redesenhar(); if (EP.sorteio && EP.sorteio.rodando) vigiarSorteio(); });
      return volta + cabeca("Criar meu estilo", "") + esqueleto(4);
    }
    var qs = EP.perguntas || [], s = EP.sorteio || {}, atual = EP.atual || {};
    if (!meuEstilo || !meuEstilo.r) { meuEstilo = { passo: -1, r: {}, nome: "" }; salvarMeuEstilo(); }
    var me = meuEstilo;
    if (!EP.disponivel) {
      return volta + '<section class="me-centro">' + ilustracao("erro", "tv-cade", "vazio-ilustra") + '<h1 class="titulo">Esta versão do kit ainda não desenha estilos</h1>' +
        '<p class="lead">A IA cria o estilo pra você na conversa, com as mesmas perguntas.</p><div class="acoes-centro">' + acaoIAEstilo("Pedir pra IA criar") + "</div></section>";
    }
    if (s.rodando) {
      return volta + '<section class="me-centro me-sorteando" aria-live="polite">' + ilustra("tv-notebook", "me-ilustra") +
        '<h1 class="titulo">' + (s.fase === "desenhando" ? "Desenhando os personagens" : "Sorteando as cores") + '<span class="pontos" aria-hidden="true"><i></i><i></i><i></i></span></h1>' +
        '<p class="lead">Leva uns segundos. Pode ir pra outra tela: o desenho continua.</p><span class="me-barra indeterminada" aria-hidden="true"><i></i></span></section>';
    }
    if (me.passo === "ver" && s.ok && s.resultado && s.resultado.folha) {
      var res = s.resultado, ficha = qs.map(function (q) {
        var t = livreDe(q.id);
        return '<li><span>' + esc((PERGUNTA_AMIGA[q.id] || [q.pergunta])[0].replace(/\?$/, "")) + "</span><b>" + esc(t ? "Do seu jeito: " + t : rotuloEstilo(q.id, s.respostas[q.id])) + "</b></li>";
      }).join("");
      var acoesVer = temLivre()
        ? '<p class="apoio">O sorteio usa só as opções prontas. As respostas do seu jeito a IA aplica por cima, antes de você aprovar.</p>' +
          '<div class="acoes me-acoes" data-tour="me-usar">' + acaoIAEstilo("Mandar pra IA deixar do meu jeito") + botao("Sortear de novo", 'data-acao="me-sortear"', "secundario", "atualizar") + "</div>"
        : '<div class="acoes me-acoes" data-tour="me-usar">' + botao("Gostei, usar", 'data-acao="me-usar"', "gigante", "certo") + botao("Sortear de novo", 'data-acao="me-sortear"', "secundario", "atualizar") + "</div>";
      return volta + '<div class="me-resultado"><button type="button" class="me-folha" data-acao="ampliar" data-src="' + esc(res.folha) + '" data-titulo="A folha do estilo" data-tour="me-folha">' +
        '<img src="' + esc(midia(res.folha)) + '" alt="Folha do estilo: as cores sorteadas e os três personagens"><span class="meta">Toque para ver maior</span></button>' +
        '<section class="me-lado"><h1 class="titulo">' + esc(s.nome || "Seu estilo") + '</h1><p class="lead">As cores, o corte do papel e o elenco de partida' + (res.elenco && res.elenco.length ? ": " + esc(res.elenco.join(", ")) : "") + ".</p>" +
        '<ul class="me-ficha">' + ficha + "</ul>" +
        acoesVer +
        '<button type="button" class="discreto" data-acao="me-mudar">Voltar e mudar uma resposta</button>' +
        '<p class="meta">Nada muda no canal até você tocar em Gostei, usar.</p></section></div>';
    }
    if (me.passo === "ver" && s.erro) {
      return volta + '<section class="me-centro">' + ilustracao("erro", "tv-cade", "vazio-ilustra") + '<h1 class="titulo">' + (s.falta ? "Falta uma parte do programa de desenho" : "O desenho não saiu desta vez") + "</h1>" +
        '<p class="lead">' + esc(s.falta ? "Este computador ainda não tem as partes que desenham. A IA instala e cria o estilo com as suas respostas." : s.erro) + "</p>" +
        '<div class="acoes-centro">' + acaoIAEstilo() + botao("Tentar de novo", 'data-acao="me-sortear"', "secundario", "atualizar") + "</div>" +
        '<button type="button" class="discreto" data-acao="me-mudar">Mudar uma resposta</button></section>';
    }
    if (me.passo === "feito") {
      return volta + '<section class="me-centro">' + (atual.folha ? '<img class="me-folha-mini" src="' + esc(midia(atual.folha)) + '" alt="A folha do estilo do canal">' : ilustra("tv-rede", "me-ilustra")) +
        '<h1 class="titulo">Pronto! Esse é o estilo do canal</h1><p class="lead">Vale pras séries com voto, do primeiro episódio até o fim da série.</p>' +
        '<div class="acoes-centro">' + (me.origem === "mago" ? botao("Voltar pras perguntas do canal", 'data-acao="me-voltar-mago"', "gigante", "seguir") : link("Fazer um vídeo", "#fazer", "botao gigante", "claquete")) +
        link("Ver os estilos", "#estilos", "botao secundario") + "</div></section>";
    }
    if (me.passo === "mudar") {
      return volta + cabeca("Qual resposta você quer mudar?", "Toque numa. Depois o kit sorteia de novo.") + '<ul class="me-mudar-lista">' + qs.map(function (q, i) {
        var v = me.r[q.id];
        return '<li><button type="button" class="opcao" data-acao="me-ir" data-i="' + i + '"><span class="texto"><strong>' + esc((PERGUNTA_AMIGA[q.id] || [q.pergunta])[0]) + "</strong><small>" +
          esc(respostaEstilo(q.id, v) || (s.respostas && s.respostas[q.id] ? rotuloEstilo(q.id, s.respostas[q.id]) + " (o kit escolheu)" : "o kit escolhe")) + "</small></span>" + icone("lado", "seta") + "</button></li>";
      }).join("") + "</ul>";
    }
    if (me.passo < 0) {
      return volta + '<section class="me-centro me-intro">' + ilustra("tv-apontando", "me-ilustra") + '<h1 class="titulo">Criar o estilo do seu canal</h1>' +
        '<p class="lead">São ' + qs.length + " perguntas rápidas, uma por tela. No fim o kit desenha uma folha com as cores e os personagens pra você ver antes de usar.</p>" +
        '<div class="acoes-centro">' + botao("Começar", 'data-acao="me-ir" data-i="0"', "gigante", "seguir") + "</div>" +
        (atual.tem ? '<p class="meta">O canal já tem um estilo' + (atual.nome ? " (" + esc(atual.nome) + ")" : "") + ". Ele só muda se você gostar do novo.</p>" : "") + "</section>";
    }
    if (me.passo < qs.length) {
      var q = qs[me.passo], amiga = PERGUNTA_AMIGA[q.id] || [q.pergunta, ""], marcado = me.r[q.id];
      var comAmostra = q.opcoes.some(function (o) { return amostraEstilo(q.id, o.id); });
      return volta + '<section class="me-pergunta" aria-labelledby="me-titulo">' + progressoEstilo(me.passo, qs.length) +
        '<h1 class="titulo" id="me-titulo">' + esc(amiga[0]) + "</h1>" + (amiga[1] ? '<p class="lead">' + esc(amiga[1]) + "</p>" : "") +
        '<div class="me-opcoes' + (comAmostra ? " com-amostra" : "") + '" role="radiogroup" aria-labelledby="me-titulo" data-tour="me-opcoes">' + q.opcoes.map(function (o) {
          var m = marcado === o.id;
          return '<button type="button" class="me-opcao" role="radio" aria-checked="' + m + '" aria-pressed="' + m + '" data-acao="me-responder" data-q="' + esc(q.id) + '" data-o="' + esc(o.id) + '">' +
            amostraEstilo(q.id, o.id) + '<span class="texto"><strong>' + esc(rotuloEstilo(q.id, o.id)) + "</strong><small>" + esc(o.texto) + "</small></span>" + (m ? '<span class="marcador">' + icone("certo") + "</span>" : "") + "</button>";
        }).join("") + "</div>" + livreEstilo(q.id, me) +
        '<div class="me-pe"><button type="button" class="discreto" data-acao="me-ir" data-i="' + (me.passo - 1) + '">' + icone("voltar") + "<span>Voltar</span></button>" +
        '<button type="button" class="botao secundario" data-acao="me-responder" data-q="' + esc(q.id) + '" data-o="auto" data-tour="me-nao-sei">' + icone("estrela") + '<span class="rotulo">Não sei, escolhe por mim</span></button></div></section>';
    }
    var sugestao = "Estilo " + ((E.canal || {}).nome || "do canal");
    return volta + '<section class="me-pergunta">' + progressoEstilo(qs.length - 1, qs.length) + '<h1 class="titulo">Que nome você dá pro estilo?</h1><p class="lead">Só pra você reconhecer. Pode deixar o sugerido.</p>' +
      '<div class="campo me-nome"><label for="me-nome">Nome do estilo</label><input class="entrada" type="text" id="me-nome" maxlength="40" value="' + esc(me.nome || sugestao) + '" data-acao-mudar="me-nome" autocomplete="off"></div>' +
      '<div class="me-pe"><button type="button" class="discreto" data-acao="me-ir" data-i="' + (qs.length - 1) + '">' + icone("voltar") + "<span>Voltar</span></button>" +
      botao("Sortear meu estilo", 'data-acao="me-sortear"', "gigante", "estrela") + "</div>" +
      (temLivre() ? '<p class="meta">Você respondeu do seu jeito em alguma pergunta: o kit sorteia com as opções prontas e, na folha, a IA deixa do jeito que você escreveu.</p>' : "") + "</section>";
  };

  /* ------------------------------------------------------------ personagens e cenários */
  var personagemVideo = "";
  function nomeGente(n) { n = String(n || ""); return n.charAt(0).toUpperCase() + n.slice(1); }
  function descricaoCurta(p) {
    var d = String(p.descricao || "Personagem do seu canal.");
    var depois = d.split(":").slice(1).join(":").trim();
    d = (depois || d).replace(/\s*Livre para usar e modificar\.?/i, "").trim();
    return d.charAt(0).toUpperCase() + d.slice(1);
  }
  function figuraPersonagem(p) {
    if (p.previa) return '<img class="figura" src="' + esc(midia(p.previa)) + '" alt="' + esc(nomeGente(p.nome)) + '">';
    if (p.boneco && p.boneco.caixa) {
      var cx = p.boneco.caixa;
      return '<div class="boneco" style="aspect-ratio:' + cx[2] + "/" + cx[3] + '" role="img" aria-label="' + esc(nomeGente(p.nome)) + '">' + p.boneco.camadas.map(function (c) {
        return '<img src="' + esc(midia(c.src)) + '" alt="" loading="lazy" style="left:' + ((c.x - cx[0]) / cx[2] * 100).toFixed(2) + "%;top:" + ((c.y - cx[1]) / cx[3] * 100).toFixed(2) + "%;width:" + (c.w / cx[2] * 100).toFixed(2) + "%;height:" + (c.h / cx[3] * 100).toFixed(2) + '%">';
      }).join("") + "</div>";
    }
    return '<span class="figura-vazia" aria-hidden="true">' + icone("pessoa") + "</span>";
  }
  var NOMES_CENARIO = { cenario3d: "Ruas e casas", interiores: "Dentro de casa", paisagens: "Paisagens" };
  T.personagens = function () {
    var pe = E.personagens || { lista: [] };
    var pedidoNovo = "cria um personagem novo pro meu canal, me mostra a folha de poses antes de animar";
    var cards = pe.lista.map(function (p) {
      var nome = nomeGente(p.nome);
      return '<li class="card-pers"><div class="moldura-pers">' + figuraPersonagem(p) + '<span class="chao" aria-hidden="true"></span></div>' +
        '<h2 class="nome-pers">' + esc(nome) + '</h2><p class="desc-pers" title="' + esc(descricaoCurta(p)) + '">' + esc(descricaoCurta(p)) + "</p>" +
        '<div class="acoes-pers">' + botao("Usar no próximo vídeo", 'data-acao="usar-personagem" data-curto="Usar" data-nome="' + esc(nome) + '"', "secundario", "claquete") +
        botaoCopiar("faz um episódio com o personagem " + nome, "Copiar o pedido", "discreto", "Pedido copiado. Agora cole no chat da IA.") + "</div></li>";
    }).join("");
    var novo = '<li class="card-pers card-novo"><div class="moldura-pers">' + ilustra("tv-apontando", "figura-novo") + '<span class="chao" aria-hidden="true"></span></div>' +
      '<h2 class="nome-pers">Personagem 100% seu</h2><p class="desc-pers">Descreva do seu jeito. A IA desenha e mostra as poses antes de animar.</p>' +
      (ESTATICO ? "" : '<label class="so-leitor" for="pers-livre">Como é o personagem</label><textarea class="entrada pers-livre" id="pers-livre" rows="3" maxlength="400" placeholder="Ex.: uma senhora de 70 anos, baixinha, de óculos redondos e avental, que fala alto e ri de tudo"></textarea>') +
      '<div class="acoes-pers">' + (ESTATICO ? "" : botao(iaPronta() ? "Mandar pra IA criar" : "Pedir personagem novo", 'data-curto="Pedir novo" data-acao="pers-novo" data-texto="' + esc(pedidoNovo) + '" data-tour="pedir"', "", iaPronta() ? "seguir" : "copiar")) + "</div></li>";
    var lugares = '<section class="lugares" data-tour="lugares"><h2 class="bloco-titulo">Lugares</h2><p class="apoio">Os cenários que a IA já desenha. Ela escolhe o que combina com cada cena.</p><ul class="trilho-lugares">' +
      (pe.cenarios || []).map(function (c) {
        var id = String(c.arquivo || "").split("/").pop().replace(/\.py$/, "");
        var frase = String(c.texto || "").split(/[:.]/)[0];
        return '<li class="lugar lugar-' + esc(id) + '"><span class="lugar-quadro" aria-hidden="true">' + icone("casa") + "</span><b>" + esc(NOMES_CENARIO[id] || bonito(id)) + "</b><span>" + esc(frase) + "</span></li>";
      }).join("") + "</ul></section>";
    var exemplos = (pe.exemplos || []).length ? recolhe("Exemplos prontos pra ver funcionando", "Um vídeo de cada tipo, feito pelo kit", '<ul class="lista-simples">' + pe.exemplos.map(function (x) {
      return "<li><span>" + esc(x.texto) + "</span>" + botaoCopiar("roda o exemplo de " + x.pasta + " pra eu ver", "Copiar o pedido", "discreto", "Pedido copiado. Agora cole no chat da IA.") + "</li>";
    }).join("") + "</ul>") : "";
    var ident = pe.identidade_html ? recolhe("O personagem principal do canal", "Como ele é e as regras de desenho", '<div class="md">' + pe.identidade_html + "</div>") : "";
    return voltarLinha("personagens") + cabeca("Personagens e cenários", "Quem está nos seus vídeos e onde a história acontece.") +
      '<ul class="elenco" data-tour="elenco">' + cards + novo + "</ul>" + lugares + exemplos + ident;
  };

  /* ------------------------------------------------------------ ganchos */
  var PERGUNTAS_FIM = ["Qual desses você não conhecia?", "Você faria o mesmo no lugar dele?", "O que você acha que acontece na parte 2?"];
  T.ganchos = function () {
    var g = E.ganchos || {};
    var bib = g.biblioteca || {};
    var chaves = Object.keys(bib);
    var padrao = valor("roteiro", "estilo_padrao");
    var sel = lerLocal("estiloGancho", chaves.indexOf(padrao) >= 0 ? padrao : chaves[0]);
    if (chaves.indexOf(sel) < 0) sel = chaves[0];
    var capa = sel ? capaEstilo(estiloPorId(sel)) : "";
    /* Cada técnica vira os começos de exemplo dela (o texto que aparece na tela); a técnica fica embaixo. */
    var cartoes = [];
    (bib[sel] || []).forEach(function (x) {
      var vs = (x.variacoes || []).length ? x.variacoes : [x.gancho];
      vs.forEach(function (v) { cartoes.push({ gancho: v, tecnica: x.gancho }); });
    });
    cartoes = cartoes.concat((g.meus || []).map(function (x) { return { gancho: x, meu: true }; }));
    var trilho = chaves.length ? '<div class="campo filtro-gancho"><span class="rotulo" id="sel-gancho-rot">Começos que já funcionaram no estilo</span>' +
      suspensa({ id: "sel-gancho", rotuloId: "sel-gancho-rot", acaoMudar: "estilo-gancho", valor: sel, opcoes: chaves.map(function (k) { return [k, nomeEstilo(k), bib[k].length + (bib[k].length === 1 ? " começo" : " começos"), capaEstilo(estiloPorId(k))]; }) }) + "</div>" +
      '<ul class="cartoes-gancho" data-tour="ganchos">' + cartoes.map(function (x) {
        var i = ganchosEscolhidos.indexOf(x.gancho);
        return '<li><button type="button" class="cartao-abertura" aria-pressed="' + (i >= 0) + '" data-acao="gancho-escolher" data-texto="' + esc(x.gancho) + '">' +
          (capa ? '<img src="' + esc(capa) + '" alt="" loading="lazy">' : "") + '<span class="texto-abertura">' + esc(x.gancho) + "</span>" +
          (i >= 0 ? '<span class="letra-duelo">' + (i === 0 ? "A" : "B") + "</span>" : "") + "</button>" +
          (x.tecnica ? '<p class="meta" title="' + esc(x.tecnica) + '">' + esc(x.tecnica) + "</p>" : (x.meu ? '<p class="meta">Um começo seu.</p>' : "")) + "</li>";
      }).join("") + "</ul>"
      : '<div class="plano"><p class="apoio">Os começos prontos chegam numa próxima versão do kit. Enquanto isso, peça no chat: “me dá 3 começos pro próximo vídeo”.</p></div>';
    var a = ganchosEscolhidos[0], b = ganchosEscolhidos[1];
    var duelo = '<section class="plano duelo" data-tour="duelo"><h2 class="bloco-titulo">Teste dois começos</h2>' +
      '<div class="duelo-par"><div class="lado-duelo' + (a ? "" : " vago") + '"><span class="letra-duelo">A</span><p>' + esc(a || "Toque num começo acima") + "</p></div>" +
      '<span class="contra" aria-hidden="true">X</span><div class="lado-duelo' + (b ? "" : " vago") + '"><span class="letra-duelo">B</span><p>' + esc(b || "e depois em outro") + "</p></div></div>" +
      '<div class="acoes-linha">' + (ESTATICO ? "" : botao("Testar estes dois", 'data-acao="testar-dois" data-tour="testar"' + (a && b ? "" : " disabled"), "", "seguir")) +
      '<span class="meta">A IA faz duas versões do próximo vídeo, uma com cada começo.</span></div></section>';
    var pergunta = '<section class="pergunta-fim" data-tour="pergunta"><h2 class="bloco-titulo">A pergunta do fim</h2><p class="apoio">Uma pergunta que qualquer um consegue responder faz comentar.</p>' +
      '<div class="respostas" role="radiogroup" aria-label="Pergunta do fim">' + PERGUNTAS_FIM.map(function (q) {
        var m = perguntaFim === q;
        return '<button type="button" class="opcao" role="radio" aria-checked="' + m + '" aria-pressed="' + m + '" data-acao="pergunta-fim" data-texto="' + esc(q) + '"><span class="texto"><strong>' + esc(q) + '</strong></span><span class="marcador">' + (m ? icone("certo") : "") + "</span></button>";
      }).join("") + "</div>" +
      '<div class="campo"><label for="pergunta-minha">Escrever a minha</label><input class="entrada" type="text" id="pergunta-minha" maxlength="140" placeholder="Ex.: Qual você escolheria?" value="' + esc(PERGUNTAS_FIM.indexOf(perguntaFim) < 0 ? perguntaFim : "") + '" data-acao-mudar="pergunta-minha"></div>' +
      botao("Usar no próximo vídeo", 'data-acao="pergunta-copiar"', "secundario", "seguir") + "</section>";
    var conferir = recolhe("Escrever e conferir um começo meu", "O kit confere do mesmo jeito que confere antes de gravar",
      '<form class="form-gancho" data-form="gancho"><div class="campo"><label for="g-fala">Primeira frase da voz</label><textarea class="entrada" rows="2" id="g-fala" name="fala" maxlength="600" placeholder="Ex.: Esse bicho existe e você nunca viu."' + (ESTATICO ? " disabled" : "") + "></textarea></div>" +
      '<div class="campo"><label for="g-tela">Texto grande na tela</label><input class="entrada" type="text" id="g-tela" name="tela" maxlength="200" placeholder="Ex.: VOCÊ NUNCA REPAROU"' + (ESTATICO ? " disabled" : "") + "></div>" +
      '<div class="campo"><label for="g-dur">Em que segundo a frase termina? (pode deixar em branco)</label><input class="entrada curto" type="text" inputmode="decimal" id="g-dur" name="dur_s" maxlength="5" autocomplete="off"' + (ESTATICO ? " disabled" : "") + "></div>" +
      (ESTATICO || g.conferidor === false ? '<p class="meta">O conferidor chega numa próxima versão do kit.</p>' : botao("Conferir o começo", 'data-acao="gancho-conferir"', "secundario", "certo")) +
      '<div class="resultado-teste" aria-live="polite"></div></form>' +
      (g.conferidor !== false ? recolhe("Guardar meus começos", "Os seus entram nas sugestões da IA", formSecao("ganchos", { campos: ["biblioteca_extra"], titulo: false })) : ""));
    var porque = g.engajamento_html || g.ganchos_html ? recolhe("Por que isso funciona", "O método dos começos e das perguntas", '<div class="md">' + (g.engajamento_html || "") + (g.ganchos_html || "") + "</div>") : "";
    return voltarLinha("ganchos") + cabeca("Como o vídeo começa", "Os primeiros 3 segundos decidem se a pessoa fica.") + trilho + '<div class="grade-ganchos">' + duelo + pergunta + "</div>" + conferir + porque;
  };

  /* ------------------------------------------------------------ estudar vídeos (kit/estudo + painel/estudo_painel.py) */
  /* Link do YouTube ou do Instagram, ou o vídeo subido do computador: vira transcrição, raio-x e molde. O molde vai pro
     "Fazer um vídeo" pelo botão "Usar este formato" (só a estrutura; o pedido proíbe copiar frase do vídeo estudado). */
  var ESTUDO = null, estudoVer = {}, estudoNicho = null, estudoBusca = null, estudoUrl = "", estudoTermo = "";
  var estudoCurtos = lerLocal("estudoCurtos", true), estudoSel = lerLocal("estudoSel", []), estudoMarcados = [];
  var estudoEsperando = false, estudoTimer = null, estudoEnvio = null, estudoBuscando = false;
  var moldeVideo = lerLocal("moldeVideo", null);
  var NOME_PLATAFORMA = { youtube: "YouTube", instagram: "Instagram", tiktok: "TikTok", local: "Arquivo do computador", outro: "Link" };
  var NOME_FUNCAO = { gancho: "Gancho", contexto: "Contexto", desenvolvimento: "Desenvolvimento", virada: "Virada", lista: "Item da lista", pergunta: "Pergunta", chamada: "Chamada", pergunta_final: "Pergunta do fim", desfecho: "Desfecho" };
  function numCurto(n) {
    if (n == null || n === "") return "–";
    n = Number(n);
    if (n >= 1e6) return (Math.round(n / 1e5) / 10).toString().replace(".", ",") + " mi";
    if (n >= 1e3) return Math.round(n / 1e3) + " mil";
    return String(n);
  }
  function br(x, casas) { return x == null ? "–" : (Math.round(x * Math.pow(10, casas || 1)) / Math.pow(10, casas || 1)).toString().replace(".", ","); }
  function carregarEstudo() {
    if (ESTATICO) return Promise.resolve(null);
    return api("GET", "/api/estudo").then(function (r) {
      var antes = ESTUDO && ESTUDO.estado && ESTUDO.estado.rodando;
      ESTUDO = r || { lista: [] };
      var est = ESTUDO.estado || {};
      clearTimeout(estudoTimer);
      if (est.rodando) estudoTimer = setTimeout(function () { if (telaAtual() === "estudar") carregarEstudo().then(redesenharEstudo); }, 1500);
      if (antes && !est.rodando) {
        (est.feitos || []).forEach(function (id) { delete estudoVer[id]; });
        if (estudoEsperando && (est.feitos || []).length === 1 && !(est.erros || []).length) {
          estudoEsperando = false;
          toast("Pronto: o raio-x do vídeo está aqui.");
          location.hash = "#estudar/" + est.feitos[0];
        } else if ((est.feitos || []).length) {
          estudoEsperando = false;
          toast((est.feitos.length === 1 ? "1 vídeo estudado" : est.feitos.length + " vídeos estudados") + ".");
        }
      }
      return ESTUDO;
    });
  }
  function redesenharEstudo() { if (telaAtual() === "estudar" && !editando()) redesenhar(); }
  function pillDado(rotulo, valor) { return '<span class="dado-estudo"><b>' + esc(valor) + "</b>" + esc(rotulo) + "</span>"; }
  T.estudar = function () {
    var sub = subRota();
    if (ESTATICO) return voltarLinha("estudar") + cabeca("Estudar vídeos", "") + vazio(ilustracao("erro", "tv-cade", "vazio-ilustra"), "O estudo de vídeos funciona no computador",
      "", "Abra o painel pelo ícone Temporada Viral no seu computador para estudar vídeos.");
    if (!ESTUDO) { carregarEstudo().then(redesenharEstudo); return voltarLinha("estudar") + cabeca("Estudar vídeos", "") + esqueleto(4); }
    if (!ESTUDO.recursos || ESTUDO.recursos.disponivel === false) return voltarLinha("estudar") + cabeca("Estudar vídeos", "") +
      vazio(ilustracao("erro", "tv-cade", "vazio-ilustra"), "O estudo de vídeos chega com a próxima versão", "", "Atualize o estúdio em Conta e suporte.");
    if (sub === "nicho") return telaNicho();
    if (sub) return telaEstudoVideo(sub);
    return telaEstudos();
  };
  function andamentoEstudo() {
    var est = (ESTUDO && ESTUDO.estado) || {};
    var envio = estudoEnvio ? '<p class="linha-conta">Enviando o vídeo: ' + estudoEnvio.pct + "%</p>" : "";
    var erros = (est.erros || []).map(function (e) {
      return '<div class="erro-estudo">' + icone("aviso") + "<div><b>" + esc(e.entrada ? (e.local ? "O arquivo " : "O vídeo ") + e.entrada.slice(0, 80) : "O estudo") + "</b><p>" + esc(e.msg) + "</p>" +
        (e.bloqueado ? '<p class="apoio">No app, toque nos três pontinhos do vídeo e em Salvar ou Baixar. Depois suba o arquivo aqui:</p>' + botaoSubirVideo("secundario") : "") + "</div></div>";
    }).join("");
    if (!est.rodando && !estudoEnvio && !erros) return "";
    var corpo = est.rodando || estudoEnvio
      ? '<div class="medidor andando" role="progressbar" aria-label="Estudando o vídeo"><i></i></div>' + envio +
        (est.rodando ? '<p class="linha-conta" aria-live="polite"><b>' + esc(est.fase || "Começando") + "…</b>" + (est.atual ? " <span class=\"meta\">" + esc(String(est.atual).slice(0, 90)) + "</span>" : "") + "</p>" +
          (est.na_fila ? '<p class="meta">Mais ' + est.na_fila + (est.na_fila === 1 ? " vídeo" : " vídeos") + " na fila.</p>" : "") +
          '<p class="meta">Pode trocar de tela: o estudo continua.</p>' + botao("Parar", 'data-acao="estudo-parar"', "discreto mini") : "")
      : "";
    return '<section class="plano andamento-estudo" data-tour="estudo-andamento">' + corpo + erros + "</section>";
  }
  function botaoSubirVideo(classe) {
    return '<label class="botao ' + (classe || "secundario") + '" data-tour="estudo-arquivo">' + icone("baixar") + '<span class="rotulo">Subir um vídeo do computador</span>' +
      '<input type="file" class="arquivo-escondido" accept="video/*,audio/*,.mp4,.mov,.m4v,.webm,.mkv,.mp3,.m4a,.wav" data-acao-mudar="estudo-arquivo"></label>';
  }
  function cartaoEstudo(x) {
    var marcado = estudoSel.indexOf(x.id) >= 0;
    var dados = [];
    if (x.primeira_fala_s != null) dados.push(pillDado("até a 1ª fala", br(x.primeira_fala_s) + " s"));
    if (x.viradas_por_min != null) dados.push(pillDado("viradas por min", br(x.viradas_por_min)));
    if (x.palavras_por_min) dados.push(pillDado("palavras por min", Math.round(x.palavras_por_min)));
    return '<li class="cartao-estudo' + (marcado ? " marcado" : "") + '"><a class="cartao-estudo-link" href="#estudar/' + esc(x.id) + '">' +
      '<span class="plataforma-estudo">' + esc(NOME_PLATAFORMA[x.plataforma] || "Vídeo") + (x.duracao_s ? " · " + fmtSeg(x.duracao_s) : "") + (x.views ? " · " + numCurto(x.views) + " views" : "") + "</span>" +
      "<strong>" + esc(x.titulo || x.id) + "</strong>" + (x.autor ? '<span class="meta">' + esc(x.autor) + "</span>" : "") +
      '<span class="dados-estudo">' + dados.join("") + "</span></a>" +
      '<button type="button" class="marcar-estudo" data-acao="estudo-marcar" data-id="' + esc(x.id) + '" aria-pressed="' + marcado + '">' + (marcado ? icone("certo") : "") + "<span>Comparar</span></button></li>";
  }
  function telaEstudos() {
    var lista = ESTUDO.lista || [], est = ESTUDO.estado || {}, min = ESTUDO.min_nicho || 3;
    var nSel = estudoSel.filter(function (id) { return lista.some(function (x) { return x.id === id; }); }).length;
    var ocupado = !!(est.rodando || estudoEnvio);
    var entrada = '<section class="plano entrada-estudo" data-tour="estudo-link"><h2 class="bloco-titulo"><span class="n">1</span><label for="estudo-url">Cole o link do vídeo</label></h2>' +
      '<div class="linha-link"><input class="entrada" type="url" id="estudo-url" inputmode="url" autocomplete="off" spellcheck="false" maxlength="2000" placeholder="https://www.youtube.com/shorts/…" value="' + esc(estudoUrl) + '" data-acao-mudar="estudo-url">' +
      botao("Estudar este vídeo", 'data-acao="estudo-link"', "", "lupa") + "</div>" +
      '<p class="ajuda">YouTube funciona direto. O Instagram e o TikTok às vezes não deixam baixar sem login: aí baixe o vídeo pelo app e suba o arquivo. O estudo nunca usa a sua conta.</p>' +
      '<div class="ou-estudo"><span>ou</span></div>' + botaoSubirVideo("secundario") + "</section>";
    var itensBusca = (estudoBusca || []).map(function (v, i) {
      var m = estudoMarcados.indexOf(i) >= 0;
      return '<li><button type="button" class="opcao busca-item" role="checkbox" aria-checked="' + m + '" aria-pressed="' + m + '" data-acao="estudo-busca-marcar" data-i="' + i + '">' +
        '<span class="texto"><strong>' + esc(v.titulo || v.link) + "</strong><small>" + esc([v.autor, v.duracao_s ? fmtSeg(v.duracao_s) : "", v.views ? numCurto(v.views) + " views" : ""].filter(Boolean).join(" · ")) + "</small></span>" +
        '<span class="marcador">' + (m ? icone("certo") : "") + "</span></button></li>";
    }).join("");
    var busca = '<section class="plano busca-estudo" data-tour="estudo-buscar"><h2 class="bloco-titulo"><span class="n">2</span><label for="estudo-termo">Ache vídeos do seu nicho</label></h2>' +
      '<p class="apoio">Escreva o assunto e o painel traz vídeos do YouTube sobre ele. Marque os que você quer estudar.</p>' +
      '<div class="linha-link"><input class="entrada" type="text" id="estudo-termo" maxlength="120" placeholder="Ex.: curiosidades de bichos" value="' + esc(estudoTermo) + '" data-acao-mudar="estudo-termo">' +
      botao(estudoBuscando ? "Buscando…" : "Buscar no YouTube", 'data-acao="estudo-buscar"' + (estudoBuscando ? " disabled" : ""), "secundario", "lupa") + "</div>" +
      '<label class="caixa-estudo"><input type="checkbox" id="estudo-curtos"' + (estudoCurtos ? " checked" : "") + ' data-acao-mudar="estudo-curtos"><span>Só vídeos curtos (até 4 min)</span></label>' +
      (estudoBusca ? (estudoBusca.length ? '<ul class="lista-busca">' + itensBusca + "</ul>" +
        '<div class="acoes-linha">' + botao("Estudar os marcados" + (estudoMarcados.length ? " (" + estudoMarcados.length + ")" : ""), 'data-acao="estudo-marcados"' + (estudoMarcados.length && !ocupado ? "" : " disabled"), "", "seguir") +
        '<span class="meta">Cada um leva uns segundos.</span></div>' : '<p class="meta">Nada achado. Tente outras palavras.</p>') : "") + "</section>";
    var cartoes = lista.length ? '<ul class="lista-estudos">' + lista.map(cartaoEstudo).join("") + "</ul>"
      : vazio(ilustracao("metricas", "tv-notebook", "vazio-ilustra"), "Nenhum vídeo estudado ainda", "", "Cole um link acima. Em segundos aparece como o vídeo foi montado.");
    var comparar = lista.length ? '<div class="acoes-linha comparar-estudos" data-tour="estudo-comparar">' +
      botao("Comparar os marcados" + (nSel ? " (" + nSel + ")" : ""), 'data-acao="estudo-comparar"' + (nSel >= min ? "" : " disabled"), nSel >= min ? "" : "secundario", "grafico") +
      '<span class="meta">' + (nSel >= min ? "Mostra o que se repete entre eles." : "Marque " + min + " ou mais vídeos do mesmo nicho para ver o padrão. Um vídeo só não mostra padrão.") + "</span></div>" : "";
    return voltarLinha("estudar") + cabeca("Estudar vídeos", "Veja como um vídeo que deu certo foi montado: o começo, as viradas, o ritmo e a fórmula pra você usar no seu.") +
      andamentoEstudo() + '<div class="grade-estudo">' + entrada + busca + "</div>" +
      '<section class="estudos-salvos" data-tour="estudo-lista"><h2 class="bloco-titulo"><span class="n">3</span>Seus estudos</h2>' + cartoes + comparar + "</section>";
  }
  function linhaDoTempo(r) {
    var dur = r.duracao_s || 1, pc = function (t) { return Math.max(0, Math.min(100, 100 * t / dur)).toFixed(2) + "%"; };
    var g = r.gancho || {}, marcas = "";
    if (g.primeira_fala_s != null) marcas += '<span class="zona-gancho" style="left:' + pc(g.primeira_fala_s) + ";width:" + pc(Math.min(3, dur)) + '" title="Gancho"></span>';
    (r.viradas.buracos || []).forEach(function (b) { marcas += '<span class="zona-buraco" style="left:' + pc(b.de) + ";width:" + pc(b.dur) + '" title="' + esc(br(b.dur, 0)) + ' s sem virada"></span>'; });
    (r.viradas.lista || []).forEach(function (v) { marcas += '<span class="ponto-virada" style="left:' + pc(v.t) + '" title="' + esc(fmtSeg(v.t) + " · " + v.marcador) + '"></span>'; });
    (r.perguntas || []).forEach(function (p) { marcas += '<span class="ponto-pergunta" style="left:' + pc(p.t) + '" title="' + esc(fmtSeg(p.t)) + ' · pergunta"></span>'; });
    (r.cta || []).forEach(function (c) { marcas += '<span class="ponto-chamada" style="left:' + pc(c.t) + '" title="' + esc(fmtSeg(c.t) + " · " + c.tipo) + '"></span>'; });
    var blocos = (r.blocos || []).map(function (b) {
      return '<span class="seg-bloco f-' + esc(b.funcao) + '" style="left:' + b.ini_pct + "%;width:" + Math.max(1, b.fim_pct - b.ini_pct) + '%" title="' + esc(fmtSeg(b.ini_s) + " " + (NOME_FUNCAO[b.funcao] || b.funcao)) + '"></span>';
    }).join("");
    return '<div class="tempo-estudo" role="img" aria-label="Linha do tempo do vídeo: ' + (r.viradas.lista || []).length + " viradas, " + (r.perguntas || []).length + " perguntas, " + (r.cta || []).length + ' chamadas">' +
      '<div class="trilho-tempo">' + marcas + "</div>" + '<div class="trilho-blocos">' + blocos + "</div>" +
      '<div class="escala-tempo"><span>0:00</span><span>' + fmtSeg(dur / 2) + "</span><span>" + fmtSeg(dur) + "</span></div></div>" +
      '<ul class="legenda-tempo"><li><i class="ponto-virada"></i>Virada</li><li><i class="ponto-pergunta"></i>Pergunta</li><li><i class="ponto-chamada"></i>Chamada</li><li><i class="zona-buraco"></i>Mais de 15 s sem virada</li></ul>';
  }
  function moldeHtml(m, rotuloBotao, acao) {
    if (!m) return "";
    return '<ol class="passos-molde">' + m.passos.map(function (p) {
      return '<li class="f-' + esc(p.funcao) + '"><span class="tempo-molde">' + fmtSeg(p.ini_s) + "–" + fmtSeg(p.fim_s) + "</span><div><b>" + esc(p.rotulo) + "</b><p>" + esc(p.instrucao) + "</p></div></li>";
    }).join("") + "</ol>" +
      '<ul class="regras-molde">' + m.regras.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul>" +
      '<div class="acoes-linha" data-tour="estudo-usar">' + botao(rotuloBotao || "Usar este formato", 'data-acao="' + acao + '"', "gigante", "seguir") +
      '<p class="apoio">Leva só a estrutura pro “Fazer um vídeo”. A IA escreve um roteiro novo, com as suas palavras, sem copiar nada do vídeo.</p></div>';
  }
  function telaEstudoVideo(id) {
    var voltar = '<div class="voltar-linha">' + link("Estudar vídeos", "#estudar", "discreto claro sem-linha voltar", "voltar") +
      '<span class="voltar-direita"><button type="button" class="discreto mini" data-acao="tour">Me mostra como usa</button></span></div>';
    var v = estudoVer[id];
    if (!v) {
      api("GET", "/api/estudo/ver?id=" + encodeURIComponent(id)).then(function (r) { estudoVer[id] = r; redesenharEstudo(); });
      return voltar + esqueleto(5);
    }
    if (!v.ok) return voltar + vazio(ilustracao("erro", "tv-cade", "vazio-ilustra"), v.msg || "Esse estudo não existe mais.", link("Ver os estudos", "#estudar", "botao secundario"));
    var e = v.estudo, r = e.raiox || {}, m = e.metadados || {}, s = v.resumo || {};
    var metaLinha = [NOME_PLATAFORMA[e.plataforma] || "Vídeo", s.autor, r.duracao_s ? fmtSeg(r.duracao_s) : "", r.formato, m.view_count ? numCurto(m.view_count) + " views" : "", m.like_count ? numCurto(m.like_count) + " likes" : ""].filter(Boolean).join(" · ");
    var como = { legenda_auto: "pela legenda automática do YouTube", legenda_manual: "pela legenda do YouTube", whisper: "ouvindo o vídeo" }[e.metodo] || "";
    var cab = cabeca(esc(s.titulo || id), esc(metaLinha) + (m.webpage_url ? ' · <a class="discreto" href="' + esc(m.webpage_url) + '" target="_blank" rel="noopener noreferrer">abrir o vídeo</a>' : ""));
    if (r.sem_fala) return voltar + cab + vazio(ilustracao("erro", "tv-cade", "vazio-ilustra"), "Esse vídeo não tem fala", "", "O raio-x olha o que é dito. Num vídeo só com música e imagem, não há o que medir.");
    var g = r.gancho || {};
    var gancho = '<section class="plano cartao-raiox" data-tour="estudo-gancho"><h2 class="bloco-titulo">O gancho</h2>' +
      '<p class="numero-grande">' + br(g.primeira_fala_s) + ' s</p><p class="meta">até a primeira palavra' + (g.primeira_fala_s > 1.5 ? ": antes disso, só imagem" : "") + "</p>" +
      (g.tipo === "muda" ? "<p>Abre <b>só com imagem</b>: a voz entra depois.</p>" : "<p>Abre com <b>" + esc(g.tipo_nome || "") + "</b>.</p>") +
      '<p class="rotulo-pequeno">' + (g.tipo === "muda" ? "Quando a voz entra, nos 3 primeiros segundos ela diz:" : "Nos 3 primeiros segundos o vídeo diz:") + '</p><blockquote class="fala-estudo">' + esc(g.abertura_3s || "") + "</blockquote></section>";
    var ritmo = '<section class="plano cartao-raiox" data-tour="estudo-ritmo"><h2 class="bloco-titulo">O ritmo</h2><div class="dados-estudo grandes">' +
      pillDado("viradas por minuto", br(r.viradas.por_min)) + pillDado("palavras por minuto", Math.round(r.palavras_por_min)) +
      pillDado(r.perguntas.length === 1 ? "pergunta" : "perguntas", r.perguntas.length) + pillDado(r.cta.length === 1 ? "chamada" : "chamadas", r.cta.length) + "</div>" +
      '<p class="meta">Transcrito ' + esc(como) + ". As contas são de palavras: servem pra comparar vídeos, não são nota.</p></section>";
    var bur = (r.viradas.buracos || []).length ? '<p class="aviso-buraco">' + icone("aviso") + "<span>" + r.viradas.buracos.map(function (b) { return "De " + fmtSeg(b.de) + " a " + fmtSeg(b.ate) + " (" + br(b.dur, 0) + " s)"; }).join("; ") +
      " sem virada. Trecho longo sem virada é onde a pessoa costuma sair.</span></p>" : '<p class="meta">Nenhum trecho passa de 15 s sem virada.</p>';
    var momentos = r.perguntas.map(function (p) { return { t: p.t, tipo: "Pergunta" + (p.provavel ? " (provável)" : ""), texto: p.texto }; })
      .concat(r.cta.map(function (c) { return { t: c.t, tipo: "Chamada: " + c.tipo, texto: c.texto }; })).sort(function (a, b) { return a.t - b.t; });
    var tempo = '<section class="plano raiox-tempo" data-tour="estudo-tempo"><h2 class="bloco-titulo">Onde cada coisa acontece</h2>' + linhaDoTempo(r) + bur +
      (momentos.length ? '<ul class="momentos">' + momentos.map(function (x) { return '<li><span class="tempo-molde">' + fmtSeg(x.t) + "</span><div><b>" + esc(x.tipo) + "</b><p>" + esc(x.texto.slice(0, 160)) + "</p></div></li>"; }).join("") + "</ul>" : "") + "</section>";
    var blocos = '<section class="plano" data-tour="estudo-blocos"><h2 class="bloco-titulo">Como ele é dividido</h2><ol class="passos-molde blocos-video">' + (r.blocos || []).map(function (b) {
      return '<li class="f-' + esc(b.funcao) + '"><span class="tempo-molde">' + fmtSeg(b.ini_s) + "–" + fmtSeg(b.fim_s) + "</span><div><b>" + esc(NOME_FUNCAO[b.funcao] || b.funcao) + '</b> <span class="meta">' + b.frases + (b.frases === 1 ? " frase" : " frases") + "</span><p>" + esc(String(b.texto || "").slice(0, 180)) + (String(b.texto || "").length > 180 ? "…" : "") + "</p></div></li>";
    }).join("") + "</ol></section>";
    var formula = e.molde ? '<section class="plano formula" data-tour="estudo-formula"><h2 class="bloco-titulo">A fórmula</h2><p class="esqueleto-molde">' + esc(e.molde.esqueleto) + "</p>" +
      moldeHtml(e.molde, "Usar este formato", "estudo-usar") + "</section>" : "";
    var transcricao = recolhe("A transcrição", (e.segmentos || []).length + " trechos com o tempo de cada um",
      '<ol class="transcricao">' + (e.segmentos || []).map(function (sg) { return '<li><span class="tempo-molde">' + fmtSeg(sg.ini) + "</span>" + esc(sg.texto) + "</li>"; }).join("") + "</ol>" +
      '<div class="acoes-linha">' + botao("Copiar a transcrição", 'data-acao="estudo-copiar"', "secundario", "copiar") + "</div>", ' data-tour="estudo-transcricao"');
    return voltar + cab + '<div class="grade-raiox">' + gancho + ritmo + "</div>" + tempo + formula + blocos + transcricao +
      '<div class="acoes-linha">' + botao("Apagar este estudo", 'data-acao="estudo-apagar" data-id="' + esc(id) + '"', "discreto mini") + "</div>";
  }
  function telaNicho() {
    var voltar = '<div class="voltar-linha">' + link("Estudar vídeos", "#estudar", "discreto claro sem-linha voltar", "voltar") +
      '<span class="voltar-direita"><button type="button" class="discreto mini" data-acao="tour">Me mostra como usa</button></span></div>';
    if (!estudoNicho) {
      api("POST", "/api/estudo/nicho", { ids: estudoSel }).then(function (r) { estudoNicho = r || { ok: false }; redesenharEstudo(); });
      return voltar + esqueleto(5);
    }
    var r = estudoNicho;
    if (!r.ok) return voltar + vazio(ilustracao("metricas", "tv-notebook", "vazio-ilustra"), "Ainda não dá pra ver o padrão", link("Escolher os vídeos", "#estudar", "botao secundario"), r.msg);
    var linhas = r.linhas.map(function (x) {
      return '<tr><th scope="row"><a href="#estudar/' + esc(x.id) + '">' + esc(String(x.titulo || x.id).slice(0, 60)) + "</a></th><td>" + numCurto(x.views) + "</td><td>" + numCurto(x.likes) + "</td><td>" + (x.duracao_s ? fmtSeg(x.duracao_s) : "–") +
        "</td><td>" + br(x.primeira_fala_s) + " s</td><td>" + esc(({ pergunta: "pergunta", negacao: "negação", numero: "número", voce: "fala com você", afirmacao: "afirmação", muda: "só imagem" })[x.tipo_gancho] || "–") +
        "</td><td>" + br(x.viradas_por_min) + "</td><td>" + (x.palavras_por_min ? Math.round(x.palavras_por_min) : "–") + "</td><td>" + esc(x.formato || "–") + "</td></tr>";
    }).join("");
    var tabela = '<section class="plano" data-tour="nicho-tabela"><h2 class="bloco-titulo">Lado a lado</h2><div class="tabela"><table><thead><tr><th scope="col">Vídeo</th><th scope="col">Views</th><th scope="col">Likes</th><th scope="col">Duração</th><th scope="col">1ª fala</th><th scope="col">Abre com</th><th scope="col">Viradas/min</th><th scope="col">Palavras/min</th><th scope="col">Formato</th></tr></thead><tbody>' +
      linhas + "</tbody></table></div></section>";
    var lista = function (t, itens, nota) { return itens.length ? "<h3 class=\"bloco-titulo menor\">" + t + "</h3>" + (nota ? '<p class="meta">' + nota + "</p>" : "") + '<ul class="padroes">' + itens.map(function (p) { return "<li>" + esc(p) + "</li>"; }).join("") + "</ul>" : ""; };
    var padrao = '<section class="plano" data-tour="nicho-padrao"><h2 class="bloco-titulo">O que se repete</h2>' + lista("Nos " + r.n + " vídeos", r.padroes) + lista("O que muda de um pra outro", r.varia) +
      lista("Os mais vistos", r.contraste, "Isso descreve estes vídeos; não é garantia de que funciona igual no seu.") + "</section>";
    var formula = '<section class="plano formula" data-tour="estudo-formula"><h2 class="bloco-titulo">A fórmula do nicho</h2><p class="esqueleto-molde">' + esc(r.molde.esqueleto) + "</p>" + moldeHtml(r.molde, "Usar este formato", "estudo-usar-nicho") + "</section>";
    return voltar + cabeca("O padrão do nicho", r.n + " vídeos comparados. Um padrão só entra aqui quando aparece em pelo menos 6 de cada 10.") + tabela + padrao + formula;
  }
  function enviarVideoEstudo(input) {
    var arq = input.files && input.files[0];
    if (!arq) return;
    if (arq.size > 600 * 1024 * 1024) { toast("Vídeo grande demais: use um de até 600 MB.", "erro"); return; }
    var x = new XMLHttpRequest();
    estudoEnvio = { pct: 0 };
    estudoEsperando = true;
    x.open("POST", "/api/estudo/arquivo?nome=" + encodeURIComponent(arq.name));
    x.setRequestHeader("X-Painel-Token", TOKEN);
    x.setRequestHeader("Content-Type", "application/octet-stream");
    x.upload.onprogress = function (ev) {
      if (!ev.lengthComputable) return;
      estudoEnvio.pct = Math.round(100 * ev.loaded / ev.total);
      var el = main.querySelector(".andamento-estudo .linha-conta"); if (el) el.textContent = "Enviando o vídeo: " + estudoEnvio.pct + "%";
    };
    x.onload = function () {
      estudoEnvio = null;
      var r = {}; try { r = JSON.parse(x.responseText); } catch (e) { r = { ok: false }; }
      if (!r.ok) { estudoEsperando = false; toast(r.msg || "Não consegui receber o vídeo.", "erro"); }
      if (location.hash.indexOf("#estudar") !== 0) location.hash = "#estudar";
      carregarEstudo().then(function () { redesenhar(); });
    };
    x.onerror = function () { estudoEnvio = null; estudoEsperando = false; toast("O envio parou. Tente de novo.", "erro"); redesenhar(); };
    x.send(arq);
    if (location.hash !== "#estudar") location.hash = "#estudar"; else redesenhar();
  }
  function comecarEstudo(urls) {
    estudoEsperando = urls.length === 1;
    return api("POST", "/api/estudo/comecar", { urls: urls }).then(function (r) {
      if (!r.ok) { estudoEsperando = false; toast(r.msg || "Não consegui começar.", "erro"); return; }
      return carregarEstudo().then(function () { redesenhar(); });
    });
  }
  function usarMolde(titulo, curto, arquivo) {
    moldeVideo = { titulo: String(titulo || "vídeo estudado").slice(0, 80), curto: curto, arquivo: arquivo };
    gravarLocal("moldeVideo", moldeVideo);
    location.hash = "#fazer";
    toast("Pronto: o pedido do vídeo vai com esse formato.");
  }
  var ACOES_ESTUDO = {
    "estudo-link": function () {
      var u = (document.getElementById("estudo-url") || {}).value || estudoUrl;
      u = String(u).trim();
      if (!/^https?:\/\/\S+$/.test(u)) { toast("Cole o link inteiro do vídeo, começando com https://.", "aviso"); var c = document.getElementById("estudo-url"); if (c) c.focus(); return; }
      estudoUrl = "";
      comecarEstudo([u]);
    },
    "estudo-parar": function () { estudoEsperando = false; api("POST", "/api/estudo/parar", {}).then(function () { carregarEstudo().then(redesenhar); }); },
    "estudo-buscar": function (b) {
      var t = String((document.getElementById("estudo-termo") || {}).value || estudoTermo).trim();
      if (!t) { toast("Escreva o assunto para buscar.", "aviso"); return; }
      estudoTermo = t; estudoBuscando = true; redesenhar('[data-acao="estudo-buscar"]');
      api("POST", "/api/estudo/buscar", { termo: t, curtos: estudoCurtos }).then(function (r) {
        estudoBuscando = false;
        if (r.falta) {
          toast("Preparando o estudo de vídeos (só na primeira vez). Depois busque de novo.");
          api("POST", "/api/estudo/preparar", {}).then(function () { carregarEstudo().then(redesenhar); });
          return;
        }
        if (!r.ok) { toast(r.msg || "A busca não respondeu.", "erro"); redesenhar(); return; }
        estudoBusca = r.itens || []; estudoMarcados = [];
        redesenhar('[data-acao="estudo-buscar"]');
      });
    },
    "estudo-busca-marcar": function (b) {
      var i = Number(b.dataset.i), k = estudoMarcados.indexOf(i);
      if (k >= 0) estudoMarcados.splice(k, 1); else estudoMarcados.push(i);
      redesenhar('[data-acao="estudo-busca-marcar"][data-i="' + i + '"]');
    },
    "estudo-marcados": function () {
      var urls = estudoMarcados.map(function (i) { return (estudoBusca[i] || {}).link; }).filter(Boolean);
      if (!urls.length) return;
      estudoMarcados = []; estudoBusca = null;
      comecarEstudo(urls);
    },
    "estudo-marcar": function (b) {
      var id = b.dataset.id, k = estudoSel.indexOf(id);
      if (k >= 0) estudoSel.splice(k, 1); else estudoSel.push(id);
      gravarLocal("estudoSel", estudoSel); estudoNicho = null;
      redesenhar('[data-acao="estudo-marcar"][data-id="' + id + '"]');
    },
    "estudo-comparar": function () { estudoNicho = null; location.hash = "#estudar/nicho"; },
    "estudo-usar": function () {
      var id = subRota(), v = estudoVer[id];
      if (!v || !v.ok) return;
      usarMolde((v.resumo || {}).titulo, v.molde_curto, v.molde_arquivo);
    },
    "estudo-usar-nicho": function () {
      if (!estudoNicho || !estudoNicho.ok) return;
      usarMolde("nicho com " + estudoNicho.n + " vídeos", estudoNicho.molde_curto, estudoNicho.molde_arquivo);
    },
    "estudo-copiar": function (b) {
      var v = estudoVer[subRota()];
      if (!v || !v.ok) return;
      copiar((v.estudo.segmentos || []).map(function (s) { return "[" + fmtSeg(s.ini) + "] " + s.texto; }).join("\n"), b, "Transcrição copiada.");
    },
    "estudo-apagar": function (b) {
      var id = b.dataset.id;
      abrirJanela("Apagar este estudo?", "<p>O raio-x e a transcrição deste vídeo saem do seu computador. Dá pra estudar de novo depois pelo link.</p>",
        botao("Apagar", 'data-acao="estudo-apagar-ok" data-id="' + esc(id) + '"', "", "fechar") + botao("Cancelar", 'data-acao="fechar-janela"', "secundario"));
    },
    "estudo-apagar-ok": function (b) {
      var id = b.dataset.id;
      api("POST", "/api/estudo/apagar", { id: id }).then(function () {
        fecharJanela(); delete estudoVer[id];
        estudoSel = estudoSel.filter(function (x) { return x !== id; }); gravarLocal("estudoSel", estudoSel); estudoNicho = null;
        toast("Estudo apagado.");
        carregarEstudo().then(function () { location.hash = "#estudar"; redesenhar(); });
      });
    },
    "tirar-molde": function () { moldeVideo = null; gravarLocal("moldeVideo", null); redesenhar("#assunto-video"); }
  };
  document.addEventListener("input", function (ev) {
    var a = ev.target.dataset && ev.target.dataset.acaoMudar;
    if (a === "estudo-url") estudoUrl = ev.target.value;
    if (a === "estudo-termo") estudoTermo = ev.target.value;
  });
  document.addEventListener("change", function (ev) {
    var a = ev.target.dataset && ev.target.dataset.acaoMudar;
    if (a === "estudo-curtos") { estudoCurtos = ev.target.checked; gravarLocal("estudoCurtos", estudoCurtos); }
    if (a === "estudo-arquivo" && !ESTATICO) enviarVideoEstudo(ev.target);
  });
  /* Ao entrar na tela (ou trocar de estudo), pega a fila e a lista de novo: o estudo pode ter terminado em outra tela. */
  window.addEventListener("hashchange", function () { if (ESTUDO && telaAtual() === "estudar") carregarEstudo().then(redesenharEstudo); });
  document.addEventListener("keydown", function (ev) {
    if (ev.key !== "Enter" || !ev.target || !ev.target.id) return;
    if (ev.target.id === "estudo-url") { ev.preventDefault(); ACOES_ESTUDO["estudo-link"](); }
    if (ev.target.id === "estudo-termo") { ev.preventDefault(); ACOES_ESTUDO["estudo-buscar"](); }
  });

  /* ------------------------------------------------------------ métricas */
  function lerNumero(t) {
    t = String(t || "").trim().toLowerCase().replace(/\s+/g, " ");
    if (!t) return null;
    var mil = /mil$/.test(t), mi = /(mi|milh[aõ]o|milh[oõ]es)$/.test(t);
    t = t.replace(/[^\d.,]/g, "");
    if (!t) return null;
    /* 12.480 = doze mil; 32,4 = trinta e dois vírgula quatro; 1,5 mil = mil e quinhentos. */
    if (mil || mi) t = t.replace(/\./g, "").replace(",", ".");
    else t = t.replace(/\.(?=\d{3}(?!\d))/g, "").replace(",", ".");
    var n = Number(t);
    if (isNaN(n)) return null;
    return mil ? n * 1000 : (mi ? n * 1e6 : n);
  }
  function pct(v) { return (Math.round(v * 100) / 100).toString().replace(".", ","); }
  function historicoMetricas() { var mh = E.metricas || {}; return (Array.isArray(mh.historico) ? mh.historico : []).filter(function (h) { return h && typeof h === "object"; }); }
  function numerosDe(h) { return h.numeros && typeof h.numeros === "object" ? h.numeros : h; }
  function estadoEpMetrica(ep, hist, dias) {
    var anot = hist.filter(function (h) { return h.episodio === ep.nome; }).pop();
    if (anot) return ["anotado", "Anotado em " + String(anot.data || "").slice(8, 10) + "/" + String(anot.data || "").slice(5, 7)];
    if (!ep.pronto) return ["fazendo", "Ainda sendo feito"];
    var d = dataDoQuando(ep.quando);
    var passou = d ? Math.floor((Date.now() - d.getTime()) / 864e5) : 99;
    if (passou < dias) { var f = dias - passou; return ["espera", "Pronto " + quandoHumano(ep.quando, true) + " · espere mais " + f + (f === 1 ? " dia" : " dias")]; }
    return ["falta", "Pronto " + quandoHumano(ep.quando, true) + " · falta anotar"];
  }
  var VEREDITO = {
    pulados_pct: [function (v) { return v < 40; }, "pularam no começo", "Bom. Abaixo de 40% quer dizer que o começo prende.", "Alto. Mostre o assunto já no primeiro segundo."],
    comentarios_pct: [function (v) { return v >= 0.5; }, "comentaram", "Bom. A pergunta do fim está funcionando.", "Baixo. Termine com uma pergunta que qualquer um consegue responder."],
    compartilhamentos_pct: [function (v) { return v >= 0.5; }, "compartilharam", "Bom. O vídeo dá vontade de mandar pra alguém.", "Baixo. Puxe pra “manda pra quem…” no meio do vídeo."],
    salvamentos_pct: [function (v) { return v >= 1; }, "salvaram", "Bom. Quem vê quer guardar pra depois.", "Baixo. Dê uma dica que vale guardar."]
  };
  function vereditoHtml(h) {
    if (!h) return '<aside class="plano veredito" data-tour="veredito"><h2 class="bloco-titulo">O que os números dizem</h2>' + ilustracao("metricas", "tv-notebook", "veredito-ilustra") +
      '<p class="apoio">Anote os números do primeiro vídeo e aqui aparece o que está bom e o que mudar no próximo.</p></aside>';
    var n = numerosDe(h);
    var itens = Object.keys(VEREDITO).filter(function (k) { return typeof n[k] === "number"; }).map(function (k) {
      var v = VEREDITO[k], bom = v[0](n[k]);
      return '<li><span class="num ' + (bom ? "bom" : "baixo") + '">' + pct(n[k]) + "%</span><div><b>" + esc(v[1]) + "</b><span>" + esc(bom ? v[2] : v[3]) + "</span></div></li>";
    }).join("");
    var sug = Array.isArray(h.sugestoes) && h.sugestoes.length ? '<h3 class="bloco-titulo menor">O que mudar no próximo</h3><ul class="sugestoes">' + h.sugestoes.map(function (s) { return "<li>" + esc(s) + "</li>"; }).join("") + "</ul>" : "";
    return '<aside class="plano veredito" data-tour="veredito"><h2 class="bloco-titulo">O que os números dizem</h2><p class="meta">' + esc(bonito(h.episodio)) + " · " + esc(nomeRede(h.rede || "")) +
      (h.data ? " · anotado em " + esc(String(h.data).slice(8, 10) + "/" + String(h.data).slice(5, 7)) : "") + "</p>" + (itens ? "<ul>" + itens + "</ul>" : "") + sug + "</aside>";
  }
  T.metricas = function () {
    var eps = E.episodios || [];
    var mh = E.metricas || { disponivel: false };
    var dias = Number(valor("metricas", "dias_para_medir")) || 2;
    var hist = historicoMetricas();
    var redes = valor("redes", "escolhidas") || ["instagram"];
    if (!redeMetricas || redes.indexOf(redeMetricas) < 0) redeMetricas = redes.indexOf(valor("metricas", "rede_principal")) >= 0 ? valor("metricas", "rede_principal") : redes[0];
    var ordem = { falta: 0, espera: 1, anotado: 2, fazendo: 3 };
    var opcoes = eps.map(function (ep) { var st = estadoEpMetrica(ep, hist, dias); return { ep: ep, st: st }; })
      .sort(function (a, b) { return ordem[a.st[0]] - ordem[b.st[0]]; });
    if (!epMetricas || !eps.some(function (x) { return x.nome === epMetricas; })) epMetricas = opcoes.length ? opcoes[0].ep.nome : "";
    var campoNum = function (c) {
      var inteiro = ["views", "comentarios", "compartilhamentos", "salvamentos", "curtidas"].indexOf(c[0]) >= 0;
      return '<div class="campo"><label for="m-' + c[0] + '">' + esc(c[1]) + '</label><input class="entrada numero" type="text" inputmode="' + (inteiro ? "numeric" : "decimal") + '" id="m-' + c[0] + '" data-num="' + c[0] + '" autocomplete="off" aria-describedby="m-' + c[0] + '-aj"' + (ESTATICO || !eps.length ? " disabled" : "") + '><p class="ajuda" id="m-' + c[0] + '-aj">' + esc(c[2]) + "</p></div>";
    };
    var principais = ["views", "pulados_pct", "comentarios"];
    var form = '<form class="form-metricas" data-form="metricas"><div class="escolher"><div class="campo" data-tour="qual-video"><span class="rotulo" id="m-ep-rot">Qual vídeo?</span>' +
      (eps.length ? suspensa({ id: "m-ep", nome: "episodio", rotuloId: "m-ep-rot", acaoMudar: "metrica-ep", valor: epMetricas, dis: ESTATICO,
        opcoes: opcoes.map(function (o) { var c = capaEp(o.ep); return [o.ep.nome, bonito(o.ep.nome), o.st[1], c ? midia(c) : ""]; }) })
        : '<p class="apoio">Nenhum vídeo ainda. Quando a IA fizer o primeiro, ele aparece aqui.</p>') + "</div>" +
      '<div class="campo"><span class="rotulo" id="m-rede-rot">Onde?</span><div class="segmentos" role="radiogroup" aria-labelledby="m-rede-rot">' + redes.map(function (r) {
        var m = r === redeMetricas;
        return '<button type="button" role="radio" aria-checked="' + m + '" aria-pressed="' + m + '" data-acao="metrica-rede" data-rede="' + r + '">' + (m ? selo(r, true) : "") + "<span>" + esc(r === "youtube_shorts" ? "Shorts" : nomeRede(r)) + "</span></button>";
      }).join("") + "</div></div></div>" +
      '<div class="numeros" data-tour="numeros">' + CAMPOS_METRICAS.filter(function (c) { return principais.indexOf(c[0]) >= 0; }).map(campoNum).join("") + "</div>" +
      recolhe("Mais números", "Compartilhamentos, salvamentos, tempo assistido. Opcional.", '<div class="numeros">' + CAMPOS_METRICAS.filter(function (c) { return principais.indexOf(c[0]) < 0; }).map(campoNum).join("") + "</div>") +
      '<p class="erro-msg msgs-metricas" role="alert" hidden></p>' +
      (ESTATICO ? "" : botao("Anotar números", 'data-acao="metricas-enviar" data-tour="anotar"' + (eps.length && mh.disponivel !== false ? "" : " disabled"), "gigante enviar")) +
      (mh.disponivel === false ? '<p class="meta">O registro de números chega numa próxima versão do kit. Por enquanto, mande os números no chat da IA.</p>' : "") + "</form>";
    var tabela = "";
    if (hist.length) {
      var cols = ["views", "pulados_pct", "comentarios_pct", "compartilhamentos_pct", "salvamentos_pct", "tempo_medio_s"];
      tabela = recolhe("Todos os números anotados", hist.length + (hist.length === 1 ? " anotação" : " anotações"), '<div class="tabela"><table><thead><tr><th scope="col">Data</th><th scope="col">Vídeo</th><th scope="col">Rede</th>' +
        cols.map(function (c) { return '<th scope="col">' + esc(ROTULO_METRICA[c]) + "</th>"; }).join("") + "</tr></thead><tbody>" +
        hist.slice(-60).reverse().map(function (h) {
          var n = numerosDe(h);
          return "<tr><td>" + esc(String(h.data || "").slice(0, 10).split("-").reverse().join("/")) + "</td><td>" + esc(bonito(h.episodio)) + "</td><td>" + esc(nomeRede(h.rede || "")) + "</td>" +
            cols.map(function (c) { var v = n[c]; return "<td>" + (typeof v === "number" ? esc(c === "views" ? num1(v) : pct(v) + (/_pct$/.test(c) ? "%" : "")) : "") + "</td>"; }).join("") + "</tr>";
        }).join("") + "</tbody></table></div>");
    }
    return voltarLinha("metricas") + cabeca("Como foi o vídeo?", "Anote " + dias + " dias depois de postar. São só 3 números, a conta é com a gente.") +
      '<div class="grade-metricas">' + form + vereditoHtml(hist[hist.length - 1]) + "</div>" + tabela +
      recolhe("Ajustes dos números", "Rede principal e quantos dias esperar", formSecao("metricas", { titulo: false }));
  };

  /* ------------------------------------------------------------ conquistas (troféus por vídeos e views, kit/conquistas.py) */
  var NIVEL_COR = { bronze: ["#F0A868", "#A85F2C"], prata: ["#EEF4F7", "#8FA4AE"], ouro: ["#FFE27A", "#E0A100"], diamante: ["#B8F6FF", "#2FB8D3"], lendario: ["#FF4F8B", "#FFD23F"] };
  var NIVEL_NOME = { bronze: "Bronze", prata: "Prata", ouro: "Ouro", diamante: "Diamante", lendario: "Lendário" };
  /* Troféu cheio (24x24, regra evenodd: as alças são vazadas). Serve ao SVG da tela e ao desenho do cartão. */
  var TROFEU_D = "M7 3h10v2h3v3a4 4 0 0 1-4 4h-.4A5 5 0 0 1 13 14.9V17h3v4H8v-4h3v-2.1A5 5 0 0 1 8.4 12H8a4 4 0 0 1-4-4V5h3V3zM6 7v1a2 2 0 0 0 1.4 1.9A6 6 0 0 1 7 8V7H6zm11 0v1a6 6 0 0 1-.4 1.9A2 2 0 0 0 18 8V7h-1z";
  var comemorando = false, ultimoCartao = null;
  function conq() { return (E && E.conquistas) || { disponivel: false, lista: [], novas: [] }; }
  function conqPorId(id) { return conq().lista.filter(function (m) { return m.id === id; })[0]; }
  function trofeuSvg(m, classe) {
    var c = NIVEL_COR[m.nivel] || NIVEL_COR.bronze, gid = "g-" + m.id + "-" + (classe || "n");
    var cor = m.ganha ? "url(#" + gid + ")" : "var(--apagado)";
    return '<svg class="trofeu' + (classe ? " " + classe : "") + (m.ganha ? " ganho" : " trancado") + '" viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
      (m.ganha ? '<defs><linearGradient id="' + gid + '" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="' + c[0] + '"/><stop offset="1" stop-color="' + c[1] + '"/></linearGradient></defs>' : "") +
      '<path fill-rule="evenodd" d="' + TROFEU_D + '" fill="' + cor + '"/></svg>';
  }
  function faltaConquista(m) {
    var f = m.meta - m.atual;
    if (m.tipo === "videos") return f === 1 ? "Falta 1 vídeo" : "Faltam " + f + " vídeos";
    if (m.tipo === "publicados") return "Poste um vídeo e anote as views em Métricas";
    return m.atual ? "Seu melhor vídeo: " + num1(m.atual) + " views" : "Anote as views de um vídeo postado";
  }
  function legendaConquista(m) {
    return "🏆 Conquista desbloqueada: " + m.titulo + ". " + m.frase + ".\n\nFeito com @temporadaviral #temporadaviral";
  }
  T.conquistas = function () {
    var q = conq();
    if (!q.disponivel) return voltarLinha("conquistas") + cabeca("Conquistas", "") + vazio(ilustracao("erro", "tv-cade", "vazio-ilustra"), "As conquistas chegam com a atualização do kit", "", "");
    var prox = ["videos", "publicados", "views"].map(function (t) {
      var p = (q.proximas || {})[t]; if (!p) return "";
      var m = conqPorId(p.id), pc = Math.max(3, Math.min(100, Math.round(p.atual / p.meta * 100)));
      return '<div class="prox-conquista">' + trofeuSvg({ id: p.id, nivel: m.nivel, ganha: false }, "mini") + '<div class="prox-texto"><strong>' + esc(p.titulo) + "</strong><small>" + esc(faltaConquista(m)) + "</small>" +
        '<div class="medidor" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="' + pc + '" aria-label="' + esc(p.titulo) + '"><i style="width:' + pc + '%"></i></div></div></div>';
    }).join("");
    var grupo = function (titulo, tipos) {
      return '<h2 class="bloco-titulo">' + titulo + '</h2><ul class="trofeus">' + q.lista.filter(function (m) { return tipos.indexOf(m.tipo) >= 0; }).map(function (m) {
        return '<li class="trofeu-cartao' + (m.ganha ? " ganho n-" + m.nivel : "") + '">' + trofeuSvg(m) + '<span class="nivel">' + esc(NIVEL_NOME[m.nivel]) + " · " + m.pontos + " pontos</span><strong>" + esc(m.titulo) + "</strong>" +
          "<small>" + esc(m.ganha ? m.frase + (m.data ? " · " + String(m.data).slice(0, 10).split("-").reverse().join("/") : "") : faltaConquista(m)) + "</small>" +
          (m.ganha && !ESTATICO ? botao("Compartilhar", 'data-acao="conquista-compartilhar" data-id="' + esc(m.id) + '"', "secundario", "seguir") : "") + "</li>";
      }).join("") + "</ul>";
    };
    return voltarLinha("conquistas") + cabeca("Conquistas", "Cada vídeo feito e cada marco de views vira troféu e pontos. Quanto mais difícil, mais especial.") +
      '<div class="placar-conquistas" data-tour="pontos"><span class="pontos">' + num1(q.pontos) + '</span><span class="rotulo-pontos">pontos</span><small>' + q.ganhas + " de " + q.total + " troféus</small></div>" +
      (prox ? '<section class="plano" data-tour="proxima"><h2 class="bloco-titulo">Os próximos</h2>' + prox + "</section>" : "") +
      '<div data-tour="trofeus">' + grupo("Vídeos feitos", ["videos", "publicados"]) + grupo("Views", ["views"]) + "</div>" +
      '<p class="meta">As views contam pelo número que você anota em ' + link("Métricas", "#metricas", "discreto") + ", no vídeo que você postou. Vale o melhor vídeo numa rede.</p>";
  };

  /* ------------------------------------------------------------ IA de vídeo (chave do próprio usuário) */
  var CONTAS_VIDEO = [
    { id: "FAL_KEY", prov: "fal", nome: "fal.ai", sel: "Recomendado", site: "https://fal.ai/dashboard/keys",
      resumo: "Uma chave só para Seedance, Kling e MiniMax. Paga com cartão, em dólar, só o que usar.",
      passos: ["Entre no fal.ai (pode ser com o Google) e coloque saldo em Billing. US$ 10 já dá para testar.",
        "Abra “Keys”, clique em “Add key”, dê um nome e copie o código. Ele só aparece uma vez."] },
    { id: "HIGGSFIELD_API_KEY", prov: "higgsfield", nome: "Higgsfield", sel: "Mostra o preço exato antes", site: "https://console.higgsfield.ai",
      resumo: "Seedance e Kling. Antes de cada clipe, a conta diz o preço exato. O saldo da API é separado do plano do site.",
      passos: ["Entre no console de API do Higgsfield e coloque saldo (é diferente do plano do site).",
        "Crie uma chave. Ela tem duas partes, o Key ID e o Secret: copie as duas."] }
  ];
  function vidIA() { return (E && E.video_ia) || null; }
  T.videoia = function () {
    var v = vidIA(), ch = E.chaves || {};
    if (!v) return voltarLinha("videoia") + cabeca("IA de vídeo", "") + vazio(ilustracao("erro", "tv-cade", "vazio-ilustra"), "A IA de vídeo chega com a atualização do kit", "", "");
    var algum = CONTAS_VIDEO.some(function (c) { return ch[c.id]; });
    var contas = CONTAS_VIDEO.map(function (c) {
      var tem = !!ch[c.id], fim = chaveSalva[c.id];
      var form = ESTATICO ? '<p class="apoio">Na versão só para ver não dá para salvar. Abra o painel no computador.</p>' :
        '<form class="campo" data-form="chave" data-nome="' + c.id + '"><div class="chave"><label class="so-leitor" for="ch-' + c.id + '">' + (c.prov === "higgsfield" ? "Key ID" : "Chave") + " do " + esc(c.nome) + "</label>" +
        '<input class="entrada" type="password" id="ch-' + c.id + '" name="valor" autocomplete="off" spellcheck="false" autocapitalize="off" placeholder="' + (c.prov === "higgsfield" ? "cole o Key ID" : (tem ? "cole a chave nova aqui" : "cole a chave aqui")) + '">' +
        (c.prov === "higgsfield" ? '<label class="so-leitor" for="ch-' + c.id + '-s">Secret do Higgsfield</label><input class="entrada" type="password" id="ch-' + c.id + '-s" name="segredo" autocomplete="off" spellcheck="false" autocapitalize="off" placeholder="cole o Secret">' : "") +
        botao("Testar e salvar", 'data-acao="chave-enviar"', "secundario") + '</div><p class="ajuda msg-chave" aria-live="polite"></p></form>';
      return '<section class="conectar conta-video"><h2 class="bloco-titulo">' + esc(c.nome) + ' <span class="selo-mini">' + esc(c.sel) + "</span></h2>" +
        "<p>" + esc(c.resumo) + "</p>" +
        (tem ? '<p class="salvo-chave">' + icone("certo") + "Conectado" + (fim ? " (chave termina em …" + esc(fim) + ")" : "") + ". Dá pra trocar abaixo.</p>" : "") +
        "<ol>" + c.passos.map(function (p, n) {
          return '<li><span class="n">' + (n + 1) + "</span><div><p>" + esc(p) + "</p>" + (n === 0 ? '<a class="discreto" href="' + c.site + '" target="_blank" rel="noopener noreferrer">' + icone("abrir") + '<span>Abrir o site</span><span class="so-leitor"> (abre em outra aba)</span></a>' : "") + "</div></li>";
        }).join("") + '<li><span class="n">3</span><div><p>Cole aqui. A gente testa antes de salvar, sem gastar nada.</p>' + form + "</div></li></ol></section>";
    }).join("");
    var linhas = v.modelos.map(function (m) {
      return '<div class="linha" role="row"><div class="quem" role="cell"><span class="icone-voz" style="background:var(--' + (m.fala_pt ? "rosa" : "turquesa") + ')">' + icone("claquete") + "</span><div><b>" + esc(m.nome) + "</b><small>" + esc(m.provedores.map(function (p) { return p === "fal" ? "fal.ai" : "Higgsfield"; }).join(" e ")) + "</small></div></div>" +
        '<div class="preco" role="cell">US$ ' + num1(m.novelinha_60s[0]).replace(".", ",") + " a " + num1(m.novelinha_60s[1]).replace(".", ",") + "<small>por episódio de 30 s, já contando refação</small></div>" +
        '<p class="ganha" role="cell">' + esc(m.faz) + "</p></div>";
    }).join("");
    var pedido = "quero fazer o próximo episódio da minha novelinha de fruta com IA de vídeo. Segue o metodo/video-ia.md: se já tem elenco em canal/novelinha, continua a série de onde parou; se não tem, monta o elenco comigo. Mostra o custo antes de gerar qualquer clipe e só gera com o meu ok";
    var fazer = '<section class="plano" data-tour="fazer"><h2 class="bloco-titulo">Fazer uma novelinha de fruta</h2>' +
      "<p>A IA escreve a história em cenas, cria cada fruta, mostra quanto vai custar e só gera com o seu ok. Depois junta as cenas com legenda.</p>" +
      (ESTATICO ? "" : algum ? botao("Fazer o próximo episódio", 'data-acao="ia-pedir" data-texto="' + esc(pedido) + '"', "", "seguir") : '<p class="apoio">Conecte uma das contas abaixo para começar.</p>') +
      (v.gastos && v.gastos.clipes ? '<p class="meta">Gasto com IA de vídeo este mês: US$ ' + String(v.gastos.mes.toFixed(2)).replace(".", ",") + " (" + v.gastos.clipes + " clipes no total).</p>" : "") + "</section>";
    var avisos = recolhe("Antes de começar", "Custo de verdade, rótulo de IA e o que pode dar errado",
      "<ul>" +
      "<li><b>Quem paga é a sua conta</b>, por segundo de vídeo. O preço da tabela é para 1 minuto pronto; conte o dobro, porque sempre tem cena para refazer.</li>" +
      "<li><b>Marque como IA</b> ao postar (TikTok, Instagram e YouTube pedem). Vídeo de IA sem a marca perde alcance.</li>" +
      "<li><b>Monetização:</b> o YouTube não paga vídeo repetitivo ou genérico. Uma história com gancho e personagem próprio é o que segura.</li>" +
      "<li><b>Nada de nome de programa famoso</b> no título (dá problema de marca) e nada de drama com criança.</li>" +
      "<li>O rosto da fruta pode mudar de uma cena para outra. A IA confere cada clipe e refaz só o que saiu errado, sempre com o seu ok.</li>" +
      "</ul><p class=\"meta\">Preços conferidos em " + esc(v.conferido_em) + ". Eles mudam: o Higgsfield mostra o valor exato antes de cada clipe.</p>");
    return voltarLinha("videoia") + cabeca("IA de vídeo", "Ligue a sua conta de uma IA de vídeo e o estúdio faz novelinhas de fruta e outros vídeos gerados, cena por cena.", ilustracao("voz", "tv-frente", "cabeca-ilustra pequena")) +
      fazer +
      '<div class="comparar tres" role="table" aria-label="Modelos de vídeo" data-tour="modelos"><div class="linha cab" role="row"><span role="columnheader">Modelo</span><span role="columnheader">Quanto custa</span><span role="columnheader">O que faz</span></div>' + linhas + "</div>" +
      '<div class="contas-video" data-tour="contas">' + contas + "</div>" +
      '<p class="seguranca">A chave é como uma senha: fica só neste computador. Nunca cole a chave no chat da IA.</p>' + avisos;
  };
  /* Parabéns: aparece sozinho quando entra troféu novo, sem atrapalhar quem digita, vê o tour ou está numa janela. */
  function agendarComemoracao() { setTimeout(comemorar, 700); }
  function comemorar() {
    var q = conq();
    if (ESTATICO || comemorando || !q.novas || !q.novas.length) return;
    var j = document.getElementById("janela");
    if ((j && j.open) || tourAtivo || editando() || telaAtual() === "arrumar") return;
    var novas = q.novas.map(conqPorId).filter(Boolean).sort(function (a, b) { return b.pontos - a.pontos; });
    if (!novas.length) return;
    var m = novas[0], pts = novas.reduce(function (s, x) { return s + x.pontos; }, 0);
    comemorando = true;
    api("POST", "/api/conquistas/vistas", { ids: q.novas });
    q.novas = [];
    abrirJanela("Parabéns!", '<div class="comemora n-' + m.nivel + '"><span class="brilho" aria-hidden="true"></span>' + trofeuSvg(m, "grande") +
      '<span class="nivel">' + esc(NIVEL_NOME[m.nivel]) + '</span><h2 class="titulo menor">' + esc(m.titulo) + '</h2><p class="lead">' + esc(m.frase) + ".</p>" +
      '<p class="ganhou-pontos">+' + num1(pts) + " pontos</p>" +
      (novas.length > 1 ? '<p class="meta">E mais ' + (novas.length - 1) + (novas.length === 2 ? " troféu" : " troféus") + " na sua estante.</p>" : "") + "</div>",
      botao("Compartilhar", 'data-acao="conquista-compartilhar" data-id="' + esc(m.id) + '"', "", "seguir") + botao("Ver meus troféus", 'data-acao="conquista-ver"', "secundario"), "janela-comemora");
    setTimeout(function () { comemorando = false; }, 1500);
  }
  /* Cartão 1080x1920 (stories e Reels) desenhado no navegador: nada sai do computador até a pessoa postar. */
  function quebrarLinhas(ctx, texto, larg) {
    var linhas = [], atual = "";
    String(texto).split(" ").forEach(function (p) { var t = atual ? atual + " " + p : p; if (ctx.measureText(t).width > larg && atual) { linhas.push(atual); atual = p; } else atual = t; });
    if (atual) linhas.push(atual);
    return linhas;
  }
  function desenharCartao(m) {
    var W = 1080, H = 1920, cv = document.createElement("canvas"); cv.width = W; cv.height = H;
    var ctx = cv.getContext("2d"), c = NIVEL_COR[m.nivel] || NIVEL_COR.bronze, raro = ["diamante", "lendario"].indexOf(m.nivel) >= 0;
    var cx = W / 2, cy = 800;
    ctx.fillStyle = "#08262F"; ctx.fillRect(0, 0, W, H);
    var g = ctx.createRadialGradient(cx, cy, 40, cx, cy, 950); g.addColorStop(0, c[0] + "70"); g.addColorStop(1, "rgba(8,38,47,0)");
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    var raios = { bronze: 12, prata: 16, ouro: 20, diamante: 28, lendario: 36 }[m.nivel] || 12;
    ctx.save(); ctx.translate(cx, cy); ctx.fillStyle = c[0] + (raro ? "26" : "18");
    for (var i = 0; i < raios; i++) { ctx.rotate(Math.PI * 2 / raios); ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(-70, -1500); ctx.lineTo(70, -1500); ctx.closePath(); ctx.fill(); }
    ctx.restore();
    if (raro || m.nivel === "ouro") {
      var semente = 7, rnd = function () { semente = (semente * 9301 + 49297) % 233280; return semente / 233280; };
      for (var k = 0; k < (raro ? 46 : 22); k++) {
        var x = rnd() * W, y = 330 + rnd() * 1000, r = 4 + rnd() * (raro ? 12 : 8);
        ctx.fillStyle = k % 3 ? c[0] : "#FFF4DE"; ctx.beginPath();
        ctx.moveTo(x, y - r * 2); ctx.lineTo(x + r * .5, y - r * .5); ctx.lineTo(x + r * 2, y); ctx.lineTo(x + r * .5, y + r * .5);
        ctx.lineTo(x, y + r * 2); ctx.lineTo(x - r * .5, y + r * .5); ctx.lineTo(x - r * 2, y); ctx.lineTo(x - r * .5, y - r * .5); ctx.closePath(); ctx.fill();
      }
    }
    var escala = 26, lado = 24 * escala;
    ctx.save(); ctx.translate(cx - lado / 2, cy - lado / 2); ctx.scale(escala, escala);
    var p = new Path2D(TROFEU_D), gt = ctx.createLinearGradient(0, 0, 24, 24); gt.addColorStop(0, c[0]); gt.addColorStop(1, c[1]);
    ctx.shadowColor = c[0]; ctx.shadowBlur = 60; ctx.fillStyle = gt; ctx.fill(p, "evenodd");
    ctx.shadowBlur = 0; ctx.lineWidth = .35; ctx.strokeStyle = "#041419"; ctx.stroke(p);
    ctx.restore();
    ctx.textAlign = "center";
    ctx.fillStyle = "#A9CFD3"; ctx.font = '900 46px "Nunito", sans-serif'; ctx.fillText("CONQUISTA DESBLOQUEADA", cx, 250);
    ctx.fillStyle = c[0]; ctx.font = '900 40px "Nunito", sans-serif'; ctx.fillText(NIVEL_NOME[m.nivel].toUpperCase(), cx, 320);
    ctx.fillStyle = "#FFF4DE"; ctx.font = '120px "Luckiest Guy", sans-serif';
    var titulo = quebrarLinhas(ctx, m.titulo, 940), y0 = 1300;
    titulo.forEach(function (l, n) { ctx.fillText(l, cx, y0 + n * 130); });
    ctx.fillStyle = "#A9CFD3"; ctx.font = '800 50px "Nunito", sans-serif';
    var fy = y0 + titulo.length * 130 - 10;
    quebrarLinhas(ctx, m.frase, 900).slice(0, 3).forEach(function (l, n) { ctx.fillText(l, cx, fy + n * 64); });
    ctx.font = '900 46px "Nunito", sans-serif'; var pts = "+" + num1(m.pontos) + " PONTOS", pw = ctx.measureText(pts).width + 72;
    ctx.fillStyle = "#FFD23F"; ctx.beginPath(); ctx.roundRect(cx - pw / 2, 1530, pw, 84, 42); ctx.fill();
    ctx.fillStyle = "#08262F"; ctx.fillText(pts, cx, 1588);
    var arroba = String(valor("canal", "arroba") || "").replace(/^@/, "");
    if (arroba) { ctx.fillStyle = "#FFF4DE"; ctx.font = '900 54px "Nunito", sans-serif'; ctx.fillText("@" + arroba, cx, 1710); }
    ctx.fillStyle = "#FFD23F"; ctx.font = '900 40px "Nunito", sans-serif'; ctx.fillText("feito com @temporadaviral", cx, 1815);
    return cv;
  }
  function compartilharConquista(id) {
    var m = conqPorId(id); if (!m) return;
    var fontes = document.fonts ? Promise.all(['120px "Luckiest Guy"', '900 46px "Nunito"'].map(function (f) { return document.fonts.load(f); })).catch(function () { /* desenha com a letra reserva */ }) : Promise.resolve();
    fontes.then(function () {
      var cv = desenharCartao(m), url = cv.toDataURL("image/png"), nome = "conquista-" + m.id + ".png", leg = legendaConquista(m);
      var podeArquivo = false;
      try { podeArquivo = !!(navigator.canShare && navigator.canShare({ files: [new File([new Blob()], nome, { type: "image/png" })] })); } catch (e) { podeArquivo = false; }
      ultimoCartao = { cv: cv, nome: nome, leg: leg };
      abrirJanela("Compartilhe sua conquista", '<div class="cartao-conquista"><img src="' + url + '" alt="Cartão da conquista ' + esc(m.titulo) + '"></div>' +
        '<p class="apoio">Poste nos stories, no Reels, no TikTok ou onde quiser. A legenda já marca a @temporadaviral.</p><p class="legenda-conquista">' + esc(leg).replace(/\n/g, "<br>") + "</p>",
        (podeArquivo ? botao("Compartilhar", 'data-acao="conquista-enviar"', "", "seguir") : "") +
        '<a class="botao' + (podeArquivo ? " secundario" : "") + '" href="' + url + '" download="' + nome + '">' + icone("baixar") + '<span class="rotulo">Baixar imagem</span></a>' +
        botaoCopiar(leg, "Copiar legenda", "secundario", "Legenda copiada. Cole no post."), "janela-cartao");
    });
  }
  function enviarConquista() {
    var u = ultimoCartao; if (!u) return;
    u.cv.toBlob(function (b) {
      navigator.share({ files: [new File([b], u.nome, { type: "image/png" })], text: u.leg }).catch(function () { /* a pessoa desistiu: nada a fazer */ });
    }, "image/png");
  }

  /* ------------------------------------------------------------ aprender (os guias do kit, dentro do painel) */
  var TUT = E && E.tutoriais ? E.tutoriais.lista : null;
  var tutPromessa = null;
  function guiasVirtuais(lista) {
    var es = (E && E.estilos) || {};
    if (es.como_escolher_html && !lista.some(function (t) { return t.id === "como-escolher"; })) {
      lista.push({ id: "como-escolher", titulo: "Como escolher o estilo", grupo: "Estilos", resumo: "O que cada estilo faz melhor e o que todo estilo tem.",
        texto: (es.como_escolher_html + " " + (es.comum_html || "")).replace(/<[^>]+>/g, " "), html: es.como_escolher_html + (es.comum_html ? "<h2>Todo estilo tem</h2>" + es.comum_html : "") });
    }
    return lista;
  }
  function carregarTutoriais() {
    if (TUT) return Promise.resolve(TUT);
    if (ESTATICO) { TUT = guiasVirtuais([]); return Promise.resolve(TUT); }
    if (!tutPromessa) {
      tutPromessa = fetch("/api/tutoriais", { credentials: "same-origin", headers: { "X-Painel-Token": TOKEN } })
        .then(function (r) { if (r.status === 403) { location.reload(); throw new Error("bloqueado"); } return r.json(); })
        .then(function (j) { TUT = guiasVirtuais((j && j.lista) || []); return TUT; })
        .catch(function () { tutPromessa = null; return []; });
    }
    return tutPromessa;
  }
  function tutorial(id) { return (TUT || []).filter(function (t) { return t.id === id; })[0] || null; }
  /* No modo simples, os guias de instalação técnica (programas, caminhos do Windows) ficam fora da lista. */
  var TECNICO = /python|ffmpeg|caminho comprido|terminal|\bpip\b|winget|prompt de comando/i;
  function guiasVisiveis() { return (TUT || []).filter(function (t) { return !TECNICO.test(t.titulo + " " + t.resumo); }); }
  function guiasTecnicos() { return (TUT || []).filter(function (t) { return TECNICO.test(t.titulo + " " + t.resumo); }); }
  var buscaGuias = "";
  function lidos() { return lerLocal("lidos", []); }
  function resultadosGuias(q) {
    var termo = semAcento(q).trim();
    if (!termo) return "";
    var achados = guiasVisiveis().filter(function (t) { return semAcento(t.titulo + " " + t.resumo + " " + t.texto).indexOf(termo) >= 0; });
    if (!achados.length) return '<p class="apoio vazio-busca">Nada com “' + esc(q) + '”. Tente uma palavra mais curta, como voz, postar ou gancho.</p>';
    return '<p class="meta" role="status">' + achados.length + (achados.length === 1 ? " guia encontrado" : " guias encontrados") + '</p><ul class="lista-titulos">' + achados.map(function (t) {
      return '<li><a href="#aprender/' + esc(t.id) + '"><b>' + esc(t.titulo) + "</b><span>" + esc(t.resumo) + "</span></a></li>";
    }).join("") + "</ul>";
  }
  function sumarioGuia(html) {
    var m, out = [], re = /<h2[^>]*>([\s\S]*?)<\/h2>/g;
    while ((m = re.exec(html))) out.push(m[1].replace(/<[^>]+>/g, "").trim());
    return out;
  }
  T.aprender = function () {
    if (!TUT) {
      carregarTutoriais().then(function () { if (telaAtual() === "aprender") redesenhar(); });
      return voltarLinha("aprender") + cabeca("Aprender", "") + esqueleto(5);
    }
    var id = subRota();
    var t = id ? tutorial(id) : null;
    if (t) {
      var i = TUT.indexOf(t), prox = TUT[i + 1], ant = TUT[i - 1];
      var l = lidos(); if (l.indexOf(t.id) < 0) { l.push(t.id); gravarLocal("lidos", l); }
      var sum = sumarioGuia(t.html || "");
      return '<div class="voltar-linha">' + link("Aprender", "#aprender", "discreto claro sem-linha voltar", "voltar") + "<span></span></div>" +
        '<div class="grade-guia">' + (sum.length > 1 ? '<nav class="sumario" aria-label="Neste guia"><p class="meta">Neste guia</p><ol>' + sum.map(function (s, k) { return '<li><a href="#aprender/' + esc(t.id) + '" data-acao="sumario" data-i="' + k + '">' + esc(s) + "</a></li>"; }).join("") + "</ol></nav>" : "<span></span>") +
        '<article class="guia" aria-labelledby="guia-titulo"><p class="meta">' + esc(t.grupo) + '</p><h1 class="titulo" id="guia-titulo">' + esc(t.titulo) + "</h1>" +
        '<div class="md corpo-guia">' + t.html + "</div>" +
        '<nav class="guia-pe" aria-label="Outros guias">' + (ant ? link(ant.titulo, "#aprender/" + ant.id, "discreto mini", "voltar") : "<span></span>") +
        (prox ? '<a class="botao secundario" href="#aprender/' + esc(prox.id) + '"><span class="rotulo">Próximo guia: ' + esc(prox.titulo) + "</span>" + icone("seguir") + "</a>" : "") + "</nav></article></div>";
    }
    var trilhaIds = ["comece", "primeiro-video", "chaves"].filter(function (x) { return tutorial(x); });
    var l2 = lidos();
    var trilha = '<section class="trilha" data-tour="trilha"><h2 class="bloco-titulo">Comece por estes ' + trilhaIds.length + '</h2><ol class="trilha-lista">' + trilhaIds.map(function (x, k) {
      var g = tutorial(x), lido = l2.indexOf(x) >= 0;
      return '<li><a class="opcao" href="#aprender/' + esc(x) + '"><span class="n">' + (k + 1) + '</span><span class="texto"><strong>' + esc(g.titulo) + "</strong><small>" + esc(g.resumo) + "</small></span>" +
        (lido ? '<span class="lido">' + icone("certo") + "lido</span>" : icone("lado", "seta")) + "</a></li>";
    }).join("") + "</ol></section>";
    var grupos = [], visiveis = guiasVisiveis();
    visiveis.forEach(function (g) { if (grupos.indexOf(g.grupo) < 0) grupos.push(g.grupo); });
    var temas = '<div class="temas">' + grupos.map(function (gr) {
      var doGrupo = visiveis.filter(function (g) { return g.grupo === gr && trilhaIds.indexOf(g.id) < 0; });
      if (!doGrupo.length) return "";
      return '<section class="tema"><h2 class="bloco-titulo">' + esc(gr) + '</h2><ul class="lista-titulos">' + doGrupo.map(function (g) {
        return '<li><a href="#aprender/' + esc(g.id) + '"><b>' + esc(g.titulo) + (l2.indexOf(g.id) >= 0 ? ' <span class="lido">' + icone("certo") + "lido</span>" : "") + "</b><span>" + esc(g.resumo) + "</span></a></li>";
      }).join("") + "</ul></section>";
    }).join("") + "</div>";
    return voltarLinha("aprender") + cabeca("Aprender", "Os guias do kit, em português de gente. Não precisa abrir arquivo nenhum.", ilustracao("aprender", "tv-notebook", "cabeca-ilustra pequena")) +
      '<div class="busca grande" data-tour="busca" role="search">' + icone("lupa") + '<label class="so-leitor" for="busca-guias">O que você quer aprender?</label>' +
      '<input class="entrada" type="search" id="busca-guias" placeholder="O que você quer aprender?" value="' + esc(buscaGuias) + '" data-acao-mudar="busca-guias" enterkeyhint="search" autocomplete="off"></div>' +
      '<div id="resultado-guias" aria-live="polite">' + resultadosGuias(buscaGuias) + "</div>" + trilha + temas + guiasTecnicosHtml(l2);
  };
  /* Guias técnicos (Python, pastas, terminal): fora da lista principal, recolhidos no fim para quem gosta de mexer. */
  function guiasTecnicosHtml(l2) {
    var tec = guiasTecnicos();
    if (!tec.length) return "";
    return recolhe("Guias técnicos", "Para quem gosta de mexer no computador: pastas, programas e comandos", '<ul class="lista-titulos">' + tec.map(function (g) {
      return '<li><a href="#aprender/' + esc(g.id) + '"><b>' + esc(g.titulo) + (l2.indexOf(g.id) >= 0 ? ' <span class="lido">' + icone("certo") + "lido</span>" : "") + "</b><span>" + esc(g.resumo) + "</span></a></li>";
    }).join("") + "</ul>");
  }

  /* ------------------------------------------------------------ ajuda */
  var FAQ_AJUDA = [
    ["O painel diz que falta alguma coisa", "Abra Está tudo certo? e toque no botão de cada item, ou peça tudo de uma vez pra IA.", "link", "Ver o que falta", "#problema"],
    ["Não sei como pedir o vídeo", "Escolha o estilo, escreva o assunto e toque no botão: o pedido vai direto pro chat da IA aqui no painel.", "link", "Fazer um vídeo", "#fazer"],
    FAQ_CURTA[0],
    ["O vídeo não aparece em Meus vídeos", "A IA pode ainda estar fazendo. Peça pra ela conferir e montar o pacote das redes.", "copiar", "Copiar pedido", "o vídeo já terminou? se sim, monta o pacote das redes de novo pro painel"],
    ["Deu erro no chat da IA", "Peça ajuda do seu jeito: ela lê o erro, explica em uma linha e resolve.", "copiar", "Copiar pedido", "deu erro, me ajuda"],
    ["Quero mudar a letra, a voz ou o jeito do vídeo", "Tudo isso fica em Jeito dos vídeos e salva sozinho.", "link", "Abrir Jeito dos vídeos", "#jeito"],
    FAQ_CURTA[2],
    ["O computador ficou lento ou sem espaço", "Peça pra IA apagar os testes velhos e conferir o computador.", "copiar", "Copiar pedido", "o que falta na minha máquina? libera espaço apagando os testes velhos"]
  ];
  T.ajuda = function () {
    var erros = (E.ajuda && E.ajuda.erros) || [];
    var c = E.conta || {}, email = ((c.suporte || {}).email) || "contato@temporadaviral.com";
    var outros = erros.length ? '<section class="grupo"><h2 class="bloco-titulo">Avisos que o kit pode mostrar</h2><div class="perguntas">' + erros.map(function (e) {
      var titulo = e.explica.charAt(0).toUpperCase() + e.explica.slice(1);
      return '<details class="recolhe pergunta-item" data-busca="' + esc(semAcento(e.explica + " " + e.fazer)) + '"><summary><b>' + esc(titulo) + "</b><span></span>" + icone("abaixo") + "</summary>" +
        '<div class="recolhe-corpo"><p>A IA resolve isso pra você.</p>' + botaoCopiar("deu este erro: " + e.explica + ". resolve pra mim", "Copiar pedido", "secundario", "Pedido copiado. Agora cole no chat da IA.") + "</div></details>";
    }).join("") + "</div></section>" : "";
    return voltarLinha("ajuda") + cabeca("Ajuda", "Quase tudo se resolve pedindo no chat da IA, do seu jeito.") +
      '<div class="busca grande" data-tour="busca" role="search">' + icone("lupa") + '<label class="so-leitor" for="busca-ajuda">O que aconteceu?</label>' +
      '<input class="entrada" type="search" id="busca-ajuda" placeholder="O que aconteceu?" data-acao-mudar="busca-ajuda" enterkeyhint="search" autocomplete="off"></div>' +
      '<section class="grupo"><h2 class="bloco-titulo">As perguntas mais comuns</h2>' + faqHtml(FAQ_AJUDA, ' data-tour="perguntas"') + "</section>" + outros +
      '<p class="apoio vazio-busca" id="ajuda-vazio" hidden>Nada com essa palavra. Cole a mensagem inteira no chat da IA: ela resolve.</p>' +
      '<section class="plano nao-achou" data-tour="suporte"><div><h2 class="bloco-titulo">Não achou? Fale com a gente</h2><p class="apoio">Gente de verdade responde. E-mail: ' + esc(email) + "</p></div>" +
      link("Falar com o suporte", "#suporte", "botao secundario", "balao") + "</section>" +
      '<p class="meta sobre">Temporada Viral ' + esc(E.versao || "") + " · o painel roda só neste computador e mostra sozinho o que a IA muda.</p>";
  };

  /* ------------------------------------------------------------ tour guiado (driver.js + tours.js) */
  var TOURS = (window.TOURS_PAINEL && window.TOURS_PAINEL.telas) || {};
  var tourAtivo = null, tourTimer = null;
  var TOUR_SOZINHO = ["inicio", "fazer"];
  function chaveTourBase(tela) { return "tour:" + tela + ":" + (TOURS[tela] ? TOURS[tela].versao : 0); }
  function temTour(tela) { return !!TOURS[tela]; }
  function visivel(el) {
    if (!el || el.closest("[hidden]")) return false;
    if (!el.getClientRects().length) return false;
    var cs = getComputedStyle(el);
    return cs.visibility !== "hidden" && cs.display !== "none";
  }
  /* Passos cujo alvo está na tela agora (um alvo que só existe no celular, ou só com vídeo pronto, fica de fora). */
  function passosDaTela(tela) {
    var out = [];
    (TOURS[tela] ? TOURS[tela].passos : []).forEach(function (p) {
      var el = Array.prototype.filter.call(document.querySelectorAll('[data-tour="' + p.alvo + '"]'), visivel)[0];
      if (el) out.push({ p: p, el: el });
    });
    return out;
  }
  function tourVisto(k) { try { return localStorage.getItem(k) === "1"; } catch (e) { return false; } }
  function marcarTourVisto(k) { try { localStorage.setItem(k, "1"); } catch (e) { /* sem armazenamento: o tour volta na próxima visita */ } }
  function abrirTour(tela, auto) {
    tela = tela || telaAtual();
    if (!TOURS[tela]) { if (!auto) toast(tela === "arrumar" ? "Esta tela já vai te guiando, uma pergunta por vez." : "Esta tela ainda não tem tour.", "aviso"); return; }
    var criar = window.driver && window.driver.js && window.driver.js.driver;
    if (!criar) { if (!auto) toast("O tour não carregou. Feche o painel e abra de novo.", "aviso"); return; }
    var passos = passosDaTela(tela);
    if (!passos.length) { if (!auto) toast("Nada pra mostrar nesta tela agora.", "aviso"); return; }
    var t = TOURS[tela];
    var parcial = passos.length < t.passos.length ? ":" + passos.map(function (x) { return x.p.alvo; }).join("+") : "";
    var chave = "tour:" + tela + ":" + t.versao + parcial;
    if (auto && tourVisto(chave)) return;
    fecharSuspensa(false); fecharGaveta();
    var reduz = matchMedia("(prefers-reduced-motion: reduce)").matches;
    var cel = matchMedia("(max-width: 760px)").matches;
    var d = criar({
      popoverClass: "tv-tour", showProgress: true, progressText: "{{current}} de {{total}}",
      nextBtnText: "Próximo", prevBtnText: "Voltar", doneBtnText: "Pronto!", showButtons: ["next", "previous"],
      overlayColor: "#041419", overlayOpacity: 0.74, stagePadding: cel ? 6 : 10, stageRadius: 26,
      smoothScroll: !reduz, animate: !reduz, allowClose: true, allowKeyboardControl: true, disableActiveInteraction: true,
      steps: passos.map(function (x) { return { element: x.el, popover: { title: esc(x.p.titulo), description: esc(x.p.texto), side: x.p.lado, align: "start" } }; }),
      onPopoverRender: function (pop, op) {
        var cara = document.createElement("img");
        cara.className = "cara"; cara.src = ICONE; cara.alt = "";
        pop.wrapper.appendChild(cara);
        var pular = document.createElement("button");
        pular.type = "button"; pular.className = "tour-pular"; pular.textContent = "Pular";
        pular.addEventListener("click", function () { d.destroy(); });
        pop.footer.insertBefore(pular, pop.footerButtons);
        /* Celular: o balão fica embaixo; o alvo sobe pra não ficar atrás dele. */
        if (cel) setTimeout(function () {
          var alvo = op && op.state && op.state.activeElement;
          if (!alvo) return;
          var r = alvo.getBoundingClientRect(), limite = window.innerHeight - pop.wrapper.offsetHeight - 110;
          if (r.bottom > limite) { window.scrollBy(0, Math.min(r.top - 80, r.bottom - limite)); if (d.refresh) d.refresh(); }
        }, 60);
        if (!cel) requestAnimationFrame(function () {
          var w = pop.wrapper, r = w.getBoundingClientRect(), m = 12;
          var dx = r.right > innerWidth - m ? innerWidth - m - r.right : (r.left < m ? m - r.left : 0);
          var dy = r.bottom > innerHeight - m ? innerHeight - m - r.bottom : (r.top < m ? m - r.top : 0);
          if (dx || dy) {
            w.style.left = (parseFloat(w.style.left) || r.left) + dx + "px"; w.style.top = (parseFloat(w.style.top) || r.top) + dy + "px";
            if (pop.arrow) pop.arrow.style.display = "none";
          }
        });
        /* O foco vai para o Próximo: Enter avança, Tab chega no Pular e no Voltar. */
        setTimeout(function () { if (pop.nextButton && document.contains(pop.nextButton)) pop.nextButton.focus({ preventScroll: true }); }, 30);
      },
      onDestroyed: function () { marcarTourVisto(chave); marcarTourVisto(chaveTourBase(tela)); tourAtivo = null; document.body.classList.remove("com-tour"); }
    });
    tourAtivo = d;
    document.body.classList.add("com-tour");
    d.drive();
  }
  /* Abre sozinho na primeira visita de cada tela, 600 ms depois de ela montar, nunca por cima do assistente, da
     abertura, de uma lista aberta, do Mais opções, de uma janela ou de um aviso. */
  function agendarTour(tela) {
    clearTimeout(tourTimer);
    if (!TOURS[tela] || tourAtivo) return;
    if (TOUR_SOZINHO.indexOf(tela) < 0) {
      if (!tourVisto(chaveTourBase(tela))) main.querySelectorAll('[data-acao="tour"]').forEach(function (b) { b.classList.add("pisca"); });
      return;
    }
    var tentar = function (n) {
      if (telaAtual() !== tela || tourAtivo) return;
      var ocupado = document.getElementById("abertura") || susp || (gaveta && gaveta.open) || document.getElementById("janela").open ||
        document.querySelector("#toasts .aviso") || editandoLinha || (document.activeElement && /INPUT|TEXTAREA/.test(document.activeElement.tagName));
      if (ocupado) { if (n < 30) tourTimer = setTimeout(function () { tentar(n + 1); }, 700); return; }
      abrirTour(tela, true);
    };
    tourTimer = setTimeout(function () { tentar(0); }, 600);
  }

  /* ------------------------------------------------------------ render */
  function render() {
    if (!E) return;
    var bruto = (location.hash || "").replace("#", "").split("/")[0];
    if (APELIDOS[bruto]) history.replaceState(null, "", "#" + APELIDOS[bruto] + location.hash.slice(1 + bruto.length));
    var id = telaAtual();
    var foco = id === "arrumar" && magoAberto();
    Array.prototype.slice.call(document.body.classList).forEach(function (c) { if (/^t-/.test(c)) document.body.classList.remove(c); });
    document.body.classList.add("t-" + id);
    document.body.classList.toggle("modo-foco", foco);
    document.body.classList.toggle("modo-completo", COMPLETO);
    document.body.classList.toggle("modo-simples", !COMPLETO);
    document.body.classList.toggle("estatico", ESTATICO);
    renderTopo(id);
    lateral.hidden = foco;
    if (!foco) renderLateral(id); else lateral.innerHTML = "";
    barra.hidden = foco;
    renderBarra(id);
    if (gaveta && gaveta.open) renderGaveta();
    if (susp) fecharSuspensa(false);
    var guia = id === "aprender" && TUT ? tutorial(subRota()) : null;
    document.title = (guia ? guia.titulo + " · " : "") + TELAS[id][0] + " · Temporada Viral";
    if (E.prefs && E.prefs.erro && ["canal", "redes", "jeito", "metricas"].indexOf(id) >= 0) {
      main.innerHTML = voltarLinha(id) + vazio(ilustracao("erro", "tv-cade", "vazio-ilustra"), "As preferências não carregaram", link("Ver o que aconteceu", "#problema", "botao secundario"), E.prefs.erro);
      return;
    }
    main.innerHTML = T[id]();
    main.dataset.tela = id;
    ligarPlayers(main);
    if (TOURS[id] && passosDaTela(id).length < 2) main.querySelectorAll('[data-acao="tour"]').forEach(function (b) { b.remove(); });
    if (id === "aprender") ligarCodigos(main.querySelector(".corpo-guia"));
    agendarTour(id);
  }
  /* Redesenha a tela sem pular: guarda a rolagem, as listas que rolam e os recolhidos abertos, e devolve o foco. */
  function redesenhar(seletorFoco, seletorReserva) {
    var y = window.scrollY;
    var abertos = Array.prototype.filter.call(main.querySelectorAll("details[open] > summary"), Boolean).map(function (s) { return s.textContent; });
    var rolam = {};
    [".estilos", ".outros ul", ".cartoes-gancho", ".trilho-lugares"].forEach(function (s) { var el = main.querySelector(s); if (el) rolam[s] = [el.scrollTop, el.scrollLeft]; });
    /* O chat é refeito junto com a tela (a conferência de mudanças roda a cada 4 s): guarda onde a pessoa estava. */
    var logAntes = document.getElementById("chat-log"), chatRol = null, chatAbertos = {};
    if (logAntes) {
      chatRol = { topo: logAntes.scrollTop, fim: logAntes.scrollHeight - logAntes.scrollTop - logAntes.clientHeight < 60 };
      Array.prototype.forEach.call(logAntes.querySelectorAll("details[open][data-id]"), function (d) { chatAbertos[d.getAttribute("data-id")] = true; });
    }
    render();
    var logDepois = document.getElementById("chat-log");
    if (logDepois && chatRol) {
      Array.prototype.forEach.call(logDepois.querySelectorAll("details[data-id]"), function (d) { if (chatAbertos[d.getAttribute("data-id")]) d.open = true; });
      logDepois.scrollTop = chatRol.fim ? logDepois.scrollHeight : chatRol.topo;
    }
    main.querySelectorAll("details > summary").forEach(function (s) { if (abertos.indexOf(s.textContent) >= 0) s.parentNode.open = true; });
    Object.keys(rolam).forEach(function (s) { var el = main.querySelector(s); if (el) { el.scrollTop = rolam[s][0]; el.scrollLeft = rolam[s][1]; } });
    window.scrollTo(0, y);
    var el = (seletorFoco && document.querySelector(seletorFoco)) || (seletorReserva && document.querySelector(seletorReserva));
    if (el) { if (!el.matches("a, button, input, textarea, [tabindex]")) el.setAttribute("tabindex", "-1"); el.focus({ preventScroll: true }); }
  }
  /* Player próprio: tocar e pausar, tempo, barra de posição e som. Com movimento reduzido, nada toca sozinho. */
  function ligarPlayers(raiz) {
    var reduz = matchMedia("(prefers-reduced-motion: reduce)").matches;
    raiz.querySelectorAll(".player-proprio").forEach(function (box) {
      var v = box.querySelector("video"), r = box.querySelector(".barrinha"), ta = box.querySelector(".t-atual"), tt = box.querySelector(".t-total");
      var bt = box.querySelector('[data-acao="player-tocar"]');
      if (!v) return;
      var att = function () {
        if (v.duration && isFinite(v.duration)) { var p = v.currentTime / v.duration; r.value = Math.round(p * 1000); r.style.setProperty("--p", (p * 100).toFixed(1) + "%"); tt.textContent = fmtSeg(v.duration); }
        ta.textContent = fmtSeg(v.currentTime);
      };
      v.addEventListener("timeupdate", att); v.addEventListener("loadedmetadata", att);
      v.addEventListener("play", function () { bt.innerHTML = icone("pausa"); bt.setAttribute("aria-label", "Pausar"); box.classList.add("tocando"); });
      v.addEventListener("pause", function () { bt.innerHTML = icone("tocar"); bt.setAttribute("aria-label", "Tocar"); box.classList.remove("tocando"); });
      r.addEventListener("input", function () { if (v.duration) v.currentTime = r.value / 1000 * v.duration; });
      v.addEventListener("click", function () { if (v.paused) v.play().catch(function () {}); else v.pause(); });
      if (v.autoplay) { if (reduz) { v.removeAttribute("autoplay"); v.pause(); } else v.play().catch(function () { /* sem autoplay: fica a capa */ }); }
    });
  }

  /* ------------------------------------------------------------ janela (exemplo, ficha, guia, imagem) */
  function abrirJanela(titulo, corpoHtml, peHtml, classe) {
    var d = document.getElementById("janela");
    var corpo = document.getElementById("janela-corpo"), pe = document.getElementById("janela-pe");
    document.getElementById("janela-titulo").textContent = titulo;
    pararMidia(d);
    corpo.innerHTML = corpoHtml; corpo.scrollTop = 0;
    pe.innerHTML = peHtml || ""; pe.hidden = !peHtml;
    d.className = "janela" + (classe ? " " + classe : "");
    ligarCodigos(corpo); ligarPlayers(corpo);
    if (d.open) return;
    if (d.showModal) d.showModal(); else d.setAttribute("open", "");
    document.body.classList.add("com-janela");
  }
  /* Áudio e vídeo da janela param de vez ao fechar ou trocar o conteúdo (por qualquer caminho: X, Fechar, Esc, fora). */
  function pararMidia(raiz) {
    raiz.querySelectorAll("audio, video").forEach(function (m) {
      try { m.pause(); m.removeAttribute("src"); m.load(); } catch (e) { /* elemento já fora da página */ }
    });
  }
  function fecharJanela() {
    var d = document.getElementById("janela");
    pararMidia(d);
    if (d.close) d.close(); else d.removeAttribute("open");
    document.body.classList.remove("com-janela");
  }
  function abrirTutorial(id) {
    carregarTutoriais().then(function () {
      var t = tutorial(id);
      if (!t) { toast("Esse guia não está nesta versão do kit. Peça no chat da IA: me explica isso.", "aviso"); return; }
      abrirJanela(t.titulo, '<div class="md">' + t.html + "</div>", link("Abrir em Aprender", "#aprender/" + t.id, "botao secundario", "seguir", ' data-acao="fechar-janela"'), "janela-guia");
    });
  }
  /* Caminho de arquivo citado num guia (`metodo/ganchos.md`) vira link para o guia correspondente. */
  function ligarCodigos(raiz) {
    if (!TUT || !raiz) return;
    var porArquivo = {};
    TUT.forEach(function (t) { if (t.arquivo) porArquivo[t.arquivo] = t; });
    raiz.querySelectorAll("code").forEach(function (c) {
      var alvo = porArquivo[c.textContent.trim()];
      if (!alvo || c.closest("pre") || c.closest("a")) return;
      var a = document.createElement("a");
      a.href = "#aprender/" + alvo.id; a.className = "link-codigo"; a.dataset.acao = "fechar-janela";
      a.textContent = alvo.titulo;
      c.replaceWith(a);
    });
  }

  /* ------------------------------------------------------------ versão nova do kit */
  /* Ao abrir: com versão nova liberada (dentro do prazo das atualizações), pergunta se pode atualizar; fora do prazo,
     conta que ela saiu e mostra o Atualizações para Sempre. Uma vez por sessão do navegador; depois, o botão fica em
     Suporte > Sua licença. */
  function sessao(k, v) {
    try {
      if (v === undefined) return sessionStorage.getItem("tvpainel." + k);
      sessionStorage.setItem("tvpainel." + k, v);
    } catch (e) { /* sem armazenamento: pergunta de novo na próxima abertura */ }
    return null;
  }
  function verificarAtualizacao() {
    if (ESTATICO) return;
    var feita = sessao("atualizado");
    if (feita) { sessao("atualizado", ""); toast("Pronto: o estúdio está na versão " + feita + "."); }
    api("GET", "/api/atualizacao?conferir=1").then(function (a) {
      if (!a || !a.nova) return;
      E.atualizacao = a;
      if (a.andamento && a.andamento.rodando) { janelaAtualizando(a.nova.numero); return; }
      if (sessao("atualizacaoVista") === a.nova.numero) return;
      /* Não atrapalha as perguntas da primeira vez, o tour nem outra janela aberta: tenta de novo daqui a pouco. */
      if (tourAtivo || precisaMago() || document.getElementById("janela").open) { setTimeout(verificarAtualizacao, 60000); return; }
      sessao("atualizacaoVista", a.nova.numero);
      janelaAtualizacao(a);
    });
  }
  function novidadesHtml(n) {
    if (!n.novidades || !n.novidades.length) return "";
    return '<ul class="novidades">' + n.novidades.map(function (x) { return "<li>" + icone("estrela") + "<span>" + esc(x) + "</span></li>"; }).join("") + "</ul>";
  }
  function janelaAtualizacao(a) {
    var n = a.nova;
    if (a.nuvem) {
      abrirJanela("Saiu a versão " + n.numero, "<p>Você está na " + esc(a.local) + ". Nesta instalação na nuvem, a versão nova chega pelo instalador: peça no chat da IA <b>atualizar o estúdio</b>.</p>" + novidadesHtml(n),
        botao("Fechar", 'data-acao="fechar-janela"', "secundario"), "janela-versao");
      return;
    }
    if (!a.liberada) {
      abrirJanela("Saiu a versão " + n.numero,
        "<p>Você está na " + esc(a.local) + ". Suas atualizações grátis terminaram em " + esc(dataBr(a.atualizacoes_ate)) + ", então esta versão não chega sozinha. Seu estúdio continua funcionando como está.</p>" +
        novidadesHtml(n) + "<p>Com o <b>Atualizações para Sempre</b>, esta e todas as próximas versões chegam pra você, sem prazo.</p>",
        (a.oferta ? link("Quero as atualizações para sempre", a.oferta, "botao", "estrela", ' target="_blank" rel="noopener noreferrer"') : "") +
          botao("Agora não", 'data-acao="fechar-janela"', "secundario"), "janela-versao");
      return;
    }
    abrirJanela("Chegou a versão " + n.numero,
      "<p>Tem versão nova do Temporada Viral (você está na " + esc(a.local) + "). Quer atualizar agora?</p>" + novidadesHtml(n) +
      '<p class="nota">Leva uns 2 minutos' + (n.tamanho ? " (" + Math.max(1, Math.round(n.tamanho / 1e6)) + " MB)" : "") +
      ". Seus canais, séries, vídeos e ajustes ficam como estão, e a versão de agora fica guardada.</p>",
      botao("Atualizar agora", 'data-acao="atualizar-agora"', "", "seguir") + botao("Depois", 'data-acao="fechar-janela"', "secundario"), "janela-versao");
  }
  var atuTimer = null;
  function janelaAtualizando(numero) {
    abrirJanela("Atualizando para a " + numero,
      '<div class="atualizando"><div class="medidor" role="progressbar" aria-label="Andamento da atualização" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><i style="width:0%"></i></div>' +
      '<p id="atu-texto" class="linha-conta" aria-live="polite">Começando…</p><p class="nota">Deixe esta aba aberta até terminar. Se fechar, a atualização continua e o painel volta sozinho.</p></div>',
      "", "janela-versao janela-atualizando");
    clearInterval(atuTimer);
    var viuPronto = 0, caiu = false, inicio = Date.now(), desde = null;
    function mostrar(texto, pct) {
      var t = document.getElementById("atu-texto"), m = document.querySelector(".janela-atualizando .medidor");
      if (t) t.textContent = texto;
      if (m && pct != null) { m.setAttribute("aria-valuenow", String(Math.round(pct))); m.firstChild.style.width = Math.round(pct) + "%"; }
    }
    function terminar() { clearInterval(atuTimer); sessao("atualizado", numero); location.reload(); }
    atuTimer = setInterval(function () {
      fetch("/api/atualizacao", { credentials: "same-origin", headers: { "X-Painel-Token": TOKEN } })
        .then(function (r) { if (!r.ok) throw new Error("fora"); return r.json(); })
        .then(function (a) {
          var an = (a && a.andamento) || {};
          if (desde === null && a) desde = a.painel_desde;
          /* Painel novo no ar (reabriu: outro início, ou caiu e voltou), ou o antigo não fechou em 20 s: recarrega. */
          if (viuPronto && (caiu || (a && a.painel_desde !== desde) || Date.now() - viuPronto > 20000)) { terminar(); return; }
          if (an.etapa === "erro") {
            clearInterval(atuTimer);
            var corpo = document.getElementById("janela-corpo"), pe = document.getElementById("janela-pe");
            corpo.innerHTML = '<p class="erro-linha">' + icone("aviso") + "<span>" + esc(an.msg || "Não deu certo.") + "</span></p>" +
              (/Atualizações para Sempre/.test(an.msg || "") && E.atualizacao && E.atualizacao.oferta ? "" : '<p class="nota">Seu estúdio continua funcionando na versão de agora.</p>');
            pe.innerHTML = botao("Tentar de novo", 'data-acao="atualizar-agora"', "", "seguir") + botao("Fechar", 'data-acao="fechar-janela"', "secundario");
            pe.hidden = false;
            return;
          }
          if (an.etapa === "pronto" || (a && a.local === numero)) {
            if (!viuPronto) viuPronto = Date.now();
            mostrar("Pronto! Abrindo o painel na versão " + numero + "…", 100);
            return;
          }
          mostrar((an.texto || "Atualizando") + (an.etapa === "baixando" || an.etapa === "instalando" ? " · " + (an.pct || 0) + "%" : "…"), an.pct);
        })
        .catch(function () {
          if (viuPronto) caiu = true;
          if (Date.now() - inicio > 120000 || (viuPronto && Date.now() - viuPronto > 45000)) {
            clearInterval(atuTimer);
            mostrar("O painel não voltou sozinho. Feche esta aba e abra pelo ícone Temporada Viral: ele já abre na versão nova.", 100);
          }
        });
    }, 800);
  }

  /* ------------------------------------------------------------ ações */
  function trocarCanal(rota, corpo) {
    api("POST", rota, corpo).then(function (r) {
      if (!r.ok) { toast(r.msg || "Não deu para trocar.", "erro"); return; }
      /* Canal novo começa do zero: as perguntas voltam a aparecer. */
      mago = null; gravarLocal("mago", null); gravarLocal("magoPulado", false);
      fecharJanela(); toast(r.msg);
      recarregarTela().then(function () { location.hash = precisaMago() ? "#arrumar" : "#inicio"; });
    });
  }
  function marcarSegmento(b) {
    var grupo = b.parentNode;
    grupo.querySelectorAll("button").forEach(function (x) { var m = x === b; x.setAttribute("aria-pressed", String(m)); if (x.hasAttribute("aria-checked")) x.setAttribute("aria-checked", String(m)); });
  }
  var pronTimer = null;
  function salvarPronuncia() {
    clearTimeout(pronTimer);
    pronTimer = setTimeout(function () {
      var box = document.getElementById("pronuncia");
      if (!box || ESTATICO) return;
      var trocas = Array.prototype.map.call(box.querySelectorAll("#pron-linhas tr"), function (tr) {
        var t = tr.querySelector('[data-pron="termo"]'), g = tr.querySelector('[data-pron="grafia"]');
        return { termo: t.value, grafia: g.value, padrao: t.dataset.padrao || "" };
      }).filter(function (x) { return x.termo.trim() || x.grafia.trim(); });
      var fora = document.getElementById("pron-fora").value.split("\n");
      var caixa = box.querySelector(".msgs-pron");
      api("POST", "/api/pronuncia", { trocas: trocas, fora_da_fala: fora }).then(function (r) {
        if (!r.ok) { caixa.innerHTML = '<p class="erro-msg">' + icone("aviso") + "<span>" + esc((r.erros || [r.msg]).join(" ")) + "</span></p>"; return; }
        caixa.innerHTML = ""; box.removeAttribute("data-sujo");
        carregar().then(function () { mostrarSalvo(); });
      });
    }, 500);
  }
  function salvarLinhaCanal(b) {
    var secao = b.dataset.secao, campo = b.dataset.campo;
    var linha = b.closest(".def-linha");
    var input = linha.querySelector("[data-linha-campo]");
    var v = String(input.value || "").trim();
    if (campo === "arroba") v = v.replace(/^@/, "").toLowerCase();
    var erro = linha.querySelector(".erro-msg");
    var falhou = function (msg) { linha.classList.add("erro"); erro.hidden = false; erro.innerHTML = icone("aviso") + "<span></span>"; erro.lastChild.textContent = msg; input.focus(); };
    if ((campo === "nome" || campo === "nicho" || campo === "publico") && v.length < 3) { falhou("Escreva pelo menos 3 letras."); return; }
    var mud = {}; mud[secao] = {}; mud[secao][campo] = v;
    if (campo === "nome" && !valor("canal", "arroba")) mud.canal.arroba = slug(v);
    api("POST", "/api/prefs", { mudancas: mud }).then(function (r) {
      if (!r.ok) { var m = (r.erros || [r.msg]).join(" "); var meta1 = meta(secao, campo); falhou(meta1 ? m.replace(meta1.rotulo + ":", "").trim() : m); return; }
      editandoLinha = "";
      carregar().then(function () { redesenhar('[data-acao="linha-mudar"][data-campo="' + campo + '"]'); mostrarSalvo(); });
    });
  }
  function enviarMetricas(b) {
    var f = b.closest("form");
    var msg = f.querySelector(".msgs-metricas");
    var falha = function (t) { msg.hidden = false; msg.innerHTML = icone("aviso") + "<span></span>"; msg.lastChild.textContent = t; };
    msg.hidden = true;
    var lidos0 = {};
    f.querySelectorAll("[data-num]").forEach(function (i) { var n = lerNumero(i.value); if (i.value.trim() && n === null) lidos0.erro = CAMPOS_METRICAS.filter(function (c) { return c[0] === i.dataset.num; })[0][1]; else if (n !== null) lidos0[i.dataset.num] = n; });
    if (lidos0.erro) { falha("Confira o número em “" + lidos0.erro + "”."); return; }
    if (!Object.keys(lidos0).length) { falha("Escreva pelo menos um número."); return; }
    var views = lidos0.views;
    var numeros = {};
    Object.keys(lidos0).forEach(function (k) {
      if (CONTA_VIRA_PCT[k]) {
        if (!views) return;
        numeros[CONTA_VIRA_PCT[k]] = pct(lidos0[k] / views * 100);
      } else numeros[k] = k === "views" ? String(Math.round(lidos0[k])) : pct(lidos0[k]);
    });
    if (Object.keys(lidos0).some(function (k) { return CONTA_VIRA_PCT[k]; }) && !views) { falha("Escreva as visualizações: a porcentagem é calculada a partir delas."); return; }
    var ep = (f.querySelector('input[name="episodio"]') || {}).value || epMetricas;
    b.disabled = true;
    api("POST", "/api/metricas", { episodio: ep, rede: redeMetricas, numeros: numeros }).then(function (r) {
      b.disabled = false;
      if (!r.ok) {
        var t = String(r.msg || "Não deu para anotar.");
        Object.keys(ROTULO_METRICA).forEach(function (c) { t = t.replace(new RegExp(c, "ig"), ROTULO_METRICA[c]); });
        falha(t); return;
      }
      toast(r.msg || "Números anotados.");
      carregar().then(function () { redesenhar('[data-tour="veredito"]'); });
    });
  }
  var ACOES = {
    "conquista-compartilhar": function (b) { compartilharConquista(b.dataset.id); },
    "conquista-enviar": function () { enviarConquista(); },
    "conquista-ver": function () { fecharJanela(); location.hash = "#conquistas"; },
    copiar: function (b) { if (/chat da IA/i.test(b.dataset.aviso || "")) { pedirIA(b.dataset.texto, b); return; } copiar(b.dataset.texto, b, b.dataset.aviso); },
    "pedir-ia": function (b) { confirmarArrumar(b.dataset.texto, Number(b.dataset.n) || 1, b); },
    "arrumar-ok": function () { var t = iaPendente; fecharJanela(); iaPendente = ""; if (t) pedirIA(t, null, "Arruma o que falta no meu estúdio."); },
    "mandar-pedido": function (b) { pedirIA(fraseVideo(estiloPorId(b.dataset.id)), b); },
    "ia-pedir": function (b) { pedirIA(b.dataset.texto, b); },
    "postar-modo": function (b) { modoPostar = b.dataset.modo; redesenhar('[data-acao="postar-modo"][data-modo="' + modoPostar + '"]'); },
    "mago-comecar": function () { magoIr(0); },
    "ia-escolher": function (b) { iaCli = b.dataset.cli; gravarLocal("iaCli", iaCli); redesenhar('[data-acao="ia-escolher"][data-cli="' + iaCli + '"]'); },
    "ia-conferir": function (b) { b.disabled = true; carregarIA(true).then(function () { redesenhar('[data-acao="ia-escolher"][data-cli="' + iaCli + '"]'); }); },
    "ia-atalho": function (b) {
      if (b.dataset.n) { confirmarArrumar(b.dataset.texto, Number(b.dataset.n) || 1, b); return; }
      if (iaPronta()) mandarIA(b.dataset.texto, b.dataset.mostrar); else copiar(b.dataset.texto, null, "Pedido copiado. Cole no chat da IA e mande.");
    },
    "ia-mandar": function () { var t = document.getElementById("chat-texto"); if (t && t.value.trim()) mandarIA(t.value); else if (t) t.focus(); },
    "ia-parar": function () { pararIA(); },
    "ia-arquivo": function (b) { abrirArquivoIA(b.dataset.c); },
    "ia-historico": function () { abrirHistoricoIA(); },
    "ia-abrir-conversa": function (b) { abrirConversaIA(b.dataset.id); },
    "ia-conversa-video": function (b) {
      fetch("/api/ia/conversa-do-video?nome=" + encodeURIComponent(b.dataset.ep), { credentials: "same-origin", headers: { "X-Painel-Token": TOKEN } })
        .then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; })
        .then(function (j) {
          if (j && j.ok) abrirConversaIA(j.id);
          else toast("Não achei a conversa deste vídeo. Ela pode ter sido feita em outro computador ou apagada.", "aviso");
        });
    },
    "ia-resposta": function (b) { if (iaPronta() && !conversaDe(iaCli).rodando) mandarIA(b.dataset.texto); },
    "ia-ep": function (b) { iaEpSel = b.dataset.ep; gravarLocal("iaEp", iaEpSel); desenharEp(); },
    "ia-nova": function () { iaConversas[iaCli] = { id: null, msgs: [] }; guardarConversas(); redesenhar("#chat-texto"); },
    "ia-abrir": function (b) {
      b.disabled = true;
      api("POST", "/api/ia/abrir", { cli: iaCli }).then(function (r) {
        b.disabled = false;
        if (r.ok) { feito(b, "Aberta"); toast("A IA abriu numa janela separada."); return; }
        toast(r.msg || "Não consegui abrir a IA.", "erro");
        if ((r.passos || []).length) abrirJanela("Para abrir a IA", '<ol class="passos-ia">' + r.passos.map(function (p) { return "<li>" + esc(p) + "</li>"; }).join("") + "</ol>");
      });
    },
    "copiar-frase": function (b) { pedirIA(fraseVideo(estiloPorId(b.dataset.id)), b); },
    "escolher-estilo": function (b) {
      history.replaceState(null, "", "#fazer/" + b.dataset.id);
      redesenhar('[data-acao="escolher-estilo"][data-id="' + b.dataset.id + '"]');
    },
    ideia: function (b) {
      assuntoVideo = b.dataset.texto;
      if (b.dataset.estilo) history.replaceState(null, "", "#fazer/" + b.dataset.estilo);
      redesenhar("#assunto-video");
    },
    "usar-personagem": function (b) { personagemVideo = b.dataset.nome; location.hash = "#fazer"; toast("Pronto: o pedido vai com " + b.dataset.nome + "."); },
    "tirar-personagem": function () { personagemVideo = ""; redesenhar("#assunto-video"); },
    "player-tocar": function (b) { var v = b.closest(".player-proprio").querySelector("video"); if (v.paused) v.play().catch(function () {}); else v.pause(); },
    "player-som": function (b) {
      var v = b.closest(".player-proprio").querySelector("video");
      v.muted = !v.muted; b.innerHTML = icone(v.muted ? "mudo" : "som"); b.setAttribute("aria-label", v.muted ? "Ligar o som" : "Tirar o som");
    },
    exemplo: function (b) {
      var x = estiloPorId(b.dataset.id);
      if (!x) return;
      abrirJanela(nomeEstilo(x.id), playerHtml(urlExemplo(x.id, "video"), capaEstilo(x), { auto: true, rotulo: "Exemplo do estilo " + nomeEstilo(x.id), total: "0:10" }) +
        '<p class="apoio exemplo-legenda">' + esc(fraseEstilo(x)) + "</p>", link("Usar este estilo", "#fazer/" + x.id, "botao", "", ' data-acao="fechar-janela"'), "janela-video");
    },
    ficha: function (b) {
      var x = estiloPorId(b.dataset.id);
      if (x) abrirJanela(nomeEstilo(x.id), '<div class="md">' + (x.ficha_html || "") + "</div>", link("Usar este estilo", "#fazer/" + x.id, "botao", "", ' data-acao="fechar-janela"'), "janela-guia");
    },
    ampliar: function (b) { abrirJanela(b.dataset.titulo, '<img class="grande" src="' + esc(midia(b.dataset.src)) + '" alt="' + esc(b.dataset.titulo) + '">'); },
    abrir: function (b) { api("POST", "/api/abrir", { caminho: b.dataset.caminho }).then(function (r) { if (!r.ok) toast(r.msg || "Não consegui abrir.", "erro"); else toast("Pasta aberta no seu computador."); }); },
    aba: function (b) { abaEpisodio[b.dataset.ep] = Number(b.dataset.i); redesenhar('[data-acao="aba"][data-i="' + b.dataset.i + '"]'); },
    "ir-postar": function (b) { redePostar = b.dataset.rede; },
    "mudar-ir": function (b, ev) {
      ev.preventDefault();
      var alvo = document.querySelector(b.getAttribute("href"));
      if (alvo) { alvo.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" }); var t = alvo.querySelector("textarea"); if (t) t.focus({ preventScroll: true }); }
    },
    "mudar-onde": function (b) {
      marcarSegmento(b);
      var f = b.closest("form"); f.dataset.onde = b.dataset.onde;
      f.querySelector(".campo-cena").hidden = b.dataset.onde !== "cena";
      if (b.dataset.onde === "cena") montarCenas(f.querySelector(".cenas-video"));
    },
    "cena-video": function (b) {
      var g = b.closest(".cenas-video");
      g.querySelectorAll(".cena-video").forEach(function (x) { var m = x === b; x.setAttribute("aria-pressed", String(m)); x.setAttribute("aria-checked", String(m)); });
      b.closest("form").querySelector('[name="trecho"]').value = b.dataset.t;
    },
    "pedido-enviar": function (b) {
      var f = b.closest("form"), t = f.querySelector('[name="texto"]'), erro = t.parentNode.querySelector(".erro-msg");
      if (t.value.trim().length < 3) { erro.hidden = false; erro.innerHTML = icone("aviso") + "<span>Escreva o que mudar.</span>"; t.focus(); return; }
      erro.hidden = true;
      var campoCena = f.querySelector('[name="cena"]'), campoTrecho = f.querySelector('[name="trecho"]');
      var cena = f.dataset.onde === "cena" && campoCena ? campoCena.value : "";
      var trecho = f.dataset.onde === "cena" && campoTrecho ? campoTrecho.value : "";
      if (f.dataset.onde === "cena" && campoTrecho && !trecho) { erro.hidden = false; erro.innerHTML = icone("aviso") + "<span>Toque na cena que você quer mudar.</span>"; return; }
      var textoPedido = trecho ? "No trecho perto de " + trecho + ": " + t.value.trim() : t.value;
      api("POST", "/api/pedido", { episodio: f.dataset.ep, cena: cena, texto: textoPedido }).then(function (r) {
        if (!r.ok) { erro.hidden = false; erro.innerHTML = icone("aviso") + "<span></span>"; erro.lastChild.textContent = r.msg || "Não deu."; return; }
        var onde = cena ? " (na cena " + cena + ")" : (trecho ? " (no trecho perto de " + trecho + ")" : " (no vídeo todo)");
        var mostrar = "Muda isto no vídeo «" + f.dataset.nome + "»" + onde + ": " + t.value.trim();
        if (iaPronta()) { pedirIA(mostrar + ". O pedido também está anotado em canal/pedidos.md: marca como feito quando terminar.", null, mostrar); }
        else toast("Pedido guardado. A IA faz a mudança da próxima vez que você conversar com ela.");
        carregar().then(function () { if (telaAtual() === "meus") redesenhar(); });
      });
    },
    corrigir: function (b) { salvarPrefs(JSON.parse(b.dataset.mudancas)); },
    verificar: function (b) {
      b.disabled = true; b.innerHTML = '<span class="girando" aria-hidden="true"></span><span class="rotulo">Conferindo</span>';
      api("POST", "/api/verificar", {}).then(function () { setTimeout(recarregarTela, 600); });
    },
    "postar-rede": function (b) { redePostar = b.dataset.rede; redesenhar('[data-rede="' + redePostar + '"]'); },
    "voz-conectar": function (b) {
      vozConectar = b.dataset.chave;
      redesenhar();
      var alvo = document.getElementById("conectar");
      if (alvo) { alvo.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" }); var i = alvo.querySelector('input[type="password"]'); if (i) i.focus({ preventScroll: true }); }
    },
    "voz-usar": function (b) { salvarPrefs({ voz: { provedor: b.dataset.id } }); },
    "chave-enviar": function (b) {
      var f = b.closest("form"), input = f.querySelector('[name="valor"]'), msg = f.querySelector(".msg-chave");
      var v = input.value.trim(), seg = f.querySelector('[name="segredo"]');
      if (!v) { msg.textContent = "Cole a chave primeiro."; input.focus(); return; }
      /* Higgsfield: a chave tem duas partes (Key ID e Secret) e vai como ID:SECRET. */
      if (seg) { if (!seg.value.trim()) { msg.textContent = "Cole o Secret também."; seg.focus(); return; } v = v + ":" + seg.value.trim(); }
      b.disabled = true; b.innerHTML = '<span class="girando" aria-hidden="true"></span><span class="rotulo">Testando</span>';
      msg.textContent = "Testando a chave no site…";
      api("POST", "/api/chave", { nome: f.dataset.nome, valor: v }).then(function (r) {
        if (r.ok) { input.value = ""; if (seg) seg.value = ""; }
        v = "";
        b.disabled = false; b.innerHTML = '<span class="rotulo">Testar e salvar</span>';
        msg.textContent = r.msg || "";
        if (r.ok) {
          chaveSalva[f.dataset.nome] = r.fim;
          if (r.saldo) ultimoSaldo = r.saldo;
          toast("Chave salva (termina em …" + r.fim + ").");
          recarregarTela();
        }
      });
    },
    "me-ir": function (b) {
      meuEstilo.passo = Math.max(-1, Number(b.dataset.i)); salvarMeuEstilo(); redesenhar(".me-opcao[aria-checked=true], .me-opcao, #me-nome");
      scrollTo(0, 0);
    },
    "pers-novo": function (b) {
      var campo = document.getElementById("pers-livre"), t = campo ? campo.value.trim().replace(/"/g, "'") : "";
      pedirIA(t ? "cria um personagem novo pro meu canal exatamente assim: \"" + t + "\". Segue as regras de corpo e roupa do kit e me mostra a folha de poses antes de animar" : b.dataset.texto, b);
    },
    "me-livre": function (b) {
      var campo = document.getElementById("me-livre"), t = campo ? campo.value.trim() : "";
      if (t.length < 3) { toast("Escreva como você quer (umas palavras já bastam).", "erro"); if (campo) campo.focus(); return; }
      meuEstilo.livre = meuEstilo.livre || {};
      meuEstilo.livre[b.dataset.q] = t; meuEstilo.r[b.dataset.q] = "auto";
      var qs = (EP && EP.perguntas) || [];
      meuEstilo.passo = meuEstilo.mudando ? qs.length : meuEstilo.passo + 1;
      meuEstilo.mudando = false; salvarMeuEstilo(); redesenhar(".me-opcao, #me-nome"); scrollTo(0, 0);
    },
    "me-responder": function (b) {
      if (meuEstilo.livre) delete meuEstilo.livre[b.dataset.q];
      meuEstilo.r[b.dataset.q] = b.dataset.o;
      var qs = (EP && EP.perguntas) || [];
      meuEstilo.passo = meuEstilo.mudando ? qs.length : meuEstilo.passo + 1;
      meuEstilo.mudando = false; salvarMeuEstilo(); redesenhar(".me-opcao, #me-nome"); scrollTo(0, 0);
    },
    "me-mudar": function () { meuEstilo.passo = "mudar"; meuEstilo.mudando = true; salvarMeuEstilo(); redesenhar(); scrollTo(0, 0); },
    "me-sortear": function (b) {
      var campo = document.getElementById("me-nome"); if (campo) meuEstilo.nome = campo.value.trim();
      b.disabled = true;
      api("POST", "/api/estilo-proprio/sortear", { respostas: meuEstilo.r, nome: meuEstilo.nome }).then(function (r) {
        b.disabled = false;
        if (!r.ok) { toast(r.msg || "Não deu pra sortear agora.", "erro"); if (r.falta) { EP.disponivel = false; redesenhar(); } return; }
        meuEstilo.passo = "ver"; salvarMeuEstilo();
        EP.sorteio = { rodando: true, fase: "sorteando" }; redesenhar(); scrollTo(0, 0); vigiarSorteio();
      });
    },
    "me-usar": function (b) {
      b.disabled = true;
      api("POST", "/api/estilo-proprio/usar", {}).then(function (r) {
        b.disabled = false;
        if (!r.ok) { toast(r.msg || "Não deu pra salvar.", "erro"); return; }
        if (meuEstilo.origem === "mago" && mago && mago.r && r.estilo_padrao) { mago.r.estilo = r.estilo_padrao; salvarMago(); }
        meuEstilo.passo = "feito"; salvarMeuEstilo();
        toast("Estilo salvo. Ele vale pras séries com voto.");
        Promise.all([carregar(), carregarEstiloProprio()]).then(function () { if (telaAtual() === "meuestilo") redesenhar(); });
      });
    },
    "me-voltar-mago": function () { meuEstilo = null; salvarMeuEstilo(); location.hash = "#arrumar"; },
    "mago-criar-estilo": function () { meuEstilo = { passo: -1, r: {}, nome: "", origem: "mago" }; salvarMeuEstilo(); location.hash = "#meuestilo"; },
    "criar-estilo": function () {
      if (!meuEstilo || meuEstilo.passo === "feito") { meuEstilo = { passo: -1, r: {}, nome: "" }; salvarMeuEstilo(); }
      location.hash = "#meuestilo";
    },
    modo: function (b) {
      var novo = b.dataset.modo === "completo";
      if (novo === COMPLETO) return;
      COMPLETO = novo; gravarLocal("completo", COMPLETO);
      render();
      toast(COMPLETO ? "Modo completo: todas as telas no menu." : "Modo simples: só o essencial no menu. O resto continua nos atalhos das telas.");
    },
    "gaveta-abrir": function () { abrirGaveta(); },
    "gaveta-fechar": function () { fecharGaveta(); },
    tour: function () {
      fecharGaveta(); marcarTourVisto(chaveTourBase(telaAtual()));
      main.querySelectorAll(".pisca").forEach(function (x) { x.classList.remove("pisca"); });
      setTimeout(function () { abrirTour(telaAtual(), false); }, 60);
    },
    canais: function () {
      var ca = E.canais || { lista: [] };
      fecharGaveta();
      abrirJanela("Trocar de canal",
        '<p class="apoio">O canal que sai fica guardado, com tudo dele. Dá pra voltar quando quiser.</p><ul class="lista-canais">' + ca.lista.map(function (x) {
          return "<li>" + avatarHtml(x) + "<span><b>" + esc(x.nome) + "</b><small>" + esc(x.arroba ? "@" + x.arroba : x.id) + "</small></span>" +
            (x.ativo ? '<span class="em-uso">' + icone("certo") + "Em uso</span>" : botao("Usar este", 'data-acao="canal-usar" data-id="' + esc(x.id) + '" data-nome="' + esc(x.nome) + '"', "secundario")) + "</li>";
        }).join("") + "</ul>" +
        '<div class="campo"><label for="canal-novo-nome">Canal novo</label><div class="chave"><input class="entrada" type="text" id="canal-novo-nome" maxlength="60" placeholder="Nome do canal novo">' +
        botao("Criar", 'data-acao="canal-novo"', "secundario") + "</div></div>", "", "janela-guia");
    },
    "canal-usar": function (b) { if (window.confirm("Trocar para o canal " + b.dataset.nome + "? O canal de agora fica guardado.")) trocarCanal("/api/canais/usar", { id: b.dataset.id }); },
    "canal-novo": function () {
      var nome = ((document.getElementById("canal-novo-nome") || {}).value || "").trim();
      if (nome.length < 3) { toast("Escreva o nome do canal novo (pelo menos 3 letras).", "aviso"); return; }
      if (window.confirm("Criar o canal " + nome + "? O canal de agora fica guardado.")) trocarCanal("/api/canais/novo", { nome: nome });
    },
    "linha-mudar": function (b) { editandoLinha = b.dataset.campo; redesenhar("#ed-" + b.dataset.campo); },
    "linha-cancelar": function () { var c = editandoLinha; editandoLinha = ""; redesenhar('[data-acao="linha-mudar"][data-campo="' + c + '"]'); },
    "linha-salvar": function (b) { salvarLinhaCanal(b); },
    arroba: function (b) {
      var input = document.getElementById("ed-arroba");
      var caixa = b.closest(".def-linha").querySelector(".arroba-resultado");
      var n = (input.value || "").trim().replace(/^@/, "").toLowerCase();
      if (!n) { input.focus(); return; }
      b.disabled = true; b.textContent = "Conferindo…";
      caixa.innerHTML = '<p class="meta">Consultando os sites, leva uns segundos…</p>';
      fetch("/api/arroba?n=" + encodeURIComponent(n), { credentials: "same-origin", headers: { "X-Painel-Token": TOKEN } }).then(function (r) { return r.json(); }).then(function (r) {
        b.disabled = false; b.textContent = "Conferir de novo";
        if (!r.formato) { caixa.innerHTML = '<p class="erro-msg">' + icone("aviso") + "<span>" + esc(r.aviso) + "</span></p>"; return; }
        var nomes = { com: n + ".com", instagram: "Instagram", youtube: "YouTube", tiktok: "TikTok" };
        var txt = { livre: "parece livre", ocupado: "parece ocupado", incerto: "não deu pra saber" };
        caixa.innerHTML = '<ul class="arroba-lista">' + Object.keys(r.redes).map(function (k) { return '<li class="' + r.redes[k] + '">' + esc(nomes[k] || k) + ": " + txt[r.redes[k]] + "</li>"; }).join("") + "</ul>" +
          '<p class="meta">É uma estimativa: a confirmação de verdade é criar a conta no app de cada rede.' + (r.aviso ? " " + esc(r.aviso) : "") + "</p>";
      }).catch(function () { b.disabled = false; b.textContent = "Conferir se está livre"; caixa.innerHTML = '<p class="erro-msg">Não consegui conferir agora.</p>'; });
    },
    refazer: function () { mago = null; gravarLocal("mago", null); iniciarMago(); if (location.hash === "#arrumar") render(); else location.hash = "#arrumar"; },
    ajuste: function (b) {
      var mud = {}; mud[b.dataset.secao] = {}; mud[b.dataset.secao][b.dataset.campo] = JSON.parse(b.dataset.valor);
      marcarSegmento(b);
      salvarPrefs(mud, null, '[data-acao="ajuste"][data-campo="' + b.dataset.campo + '"][data-valor="' + CSS.escape(b.dataset.valor) + '"]');
    },
    "campo-rec": function (b) {
      var mud = {}; mud[b.dataset.secao] = {}; mud[b.dataset.secao][b.dataset.campo] = recomendado(b.dataset.secao, b.dataset.campo);
      salvarPrefs(mud, null, '[data-campo="' + b.dataset.campo + '"]');
    },
    "jeito-rec": function () {
      if (!window.confirm("Voltar os ajustes desta tela ao recomendado?")) return;
      var mud = {};
      AJUSTES.forEach(function (a) { if (a[3] === "provedor") return; mud[a[2]] = mud[a[2]] || {}; mud[a[2]][a[3]] = recomendado(a[2], a[3]); });
      salvarPrefs(mud);
    },
    "rede-detalhe": function (b) {
      var r = b.dataset.rede; detalheRede[r] = !detalheRede[r];
      var ul = document.getElementById("det-" + r); if (ul) ul.hidden = !detalheRede[r];
      main.querySelectorAll('[data-acao="rede-detalhe"][data-rede="' + r + '"]').forEach(function (x) { x.setAttribute("aria-expanded", String(detalheRede[r])); x.textContent = detalheRede[r] ? "Esconder detalhes" : "Ver detalhes"; });
    },
    "rede-ligar": function (b) {
      var l = (valor("redes", "escolhidas") || []).slice(), r = b.dataset.rede, i = l.indexOf(r);
      if (i >= 0) l.splice(i, 1); else l.push(r);
      if (!l.length) { toast("Deixe pelo menos uma rede ligada.", "aviso"); return; }
      b.setAttribute("aria-checked", String(i < 0));
      salvarPrefs({ redes: { escolhidas: l } }, null, '[data-acao="rede-ligar"][data-rede="' + r + '"]');
    },
    objetivo: function (b) { objetivo = objetivo === b.dataset.id ? "" : b.dataset.id; redesenhar('[data-acao="objetivo"][data-id="' + b.dataset.id + '"]'); },
    "usar-estilo": function (b) { salvarPrefs({ roteiro: { estilo_padrao: b.dataset.id } }); },
    "gancho-escolher": function (b) {
      var t = b.dataset.texto, i = ganchosEscolhidos.indexOf(t);
      if (i >= 0) ganchosEscolhidos.splice(i, 1); else { if (ganchosEscolhidos.length >= 2) ganchosEscolhidos.pop(); ganchosEscolhidos.push(t); }
      redesenhar('[data-acao="gancho-escolher"][data-texto="' + CSS.escape(t) + '"]');
    },
    "testar-dois": function (b) {
      var a = ganchosEscolhidos[0], c = ganchosEscolhidos[1];
      if (!a || !c) return;
      pedirIA("faz duas versões do próximo vídeo pra testar o começo: a versão A começa com “" + a + "” e a versão B começa com “" + c + "”, o resto igual. depois me ajuda a ver qual segurou mais gente nos 3 primeiros segundos", b);
    },
    "pergunta-fim": function (b) { perguntaFim = b.dataset.texto; redesenhar('[data-acao="pergunta-fim"][data-texto="' + CSS.escape(perguntaFim) + '"]'); },
    "pergunta-copiar": function (b) {
      var q = (perguntaFim || "").trim();
      if (!q) { toast("Escolha ou escreva uma pergunta.", "aviso"); return; }
      pedirIA("no próximo vídeo, termina com esta pergunta: " + q, b);
    },
    "gancho-conferir": function (b) {
      var f = b.closest("form"), res = f.querySelector(".resultado-teste");
      res.innerHTML = '<p class="meta">Conferindo…</p>';
      api("POST", "/api/gancho", { fala: f.fala.value, tela: f.tela.value, dur_s: f.dur_s.value }).then(function (r) {
        if (!r.ok) { res.innerHTML = '<p class="erro-msg">' + icone("aviso") + "<span>" + esc(r.msg) + "</span></p>"; return; }
        var linhas = (r.erros || []).map(function (e) { return '<li class="ruim">' + icone("aviso") + "<span>" + esc(e) + "</span></li>"; })
          .concat((r.avisos || []).map(function (a) { return '<li class="atencao">' + icone("aviso") + "<span>" + esc(a) + "</span></li>"; }));
        if (!linhas.length) linhas.push('<li class="bom">' + icone("certo") + "<span>Começo aprovado: prende rápido, abre uma pergunta e tem texto na tela.</span></li>");
        res.innerHTML = '<p class="meta">' + (r.estimado ? "Tempo estimado pelo ritmo da fala: " : "A frase termina em ") + num(r.dur_s) + ' s.</p><ul class="resultado-lista">' + linhas.join("") + "</ul>";
      });
    },
    "metrica-rede": function (b) {
      redeMetricas = b.dataset.rede;
      b.parentNode.querySelectorAll("button").forEach(function (x) {
        var m = x === b; x.setAttribute("aria-pressed", String(m)); x.setAttribute("aria-checked", String(m));
        var s = x.querySelector(".rede"); if (s) s.remove();
        if (m) x.insertAdjacentHTML("afterbegin", selo(x.dataset.rede, true));
      });
    },
    "metricas-enviar": function (b) { enviarMetricas(b); },
    sumario: function (b, ev) {
      ev.preventDefault();
      var h = main.querySelectorAll(".corpo-guia h2")[Number(b.dataset.i)];
      if (h) { h.setAttribute("tabindex", "-1"); h.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" }); h.focus({ preventScroll: true }); }
    },
    "pron-adicionar": function () {
      var tb = document.getElementById("pron-linhas");
      var n = tb.children.length + 1;
      var tr = document.createElement("tr");
      tr.innerHTML = '<td><input class="entrada" type="text" aria-label="Palavra, linha ' + n + '" data-pron="termo" data-padrao="" maxlength="60"></td><td><input class="entrada" type="text" aria-label="Como a voz fala, linha ' + n + '" data-pron="grafia" maxlength="80"></td><td><button type="button" class="discreto mini" data-acao="pron-remover">Tirar</button></td>';
      tb.appendChild(tr); tr.querySelector("input").focus();
    },
    "pron-remover": function (b) { b.closest("tr").remove(); salvarPronuncia(); },
    tutorial: function (b) { abrirTutorial(b.dataset.id); },
    "fechar-janela": function () { fecharJanela(); },
    "atualizar-abrir": function () { if (E.atualizacao && E.atualizacao.nova) janelaAtualizacao(E.atualizacao); },
    "atualizar-agora": function (b) {
      var numero = E.atualizacao && E.atualizacao.nova ? E.atualizacao.nova.numero : "";
      b.disabled = true;
      api("POST", "/api/atualizacao/aplicar", {}).then(function (r) {
        b.disabled = false;
        if (!r.ok) { toast(r.msg || "Não deu para atualizar agora.", "erro"); return; }
        janelaAtualizando(numero);
      });
    },
    /* assistente */
    "mago-voltar": function () { magoLer(); if (mago.passo === 0) { location.hash = "#inicio"; return; } magoIr(mago.passo - 1); },
    "mago-seguir": function () { magoLer(); magoAvancar(); },
    "mago-nao-sei": function () {
      magoLer();
      var etapa = PASSOS_MAGO[mago.passo], r = mago.r;
      if (etapa === "assunto") r.nicho = "";
      if (etapa === "nome") { r.nome = ""; mago.outro.nome = false; }
      if (etapa === "publico") r.publico = "";
      if (etapa === "caminho") r.caminho = "";
      if (etapa === "estilo") r.estilo = "";
      if (etapa === "redes") r.redes = [];
      if (etapa === "assunto") mago.outro.assunto = false;
      if (etapa === "publico") mago.outro.publico = false;
      completarMago(mago.passo);
      if (mago.passo === PASSOS_MAGO.length - 1) { magoTerminar(); return; }
      magoIr(mago.passo + 1);
    },
    "mago-mudar-arroba": function (b) { var c = main.querySelector(".campo-arroba"); c.hidden = false; b.hidden = true; mago.r.arrobaMexido = true; salvarMago(); c.querySelector("input").focus(); },
    "mago-assunto": function (b) { magoEscolha(b, "nicho", "assunto"); },
    "mago-nome": function (b) { magoEscolha(b, "nome", "nome"); },
    "mago-publico": function (b) { magoEscolha(b, "publico", "publico"); },
    "mago-caminho": function (b) { magoEscolha(b, "caminho", "caminho"); },
    "mago-estilo": function (b) { mago.r.estilo = b.dataset.id; salvarMago(); redesenhar('[data-acao="mago-estilo"][data-id="' + b.dataset.id + '"]'); },
    "mago-rede": function (b) {
      var r = mago.r.redes, v = b.dataset.valor, i = r.indexOf(v);
      if (i >= 0) r.splice(i, 1); else r.push(v);
      b.setAttribute("aria-checked", String(i < 0));
      b.querySelector(".palavra").textContent = i < 0 ? "Sim" : "Não";
      salvarMago(); magoMsg("");
    },
    "mago-depois": function (b, ev) { if (ev) ev.preventDefault(); if (mago && !mago.fim) magoLer(); try { sessionStorage.setItem("tvpainel.magoPulado", "1"); } catch (e) { /* sem armazenamento */ } location.hash = "#inicio"; },
    "mago-sair": function () { mago = null; }
  };
  Object.keys(ACOES_ESTUDO).forEach(function (k) { ACOES[k] = ACOES_ESTUDO[k]; });
  var LINKS_COM_ACAO = ["fechar-janela", "mago-depois", "mago-sair", "ir-postar", "mudar-ir", "sumario"];
  document.addEventListener("keydown", teclaSuspensa);
  window.addEventListener("scroll", function () { document.body.classList.toggle("rolou", window.scrollY > 4); }, { passive: true });
  document.addEventListener("click", function (ev) {
    if (susp && !susp.lista.contains(ev.target) && !susp.botao.contains(ev.target)) fecharSuspensa(false);
    var sb = ev.target.closest(".suspensa-botao");
    if (sb) { if (susp && susp.botao === sb) fecharSuspensa(true); else abrirSuspensa(sb.closest(".suspensa")); return; }
    var op = ev.target.closest('.suspensa-lista [role="option"]');
    if (op && susp) { escolherSuspensa(Array.prototype.indexOf.call(opcoesSusp(), op)); return; }
    var b = ev.target.closest("[data-acao]");
    if (!b || !ACOES[b.dataset.acao] || b.disabled) return;
    if (b.tagName === "BUTTON" || LINKS_COM_ACAO.indexOf(b.dataset.acao) >= 0) ACOES[b.dataset.acao](b, ev);
  });

  /* ------------------------------------------------------------ campos: digitar, mudar, salvar sozinho */
  document.addEventListener("input", function (ev) {
    var el = ev.target;
    if (el.dataset && el.dataset.espelho) { var alvo = document.getElementById(el.dataset.espelho); if (alvo) alvo.value = el.type === "color" ? el.value.toUpperCase() : el.value; }
    if (el.type === "number" || el.type === "text") {
      var irmao = el.parentNode && el.parentNode.querySelector('[data-espelho="' + el.id + '"]');
      if (irmao && (irmao.type === "range" || /^#[0-9a-f]{6}$/i.test(el.value))) irmao.value = el.value;
    }
    if (el.classList && el.classList.contains("alternador-caixa")) el.parentNode.querySelector(".palavra").textContent = el.checked ? "Sim" : "Não";
    var form = el.closest && el.closest("form.form-prefs");
    if (form && el.type !== "range" && el.type !== "hidden") form.setAttribute("data-sujo", "1");
    if (el.dataset && el.dataset.pron) { document.getElementById("pronuncia").setAttribute("data-sujo", "1"); }
    var acao = el.dataset && el.dataset.acaoMudar;
    if (acao === "calc") document.getElementById("calc-res").innerHTML = calcTexto(el.value);
    if (acao === "assunto") { assuntoVideo = el.value; var frase = document.getElementById("frase-ia"); if (frase) frase.textContent = fraseVideo(estiloPorId(subRota())); }
    if (acao === "pergunta-minha") {
      perguntaFim = el.value;
      main.querySelectorAll('[data-acao="pergunta-fim"]').forEach(function (x) { x.setAttribute("aria-pressed", "false"); x.setAttribute("aria-checked", "false"); x.querySelector(".marcador").innerHTML = ""; });
    }
    if (mago && el.dataset && el.dataset.mago) {
      mago.r[el.dataset.mago] = el.value;
      if (el.dataset.mago === "arroba") mago.r.arrobaMexido = true;
      if (!mago.r.arrobaMexido) mago.r.arroba = slug(mago.r.nome);
      var ver = document.getElementById("mg-arroba-ver"); if (ver) ver.textContent = "@" + (mago.r.arroba || slug(mago.r.nome) || "…");
      magoMsg(""); salvarMago();
    }
    if (acao === "ia-rascunho") iaRascunho = el.value;
    if (acao === "me-nome" && meuEstilo) { meuEstilo.nome = el.value; salvarMeuEstilo(); }
    if (acao === "busca-guias") { buscaGuias = el.value; var rg = document.getElementById("resultado-guias"); if (rg) rg.innerHTML = resultadosGuias(el.value); }
    if (acao === "busca-ajuda") {
      var q = semAcento(el.value.trim()), visiveis = 0;
      main.querySelectorAll(".pergunta-item").forEach(function (d) { d.hidden = !!q && d.dataset.busca.indexOf(q) < 0; if (!d.hidden) visiveis++; if (q && !d.hidden && visiveis === 1) d.open = true; });
      var vz = document.getElementById("ajuda-vazio"); if (vz) vz.hidden = visiveis > 0;
    }
  });
  document.addEventListener("change", function (ev) {
    var el = ev.target;
    if (el.value === "__criar") { location.hash = "#meuestilo"; return; }
    var form = el.closest && el.closest("form.form-prefs");
    if (form && !(el.dataset && el.dataset.upload) && !ESTATICO) {
      var mud = mudancasDoForm(form);
      if (Object.keys(mud).length) salvarPrefs(mud, form, el.id ? "#" + CSS.escape(el.id) : (el.name ? '[name="' + el.name + '"]' : null));
      else form.removeAttribute("data-sujo");
    }
    if (el.dataset && el.dataset.pron) salvarPronuncia();
    var acao = el.dataset && el.dataset.acaoMudar;
    if (acao === "perfil") { estiloPerfil = el.value; redesenhar("#sel-estilo"); }
    if (acao === "estilo-gancho") { gravarLocal("estiloGancho", el.value); ganchosEscolhidos = []; redesenhar("#sel-gancho"); }
    if (acao === "estilo-padrao") salvarPrefs({ roteiro: { estilo_padrao: el.value } }, null, "#ed-estilo");
    if (acao === "metrica-ep") epMetricas = el.value;
    if (el.dataset && el.dataset.upload) enviarImagem(el);
  });
  function enviarImagem(input) {
    var arq = input.files && input.files[0];
    if (!arq) return;
    if (arq.size > 5 * 1024 * 1024) { toast("Imagem grande demais: use uma de até 5 MB.", "erro"); return; }
    arq.arrayBuffer().then(function (buf) { return api("POST", "/api/upload?tipo=" + encodeURIComponent(input.dataset.upload), buf, true); })
      .then(function (r) { if (!r.ok) { toast(r.msg || "Não consegui salvar a imagem.", "erro"); return; } toast(r.msg); recarregarTela(); });
  }
  document.addEventListener("keydown", function (ev) {
    var t = ev.target;
    if (!t || !t.matches) return;
    if (ev.key === "Enter" && t.id === "busca-guias") { var p = main.querySelector("#resultado-guias a"); if (p) { ev.preventDefault(); location.hash = p.getAttribute("href"); } }
    if (t.matches("[data-linha-campo]")) {
      if (ev.key === "Enter" && t.tagName === "INPUT") { ev.preventDefault(); var b = t.closest(".def-linha").querySelector('[data-acao="linha-salvar"]'); if (b) salvarLinhaCanal(b); }
      if (ev.key === "Escape") { ev.preventDefault(); ACOES["linha-cancelar"](); }
    }
    if (ev.key === "Enter" && t.closest && t.closest("#mago") && t.tagName === "INPUT") { ev.preventDefault(); magoLer(); magoAvancar(); }
    if (ev.key === "Enter" && !ev.shiftKey && t.id === "chat-texto") { ev.preventDefault(); if (t.value.trim()) mandarIA(t.value); }
  });
  /* Nenhum formulário recarrega a página: Enter vira a ação do botão do formulário. */
  document.addEventListener("submit", function (ev) {
    ev.preventDefault();
    var f = ev.target, tipo = f.dataset.form;
    var mapa = { chave: "chave-enviar", pedido: "pedido-enviar", gancho: "gancho-conferir", metricas: "metricas-enviar", ia: "ia-mandar" };
    var b = mapa[tipo] && f.querySelector('[data-acao="' + mapa[tipo] + '"]');
    if (b && !b.disabled && !ESTATICO) ACOES[mapa[tipo]](b, ev);
  });

  document.getElementById("janela-fechar").innerHTML = icone("fechar");
  document.getElementById("janela-fechar").addEventListener("click", fecharJanela);
  document.getElementById("janela").addEventListener("close", function () { pararMidia(this); document.body.classList.remove("com-janela"); });
  document.getElementById("janela").addEventListener("cancel", function () { pararMidia(this); });  // Esc: para na hora
  document.getElementById("janela").addEventListener("click", function (ev) { if (ev.target === this) fecharJanela(); });
  document.getElementById("aviso-ia-botao").addEventListener("click", function () {
    main.querySelectorAll("[data-sujo]").forEach(function (f) { f.removeAttribute("data-sujo"); });
    recarregarTela();
  });
  window.addEventListener("hashchange", function () {
    fecharGaveta();
    if (tourAtivo) tourAtivo.destroy();
    var base = (location.hash.split("/")[0] || "").replace("#", "");
    if (base !== "canal") editandoLinha = "";
    render();
    window.scrollTo(0, 0);
    main.focus({ preventScroll: true });
  });
  window.addEventListener("beforeunload", function (ev) { if (main.querySelector("[data-sujo]")) { ev.preventDefault(); ev.returnValue = ""; } });

  /* ------------------------------------------------------------ abertura e início */
  function tirarAbertura() {
    var a = document.getElementById("abertura");
    if (!a) return;
    a.classList.add("saindo");
    setTimeout(function () { a.remove(); agendarTour(telaAtual()); }, 260);
  }
  /* Primeira vez (canal sem o básico): abre direto nas perguntas, a menos que a pessoa tenha dito "depois". */
  function primeiraVez() {
    var h = (location.hash || "").replace("#", "").split("/")[0];
    var pulado = false;
    try { pulado = sessionStorage.getItem("tvpainel.magoPulado") === "1"; } catch (e) { /* sem armazenamento */ }
    if (!ESTATICO && precisaMago() && !pulado && (!h || h === "inicio" || h === "comece")) history.replaceState(null, "", "#arrumar");
  }
  if (!ESTATICO && TOKEN) {
    try { localStorage.setItem("tvpainel.codigo", TOKEN); sessionStorage.removeItem("tvpainel.tentou"); } catch (e) { /* sem armazenamento */ }
  }
  if (ESTATICO) {
    primeiraVez(); render(); tirarAbertura();
  } else {
    carregar().then(function () {
      primeiraVez(); render(); tirarAbertura();
      carregarTutoriais();
      setTimeout(verificarAtualizacao, 1500);
      // Com o chat pronto, os pedidos de toda tela viram "Mandar pra IA" (sem copiar e colar): redesenha a tela aberta.
      carregarIA().then(function () { if (!editando()) redesenhar(); });
    }).catch(function () {
      var a = document.getElementById("abertura");
      if (a) a.classList.add("erro");
    });
    setInterval(conferirMudancas, 4000);
    window.addEventListener("focus", conferirMudancas);
    document.addEventListener("visibilitychange", conferirMudancas);
    sinalDeVida();
    setInterval(sinalDeVida, 20000);
  }
})();
