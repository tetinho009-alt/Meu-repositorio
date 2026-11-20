# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Manda o vídeo para a CAIXA DE ENTRADA (rascunho) do TikTok pela Content Posting API. O dono abre o app,
confere, escreve a legenda e publica.

Uso:
    python -m publicar.tiktok --video ep.mp4 [--seco]

Token: TIKTOK_ACCESS_TOKEN (OAuth do usuário com o escopo video.upload).

AVISO DE AUDITORIA: app próprio que não passou na auditoria do TikTok não publica direto ("Direct Post" sai só como
privado e com limites). O caminho realista e seguro é este: enviar para o rascunho e publicar no app. Se o seu app
for auditado, ainda assim mantenha 1 publicação por vez e nunca automatize curtida, seguida ou comentário.
"""
import argparse
import os
import time
from pathlib import Path

from config import CFG

from .http import Cliente, ErroAPI, token

TT = CFG["publicar"]["tiktok"]
MB = 1024 * 1024


def plano_de_partes(tam):
    """Partes do envio: arquivo até 64 MB vai inteiro; acima disso, partes de 10 MB (a última leva o resto)."""
    if tam <= 64 * MB:
        return tam, 1
    parte = 10 * MB
    return parte, tam // parte


def enviar(video, seco=False, espera_max_s=120):
    print(__doc__.split("AVISO DE AUDITORIA:")[1].strip().split("\n\n")[0].replace("\n", " "))
    tok = token("tiktok", seco)
    cli = Cliente(seco)
    base = TT["api"].rstrip("/")
    tam = os.path.getsize(video) if Path(video).exists() else 0
    parte, n = plano_de_partes(tam)
    cab = {"Authorization": f"Bearer {tok}", "Content-Type": "application/json; charset=UTF-8"}
    r, _ = cli.pedido("POST", f"{base}/v2/post/publish/inbox/video/init/", headers=cab,
                      json_={"source_info": {"source": "FILE_UPLOAD", "video_size": tam, "chunk_size": parte,
                                             "total_chunk_count": n}},
                      descricao="1/3 iniciar envio para o rascunho",
                      falso={"data": {"publish_id": "SECO_PUBLISH", "upload_url": "https://seco.invalid/upload"},
                             "error": {"code": "ok"}})
    if r.get("error", {}).get("code", "ok") != "ok":
        raise ErroAPI(f"init falhou: {r['error']}")
    dados = r["data"]
    with open(video, "rb") if not seco else _Vazio() as f:
        for k in range(n):
            ini = k * parte
            fim = tam - 1 if k == n - 1 else ini + parte - 1
            bloco = f.read(fim - ini + 1) if not seco else b""
            cli.pedido("PUT", dados["upload_url"], corpo=bloco if not seco else None,
                       headers={"Content-Type": "video/mp4", "Content-Range": f"bytes {ini}-{fim}/{tam}"},
                       descricao=f"2/3 enviar parte {k + 1}/{n}", ok=(200, 201, 206))
    inicio = time.time()
    while True:
        st, _ = cli.pedido("POST", f"{base}/v2/post/publish/status/fetch/", headers=cab,
                           json_={"publish_id": dados["publish_id"]}, descricao="3/3 status",
                           falso={"data": {"status": "SEND_TO_USER_INBOX"}, "error": {"code": "ok"}})
        estado = st.get("data", {}).get("status")
        print(f"status {estado}", flush=True)
        if estado in ("SEND_TO_USER_INBOX", "PUBLISH_COMPLETE"):
            break
        if estado == "FAILED":
            raise ErroAPI(f"falhou: {st}")
        if time.time() - inicio > espera_max_s:
            print("ainda processando; confira a caixa de entrada do app em alguns minutos")
            break
        time.sleep(5)
    print(("SECO_OK (nada foi enviado)" if seco else "NO_RASCUNHO") + ": abra o TikTok > caixa de entrada, revise e publique.")
    return dict(publish_id=dados["publish_id"], pedidos=cli.pedidos)


class _Vazio:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--video", required=True)
    ap.add_argument("--seco", action="store_true")
    a = ap.parse_args()
    if not Path(a.video).is_file():
        raise SystemExit(f"vídeo não encontrado: {a.video}")
    enviar(a.video, a.seco)


if __name__ == "__main__":
    main()
