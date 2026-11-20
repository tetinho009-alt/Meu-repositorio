# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Token longo do Instagram (60 dias): usa o salvo e renova antes de vencer, como o placar real faz no servidor.

    python -m publicar.ig_token --status      # dias desde a última renovação (nunca mostra o token)
    python -m publicar.ig_token --renovar     # renova agora e grava no arquivo de segredos

A renovação (`refresh_access_token`, grant `ig_refresh_token`) só funciona com o token ainda válido e com mais de
24 h. O token novo é gravado no arquivo de segredos (`segredos.arquivo`, FORA da pasta do kit). Se a chave estiver só
em variável de ambiente, o kit não tem onde gravar: ele avisa a partir de `publicar.instagram.renovar_dias` e você
gera outro token no painel da Meta (`comandos/conectar-redes.md`).
"""
import argparse
import hashlib
import json
import time

from config import CFG, caminho, pasta, segredo

from .http import AUSENTE, Cliente, token

IG = CFG["publicar"]["instagram"]


def _estado_arq():
    return pasta("trabalho") / ".ig_token_estado.json"


def _impressao(tok):
    return hashlib.sha256(tok.encode()).hexdigest()[:16]


def _estado(tok):
    arq = _estado_arq()
    est = json.loads(arq.read_text(encoding="utf-8")) if arq.is_file() else {}
    if est.get("impressao") != _impressao(tok):  # token novo (gerado no painel): conta a partir de agora
        est = {"impressao": _impressao(tok), "renovado_em": time.time()}
        arq.write_text(json.dumps(est), encoding="utf-8")
    return est


def _grava_no_arquivo(novo):
    """Grava no arquivo de segredos. Devolve False se não houver arquivo configurado."""
    if not CFG["segredos"].get("arquivo"):
        return False
    arq = caminho(CFG["segredos"]["arquivo"])
    dados = json.loads(arq.read_text(encoding="utf-8")) if arq.is_file() else {}
    dados["IG_ACCESS_TOKEN"] = novo
    arq.parent.mkdir(parents=True, exist_ok=True)
    arq.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    return True


def renovar(tok, forcar=False):
    """Renova se passou de `renovar_dias`. Devolve o token em uso (o novo, se renovou e conseguiu gravar)."""
    est = _estado(tok)
    dias = (time.time() - est["renovado_em"]) / 86400
    limite = float(IG.get("renovar_dias", 45))
    if not forcar and dias < limite:
        return tok
    if not CFG["segredos"].get("arquivo"):
        print(f"AVISO: o token do Instagram tem {dias:.0f} dias (vence com 60). Gere outro no painel da Meta ou "
              "configure segredos.arquivo para o kit renovar sozinho.", flush=True)
        return tok
    r, _ = Cliente().pedido("GET", f"{IG['api'].rstrip('/')}/refresh_access_token",
                            params={"grant_type": "ig_refresh_token", "access_token": tok},
                            descricao="renovar o token do Instagram")
    novo = r.get("access_token")
    if not novo:
        print("AVISO: a Meta não devolveu token novo; o atual continua valendo até vencer.", flush=True)
        return tok
    _grava_no_arquivo(novo)
    _estado_arq().write_text(json.dumps({"impressao": _impressao(novo), "renovado_em": time.time()}), encoding="utf-8")
    print("token do Instagram renovado e gravado no arquivo de segredos", flush=True)
    return novo


def token_instagram(seco=False):
    """Token pronto para usar: renovado quando precisa. No seco, não renova nem exige o token."""
    tok = token("instagram", seco)
    if seco or tok == AUSENTE:
        return tok
    return renovar(tok)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--status", action="store_true")
    g.add_argument("--renovar", action="store_true")
    a = ap.parse_args()
    tok = segredo("instagram")
    if a.status:
        dias = (time.time() - _estado(tok)["renovado_em"]) / 86400
        print(f"token do Instagram: {dias:.1f} dias desde a última renovação (renova com "
              f"{IG.get('renovar_dias', 45)}; vence com 60)")
    else:
        renovar(tok, forcar=True)


if __name__ == "__main__":
    main()
