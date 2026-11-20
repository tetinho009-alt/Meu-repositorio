# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Estudar vídeos pelo painel: roda o `python -m estudo` do kit em segundo plano (um estudo por vez, em fila), recebe
o vídeo que a pessoa sobe e devolve os estudos, o raio-x e a comparação do nicho.

Na primeira vez, instala sozinho o que falta (`instalar_recursos.py estudo`: o leitor de links e o Whisper), sem
terminal. Nada aqui usa login, cookies ou contorno de bloqueio: quando a rede bloqueia, o painel pede o arquivo.
"""
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import threading
from datetime import datetime

import dados

EXT_VIDEO = {".mp4", ".mov", ".m4v", ".webm", ".mkv", ".mp3", ".m4a", ".wav", ".aac", ".ogg", ".opus"}
MAX_VIDEO = 600 * 1024 * 1024
LIMITE_S = 1800          # um estudo (com o download do modelo na primeira vez) não passa de 30 min
FILA_MAX = 10


def _estudo():
    """O pacote kit/estudo (importado só na hora: o painel abre mesmo se ele faltar numa versão antiga)."""
    try:
        import estudo
        from estudo import nicho, raiox
        return estudo, nicho, raiox
    except ImportError:
        return None, None, None


def _tem(modulo):
    try:
        return importlib.util.find_spec(modulo) is not None
    except (ImportError, ValueError):
        return False


def recursos():
    return {"leitor": _tem("yt_dlp"), "whisper": _tem("faster_whisper"), "disponivel": _estudo()[0] is not None}


def _sem_janela():
    return {"creationflags": 0x08000000} if os.name == "nt" else {}


class Trabalho:
    """Fila de estudos. O estado fica em memória; o resultado de cada um vai para canal/estudos/<id>/."""

    def __init__(self):
        self.trava = threading.Lock()
        self.fila = []
        self.rodando = False
        self.fase = ""
        self.atual = ""
        self.feitos = []
        self.erros = []
        self.proc = None
        self.parar_pedido = False
        self.atualizou = False   # o leitor de links é atualizado no máximo uma vez por abertura do painel

    def estado(self):
        with self.trava:
            return {"rodando": self.rodando, "fase": self.fase, "atual": self.atual, "na_fila": len(self.fila),
                    "feitos": list(self.feitos), "erros": list(self.erros)}

    def comecar(self, entradas, apagar=False):
        entradas = [str(e).strip() for e in (entradas or []) if str(e or "").strip()]
        for e in entradas:
            if not (re.match(r"^https?://[^\s]{4,2000}$", e) or os.path.isfile(e)):
                return {"ok": False, "msg": "Cole o link inteiro do vídeo, começando com https://."}
        with self.trava:
            if len(self.fila) + len(entradas) > FILA_MAX:
                return {"ok": False, "msg": f"Dá pra pôr até {FILA_MAX} vídeos na fila de uma vez."}
            if not self.rodando:
                self.feitos, self.erros = [], []
            self.fila += [(e, apagar) for e in entradas]
            ja = self.rodando
            self.rodando = True
            self.parar_pedido = False
            if not ja:
                self.fase = "Começando"
        if not ja:
            threading.Thread(target=self._executar, daemon=True).start()
        return {"ok": True}

    def parar(self):
        with self.trava:
            self.fila.clear()
            self.parar_pedido = True
            p = self.proc
        if p and p.poll() is None:
            try:
                p.kill()
            except OSError:
                pass
        return {"ok": True}

    def _fase(self, texto, atual=None):
        with self.trava:
            self.fase = texto
            if atual is not None:
                self.atual = atual

    def _rodar(self, cmd, ao_ler):
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
        p = subprocess.Popen(cmd, cwd=str(dados.KIT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                             encoding="utf-8", errors="replace", env=env, **_sem_janela())
        with self.trava:
            self.proc = p
        linhas = []
        timer = threading.Timer(LIMITE_S, p.kill)
        timer.start()
        try:
            for linha in p.stdout:
                linha = linha.rstrip()
                linhas.append(linha)
                ao_ler(linha)
            p.wait()
        finally:
            timer.cancel()
            with self.trava:
                self.proc = None
        return p.returncode, linhas

    def _instalar(self, receita, fase, *extra):
        self._fase(fase)
        cod, linhas = self._rodar([sys.executable, str(dados.KIT / "instalar_recursos.py"), receita, *extra],
                                  lambda _l: None)
        importlib.invalidate_caches()
        return cod, linhas

    def preparar(self):
        """Só o leitor de links (pequeno), na primeira vez. O Whisper, que é pesado, entra só quando precisa ouvir um
        arquivo ou um vídeo sem legenda (preparar_whisper): assim o YouTube com legenda funciona em qualquer
        computador, mesmo onde o Whisper não instalar. Devolve (ok, mensagem)."""
        if recursos()["leitor"]:
            return True, ""
        cod, linhas = self._instalar("estudo", "Preparando o estudo de vídeos (só na primeira vez, 1 minuto)")
        if cod == 0 and recursos()["leitor"]:
            return True, ""
        return False, _erro_de(linhas) or "Não consegui preparar o estudo de vídeos. Confira a internet e tente de novo."

    def preparar_whisper(self):
        if recursos()["whisper"]:
            return True
        self._instalar("tempos", "Instalando o ouvido do estudo, o Whisper (só na primeira vez, uns 3 minutos)")
        return recursos()["whisper"]

    def _executar(self):
        try:
            ok, msg = self.preparar()
            if not ok:
                with self.trava:
                    self.erros.append({"entrada": "", "msg": msg, "bloqueado": False})
                    self.fila.clear()
            while True:
                with self.trava:
                    if not self.fila or self.parar_pedido:
                        break
                    entrada, apagar = self.fila.pop(0)
                nome = os.path.basename(entrada) if os.path.isfile(entrada) else entrada
                self._fase("Começando", nome)
                cmd = [sys.executable, "-m", "estudo", entrada] + (["--apagar-entrada"] if apagar else [])
                ident = []

                def ler(linha):
                    if linha.startswith("ETAPA: "):
                        self._fase(linha[7:].strip())
                    elif linha.startswith("ESTUDO_OK "):
                        ident.append(linha.split()[1])
                if os.path.isfile(entrada):
                    self.preparar_whisper()
                cod, linhas = self._rodar(cmd, ler)
                if cod == 3 and not recursos()["whisper"] and self.preparar_whisper():
                    # Vídeo sem legenda: precisou ouvir o áudio e o Whisper ainda não estava instalado.
                    self._fase("Tentando de novo")
                    cod, linhas = self._rodar(cmd, ler)
                if cod == 3:
                    linhas = linhas + ["ERRO: Este computador não conseguiu instalar o Whisper, que ouve o vídeo.",
                                       "O QUE FAZER: vídeos do YouTube com legenda funcionam sem ele. Para ouvir "
                                       "arquivos, peça no chat da IA: instala o Whisper."]
                    linhas = [ln for ln in linhas if not ln.startswith(("ERRO: falta", "O QUE FAZER: rode"))]
                if cod == 1 and not self.atualizou and entrada.startswith("http") and "abrir esse link" in _erro_de(linhas):
                    # O YouTube muda e o leitor de links velho para de abrir: atualiza uma vez e tenta de novo.
                    self.atualizou = True
                    self._instalar("estudo", "Atualizando o leitor de links", "--atualizar")
                    self._fase("Tentando de novo")
                    cod, linhas = self._rodar(cmd, ler)
                with self.trava:
                    if self.parar_pedido:
                        break
                    if cod == 0 and ident:
                        self.feitos.append(ident[0])
                    else:
                        self.erros.append({"entrada": nome, "bloqueado": cod == 2, "local": os.path.isfile(entrada),
                                           "msg": _erro_de(linhas) or "Não consegui estudar esse vídeo."})
                if apagar and os.path.isfile(entrada) and cod != 0:
                    try:
                        os.remove(entrada)
                    except OSError:
                        pass
        except Exception as e:  # noqa: BLE001
            with self.trava:
                self.erros.append({"entrada": self.atual, "msg": f"O estudo parou ({type(e).__name__}).", "bloqueado": False})
        finally:
            with self.trava:
                self.rodando, self.fase, self.atual, self.parar_pedido = False, "", "", False
                self.fila.clear()


def _erro_de(linhas):
    """"ERRO: ..." e "O QUE FAZER: ..." da saída do kit, juntos numa frase para a tela."""
    erro = next((ln[5:].strip() for ln in linhas if ln.startswith("ERRO:")), "")
    fazer = next((ln[12:].strip() for ln in linhas if ln.startswith("O QUE FAZER:")), "")
    return (erro + (" " + fazer if fazer else "")).strip()


TRABALHO = Trabalho()


# ---------------------------------------------------------------- leitura dos estudos

def payload():
    est, _, _ = _estudo()
    return {"recursos": recursos(), "estado": TRABALHO.estado(), "lista": est.listar() if est else [],
            "min_nicho": getattr(est, "MIN_NICHO", 3)}


def ver(ident):
    est, _, raiox = _estudo()
    if not est or not est.id_valido(ident):
        return {"ok": False, "msg": "Estudo não encontrado."}
    e = est.ler_estudo(ident)
    if not e:
        return {"ok": False, "msg": "Esse estudo não existe mais."}
    m = e.get("molde")
    return {"ok": True, "estudo": e, "resumo": est.resumo(e),
            "molde_curto": raiox.molde_curto(m) if m else "",
            "molde_arquivo": f"canal/estudos/{ident}/molde.md" if m else "",
            "txt": dados.chave_midia(est.pasta_estudo(ident) / "transcricao.txt")}


def apagar(ident):
    est, _, _ = _estudo()
    if not est or not est.id_valido(ident):
        return {"ok": False, "msg": "Estudo não encontrado."}
    p = est.pasta_estudo(ident)
    if p.is_dir() and p.parent == est.ESTUDOS:
        shutil.rmtree(p, ignore_errors=True)
    return {"ok": True}


def comparar(ids):
    est, nicho, raiox = _estudo()
    if not est:
        return {"ok": False, "msg": "Esta versão do kit não tem o estudo de vídeos."}
    ids = [i for i in (ids or []) if est.id_valido(i)][:20]
    r = nicho.comparar(ids)
    if r.get("ok"):
        r["molde_curto"] = raiox.molde_curto(r["molde"])
        titulos = [x.get("titulo") or x.get("id") for x in r["linhas"]]
        texto = raiox.molde_md(f"nicho ({r['n']} vídeos)", r["molde"], "; ".join(str(t) for t in titulos))
        texto += "\n## O que se repete\n\n" + "\n".join(f"- {p}" for p in r["padroes"]) + "\n"
        if r["varia"]:
            texto += "\n## O que varia\n\n" + "\n".join(f"- {p}" for p in r["varia"]) + "\n"
        try:
            est.ESTUDOS.mkdir(parents=True, exist_ok=True)
            (est.ESTUDOS / "nicho.md").write_text(texto, encoding="utf-8")
            r["molde_arquivo"] = "canal/estudos/nicho.md"
        except OSError:
            r["molde_arquivo"] = ""
    return r


def buscar(termo, curtos):
    if not _tem("yt_dlp"):
        return {"ok": False, "falta": True, "msg": "O estudo de vídeos ainda não foi preparado neste computador."}
    try:
        from estudo.transcrever import ErroEstudo, buscar_youtube
    except ImportError:
        return {"ok": False, "msg": "Esta versão do kit não tem o estudo de vídeos."}
    try:
        return {"ok": True, "itens": buscar_youtube(termo, curtos=bool(curtos))}
    except ErroEstudo as e:
        return {"ok": False, "msg": f"{e} {e.fazer}".strip()}
    except Exception:  # noqa: BLE001
        return {"ok": False, "msg": "A busca no YouTube não respondeu. Confira a internet e tente de novo."}


def preparar_ao_fundo():
    """Só a instalação (a busca precisa do leitor de links): a fila vazia roda o preparar e termina."""
    return TRABALHO.comecar([])


# ---------------------------------------------------------------- vídeo subido pelo navegador

def nome_entrada(nome):
    base, ext = os.path.splitext(os.path.basename(str(nome or "")))
    ext = ext.lower()
    if ext not in EXT_VIDEO:
        return None
    est, _, _ = _estudo()
    s = est.slug(base, 40) if est else re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")[:40]
    return f"{s or 'video'}{ext}"


def receber(leitor, tamanho, nome):
    """Grava o vídeo enviado em trabalho/estudo/entrada/ (em pedaços, sem guardar tudo na memória) e põe na fila."""
    seguro = nome_entrada(nome)
    if not seguro:
        return {"ok": False, "msg": "Esse arquivo não é vídeo nem áudio. Use mp4, mov, webm, mp3 ou m4a."}
    if tamanho <= 0 or tamanho > MAX_VIDEO:
        return {"ok": False, "msg": "O vídeo precisa ter até 600 MB."}
    pasta = dados.trabalho() / "estudo" / "entrada"
    pasta.mkdir(parents=True, exist_ok=True)
    destino = pasta / seguro
    falta = tamanho
    try:
        with open(destino, "wb") as f:
            while falta > 0:
                bloco = leitor.read(min(1 << 20, falta))
                if not bloco:
                    break
                f.write(bloco)
                falta -= len(bloco)
    except OSError:
        falta = 1
    if falta:
        try:
            destino.unlink()
        except OSError:
            pass
        return {"ok": False, "msg": "O envio parou no meio. Tente de novo."}
    r = TRABALHO.comecar([str(destino)], apagar=True)
    return dict(r, arquivo=seguro, quando=datetime.now().isoformat(timespec="seconds"))
