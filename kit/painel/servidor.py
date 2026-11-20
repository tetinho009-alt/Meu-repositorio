# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Painel do Temporada Viral: a parte visual do estúdio, aberta no navegador, só neste computador.

O painel mostra o que a IA fez (vídeos, capas, legendas, status) e facilita os ajustes do canal. Toda mudança de
vídeo continua sendo pedida no chat da IA. Só usa a biblioteca padrão do Python.

Uso, a partir da pasta do estúdio:
    python kit/painel/servidor.py                 # abre o painel no navegador e mostra o link
    python kit/painel/servidor.py --sem-navegador # só mostra o link (a IA usa assim)
    python kit/painel/servidor.py --estatico      # grava painel.html na pasta do estúdio, só para ver (nuvem/celular)

Segurança: escuta só em 127.0.0.1, numa porta livre sorteada, e cada pedido precisa do código do link (depois ele
fica num cookie desta sessão). A licença é conferida no servidor antes de qualquer página ou ação.

O caminho normal é o ícone "Temporada Viral" (kit/painel/atalho.py): roda sem janela preta e, se o painel já estiver
aberto, só abre o navegador de novo. A página manda um sinal de vida (POST /api/vivo a cada 20 s); sem nenhum pedido
por 3 minutos (e sem IA trabalhando), o painel se fecha sozinho. Erros vão para trabalho/painel.log, sem código de
acesso, chave nem e-mail completo.
"""
import argparse
import base64
import html
import json
import logging
import logging.handlers
import os
import re
import secrets
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PAINEL = Path(__file__).resolve().parent
if str(PAINEL) not in sys.path:
    sys.path.insert(0, str(PAINEL))

import arroba  # noqa: E402
import dados  # noqa: E402
import estilo_proprio  # noqa: E402
import estudo_painel  # noqa: E402
import ia  # noqa: E402
from dados import CANAL, ESTUDIO, KIT  # noqa: E402

LOG = logging.getLogger("painel")
OCIOSO_S = 180          # sem nenhum pedido por 3 min (aba fechada), o painel se fecha
GRACA_INICIAL_S = 600   # antes da primeira visita: tempo para a pessoa abrir o link

ESTATICO = PAINEL / "estatico"
ARQ_FONTE = KIT / "fontes" / "Anton-Regular.ttf"
SITE = "https://temporadaviral.com"
MAX_CORPO = 6 * 1024 * 1024
MAX_IMAGEM = 5 * 1024 * 1024
# Tudo o que está em estatico/ (subpastas incluídas: fontes/, vendor/, marca/, ilustracoes/), só com extensão conhecida
# e sem sair da pasta. index.html não sai por aqui: a página vai pelo html_app, com o código de acesso.
TIPOS_ESTATICOS = {".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".png": "image/png",
                   ".webp": "image/webp", ".apng": "image/apng", ".jpg": "image/jpeg", ".svg": "image/svg+xml", ".woff2": "font/woff2"}
# O visual das páginas de entrada (código de acesso e licença) sai sem código e sem licença: só a folha de estilo,
# as letras, as imagens da marca e o acesso.js. O painel.js e o resto continuam atrás dos dois portões.
PUBLICOS = ("painel.css", "acesso.js", "fontes/", "marca/", "ilustracoes/", "favicon-48.png", "icone-256.png",
            "apple-touch-icon.png", "favicon.svg", "mascote.png")
VALIDADE_CODIGO_S = 7 * 24 * 3600   # o código de acesso vale entre aberturas e troca a cada 7 dias


def arquivo_estatico(nome):
    try:
        raiz = ESTATICO.resolve()
        p = (raiz / nome).resolve()
        p.relative_to(raiz)
    except (ValueError, OSError):
        return None, None
    tipo = TIPOS_ESTATICOS.get(p.suffix.lower())
    if not tipo or p.name == "index.html" or not p.is_file():
        return None, None
    return p, tipo


def estatico_publico(nome):
    return ".." not in nome and any(nome == x or (x.endswith("/") and nome.startswith(x)) for x in PUBLICOS)


def arquivo_estatico(nome):
    try:
        raiz = ESTATICO.resolve()
        p = (raiz / nome).resolve()
        p.relative_to(raiz)
    except (ValueError, OSError):
        return None, None
    tipo = TIPOS_ESTATICOS.get(p.suffix.lower())
    if not tipo or p.name == "index.html" or not p.is_file():
        return None, None
    return p, tipo


# Ícones da marca, os mesmos do site (assets/marca): favicon de 48 px, ícone de 256 px e o do iPhone.
ICONES_MARCA = (("/static/favicon-48.png", "favicon-48.png"), ("/static/icone-256.png", "icone-256.png"),
                ("/static/apple-touch-icon.png", "apple-touch-icon.png"))
CSP = ("default-src 'self'; img-src 'self' data: blob:; media-src 'self'; style-src 'self' 'unsafe-inline'; "
       "font-src 'self' data:; script-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; "
       "form-action 'self'")


def _utf8():
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


class _Mascara(logging.Filter):
    """Nada de código de acesso, chave ou e-mail completo no arquivo de log."""

    def filter(self, registro):
        registro.msg = ia.mascarar(registro.getMessage())
        registro.args = ()
        if registro.exc_info:
            registro.exc_text = ia.mascarar(logging.Formatter().formatException(registro.exc_info))
            registro.exc_info = None
        return True


def configurar_log():
    """trabalho/painel.log (até ~2 x 256 KB). Sem a pasta de trabalho, o log fica desligado."""
    if LOG.handlers:
        return
    LOG.setLevel(logging.INFO)
    LOG.propagate = False
    try:
        pasta = dados.trabalho()
        pasta.mkdir(parents=True, exist_ok=True)
        h = logging.handlers.RotatingFileHandler(pasta / "painel.log", maxBytes=256 * 1024, backupCount=1,
                                                 encoding="utf-8")
    except OSError:
        LOG.addHandler(logging.NullHandler())
        return
    h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S"))
    h.addFilter(_Mascara())
    LOG.addHandler(h)


def _dizer(*partes, **kw):
    """print que não quebra sem console (pythonw: sys.stdout é None)."""
    if sys.stdout is not None:
        try:
            print(*partes, **kw)
        except (OSError, ValueError):
            pass


# ---------------------------------------------------------------- vida do servidor (desligar sozinho)

class Vida:
    def __init__(self):
        self.trava = threading.Lock()
        self.inicio = time.time()
        self.ultimo = 0.0

    def tocar(self):
        with self.trava:
            self.ultimo = time.time()

    def ocioso(self):
        """Segundos sem uso, ou None se ainda está no prazo."""
        if ia.ocupado() or estudo_painel.TRABALHO.rodando:
            self.tocar()
            return None
        with self.trava:
            agora = time.time()
            if not self.ultimo:
                return agora - self.inicio if agora - self.inicio > GRACA_INICIAL_S else None
            return agora - self.ultimo if agora - self.ultimo > OCIOSO_S else None


VIDA = Vida()


def arquivo_aberto():
    """Porta e código do painel aberto: na pasta de trabalho do kit (fora do pacote), nunca no log."""
    return dados.trabalho() / "painel.estado.json"


def painel_ja_aberto():
    """URL do painel que já está rodando neste estúdio, ou None."""
    info = dados.ler_json(arquivo_aberto(), {}) or {}
    porta, token = info.get("porta"), str(info.get("token") or "")
    if not isinstance(porta, int) or not token:
        return None
    try:
        pedido = urllib.request.Request(f"http://127.0.0.1:{porta}/api/ping", headers={"X-Painel-Token": token})
        with urllib.request.urlopen(pedido, timeout=3) as r:
            if json.loads(r.read().decode("utf-8")).get("app") == "painel-temporada-viral":
                return f"http://127.0.0.1:{porta}/?t={token}"
    except Exception:  # noqa: BLE001
        return None
    return None


def arquivo_codigo():
    """Código de acesso guardado entre aberturas (pasta de trabalho, fora do pacote): {token, criado, porta}."""
    return dados.trabalho() / "painel.codigo.json"


def codigo_guardado():
    """(token, porta preferida, segundos que ainda vale, info). Passados 7 dias, gera outro."""
    info = dados.ler_json(arquivo_codigo(), {}) or {}
    token, porta = str(info.get("token") or ""), info.get("porta")
    try:
        idade = time.time() - float(info.get("criado") or 0)
    except (TypeError, ValueError):
        idade = VALIDADE_CODIGO_S
    if len(token) < 24 or idade >= VALIDADE_CODIGO_S:
        token, idade = secrets.token_urlsafe(24), 0
        info = {"token": token, "criado": time.time()}
    return token, porta if isinstance(porta, int) else 0, int(VALIDADE_CODIGO_S - idade), info


def _gravar_privado(destino, texto, nome):
    """Grava trocando o arquivo de uma vez. No Windows, o replace falha se outro processo lê o arquivo naquele
    instante (antivírus, OneDrive, o outro painel): tenta de novo algumas vezes antes de desistir."""
    erro = None
    for _ in range(6):
        try:
            destino.parent.mkdir(parents=True, exist_ok=True)
            tmp = destino.with_suffix(".tmp")
            tmp.write_text(texto, encoding="utf-8")
            if os.name != "nt":
                os.chmod(tmp, 0o600)
            tmp.replace(destino)
            return True
        except OSError as e:
            erro = e
            time.sleep(0.25)
    LOG.warning("não gravei %s (%s)", nome, type(erro).__name__)
    return False


def gravar_codigo(info):
    _gravar_privado(arquivo_codigo(), json.dumps(info), "o código do painel")


def gravar_aberto(porta, token):
    _gravar_privado(arquivo_aberto(), json.dumps({"porta": porta, "token": token, "pid": os.getpid(),
                                                  "desde": datetime.now().isoformat(timespec="seconds")}),
                    "o arquivo do painel aberto")


def apagar_aberto(token):
    try:
        info = dados.ler_json(arquivo_aberto(), {}) or {}
        if info.get("token") == token:
            arquivo_aberto().unlink()
    except OSError:
        pass


def vigiar(srv):
    while True:
        time.sleep(15)
        parado = VIDA.ocioso()
        if parado is not None:
            LOG.info("painel fechado sozinho depois de %d s sem uso", int(parado))
            srv.shutdown()
            return


# ---------------------------------------------------------------- licença (só no servidor)

class Licenca:
    """Guarda o resultado de licenca.verifica() por alguns minutos para não consultar a cada pedido.
    A própria licença do kit já guarda a confirmação do site por 12 h e tolera 10 dias sem internet."""

    def __init__(self):
        self.trava = threading.Lock()
        self.valor = None
        self.quando = 0.0

    def estado(self, fresco=False):
        """(ativa, mensagem, plano)."""
        with self.trava:
            lic = dados.importar("licenca")
            try:
                marca = lic.ARQUIVO.stat().st_mtime if lic else 0.0
            except OSError:
                marca = 0.0
            if self.valor and not fresco and marca == getattr(self, "marca", None):
                ttl = 300 if self.valor[0] else 20
                if time.time() - self.quando < ttl:
                    return self.valor
            self.marca = marca
            if not lic:
                self.valor = (False, "O arquivo da licença do kit (kit/licenca.py) não foi encontrado.", "")
            else:
                try:
                    ativa, msg = lic.verifica()
                    self.valor = (bool(ativa), str(msg or ""), lic.plano() if ativa else "")
                except Exception:  # noqa: BLE001
                    self.valor = (False, "Não consegui conferir a licença. Confira a internet e tente de novo.", "")
            self.quando = time.time()
            return self.valor


LICENCA = Licenca()
ATIVACAO = threading.Lock()
ATIVACAO_ULTIMA = [0.0]


# ---------------------------------------------------------------- estado e ações

def _seguro(fn, padrao):
    try:
        return fn()
    except Exception as e:  # noqa: BLE001
        LOG.warning("%s falhou (%s: %s)", getattr(fn, "__name__", "parte"), type(e).__name__, e)
        return padrao


SUPORTE_EMAIL = "contato@temporadaviral.com"


def conta_licenca(ativa):
    """Dados da conta para a área de suporte: lê a última confirmação guardada pelo kit (não consulta o site).
    Sem licença ativa, só o e-mail de contato."""
    lic = dados.importar("licenca")
    if not ativa or not lic or not hasattr(lic, "conta"):
        return {"ativa": bool(ativa), "email": "", "desde": None, "atualizacoes_ate": None,
                "suporte": {"email": SUPORTE_EMAIL}}
    c = lic.conta()
    sup = c.get("suporte") or {}
    tg = str(sup.get("telegram") or "")
    # O link do Telegram vem do site (ele redireciona para o grupo); sem ele, o do próprio site. Só endereços conhecidos.
    if not (tg.startswith("https://t.me/") or tg.startswith(SITE + "/")):
        tg = SITE + "/telegram"
    # Link para comprar as atualizações sem prazo depois dos 12 meses: só o site ou o checkout da Cakto.
    # Grupo da comunidade: o site manda o endereço; sem ele, o redirecionador fixo do site.
    comunidade = str(c.get("comunidade") or "")
    if not (comunidade.startswith("https://t.me/") or comunidade.startswith(SITE + "/")):
        comunidade = SITE + "/comunidade"
    oferta = str(c.get("oferta_sempre") or "")
    if not (oferta.startswith(SITE + "/") or oferta.startswith("https://pay.cakto.com.br/")):
        oferta = ""
    return {"ativa": True, "email": str(c.get("email") or ""), "desde": c.get("desde"),
            "atualizacoes_ate": c.get("atualizacoes_ate"), "atualizacoes_sempre": bool(c.get("atualizacoes_sempre")),
            "oferta_sempre": oferta, "comunidade": comunidade, "copia": c.get("copia") if isinstance(c.get("copia"), dict) else None,
            "suporte": {"telegram": tg,
                        "email": str(sup.get("email") or SUPORTE_EMAIL), "resposta": str(sup.get("resposta") or "")}}


REINICIAR = threading.Event()    # depois de atualizar: o painel fecha e abre de novo já na versão nova
SERVIDOR = [None]


def atualizacao_estado(conferir=False):
    """Versão instalada, versão nova no site e se ela está liberada (kit/atualizar.py). None se o kit não tem o módulo."""
    a = dados.importar("atualizar")
    if not a or not hasattr(a, "estado"):
        return None
    e = a.estado(conferir=conferir)
    if not str(e.get("oferta") or "").startswith(("https://pay.cakto.com.br/", SITE + "/")):
        e["oferta"] = ""
    e["reiniciando"] = REINICIAR.is_set()
    e["painel_desde"] = VIDA.inicio   # muda quando o painel reabre: a página sabe que já é o da versão nova
    return e


def atualizacao_aplicar():
    """Começa a atualização numa linha de fundo; a página acompanha por /api/atualizacao/progresso."""
    a = dados.importar("atualizar")
    if not a or not hasattr(a, "aplicar"):
        return {"ok": False, "msg": "Esta versão do kit ainda não se atualiza sozinha."}
    if ia.ocupado():
        return {"ok": False, "msg": "A IA está trabalhando agora. Espere ela terminar e atualize em seguida."}
    if a.ANDAMENTO.copia().get("rodando"):
        return {"ok": True, "msg": "A atualização já está em andamento."}

    def rodar():
        r = a.aplicar()
        LOG.info("atualização do kit: %s", "ok " + str(r.get("versao")) if r.get("ok") else "recusada (" + str(r.get("motivo")) + ")")
        if r.get("ok") and SERVIDOR[0] is not None:
            REINICIAR.set()
            # Um instante para a página ler o "pronto" antes de o painel fechar e abrir de novo.
            threading.Timer(1.5, SERVIDOR[0].shutdown).start()

    threading.Thread(target=rodar, daemon=True).start()
    return {"ok": True, "msg": "Atualização começou."}


def reabrir_painel(a):
    """Abre o painel de novo (mesma porta e mesmo código, guardados em painel.codigo.json), sem janela nem navegador."""
    exe = Path(sys.executable)
    if os.name == "nt" and exe.name.lower() == "python.exe" and (exe.parent / "pythonw.exe").is_file():
        exe = exe.parent / "pythonw.exe"
    args = [str(exe), str(PAINEL / "servidor.py"), "--sem-navegador", "--porta", str(Pedido.porta)]
    if a.sem_desligar:
        args.append("--sem-desligar")
    if a.ia_tempo_max:
        args += ["--ia-tempo-max", str(a.ia_tempo_max)]
    extra = {"creationflags": 0x00000008 | 0x00000200} if os.name == "nt" else {"start_new_session": True}
    try:
        # O código vai por variável de ambiente (não aparece na lista de processos): a aba aberta continua valendo.
        env = dict(os.environ, TV_PAINEL_CODIGO=Pedido.token)
        subprocess.Popen(args, cwd=str(ESTUDIO), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, close_fds=True, env=env, **extra)
        LOG.info("painel reaberto depois da atualização")
    except OSError as e:
        LOG.error("não consegui reabrir o painel depois da atualização (%s)", type(e).__name__)


def canais_lista():
    """Canais do estúdio (kit/canais): o em uso e os guardados. Lista vazia se o kit ainda não tem o módulo."""
    c = dados.importar("canais")
    if not c or not hasattr(c, "listar"):
        return {"disponivel": False, "lista": []}
    return {"disponivel": True, "lista": c.listar()}


def canais_acao(acao, corpo):
    """Troca de canal ou canal novo, pelo kit/canais (a mesma função do `python -m canais`)."""
    c = dados.importar("canais")
    if not c or not hasattr(c, acao):
        return {"ok": False, "msg": "Esta versão do kit ainda não troca de canal. Peça no chat da IA."}
    try:
        if acao == "usar":
            cid = str(corpo.get("id") or "")
            if not re.match(r"^[a-z0-9][a-z0-9\-]{0,59}$", cid):
                return {"ok": False, "msg": "Escolha um canal da lista."}
            r = c.usar(cid)
        else:
            nome = " ".join(str(corpo.get("nome") or "").split())
            if not nome or len(nome) > 60:
                return {"ok": False, "msg": "Escreva o nome do canal novo (até 60 letras)."}
            r = c.novo(nome)
    except c.ErroCanal as e:
        return {"ok": False, "msg": str(e)}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "msg": f"Não consegui trocar de canal ({type(e).__name__}). Peça no chat da IA."}
    dados.chaves(forcar=True)
    return {"ok": True, "canal": r, "msg": f"Canal em uso: {r.get('nome') or r.get('id')}."}


def montar_estado(plano=""):
    p = _seguro(dados.prefs_payload, {"erro": "As preferências não carregaram."})
    valores = p.get("valores") or {}
    return {
        "canal": _seguro(lambda: dados.canal_resumo(valores), {}) if valores else {},
        "prefs": p,
        "versao": dados.versao_kit(),
        "pedidos": _seguro(dados.pedidos, []),
        "episodios": _seguro(dados.episodios, []),
        "metricas": _seguro(dados.metricas_historico, {"disponivel": False, "historico": []}),
        "conquistas": _seguro(dados.conquistas, {"disponivel": False, "lista": [], "novas": []}),
        "pronuncia": _seguro(dados.pronuncia, {"trocas": [], "fora_da_fala": [], "base": [], "base_fora": []}),
        "chaves": _seguro(dados.chaves, {}),
        "video_ia": _seguro(dados.video_ia, None),
        "status": _seguro(lambda: dados.checagens(("ativa", plano)), {"itens": [], "pct": 0}),
        "estilos": _seguro(dados.estilos, {"lista": []}),
        "personagens": _seguro(dados.personagens, {"lista": []}),
        "ganchos": _seguro(dados.ganchos, {}),
        "ajuda": _seguro(dados.ajuda, {"erros": []}),
        "assinatura": _seguro(dados.assinatura, ""),
        "conta": _seguro(lambda: conta_licenca(LICENCA.estado()[0]), {"ativa": False, "suporte": {"email": SUPORTE_EMAIL}}),
        "canais": _seguro(canais_lista, {"disponivel": False, "lista": []}),
        "atualizacao": _seguro(atualizacao_estado, None),
        "ideias": _seguro(dados.ideias, []),
        "estatico": False,
        "site": SITE,
        "gerado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }


def _get_status(url, cabecalhos):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=cabecalhos), timeout=20) as r:
            return r.status
    except urllib.error.HTTPError as e:
        try:                                   # chave válida mas restrita: a ElevenLabs diz "missing_permissions"
            if "permission" in e.read(4000).decode("utf-8", "replace").lower():
                return 4031
        except Exception:  # noqa: BLE001
            pass
        return e.code
    except Exception:  # noqa: BLE001
        return -1


def _testar_sem_requests(nome, valor):
    """Teste da chave só com a biblioteca padrão (OpenAI, ou quando o Python do painel não tem o requests)."""
    ua = {"User-Agent": "temporada-viral-painel"}
    if nome == "OPENAI_API_KEY":
        st = _get_status("https://api.openai.com/v1/models", dict(ua, Authorization=f"Bearer {valor}"))
        servico = "A OpenAI"
    elif nome == "GEMINI_API_KEY":
        st = _get_status("https://generativelanguage.googleapis.com/v1beta/models", dict(ua, **{"x-goog-api-key": valor}))
        servico = "O Google"
    elif nome == "elevenlabs":
        st = _get_status("https://api.elevenlabs.io/v1/voices", dict(ua, **{"xi-api-key": valor}))
        servico = "A ElevenLabs"
    else:
        return False, "Tipo de chave desconhecido.", None
    if st == 200:
        return True, "A chave funcionou.", None
    if st == 4031:
        return True, ("A chave é válida, mas está com permissões limitadas. No site do serviço, deixe ligada a "
                      "permissão de voz (Text to Speech) e a de ler as vozes."), None
    if st == -1:
        return False, "Sem internet ou o serviço não respondeu. Tente de novo em instantes.", None
    return False, f"{servico} recusou essa chave. Confira se copiou o código inteiro e tente de novo.", None


def salvar_chave(nome, valor):
    """Testa e salva pelo kit/chave.py (arquivo de segredos fora do kit). Nunca devolve nem registra a chave."""
    valor = "".join(str(valor or "").split())   # espaço ou quebra de linha colados junto com a chave
    if nome not in dados.NOMES_CHAVE:
        return {"ok": False, "msg": "Tipo de chave desconhecido."}
    valor = str(valor or "").strip()
    if len(valor) < 16 or len(valor) > 400 or re.search(r"\s", valor):
        return {"ok": False, "msg": "Essa chave parece incompleta. Copie de novo, sem espaço no meio."}
    chave = dados.importar("chave")
    if not chave:
        return {"ok": False, "msg": "O kit não carregou a parte que guarda as chaves (kit/chave.py). "
                                    "Peça pra IA: conecta a voz pela janela da chave."}
    saldo = None
    try:
        if nome == "OPENAI_API_KEY":
            ok, msg, saldo = _testar_sem_requests(nome, valor)
        elif nome in ("FAL_KEY", "HIGGSFIELD_API_KEY"):
            video = dados.importar("video_ia")
            if not video:
                return {"ok": False, "msg": "O kit não carregou a parte da IA de vídeo (kit/video_ia.py). Atualize o kit."}
            ok, msg, saldo = video.testar(nome, valor)
        else:
            try:
                ok, msg, saldo = chave.testar(nome, valor)
            except ImportError:
                ok, msg, saldo = _testar_sem_requests(nome, valor)
    except Exception:  # noqa: BLE001
        ok, msg = False, "Sem internet ou o serviço não respondeu. Tente de novo em instantes."
    if not ok:
        return {"ok": False, "msg": msg}
    try:
        chave.salvar(nome, valor)
    except BaseException:  # noqa: BLE001  (chave.salvar sai com SystemExit se o arquivo estiver dentro do kit)
        return {"ok": False, "msg": "A chave funcionou, mas não consegui guardar. Peça pra IA: confere o arquivo "
                                    "de segredos do kit."}
    dados.chaves(forcar=True)
    fim = valor[-4:]
    return {"ok": True, "msg": msg, "fim": fim, "saldo": saldo}


def abrir_pasta(chave_rel):
    """Abre no gerenciador de arquivos uma pasta de dentro do estúdio."""
    chave_rel = str(chave_rel or "").replace("\\", "/")
    raiz = ESTUDIO
    if chave_rel.startswith("~t/"):
        raiz, chave_rel = dados.trabalho(), chave_rel[3:]
    partes = [x for x in chave_rel.split("/") if x]
    if any(x in (".", "..") or x.startswith(".") for x in partes):
        return False
    raiz = raiz.resolve()
    alvo = raiz.joinpath(*partes).resolve() if partes else raiz
    try:
        alvo.relative_to(raiz)
    except ValueError:
        return False
    if not alvo.is_dir():
        return False
    try:
        if os.name == "nt":
            os.startfile(str(alvo))  # noqa: S606
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(alvo)])
        else:
            subprocess.Popen(["xdg-open", str(alvo)])
        return True
    except OSError:
        return False


def salvar_imagem(tipo, corpo):
    if tipo not in ("logo", "mascote"):
        return {"ok": False, "msg": "Tipo de imagem desconhecido."}
    if not corpo:
        return {"ok": False, "msg": "Escolha uma imagem."}
    if len(corpo) > MAX_IMAGEM:
        return {"ok": False, "msg": "Imagem grande demais: use uma de até 5 MB."}
    if corpo.startswith(b"\x89PNG\r\n\x1a\n"):
        ext = "png"
    elif corpo[:4] == b"RIFF" and corpo[8:12] == b"WEBP":
        ext = "webp"
    elif corpo.startswith(b"\xff\xd8\xff") and tipo == "logo":
        ext = "jpg"
    else:
        return {"ok": False, "msg": "Use PNG" + (" ou JPG" if tipo == "logo" else " com fundo transparente") + "."}
    CANAL.mkdir(parents=True, exist_ok=True)
    for velho in ("png", "jpg", "webp"):
        arq = CANAL / f"{tipo}.{velho}"
        if velho != ext and arq.is_file():
            arq.unlink()
    destino = CANAL / f"{tipo}.{ext}"
    tmp = destino.with_suffix(".tmp")
    tmp.write_bytes(corpo)
    tmp.replace(destino)
    p = dados.prefs()
    if not p:
        return {"ok": False, "msg": "A imagem foi salva, mas as preferências não carregaram."}
    ok, erros, avisos = p.salvar({"canal": {tipo: f"canal/{tipo}.{ext}"}})
    return {"ok": ok, "erros": erros, "avisos": avisos,
            "msg": ("Logo salvo." if tipo == "logo" else "Mascote salvo.") if ok else "; ".join(erros)}


_arroba_cache = {}
_arroba_trava = threading.Lock()


def conferir_arroba(nome):
    n = str(nome or "").strip().lstrip("@").lower()
    with _arroba_trava:
        guardado = _arroba_cache.get(n)
        if guardado and time.time() - guardado[0] < 600:
            return guardado[1]
        r = arroba.conferir(n)
        _arroba_cache[n] = (time.time(), r)
        return r


def registrar_metricas(corpo):
    m = dados.importar("metricas")
    if not m or not hasattr(m, "registrar"):
        return {"ok": False, "indisponivel": True,
                "msg": "O registro de métricas chega numa próxima versão do kit. Por enquanto, mande os números "
                       "no chat da IA."}
    episodio = str(corpo.get("episodio") or "").strip()
    rede = str(corpo.get("rede") or "").strip()
    if not re.match(r"^[\w.\-]{1,100}$", episodio):
        return {"ok": False, "msg": "Escolha o episódio."}
    if rede not in dados.REDE_DA_PASTA.values():
        return {"ok": False, "msg": "Escolha a rede."}
    # Os números vão como o usuário escreveu ("1.850", "32,4"): o metricas.py entende o jeito brasileiro e valida.
    numeros = {str(k): str(v).strip()[:30] for k, v in (corpo.get("numeros") or {}).items()
               if re.match(r"^[a-z_0-9]{1,40}$", str(k)) and str(v or "").strip()}
    if not numeros:
        return {"ok": False, "msg": "Preencha pelo menos um número."}
    try:
        reg = m.registrar(episodio, rede, numeros)
        sugestoes = reg.get("sugestoes") if isinstance(reg, dict) and "sugestoes" in reg else (
            m.sugestoes(numeros) if hasattr(m, "sugestoes") else [])
    except ValueError as e:
        msg = str(e)
        return {"ok": False, "msg": (msg[:1].upper() + msg[1:]) if msg else "Confira os números."}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "msg": f"Não consegui registrar ({type(e).__name__}). Mande os números no chat da IA."}
    return {"ok": True, "msg": "Números anotados.", "sugestoes": [str(s) for s in (sugestoes or [])]}


# ---------------------------------------------------------------- páginas fixas

_URIS = {}


def _uri(nome):
    """Arquivo da pasta estatico/ como data URI: as páginas de bloqueio e a versão estática não carregam /static
    (ele também passa pelo portão da licença)."""
    if nome not in _URIS:
        try:
            _URIS[nome] = "data:image/png;base64," + base64.b64encode((ESTATICO / nome).read_bytes()).decode()
        except OSError:
            _URIS[nome] = ""
    return _URIS[nome]


def pagina_painel(titulo, corpo_html, token="", pagina="", ilustracao="erro", reserva="tv-cade"):
    """Página de entrada (sem código, licença) no visual do painel: mesma folha de estilo, letras e mascote."""
    meta = f'<meta name="painel-token" content="{html.escape(token, quote=True)}">' if token else ""
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="dark">
<meta name="theme-color" content="#08262F">{meta}<title>{html.escape(titulo)}</title>
<link rel="icon" href="{_uri("favicon-48.png")}" type="image/png" sizes="48x48">
<link rel="apple-touch-icon" href="{_uri("apple-touch-icon.png")}">
<link rel="stylesheet" href="/static/painel.css"></head>
<body class="pagina-fixa" data-pagina="{html.escape(pagina)}">
<header class="topo"><span class="marca"><img class="inteira" src="/static/marca/logo-360.webp" alt="Temporada Viral" width="104" height="54">
<img class="cabeca" src="{_uri("icone-256.png")}" alt="Temporada Viral" width="44" height="44"></span></header>
<main class="fixa"><img class="ilustra fixa-ilustra" src="/static/ilustracoes/{ilustracao}.webp" data-reserva-src="/static/marca/{reserva}.webp" alt="">
{corpo_html}</main><script src="/static/acesso.js"></script></body></html>"""


