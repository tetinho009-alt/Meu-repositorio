# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Publica um Reel pela Instagram Graph API (API do Instagram com login do Instagram): container -> envio ->
status até FINISHED -> publicar -> link.

Uso:
    python -m publicar.instagram --video ep.mp4 --legenda legenda.txt [--capa-url URL | --capa-ms 1500] [--seco]
    python -m publicar.instagram --video-url https://.../ep.mp4 --legenda legenda.txt [--seco]

- Arquivo local: envio "resumable" para rupload.facebook.com (não precisa hospedar o vídeo em lugar nenhum).
- URL pública: a própria API puxa o vídeo.
- Token: variável IG_ACCESS_TOKEN (token longo da conta profissional; permissão instagram_business_content_publish).
- Rótulo de IA (`publicar.instagram.rotulo_ia`): pede o selo "Informações de IA" (voz sintética realista conta).
  Se a API recusar o campo, o envio é refeito sem ele e o aviso manda marcar no app.
- Capa de Reel já publicado não muda pela API: escolha a capa antes (--capa-url ou --capa-ms).
"""
import argparse
import os
import time
from pathlib import Path

from config import CFG

from .http import Cliente, ErroAPI, token

IG = CFG["publicar"]["instagram"]
RUPLOAD = "https://rupload.facebook.com/ig-api-upload/{v}/{id}"


def publicar(video=None, video_url=None, legenda="", capa_url=None, capa_ms=None, rotulo_ia=None, seco=False,
             espera_max_s=600):
    tok = token("instagram", seco)
    cli = Cliente(seco)
    base = f"{IG['api'].rstrip('/')}/{IG['versao']}"
    rotulo_ia = IG.get("rotulo_ia", True) if rotulo_ia is None else rotulo_ia
    dados = {"media_type": "REELS", "caption": legenda, "share_to_feed": str(bool(IG.get("compartilhar_no_feed", True))).lower(),
             "access_token": tok}
    if video:
        dados["upload_type"] = "resumable"
    else:
        dados["video_url"] = video_url
    if capa_url:
        dados["cover_url"] = capa_url
    elif capa_ms is not None:
        dados["thumb_offset"] = str(int(capa_ms))
    if rotulo_ia:
        dados["is_ai_generated"] = "true"
    try:
        r, _ = cli.pedido("POST", f"{base}/me/media", data=dados, descricao="1/5 criar container do Reel",
                          falso={"id": "SECO_CONTAINER"})
    except ErroAPI as e:
        if rotulo_ia and "is_ai_generated" in str(e):
            print("AVISO: a API não aceitou o rótulo de IA; publicando sem ele. Marque 'Informações de IA' no app.")
            dados.pop("is_ai_generated")
            r, _ = cli.pedido("POST", f"{base}/me/media", data=dados, descricao="1/5 criar container (sem rótulo)")
        else:
            raise
    cid = r["id"]
    if video:
        tam = os.path.getsize(video) if Path(video).exists() else 0
        up, _ = cli.pedido("POST", RUPLOAD.format(v=IG["versao"], id=cid), corpo=str(video),
                           headers={"Authorization": f"OAuth {tok}", "offset": "0", "file_size": str(tam)},
                           descricao="2/5 enviar o arquivo (resumable)", falso={"success": True})
        if not up.get("success", False):
            raise ErroAPI(f"envio falhou: {up}")
    inicio = time.time()
    while True:
        st, _ = cli.pedido("GET", f"{base}/{cid}", params={"fields": "status_code,status", "access_token": tok},
                           descricao="3/5 status do processamento", falso={"status_code": "FINISHED"})
        cod = st.get("status_code")
        print(f"status {cod}", flush=True)
        if cod == "FINISHED":
            break
        if cod in ("ERROR", "EXPIRED"):
            raise ErroAPI(f"processamento falhou: {st}")
        if time.time() - inicio > espera_max_s:
            raise ErroAPI("tempo esgotado esperando FINISHED")
        time.sleep(10)
    pub, _ = cli.pedido("POST", f"{base}/me/media_publish", data={"creation_id": cid, "access_token": tok},
                        descricao="4/5 publicar", falso={"id": "SECO_MIDIA"})
    link, _ = cli.pedido("GET", f"{base}/{pub['id']}", params={"fields": "permalink", "access_token": tok},
                         descricao="5/5 link", falso={"permalink": "https://www.instagram.com/reel/SECO/"})
    print(("SECO_OK (nada foi enviado) " if seco else "PUBLICADO ") + link.get("permalink", ""))
    return dict(midia=pub["id"], permalink=link.get("permalink"), pedidos=cli.pedidos)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--video", help="arquivo mp4 local (envio resumable)")
    g.add_argument("--video-url", help="URL pública do mp4")
    ap.add_argument("--legenda", required=True, help="arquivo .txt com o texto do post")
    ap.add_argument("--capa-url")
    ap.add_argument("--capa-ms", type=int, help="quadro da capa em milissegundos")
    ap.add_argument("--sem-rotulo-ia", action="store_true")
    ap.add_argument("--seco", action="store_true", help="monta os pedidos e não envia nada")
    a = ap.parse_args()
    legenda = Path(a.legenda).read_text(encoding="utf-8").strip()
    if len(legenda) > 2200:
        raise SystemExit("legenda passa de 2.200 caracteres (limite do Instagram)")
    if a.video and not Path(a.video).is_file():
        raise SystemExit(f"vídeo não encontrado: {a.video}")
    publicar(a.video, a.video_url, legenda, a.capa_url, a.capa_ms, False if a.sem_rotulo_ia else None, a.seco)


if __name__ == "__main__":
    main()
