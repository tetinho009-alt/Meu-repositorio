# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Janela da chave: o usuário cola a chave (voz, YouTube, Instagram) numa página local, sem ela passar pela conversa com a IA.

Uso (a partir da pasta kit/):
    python chave.py                  # ElevenLabs: abre a janela no navegador, testa e salva
    python chave.py --qual azure     # Azure Speech
    python chave.py --qual gemini    # voz grátis do Google (AI Studio)
    python chave.py --qual youtube   # leitura dos comentários do YouTube (contar votos)
    python chave.py --qual instagram # token do Instagram (contar votos e publicar)
    python chave.py --conferir       # só testa a chave já salva e mostra o saldo do plano

A página roda só neste computador (127.0.0.1, porta aleatória, link com código de uso único) e fecha sozinha
depois de salvar ou em 30 minutos. A chave vai para um arquivo de segredos FORA da pasta do kit
(~/.temporada-viral/segredos.json), e o config.json passa a apontar para ele. O terminal nunca mostra a chave.
"""
import argparse
import html
import json
import os
import secrets
import sys
import threading
import time
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(KIT))

from config import CFG, SEGREDOS, segredo  # noqa: E402

ARQUIVO_PADRAO = "~/.temporada-viral/segredos.json"
INTRO = "Pra narrar os seus vídeos, o estúdio precisa da chave da sua conta."
ESPERA_MAX_S = 30 * 60

QUAIS = {
    "elevenlabs": {
        "titulo": "Chave da voz (ElevenLabs)",
        "passos": [
            ("Entre na ElevenLabs", "Crie a conta (pode ser com o Google) ou entre na sua.",
             "https://elevenlabs.io/app/sign-in", "Abrir a ElevenLabs"),
            ("Crie a chave", "No menu da esquerda: Developers, depois API Keys, depois Create API Key. "
             "Dê o nome que quiser. Se aparecer a lista do que a chave pode fazer, libere Text to Speech, "
             "Voices e User (o User é só pra eu te mostrar o saldo). Copie o código: ele só aparece uma vez.",
             "https://elevenlabs.io/app/developers/api-keys", "Abrir a página das chaves"),
        ],
    },
    "GEMINI_API_KEY": {
        "titulo": "Chave da voz grátis (Google AI Studio)",
        "passos": [
            ("Entre no Google AI Studio", "Entre com a sua conta do Google (a mesma do YouTube serve). É grátis e não "
             "pede cartão.", "https://aistudio.google.com/", "Abrir o AI Studio"),
            ("Crie a chave", "Clique em Get API key, depois em Create API key. Copie o código que aparecer.",
             "https://aistudio.google.com/app/apikey", "Abrir a página das chaves"),
        ],
    },
    "YT_API_KEY": {
        "titulo": "Chave do YouTube (contar votos)",
        "intro": "Pra contar os votos dos comentários do YouTube, o estúdio precisa de uma chave de leitura da sua "
                 "conta Google. Ela só lê o que já é público e não mexe no canal.",
        "passos": [
            ("Crie um projeto", "Entre com a conta Google dona do canal. No topo, clique no seletor de projeto, depois "
             "em Novo projeto, e dê o nome do canal.", "https://console.cloud.google.com/projectcreate",
             "Abrir o Google Cloud"),
            ("Ative a API do YouTube", "Com o projeto selecionado, clique em Ativar na página da YouTube Data API v3.",
             "https://console.cloud.google.com/apis/library/youtube.googleapis.com", "Abrir a API do YouTube"),
            ("Crie a chave", "Em Credenciais, clique em Criar credenciais, depois em Chave de API. Em Editar chave, "
             "marque Restringir chave e escolha só a YouTube Data API v3. Salve e copie a chave.",
             "https://console.cloud.google.com/apis/credentials", "Abrir as credenciais"),
        ],
    },
    "IG_ACCESS_TOKEN": {
        "titulo": "Token do Instagram (contar votos)",
        "intro": "Pra ler os comentários dos seus Reels e contar os votos, o estúdio precisa do token da sua conta "
                 "profissional do Instagram. Ele vale 60 dias, e o estúdio renova sozinho antes de vencer.",
        "passos": [
            ("Conta profissional", "No app do Instagram, no @ do canal: Configurações, Tipo de conta e ferramentas, "
             "Mudar para conta profissional, Criador.", None, None),
            ("Crie o app na Meta", "Entre com o seu Facebook, aceite virar desenvolvedor, clique em Criar app e "
             "escolha o caso de uso do Instagram. O nome pode ser o do canal.", "https://developers.facebook.com/apps",
             "Abrir a Meta for Developers"),
            ("Gere o token", "No app: Instagram, Configuração da API com login do Instagram. Adicione o @ do canal "
             "como testador e aceite o convite no Instagram (Configurações, Apps e sites, Convites de testador). "
             "Depois, em Gerar tokens de acesso, clique em Adicionar conta, entre com o @ do canal, autorize e "
             "copie o token.", None, None),
        ],
    },
    "azure_speech": {
        "titulo": "Chave da voz (Azure Speech)",
        "passos": [
            ("Abra o recurso de Fala", "No portal do Azure, abra o seu recurso de Speech (ou crie um na região "
             f"{CFG['voz']['azure'].get('regiao', 'brazilsouth')}, plano F0 grátis).",
             "https://portal.azure.com/#view/Microsoft_Azure_ProjectOxford/CognitiveServicesHub/~/SpeechServices",
             "Abrir o portal do Azure"),
            ("Copie a chave", "Em Chaves e Ponto de Extremidade, copie a CHAVE 1.", None, None),
        ],
    },
}


def arquivo_segredos():
    """Arquivo de segredos em uso, ou o padrão fora do kit."""
    atual = CFG["segredos"].get("arquivo")
    return Path(atual) if atual else Path(os.path.expanduser(ARQUIVO_PADRAO))


def salvar(nome, valor):
    arq = arquivo_segredos()
    if KIT in arq.parents:
        raise SystemExit("O arquivo de segredos está dentro da pasta do kit. Aponte segredos.arquivo para fora dela.")
    arq.parent.mkdir(parents=True, exist_ok=True)
    dados = json.loads(arq.read_text(encoding="utf-8")) if arq.is_file() else {}
    dados[SEGREDOS.get(nome, nome)] = valor
    arq.write_text(json.dumps(dados, indent=1), encoding="utf-8")
    if os.name != "nt":
        os.chmod(arq, 0o600)
    # O config.json do usuário passa a apontar para o arquivo (só se ainda não aponta)
    cfg_arq = Path(os.environ.get("MAQUINA_CONFIG") or KIT / "config.json")
    cfg = json.loads(cfg_arq.read_text(encoding="utf-8")) if cfg_arq.is_file() else {}
    if not cfg.get("segredos", {}).get("arquivo"):
        cfg.setdefault("segredos", {})["arquivo"] = ARQUIVO_PADRAO
        cfg_arq.write_text(json.dumps(cfg, indent=1, ensure_ascii=False), encoding="utf-8")
    return arq


def _falta_permissao(resposta):
    """True quando a ElevenLabs recusou por falta de permissão da chave (chave válida e restrita), não por chave errada."""
    try:
        detalhe = resposta.json().get("detail")
        estado = detalhe.get("status", "") if isinstance(detalhe, dict) else str(detalhe)
    except (ValueError, AttributeError):
        return False
    return "missing_permission" in estado or "permission" in estado.lower()


def _pode_falar(h):
    """Confere a permissão Text to Speech sem gastar crédito: pede fala com texto vazio. Sem a permissão, a
    ElevenLabs recusa com 401 antes de olhar o texto; com ela, recusa o texto vazio (400/422). None: não deu pra saber."""
    import requests
    try:
        r = requests.post("https://api.elevenlabs.io/v1/text-to-speech/JBFqnCBsd6RMkjVDRZzb", headers=h,
                          json={"text": ""}, timeout=30)
    except requests.RequestException:
        return None
    if r.status_code in (401, 403) and _falta_permissao(r):
        return False
    return True if r.status_code in (200, 400, 404, 422) else None


SEM_FALA = ("A chave conecta, mas está sem a permissão de gerar voz. No site da ElevenLabs, em Developers > API Keys, "
            "clique na chave, ligue Text to Speech (Access), Voices (Read) e User (Read) e salve. Depois clique em "
            "Testar e salvar de novo (a chave é a mesma).")


def testar(nome, valor):
    """(ok, mensagem para o usuário, saldo ou None). Nunca devolve a chave."""
    import requests

    valor = "".join(valor.split())     # tira espaço, quebra de linha e tab colados junto com a chave

    if nome == "elevenlabs":
        h = {"xi-api-key": valor}
        r = requests.get("https://api.elevenlabs.io/v1/user/subscription", headers=h, timeout=30)
        if r.status_code == 200:
            d = r.json()
            sobra = max(0, d["character_limit"] - d["character_count"])
            reset = d.get("next_character_count_reset_unix")
            quando = datetime.fromtimestamp(reset).strftime("%d/%m") if reset else "?"
            saldo = {"plano": d.get("tier"), "sobra": sobra, "limite": d["character_limit"], "renova": quando,
                     "minutos": round(sobra / 1000)}
            aviso = " O plano grátis não libera uso comercial: pra monetizar, use o Starter ou acima." \
                if d.get("tier") == "free" else ""
            if _pode_falar(h) is False:
                return False, SEM_FALA, None
            return True, (f"A chave funcionou. Sobram {sobra:,} caracteres do plano {d.get('tier')} (uns "
                          f"{saldo['minutos']} minutos de narração), renova em {quando}.{aviso}").replace(",", "."), saldo
        # Chave restrita sem permissão de User: confere pelas vozes
        v = requests.get("https://api.elevenlabs.io/v1/voices", headers=h, timeout=30)
        if v.status_code == 200:
            if _pode_falar(h) is False:
                return False, SEM_FALA, None
            return True, ("A chave funcionou. Pra eu te mostrar o saldo, libere a permissão User na chave "
                          "(não é obrigatório)."), None
        if _falta_permissao(r) or _falta_permissao(v):
            # A ElevenLabs reconheceu a chave; ela só está restrita. O kit precisa de Text to Speech (obrigatório)
            # e de Voices: read (para listar as vozes); User: read só mostra o saldo.
            if _pode_falar(h) is False:
                return False, SEM_FALA, None
            return True, ("A chave é válida, mas está com permissões limitadas. No site da ElevenLabs, em API Keys, "
                          "deixe ligado: Text to Speech (obrigatório) e Voices: ler (para escolher a voz)."), None
        return False, "A ElevenLabs recusou essa chave. Confira se copiou o código inteiro e tente de novo.", None
    if nome == "GEMINI_API_KEY":
        r = requests.get("https://generativelanguage.googleapis.com/v1beta/models", headers={"x-goog-api-key": valor},
                         timeout=30)
        if r.status_code == 200:
            return True, ("A chave funcionou. A voz do Google é grátis, com limite por dia: se acabar no meio, o "
                          "estúdio espera e tenta de novo."), None
        return False, "O Google recusou essa chave. Confira se copiou o código inteiro e tente de novo.", None
    if nome == "azure_speech":
        regiao = CFG["voz"]["azure"].get("regiao", "brazilsouth")
        r = requests.get(f"https://{regiao}.tts.speech.microsoft.com/cognitiveservices/voices/list",
                         headers={"Ocp-Apim-Subscription-Key": valor}, timeout=30)
        if r.status_code == 200:
            return True, f"A chave funcionou na região {regiao}.", None
        return False, f"O Azure recusou essa chave na região {regiao}. Confira a chave e a região.", None
    if nome == "YT_API_KEY":
        r = requests.get("https://www.googleapis.com/youtube/v3/videos",
                         params={"part": "id", "id": "jNQXAC9IVRw", "key": valor}, timeout=30)
        if r.status_code == 200:
            return True, "A chave funcionou. Ela só lê dados públicos e não vence; a cota grátis sobra muito.", None
        texto = r.text
        if "accessNotConfigured" in texto or "SERVICE_DISABLED" in texto:
            return False, ("A chave existe, mas a YouTube Data API v3 não está ativada nesse projeto. Ative no passo 2 "
                           "e tente de novo (pode levar 1 minuto pra valer)."), None
        if "API_KEY_SERVICE_BLOCKED" in texto or "blocked" in texto.lower():
            return False, ("A chave está restrita a outra API. Em Editar chave, marque a YouTube Data API v3 nas "
                           "restrições."), None
        return False, "O Google recusou essa chave. Confira se copiou o código inteiro e tente de novo.", None
    if nome == "IG_ACCESS_TOKEN":
        r = requests.get("https://graph.instagram.com/v21.0/me", params={"fields": "username,account_type",
                         "access_token": valor}, timeout=30)
        if r.status_code == 200:
            d = r.json()
            tipo = d.get("account_type", "")
            aviso = "" if tipo in ("BUSINESS", "MEDIA_CREATOR", "") else (
                " Atenção: a conta não aparece como profissional; mude para Criador no app do Instagram.")
            return True, f"O token funcionou, conectado como @{d.get('username', '?')}.{aviso}", None
        return False, ("O Instagram recusou esse token. Ele vence em 60 dias e só vale para o @ que autorizou: gere "
                       "outro no passo 3 e copie inteiro."), None
    return False, "Tipo de chave desconhecido.", None


PAGINA = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{titulo}</title>
<style>
body {{ margin: 0; background: #EEF2FA; color: #141320; font: 17px/1.55 system-ui, sans-serif; }}
main {{ max-width: 560px; margin: 32px auto; padding: 28px 24px; background: #fff; border-radius: 18px;
  box-shadow: 0 6px 30px rgba(0,0,0,.08); }}
h1 {{ margin: 0 0 6px; font-size: 26px; }}
ol {{ padding-left: 22px; }} li {{ margin: 14px 0; }}
a.botao, button {{ display: inline-block; margin-top: 8px; padding: 11px 18px; border: 0; border-radius: 10px;
  background: #141320; color: #fff; font: 700 16px system-ui, sans-serif; text-decoration: none; cursor: pointer; }}
input {{ width: 100%; box-sizing: border-box; padding: 12px; border: 2px solid #141320; border-radius: 10px;
  font: 16px ui-monospace, monospace; }}
.aviso {{ padding: 12px 14px; border-radius: 10px; background: #FFE8E3; }}
.ok {{ padding: 12px 14px; border-radius: 10px; background: #E3F7EA; }}
small {{ color: #555; }}
</style></head><body><main>
<h1>{titulo}</h1>
<p>{intro} É como uma senha: fica guardada só neste computador e não passa pela conversa com a IA.</p>
{corpo}
</main></body></html>"""


