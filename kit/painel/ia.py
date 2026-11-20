# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Conversar com a IA dentro do painel: o Claude Code e o CLI do ChatGPT (Codex), os dois do próprio usuário.

Dois jeitos, pela mesma API do painel (mesmo código de acesso e mesma checagem de licença do servidor.py):
(a) "Abrir a IA aqui": abre o CLI de verdade numa janela de terminal, já na pasta do estúdio, com o fluxo de
    aprovação do próprio CLI. É o caminho para tudo o que o chat embutido não deixa fazer.
(b) Chat embutido: o CLI em modo não interativo, preso à pasta do estúdio e aos scripts do kit, com cada ação
    mostrada ao vivo. O que ficar fora do permitido não roda, e a IA diz para usar o (a).

CONTRATO DA API (para a tela do painel)
---------------------------------------
Todas as rotas exigem o cabeçalho X-Painel-Token (POST) e licença ativa, como o resto do painel.

GET  /api/ia/estado
     -> {"claude": {"instalado": bool, "logado": bool|null, "versao": str, "chat": bool, "ocupado": bool,
                    "conversa": str|null, "passos": [str], "aviso": str},
         "codex":  {...mesmos campos...}, "tempo_max_s": int}
     logado null = não deu para saber. "passos" vem preenchido (português) quando falta instalar ou entrar.
     "chat" false = o chat embutido não está disponível (CLI ausente, sem login ou versão antiga); o "aviso" diz por quê.
     "ocupado"/"conversa": há uma conversa rodando com esse CLI (mesmo que a aba que a começou tenha fechado).

POST /api/ia/abrir      {"cli": "claude"|"codex"}
     -> {"ok": bool, "msg": str, "passos": [str]}   abre o terminal real na pasta do estúdio.

POST /api/ia/mensagem   {"cli": "claude"|"codex", "texto": str, "conversa": str|null}
     -> text/event-stream; cada evento é uma linha "data: <json>" seguida de linha em branco:
        {"tipo": "inicio", "conversa": str|null}
        {"tipo": "texto", "texto": str}                     pedaço da resposta (vai somando)
        {"tipo": "acao", "id": str, "estado": "rodando"|"ok"|"erro"|"recusado",
         "resumo": "Rodou: python cartelas/rodar.py ...", "detalhe": str}
                                                           o mesmo id volta com o estado final
        {"tipo": "erro", "mensagem": str, "passos": [str]}
        {"tipo": "arquivos", "arquivos": [str]}            o que apareceu nas pastas de produção durante a resposta
        {"tipo": "fim", "conversa": str|null}              id para continuar a conversa (mande em "conversa")
     Uma conversa por vez por CLI: um segundo pedido enquanto a primeira roda recebe "erro" e "fim".
     Para ler: fetch() com POST e leitura do corpo em pedaços (EventSource não faz POST).

POST /api/ia/parar      {"conversa": str}   (ou {"cli": ...})
     -> {"ok": bool, "msg": str}   mata o processo da IA (e os filhos dele).

