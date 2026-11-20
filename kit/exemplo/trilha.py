# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Trilha do episódio: coloca a narração na linha do tempo e monta o som em ESTÉREO, só com efeitos feitos por
código (nenhum áudio de terceiros). Grava <trabalho>/audio/mix.wav e <trabalho>/linha.json.

O vídeo é sincronizado a linha.json (tempos reais da fala), nunca a tempos digitados.

Uso: python trilha.py --audio PASTA_COM_narrador.mp3_E_tempos.json --trabalho PASTA_DE_SAIDA
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent


def _acha_kit(aqui):
    """Pasta do kit: a primeira acima deste arquivo que tem maquina/ (ou a variável MAQUINA_KIT)."""
    import os
    for d in (aqui, *aqui.parents):
        if (d / "maquina" / "__init__.py").is_file():
            return d
    if os.environ.get("MAQUINA_KIT"):
        return Path(os.environ["MAQUINA_KIT"])
    raise SystemExit("não achei a pasta do kit; defina MAQUINA_KIT")


KIT = _acha_kit(AQUI)
sys.path.insert(0, str(KIT))

from maquina import som as S  # noqa: E402

SR = S.SR


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", default=str(AQUI / "audio"))
    ap.add_argument("--trabalho", required=True)
    a = ap.parse_args()
    ep = json.loads((AQUI / "episodio.json").read_text(encoding="utf-8"))
    aud, trab = Path(a.audio), Path(a.trabalho)
    narr = S.ler(aud / "narrador.mp3")
    tempos = json.loads((aud / "tempos.json").read_text(encoding="utf-8"))
    n_blocos = max(w["bloco"] for w in tempos) + 1

    # 1) narração: cada bloco recortado pelos tempos e colocado com a pausa decidida aqui (não no TTS)
    t = float(ep["inicio_narracao"])
    pausas = list(ep["pausas"]) + [0.5] * n_blocos
    eventos, trechos = [], []
    for b in range(n_blocos):
        ws = [w for w in tempos if w["bloco"] == b]
        ini, fim = max(0.0, ws[0]["ini"] - 0.08), ws[-1]["fim"] + 0.15
        trechos.append((t, S.fade(narr[int(ini * SR): int(fim * SR)], 0.01, 0.06)))
        eventos.append({"tipo": f"n{b}", "t0": round(t, 3), "t1": round(t + fim - ini, 3),
                        "palavras": [[round(t + w["ini"] - ini, 3), w["palavra"]] for w in ws]})
        t += fim - ini + pausas[b]
    ev = {e["tipo"]: e for e in eventos}
    bv = ev[f"n{ep['bloco_voto']}"]
    t_voto = bv["t0"] - 0.15
    total = round(bv["t1"] + float(ep["cauda_voto"]), 3)
    t_luz = 0.0                                    # gancho no quadro 0: a janela já acende com a voz, sem espera
    t_aceno = next((p[0] for p in ev["n2"]["palavras"] if p[1].lower().startswith("acenou")), ev["n2"]["t1"] - 1.0)

    m = S.Mesa(total)
    for t0, x in trechos:
        m.poe(t0, x, pan=0.0, voz=True, ganho=1.0)

    # 2) cama e clima: grave contínuo + vento que anda de um ouvido pro outro ("use fone")
    m.poe(0.0, S.drone(total + 1, f=46.0), ganho=0.9)
    vento = S.vento(total + 1)
    m.poe(0.0, vento, pan=np.sin(np.linspace(0, 2.2 * np.pi, 64)) * 0.7, ganho=1.2)

    # 3) gancho: estalo da lâmpada e o zumbido dela, vindo da janela (à esquerda na tela)
    m.poe(t_luz, S.estalo(), pan=-0.35, ganho=0.9)
    m.poe(t_luz + 0.05, S.zumbido_lampada(total - t_luz), pan=-0.35, ganho=0.6)

    # 4) o aceno: coração acelerando + golpe grave; silêncio curto antes da pergunta
    m.poe(ev["n2"]["t0"], S.coracao(t_voto - ev["n2"]["t0"], 70, 110), ganho=0.8)
    m.poe(t_aceno, S.impacto(), ganho=0.9)
    fim_n2 = ev["n2"]["t1"]
    if t_voto - fim_n2 > 0.35:
        m.silencio(fim_n2 + 0.05, t_voto - 0.05)

    # 5) a escolha: grave subindo até o fim
    m.poe(t_voto, S.subida(total - t_voto + 0.2), ganho=1.0)

    trab.mkdir(parents=True, exist_ok=True)
    m.gravar(trab / "audio" / "mix.wav", duck=0.6)
    cortes = [ev["n1"]["t0"], ev["n2"]["t0"], round(t_aceno - 0.35, 3), round(t_voto, 3)]
    linha = {"total": total, "eventos": eventos, "t_luz": t_luz, "t_aceno": round(t_aceno, 3),
             "t_voto": round(t_voto, 3), "cortes": cortes}
    (trab / "linha.json").write_text(json.dumps(linha, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"TRILHA_OK total {total:.2f}s  voto {t_voto:.2f}s  aceno {t_aceno:.2f}s")


if __name__ == "__main__":
    main()
