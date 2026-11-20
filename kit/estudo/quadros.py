# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Folha de quadros da referência: 12 imagens do vídeo em ordem, num quadros.jpg dentro da pasta do estudo.

A transcrição só pega o que é falado. Sem ver a imagem, a IA não sabe que o vídeo estudado tem personagem, cenário e
movimento, e inventa um visual genérico (caso real de comprador, 17/11/2026). Com a folha, ela olha como o vídeo é
e reproduz o mesmo tipo de visual com as peças do kit.

Mesma regra do resto do estudo: só conteúdo público, sem login e sem cookies. Se a rede bloquear ou faltar o ffmpeg,
o estudo segue sem a folha e avisa.
"""
import subprocess
import tempfile
from pathlib import Path

N_QUADROS = 12


def _baixar_video(url, pasta):
    """Vídeo sem som na menor resolução perto de 480p: só para tirar os quadros."""
    import yt_dlp

    from .transcrever import _ydl_base
    opcoes = {**_ydl_base(pasta), "format": "bv*/b", "format_sort": ["res:480", "+size"]}
    with yt_dlp.YoutubeDL(opcoes) as ydl:
        info = ydl.extract_info(url, download=True)
        return Path(info["requested_downloads"][0]["filepath"])


def gerar(entrada, pasta_estudo, duracao=None, cfg=None, avisar=print):
    """Grava <pasta_estudo>/quadros.jpg e devolve o caminho, ou None (sem ffmpeg, bloqueio ou vídeo sem imagem)."""
    from .transcrever import _exe, _sem_janela, info_arquivo
    ff = _exe("ffmpeg", cfg)
    if not ff:
        avisar("Sem o ffmpeg: o estudo fica sem a folha de quadros")
        return None
    destino = Path(pasta_estudo) / "quadros.jpg"
    with tempfile.TemporaryDirectory(prefix="tv_quadros_") as tmp:
        local = Path(entrada)
        if not local.is_file():
            avisar("Pegando os quadros do vídeo")
            try:
                local = _baixar_video(str(entrada), tmp)
            except Exception:  # noqa: BLE001  bloqueio ou formato sem vídeo: segue sem a folha
                avisar("Não deu para pegar a imagem do vídeo: o estudo fica só com a fala")
                return None
        dur = duracao or info_arquivo(local, cfg).get("duration")
        if not dur:
            return None
        filtro = (f"fps={N_QUADROS}/{float(dur):.3f},scale='if(gt(iw,ih),360,240)':-2,"
                  f"tile={N_QUADROS // 2}x2:padding=4:color=white")
        r = subprocess.run([ff, "-v", "error", "-y", "-i", str(local), "-vf", filtro, "-frames:v", "1", "-q:v", "3",
                            str(destino)], capture_output=True, timeout=300, **_sem_janela())
    if r.returncode or not destino.is_file():
        avisar("Não deu para montar a folha de quadros: o estudo fica só com a fala")
        return None
    return destino
