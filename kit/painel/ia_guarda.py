# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Guarda do chat do painel: gancho PreToolUse do Claude Code que confere cada ação antes de ela rodar.

O ia.py passa este arquivo ao Claude Code (--settings, hooks.PreToolUse). O Claude Code manda a ação em JSON pela
entrada padrão; a guarda sai com 0 (segue para as regras de permissão do próprio CLI) ou com 2 (bloqueia, e a
mensagem da saída de erro volta para a IA). Qualquer falha aqui também bloqueia.

O que passa:
- ler qualquer arquivo dentro da pasta do estúdio (menos a licença e arquivos de segredo);
- editar dentro do estúdio, menos o código do kit (kit/, exceto config.json, config_16x9.json, estilo.json e as pastas
  de produção series/, canais/ e trabalho/), os arquivos de entrada da IA e qualquer arquivo que rode sozinho (.py, .bat, .ps1, .sh...);
- rodar `python` de um script que já existe em kit/ (ou `python -m <módulo do kit>` de dentro de kit/), `ffmpeg` e
  `ffprobe`, e comandos só de leitura (ls, cat, grep...). Todo caminho citado tem de ficar dentro do estúdio.

Uso (só pelo Claude Code): python -I ia_guarda.py <pasta do estúdio>
"""
import json
import os
import re
import sys
import tempfile
from pathlib import Path, PurePosixPath

MARCA = "FORA DO PERMITIDO NO CHAT DO PAINEL"
VERBOS_ARQUIVO = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
LEITURA = {"Read", "Glob", "Grep"}
SHELL = {"Bash", "PowerShell"}
# Arquivos do kit que a IA ajusta na instalação (o resto de kit/ é código e só muda por versão nova).
KIT_EDITAVEIS = {"config.json", "config_16x9.json", "estilo.json"}
# Pastas de produção dentro de kit/: episódio, canais e trabalho (o código continua de fora).
KIT_PRODUCAO = {"trabalho", "series", "canais"}
# Onde a IA pode criar o programa da cena do episódio (.py) e rodá-lo: só nas pastas de produção.
CENA_PY_KIT = {"series", "trabalho"}
RAIZ_PROTEGIDA = {"claude.md", "agents.md", "licenca_e_termos.md", ".licenca.json", "abrir-painel.bat",
                  "abrir-painel.command"}
EXT_EXECUTAVEL = {".py", ".pyw", ".pth", ".bat", ".cmd", ".ps1", ".psm1", ".sh", ".command", ".vbs", ".js",
                  ".mjs", ".lnk", ".exe", ".dll", ".app", ".scpt", ".desktop"}
SEGREDO = re.compile(r"(^|/)(\.licenca\.json|\.env|[^/]*\.segredos\.json|[^/]*segredos[^/]*)$", re.I)
# Scripts do kit que o chat não roda: publicar mexe na conta da pessoa e pede a aprovação do terminal de verdade.
SCRIPTS_FORA = ("publicar/",)
LEITURA_CMD = {"ls", "dir", "cat", "type", "head", "tail", "wc", "echo", "pwd", "grep", "findstr", "sort", "uniq",
               "du", "stat", "file", "tree", "which", "where", "find", "get-childitem", "gci", "get-content", "gc",
               "select-string", "sls", "test-path", "get-location", "write-output", "measure-object",
               "select-object", "get-item", "resolve-path", "get-command", "test", "sleep",
               "start-sleep", "true"}
CD = {"cd", "set-location", "sl", "chdir", "pushd", "popd"}
PYTHON = re.compile(r"^(python(3(\.\d+)?)?|py)$")
FLAGS_PY_SOLTAS = {"-u", "-B", "-I", "-E", "-s", "-S", "-O", "-OO", "-q"}
FFMPEG = {"ffmpeg", "ffprobe"}
REDE = re.compile(r"(://|^(tcp|udp|rtmp\w*|rtsp|srt|ftp|sftp|http|https|ws|wss)[:])", re.I)
SEPARADOR = re.compile(r"\|\||&&|[;|&\n]")
REDIR_OK = re.compile(r"\s(\d?>&\d|\d?>\s*/dev/null|\d?>\s*\$null|\d?>\s*nul)\b", re.I)


class Fora(Exception):
    pass


def _normaliza(txt):
    """Caminho do jeito do Git Bash (/c/pasta) vira C:/pasta no Windows."""
    txt = str(txt).strip().strip('"').strip("'")
    if os.name == "nt":
        m = re.match(r"^/([a-zA-Z])(/|$)(.*)", txt)
        if m:
            txt = f"{m.group(1).upper()}:/{m.group(3)}"
    return txt


def _resolver(txt, cwd):
    p = Path(os.path.expanduser(_normaliza(txt)))
    if not p.is_absolute():
        p = Path(cwd) / p
    return Path(os.path.realpath(p))


def _dentro(p, raiz):
    try:
        p.relative_to(raiz)
        return True
    except ValueError:
        return False


def _rel(p, raiz):
    return PurePosixPath(p.relative_to(raiz).as_posix())


def _pasta_de_cena(partes):
    """series/<serie>/... na raiz do estúdio ou kit/series|trabalho/...: onde o episódio guarda o programa da cena."""
    return (len(partes) >= 3 and partes[0] == "series") or \
        (len(partes) >= 4 and partes[0] == "kit" and partes[1] in CENA_PY_KIT)


def _saida_de_tarefa(txt):
    """Arquivo de saída de um comando que a própria IA deixou rodando ao fundo (voz, render): só leitura."""
    try:
        p = Path(os.path.realpath(_normaliza(txt)))
        base = Path(os.path.realpath(tempfile.gettempdir())) / "claude"
        p.relative_to(base)
    except (ValueError, OSError):
        return False
    return p.suffix.lower() in (".output", ".txt", ".log", "")


def conferir_caminho(txt, cwd, estudio, escrita=False):
    p = _resolver(txt, cwd)
    if not _dentro(p, estudio):
        raise Fora(f"o caminho {txt} fica fora da pasta do estúdio.")
    rel = _rel(p, estudio)
    rel_txt = rel.as_posix()
    if SEGREDO.search("/" + rel_txt):
        raise Fora("arquivos de licença e de segredo não são abertos pelo chat.")
    if any(parte.lower() == ".claude" for parte in rel.parts):
        raise Fora("a configuração da IA não é mexida pelo chat.")
    if escrita:
        partes = [x.lower() for x in rel.parts]
        if len(partes) == 1 and partes[0] in RAIZ_PROTEGIDA:
            raise Fora(f"{rel_txt} é um arquivo do kit e não muda pelo chat.")
        if partes and partes[0] == "kit":
            ok = (len(partes) == 2 and partes[1] in KIT_EDITAVEIS) or (len(partes) >= 3 and partes[1] in KIT_PRODUCAO)
            if not ok:
                raise Fora(f"{rel_txt} é código do kit e não muda pelo chat.")
        if p.suffix.lower() in EXT_EXECUTAVEL or rel_txt.lower().endswith(".app"):
            if not (p.suffix.lower() == ".py" and _pasta_de_cena(partes)):
                raise Fora("o chat só cria programa (.py) dentro da pasta do episódio (series/ ou kit/series/); "
                           "atalhos e outros scripts não.")
    return p


def _tokens(segmento):
    """Divide em palavras respeitando aspas. Sem escape por barra invertida (caminho do Windows usa barra)."""
    out, atual, aspas, tem = [], [], "", False
    for ch in segmento:
        if aspas:
            if ch == aspas:
                aspas = ""
            else:
                atual.append(ch)
        elif ch in "\"'":
            aspas, tem = ch, True
        elif ch.isspace():
            if atual or tem:
                out.append("".join(atual))
            atual, tem = [], False
        else:
            atual.append(ch)
    if aspas:
        raise Fora("o comando tem aspas sem fechar.")
    if atual or tem:
        out.append("".join(atual))
    return out


def _parece_caminho(tok):
    t = _normaliza(tok)
    return bool(re.match(r"^([a-zA-Z]:[\\/]|[\\/]|~)", t)) or ".." in re.split(r"[\\/]", t)


def _conferir_args(args, cwd, estudio, rede_ok=True):
    for a in args:
        valor = a.split("=", 1)[1] if a.startswith("-") and "=" in a else a
        if not rede_ok and REDE.search(valor):
            raise Fora("acesso à rede por este comando não é permitido.")
        if valor.startswith("\\\\"):
            raise Fora("caminho de rede não é permitido.")
        if _parece_caminho(valor) and not REDE.search(valor):
            conferir_caminho(valor, cwd, estudio)


def _modulo_do_kit(nome, cwd, estudio):
    kit = estudio / "kit"
    if not _dentro(Path(cwd), kit):
        raise Fora("`python -m` só roda de dentro da pasta kit/.")
    if not re.match(r"^[A-Za-z_][\w.]*$", nome):
        raise Fora(f"módulo {nome} desconhecido.")
    base = Path(cwd).joinpath(*nome.split("."))
    if not (base.with_suffix(".py").is_file() or (base / "__init__.py").is_file() or (base / "__main__.py").is_file()):
        raise Fora(f"{nome} não é um módulo do kit. Para conferir ou instalar o que falta, rode "
                   "`python instalar_recursos.py --conferir` (ou `python instalar_recursos.py voz-gratis`) a partir de kit/.")


def _conferir_python(args, cwd, estudio):
    kit = estudio / "kit"
    i = 0
    while i < len(args):
        a = args[i]
        if a in FLAGS_PY_SOLTAS or re.match(r"^-3(\.\d+)?$", a) or re.match(r"^-W\S+$", a):
            i += 1
            continue
        if a in ("-X", "-W"):
            i += 2
            continue
        if a == "-m":
            if i + 1 >= len(args):
                raise Fora("faltou o módulo depois de -m.")
            _modulo_do_kit(args[i + 1], cwd, estudio)
            _conferir_args(args[i + 2:], cwd, estudio)
            return
        if a.startswith("-"):
            raise Fora(f"a opção {a} do python não é permitida (só scripts do kit). Para conferir se algo está "
                       "instalado, rode `python instalar_recursos.py --conferir` a partir de kit/.")
        script = _resolver(a, cwd)
        if script.suffix.lower() != ".py" or not script.is_file() or \
                not (_dentro(script, kit) or _dentro(script, estudio / "series")):
            raise Fora("o python só roda scripts do kit/ e o programa da cena do episódio (series/).")
        rel = _rel(script, kit).as_posix() if _dentro(script, kit) else ""
        if rel.startswith(SCRIPTS_FORA):
            raise Fora("publicar nas redes pede a aprovação no terminal de verdade.")
        _conferir_args(args[i + 1:], cwd, estudio)
        return
    raise Fora("o python sem script (modo interativo) não é permitido.")


def _segmentos(cmd):
    """Divide em comandos (;, |, &, &&, ||, quebra de linha) sem quebrar o que está entre aspas."""
    segs, atual, aspas, i = [], [], "", 0
    while i < len(cmd):
        ch = cmd[i]
        if aspas:
            atual.append(ch)
            if ch == aspas:
                aspas = ""
        elif ch in "\"'":
            aspas = ch
            atual.append(ch)
        elif cmd.startswith("&&", i) or cmd.startswith("||", i):
            segs.append("".join(atual))
            atual = []
            i += 2
            continue
        elif ch in ";|&\n":
            segs.append("".join(atual))
            atual = []
        else:
            atual.append(ch)
        i += 1
    segs.append("".join(atual))
    return segs


def conferir_comando(cmd, cwd, estudio):
    if len(cmd) > 4000:
        raise Fora("comando longo demais.")
    if re.search(r"[$`]|<\(|>\(", cmd):
        raise Fora("variáveis e subcomandos ($, crase) não são permitidos; rode um comando simples.")
    limpo = REDIR_OK.sub(" ", " " + cmd)
    if re.search(r"[<>]", limpo):
        raise Fora("redirecionar a saída (> ou <) não é permitido; o script do kit já grava onde precisa.")
    for seg in _segmentos(limpo):
        toks = _tokens(seg.strip())
        if toks and toks[0] == "&":  # operador de chamada do PowerShell
            toks = toks[1:]
        while toks and toks[0].lower() in ("timeout", "time", "nice") and len(toks) > 1:
            toks = toks[2:] if toks[0].lower() == "timeout" else toks[1:]
        if not toks:
            continue
        if re.match(r"^[A-Za-z_]\w*=", toks[0]):
            raise Fora("mudar variável de ambiente antes do comando não é permitido.")
        prog = re.sub(r"\.exe$", "", Path(_normaliza(toks[0])).name.lower())
        args = toks[1:]
        if prog in CD:
            destino = next((a for a in args if not a.startswith("-")), str(estudio))
            novo = _resolver(destino, cwd) if prog != "popd" else Path(cwd)
            if not _dentro(novo, estudio):
                raise Fora("o chat só trabalha dentro da pasta do estúdio.")
            cwd = novo
        elif PYTHON.match(prog):
            _conferir_python(args, cwd, estudio)
        elif prog in FFMPEG:
            _conferir_args(args, cwd, estudio, rede_ok=False)
        elif prog in LEITURA_CMD:
            if prog == "find" and any(a.lower() in ("-exec", "-execdir", "-delete", "-ok", "-okdir", "-fprint",
                                                    "-fprintf", "-fls") for a in args):
                raise Fora("find só para procurar, sem apagar nem rodar nada.")
            for a in args:
                if not a.startswith("-"):
                    conferir_caminho(a, cwd, estudio)
        else:
            raise Fora(f"o comando {toks[0]} não é permitido aqui (só python dos scripts do kit, ffmpeg, ffprobe "
                       "e leitura).")
    return True


def conferir(ferramenta, entrada, cwd, estudio):
    if ferramenta in SHELL:
        return conferir_comando(str(entrada.get("command") or ""), cwd, estudio)
    if ferramenta in VERBOS_ARQUIVO:
        alvo = entrada.get("file_path") or entrada.get("notebook_path") or entrada.get("path")
        if not alvo:
            raise Fora("edição sem arquivo.")
        conferir_caminho(alvo, cwd, estudio, escrita=True)
        return True
    if ferramenta in LEITURA:
        alvo = entrada.get("file_path") or entrada.get("path")
        if alvo and ferramenta == "Read" and _saida_de_tarefa(alvo):
            return True
        if alvo:
            conferir_caminho(alvo, cwd, estudio)
        return True
    # Ferramentas internas que não tocam em arquivo nem em rede (lista de tarefas, fim de conversa) seguem; o
    # resto já fica de fora pela lista de ferramentas que o ia.py libera.
    return True


def main():
    try:
        estudio = Path(os.path.realpath(sys.argv[1]))
        pedido = json.loads(sys.stdin.buffer.read().decode("utf-8") or "{}")
        cwd = _normaliza(pedido.get("cwd") or estudio)
        if not _dentro(Path(os.path.realpath(cwd)), estudio):
            cwd = str(estudio)
        conferir(str(pedido.get("tool_name") or ""), pedido.get("tool_input") or {}, cwd, estudio)
        return 0
    except Fora as e:
        motivo = str(e)
    except Exception as e:  # noqa: BLE001  (na dúvida, bloqueia)
        motivo = f"não consegui conferir esta ação ({type(e).__name__})."
    try:
        sys.stderr.buffer.write((f"{MARCA}: {motivo} Siga pelo caminho permitido: scripts do kit, a pasta "
                                 "do episódio e, para instalar o que falta, `python instalar_recursos.py` (a "
                                 "partir de kit/). Não mande a pessoa para o terminal.").encode("utf-8"))
        sys.stderr.flush()
    except Exception:  # noqa: BLE001
        pass
    return 2


if __name__ == "__main__":
    sys.exit(main())
