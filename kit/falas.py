# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Grava as falas do episódio UMA TOMADA POR FALA, cada personagem com a sua voz, com o tempo de cada palavra.

É o jeito do estúdio real com o ElevenLabs: uma fala por pedido (o personagem tem voz própria e a fala refeita não
mexe nas outras), tags de direção do eleven_v3 ([whispers], [sighs]...) e tempo de palavra devolvido pelo próprio
ElevenLabs (endpoint with-timestamps), sem precisar do Whisper. Provedor sem tempo de palavra (Kokoro, Piper) passa
pelo Whisper automaticamente.

Uso:
    python falas.py <falas.json> [--refazer] [--seco]
    python falas.py <falas.json> --juntar <pasta> [--pausa 0.35]

falas.json: [{"saida": "audio/falas/01_narrador.mp3", "personagem": "narrador", "texto": "[whispers] ...",
              "voz": "<voice_id do ElevenLabs>", "provedor": "elevenlabs", "modelo": "eleven_v3"}]
("provedor" e "modelo" são opcionais: o padrão é o do config.json.) Caminhos relativos à pasta do falas.json.

Saída de cada fala: o mp3 e, ao lado, <nome>.tempos.json = [{"palavra", "ini", "fim"}] (tags não entram).
Fala que já tem mp3 é pulada: refazer uma fala = apagar só o mp3 dela (ou --refazer para todas).
Ritmo do ElevenLabs (lição real de 429): um pedido por vez, com o intervalo mínimo do config e espera crescente.

Tomada que o gerador cortou com a voz ainda soando (os últimos 30 ms a menos de 45 dB do pico) ganha, ao juntar, uma
cauda de soltura de 180 ms (o espelho do fim, em fade de cosseno): nunca termina num corte seco, e nada é esticado.

--juntar <pasta>: põe as falas em sequência num áudio só e grava <pasta>/narrador.mp3 + <pasta>/tempos.json no
formato do alinhar.py (bloco = número da fala, mais o campo "personagem"). A trilha do episódio
(`<episodio>/trilha.py --audio <pasta>`) e a legenda funcionam igual à narração única; as pausas entre falas
continuam sendo decididas no episodio.json.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(KIT))

from config import CFG, ErroConfig, ffmpeg  # noqa: E402
from maquina.alinhamento import alinhar_palavras, sem_tags  # noqa: E402
from voz import PROVEDORES, ErroVoz, provedor  # noqa: E402


def _falas(arq):
    lista = json.loads(Path(arq).read_text(encoding="utf-8"))
    base = Path(arq).resolve().parent
    for i, f in enumerate(lista):
        if not f.get("texto") or not f.get("saida"):
            raise SystemExit(f"fala {i}: faltam 'texto' ou 'saida'")
        f["_saida"] = (base / f["saida"]).resolve()
        f["_provedor"] = f.get("provedor") or CFG["voz"]["provedor"]
        if f["_provedor"] not in PROVEDORES:
            raise SystemExit(f"fala {i}: provedor desconhecido {f['_provedor']}")
    return lista


def _tempos_whisper(audio, texto):
    import alinhar
    res, _ = alinhar_palavras([texto], alinhar.ouvir_whisper(audio))
    return [{"palavra": w["palavra"], "ini": w["ini"], "fim": w["fim"]} for w in res]


