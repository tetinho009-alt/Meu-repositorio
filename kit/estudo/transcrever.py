# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Transcrição de referência: legenda do YouTube quando existe, senão Whisper local (placa NVIDIA se der, senão CPU).

Regra fixa: só conteúdo público, sem login, sem cookies e sem contornar bloqueio. Se a rede pedir login ou
bloquear, levanta Bloqueado e o painel pede o arquivo baixado pelo app.

Escolha do Whisper (sempre o mais rápido que a máquina aguenta, sem perder qualidade):
- placa NVIDIA com as bibliotecas do CUDA presentes: large-v3-turbo na placa (acerta nome e gíria; baixa 1,6 GB uma vez);
- qualquer outro computador: small na CPU (baixa ~460 MB uma vez; o mesmo modelo do alinhar.py).
"""
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import quote, urlparse

CAMPOS_META = ["id", "title", "uploader", "uploader_id", "channel", "duration", "view_count", "like_count",
               "comment_count", "upload_date", "webpage_url", "extractor_key", "language", "width", "height"]
SINAIS_BLOQUEIO = ["login", "log in", "cookies", "private", "privad", "rate-limit", "rate limit", "not available",
                   "unavailable", "unexpected response", "empty media response", "sign in", "confirm you", "blocked",
                   "403", "429"]
TAMANHO_MODELO = {"small": "460 MB", "large-v3-turbo": "1,6 GB"}


class Bloqueado(Exception):
    pass


class ErroEstudo(Exception):
    """Erro com mensagem pronta para o usuário (o que houve e o que fazer)."""

    def __init__(self, msg, fazer=""):
        super().__init__(msg)
        self.fazer = fazer


class _LoggerMudo:
    def debug(self, msg):
        pass

    warning = info = error = debug


def plataforma_de(url):
    host = urlparse(url).netloc.lower()
    if "youtu" in host:
        return "youtube"
    if "tiktok" in host:
        return "tiktok"
    if "instagram" in host:
        return "instagram"
    return "outro"


def _ydl_base(pasta):
    # Sem cookiefile, sem cookiesfrombrowser, sem impersonate: só acesso anônimo.
    return {"quiet": True, "no_warnings": True, "noprogress": True, "cookiefile": None, "logger": _LoggerMudo(),
            "outtmpl": str(Path(pasta) / "%(extractor_key)s_%(id)s.%(ext)s"), "retries": 3, "socket_timeout": 30,
            "js_runtimes": {"deno": {}, "node": {}}}


def _bloqueio(plataforma, erro):
    texto = str(erro)
    if any(s in texto.lower() for s in SINAIS_BLOQUEIO):
        nome = {"instagram": "O Instagram", "tiktok": "O TikTok", "youtube": "O YouTube"}.get(plataforma, "O site")
        return Bloqueado(f"{nome} não deixou abrir esse vídeo sem login (ou ele é privado ou saiu do ar).")
    return None


def extrair_info(url, pasta):
    import yt_dlp
    plat = plataforma_de(url)
    try:
        with yt_dlp.YoutubeDL({**_ydl_base(pasta), "skip_download": True}) as ydl:
            return ydl.extract_info(url, download=False)
    except yt_dlp.utils.DownloadError as e:
        raise _bloqueio(plat, e) or ErroEstudo(
            "Não consegui abrir esse link.",
            "Confira se o link abre no navegador sem login. Se abrir, baixe o vídeo pelo app e suba o arquivo aqui.") from e


def baixar_audio(url, pasta):
    import yt_dlp
    plat = plataforma_de(url)
    try:
        with yt_dlp.YoutubeDL({**_ydl_base(pasta), "format": "bestaudio/best"}) as ydl:
            info = ydl.extract_info(url, download=True)
            return Path(info["requested_downloads"][0]["filepath"]), info
    except yt_dlp.utils.DownloadError as e:
        raise _bloqueio(plat, e) or ErroEstudo(
            "Não consegui baixar o som desse vídeo.",
            "Baixe o vídeo pelo app (ou grave a tela) e suba o arquivo aqui.") from e


def escolher_legenda(info, idioma):
    """(tipo, chave, url_json3) ou None. Só no idioma falado: legenda traduzida pela máquina estraga a análise."""
    original = (info.get("language") or (idioma if idioma != "auto" else "pt")).split("-")[0]
    quer = [original] if idioma in ("auto", original) else [idioma, original]
    manuais = info.get("subtitles") or {}
    autos = info.get("automatic_captions") or {}

    def json3(lista):
        return next((f["url"] for f in lista if f.get("ext") == "json3"), None)

    for pref in quer:
        for chave, lista in manuais.items():
            if chave.split("-")[0] == pref and chave != "live_chat" and json3(lista):
                return "legenda_manual", chave, json3(lista)
    for pref in quer:
        for chave in (f"{pref}-orig", pref):
            if chave in autos and json3(autos[chave]):
                return "legenda_auto", chave, json3(autos[chave])
    return None


def ler_json3(url, pasta, por_palavra):
    import yt_dlp
    with yt_dlp.YoutubeDL(_ydl_base(pasta)) as ydl:
        dados = json.loads(ydl.urlopen(url).read().decode("utf-8"))
    segmentos = []
    for ev in dados.get("events", []):
        partes = ev.get("segs") or []
        texto = "".join(p.get("utf8", "") for p in partes).replace("\n", " ").strip()
        if not texto:
            continue
        ini = ev["tStartMs"] / 1000
        fim = ini + ev.get("dDurationMs", 0) / 1000
        palavras = []
        if por_palavra:  # legenda automática: cada "seg" é uma palavra com deslocamento próprio
            for i, p in enumerate(partes):
                w = p.get("utf8", "").strip()
                if not w:
                    continue
                w_ini = ini + p.get("tOffsetMs", 0) / 1000
                prox = next((q for q in partes[i + 1:] if q.get("utf8", "").strip()), None)
                w_fim = ini + prox.get("tOffsetMs", 0) / 1000 if prox else fim
                palavras.append({"palavra": w, "ini": round(w_ini, 3), "fim": round(w_fim, 3)})
        segmentos.append({"ini": round(ini, 3), "fim": round(fim, 3), "texto": texto, "palavras": palavras})
    # Na legenda automática o fim de um evento invade o seguinte; corta para não sobrepor no SRT.
    for a, b in zip(segmentos, segmentos[1:]):
        a["fim"] = min(a["fim"], b["ini"])
    return segmentos


def _dlls_cuda():
    """No Windows, as DLLs de cuDNN/cuBLAS do PyTorch (se instalado) servem ao CTranslate2."""
    if os.name != "nt":
        return
    try:
        import importlib.util
        spec = importlib.util.find_spec("torch")
        if spec and spec.origin:
            lib = Path(spec.origin).parent / "lib"
            if lib.is_dir():
                os.add_dll_directory(str(lib))
                os.environ["PATH"] = str(lib) + os.pathsep + os.environ.get("PATH", "")
    except Exception:  # noqa: BLE001
        pass


def _cuda_pronto():
    """Placa NVIDIA com as bibliotecas que o Whisper usa. Sonda antes de escolher o turbo: sem isso, o turbo seria
    baixado à toa e o Whisper cairia na CPU no meio da transcrição."""
    try:
        import ctranslate2
        if ctranslate2.get_cuda_device_count() < 1:
            return False
    except Exception:  # noqa: BLE001
        return False
    if os.name != "nt":
        return True
    _dlls_cuda()
    import ctypes
    for dll in ("cublas64_12.dll", "cudnn_ops64_9.dll"):
        try:
            ctypes.WinDLL(dll)
        except OSError:
            return False
    return True


def pasta_modelos(cfg=None):
    """Mesma pasta do alinhar.py (config whisper.pasta_modelos); vazio = cache padrão do Hugging Face."""
    p = os.environ.get("TV_PASTA_WHISPER") or ((cfg or {}).get("whisper") or {}).get("pasta_modelos") or ""
    return str(Path(p).expanduser()) if p else None


def _modelo_baixado(nome, raiz):
    repo = {"small": "Systran--faster-whisper-small",
            "large-v3-turbo": "mobiuslabsgmbh--faster-whisper-large-v3-turbo"}.get(nome, "")
    base = Path(raiz) if raiz else Path(os.environ.get("HF_HOME") or Path.home() / ".cache" / "huggingface") / "hub"
    return bool(repo) and (base / f"models--{repo}").is_dir()


def _exe(nome, cfg=None):
    """ffmpeg/ffprobe: o do config, o que o painel instalou (~/.temporada-viral/ffmpeg) ou o do sistema."""
    dado = (((cfg or {}).get("ferramentas") or {}).get(nome) or "").strip()
    if dado and Path(dado).is_file():
        return dado
    local = Path.home() / ".temporada-viral" / "ffmpeg" / (nome + (".exe" if os.name == "nt" else ""))
    return str(local) if local.is_file() else shutil.which(nome)


def _sem_janela():
    return {"creationflags": 0x08000000} if os.name == "nt" else {}


def carregar_audio(arquivo, cfg=None):
    """Áudio mono 16 kHz em float32. ffmpeg primeiro (lê qualquer coisa); sem ele, o PyAV que vem com o Whisper."""
    import numpy as np
    ff = _exe("ffmpeg", cfg)
    if ff:
        r = subprocess.run([ff, "-v", "error", "-i", str(arquivo), "-vn", "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                           capture_output=True, **_sem_janela())
        if r.returncode == 0 and r.stdout:
            return np.frombuffer(r.stdout, dtype=np.float32)
    from faster_whisper import decode_audio
    try:
        return decode_audio(str(arquivo), sampling_rate=16000)
    except Exception as e:  # noqa: BLE001
        raise ErroEstudo("Não consegui ler o som desse arquivo.",
                         "Confira se é um vídeo ou áudio que abre no computador (mp4, mov, m4a, mp3).") from e


def transcrever_whisper(arquivo, idioma, avisar, modelo="auto", cfg=None):
    from faster_whisper import WhisperModel
    raiz = pasta_modelos(cfg)
    kw = {"download_root": raiz} if raiz else {}
    planos = []
    if modelo in ("auto", "large-v3-turbo") and _cuda_pronto():
        planos.append(("large-v3-turbo", "cuda", "float16"))
    planos.append(("small" if modelo in ("auto", "large-v3-turbo") else modelo, "cpu", "int8"))
    audio = carregar_audio(arquivo, cfg)
    if not len(audio):
        raise ErroEstudo("Esse arquivo não tem som.", "Suba o vídeo com o áudio original.")
    lingua = None if idioma == "auto" else idioma
    ultimo = None
    for nome, disp, tipo in planos:
        if not _modelo_baixado(nome, raiz):
            avisar(f"Baixando o modelo de fala ({TAMANHO_MODELO.get(nome, 'uns minutos')}, só na primeira vez)")
        avisar("Ouvindo o vídeo na placa de vídeo" if disp == "cuda" else "Ouvindo o vídeo (no processador, leva uns segundos por minuto de vídeo)")
        try:
            m = WhisperModel(nome, device=disp, compute_type=tipo, **kw)
            segs, info = m.transcribe(audio, language=lingua, word_timestamps=True, vad_filter=False,
                                      condition_on_previous_text=False, beam_size=5)
            segmentos = [{
                "ini": round(s.start, 3), "fim": round(s.end, 3), "texto": s.text.strip(),
                "palavras": [{"palavra": w.word.strip(), "ini": round(w.start, 3), "fim": round(w.end, 3),
                              "prob": round(w.probability, 3)} for w in (s.words or [])],
            } for s in segs]
            return segmentos, {"modelo": nome, "dispositivo": disp, "idioma_detectado": info.language,
                               "duracao_audio": round(len(audio) / 16000, 2)}
        except Exception as e:  # noqa: BLE001  placa sem memória ou sem biblioteca: tenta a CPU
            ultimo = e
            if disp == "cpu":
                break
            avisar("A placa de vídeo não deu conta; seguindo no processador")
    raise ErroEstudo(f"Não consegui ouvir o vídeo ({type(ultimo).__name__}).",
                     "Confira se o arquivo abre no computador. Se abrir, tente de novo; se repetir, fale com o suporte.")


def limpar(segmentos):
    """Tira marcas da legenda automática: '>>' (troca de falante) e trechos só de [música], [aplausos]."""
    limpos = []
    for s in segmentos:
        texto = re.sub(r"\s+", " ", re.sub(r"\[[^\]]*\]", " ", s["texto"].replace(">>", " "))).strip()
        if not texto:
            continue
        palavras = [{**w, "palavra": w["palavra"].replace(">>", "").strip()} for w in s["palavras"]]
        palavras = [w for w in palavras if w["palavra"] and not re.fullmatch(r"\[[^\]]*\]", w["palavra"])]
        limpos.append({**s, "texto": texto, "palavras": palavras})
    return limpos


def formato_de(largura, altura):
    if not largura or not altura:
        return None
    r = largura / altura
    return "vertical" if r < 0.8 else ("quadrado" if r < 1.25 else "horizontal")


def info_arquivo(arquivo, cfg=None):
    """Duração e tamanho do quadro de um vídeo local (ffprobe; sem ele, o PyAV que vem com o Whisper)."""
    fp = _exe("ffprobe", cfg)
    if fp:
        try:
            r = subprocess.run([fp, "-v", "error", "-select_streams", "v:0", "-show_entries",
                                "stream=width,height:format=duration", "-of", "json", str(arquivo)],
                               capture_output=True, text=True, timeout=60, **_sem_janela())
            j = json.loads(r.stdout or "{}")
            v = (j.get("streams") or [{}])[0]
            dur = float((j.get("format") or {}).get("duration") or 0) or None
            return {"duration": round(dur, 2) if dur else None, "width": v.get("width"), "height": v.get("height")}
        except (OSError, ValueError, subprocess.TimeoutExpired):
            pass
    try:
        import av
        with av.open(str(arquivo)) as c:
            dur = float(c.duration / 1e6) if c.duration else None
            v = next((s for s in c.streams if s.type == "video"), None)
            return {"duration": round(dur, 2) if dur else None,
                    "width": v.codec_context.width if v else None, "height": v.codec_context.height if v else None}
    except Exception:  # noqa: BLE001
        return {}


def transcrever(entrada, idioma="auto", avisar=print, modelo="auto", forcar_whisper=False, cfg=None):
    """Devolve (base, plataforma, metodo, metadados, segmentos, extra). Levanta Bloqueado ou ErroEstudo."""
    local = Path(entrada)
    if local.is_file():
        meta = {"arquivo_nome": local.name, "tamanho_mb": round(local.stat().st_size / 1e6, 2), **info_arquivo(local, cfg)}
        segmentos, extra = transcrever_whisper(local, idioma, avisar, modelo, cfg)
        return "arquivo", "local", "whisper", meta, limpar(segmentos), extra
    if not re.match(r"^https?://", str(entrada)):
        raise ErroEstudo("Isso não parece um link nem um arquivo.", "Cole o link inteiro, começando com https://.")
    plataforma = plataforma_de(entrada)
    tmp = Path(tempfile.mkdtemp(prefix="tv_estudo_"))
    try:
        avisar("Lendo o link")
        info = extrair_info(entrada, tmp)
        meta = {k: info.get(k) for k in CAMPOS_META if info.get(k) is not None}
        if not forcar_whisper and plataforma == "youtube":
            escolha = escolher_legenda(info, idioma)
            if escolha:
                metodo, chave, url_leg = escolha
                avisar("Pegando a legenda do vídeo")
                segmentos = limpar(ler_json3(url_leg, tmp, metodo == "legenda_auto"))
                if segmentos:
                    return f"{plataforma}_{info['id']}", plataforma, metodo, meta, segmentos, {"legenda": chave}
        avisar("Baixando o som do vídeo")
        arquivo, _ = baixar_audio(entrada, tmp)
        segmentos, extra = transcrever_whisper(arquivo, idioma, avisar, modelo, cfg)
        return f"{plataforma}_{info['id']}", plataforma, "whisper", meta, limpar(segmentos), extra
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def buscar_youtube(termo, n=8, curtos=False):
    """Vídeos públicos do YouTube sobre o assunto (busca anônima), com views e duração quando o YouTube informa."""
    import yt_dlp
    termo = re.sub(r"\s+", " ", str(termo or "")).strip()[:120]
    if not termo:
        raise ErroEstudo("Escreva o assunto para buscar.", "Ex.: curiosidades de bichos.")
    # Curtos: o filtro do próprio YouTube (só vídeos, até 4 min); a busca simples devolve uma mistura que muda a cada
    # pedido e quase não traz vídeo curto.
    consulta = (f"https://www.youtube.com/results?search_query={quote(termo)}&sp=EgQQARgB" if curtos
                else f"ytsearch{n * 2}:{termo}")
    try:
        with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "extract_flat": True, "logger": _LoggerMudo(),
                               "socket_timeout": 30, "playlistend": n * 2}) as ydl:
            r = ydl.extract_info(consulta, download=False)
    except yt_dlp.utils.DownloadError as e:
        raise ErroEstudo("A busca no YouTube não respondeu.", "Confira a internet e tente de novo.") from e
    saida = []
    for e in list(r.get("entries") or [])[:n * 2]:
        url = e.get("url") or ""
        if "/shorts/" not in url and "watch?v=" not in url:
            continue
        dur = e.get("duration")
        if curtos and dur and dur > 240:
            continue
        saida.append({"link": url, "titulo": e.get("title"), "autor": e.get("channel") or e.get("uploader"),
                      "duracao_s": dur, "views": e.get("view_count")})
    # Os mais vistos primeiro: a ideia é estudar o que deu certo.
    return sorted(saida, key=lambda x: -(x["views"] or 0))[:n]