def mensagem_licenca(msg):
    """A mensagem do site em linguagem de gente: sem o aviso dirigido à IA e sem comando de terminal."""
    msg = re.split(r"\s*Aviso para a IA", str(msg or ""), maxsplit=1)[0].strip()
    if "licenca.py" in msg:
        return ""
    return msg.replace(" (LICENCA_E_TERMOS.md)", "").replace(", como diz a seção 6 dos termos", " (seção 6 dos termos)")


def situacao_licenca(msg):
    """"ativar" (nunca ativado), "internet" (não deu para conferir) ou "bloqueada"."""
    lic = dados.importar("licenca")
    try:
        email = lic.conta().get("email") if lic and hasattr(lic, "conta") else ""
    except Exception:  # noqa: BLE001
        email = ""
    if not email or "licenca.py" in str(msg or ""):
        return "ativar"
    if str(msg or "").startswith("Não consegui confirmar a licença"):
        return "internet"
    return "bloqueada"


def form_ativar(rotulo_botao="Ativar"):
    return ('<form class="ativar" id="form-ativar" novalidate><div class="campo"><label for="email-compra">E-mail da compra</label>'
            '<input class="entrada" type="email" id="email-compra" name="email" autocomplete="email" inputmode="email" '
            'placeholder="o e-mail que você usou para comprar" required>'
            '<p class="erro-msg" id="erro-ativar" role="alert" hidden></p></div>'
            f'<button type="submit" class="botao gigante largo"><span class="rotulo">{rotulo_botao}</span></button></form>')