def pagina_form(qual, token, erro=""):
    info = QUAIS[qual]
    itens = []
    for titulo, texto, link, rotulo in info["passos"]:
        botao = f'<br><a class="botao" href="{link}" target="_blank" rel="noopener">{rotulo}</a>' if link else ""
        itens.append(f"<li><b>{html.escape(titulo)}</b><br>{html.escape(texto)}{botao}</li>")
    itens.append('<li><b>Cole a chave aqui</b><form method="post" action="/salvar">'
                 f'<input type="hidden" name="t" value="{token}">'
                 '<input type="password" name="chave" autocomplete="off" spellcheck="false" required '
                 'aria-label="Chave" placeholder="cole a chave"><br><button type="submit">Salvar a chave</button>'
                 '</form></li>')
    aviso = f'<p class="aviso" role="alert">{html.escape(erro)}</p>' if erro else ""
    corpo = f"{aviso}<ol>{''.join(itens)}</ol><small>Esta janela fecha sozinha em 30 minutos.</small>"
    return PAGINA.format(titulo=html.escape(info["titulo"]), intro=html.escape(info.get("intro", INTRO)), corpo=corpo)


def pagina_ok(qual, msg):
    corpo = (f'<p class="ok" role="status">{html.escape(msg)}</p>'
             "<p>Pode fechar esta janela e voltar pra conversa.</p>")
    return PAGINA.format(titulo=html.escape(QUAIS[qual]["titulo"]), intro=html.escape(QUAIS[qual].get("intro", INTRO)), corpo=corpo)


