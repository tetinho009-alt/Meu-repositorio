# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Trava de mãos do estilo desenhado: na caminhada e na corrida, nenhuma mão cai atrás das costas nem na barriga.

Desenha cada personagem do elenco do estilo ao longo de um ciclo inteiro de andar (de frente e de costas) e de correr
(de costas; de frente o braço dobrado passa na frente do peito de propósito) e mede, em cada pose, quanto da mão cai
dentro da silhueta do corpo (tronco, quadril, saia). Passou de 30% é mão no lugar errado: reprova.

Uso (da pasta kit/):
    python qa/maos.py                  # elenco do estilo do canal
    python qa/maos.py --passos 24      # mais poses por ciclo
Sai com código 1 se alguma pose reprovar.
"""
import argparse
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT))

import skia  # noqa: E402

from estilo_desenhado import personagem as P  # noqa: E402
from estilo_desenhado.elenco import ELENCO, andar, correr, pessoa  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--passos", type=int, default=12, help="poses por ciclo")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    P.QA_MAOS.update(ligado=True, medidas=[])
    casos = [("andar", andar, 0.62, False), ("andar", andar, 0.62, True), ("correr", correr, 0.34, True)]
    sup = skia.Surface(700, 1150)
    for nome in ELENCO:
        b = pessoa(nome)
        for ciclo, fn, periodo, costas in casos:
            for k in range(a.passos):
                t = periodo * k / a.passos
                pose = fn(t)
                if costas:
                    pose["costas"] = True
                P.QA_MAOS.update(plano=f"{ciclo}{' de costas' if costas else ''}", t=round(t, 3))
                b.desenhar(sup.getCanvas(), 350, 1100, 1000, pose)
    lim = P.QA_MAOS["limite"]
    ruins = [m for m in P.QA_MAOS["medidas"] if m["frac"] > lim]
    print(f"mãos: {len(P.QA_MAOS['medidas'])} medidas, {len(ruins)} acima de {lim:.0%} dentro do corpo")
    for m in ruins:
        print(f"  FALHA {m['nome']}: {m['plano']} t={m['t']:.3f}s mão {m['lado']} {m['frac']:.0%} dentro do corpo")
    if ruins:
        sys.exit(1)
    print("MAOS_OK")


if __name__ == "__main__":
    main()
