# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Envia um Short pela YouTube Data API v3 (`videos.insert`, envio resumable) com OAuth.

Uso:
    python -m publicar.youtube autorizar                  # uma vez, num computador com navegador
    python -m publicar.youtube enviar --video ep.mp4 --titulo "..." --descricao desc.txt
        [--tags terror,suspense] [--privacidade private|unlisted|public] [--publicar-em 2026-11-03T22:00:00Z]
        [--sintetico | --nao-sintetico] [--seco]

Credenciais (variáveis de ambiente): YT_CLIENT_ID, YT_CLIENT_SECRET (app OAuth "Desktop" do Google Cloud, com a
YouTube Data API ativada) e YT_REFRESH_TOKEN (sai do `autorizar`). App em "Testing" expira o token em 7 dias:
publique o app (Produção) para uso contínuo.
Campos fixos: selfDeclaredMadeForKids = false (canal de terror não é para crianças).
`containsSyntheticMedia` (rótulo de conteúdo alterado/sintético): padrão em publicar.youtube.midia_sintetica.
Animação não realista é isenta; marque se houver cena fotorrealista, voz imitando pessoa real ou música de IA.
Agendar: --publicar-em exige --privacidade private (a API publica no horário).
"""
import argparse
import json
import os
import secrets
import urllib.parse
from pathlib import Path

from config import CFG, segredo

from .http import Cliente, ErroAPI, token

YT = CFG["publicar"]["youtube"]
ESCOPO = "https://www.googleapis.com/auth/youtube.upload"
TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD = "https://www.googleapis.com/upload/youtube/v3/videos"


def acesso(cli, seco):
    """Troca o refresh token por um access token."""
    dados = {"client_id": token("youtube_client_id", seco), "client_secret": token("youtube_client_secret", seco),
             "refresh_token": token("youtube_refresh_token", seco), "grant_type": "refresh_token"}
    r, _ = cli.pedido("POST", TOKEN_URL, data=dados, descricao="token de acesso (OAuth)", falso={"access_token": "SECO"})
    return r["access_token"]


def corpo_video(titulo, descricao, tags, privacidade, publicar_em, sintetico, categoria):
    if len(titulo) > 100:
        raise SystemExit("título passa de 100 caracteres (limite do YouTube)")
    status = {"privacyStatus": privacidade, "selfDeclaredMadeForKids": False, "containsSyntheticMedia": bool(sintetico)}
    if publicar_em:
        if privacidade != "private":
            raise SystemExit("--publicar-em exige --privacidade private")
        status["publishAt"] = publicar_em
    return {"snippet": {"title": titulo, "description": descricao, "tags": tags, "categoryId": str(categoria),
                        "defaultLanguage": "pt-BR", "defaultAudioLanguage": "pt-BR"}, "status": status}


def enviar(video, titulo, descricao, tags=(), privacidade=None, publicar_em=None, sintetico=None, seco=False):
    cli = Cliente(seco)
    privacidade = privacidade or YT.get("privacidade", "private")
    sintetico = YT.get("midia_sintetica", False) if sintetico is None else sintetico
    corpo = corpo_video(titulo, descricao, list(tags), privacidade, publicar_em, sintetico, YT.get("categoria", "1"))
    acc = acesso(cli, seco)
    tam = os.path.getsize(video) if Path(video).exists() else 0
    _, cab = cli.pedido("POST", UPLOAD, params={"uploadType": "resumable", "part": "snippet,status"}, json_=corpo,
                        headers={"Authorization": f"Bearer {acc}", "X-Upload-Content-Type": "video/mp4",
                                 "X-Upload-Content-Length": str(tam), "Content-Type": "application/json; charset=UTF-8"},
                        descricao="1/2 abrir envio (videos.insert)")
    destino = cab.get("Location")
    if not destino:
        raise ErroAPI("o YouTube não devolveu a URL de envio")
    r, _ = cli.pedido("PUT", destino, corpo=str(video), headers={"Authorization": f"Bearer {acc}", "Content-Type": "video/mp4"},
                      descricao="2/2 enviar o arquivo", falso={"id": "SECO_VIDEO", "status": corpo["status"]})
    print(("SECO_OK (nada foi enviado) " if seco else "ENVIADO ") + f"https://youtube.com/shorts/{r.get('id')}")
    return dict(id=r.get("id"), pedidos=cli.pedidos)


def autorizar(porta=8765):
    """Fluxo OAuth de app instalado (loopback): abre o consentimento e devolve o refresh token."""
    import http.server
    import webbrowser

    cid, csec = segredo("youtube_client_id"), segredo("youtube_client_secret")
    estado = secrets.token_urlsafe(16)
    redir = f"http://127.0.0.1:{porta}/"
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(
        {"client_id": cid, "redirect_uri": redir, "response_type": "code", "scope": ESCOPO, "access_type": "offline",
         "prompt": "consent", "state": estado})
    recebido = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            recebido.update({k: v[0] for k, v in q.items()})
            self.send_response(200)
            self.end_headers()
            self.wfile.write("Autorizado. Pode fechar esta aba.".encode("utf-8"))

        def log_message(self, *a):
            pass

    print("Abra no navegador e autorize:\n" + url)
    webbrowser.open(url)
    with http.server.HTTPServer(("127.0.0.1", porta), H) as srv:
        srv.handle_request()
    if recebido.get("state") != estado or "code" not in recebido:
        raise SystemExit(f"autorização falhou: {recebido.get('error', 'resposta inválida')}")
    import requests

    r = requests.post(TOKEN_URL, data={"code": recebido["code"], "client_id": cid, "client_secret": csec,
                                       "redirect_uri": redir, "grant_type": "authorization_code"}, timeout=60).json()
    if "refresh_token" not in r:
        raise SystemExit(f"sem refresh token: {json.dumps(r)[:300]}")
    print("\nGuarde como variável de ambiente YT_REFRESH_TOKEN (não cole em arquivo do kit):\n" + r["refresh_token"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("autorizar")
    e = sub.add_parser("enviar")
    e.add_argument("--video", required=True)
    e.add_argument("--titulo", required=True)
    e.add_argument("--descricao", required=True, help="arquivo .txt")
    e.add_argument("--tags", default="")
    e.add_argument("--privacidade", choices=["private", "unlisted", "public"])
    e.add_argument("--publicar-em", help="ISO 8601 UTC, ex.: 2026-11-03T22:00:00Z")
    s = e.add_mutually_exclusive_group()
    s.add_argument("--sintetico", dest="sintetico", action="store_true", default=None)
    s.add_argument("--nao-sintetico", dest="sintetico", action="store_false")
    e.add_argument("--seco", action="store_true")
    a = ap.parse_args()
    if a.cmd == "autorizar":
        autorizar()
        return
    if not a.seco and not Path(a.video).is_file():
        raise SystemExit(f"vídeo não encontrado: {a.video}")
    desc = Path(a.descricao).read_text(encoding="utf-8").strip()
    tags = [t.strip() for t in a.tags.split(",") if t.strip()]
    enviar(a.video, a.titulo, desc, tags, a.privacidade, a.publicar_em, a.sintetico, a.seco)


if __name__ == "__main__":
    main()
