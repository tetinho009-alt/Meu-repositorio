# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Criar meu estilo pelo painel (comandos/criar-estilo.md sem a conversa): as respostas viram o sorteio do
estilo desenhado (estilo_desenhado/estilo.py) e a folha de conferência (estilo_desenhado/folha.py), rodados em
segundo plano com o mesmo Python do painel. Nada muda no canal até a pessoa escolher "Gostei, usar".

As perguntas e as opções vêm do estilo.py instalado (lidas do código, sem importar), então o painel acompanha a
versão do kit que a pessoa tem.
"""
import ast
import json
import os
import random
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

import dados

ESTILO_PY = dados.KIT / "estilo_desenhado" / "estilo.py"
FOLHA_PY = dados.KIT / "estilo_desenhado" / "folha.py"
SERIES = ("serie-2d-voto", "terror-voto", "pov")   # estilos do catálogo que usam o estilo desenhado
CLIMAS_SERIOS = ("sombrio", "melancolico")
_cache = {"mtime": None, "perguntas": None}


def _pasta():
    p = dados.trabalho() / "estilo"
    p.mkdir(parents=True, exist_ok=True)
    return p


def perguntas():
    """[(id, pergunta, [(opcao, explicacao), ...]), ...] do estilo.py instalado; [] se não houver."""
    try:
        mtime = ESTILO_PY.stat().st_mtime
    except OSError:
        return []
    if _cache["mtime"] == mtime:
        return _cache["perguntas"]
    lista = []
    try:
        arvore = ast.parse(ESTILO_PY.read_text(encoding="utf-8"))
        for no in arvore.body:
            if isinstance(no, ast.Assign) and any(getattr(t, "id", "") == "PERGUNTAS" for t in no.targets):
                for k, (q, ops) in ast.literal_eval(no.value).items():
                    lista.append({"id": k, "pergunta": q, "opcoes": [{"id": o, "texto": d} for o, d in ops.items()]})
    except (OSError, SyntaxError, ValueError, TypeError):
        lista = []
    _cache.update(mtime=mtime, perguntas=lista)
    return lista


def _estilo_atual():
    e = dados.ler_json(dados.KIT / "estilo.json", None)
    if not isinstance(e, dict) or "respostas" not in e:
        return {"tem": False}
    folha = _pasta() / "folha.jpg"
    return {"tem": True, "nome": str(e.get("nome") or ""), "semente": e.get("semente"),
            "respostas": e.get("respostas") or {},
            "folha": dados.chave_midia(folha) if folha.is_file() else None}


class Sorteio:
    """Um sorteio por vez. O estado fica em memória; a proposta fica em trabalho/estilo/painel_*."""

    def __init__(self):
        self.trava = threading.Lock()
        self.n = 0
        self.rodando = False
        self.fase = ""
        self.ok = False
        self.erro = ""
        self.falta = False
        self.resultado = {}
        self.respostas = {}
        self.nome = ""

    def estado(self):
        with self.trava:
            return {"n": self.n, "rodando": self.rodando, "fase": self.fase, "ok": self.ok, "erro": self.erro,
                    "falta": self.falta, "resultado": dict(self.resultado), "respostas": dict(self.respostas),
                    "nome": self.nome}

    def comecar(self, respostas, nome):
        lista = perguntas()
        if not lista or not FOLHA_PY.is_file():
            return {"ok": False, "falta": True, "msg": "Esta versão do kit não tem o estilo desenhado."}
        if not isinstance(respostas, dict):
            return {"ok": False, "msg": "Pedido inválido."}
        limpas = {}
        for q in lista:
            validas = [o["id"] for o in q["opcoes"]]
            v = str(respostas.get(q["id"]) or "")
            if v == "auto" or v not in validas:
                if v not in ("", "auto"):
                    return {"ok": False, "msg": "Resposta inválida em: " + q["pergunta"]}
                v = random.SystemRandom().choice(validas)
            limpas[q["id"]] = v
        nome = re.sub(r"\s+", " ", str(nome or "")).strip()[:40]
        with self.trava:
            if self.rodando:
                return {"ok": False, "msg": "Já estou sorteando. Espere terminar."}
            self.n += 1
            self.rodando, self.fase, self.ok, self.erro, self.falta = True, "sorteando", False, "", False
            self.resultado, self.respostas, self.nome = {}, limpas, nome
            n = self.n
        threading.Thread(target=self._executar, args=(n, limpas, nome), daemon=True).start()
        return {"ok": True, "n": n, "respostas": limpas}

    def _fim(self, n, **kw):
        with self.trava:
            if n != self.n:
                return
            for k, v in kw.items():
                setattr(self, k, v)
            self.rodando = False

    def _rodar(self, cmd, env, limite):
        extra = {"creationflags": 0x08000000} if os.name == "nt" else {}  # sem janela de console no Windows
        return subprocess.run(cmd, cwd=str(dados.KIT), capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=limite, env=env, **extra)

    def _executar(self, n, respostas, nome):
        pasta = _pasta()
        arq_resp, proposta, folha = pasta / "painel_respostas.json", pasta / "painel_proposta.json", pasta / f"painel_folha_{n}.jpg"
        for velho in pasta.glob("painel_folha_*.jpg"):
            try:
                velho.unlink()
            except OSError:
                pass
        arq_resp.write_text(json.dumps(respostas, ensure_ascii=False), encoding="utf-8")
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
        try:
            # estilo.py como arquivo (não como módulo): o sorteio não precisa das bibliotecas de desenho
            r = self._rodar([sys.executable, str(ESTILO_PY), "--respostas", str(arq_resp), "--saida", str(proposta)], env, 240)
            m = re.search(r"ESTILO_OK .* semente (\d+)", r.stdout)
            if r.returncode != 0 or not m:
                return self._fim(n, erro=_motivo(r.stderr), falta=_falta(r.stderr))
            with self.trava:
                if n == self.n:
                    self.fase = "desenhando"
            r = self._rodar([sys.executable, "-m", "estilo_desenhado.folha", str(folha)], dict(env, ESTILO_JSON=str(proposta)), 300)
            if r.returncode != 0 or not folha.is_file():
                return self._fim(n, erro=_motivo(r.stderr), falta=_falta(r.stderr))
            e = dados.ler_json(proposta, {}) or {}
            bruto = e.get("elenco") or []
            bruto = list(bruto.values()) if isinstance(bruto, dict) else bruto
            elenco = [str(p.get("nome") or "") for p in bruto if isinstance(p, dict)]
            self._fim(n, ok=True, fase="pronto", resultado={
                "semente": int(m.group(1)), "folha": dados.chave_midia(folha), "elenco": [x for x in elenco if x],
                "fonte": Path(str((e.get("fontes") or {}).get("titulo") or "")).stem})
        except subprocess.TimeoutExpired:
            self._fim(n, erro="Demorou demais para desenhar. Tente de novo; se repetir, peça pra IA.")
        except Exception as erro:  # noqa: BLE001
            self._fim(n, erro=f"Não consegui rodar o sorteio ({type(erro).__name__}).")

    def usar(self):
        with self.trava:
            if self.rodando or not self.ok:
                return {"ok": False, "msg": "Sorteie um estilo antes."}
            respostas, nome, res = dict(self.respostas), self.nome, dict(self.resultado)
        pasta = _pasta()
        proposta = pasta / "painel_proposta.json"
        e = dados.ler_json(proposta, None)
        folha = dados.resolver_midia(res.get("folha"))
        if not isinstance(e, dict) or not folha:
            return {"ok": False, "msg": "A prévia sumiu. Sorteie de novo."}
        if nome:
            e["nome"] = nome
        destino = dados.KIT / "estilo.json"
        if destino.is_file():
            shutil.copy2(destino, pasta / f"estilo_antes_{time.strftime('%Y%m%d_%H%M%S')}.json")
        tmp = destino.with_suffix(".tmp")
        tmp.write_text(json.dumps(e, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(destino)
        shutil.copy2(folha, pasta / "folha.jpg")
        (pasta / "respostas.json").write_text(json.dumps(respostas, ensure_ascii=False, indent=1), encoding="utf-8")
        _anotar_identidade(e)
        avisos, padrao = [], ""
        p = dados.prefs()
        if p:
            atual = (p.carregar().get("roteiro") or {}).get("estilo_padrao")
            padrao = atual if atual in SERIES else ("terror-voto" if respostas.get("clima") in CLIMAS_SERIOS else "serie-2d-voto")
            if padrao != atual:
                ok, erros, avisos = p.salvar({"roteiro": {"estilo_padrao": padrao}})
                if not ok:
                    padrao = atual or ""
        return {"ok": True, "estilo_padrao": padrao, "avisos": avisos}


def _falta(stderr):
    return bool(re.search(r"No module named|ModuleNotFoundError|ImportError|DLL load failed", stderr or ""))


def _motivo(stderr):
    if _falta(stderr):
        return "Faltam partes do programa de desenho neste computador."
    ultima = [x for x in (stderr or "").strip().splitlines() if x.strip()]
    if ultima and "nenhum sorteio passou" in ultima[-1]:
        return "Essas respostas não fecharam um estilo legível. Mude uma resposta e tente de novo."
    return "O desenho não saiu desta vez. Tente de novo; se repetir, peça pra IA."


def _anotar_identidade(e):
    """A linha que o comandos/criar-estilo.md pede em canal/identidade.md, trocada se já existir."""
    R = e.get("respostas") or {}
    linha = (f"Estilo: semente {e.get('semente')}, {R.get('clima', '')} · {R.get('recorte', R.get('traco', ''))} · "
             f"{R.get('cor', '')} · {R.get('proporcao', '')} · {R.get('textura', '')}")
    if e.get("nome"):
        linha += f" (\"{e['nome']}\")"
    arq = dados.CANAL / "identidade.md"
    try:
        texto = arq.read_text(encoding="utf-8") if arq.is_file() else "# Identidade do canal\n"
        if re.search(r"^Estilo: semente .*$", texto, re.M):
            texto = re.sub(r"^Estilo: semente .*$", linha, texto, count=1, flags=re.M)
        else:
            texto = texto.rstrip("\n") + "\n\n" + linha + "\n"
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto, encoding="utf-8")
    except OSError:
        pass


SORTEIO = Sorteio()


def payload():
    return {"disponivel": bool(perguntas()) and FOLHA_PY.is_file(), "perguntas": perguntas(),
            "atual": _estilo_atual(), "sorteio": SORTEIO.estado()}
