# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Cria a pasta de um episódio novo a partir dos modelos.

Uso:
    python episodio_novo.py <pasta> --serie "Nome da Série" --parte 1 --titulo "Título" \\
        --pergunta "O que o Nico faz?" --opcoes Entrar Fugir [--personagem nico]

Copia:
- de `modelos/episodio/`: roteiro.md, narrador.txt e post.md (com os campos preenchidos);
- de `exemplo/`: ep.py, trilha.py e rodar.py (o código do episódio de demonstração é o ponto de partida: troque as
  cenas em ep.py:cena() e os efeitos em trilha.py, mantenha pós, legenda, selo e voto);
- e gera episodio.json e respostas.json.
A pasta pode ficar em qualquer lugar dentro do kit (ex.: series/<serie>/ep1). Fora dele, defina MAQUINA_KIT.
Depois: escreva o roteiro e o narrador.txt, aprove, e rode `python <pasta>/rodar.py --voz kokoro`.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(KIT))

MODELOS = KIT / "modelos" / "episodio"
EXEMPLO = KIT / "exemplo"


def criar(pasta, serie, parte, titulo, pergunta, opcoes, personagem, forcar=False):
    pasta = Path(pasta)
    if pasta.exists() and any(pasta.iterdir()) and not forcar:
        raise SystemExit(f"{pasta} já existe e não está vazia (use --forcar para sobrescrever)")
    (pasta / "audio").mkdir(parents=True, exist_ok=True)
    o1, o2 = opcoes
    campos = {"{SERIE}": serie, "{PARTE}": str(parte), "{PROXIMA}": str(parte + 1), "{TITULO}": titulo,
              "{PERGUNTA}": pergunta, "{OPCAO1}": o1, "{OPCAO2}": o2, "{OPCAO1_MIN}": o1.lower(), "{OPCAO2_MIN}": o2.lower()}
    for arq in ("roteiro.md", "narrador.txt", "post.md"):
        txt = (MODELOS / arq).read_text(encoding="utf-8")
        for k, v in campos.items():
            txt = txt.replace(k, v)
        (pasta / arq).write_text(txt, encoding="utf-8")
    for arq in ("ep.py", "trilha.py", "rodar.py"):
        shutil.copy2(EXEMPLO / arq, pasta / arq)
    base = json.loads((EXEMPLO / "episodio.json").read_text(encoding="utf-8"))
    base.update(serie=serie, parte=parte, titulo=titulo, personagem=personagem, pergunta=pergunta,
                opcoes=[[o1, "consequência curta da opção 1"], [o2, "consequência curta da opção 2"]],
                palavras_voto={"1": [o1.upper()], "2": [o2.upper()]}, chaves={},
                gancho=["TEXTO GRANDE DO", "QUADRO 0"], nega={"1": "2", "2": "1"})
    base["bloco_voto"] = len([ln for ln in (pasta / "narrador.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]) - 1
    (pasta / "episodio.json").write_text(json.dumps(base, ensure_ascii=False, indent=2), encoding="utf-8")
    respostas = {"<id da mídia ou /reel/CODIGO depois de publicar>": {
        "opcoes": base["palavras_voto"],
        "respostas": {"1": [f"Voto contado: {o1.lower()}.", "Anotado. A Parte {} decide.".format(parte + 1)],
                      "2": [f"Voto contado: {o2.lower()}.", "Contado. A maioria decide a próxima parte."]}}}
    (pasta / "respostas.json").write_text(json.dumps(respostas, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"EPISODIO_OK {pasta}\n  1) escreva roteiro.md e narrador.txt (um bloco por linha; o primeiro é o gancho do quadro 0, o último é a "
          f"pergunta aberta) e o texto do gancho em episodio.json"
          f"\n  2) ajuste episodio.json (opções, pausas, chaves) e as cenas em ep.py"
          f"\n  3) python {pasta / 'rodar.py'} --voz kokoro --stills   (conferência rápida)"
          f"\n  4) python {pasta / 'rodar.py'} --voz kokoro            (vídeo, grade de QA e capa)")
    return pasta


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pasta")
    ap.add_argument("--serie", required=True)
    ap.add_argument("--parte", type=int, default=1)
    ap.add_argument("--titulo", required=True)
    ap.add_argument("--pergunta", required=True)
    ap.add_argument("--opcoes", nargs=2, required=True, metavar=("OPCAO1", "OPCAO2"))
    ap.add_argument("--personagem", default="nico")
    ap.add_argument("--forcar", action="store_true")
    a = ap.parse_args()
    criar(a.pasta, a.serie, a.parte, a.titulo, a.pergunta, a.opcoes, a.personagem, a.forcar)


if __name__ == "__main__":
    main()