def pagina_bloqueio(mensagem, token=""):
    sit = situacao_licenca(mensagem)
    contato = (f'<p class="meta">Dúvida? Escreva para <a href="mailto:{SUPORTE_EMAIL}">{SUPORTE_EMAIL}</a> '
               "com o e-mail da compra.</p>")
    if sit == "ativar":
        corpo = ('<h1 class="titulo">Vamos ativar o seu kit</h1>'
                 '<p class="lead">Escreva o e-mail que você usou na compra. Leva uns segundos.</p>' + form_ativar() + contato)
        return pagina_painel("Ativar o kit · Temporada Viral", corpo, token, "licenca", "licenca", "tv-frente")
    if sit == "internet":
        corpo = ('<h1 class="titulo">Sem internet para conferir</h1>'
                 '<p class="lead">O kit confere a licença no site de vez em quando. Ligue a internet e tente de novo.</p>'
                 '<div class="acoes-centro"><a class="botao gigante" href="">Tentar de novo</a></div>' + contato)
        return pagina_painel("Sem internet · Temporada Viral", corpo, token, "licenca")
    texto = mensagem_licenca(mensagem) or "A licença deste e-mail não está ativa."
    corpo = ('<h1 class="titulo">O kit está bloqueado</h1>'
             f'<p class="lead">{html.escape(texto)}</p>'
             f'<div class="acoes-centro"><a class="botao secundario" href="mailto:{SUPORTE_EMAIL}?subject=Licen%C3%A7a%20Temporada%20Viral">'
             '<span class="rotulo">Falar com o suporte</span></a></div>'
             '<h2 class="bloco-titulo">Comprou com outro e-mail?</h2>' + form_ativar("Ativar com este e-mail"))
    return pagina_painel("Kit bloqueado · Temporada Viral", corpo, token, "licenca")


