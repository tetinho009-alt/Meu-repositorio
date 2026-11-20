/*! © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C */
/* Carregando: a animação do mascote; se o arquivo ainda não existir, tenta a reserva .apng e, por fim, a ilustração
   parada. Carrega no <head> para pegar o erro da imagem antes do painel.js. */
(function () {
  var ORDEM = ["/static/ilustracoes/carregando-anim.webp", "/static/ilustracoes/carregando-anim.apng", "/static/ilustracoes/carregando.webp"];
  document.addEventListener("error", function (ev) {
    var img = ev.target;
    if (!img || !img.classList || !img.classList.contains("masc-anim")) return;
    var i = ORDEM.indexOf(new URL(img.currentSrc || img.src, location.href).pathname);
    if (i >= 0 && i < ORDEM.length - 1) {
      var fonte = img.parentNode && img.parentNode.querySelector("source");
      if (fonte) fonte.remove();
      img.src = ORDEM[i + 1];
    }
  }, true);
})();