Nunca vai para eventos nem para o log: código de acesso do painel, chave, e-mail completo (são mascarados).
O tempo máximo de uma resposta vem de TV_IA_TEMPO_MAX (segundos) ou de --ia-tempo-max no servidor.py.
"""
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from pathlib import Path

PAINEL = Path(__file__).resolve().parent
KIT = PAINEL.parent
ESTUDIO = KIT.parent
GUARDA = PAINEL / "ia_guarda.py"
WINDOWS = os.name == "nt"
SEM_JANELA = getattr(subprocess, "CREATE_NO_WINDOW", 0)
NOVA_JANELA = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
NOMES = {"claude": "Claude Code", "codex": "Codex (ChatGPT)"}
try:
    TEMPO_MAX = max(60, int(os.environ.get("TV_IA_TEMPO_MAX") or 5400))
except ValueError:
    TEMPO_MAX = 5400  # 90 min: voz + cenas + render de um episódio cabem numa resposta
TEXTO_MAX = 8000
ID_OK = re.compile(r"^[0-9a-fA-F][0-9a-fA-F\-]{7,63}$")
# Flags do Claude Code sem as quais o chat embutido não roda (confere na ajuda do CLI instalado).
FLAGS_CLAUDE = ("--print", "--output-format", "--permission-mode", "--settings", "--strict-mcp-config", "--tools",
                "--restricted", "--append-system-prompt", "--session-id", "--resume")
FERRAMENTAS_CLAUDE = ["Read", "Edit", "Write", "Glob", "Grep", "Bash"] + (["PowerShell"] if WINDOWS else [])
PROIBIDAS_NO_INICIO = {"WebFetch", "WebSearch", "Agent", "Task"}
PERMITIDAS_CLAUDE = [
    "Read", "Glob", "Grep",
    "Bash(python *)", "Bash(python3 *)", "Bash(py *)", "Bash(ffmpeg *)", "Bash(ffprobe *)", "Bash(cd *)",
    "Bash(sleep *)",  # as REGRAS mandam esperar comando ao fundo com `sleep 30`
] + ([
    "PowerShell(python *)", "PowerShell(py *)", "PowerShell(ffmpeg *)", "PowerShell(ffprobe *)", "PowerShell(Start-Sleep *)",
    "PowerShell(Set-Location *)", "PowerShell(Get-ChildItem *)", "PowerShell(Get-Content *)",
] if WINDOWS else [])
NEGADAS_CLAUDE = [
    "WebFetch", "WebSearch", "Agent", "Task", "NotebookEdit",
    "Bash(rm *)", "Bash(curl *)", "Bash(wget *)", "Bash(pip *)", "Bash(git *)", "Bash(ssh *)", "Bash(scp *)",
    "Read(//**/.licenca.json)", "Edit(//**/.licenca.json)",
] + (["PowerShell(Remove-Item *)", "PowerShell(Invoke-WebRequest *)", "PowerShell(Invoke-RestMethod *)",
      "PowerShell(Start-Process *)"] if WINDOWS else [])
REGRAS = (
    "Você está no CHAT DO PAINEL do Temporada Viral, não no terminal. Aqui a pessoa não aprova nada pelo meio: o que "
    "não estiver liberado é recusado na hora. Liberado: ler e editar arquivos dentro da pasta do estúdio (menos o "
    "código do kit; o episódio, em series/, kit/series/, kit/canais/ e kit/trabalho/, pode ser gravado, "
    "inclusive o programa da cena em .py dentro da pasta do episódio, que você pode rodar com python), rodar `python` dos scripts que já vêm em kit/, `ffmpeg` e `ffprobe`. Um comando por chamada, "
    "sem juntar com && ou ;: rode `python kit/<script>.py ...` da pasta do estúdio; o que o kit manda rodar \"a "
    "partir de kit/\" (como `python -m prefs`), rode em duas chamadas: primeiro só `cd kit`, depois só o comando. "
    "Não use $, crase, redirecionamento (> ou <) nem variável de ambiente no comando. O vídeo inteiro se faz por aqui: roteiro, voz, cenas, "
    "trilha, prévia, vídeo final e pacote das redes. Quem usa este chat nunca abriu um terminal: não mande a pessoa "
    "para o terminal nem para o 'Abrir a IA aqui' para seguir o vídeo. Comando demorado (voz, render): rode ao "
    "fundo e leia a saída dele quando terminar. Para conferir ou instalar o que falta (voz grátis, Whisper, núcleo do "
    "kit), use `python kit/instalar_recursos.py --conferir` e `python kit/instalar_recursos.py <receita>`; nunca "
    "`python -c` nem pip direto. Para esperar um comando ao fundo, use `sleep 30` (sem laço until/while) e leia a saída. Não dá para instalar programa, abrir sites, publicar nas redes "
    "(a pessoa posta pelo app de cada rede), apagar arquivos nem mexer fora da pasta. Se uma ação vier recusada com "
    "'FORA DO PERMITIDO', tente o caminho permitido (outra pasta do episódio, outro script do kit). Instalar o que "
    "o kit precisa (voz grátis, Whisper, núcleo do kit, gravador de vídeo ffmpeg, estudo de vídeos) se faz por aqui, com o instalar_recursos.py. "
    "Estudar um vídeo de referência (transcrever, raio-x, nicho) é `python -m estudo <link ou arquivo>` a partir de kit/, "
    "seguindo metodo/estudar-referencias.md: o molde é só estrutura, nunca copie frase do vídeo estudado. Se antes "
    "nesta conversa você disse para usar o terminal ou o 'Abrir a IA aqui', isso mudou: faça por aqui. Só sugira "
    "o 'Abrir a IA aqui' se o instalar_recursos.py der erro e disser para usar. Fale em "
    "português simples, como para quem nunca abriu um terminal. Sem botões de resposta: pergunte em texto, com "
    "duas sugestões prontas, cada uma numa linha começando com a) e b) e o texto curto em negrito (o painel "
    "transforma essas linhas em botões). Antes de qualquer etapa demorada (voz, render, prévia), diga em uma frase "
    "quanto tempo leva em minutos, por exemplo: 'leva uns 10 minutos'; o painel usa esse número para mostrar a "
    "previsão."
)
REGRAS_CODEX = ("[Regras do chat do painel] " + REGRAS.replace("rodar `python`", "rodar `python`")
                + " Os scripts do kit podem usar a internet (voz da ElevenLabs ou do Google).\n\n[Pedido]\n")

# ---------------------------------------------------------------- máscara (eventos e log)

_EMAIL = re.compile(r"([A-Za-z0-9._%+\-])[A-Za-z0-9._%+\-]*@([A-Za-z0-9.\-]+\.[A-Za-z]{2,})")
_CHAVE = re.compile(r"\b(sk-[A-Za-z0-9_\-]{12,}|AIza[0-9A-Za-z_\-]{20,}|xi-[A-Za-z0-9]{16,}|"
                    r"(?=[A-Za-z0-9_\-]*\d)(?=[A-Za-z0-9_\-]*[A-Za-z])[A-Za-z0-9_\-]{40,})\b")
_SEGREDOS_EXTRA = []


def ocultar_tambem(valor):
    """Registra um valor que nunca pode sair (o código de acesso do painel)."""
    if valor and len(valor) >= 8:
        _SEGREDOS_EXTRA.append(valor)


def mascarar(txt):
    txt = str(txt or "")
    for s in _SEGREDOS_EXTRA:
        txt = txt.replace(s, "[código oculto]")
    txt = _EMAIL.sub(lambda m: f"{m.group(1)}***@{m.group(2)}", txt)
    return _CHAVE.sub("[chave oculta]", txt)


def _log():
    try:
        import logging
        return logging.getLogger("painel")
    except Exception:  # noqa: BLE001
        return None


def _avisar(msg):
    lg = _log()
    if lg:
        lg.warning(mascarar(msg))


# ---------------------------------------------------------------- achar o CLI

def _candidatos(cli):
    casa = Path.home()
    if WINDOWS:
        ad = Path(os.environ.get("APPDATA") or casa / "AppData" / "Roaming")
        la = Path(os.environ.get("LOCALAPPDATA") or casa / "AppData" / "Local")
        return [casa / ".local" / "bin" / f"{cli}.exe", ad / "npm" / f"{cli}.cmd",
                la / "Programs" / cli / f"{cli}.exe", la / "Microsoft" / "WinGet" / "Links" / f"{cli}.exe"]
    return [casa / ".local" / "bin" / cli, Path("/opt/homebrew/bin") / cli, Path("/usr/local/bin") / cli,
            casa / ".npm-global" / "bin" / cli, casa / ".claude" / "local" / cli]


def localizar(cli):
    achado = shutil.which(cli)
    if achado:
        return achado
    for p in _candidatos(cli):
        if p.is_file():
            return str(p)
    return None


def _base_cmd(exe):
    """Um .cmd/.bat (instalação pelo npm) só roda pelo cmd.exe. Só passamos argumentos nossos (nunca o texto da
    pessoa, que vai pela entrada padrão), então o cmd não interpreta nada vindo de fora."""
    if WINDOWS and exe.lower().endswith((".cmd", ".bat")):
        return [os.environ.get("COMSPEC") or "cmd.exe", "/d", "/s", "/c", exe]
    return [exe]


def _ambiente():
    try:
        import dados
        dados.ffmpeg_no_path()  # o ffmpeg que o painel instalou vale também para os comandos da IA
    except Exception:  # noqa: BLE001  (sem isso a IA segue com o PATH do sistema)
        pass
    amb = dict(os.environ)
    # Painel aberto por uma sessão do Claude Code: sem isso o CLI recusaria rodar "dentro de outra sessão".
    for k in list(amb):
        if k == "CLAUDECODE" or k.startswith("CLAUDE_CODE_ENTRYPOINT"):
            amb.pop(k, None)
    amb["PYTHONIOENCODING"] = "utf-8"
    amb["NO_COLOR"] = "1"
    return amb


def _rodar(cmd, tempo=20):
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=tempo, cwd=str(ESTUDIO), env=_ambiente(),
                           stdin=subprocess.DEVNULL, creationflags=SEM_JANELA)
        return r.returncode, r.stdout.decode("utf-8", "replace"), r.stderr.decode("utf-8", "replace")
    except (OSError, subprocess.SubprocessError) as e:
        return -1, "", type(e).__name__


PASSOS_INSTALAR = {
    "claude": ["Instale o Claude Code pelo site oficial: claude.com/claude-code (no Windows, pelo PowerShell; no Mac, "
               "pelo Terminal, com o comando que o site mostra).",
               "Depois clique em 'Abrir a IA aqui' uma vez e entre com sua conta do Claude (plano Pro ou maior).",
               "Volte para o painel: o chat aparece sozinho."],
    "codex": ["Instale o Codex, o CLI do ChatGPT: siga o passo a passo do site oficial (developers.openai.com/codex).",
              "Depois clique em 'Abrir a IA aqui' uma vez e entre com sua conta do ChatGPT.",
              "Volte para o painel: o chat aparece sozinho."],
}
PASSOS_LOGIN = {
    "claude": ["Clique em 'Abrir a IA aqui' e escolha o Claude.", "Na janela que abrir, entre com sua conta do Claude "
               "(ele abre o navegador para você confirmar).", "Feche a janela e volte para o painel."],
    "codex": ["Clique em 'Abrir a IA aqui' e escolha o Codex.", "Na janela que abrir, escolha entrar com a conta do "
              "ChatGPT (ele abre o navegador para você confirmar).", "Feche a janela e volte para o painel."],
}

_cache = {}
_cache_trava = threading.Lock()


def _estado_claude(exe):
    cod, saida, _ = _rodar(_base_cmd(exe) + ["--version"], 20)
    versao = (re.search(r"\d+\.\d+\.\d+", saida) or [""])[0] if cod == 0 else ""
    cod, saida, _ = _rodar(_base_cmd(exe) + ["auth", "status", "--json"], 25)
    logado = None
    if saida.strip():
        try:
            logado = bool(json.loads(saida).get("loggedIn"))  # só este campo é lido; e-mail e conta ficam de fora
        except ValueError:
            logado = None
    _, ajuda, _ = _rodar(_base_cmd(exe) + ["--help"], 20)
    faltam = [f for f in FLAGS_CLAUDE if f not in ajuda] if ajuda else list(FLAGS_CLAUDE)
    if "dontAsk" not in ajuda:
        faltam.append("dontAsk")
    extras = [f for f in ("--permission-prompts", "--include-partial-messages", "--disable-slash-commands",
                          "--no-chrome") if f in ajuda]
    return versao, logado, faltam, extras


def _estado_codex(exe):
    cod, saida, _ = _rodar(_base_cmd(exe) + ["--version"], 20)
    versao = (re.search(r"\d+\.\d+\.\d+", saida) or [""])[0] if cod == 0 else ""
    cod, saida, erro = _rodar(_base_cmd(exe) + ["login", "status"], 25)
    if cod == 0:
        logado = True
    elif re.search(r"not logged in|não", saida + erro, re.I) or cod == 1:
        logado = False
    else:
        logado = None
    return versao, logado, [], []


def estado_cli(cli, forcar=False):
    with _cache_trava:
        guardado = _cache.get(cli)
        if guardado and not forcar and time.time() - guardado[0] < (120 if guardado[1].get("logado") else 15):
            info = dict(guardado[1])
        else:
            exe = localizar(cli)
            info = {"instalado": bool(exe), "logado": None, "versao": "", "chat": False, "passos": [], "aviso": "",
                    "_exe": exe, "_extras": []}
            if exe:
                versao, logado, faltam, extras = (_estado_claude if cli == "claude" else _estado_codex)(exe)
                info.update(versao=versao, logado=logado, _extras=extras)
                if faltam:
                    info["aviso"] = (f"Este {NOMES[cli]} é de uma versão antiga para o chat do painel. Use 'Abrir a "
                                     "IA aqui' e peça para ela se atualizar (no Claude: claude update).")
                elif logado is False:
                    info["aviso"] = "Falta entrar com a sua conta."
                    info["passos"] = PASSOS_LOGIN[cli]
                else:
                    info["chat"] = True
            else:
                info["aviso"] = f"O {NOMES[cli]} não está instalado neste computador."
                info["passos"] = PASSOS_INSTALAR[cli]
            _cache[cli] = (time.time(), dict(info))
    ativo = CONVERSAS.ativa(cli)
    info["ocupado"] = bool(ativo)
    info["conversa"] = ativo
    return info


def _publico(info):
    return {k: v for k, v in info.items() if not k.startswith("_")}


def estado(forcar=False):
    r = {cli: _publico(estado_cli(cli, forcar)) for cli in NOMES}
    r["tempo_max_s"] = TEMPO_MAX
    return r


# ---------------------------------------------------------------- (a) abrir o terminal de verdade

def abrir_terminal(cli):
    if cli not in NOMES:
        return {"ok": False, "msg": "Escolha o Claude ou o Codex.", "passos": []}
    exe = localizar(cli)
    if not exe:
        return {"ok": False, "msg": f"O {NOMES[cli]} não está instalado.", "passos": PASSOS_INSTALAR[cli]}
    try:
        if WINDOWS:
            # cmd /k: a janela continua aberta se o CLI fechar (dá para ler a mensagem e digitar de novo).
            subprocess.Popen([os.environ.get("COMSPEC") or "cmd.exe", "/d", "/k", exe], cwd=str(ESTUDIO),
                             creationflags=NOVA_JANELA, env=_ambiente())
        elif sys.platform == "darwin":
            linha = f"cd {_aspas_sh(str(ESTUDIO))} && {_aspas_sh(exe)}"
            script = f'tell application "Terminal"\nactivate\ndo script "{_aspas_as(linha)}"\nend tell'
            subprocess.Popen(["osascript", "-e", script])
        else:
            term = next((t for t in ("x-terminal-emulator", "gnome-terminal", "konsole", "xterm") if shutil.which(t)),
                        None)
            if not term:
                return {"ok": False, "msg": "Não achei um terminal. Abra o terminal na pasta do estúdio e digite "
                                            f"{cli}.", "passos": []}
            arg = ["--"] if term == "gnome-terminal" else ["-e"]
            subprocess.Popen([term] + arg + [exe], cwd=str(ESTUDIO))
    except OSError as e:
        _avisar(f"ia: abrir terminal falhou ({type(e).__name__})")
        return {"ok": False, "msg": "Não consegui abrir a janela. Abra o terminal na pasta do estúdio e digite "
                                    f"{cli}.", "passos": []}
    with _cache_trava:
        _cache.pop(cli, None)  # depois do login, o estado tem de ser conferido de novo
    return {"ok": True, "msg": f"Abri o {NOMES[cli]} numa janela nova, já na pasta do estúdio.", "passos": []}


def _aspas_sh(s):
    return "'" + s.replace("'", "'\\''") + "'"


def _aspas_as(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


# ---------------------------------------------------------------- (b) chat embutido

class Execucao:
    def __init__(self, cli, conversa):
        self.cli = cli
        self.conversa = conversa
        self.proc = None
        self.parado = False
        self.estourou = False
        self.inicio = time.time()


class Conversas:
    def __init__(self):
        self.trava = threading.Lock()
        self.ativas = {}

    def reservar(self, cli, conversa):
        with self.trava:
            if cli in self.ativas:
                return None
            ex = Execucao(cli, conversa)
            self.ativas[cli] = ex
            return ex

    def soltar(self, ex):
        with self.trava:
            if self.ativas.get(ex.cli) is ex:
                del self.ativas[ex.cli]

    def ativa(self, cli):
        with self.trava:
            ex = self.ativas.get(cli)
            return ex.conversa if ex else None

    def alguma(self):
        with self.trava:
            return bool(self.ativas)

    def parar(self, conversa=None, cli=None):
        with self.trava:
            alvos = [ex for ex in self.ativas.values()
                     if (conversa and ex.conversa == conversa) or (cli and ex.cli == cli) or (not conversa and not cli)]
        for ex in alvos:
            ex.parado = True
            matar(ex.proc)
        return bool(alvos)


CONVERSAS = Conversas()


def matar(proc):
    if not proc or proc.poll() is not None:
        return
    try:
        if WINDOWS:
            subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True, timeout=15,
                           creationflags=SEM_JANELA)
        else:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            try:
                proc.wait(5)
            except subprocess.TimeoutExpired:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except (OSError, subprocess.SubprocessError):
        try:
            proc.kill()
        except OSError:
            pass


def _python_guarda():
    """Python de console para a guarda (o pythonw não tem saída padrão confiável)."""
    exe = Path(sys.executable)
    if exe.name.lower() == "pythonw.exe" and (exe.parent / "python.exe").is_file():
        return str(exe.parent / "python.exe")
    return str(exe)


def _padrao_abs(p):
    """Caminho no formato das regras do Claude Code: //c/pasta (Windows) ou //Users/... (Mac), com os
    caracteres de padrão escapados."""
    txt = Path(p).resolve().as_posix()
    m = re.match(r"^([A-Za-z]):/(.*)$", txt)
    if m:
        txt = f"/{m.group(1).lower()}/{m.group(2)}"
    return "/" + "".join("\\" + c if c in "\\[]*?!#" else c for c in txt).rstrip("/")


def _config_claude():
    cfg = {
        # Regras, ganchos e travas num arquivo só, fora do alcance da IA (o --settings vale mesmo com --restricted).
        # Caminho absoluto (//c/...), porque "/" num arquivo de --settings é a pasta do próprio arquivo.
        "permissions": {"allow": PERMITIDAS_CLAUDE + [f"Edit({_padrao_abs(ESTUDIO)}/**)"],
                        "deny": NEGADAS_CLAUDE + [f"Edit({_padrao_abs(KIT)}/licenca.py)"],
                        "disableBypassPermissionsMode": "disable", "disableAutoMode": "disable",
                        # Leitura fora da pasta já cai no dontAsk (pediria aprovação) e na guarda. A trava
                        # blockReadsOutsideWorkingDirectories ficou de fora: no Claude Code 2.1.319 no Windows ela
                        # recusa até "cd kit" dentro do estúdio.
                        "blockWritesOutsideWorkingDirectories": True},
        "hooks": {"PreToolUse": [{"matcher": "*", "hooks": [
            {"type": "command", "command": _python_guarda(), "args": ["-I", str(GUARDA), str(ESTUDIO)],
             "timeout": 30}]}]},
    }
    # Fora da pasta do estúdio: a IA não alcança este arquivo (o chat só escreve dentro do estúdio).
    fd, caminho = tempfile.mkstemp(prefix="tv-ia-", suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(cfg, f)
    return caminho


def _contexto_maquina():
    """Uma frase sobre a máquina para a IA acertar a previsão de tempo do render (com placa é bem mais rápido)."""
    try:
        import dados
        placa = dados.placa_dedicada(dados.placas_de_video() or [])
    except Exception:  # noqa: BLE001  (sem a informação, a IA estima como sempre)
        return ""
    if placa:
        return (f" Este computador tem placa de vídeo ({placa}): o render na placa leva cerca de 1,5 vez a duração "
                "do vídeo (um vídeo de 2 min fica pronto em uns 3 a 4 min). Use isso nas previsões de tempo.")
    return (" Este computador não tem placa de vídeo dedicada: o render vai pelo processador e leva várias vezes a "
            "duração do vídeo; antes de prever, rode os quadros-marco (--stills) e meça.")


def _cmd_claude(info, conversa_nova, conversa, cfg):
    cmd = _base_cmd(info["_exe"]) + [
        "--print", "--output-format", "stream-json", "--verbose",
        "--restricted", "--strict-mcp-config",
        "--tools", ",".join(FERRAMENTAS_CLAUDE),
        "--permission-mode", "dontAsk",
        "--settings", cfg,
        "--append-system-prompt", REGRAS + _contexto_maquina(),
    ]
    extras = info.get("_extras") or []
    if "--permission-prompts" in extras:
        cmd += ["--permission-prompts", "none"]
    if "--include-partial-messages" in extras:
        cmd += ["--include-partial-messages"]
    if "--disable-slash-commands" in extras:
        cmd += ["--disable-slash-commands"]
    if "--no-chrome" in extras:
        cmd += ["--no-chrome"]
    cmd += ["--session-id", conversa] if conversa_nova else ["--resume", conversa]
    return cmd


def _cmd_codex(info, conversa):
    base = _base_cmd(info["_exe"]) + [
        "exec", "--json", "--skip-git-repo-check", "--sandbox", "workspace-write", "--cd", str(ESTUDIO),
        "-c", 'approval_policy="never"', "-c", "sandbox_workspace_write.network_access=true",
    ]
    return base + (["resume", conversa, "-"] if conversa else ["-"])


def _rel(caminho):
    try:
        return Path(caminho).resolve().relative_to(ESTUDIO.resolve()).as_posix()
    except (ValueError, OSError):
        return str(caminho)


def _resumo_claude(nome, entrada):
    e = entrada or {}
    if nome in ("Bash", "PowerShell"):
        cmd = " ".join(str(e.get("command") or "").split())
        return f"Rodou: {cmd[:220]}", str(e.get("description") or "")
    if nome == "Read":
        return f"Leu: {_rel(e.get('file_path') or '')}", ""
    if nome == "Write":
        return f"Gravou: {_rel(e.get('file_path') or '')}", ""
    if nome in ("Edit", "MultiEdit", "NotebookEdit"):
        return f"Editou: {_rel(e.get('file_path') or e.get('notebook_path') or '')}", ""
    if nome in ("Glob", "Grep"):
        return f"Procurou: {str(e.get('pattern') or '')[:120]}", _rel(e.get("path") or "") if e.get("path") else ""
    if nome == "TodoWrite":
        return "Organizou a lista de tarefas", ""
    return f"Usou: {nome}", ""


EXT_ARQ_CHAT = (".mp4", ".mov", ".webm", ".mp3", ".wav", ".png", ".jpg", ".jpeg", ".webp", ".gif")
EXT_TXT_CHAT = (".md", ".txt", ".json", ".srt", ".csv")
_RE_ARQ = re.compile(r"([A-Za-z]:[\\/][^\s\"'<>|*?]+|[\w.\\/-]+)\.(mp4|mov|webm|mp3|wav|png|jpe?g|webp|gif)\b", re.I)


def _arquivo_chat(caminho):
    """Caminho relativo ao estúdio de um arquivo que existe e pode aparecer no chat (nada de licença ou segredo)."""
    if not caminho:
        return None
    for base in (None, ESTUDIO, KIT):
        try:
            p = Path(caminho) if base is None else base / caminho
            if base is None and not p.is_absolute():
                continue
            p = p.resolve()
            rel = p.relative_to(ESTUDIO.resolve())
        except (ValueError, OSError):
            continue
        nome = rel.as_posix().lower()
        if (not p.is_file() or any(x.startswith(".") for x in rel.parts) or "segredo" in nome or "licenca" in nome
                or p.suffix.lower() not in EXT_ARQ_CHAT + EXT_TXT_CHAT):
            return None
        return rel.as_posix()
    return None


def _arquivos_no_texto(txt):
    achados = []
    for m in _RE_ARQ.finditer(str(txt or "")[-20000:]):
        rel = _arquivo_chat(m.group(0))
        if rel and rel not in achados:
            achados.append(rel)
    return achados[:8]


PULAR_PASTAS = {"quadros", "qa", "cache", "tmp", "__pycache__", "node_modules"}
PRIORIDADE_EXT = {".mp4": 0, ".mov": 0, ".webm": 0, ".png": 1, ".jpg": 1, ".jpeg": 1, ".webp": 1, ".gif": 1,
                  ".mp3": 2, ".wav": 2}


def _arquivos_da_rodada(desde, limite=10):
    """Arquivos de vídeo, imagem, áudio e texto que apareceram ou mudaram nas pastas de produção durante a resposta
    (os que um script do kit gerou não passam pelo Write da IA). Mais importantes e mais novos primeiro."""
    achados = []
    trab = KIT / "trabalho"
    for raiz in (ESTUDIO / "series", KIT / "series", trab):
        if not raiz.is_dir():
            continue
        for pasta, subpastas, arquivos in os.walk(raiz):
            subpastas[:] = [d for d in subpastas if d not in PULAR_PASTAS and not d.startswith(".")]
            if Path(pasta) == trab:  # arquivos soltos de trabalho/ são do painel (estado, log), não do episódio
                continue
            for nome in arquivos:
                ext = os.path.splitext(nome)[1].lower()
                if ext not in EXT_ARQ_CHAT + EXT_TXT_CHAT or nome.startswith("."):
                    continue
                caminho = os.path.join(pasta, nome)
                try:
                    quando = os.path.getmtime(caminho)
                except OSError:
                    continue
                if quando >= desde - 2:
                    achados.append((PRIORIDADE_EXT.get(ext, 3), -quando, caminho))
    rels = []
    for _, _, caminho in sorted(achados):
        rel = _arquivo_chat(caminho)
        if rel and rel not in rels:
            rels.append(rel)
        if len(rels) >= limite:
            break
    return rels


def _texto_resultado(conteudo):
    if isinstance(conteudo, list):
        return " ".join(str(c.get("text") or "") for c in conteudo if isinstance(c, dict))
    return str(conteudo or "")


class _Leitor:
    """Traduz as linhas do CLI em eventos do contrato."""

    def __init__(self, cli, emitir):
        self.cli = cli
        self.emitir = emitir
        self.conversa = None
        self.parcial = False
        self.resultado = None
        self.erro_api = ""
        self.falou = False
        self.escritos = {}

    def acao(self, ident, estado, resumo, detalhe="", arquivos=None):
        ev = {"tipo": "acao", "id": str(ident), "estado": estado, "resumo": resumo, "detalhe": detalhe}
        if arquivos:
            ev["arquivos"] = arquivos
        self.emitir(ev)

    def claude(self, ev):
        t = ev.get("type")
        if t == "system" and ev.get("subtype") == "init":
            self.conversa = ev.get("session_id") or self.conversa
            ferramentas = set(ev.get("tools") or [])
            ruins = sorted(f for f in ferramentas if f in PROIBIDAS_NO_INICIO or f.startswith("mcp__"))
            if ruins or (ev.get("permissionMode") not in (None, "dontAsk")):
                raise RuntimeError("o Claude Code abriu com ferramentas fora do combinado: " + ", ".join(ruins))
        elif t == "stream_event":
            d = (ev.get("event") or {}).get("delta") or {}
            if d.get("type") == "text_delta" and d.get("text"):
                self.parcial = True
                self.falou = True
                self.emitir({"tipo": "texto", "texto": d["text"]})
        elif t == "assistant":
            for b in (ev.get("message") or {}).get("content") or []:
                if b.get("type") == "text" and b.get("text") and not self.parcial:
                    self.falou = True
                    self.emitir({"tipo": "texto", "texto": b["text"]})
                elif b.get("type") == "tool_use":
                    self.falou = False
                    resumo, detalhe = _resumo_claude(b.get("name"), b.get("input"))
                    entrada = b.get("input") or {}
                    if b.get("name") in ("Write", "Edit", "MultiEdit"):
                        self.escritos[str(b.get("id"))] = entrada.get("file_path") or ""
                    self.acao(b.get("id"), "rodando", resumo, detalhe)
            blocos = (ev.get("message") or {}).get("content") or []
            if self.parcial and any(b.get("type") == "text" and b.get("text") for b in blocos):
                self.emitir({"tipo": "texto", "texto": "\n\n"})
        elif t == "user":
            for b in (ev.get("message") or {}).get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    txt = _texto_resultado(b.get("content"))
                    if b.get("is_error"):
                        recusado = bool(re.search(r"FORA DO PERMITIDO|permission|permiss|denied|blocked", txt, re.I))
                        motivo = txt.split("FORA DO PERMITIDO NO CHAT DO PAINEL:", 1)[-1].strip()
                        self.acao(b.get("tool_use_id"), "recusado" if recusado else "erro", "",
                                  " ".join(motivo.split())[:300])
                    else:
                        ident = str(b.get("tool_use_id"))
                        rel = _arquivo_chat(self.escritos.pop(ident, ""))
                        self.acao(ident, "ok", "", "", [rel] if rel else _arquivos_no_texto(txt))
        elif t == "result":
            self.conversa = ev.get("session_id") or self.conversa
            self.resultado = ev
            if ev.get("is_error"):
                self.erro_api = str(ev.get("result") or ev.get("subtype") or "")
            elif not self.falou and str(ev.get("result") or "").strip():
                # A última mensagem só veio no resultado: mostra, para a resposta nunca terminar calada.
                self.falou = True
                self.emitir({"tipo": "texto", "texto": str(ev["result"])})

    def codex(self, ev):
        t = ev.get("type")
        item = ev.get("item") or {}
        tipo_item = item.get("type")
        if t == "thread.started":
            self.conversa = ev.get("thread_id") or self.conversa
        elif t == "item.started" and tipo_item == "command_execution":
            self.acao(item.get("id"), "rodando", f"Rodou: {' '.join(str(item.get('command') or '').split())[:220]}")
        elif t == "item.completed":
            if tipo_item == "agent_message" and item.get("text"):
                self.emitir({"tipo": "texto", "texto": item["text"] + "\n\n"})
            elif tipo_item == "command_execution":
                ok = item.get("exit_code") == 0
                estado = "ok" if ok else ("recusado" if item.get("status") == "declined" else "erro")
                self.acao(item.get("id"), estado,
                          f"Rodou: {' '.join(str(item.get('command') or '').split())[:220]}",
                          "" if ok else f"saiu com código {item.get('exit_code')}",
                          _arquivos_no_texto(item.get("aggregated_output")) if ok else None)
            elif tipo_item == "file_change":
                arqs = ", ".join(_rel(c.get("path") or "") for c in item.get("changes") or [])
                feitos = [r for r in (_arquivo_chat(c.get("path")) for c in item.get("changes") or []) if r]
                self.acao(item.get("id"), "ok" if item.get("status") != "failed" else "erro", f"Editou: {arqs[:220]}",
                          "", feitos[:8])
            elif tipo_item == "web_search":
                self.acao(item.get("id"), "ok", f"Pesquisou: {str(item.get('query') or '')[:120]}")
            elif tipo_item == "error":
                self.erro_api = str(item.get("message") or "")
        elif t in ("turn.failed", "error"):
            self.erro_api = str((ev.get("error") or {}).get("message") or ev.get("message") or "falhou")
        elif t == "turn.completed":
            self.resultado = ev


def _mensagem_erro(cli, saida_erro, erro_api):
    tudo = f"{saida_erro}\n{erro_api}"
    if re.search(r"log ?in|logged|authenticat|unauthori|401|credential|/login|api key", tudo, re.I):
        return "A IA pediu para entrar na conta de novo.", PASSOS_LOGIN[cli]
    if re.search(r"rate.?limit|usage limit|quota|429|overloaded|limite", tudo, re.I):
        return "A conta da IA chegou no limite de uso agora. Espere um pouco e tente de novo.", []
    if re.search(r"No conversation found|not found|session", tudo, re.I):
        return "Não achei essa conversa para continuar. Comece uma nova.", []
    return "A IA parou com um erro. Tente de novo; se repetir, fale com o suporte.", []


def conversar(cli, texto, conversa, emitir):
    """Roda uma resposta da IA e chama emitir(evento) para cada evento do contrato. Volta quando a IA termina."""
    if cli not in NOMES:
        emitir({"tipo": "erro", "mensagem": "Escolha o Claude ou o Codex.", "passos": []})
        emitir({"tipo": "fim", "conversa": None})
        return
    texto = str(texto or "").strip()
    if not texto:
        emitir({"tipo": "erro", "mensagem": "Escreva o que você quer pedir.", "passos": []})
        emitir({"tipo": "fim", "conversa": conversa})
        return
    if len(texto) > TEXTO_MAX:
        emitir({"tipo": "erro", "mensagem": f"Mensagem longa demais (até {TEXTO_MAX} letras).", "passos": []})
        emitir({"tipo": "fim", "conversa": conversa})
        return
    if conversa is not None and not ID_OK.match(str(conversa)):
        conversa = None
    info = estado_cli(cli)
    if not info.get("chat"):
        emitir({"tipo": "erro", "mensagem": info.get("aviso") or "O chat não está disponível.",
                "passos": info.get("passos") or []})
        emitir({"tipo": "fim", "conversa": conversa})
        return
    nova = conversa is None
    if cli == "claude" and nova:
        conversa = str(uuid.uuid4())
    ex = CONVERSAS.reservar(cli, conversa)
    if not ex:
        emitir({"tipo": "erro", "mensagem": f"O {NOMES[cli]} ainda está respondendo o pedido anterior. Espere "
                                            "terminar ou clique em Parar, aqui embaixo do chat.", "passos": [],
                "ocupado": True})
        emitir({"tipo": "fim", "conversa": None if nova else conversa})
        return
    reg = REGISTRO.nova(cli, conversa)
    emitir = _com_registro(cli, reg, emitir)
    cfg = None
    leitor = _Leitor(cli, lambda ev: emitir(_limpar(ev)))
    erros_txt = []
    try:
        if cli == "claude":
            cfg = _config_claude()
            cmd = _cmd_claude(info, nova, conversa, cfg)
            entrada = texto
        else:
            cmd = _cmd_codex(info, conversa)
            entrada = (REGRAS_CODEX.replace("[Pedido]", _contexto_maquina().strip() + "\n\n[Pedido]") + texto) if nova else texto
        emitir({"tipo": "inicio", "conversa": conversa, "rodada": reg["rodada"]})
        comeco = time.time()
        ex.proc = subprocess.Popen(cmd, cwd=str(ESTUDIO), env=_ambiente(), stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=SEM_JANELA,
                                   start_new_session=not WINDOWS)
        threading.Thread(target=_ler_erros, args=(ex.proc, erros_txt), daemon=True).start()
        relogio = threading.Timer(TEMPO_MAX, _estourar, args=(ex,))
        relogio.daemon = True
        relogio.start()
        try:
            ex.proc.stdin.write(entrada.encode("utf-8"))
            ex.proc.stdin.close()
        except OSError:
            pass
        traduzir = leitor.claude if cli == "claude" else leitor.codex
        for linha in ex.proc.stdout:
            linha = linha.strip()
            if not linha.startswith(b"{"):
                continue
            try:
                ev = json.loads(linha.decode("utf-8", "replace"))
            except ValueError:
                continue
            if cli == "codex" and leitor.conversa and not ex.conversa:
                ex.conversa = leitor.conversa
            traduzir(ev)
            if cli == "codex" and leitor.conversa:
                ex.conversa = leitor.conversa
        ex.proc.wait()
        relogio.cancel()
    except RuntimeError as e:
        matar(ex.proc)
        _avisar(f"ia: {cli} recusado na abertura ({e})")
        emitir(_limpar({"tipo": "erro", "mensagem": "O chat foi interrompido por segurança: " + str(e) + ". Use "
                                                    "'Abrir a IA aqui'.", "passos": []}))
    except OSError as e:
        _avisar(f"ia: {cli} não abriu ({type(e).__name__})")
        emitir({"tipo": "erro", "mensagem": f"Não consegui abrir o {NOMES[cli]}.", "passos": PASSOS_INSTALAR[cli]})
    else:
        if ex.estourou:
            emitir({"tipo": "erro", "mensagem": f"A resposta passou do tempo máximo ({TEMPO_MAX // 60} min) e foi "
                                                "parada. Peça em partes menores (por exemplo, só a voz, depois só o vídeo).",
                    "passos": []})
        elif ex.parado:
            emitir({"tipo": "erro", "mensagem": "Parado a seu pedido.", "passos": []})
        elif ex.proc.returncode != 0 or leitor.erro_api:
            msg, passos = _mensagem_erro(cli, "".join(erros_txt)[-2000:], leitor.erro_api)
            _avisar(f"ia: {cli} saiu com código {ex.proc.returncode}")
            if passos:
                with _cache_trava:
                    _cache.pop(cli, None)
            emitir({"tipo": "erro", "mensagem": msg, "passos": passos})
    finally:
        matar(ex.proc)
        CONVERSAS.soltar(ex)
        if cfg:
            try:
                os.unlink(cfg)
            except OSError:
                pass
    try:
        feitos = _arquivos_da_rodada(comeco) if "comeco" in locals() else []
    except OSError:
        feitos = []
    if feitos:
        emitir({"tipo": "arquivos", "arquivos": feitos})
    # A IA pode ter instalado peças nesta rodada: reconfere o computador para o "Está tudo certo?" não ficar velho.
    try:
        import dados
        dados.VERIFICACAO.rodar()
    except Exception:  # noqa: BLE001 - reconferir é extra; nunca derruba o fim da conversa
        pass
    emitir({"tipo": "fim", "conversa": leitor.conversa or ex.conversa})


class _Registro:
    """Guarda os eventos da última resposta de cada IA. Se a aba perder a conexão ou fechar no meio, o painel
    busca o que faltou em /api/ia/eventos. Ao terminar, a resposta vai para trabalho/ (sobrevive a reabrir o painel)."""

    def __init__(self):
        self.trava = threading.Lock()
        self.rodadas = {}
        self.seq = int(time.time() * 1000)

    @staticmethod
    def _arquivo(cli):
        return KIT / "trabalho" / f"ia-ultima-{cli}.json"

    def nova(self, cli, conversa):
        with self.trava:
            self.seq += 1
            r = {"rodada": self.seq, "conversa": conversa, "eventos": [], "fim": False}
            self.rodadas[cli] = r
            return r

    def anotar(self, cli, r, ev):
        copia = None
        with self.trava:
            if self.rodadas.get(cli) is not r or len(r["eventos"]) > 50000:
                return
            r["eventos"].append(ev)
            if ev.get("tipo") == "fim":
                r["fim"] = True
                r["conversa"] = ev.get("conversa") or r["conversa"]
                copia = {"rodada": r["rodada"], "conversa": r["conversa"], "eventos": list(r["eventos"]), "fim": True}
        if copia:
            try:
                arq = self._arquivo(cli)
                arq.parent.mkdir(parents=True, exist_ok=True)
                tmp = arq.with_suffix(".tmp")
                tmp.write_text(json.dumps(copia, ensure_ascii=False), encoding="utf-8")
                os.replace(tmp, arq)
            except OSError:
                pass

    def ler(self, cli, desde):
        with self.trava:
            r = self.rodadas.get(cli)
            if r is None:
                try:
                    r = json.loads(self._arquivo(cli).read_text(encoding="utf-8"))
                    r["fim"] = True
                    self.rodadas[cli] = r
                except (OSError, ValueError):
                    return {"rodada": None, "conversa": None, "eventos": [], "total": 0, "fim": True}
            evs = r["eventos"]
            desde = max(0, min(int(desde or 0), len(evs)))
            return {"rodada": r["rodada"], "conversa": r["conversa"], "eventos": evs[desde:], "total": len(evs),
                    "fim": bool(r["fim"])}


REGISTRO = _Registro()


def _com_registro(cli, reg, emitir):
    def com_registro(ev):
        REGISTRO.anotar(cli, reg, ev)
        emitir(ev)
    return com_registro


def eventos(cli, desde=0):
    if cli not in NOMES:
        return {"rodada": None, "conversa": None, "eventos": [], "total": 0, "fim": True}
    try:
        desde = int(desde)
    except (TypeError, ValueError):
        desde = 0
    return REGISTRO.ler(cli, desde)


def _limpar(ev):
    return {k: (mascarar(v) if isinstance(v, str) else v) for k, v in ev.items()}


def _ler_erros(proc, destino):
    try:
        for linha in proc.stderr:
            if sum(len(x) for x in destino) < 20000:
                destino.append(linha.decode("utf-8", "replace"))
    except (OSError, ValueError):
        pass


def _estourar(ex):
    ex.estourou = True
    matar(ex.proc)


# ---------------------------------------------------------------- conversas anteriores (de qualquer lugar)
# O Claude Code guarda cada conversa da pasta do estúdio em ~/.claude/projects/<pasta>/<id>.jsonl, seja ela do
# painel, do terminal ou do Claude Desktop. O painel lista essas conversas e abre qualquer uma para continuar.

def _pasta_sessoes():
    base = Path(os.environ.get("CLAUDE_CONFIG_DIR") or (Path.home() / ".claude")) / "projects"
    return base / re.sub(r"[^A-Za-z0-9]", "-", str(ESTUDIO.resolve()))


def _texto_usuario(conteudo):
    if isinstance(conteudo, str):
        return conteudo
    if isinstance(conteudo, list):
        return " ".join(str(b.get("text") or "") for b in conteudo if isinstance(b, dict) and b.get("type") == "text")
    return ""


def _pedido_de_gente(txt):
    t = (txt or "").strip()
    return bool(t) and not t.startswith(("<", "[Regras", "Caveat:")) and "tool_use_id" not in t[:80]


def conversas_salvas(limite=30):
    pasta = _pasta_sessoes()
    if not pasta.is_dir():
        return {"conversas": []}
    try:
        arqs = sorted(pasta.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)[:limite * 2]
    except OSError:
        return {"conversas": []}
    saida = []
    for arq in arqs:
        if len(saida) >= limite or not ID_OK.match(arq.stem):
            continue
        titulo, pedidos = "", 0
        try:
            with arq.open(encoding="utf-8", errors="replace") as f:
                for linha in f:
                    if '"user"' not in linha:
                        continue
                    try:
                        ev = json.loads(linha)
                    except ValueError:
                        continue
                    if ev.get("type") != "user" or ev.get("isMeta"):
                        continue
                    txt = _texto_usuario((ev.get("message") or {}).get("content"))
                    if _pedido_de_gente(txt):
                        pedidos += 1
                        titulo = titulo or " ".join(txt.split())[:120]
            quando = int(arq.stat().st_mtime)
        except OSError:
            continue
        if titulo:
            saida.append({"id": arq.stem, "titulo": mascarar(titulo), "quando": quando, "pedidos": pedidos})
    return {"conversas": saida}


def conversa_do_video(nome, limite=40):
    """Conversa salva mais nova que cita a pasta do vídeo (o nome do episódio). Lê só as 40 mais recentes."""
    nome = str(nome or "").strip()
    pasta = _pasta_sessoes()
    if len(nome) < 3 or not pasta.is_dir():
        return {"ok": False}
    alvo = nome.encode("utf-8")
    try:
        arqs = sorted(pasta.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)[:limite]
    except OSError:
        return {"ok": False}
    for arq in arqs:
        if not ID_OK.match(arq.stem):
            continue
        try:
            if alvo in arq.read_bytes():
                return {"ok": True, "id": arq.stem}
        except OSError:
            continue
    return {"ok": False}


def ler_conversa(ident):
    """Mensagens de uma conversa salva, no formato do chat do painel (texto e ações na ordem)."""
    if not ID_OK.match(str(ident or "")):
        return {"ok": False, "msg": "Conversa desconhecida."}
    arq = _pasta_sessoes() / f"{ident}.jsonl"
    if not arq.is_file():
        return {"ok": False, "msg": "Não achei essa conversa."}
    msgs, atual, por_id = [], None, {}
    try:
        with arq.open(encoding="utf-8", errors="replace") as f:
            for linha in f:
                try:
                    ev = json.loads(linha)
                except ValueError:
                    continue
                tipo, conteudo = ev.get("type"), (ev.get("message") or {}).get("content")
                if tipo == "user":
                    if isinstance(conteudo, list) and any(isinstance(b, dict) and b.get("type") == "tool_result"
                                                          for b in conteudo):
                        for b in conteudo:
                            if isinstance(b, dict) and b.get("type") == "tool_result" and b.get("tool_use_id") in por_id:
                                por_id[b["tool_use_id"]]["estado"] = "erro" if b.get("is_error") else "ok"
                        continue
                    txt = _texto_usuario(conteudo)
                    if ev.get("isMeta") or not _pedido_de_gente(txt):
                        continue
                    msgs.append({"quem": "eu", "texto": mascarar(txt.strip())[:4000]})
                    atual = None
                elif tipo == "assistant" and isinstance(conteudo, list):
                    if atual is None:
                        atual = {"quem": "ia", "texto": "", "partes": [], "acoes": []}
                        msgs.append(atual)
                    for b in conteudo:
                        if not isinstance(b, dict):
                            continue
                        if b.get("type") == "text" and str(b.get("text") or "").strip():
                            tx = mascarar(str(b["text"]))
                            atual["texto"] += tx + "\n\n"
                            if atual["partes"] and atual["partes"][-1]["t"] == "texto":
                                atual["partes"][-1]["texto"] += "\n\n" + tx
                            else:
                                atual["partes"].append({"t": "texto", "texto": tx})
                        elif b.get("type") == "tool_use":
                            resumo, detalhe = _resumo_claude(b.get("name"), b.get("input"))
                            acao = {"id": str(b.get("id")), "estado": "ok", "resumo": mascarar(resumo),
                                    "detalhe": mascarar(detalhe)}
                            if b.get("name") in ("Write", "Edit", "MultiEdit"):
                                rel = _arquivo_chat((b.get("input") or {}).get("file_path"))
                                if rel:
                                    acao["arquivos"] = [rel]
                            atual["acoes"].append(acao)
                            atual["partes"].append({"t": "acao", "id": acao["id"]})
                            por_id[acao["id"]] = acao
    except OSError:
        return {"ok": False, "msg": "Não consegui ler essa conversa."}
    return {"ok": True, "id": ident, "msgs": msgs[-40:]}


def parar(conversa=None, cli=None):
    if conversa is not None and not ID_OK.match(str(conversa)):
        return {"ok": False, "msg": "Conversa desconhecida."}
    if cli is not None and cli not in NOMES:
        return {"ok": False, "msg": "Escolha o Claude ou o Codex."}
    if not conversa and not cli:
        return {"ok": False, "msg": "Diga qual conversa parar."}
    ok = CONVERSAS.parar(conversa=conversa, cli=cli)
    return {"ok": ok, "msg": "Parei a IA." if ok else "Não havia nada rodando."}


def parar_todas():
    CONVERSAS.parar()


def ocupado():
    return CONVERSAS.alguma()