PAGINA_SEM_CODIGO = pagina_painel("Abra pelo ícone · Temporada Viral", (
    '<h1 class="titulo">Abra o painel pelo ícone</h1>'
    '<p class="lead">Por segurança, o painel só abre pelo link que o ícone Temporada Viral cria neste computador.</p>'
    '<div class="acoes-centro"><button type="button" class="botao gigante" id="abrir-de-novo" aria-expanded="false" '
    'aria-controls="como-abrir"><span class="rotulo">Abrir o painel de novo</span></button></div>'
    '<ol class="passos-abrir" id="como-abrir" hidden><li><span class="n">1</span><span>Feche esta aba.</span></li>'
    '<li><span class="n">2</span><span>Dê dois cliques no ícone <b>Temporada Viral</b>, na área de trabalho ou no menu '
    'Iniciar (no Mac, em Aplicativos).</span></li><li><span class="n">3</span><span>O painel abre sozinho, já liberado.'
    '</span></li></ol>'), "", "sem-codigo", "erro", "tv-cade")


def html_app(token):
    """A página do painel com os ícones da marca embutidos: a imagem nunca depende de outra rota para aparecer."""
    modelo = (ESTATICO / "index.html").read_text(encoding="utf-8").replace("{{TOKEN}}", html.escape(token, quote=True))
    modelo = modelo.replace("{{ICONE}}", _uri("icone-256.png"))
    for url, nome in ICONES_MARCA:
        if _uri(nome):
            modelo = modelo.replace(f'href="{url}"', f'href="{_uri(nome)}"').replace(f'src="{url}"', f'src="{_uri(nome)}"')
    return modelo