def gravar(lista, refazer=False, seco=False):
    adaptadores = {}
    for i, f in enumerate(lista):
        saida = f["_saida"]
        if saida.exists() and not refazer:
            print(f"pulando {saida.name} (já gravada)")
            continue
        if seco:
            print(f"[SECO] fala {i} · {f.get('personagem', '?')} · {f['_provedor']} · voz {f.get('voz') or 'padrão'}"
                  f" · modelo {f.get('modelo') or CFG['voz'].get(f['_provedor'], {}).get('modelo', '-')}\n"
                  f"       {f['texto']}\n       -> {saida}")
            continue
        try:
            ad = adaptadores.get(f["_provedor"]) or adaptadores.setdefault(f["_provedor"], provedor(f["_provedor"]))
            modelo_antes = ad.cfg.get("modelo")
            if f.get("modelo"):
                ad.cfg["modelo"] = f["modelo"]
            res = ad.sintetizar(f["texto"], f.get("voz"), saida)
            if f.get("modelo"):
                ad.cfg["modelo"] = modelo_antes
        except (ErroVoz, ErroConfig) as e:
            if "permission" in str(e).lower() and f["_provedor"] == "elevenlabs":
                # Chave sem a permissão de gerar voz: erro claro, para a IA avisar na hora em vez de tentar outra coisa.
                raise SystemExit(
                    "ERRO: a chave da ElevenLabs está sem a permissão de gerar voz (Text to Speech). "
                    "O QUE FAZER: pare aqui e diga ao usuário, em uma frase: no site da ElevenLabs, em Developers > "
                    "API Keys, clique na chave, ligue Text to Speech (Access), Voices (Read) e User (Read) e salve "
                    "(a chave continua a mesma). Ofereça também seguir já com a voz grátis. Não tente contornar.")
            raise SystemExit(f"VOZ_FALHOU na fala {i} ({saida.name}): {e}")
        if res.palavras:
            ouvidas = [tuple(p) for p in res.palavras]
            alinhado, _ = alinhar_palavras([f["texto"]], ouvidas)
            tempos = [{"palavra": w["palavra"], "ini": w["ini"], "fim": w["fim"]} for w in alinhado]
            origem = "provedor"
        else:
            tempos, origem = _tempos_whisper(saida, f["texto"]), "whisper"
        saida.with_suffix(".tempos.json").write_text(json.dumps(tempos, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"ok {saida.name} · {f.get('personagem', '?')} · {len(tempos)} palavras (tempos: {origem})", flush=True)


def _ler_mono(arq):
    pcm = subprocess.run([ffmpeg(), "-v", "error", "-i", str(arq), "-f", "f32le", "-ac", "1", "-ar", "48000", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(pcm, dtype=np.float32)


SR = 48000
FECHO_MS = 70


def soa_no_fim(x):
    """A tomada acaba com a voz soando (o gerador truncou): os últimos 30 ms a menos de 45 dB do pico (janelas de 10 ms)."""
    h = SR // 100
    n = len(x) // h
    if n < 4:
        return False
    db = 20 * np.log10(np.sqrt(np.mean(x[: n * h].reshape(n, h).astype(np.float64) ** 2, axis=1)) + 1e-9)
    return bool(db[-3:].max() > db.max() - 45)


def fechar_cortada(x, ms=FECHO_MS):
    """Fecha a tomada que o gerador cortou com a voz soando: fade de cosseno nos últimos `ms` do próprio som.
    Não estende com espelho: o trecho tocado ao contrário soava como um "pipoco" no fim de cada frase (07/11)."""
    n = min(len(x) // 3, int(ms / 1000 * SR))
    x = np.array(x, dtype=np.float32)
    if n > 1:
        x[-n:] *= 0.5 * (1 + np.cos(np.linspace(0, np.pi, n))).astype(np.float32)
    return x


ENTRADA_MS, SAIDA_MS = 6, 20


def suavizar_bordas(x):
    """Tira o deslocamento de corrente contínua e põe fade curto na entrada e na saída de cada tomada: a emenda com o
    silêncio deixa de estalar ("pipocar") no começo e no fim das frases. Não mexe no que foi falado."""
    if len(x) == 0:
        return x
    x = (x - float(np.mean(x))).astype(np.float32)
    ne = min(len(x) // 4, int(ENTRADA_MS / 1000 * SR))
    ns = min(len(x) // 4, int(SAIDA_MS / 1000 * SR))
    if ne > 1:
        x[:ne] *= 0.5 * (1 - np.cos(np.linspace(0, np.pi, ne))).astype(np.float32)
    if ns > 1:
        x[-ns:] *= 0.5 * (1 + np.cos(np.linspace(0, np.pi, ns))).astype(np.float32)
    return x


def juntar(lista, pasta, pausa=0.35):
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    partes, tempos, t = [], [], 0.0
    silencio = np.zeros(int(SR * pausa), dtype=np.float32)
    for i, f in enumerate(lista):
        arq_t = f["_saida"].with_suffix(".tempos.json")
        if not f["_saida"].exists() or not arq_t.exists():
            raise SystemExit(f"fala {i} ainda não gravada: rode sem --juntar antes")
        x = _ler_mono(f["_saida"])
        if soa_no_fim(x):
            x = fechar_cortada(x)
            print(f"  {f['_saida'].name}: tomada cortada pelo gerador com a voz soando; o fim ganhou fade de {FECHO_MS} ms", flush=True)
        x = suavizar_bordas(x)
        for w in json.loads(arq_t.read_text(encoding="utf-8")):
            tempos.append({"bloco": i, "personagem": f.get("personagem", ""), "palavra": w["palavra"],
                           "ini": round(t + w["ini"], 3), "fim": round(t + w["fim"], 3)})
        partes += [x, silencio]
        t += len(x) / SR + pausa
    audio = np.concatenate(partes[:-1])
    subprocess.run([ffmpeg(), "-v", "error", "-y", "-f", "f32le", "-ar", "48000", "-ac", "1", "-i", "-",
                    "-c:a", "libmp3lame", "-b:a", "192k", str(pasta / "narrador.mp3")], input=audio.tobytes(), check=True)
    (pasta / "tempos.json").write_text(json.dumps(tempos, ensure_ascii=False, indent=1), encoding="utf-8")
    (pasta / "narrador.txt").write_text("\n".join(sem_tags(f["texto"]) for f in lista) + "\n", encoding="utf-8")
    print(f"JUNTADO {pasta / 'narrador.mp3'} ({t - pausa:.1f} s, {len(lista)} falas, {len(tempos)} palavras)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("falas")
    ap.add_argument("--refazer", action="store_true", help="grava de novo mesmo as que já existem")
    ap.add_argument("--seco", action="store_true", help="mostra o que seria pedido, sem gravar nem gastar crédito")
    ap.add_argument("--juntar", metavar="PASTA", help="junta as falas gravadas em narrador.mp3 + tempos.json")
    ap.add_argument("--pausa", type=float, default=0.35)
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    lista = _falas(a.falas)
    if a.juntar:
        juntar(lista, a.juntar, a.pausa)
    else:
        gravar(lista, a.refazer, a.seco)
        if not a.seco:
            print("FALAS_OK")


if __name__ == "__main__":
    main()
