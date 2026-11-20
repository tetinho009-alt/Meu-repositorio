# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Trava da cena 3D antes do render (Blender ou Three.js).

Veio de um vídeo real de comprador (17/11/2026): o assunto era raio dentro de casa, e a IA reaproveitou a cena do
exemplo. O vídeo saiu com o fundo do mar, sem personagem e quase sem nada na tela, depois de 30 min de render.
Esta trava para antes de gastar o render quando:
- o episódio não diz qual é o fundo (campo "fundo" do episodio.json) ou escolhe um que não existe;
- a cena usa o fundo do mar (fundo "mar" ou o bloco do oceano) num assunto que não é de mar;
- a cena não tem nenhum personagem (algo com olhos: olhos(), mascote(), caravela, peixe);
- sobrou bicho do exemplo (a caravela) num vídeo que não é sobre ele.

Uso (rodar.py chama sozinho): conferir(ep, texto_da_narracao, caminho_da_cena)
"""
import re
import unicodedata
from pathlib import Path

from compor import TEMAS_FUNDO

MAR = ("mar", "oceano", "praia", "peixe", "agua-viva", "aguaviva", "caravela", "onda", "submarino", "baleia",
       "tubarao", "coral", "aquario", "polvo", "lula", "golfinho", "mergulh", "recife", "mare")
# Chamadas que põem um personagem na cena (as duas linguagens: Python do Blender e JS do Three.js).
PERSONAGEM = re.compile(r"\b(olhos|mascote|caravela|peixe)\s*\(")
OCEANO = re.compile(r"\b(blocoOceano|bloco_oceano)\s*\(")


def _sem_acento(s):
    return unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode()


def _erro(msg, fazer):
    raise SystemExit(f"ERRO: {msg}\nO QUE FAZER: {fazer}")


def conferir(ep, narracao, cena):
    texto = _sem_acento(" ".join([narracao or "", ep.get("titulo", "")]))
    fonte = Path(cena).read_text(encoding="utf-8", errors="replace")
    fonte_sem_coment = re.sub(r"(#|//)[^\n]*", "", fonte)
    fundo = ep.get("fundo")
    if not fundo:
        _erro("o episodio.json não diz qual é o fundo do vídeo (campo \"fundo\").",
              f"escolha o fundo pelo assunto ({', '.join(TEMAS_FUNDO)}) e grave em episodio.json, campo \"fundo\". "
              "O mar é só para assunto de mar.")
    if fundo not in TEMAS_FUNDO:
        _erro(f"o fundo '{fundo}' não existe.", f"use um destes: {', '.join(TEMAS_FUNDO)}.")
    de_mar = any(re.search(r"\b" + p + ("" if p.endswith("h") else r"s?\b"), texto) for p in MAR)
    if not de_mar and (fundo == "mar" or OCEANO.search(fonte_sem_coment)):
        _erro("a cena está no fundo do mar, mas o vídeo não é sobre o mar.",
              "monte o cenário do assunto (ex.: raio em casa = um cômodo em corte ou a casa por fora com céu de "
              "tempestade; use blocoComodo/casinha/nuvem no Three.js ou bloco_comodo/casinha/nuvem no Blender) e "
              "troque o \"fundo\" do episodio.json (casa, tempestade, ceu, cidade...).")
    if not PERSONAGEM.search(fonte_sem_coment):
        _erro("a cena não tem nenhum personagem.",
              "todo explicativo 3D tem pelo menos um personagem com olhos que atua na história: transforme o objeto "
              "do assunto num personagem com mascote() (o raio, a casa, a tomada...) ou ponha olhos() numa peça.")
    if "caravela" in fonte_sem_coment and "caravela" not in texto:
        _erro("sobrou a caravela do exemplo numa cena que não é sobre ela.",
              "tire a caravela e use os objetos e personagens do assunto deste vídeo.")
    print("trava da cena: ok (fundo, cenário e personagem conferidos)", flush=True)
