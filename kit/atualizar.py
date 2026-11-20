# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Atualizador do estúdio: baixa a versão nova no site e troca os arquivos do kit sem mexer no que é do usuário.

Uso, a partir de kit/:
    python atualizar.py            -> diz se há versão nova e se ela está liberada para esta licença
    python atualizar.py --aplicar  -> baixa, confere e instala (a versão de antes fica guardada em trabalho/versoes/)

O painel usa as mesmas funções: aviso ao abrir e o botão "Atualizar agora".

A versão nova só sai para licença ativa e dentro do prazo das atualizações (12 meses desde a compra, ou sem prazo com o
Atualizações para Sempre). Quem confere é o site (api/atualizacao.php), não este arquivo.

O que nunca é trocado: series/, canais/ e trabalho/, a licença e os arquivos que o usuário cria (DO_USUARIO). A pasta
canal/ e a marca da cópia (.tv/, LICENCA.txt) só ganham os arquivos que ainda não têm. Antes de trocar qualquer coisa, todo arquivo que vai mudar ou
sair vai para um ZIP em trabalho/versoes/; se algo falhar no meio, eles voltam para o lugar.
"""
import hashlib
import json
import os
import re
import shutil
import sys
import threading
import time
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

KIT = Path(__file__).resolve().parent
ESTUDIO = KIT.parent
if str(KIT) not in sys.path:
    sys.path.insert(0, str(KIT))

ENDPOINT = "https://temporadaviral.com/api/atualizacao.php"
OFERTA_PADRAO = "https://pay.cakto.com.br/5cg6255"
PREFIXO = "temporada-viral/"
MANIFESTO = "kit/arquivos.json"     # arquivos de cada versão, gravado pelo zipar_kit.py: permite apagar os que saíram
GUARDAR = 3                         # cópias de versões anteriores mantidas em trabalho/versoes/
CONFERIR_A_CADA = timedelta(hours=1)

# Arquivos do usuário: o mesmo conjunto do CRIADOS_PELO_USUARIO do montar.py (que confere os dois na montagem), mais o
# estado local do painel.
DO_USUARIO = {"kit/config.json", "kit/config_16x9.json", "kit/estilo.json", ".licenca.json", "canal/preferencias.json",
              "canal/pedidos.md", "canal/metricas.json", "canal/pronuncia.json", "painel.html", "canal/idv/marca.json",
              "painel.estado.json", "painel.log", "canal/novelinha/elenco.md"}
PASTAS_DO_USUARIO = ("series/", "canais/", "trabalho/", ".git/", "canal/novelinha/")
# Só entram se ainda não existem: os modelos do canal e a marca da cópia (.tv/ e LICENCA.txt, gravados pelo site no
# download). A marca de quem já tem fica como está a cada versão.
SO_SE_FALTAR = ("canal/", ".tv/", "LICENCA.txt")


class ErroAtualizacao(Exception):
    def __init__(self, mensagem, motivo="erro", extra=None):
        super().__init__(mensagem)
        self.motivo = motivo
        self.extra = extra or {}


def _lic():
    try:
        import licenca
        return licenca
    except BaseException:  # noqa: BLE001
        return None


def versao_local():
    try:
        return (ESTUDIO / "VERSAO").read_text(encoding="utf-8").strip() or "0"
    except OSError:
        return "0"


def _tupla(v):
    return tuple(int(x) for x in re.findall(r"\d+", str(v or "0"))) or (0,)


def _do_usuario(rel):
    return rel in DO_USUARIO or rel.startswith(PASTAS_DO_USUARIO) or "/__pycache__/" in "/" + rel


def _rel_seguro(rel):
    return bool(rel) and not rel.startswith("/") and "\\" not in rel and ":" not in rel \
        and ".." not in rel.split("/")


def na_nuvem():
    """Instalação feita pelo instalador da nuvem (pasta com .git): a versão nova chega por ele, não por aqui."""
    return (ESTUDIO / ".git").exists()


def _pasta_versoes():
    p = ESTUDIO / "trabalho" / "versoes"
    p.mkdir(parents=True, exist_ok=True)
    return p


# ---------------------------------------------------------------- andamento (o painel mostra a barra)

class Andamento:
    ETAPAS = {"baixando": "Baixando a versão nova", "conferindo": "Conferindo o arquivo",
              "guardando": "Guardando a versão de agora", "instalando": "Instalando",
              "pronto": "Pronto", "erro": "Não deu certo"}

    def __init__(self):
        self.trava = threading.Lock()
        self.dados = {"rodando": False}

    def comecar(self, versao):
        with self.trava:
            if self.dados.get("rodando"):
                return False
            self.dados = {"rodando": True, "versao": versao, "etapa": "baixando", "pct": 0, "msg": ""}
            return True

    def marcar(self, etapa, pct=None, msg=""):
        with self.trava:
            self.dados.update(etapa=etapa, texto=self.ETAPAS.get(etapa, etapa), msg=msg)
            if pct is not None:
                self.dados["pct"] = max(0, min(100, int(pct)))
            if etapa in ("pronto", "erro"):
                self.dados["rodando"] = False

    def copia(self):
        with self.trava:
            return dict(self.dados)


ANDAMENTO = Andamento()


def _nada(*_a, **_k):
    return None


# ---------------------------------------------------------------- situação

def conferir_no_site(forcar=False):
    """Pergunta ao site a última versão (pela mesma consulta da licença), no máximo uma vez por hora."""
    lic = _lic()
    if not lic:
        return
    try:
        # Marca própria (não a ultima_ok): a confirmação gravada por um kit antigo não traz a versão do site.
        ultima = lic._le().get("versao_conferida_em")
        recente = ultima and datetime.now(timezone.utc) - datetime.fromisoformat(ultima) < CONFERIR_A_CADA
    except (ValueError, TypeError):
        recente = False
    if forcar or not recente:
        try:
            lic.verifica(forcar=True)
        except Exception:  # noqa: BLE001
            pass


def estado(conferir=False, forcar=False):
    """Situação para o painel e para o terminal: versão instalada, versão nova (se houver) e se ela está liberada."""
    if conferir or forcar:
        conferir_no_site(forcar)
    lic = _lic()
    local = versao_local()
    v = lic.versao_site() if lic and hasattr(lic, "versao_site") else None
    c = lic.conta() if lic and hasattr(lic, "conta") else {}
    nova = None
    if v and _tupla(v.get("numero")) > _tupla(local):
        nova = {"numero": str(v["numero"]), "data": str(v.get("data") or ""),
                "novidades": [str(x) for x in (v.get("novidades") or [])][:8], "tamanho": int(v.get("tamanho") or 0)}
    return {"local": local, "nova": nova, "liberada": bool(nova and v.get("liberada")),
            "atualizacoes_ate": c.get("atualizacoes_ate"), "sempre": bool(c.get("atualizacoes_sempre")),
            "oferta": c.get("oferta_sempre") or OFERTA_PADRAO, "nuvem": na_nuvem(), "andamento": ANDAMENTO.copia()}


def _data_br(iso):
    try:
        return datetime.strptime(str(iso)[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return str(iso or "")


def aviso_texto():
    """Uma linha para a IA, depois do `python licenca.py`; vazio se não há versão nova."""
    e = estado()
    n = e["nova"]
    if not n:
        return ""
    if e["nuvem"]:
        return (f"VERSÃO NOVA: {n['numero']} já saiu (esta é a {e['local']}). Nesta instalação na nuvem, ela chega pelo "
                "instalador da Temporada Viral.")
    if not e["liberada"]:
        return (f"VERSÃO NOVA: {n['numero']} já saiu (esta é a {e['local']}), mas as atualizações grátis desta licença "
                f"terminaram em {_data_br(e['atualizacoes_ate'])}. Conte ao usuário, sem insistir, que com o "
                f"Atualizações para Sempre ela e as próximas chegam sem prazo: {e['oferta']}")
    novidades = "; ".join(n["novidades"][:4])
    return (f"VERSÃO NOVA DISPONÍVEL: {n['numero']} (esta é a {e['local']})."
            + (f" Novidades: {novidades}." if novidades else "")
            + " Pergunte ao usuário se pode atualizar agora (leva uns 2 minutos e não mexe nos canais, séries e "
              "vídeos dele). Se ele disser sim, rode `python atualizar.py --aplicar` a partir de kit/.")


# ---------------------------------------------------------------- download

def baixar(versao, progresso=_nada):
    """Baixa o ZIP da versão em trabalho/versoes/ e confere tamanho e SHA-256. Devolve o caminho."""
    lic = _lic()
    email = lic.email_compra() if lic and hasattr(lic, "email_compra") else ""
    if not email:
        raise ErroAtualizacao("O estúdio ainda não foi ativado com o e-mail da compra.", "licenca")
    corpo = json.dumps({"email": email, "maquina": lic.maquina() or ""}).encode("utf-8")
    pedido = urllib.request.Request(ENDPOINT, data=corpo, method="POST",
                                    headers={"Content-Type": "application/json", "User-Agent": "temporada-viral-kit"})
    destino = _pasta_versoes() / f"temporada-viral-v{versao}.zip"
    parcial = destino.with_suffix(".parcial")
    try:
        with urllib.request.urlopen(pedido, timeout=60) as r:
            if "json" in (r.headers.get("Content-Type") or ""):
                j = json.loads(r.read().decode("utf-8"))
                raise ErroAtualizacao(str(j.get("mensagem") or "O site recusou o download."), str(j.get("motivo") or ""))
            total = int(r.headers.get("Content-Length") or 0)
            esperado = (r.headers.get("X-Sha256") or "").strip().lower()
            if (r.headers.get("X-Versao") or "").strip() != versao:
                raise ErroAtualizacao("O site mandou outra versão. Tente de novo em alguns minutos.", "versao")
            h, feito = hashlib.sha256(), 0
            with open(parcial, "wb") as f:
                while True:
                    bloco = r.read(256 * 1024)
                    if not bloco:
                        break
                    f.write(bloco)
                    h.update(bloco)
                    feito += len(bloco)
                    if total:
                        progresso("baixando", feito * 100 / total)
    except urllib.error.HTTPError as e:
        try:
            j = json.loads(e.read().decode("utf-8"))
        except (ValueError, OSError):
            j = {}
        raise ErroAtualizacao(str(j.get("mensagem") or f"O site recusou o download (erro {e.code})."),
                              str(j.get("motivo") or e.code), {k: j[k] for k in ("oferta_sempre", "atualizacoes_ate")
                                                               if j.get(k)}) from None
    except (OSError, ValueError) as e:
        parcial.unlink(missing_ok=True)
        if isinstance(e, ErroAtualizacao):
            raise
        raise ErroAtualizacao("A internet caiu no meio do download. Tente de novo.", "rede") from None
    progresso("conferindo", 100)
    if (total and feito != total) or (esperado and h.hexdigest() != esperado):
        parcial.unlink(missing_ok=True)
        raise ErroAtualizacao("O arquivo chegou incompleto. Tente de novo.", "integridade")
    os.replace(parcial, destino)
    return destino


# ---------------------------------------------------------------- instalação

def _sha_arquivo(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for bloco in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloco)
    return h.hexdigest()


def _igual(destino, z, info):
    try:
        if destino.stat().st_size != info.file_size:
            return False
    except OSError:
        return False
    h = hashlib.sha256()
    with z.open(info) as f:
        for bloco in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloco)
    return h.hexdigest() == _sha_arquivo(destino)


def _manifesto(z=None, itens=None):
    """Lista de arquivos de uma versão: do ZIP novo (z, itens) ou da instalação atual."""
    try:
        bruto = z.read(itens[MANIFESTO]) if z else (ESTUDIO / MANIFESTO).read_bytes()
        lista = json.loads(bruto.decode("utf-8")).get("arquivos")
        return {str(x) for x in lista} if isinstance(lista, list) else set()
    except (KeyError, OSError, ValueError, AttributeError):
        return set()


def _trocar(tmp, destino):
    # No Windows, um arquivo aberto (vídeo tocando no painel) recusa a troca por um instante.
    for tentativa in range(6):
        try:
            os.replace(tmp, destino)
            return
        except PermissionError:
            if tentativa == 5:
                raise
            time.sleep(0.5)


def _restaurar(copia, criados):
    """Põe de volta os arquivos guardados. Pula os que nem chegaram a mudar (o arquivo travado que parou a
    instalação, por exemplo) e só desiste se algum que mudou não puder voltar."""
    falhas = []
    with zipfile.ZipFile(copia) as b:
        for info in b.infolist():
            if info.filename.startswith("_") or not _rel_seguro(info.filename):
                continue
            destino = ESTUDIO / info.filename
            if destino.is_file() and _igual(destino, b, info):
                continue
            try:
                destino.parent.mkdir(parents=True, exist_ok=True)
                tmp = destino.with_name(destino.name + ".volta")
                with b.open(info) as src, open(tmp, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                _trocar(tmp, destino)
            except OSError:
                falhas.append(info.filename)
    for rel in criados:
        (ESTUDIO / rel).unlink(missing_ok=True)
    if falhas:
        raise OSError("não voltaram: " + ", ".join(falhas[:5]))


def instalar(zip_path, versao=None, progresso=_nada):
    """Troca os arquivos do kit pelos do ZIP. Devolve {"versao", "trocados", "apagados", "copia"}."""
    with zipfile.ZipFile(zip_path) as z:
        itens = {}
        for info in z.infolist():
            if info.is_dir() or not info.filename.startswith(PREFIXO):
                continue  # CLAUDE.md e AGENTS.md da pasta de fora ficam de fora
            rel = info.filename[len(PREFIXO):]
            if not _rel_seguro(rel):
                raise ErroAtualizacao("O arquivo da versão nova veio estranho. Nada foi trocado.", "zip")
            itens[rel] = info
        if not {"VERSAO", "CLAUDE.md", "kit/licenca.py"} <= set(itens):
            raise ErroAtualizacao("O arquivo da versão nova veio incompleto. Nada foi trocado.", "zip")
        nova = z.read(itens["VERSAO"]).decode("utf-8").strip()
        if versao and nova != versao:
            raise ErroAtualizacao("O arquivo não é da versão esperada. Nada foi trocado.", "versao")
        antes = versao_local()
        if _tupla(nova) <= _tupla(antes):
            raise ErroAtualizacao(f"O estúdio já está na versão {antes}.", "em_dia")

        escrever = []
        for rel, info in itens.items():
            destino = ESTUDIO / rel
            if _do_usuario(rel) or (rel.startswith(SO_SE_FALTAR) and destino.exists()) or _igual(destino, z, info):
                continue
            escrever.append((rel, info))
        # VERSAO por último: se algo parar no meio, o estúdio não diz que já está na versão nova.
        escrever.sort(key=lambda x: x[0] == "VERSAO")
        apagar = sorted(rel for rel in _manifesto() - set(itens)
                        if not _do_usuario(rel) and not rel.startswith(SO_SE_FALTAR) and (ESTUDIO / rel).is_file())

        progresso("guardando", 0)
        copia = _pasta_versoes() / f"antes-da-v{nova}-{datetime.now():%Y%m%d-%H%M%S}.zip"
        with zipfile.ZipFile(copia, "w", zipfile.ZIP_DEFLATED) as b:
            for rel in [r for r, _ in escrever] + apagar:
                if (ESTUDIO / rel).is_file():
                    b.write(ESTUDIO / rel, rel)
            b.writestr("_versao_anterior.txt", antes)

        criados = []
        try:
            for i, (rel, info) in enumerate(escrever, 1):
                destino = ESTUDIO / rel
                existia = destino.exists()
                destino.parent.mkdir(parents=True, exist_ok=True)
                tmp = destino.with_name(destino.name + ".novo")
                with z.open(info) as src, open(tmp, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                modo = (info.external_attr >> 16) & 0o777
                if os.name != "nt" and modo:
                    os.chmod(tmp, modo)
                _trocar(tmp, destino)
                if not existia:
                    criados.append(rel)
                progresso("instalando", i * 100 / max(1, len(escrever)))
            for rel in apagar:
                (ESTUDIO / rel).unlink(missing_ok=True)
        except Exception as e:  # noqa: BLE001
            try:
                _restaurar(copia, criados)
            except Exception:  # noqa: BLE001
                raise ErroAtualizacao(f"A instalação parou ({type(e).__name__}) e não consegui desfazer sozinho. A "
                                      f"versão de antes está em trabalho/versoes/{copia.name}: peça ajuda no suporte.",
                                      "restaurar") from e
            raise ErroAtualizacao(f"A instalação parou ({type(e).__name__}: {e}). Voltei tudo para a versão {antes}.",
                                  "instalar") from e

    for velha in sorted(_pasta_versoes().glob("antes-da-v*.zip"), key=lambda p: p.stat().st_mtime)[:-GUARDAR]:
        velha.unlink(missing_ok=True)
    return {"versao": nova, "anterior": antes, "trocados": len(escrever), "apagados": len(apagar), "copia": copia.name}


def aplicar(progresso=None):
    """Confere, baixa e instala a versão nova. Devolve {"ok", "msg", ...}; o andamento fica em ANDAMENTO."""
    # Pedido explícito: pergunta ao site agora (quem acabou de comprar o Atualizações para Sempre já é liberado).
    e = estado(forcar=True)
    n = e["nova"]
    if not n:
        return {"ok": False, "motivo": "em_dia", "msg": f"O estúdio já está na versão mais nova ({e['local']})."}
    if e["nuvem"]:
        return {"ok": False, "motivo": "nuvem", "msg": "Nesta instalação na nuvem, a versão nova chega pelo instalador."}
    if not e["liberada"]:
        return {"ok": False, "motivo": "prazo", "oferta": e["oferta"],
                "msg": f"As atualizações grátis desta licença terminaram em {_data_br(e['atualizacoes_ate'])}. Com o "
                       "Atualizações para Sempre, esta e as próximas versões chegam sem prazo."}
    if not ANDAMENTO.comecar(n["numero"]):
        return {"ok": False, "motivo": "rodando", "msg": "A atualização já está em andamento."}

    def marcar(etapa, pct=None, msg=""):
        ANDAMENTO.marcar(etapa, pct, msg)
        if progresso:
            progresso(etapa, pct)

    try:
        arquivo = baixar(n["numero"], marcar)
        r = instalar(arquivo, n["numero"], marcar)
        arquivo.unlink(missing_ok=True)
    except ErroAtualizacao as erro:
        ANDAMENTO.marcar("erro", msg=str(erro))
        return {"ok": False, "motivo": erro.motivo, "msg": str(erro), **erro.extra}
    except Exception as erro:  # noqa: BLE001
        ANDAMENTO.marcar("erro", msg=f"Erro inesperado ({type(erro).__name__}). Nada foi perdido: tente de novo.")
        return {"ok": False, "motivo": "erro", "msg": ANDAMENTO.copia()["msg"]}
    ANDAMENTO.marcar("pronto", 100, f"Atualizado para a versão {r['versao']}.")
    return {"ok": True, "msg": f"Atualizado para a versão {r['versao']}.", **r}


def _saida_utf8():
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def main():
    _saida_utf8()
    lic = _lic()
    if lic:
        lic.exigir()
    if "--aplicar" not in sys.argv[1:]:
        e = estado(conferir=True)
        print(aviso_texto() or f"O estúdio está na versão mais nova ({e['local']}).")
        return 0
    ultimo = [""]

    def mostrar(etapa, pct):
        linha = f"{Andamento.ETAPAS.get(etapa, etapa)}..." + (f" {int(pct)}%" if pct is not None else "")
        if etapa != ultimo[0] or (pct is not None and int(pct) % 20 == 0):
            print(linha, flush=True)
            ultimo[0] = etapa

    r = aplicar(mostrar)
    if r["ok"]:
        print(f"PRONTO: {r['msg']} A versão de antes ficou guardada em trabalho/versoes/{r['copia']}. "
              "Se o painel estiver aberto, feche e abra de novo pelo ícone.")
        return 0
    print(f"ERRO: {r['msg']}")
    if r.get("motivo") == "prazo":
        print(f"O QUE FAZER: para continuar recebendo as versões novas, o Atualizações para Sempre: {r.get('oferta')}")
    elif r.get("motivo") not in ("em_dia",):
        print("O QUE FAZER: confira a internet e rode de novo. Seu estúdio continua funcionando na versão de agora.")
    return 0 if r.get("motivo") == "em_dia" else 1


if __name__ == "__main__":
    sys.exit(main())
