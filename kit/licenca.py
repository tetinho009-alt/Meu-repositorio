# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Licença do estúdio: confere no temporadaviral.com se o e-mail da compra ainda tem acesso.

A licença é pessoal e fica ligada ao e-mail usado na compra. Reembolso ou chargeback cancelam a licença, e o kit
deixa de funcionar (LICENCA_E_TERMOS.md, seção 6). Remover ou contornar esta verificação viola a licença.

Uso, a partir de kit/:
    python licenca.py seu-email-de-compra@exemplo.com   -> ativa
    python licenca.py                                   -> confere de novo e mostra a situação

Os outros scripts chamam `exigir()` (via config.py e no render). A confirmação fica em `.licenca.json`, na raiz do
estúdio, e é refeita a cada 12 horas. Sem internet, vale a última confirmação por até 10 dias.
"""
import json
import sys
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

ENDPOINT = "https://temporadaviral.com/api/licenca.php"
ARQUIVO = Path(__file__).resolve().parent.parent / ".licenca.json"
REVALIDA = timedelta(hours=12)
TOLERANCIA_OFFLINE = timedelta(days=10)

MSG_ATIVAR = ("O estúdio ainda não foi ativado. Rode, a partir de kit/:\n"
              "    python licenca.py SEU-EMAIL-DA-COMPRA\n"
              "(o mesmo e-mail que você usou para comprar na Cakto).")
MSG_INATIVA = ("A licença deste e-mail não está ativa. Sem licença ativa, o uso do kit não é autorizado "
               "(LICENCA_E_TERMOS.md). Se você comprou e está vendo isto por engano, escreva para "
               "contato@temporadaviral.com com o e-mail da compra.")


def _agora():
    return datetime.now(timezone.utc)


def _le():
    try:
        return json.loads(ARQUIVO.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _grava(dados):
    ARQUIVO.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def _consulta(email, maquina):
    """(True/False, mensagem do site, plano) pela resposta; (None, "", None) se não deu para falar com ele."""
    corpo = json.dumps({"email": email, "maquina": maquina}).encode("utf-8")
    pedido = urllib.request.Request(ENDPOINT, data=corpo, method="POST",
                                    headers={"Content-Type": "application/json", "User-Agent": "temporada-viral-kit"})
    try:
        with urllib.request.urlopen(pedido, timeout=15) as r:
            resposta = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return (False, "E-mail inválido.", None) if e.code == 400 else (None, "", None)
    except (OSError, ValueError):
        return None, "", None
    _CONTA.clear()
    _CONTA.update({k: resposta[k] for k in ("desde", "atualizacoes_ate", "atualizacoes_sempre", "oferta_sempre", "suporte",
                                            "versao") if resposta.get(k)})
    return bool(resposta.get("ok")), str(resposta.get("mensagem") or ""), resposta.get("plano")


_CONTA = {}   # o que o site devolve além do ok: início da licença, prazo das atualizações e contato do suporte


def verifica(forcar=False):
    """(ativa, mensagem). Usa a confirmação guardada enquanto ela for recente."""
    dados = _le()
    email = dados.get("email")
    if not email:
        return False, MSG_ATIVAR
    ultima = dados.get("ultima_ok")
    ultima = datetime.fromisoformat(ultima) if ultima else None
    if not forcar and ultima and _agora() - ultima < REVALIDA:
        return True, ""
    dados.setdefault("maquina", uuid.uuid4().hex)
    ok, mensagem, plano_site = _consulta(email, dados["maquina"])
    if ok is None:
        _grava(dados)
        if ultima and _agora() - ultima < TOLERANCIA_OFFLINE:
            return True, "Sem conexão com o site: vale a última confirmação da licença."
        return False, "Não consegui confirmar a licença. Confira a internet e tente de novo."
    if not ok:
        dados.pop("ultima_ok", None)
        _grava(dados)
        return False, mensagem or MSG_INATIVA
    dados["ultima_ok"] = dados["versao_conferida_em"] = _agora().isoformat()
    dados["plano"] = str(plano_site or dados.get("plano") or "padrao")
    # A resposta nova substitui a anterior inteira: quem passou a ter atualizações sem prazo perde o prazo guardado.
    for k in ("atualizacoes_ate", "atualizacoes_sempre", "oferta_sempre", "versao"):
        dados.pop(k, None)
    dados.update(_CONTA)
    _grava(dados)
    return True, ""


def versao_site():
    """Última versão publicada que o site informou na última confirmação: {numero, data, tamanho, sha256, novidades,
    liberada} ou None. Não consulta o site."""
    v = _le().get("versao")
    return v if isinstance(v, dict) and v.get("numero") else None


def email_compra():
    """E-mail da compra, só para o atualizador pedir o download no site (nunca vai para log nem para a tela)."""
    return _le().get("email") or ""


def _saida_utf8():
    # No Windows a saída redirecionada sai em cp1252 e a IA lê os acentos quebrados.
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def plano():
    """Plano da licença ("padrao" para tudo o que já foi vendido). Reservado para planos futuros: hoje não limita nada."""
    return _le().get("plano") or "padrao"


def maquina():
    """Identificador desta instalação (o mesmo que a licença usa); nenhum segredo novo é criado."""
    return _le().get("maquina")


SUPORTE_PADRAO = {"telegram": "https://temporadaviral.com/telegram", "email": "contato@temporadaviral.com",
                  "resposta": "em até 12 horas, do meio-dia à meia-noite"}


def marca_copia():
    """Marca que o site grava em cada cópia baixada (.tv/marca.json): código da compra, e-mail já mascarado, data e
    versão. None numa cópia sem marca (baixada antes da marca existir): aí nada muda."""
    try:
        m = json.loads((ARQUIVO.parent / ".tv" / "marca.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(m, dict) or not m.get("codigo"):
        return None
    return {k: str(m.get(k) or "")[:80] for k in ("codigo", "email_mascarado", "data", "versao")}


def conta():
    """Resumo para o painel: licença ativa, e-mail da compra mascarado, início, prazo das atualizações e suporte.
    Lê a última confirmação guardada (não consulta o site)."""
    d = _le()
    email = d.get("email") or ""
    usuario, _, dominio = email.partition("@")
    mascarado = (usuario[:2] + "•" * max(1, len(usuario) - 2) + "@" + dominio) if dominio else ""
    return {"ativa": bool(d.get("ultima_ok")), "email": mascarado, "desde": d.get("desde"),
            "atualizacoes_ate": d.get("atualizacoes_ate"), "atualizacoes_sempre": bool(d.get("atualizacoes_sempre")),
            "oferta_sempre": d.get("oferta_sempre"), "suporte": {**SUPORTE_PADRAO, **(d.get("suporte") or {})},
            "copia": marca_copia()}


def exigir():
    """Para o script com a explicação se a licença não estiver ativa."""
    ativa, mensagem = verifica()
    if not ativa:
        _saida_utf8()
        raise SystemExit(f"\nTemporada Viral, licença: {mensagem}\n")


def ativar(email):
    email = email.strip().lower()
    dados = _le()
    if dados.get("email") != email:
        dados = {"email": email, "maquina": dados.get("maquina") or uuid.uuid4().hex}
        _grava(dados)
    return verifica(forcar=True)


if __name__ == "__main__":
    _saida_utf8()
    ativa, mensagem = ativar(sys.argv[1]) if len(sys.argv) > 1 else verifica(forcar=True)
    print(f"Licença ativa. {mensagem}".strip() if ativa else f"LICENÇA INATIVA: {mensagem}")
    if ativa:
        # Versão nova no site: a IA pergunta ao usuário se pode atualizar (CLAUDE.md, "Licença: confira antes de tudo").
        try:
            import atualizar
            aviso = atualizar.aviso_texto()
        except Exception:  # noqa: BLE001
            aviso = ""
        if aviso:
            print(aviso)
    sys.exit(0 if ativa else 1)