def janela(qual):
    token = secrets.token_urlsafe(16)
    estado = {"feito": False}

    class Pedido(BaseHTTPRequestHandler):
        def log_message(self, *a):  # silencioso: nada de URL nem corpo no terminal
            pass

        def _responde(self, codigo, corpo):
            dados = corpo.encode("utf-8")
            self.send_response(codigo)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(dados)))
            self.end_headers()
            self.wfile.write(dados)

        def do_GET(self):
            q = parse_qs(urlparse(self.path).query)
            if q.get("t", [""])[0] != token:
                return self._responde(403, "Link vencido. Peça um novo na conversa.")
            self._responde(200, pagina_form(qual, token))

        def do_POST(self):
            tam = min(int(self.headers.get("Content-Length", 0)), 8192)
            q = parse_qs(self.rfile.read(tam).decode("utf-8"))
            if q.get("t", [""])[0] != token:
                return self._responde(403, "Link vencido. Peça um novo na conversa.")
            valor = q.get("chave", [""])[0].strip()
            if len(valor) < 16:
                return self._responde(200, pagina_form(qual, token, "Essa chave parece incompleta. Copie de novo."))
            try:
                ok, msg, saldo = testar(qual, valor)
            except Exception:
                ok, msg, saldo = False, "Sem internet ou o serviço não respondeu. Tente de novo em instantes.", None
            if not ok:
                return self._responde(200, pagina_form(qual, token, msg))
            arq = salvar(qual, valor)
            self._responde(200, pagina_ok(qual, msg))
            estado.update(feito=True, msg=msg, saldo=saldo, arq=str(arq))

    srv = ThreadingHTTPServer(("127.0.0.1", 0), Pedido)
    url = f"http://127.0.0.1:{srv.server_address[1]}/?t={token}"
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    print("Janela da chave aberta no navegador. Se não abriu, abra este link neste computador:")
    print(url, flush=True)
    webbrowser.open(url)
    fim = time.time() + ESPERA_MAX_S
    while not estado["feito"] and time.time() < fim:
        time.sleep(0.5)
    time.sleep(1)  # deixa a página de sucesso chegar ao navegador
    srv.shutdown()
    if not estado["feito"]:
        print("CHAVE_NAO_SALVA: a janela fechou em 30 minutos sem receber a chave. Rode de novo quando quiser.")
        sys.exit(2)
    print("CHAVE_SALVA:", estado["msg"])
    if estado["saldo"]:
        print("SALDO:", json.dumps(estado["saldo"], ensure_ascii=False))
    print("Arquivo de segredos:", estado["arq"])


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--qual", choices=["elevenlabs", "azure", "gemini", "youtube", "instagram"], default="elevenlabs")
    ap.add_argument("--conferir", action="store_true", help="só testa a chave salva e mostra o saldo")
    a = ap.parse_args()
    qual = {"azure": "azure_speech", "gemini": "GEMINI_API_KEY", "youtube": "YT_API_KEY",
            "instagram": "IG_ACCESS_TOKEN"}.get(a.qual, a.qual)
    if a.conferir:
        valor = segredo(qual, obrigatorio=False)
        if not valor:
            print("SEM_CHAVE: nenhuma chave salva. Rode: python chave.py" + ("" if a.qual == "elevenlabs" else f" --qual {a.qual}"))
            sys.exit(2)
        ok, msg, saldo = testar(qual, valor)
        print(("CHAVE_OK: " if ok else "CHAVE_RECUSADA: ") + msg)
        if saldo:
            print("SALDO:", json.dumps(saldo, ensure_ascii=False))
        sys.exit(0 if ok else 1)
    janela(qual)


if __name__ == "__main__":
    main()