# ---------------------------------------------------------------- servidor HTTP

class Pedido(BaseHTTPRequestHandler):
    token = ""
    porta = 0
    validade = VALIDADE_CODIGO_S
    server_version = "PainelTemporadaViral"
    sys_version = ""
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):  # silencioso: nada de URL, código ou corpo no terminal
        pass

    # -- respostas
    def _cabecalhos(self, codigo, tipo, tamanho, extra=None):
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(tamanho))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", CSP)
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()

    def _envia(self, codigo, corpo, tipo="text/html; charset=utf-8", extra=None):
        dados_ = corpo.encode("utf-8") if isinstance(corpo, str) else corpo
        extra = dict({"Cache-Control": "no-store"}, **(extra or {}))
        self._cabecalhos(codigo, tipo, len(dados_), extra)
        if self.command != "HEAD":
            try:
                self.wfile.write(dados_)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass

    def _json(self, codigo, obj):
        self._envia(codigo, json.dumps(obj, ensure_ascii=False, default=str), "application/json; charset=utf-8")

    def _arquivo(self, p, tipo):
        tam = p.stat().st_size
        ini, fim, codigo = 0, tam - 1, 200
        faixa = self.headers.get("Range")
        if faixa:
            m = re.match(r"^bytes=(\d*)-(\d*)$", faixa.strip())
            if not m or (not m.group(1) and not m.group(2)):
                return self._envia(416, "", extra={"Content-Range": f"bytes */{tam}"})
            if m.group(1):
                ini = int(m.group(1))
                fim = min(int(m.group(2)), tam - 1) if m.group(2) else tam - 1
            else:
                ini = max(0, tam - int(m.group(2)))
            if ini > fim or ini >= tam:
                return self._envia(416, "", extra={"Content-Range": f"bytes */{tam}"})
            codigo = 206
        extra = {"Accept-Ranges": "bytes", "Cache-Control": "no-cache"}
        if codigo == 206:
            extra["Content-Range"] = f"bytes {ini}-{fim}/{tam}"
        self._cabecalhos(codigo, tipo, fim - ini + 1, extra)
        if self.command == "HEAD":
            return None
        try:
            with open(p, "rb") as f:
                f.seek(ini)
                falta = fim - ini + 1
                while falta > 0:
                    pedaco = f.read(min(262144, falta))
                    if not pedaco:
                        break
                    self.wfile.write(pedaco)
                    falta -= len(pedaco)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass
        return None

    # -- portões
    def _host_ok(self):
        host = (self.headers.get("Host") or "").lower()
        return host in (f"127.0.0.1:{self.porta}", f"localhost:{self.porta}")

    def _cookie_nome(self):
        return f"tvpainel{self.porta}"

    def _token_recebido(self, consulta):
        if consulta.get("t", [""])[0]:
            return consulta["t"][0]
        if self.headers.get("X-Painel-Token"):
            return self.headers["X-Painel-Token"]
        for parte in (self.headers.get("Cookie") or "").split(";"):
            nome, _, valor = parte.strip().partition("=")
            if nome == self._cookie_nome():
                return valor
        return ""

    def _portao(self, consulta, fresco=False):
        """True se pode seguir; senão já respondeu (403 sem código, bloqueio sem licença)."""
        if not self._host_ok():
            self._envia(403, "Acesso recusado.", "text/plain; charset=utf-8")
            return False
        if not secrets.compare_digest(self._token_recebido(consulta), self.token):
            if self.path.startswith("/api/"):
                self._json(403, {"ok": False, "msg": "Sem o código de acesso do painel."})
            else:
                self._envia(403, PAGINA_SEM_CODIGO, extra={"Cache-Control": "no-store"})
            return False
        VIDA.tocar()
        ativa, msg, _ = LICENCA.estado(fresco=fresco)
        if not ativa:
            if self.path.startswith("/api/") or self.command == "POST":
                self._json(403, {"ok": False, "bloqueado": True, "msg": msg})
            else:
                self._envia(403, pagina_bloqueio(msg, self.token), extra={"Cache-Control": "no-store"})
            return False
        return True

    # -- GET
    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        url = urllib.parse.urlsplit(self.path)
        consulta = urllib.parse.parse_qs(url.query)
        if url.path == "/api/ping":
            # Só para o ícone saber se o painel já está aberto: código no cabeçalho, sem licença e sem dados.
            if self._host_ok() and secrets.compare_digest(self.headers.get("X-Painel-Token") or "", self.token):
                return self._json(200, {"ok": True, "app": "painel-temporada-viral"})
            return self._json(403, {"ok": False})
        if url.path.startswith("/static/") and estatico_publico(url.path[len("/static/"):]):
            # Visual das páginas de entrada: sem código e sem licença (nada do estúdio sai por aqui).
            if not self._host_ok():
                return self._envia(403, "Acesso recusado.", "text/plain; charset=utf-8")
            arq, tipo = arquivo_estatico(url.path[len("/static/"):])
            if arq:
                return self._envia(200, arq.read_bytes(), tipo, {"Cache-Control": "no-cache"})
            return self._envia(404, "Não encontrado.", "text/plain; charset=utf-8")
        if not self._portao(consulta):
            return None
        rota = url.path
        if rota == "/":
            if consulta.get("t"):
                # O cookie dura enquanto o código valer (até 7 dias): o navegador reabre o painel sem o link.
                cookie = (f"{self._cookie_nome()}={self.token}; Path=/; HttpOnly; SameSite=Strict; "
                          f"Max-Age={max(60, int(self.validade))}")
                return self._envia(303, "", extra={"Location": "/", "Set-Cookie": cookie})
            return self._envia(200, html_app(self.token))
        if rota.startswith("/static/"):
            nome = rota[len("/static/"):]
            arq, tipo = arquivo_estatico(nome)
            if arq:
                return self._envia(200, arq.read_bytes(), tipo, {"Cache-Control": "no-cache"})
            return self._envia(404, "Não encontrado.", "text/plain; charset=utf-8")
        if rota == "/fonte/anton.ttf":
            if ARQ_FONTE.is_file():
                return self._envia(200, ARQ_FONTE.read_bytes(), "font/ttf", {"Cache-Control": "max-age=86400"})
            return self._envia(404, "", "text/plain; charset=utf-8")
        if rota == "/midia":
            p = dados.resolver_midia(consulta.get("c", [""])[0])
            if not p:
                return self._envia(404, "Arquivo não encontrado.", "text/plain; charset=utf-8")
            return self._arquivo(p, dados.EXT_MIDIA[p.suffix.lower()])
        if rota == "/exemplo":
            # Vídeo-exemplo de um estilo: só exemplos/estilos/<id>/exemplo.mp4 ou capa.jpg, com Range para o celular.
            tipo = consulta.get("f", [""])[0]
            p = dados.resolver_exemplo(consulta.get("e", [""])[0], tipo)
            if not p:
                return self._envia(404, "Exemplo ainda não disponível.", "text/plain; charset=utf-8")
            return self._arquivo(p, "video/mp4" if tipo == "video" else "image/jpeg")
        if rota == "/api/tutoriais":
            return self._json(200, _seguro(dados.tutoriais, {"lista": []}))
        if rota == "/api/assinatura":
            return self._json(200, {"assinatura": dados.assinatura(), "verificando": dados.VERIFICACAO.rodando})
        if rota == "/api/estado":
            _, _, plano = LICENCA.estado()
            return self._json(200, montar_estado(plano))
        if rota == "/api/arroba":
            return self._json(200, conferir_arroba(consulta.get("n", [""])[0]))
        if rota == "/api/atualizacao":
            # conferir=1 ao abrir o painel: pergunta ao site (no máximo uma vez por hora).
            return self._json(200, _seguro(lambda: atualizacao_estado(consulta.get("conferir", [""])[0] == "1"), None)
                              or {"nova": None})
        if rota == "/api/estilo-proprio":
            return self._json(200, _seguro(estilo_proprio.payload, {"disponivel": False, "perguntas": []}))
        if rota == "/api/estudo":
            return self._json(200, _seguro(estudo_painel.payload, {"recursos": {"disponivel": False}, "lista": []}))
        if rota == "/api/estudo/ver":
            return self._json(200, _seguro(lambda: estudo_painel.ver(consulta.get("id", [""])[0]),
                                           {"ok": False, "msg": "Não consegui abrir esse estudo."}))
        if rota == "/api/ia/estado":
            return self._json(200, ia.estado(forcar=consulta.get("forcar", [""])[0] == "1"))
        if rota == "/api/ia/conversas":
            return self._json(200, _seguro(ia.conversas_salvas, {"conversas": []}))
        if rota == "/api/ia/conversa-do-video":
            return self._json(200, _seguro(lambda: ia.conversa_do_video(consulta.get("nome", [""])[0]), {"ok": False}))
        if rota == "/api/ia/conversa":
            return self._json(200, ia.ler_conversa(consulta.get("id", [""])[0]))
        if rota == "/api/ia/episodios":
            return self._json(200, _seguro(dados.episodios_em_producao, {"episodios": []}))
        if rota == "/api/ia/arquivo":
            return self._json(200, dados.arquivo_para_chat(consulta.get("c", [""])[0]))
        if rota == "/api/ia/eventos":
            return self._json(200, ia.eventos(consulta.get("cli", [""])[0], consulta.get("desde", ["0"])[0]))
        return self._json(404, {"ok": False, "msg": "Rota desconhecida."})

    def _fluxo_ia(self, corpo):
        """Resposta da IA em text/event-stream. Se a aba fechar no meio, a IA termina o pedido (ou para pelo
        /api/ia/parar); o estado mostra que ela ainda está ocupada."""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Accel-Buffering", "no")
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True
        aberto = [True]
        trava = threading.Lock()
        acabou = threading.Event()

        def escrever(txt):
            if not aberto[0]:
                return
            with trava:
                try:
                    self.wfile.write(txt.encode("utf-8"))
                    self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
                    aberto[0] = False

        def emitir(ev):
            VIDA.tocar()
            escrever("data: " + json.dumps(ev, ensure_ascii=False) + "\n\n")

        def pulsar():
            # Comentário SSE a cada 15 s: a conexão não fica muda enquanto a IA roda um comando longo.
            while not acabou.wait(15):
                escrever(": ping\n\n")

        threading.Thread(target=pulsar, daemon=True).start()
        conversa = corpo.get("conversa")
        try:
            ia.conversar(str(corpo.get("cli") or ""), corpo.get("texto"), str(conversa) if conversa else None, emitir)
        finally:
            acabou.set()
        return None

    # -- POST
    def do_POST(self):
        url = urllib.parse.urlsplit(self.path)
        consulta = urllib.parse.parse_qs(url.query)
        # Ação exige o código no cabeçalho (o cookie sozinho não basta) e confere a licença de novo.
        if not secrets.compare_digest(self.headers.get("X-Painel-Token") or "", self.token):
            return self._json(403, {"ok": False, "msg": "Sem o código de acesso do painel."})
        if url.path == "/api/licenca/ativar":
            # Única ação antes da licença: ativar com o e-mail da compra (o próprio licenca.ativar confere no site).
            return self._ativar_licenca()
        if not self._portao({}, fresco=True):
            return None
        try:
            tam = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            tam = -1
        if url.path == "/api/estudo/arquivo":
            # Vídeo de referência: vai direto para o disco, em pedaços (pode ter centenas de MB).
            return self._json(200, estudo_painel.receber(self.rfile, tam, consulta.get("nome", [""])[0]))
        if tam < 0 or tam > MAX_CORPO:
            return self._json(413, {"ok": False, "msg": "Envio grande demais."})
        bruto = self.rfile.read(tam) if tam else b""
        rota = url.path
        if rota == "/api/upload":
            return self._json(200, salvar_imagem(consulta.get("tipo", [""])[0], bruto))
        try:
            corpo = json.loads(bruto.decode("utf-8")) if bruto else {}
        except (UnicodeDecodeError, ValueError):
            return self._json(400, {"ok": False, "msg": "Pedido inválido."})
        if not isinstance(corpo, dict):
            return self._json(400, {"ok": False, "msg": "Pedido inválido."})
        try:
            return self._acao(rota, corpo)
        finally:
            corpo.pop("valor", None)  # a chave não fica em memória além do necessário

    def _ativar_licenca(self):
        if not self._host_ok():
            return self._json(403, {"ok": False, "msg": "Acesso recusado."})
        try:
            tam = int(self.headers.get("Content-Length") or 0)
            corpo = json.loads(self.rfile.read(tam).decode("utf-8")) if 0 < tam < 4096 else {}
        except (ValueError, UnicodeDecodeError):
            corpo = {}
        email = str((corpo if isinstance(corpo, dict) else {}).get("email") or "").strip().lower()
        if not re.fullmatch(r"[^@\s]{1,64}@[^@\s]{1,190}\.[a-z]{2,24}", email):
            return self._json(200, {"ok": False, "msg": "Confira o e-mail: ele precisa ter @ e ponto, como nome@gmail.com."})
        with ATIVACAO:
            espera = 3 - (time.time() - ATIVACAO_ULTIMA[0])
            if espera > 0:
                time.sleep(espera)
            ATIVACAO_ULTIMA[0] = time.time()
            lic = dados.importar("licenca")
            if not lic or not hasattr(lic, "ativar"):
                return self._json(200, {"ok": False, "msg": "O arquivo da licença do kit não foi encontrado."})
            try:
                ativa, msg = lic.ativar(email)
            except Exception:  # noqa: BLE001
                ativa, msg = False, "Não consegui falar com o site agora. Confira a internet e tente de novo."
        LICENCA.estado(fresco=True)
        LOG.info("ativação da licença pelo painel: %s", "ok" if ativa else "recusada")
        if ativa:
            return self._json(200, {"ok": True, "msg": "Pronto! O kit está ativo."})
        texto = mensagem_licenca(msg) or "Não achamos esse e-mail. Confira se é o mesmo do recibo da compra."
        return self._json(200, {"ok": False, "msg": texto})

    def _acao(self, rota, corpo):
        p = dados.prefs()
        if rota == "/api/prefs":
            mudancas = corpo.get("mudancas")
            if not p or not isinstance(mudancas, dict) or not all(isinstance(v, dict) for v in mudancas.values()):
                return self._json(400, {"ok": False, "erros": ["Pedido inválido."]})
            ok, erros, avisos = p.salvar(mudancas)
            if ok and "caminho" in mudancas.get("canal", {}):
                dados.sincronizar_caminho(p.carregar()["canal"]["caminho"])
            return self._json(200, {"ok": ok, "erros": erros, "avisos": avisos})
        if rota == "/api/prefs/recomendado":
            secao = str(corpo.get("secao") or "")
            if not p or secao not in p.esquema()["secoes"]:
                return self._json(400, {"ok": False, "msg": "Seção desconhecida."})
            p.voltar_recomendado(secao)
            if secao == "canal":
                dados.sincronizar_caminho(p.carregar()["canal"]["caminho"])
            return self._json(200, {"ok": True, "avisos": p.avisos(p.carregar())})
        if rota == "/api/pronuncia":
            ok, erros = dados.salvar_pronuncia(corpo)
            return self._json(200, {"ok": ok, "erros": erros})
        if rota == "/api/pedido":
            ok, msg = dados.adicionar_pedido(corpo.get("episodio"), corpo.get("cena"), corpo.get("texto"))
            return self._json(200, {"ok": ok, "msg": msg})
        if rota == "/api/metricas":
            return self._json(200, registrar_metricas(corpo))
        if rota == "/api/conquistas/vistas":
            c = dados.importar("conquistas")
            if not c:
                return self._json(200, {"ok": False})
            ids = corpo.get("ids") if isinstance(corpo.get("ids"), list) else []
            return self._json(200, {"ok": True, "marcadas": c.marcar_vistas([str(i)[:40] for i in ids[:30]])})
        if rota == "/api/gancho":
            fala, tela = str(corpo.get("fala") or "")[:600], str(corpo.get("tela") or "")[:200]
            try:
                dur = corpo.get("dur_s")
                dur = None if dur in (None, "") else float(str(dur).replace(",", "."))
                r = dados.avaliar_gancho(fala, tela, dur, float(corpo.get("inicio_fala_s") or 0))
            except (TypeError, ValueError):
                return self._json(200, {"ok": False, "msg": "Use um número de segundos (ex.: 2,8)."})
            if r is None:
                return self._json(200, {"ok": False, "indisponivel": True,
                                        "msg": "O conferidor de gancho chega numa próxima versão do kit."})
            return self._json(200, dict(r, ok=True))
        if rota == "/api/chave":
            return self._json(200, salvar_chave(str(corpo.get("nome") or ""), corpo.get("valor")))
        if rota == "/api/verificar":
            dados.VERIFICACAO.rodar()
            return self._json(200, {"ok": True})
        if rota in ("/api/canais/usar", "/api/canais/novo"):
            return self._json(200, canais_acao(rota.rsplit("/", 1)[1], corpo))
        if rota == "/api/abrir":
            ok = abrir_pasta(corpo.get("caminho"))
            return self._json(200, {"ok": ok, "msg": "" if ok else "Não consegui abrir essa pasta."})
        if rota == "/api/vivo":
            return self._json(200, {"ok": True, "fecha_sem_uso_s": OCIOSO_S})
        if rota == "/api/atualizacao/aplicar":
            return self._json(200, atualizacao_aplicar())
        if rota == "/api/estilo-proprio/sortear":
            return self._json(200, estilo_proprio.SORTEIO.comecar(corpo.get("respostas"), corpo.get("nome")))
        if rota == "/api/estilo-proprio/usar":
            return self._json(200, estilo_proprio.SORTEIO.usar())
        if rota == "/api/estudo/comecar":
            # Só link pela rede (arquivo chega por /api/estudo/arquivo): nada de caminho local vindo da página.
            lista = corpo.get("urls") if isinstance(corpo.get("urls"), list) else [corpo.get("url")]
            links = [str(u or "").strip()[:2000] for u in lista]
            if not links or not all(re.match(r"^https?://", u) for u in links):
                return self._json(200, {"ok": False, "msg": "Cole o link inteiro do vídeo, começando com https://."})
            return self._json(200, estudo_painel.TRABALHO.comecar(links))
        if rota == "/api/estudo/parar":
            return self._json(200, estudo_painel.TRABALHO.parar())
        if rota == "/api/estudo/preparar":
            return self._json(200, estudo_painel.preparar_ao_fundo())
        if rota == "/api/estudo/buscar":
            return self._json(200, estudo_painel.buscar(str(corpo.get("termo") or ""), corpo.get("curtos")))
        if rota == "/api/estudo/nicho":
            ids = corpo.get("ids") if isinstance(corpo.get("ids"), list) else []
            return self._json(200, _seguro(lambda: estudo_painel.comparar([str(i) for i in ids]),
                                           {"ok": False, "msg": "Não consegui comparar agora."}))
        if rota == "/api/estudo/apagar":
            return self._json(200, estudo_painel.apagar(str(corpo.get("id") or "")))
        if rota == "/api/ia/mensagem":
            return self._fluxo_ia(corpo)
        if rota == "/api/ia/abrir":
            return self._json(200, ia.abrir_terminal(str(corpo.get("cli") or "")))
        if rota == "/api/ia/parar":
            conversa, cli = corpo.get("conversa"), corpo.get("cli")
            return self._json(200, ia.parar(str(conversa) if conversa else None, str(cli) if cli else None))
        return self._json(404, {"ok": False, "msg": "Ação desconhecida."})


