/*! © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C */
/* Páginas de entrada do painel (sem o código de acesso, licença para ativar ou bloqueada). Sem dados do estúdio. */
(function () {
  "use strict";
  var corpo = document.body;
  var meta = document.querySelector('meta[name="painel-token"]');
  var token = meta ? meta.content : "";

  /* Ilustração que ainda não chegou: cai no mascote do site. */
  document.querySelectorAll("img[data-reserva-src]").forEach(function (img) {
    img.addEventListener("error", function () { if (!img.dataset.trocou) { img.dataset.trocou = "1"; img.src = img.dataset.reservaSrc; } });
  });

  /* Sem código: tenta uma vez o código que este navegador já guardou; senão, explica como abrir pelo ícone. */
  if (corpo.dataset.pagina === "sem-codigo") {
    try {
      var guardado = localStorage.getItem("tvpainel.codigo");
      if (guardado && !sessionStorage.getItem("tvpainel.tentou")) {
        sessionStorage.setItem("tvpainel.tentou", "1");
        location.replace("/?t=" + encodeURIComponent(guardado) + location.hash);
        return;
      }
    } catch (e) { /* sem armazenamento: segue com a explicação */ }
    var b = document.getElementById("abrir-de-novo"), passos = document.getElementById("como-abrir");
    if (b && passos) {
      b.addEventListener("click", function () {
        passos.hidden = false;
        b.setAttribute("aria-expanded", "true");
        passos.scrollIntoView({ block: "nearest" });
      });
    }
    return;
  }

  /* Licença: ativar com o e-mail da compra. */
  var form = document.getElementById("form-ativar");
  if (!form || !token) return;
  var campo = form.querySelector('input[name="email"]'), erro = document.getElementById("erro-ativar");
  var botao = form.querySelector('button[type="submit"]'), rotulo = botao.querySelector(".rotulo"), original = rotulo.textContent;
  var mostrar = function (t) {
    erro.hidden = !t;
    erro.textContent = t || "";
    campo.closest(".campo").classList.toggle("erro", !!t);
  };
  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    var email = campo.value.trim();
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { mostrar("Confira o e-mail: ele precisa ter @ e ponto, como nome@gmail.com."); campo.focus(); return; }
    mostrar("");
    botao.disabled = true;
    rotulo.textContent = "Ativando";
    botao.insertAdjacentHTML("afterbegin", '<span class="girando" aria-hidden="true"></span>');
    fetch("/api/licenca/ativar", { method: "POST", credentials: "same-origin",
      headers: { "X-Painel-Token": token, "Content-Type": "application/json" }, body: JSON.stringify({ email: email }) })
      .then(function (r) { return r.json(); })
      .catch(function () { return { ok: false, msg: "O painel não respondeu. Feche esta aba e abra pelo ícone de novo." }; })
      .then(function (r) {
        var g = botao.querySelector(".girando"); if (g) g.remove();
        if (r && r.ok) {
          botao.classList.add("e-feito");
          rotulo.textContent = "Ativado";
          setTimeout(function () { location.reload(); }, 900);
          return;
        }
        botao.disabled = false;
        rotulo.textContent = original;
        mostrar((r && r.msg) || "Não deu para ativar agora. Tente de novo.");
        campo.focus();
      });
  });
})();