class Servidor(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = False

    def handle_error(self, request, client_address):
        # O navegador corta a conexão ao trocar de vídeo ou fechar a aba: isso é normal e não vira erro na janela.
        if isinstance(sys.exc_info()[1], (ConnectionResetError, ConnectionAbortedError, BrokenPipeError)):
            return
        LOG.error("erro ao responder um pedido", exc_info=True)


# ---------------------------------------------------------------- versão estática (nuvem e celular)

def gerar_estatico(saida=None):
    """Grava painel.html na pasta do estúdio: tudo num arquivo, só para ver, sem nenhuma ação."""
    ativa, msg, plano = LICENCA.estado(fresco=False)
    if not ativa:
        print(f"LICENÇA INATIVA: {msg}")
        return 1
    print("Conferindo a máquina (leva alguns segundos)...", flush=True)
    dados.VERIFICACAO.rodar(esperar=True)
    estado = montar_estado(plano)
    estado["estatico"] = True
    estado["icone"] = _uri("icone-256.png")
    estado["tutoriais"] = _seguro(dados.tutoriais, {"lista": []})
    css = (ESTATICO / "painel.css").read_text(encoding="utf-8")
    if ARQ_FONTE.is_file():
        fonte = "data:font/ttf;base64," + base64.b64encode(ARQ_FONTE.read_bytes()).decode()
        css = css.replace('url("/fonte/anton.ttf")', f'url("{fonte}")')
    js = (ESTATICO / "painel.js").read_text(encoding="utf-8").replace("</script", "<\\/script")
    dados_js = json.dumps(estado, ensure_ascii=False, default=str).replace("<", "\\u003c")
    pagina = html_app("")
    pagina = pagina.replace('<link rel="stylesheet" href="/static/painel.css">', f"<style>{css}</style>")
    pagina = pagina.replace('<script src="/static/painel.js"></script>',
                            f"<script>window.PAINEL_DADOS = {dados_js};</script>\n<script>{js}</script>")
    destino = Path(saida) if saida else ESTUDIO / "painel.html"
    tmp = destino.with_suffix(".tmp")
    tmp.write_text(pagina, encoding="utf-8")
    tmp.replace(destino)
    print(f"PAINEL_ESTATICO: {destino}")
    print("Versão só para ver: abra o arquivo no navegador. Para mudar algo, peça no chat da IA.")
    return 0


# ---------------------------------------------------------------- início

def main():
    _utf8()
    dados.ffmpeg_no_path()
    ap = argparse.ArgumentParser(description="Painel do Temporada Viral (só neste computador).")
    ap.add_argument("--estatico", action="store_true", help="grava painel.html (só para ver) e sai")
    ap.add_argument("--saida", help="com --estatico: onde gravar (padrão: painel.html na pasta do estúdio)")
    ap.add_argument("--sem-navegador", action="store_true", help="não abre o navegador; só mostra o link")
    ap.add_argument("--porta", type=int, default=0, help="porta (padrão: uma livre, sorteada)")
    ap.add_argument("--sem-desligar", action="store_true",
                    help="não fecha sozinho quando ninguém usa o painel por 3 minutos")
    ap.add_argument("--ia-tempo-max", type=int, default=0,
                    help="tempo máximo de uma resposta do chat da IA, em segundos (padrão: 1800)")
    a = ap.parse_args()
    configurar_log()
    if a.estatico:
        sys.exit(gerar_estatico(a.saida))
    if a.ia_tempo_max:
        ia.TEMPO_MAX = max(60, a.ia_tempo_max)
    try:
        return _servir(a)
    except Exception:  # noqa: BLE001
        LOG.error("o painel parou com um erro", exc_info=True)
        raise


def _servir(a):
    if not a.porta:
        ja = painel_ja_aberto()
        if ja:
            # Segundo clique no ícone: o painel já está aberto, só mostra de novo.
            _dizer("O painel já estava aberto neste computador.")
            _dizer(f"PAINEL_URL: {ja}", flush=True)
            if not a.sem_navegador:
                webbrowser.open(ja)
            return 0
    # O código vale entre aberturas (7 dias) e a porta tenta ser a mesma: o navegador reabre o painel pelo cookie.
    Pedido.token, porta_antes, Pedido.validade, info_codigo = codigo_guardado()
    herdado = os.environ.pop("TV_PAINEL_CODIGO", "")
    if len(herdado) >= 24 and herdado != Pedido.token:
        # Reaberto depois da atualização: mantém o código da aba que está esperando.
        Pedido.token, Pedido.validade = herdado, VALIDADE_CODIGO_S
        info_codigo = {"token": herdado, "criado": time.time()}
    ia.ocultar_tambem(Pedido.token)
    srv = None
    if not a.porta and porta_antes:
        try:
            srv = Servidor(("127.0.0.1", porta_antes), Pedido)
        except OSError:
            srv = None
    if srv is None and a.porta:
        # O painel antigo pode levar um instante para soltar a porta: tenta por até 15 s.
        for _ in range(30):
            try:
                srv = Servidor(("127.0.0.1", a.porta), Pedido)
                break
            except OSError:
                time.sleep(0.5)
    if srv is None:
        srv = Servidor(("127.0.0.1", 0 if herdado else a.porta), Pedido)
    Pedido.porta = srv.server_address[1]
    info_codigo["porta"] = Pedido.porta
    gravar_codigo(info_codigo)
    url = f"http://127.0.0.1:{Pedido.porta}/?t={Pedido.token}"
    gravar_aberto(Pedido.porta, Pedido.token)
    SERVIDOR[0] = srv
    ativa, msg, _ = LICENCA.estado()
    dados.VERIFICACAO.rodar()
    LOG.info("painel aberto na porta %d%s", Pedido.porta, "" if ativa else " (licença inativa)")
    _dizer("Painel do Temporada Viral aberto neste computador.")
    if not ativa:
        _dizer(f"LICENÇA INATIVA: {msg}")
    _dizer("Se o navegador não abrir sozinho, copie este link (só funciona neste computador):")
    _dizer(f"PAINEL_URL: {url}", flush=True)
    _dizer("O jeito normal de abrir é o ícone Temporada Viral (área de trabalho ou menu Iniciar; no Mac, Aplicativos).",
           flush=True)
    if not a.sem_desligar:
        _dizer("Ele se fecha sozinho uns 3 minutos depois que você fechar a aba do painel.", flush=True)
        threading.Thread(target=vigiar, args=(srv,), daemon=True).start()
    if not a.sem_navegador:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        _dizer("\nPainel fechado.")
    finally:
        ia.parar_todas()
        apagar_aberto(Pedido.token)
        srv.server_close()
    if REINICIAR.is_set():
        reabrir_painel(a)
    return 0


if __name__ == "__main__":
    main()
