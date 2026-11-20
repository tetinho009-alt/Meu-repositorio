# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Motor de cartelas: um vídeo inteiro a partir de um roteiro.json, sem desenhar personagem.

Serve aos estilos tipografia cinética, top 5 / curiosidades, quiz, faceless com imagens, história real narrada e
antes/depois (metodo/estilos/). A IA escreve o roteiro.json; este script faz o resto, na ordem:

    conferência do roteiro (com gancho e viradas) -> voz (uma tomada por bloco) -> tempo de cada palavra
    -> trava antes do render -> trilha e master -> render (GPU ou CPU) -> conferência do áudio -> grade de QA -> capa
    -> pacote das redes escolhidas (prefs: redes.escolhidas)

Uso (a partir da pasta kit/):
    python cartelas/rodar.py cartelas/exemplo                  # o exemplo, com a voz do config (padrão: kokoro)
    python cartelas/rodar.py <pasta> --stills                  # só os quadros-marco (segundos; usa a voz se já houver)
    python cartelas/rodar.py <pasta> --previa                  # vídeo inteiro SEM voz, no ritmo médio da fala
    python cartelas/rodar.py <pasta> --voz gemini              # voz grátis do Google (precisa da chave grátis)
    python cartelas/rodar.py <pasta> --voz elevenlabs --seco   # mostra o custo da voz, sem gravar nada
    python cartelas/rodar.py <pasta> --cpu --blur 3            # força a CPU; blur de movimento com 3 subquadros

A pasta do episódio tem o roteiro.json (modelos em cartelas/modelos/) e, se o estilo usa, as imagens. A saída vai
para <pastas.trabalho>/<nome do episódio>/ e o pacote das redes para <pastas.trabalho>/entregas/.
Refazer um bloco de voz: apague o mp3 dele em <saída>/audio/ e rode de novo; o resto é reaproveitado.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT))

from config import CFG, pasta  # noqa: E402

TIPOS = {"gancho", "texto", "item", "quiz", "revela", "imagem", "antes_depois", "cta", "voto", "fim"}
ESTILOS_CARTELA = {"tipografia", "top5", "quiz", "faceless", "historia-real", "antes-depois", "bastidores"}
PY = sys.executable


def args():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pasta")
    ap.add_argument("--stills", action="store_true")
    ap.add_argument("--previa", action="store_true")
    ap.add_argument("--voz", help="provedor: gemini, kokoro, elevenlabs, azure, piper")
    ap.add_argument("--voz-id")
    ap.add_argument("--seco", action="store_true", help="só mostra o que a voz vai gravar e o custo")
    ap.add_argument("--cpu", action="store_true")
    ap.add_argument("--fps", type=int)
    ap.add_argument("--blur", type=int, help="subquadros de blur de movimento (0 = sem; 3 a 6 com placa de vídeo)")
    ap.add_argument("--sem-pacote", action="store_true")
    return ap.parse_args()


A = args()
BASE = Path(A.pasta).resolve()
ROTEIRO = json.loads((BASE / "roteiro.json").read_text(encoding="utf-8"))
if A.fps or ROTEIRO.get("fps"):
    CFG["render"]["fps"] = int(A.fps or ROTEIRO["fps"])

from maquina import slug  # noqa: E402
from maquina.desenho import FPS  # noqa: E402

NOME = slug(ROTEIRO.get("nome") or ROTEIRO.get("titulo") or BASE.name)
TRAB = pasta("trabalho") / NOME
AUD = TRAB / "audio"


def passo(n, total, nome):
    print(f"\n== PASSO {n}/{total}: {nome}", flush=True)


def roda(nome, cmd):
    t0 = time.perf_counter()
    r = subprocess.run([PY, *[str(c) for c in cmd]], cwd=str(KIT))
    if r.returncode:
        raise SystemExit(f"\nERRO no passo '{nome}'. A mensagem acima diz o motivo; corrija e rode de novo "
                         "(o que já ficou pronto é reaproveitado).")
    print(f"   ({time.perf_counter() - t0:.1f} s)", flush=True)


def confere_roteiro():
    from qa import antes_do_render as Q
    erros, avisos = [], []
    blocos = ROTEIRO.get("blocos") or []
    if not blocos:
        erros.append("o roteiro.json não tem nenhum bloco em 'blocos'")
    for i, b in enumerate(blocos):
        if b.get("tipo") not in TIPOS:
            erros.append(f"bloco {i + 1}: tipo '{b.get('tipo')}' não existe (use um de: {', '.join(sorted(TIPOS))})")
        if b.get("tipo") in ("quiz", "voto") and len(b.get("opcoes", [])) < 2:
            erros.append(f"bloco {i + 1}: {b['tipo']} precisa de pelo menos 2 opções em 'opcoes'")
        for chave in ("imagem", "antes", "depois", "desenho"):
            if b.get(chave) and not (BASE / b[chave]).is_file():
                (avisos if A.previa or A.stills else erros).append(
                    f"bloco {i + 1}: a imagem '{b[chave]}' não está na pasta do episódio")
    # Cartela só com texto é o vídeo genérico que o comprador recebeu (17/11/2026): metade dos blocos de conteúdo,
    # no mínimo, mostra o assunto (desenho ou imagem).
    conteudo = [b for b in blocos if b.get("tipo") in ("gancho", "texto", "item", "fim", "imagem", "antes_depois")]
    com_figura = [b for b in conteudo if b.get("desenho") or b.get("imagem") or b.get("antes")]
    if conteudo and len(com_figura) * 2 < len(conteudo) and not ROTEIRO.get("amostra"):
        erros.append(f"só {len(com_figura)} de {len(conteudo)} blocos mostram o assunto: o vídeo sairia só com texto. "
                     "O QUE FAZER: desenhe o assunto de cada bloco (o mel, o bicho, o objeto) num PNG transparente por "
                     "código, salve na pasta do episódio e ponha \"desenho\": \"arquivo.png\" no bloco (ver "
                     "cartelas/LEIA-ME.md, Desenho do assunto).")
    if blocos and blocos[0].get("tipo") != "gancho":
        avisos.append("o primeiro bloco não é do tipo 'gancho': o vídeo precisa prender no primeiro segundo")
    e, av = Q.textos([b.get("fala", "") for b in blocos], [b.get("tela", "") for b in blocos])
    e2, av2 = Q.disco(TRAB)
    # Gancho e viradas antes da voz, com o tempo estimado: roteiro errado não gasta voz.
    e3, av3 = Q.gancho_roteiro(blocos) if blocos else ([], [])
    return erros + e + e2 + e3, avisos + av + av2 + av3


def monta_linha(janelas, falado, total):
    blocos = []
    for i, (b, j, ws) in enumerate(zip(ROTEIRO["blocos"], janelas, falado)):
        seg0 = 0.0 if i == 0 else max(0.0, j["t0"] - 0.12)
        blocos.append({"i": i, "tipo": b["tipo"], "t0": j["t0"], "t1": j["t1"], "seg0": round(seg0, 3),
                       "palavras": [[round(tp, 3), p] for tp, p in ws], "dados": b})
    for a, b in zip(blocos, blocos[1:]):
        a["seg1"] = b["seg0"]
    blocos[-1]["seg1"] = round(total, 3)
    return {"total": round(total, 3), "fps": FPS, "blocos": blocos}


def desenhar_fabrica(linha):
    import skia
    from cartelas import visual as V

    T = V.tema(ROTEIRO.get("tema"))
    ctx = {"base": BASE}
    # Personagem que fala junto vem ligado por padrão: vídeo de comprador saiu só com texto (17/11/2026).
    # Só "apresentador": false no roteiro desliga.
    apr = ROTEIRO.get("apresentador", True)
    if apr:
        from cartelas.apresentador import Apresentador
        ctx["apresentador"] = Apresentador({} if apr is True else apr)
    try:
        import prefs
        pv = prefs.carregar()
        blur_pref = 0 if pv["render"]["modo_leve"] else int(pv["visual"]["motion_blur"])
        leg_pref = bool(pv["legenda"]["ativa"])
    except Exception:  # noqa: BLE001
        blur_pref, leg_pref = 0, True
    blur = A.blur if A.blur is not None else ROTEIRO.get("blur", blur_pref)
    sub = max(1, int(blur or 1))
    obt = 0.7
    com_legenda = ROTEIRO.get("legenda", leg_pref and ROTEIRO.get("estilo") != "tipografia" and ctx.get("apresentador") is None)

    def desenhar(c, t):
        if sub > 1:
            for k in range(sub):
                tt = t + (k / (sub - 1) - 0.5) * obt / FPS
                p = skia.Paint()
                p.setAlphaf(1.0 / (k + 1))
                c.saveLayer(None, p)
                b = V.quadro(c, tt, linha, T, ctx)
                c.restore()
        else:
            b = V.quadro(c, t, linha, T, ctx)
        if com_legenda:
            V.legenda_do_quadro(c, t, b, T)
    return desenhar, T


def render(linha, so_marcos=False):
    from maquina.motor import renderizar
    desenhar, _ = desenhar_fabrica(linha)
    marcos = [round(b["seg0"] + 0.7 * (b["seg1"] - b["seg0"]), 2) for b in linha["blocos"]]
    saida = TRAB / f"{NOME}.mp4"
    audio = None if so_marcos else (AUD / "mix_norm.wav")
    return renderizar(desenhar, linha["total"], saida, audio=audio, cpu=A.cpu, marcos=marcos,
                      pasta_quadros=TRAB / "quadros", so_marcos=so_marcos), saida


def post_padrao():
    """Legenda das 3 redes a partir do roteiro, quando a pasta não traz um post.json."""
    r = ROTEIRO
    p = r.get("post") or {}
    fontes = r.get("fontes") or []
    if r.get("rodape"):
        rodape = r["rodape"]
    elif fontes:
        rodape = "Fonte: " + "; ".join(fontes) + ". Narração com voz sintética."
    elif r.get("estilo") in ("antes-depois", "bastidores"):
        rodape = "Fonte: registro do próprio canal. Narração com voz sintética."
    else:
        rodape = "Ficção · narração com voz sintética."
    texto = p.get("texto") or (r.get("titulo", "") + "\n\n" + (r.get("pergunta_final") or ""))
    tags = p.get("hashtags") or []
    return {
        "instagram": {"texto": f"{texto}\n\n{rodape}", "hashtags": tags[:5], "rotulo_ia": True},
        "tiktok": {"texto": f"{texto} {rodape}", "hashtags": tags[:5], "rotulo_ia": True,
                   "comentario_fixado": p.get("comentario_fixado", "")},
        "youtube": {"titulo": (p.get("titulo_youtube") or r.get("titulo", NOME))[:100],
                    "descricao": f"{texto}\n\n{rodape}", "hashtags": tags[:3], "sintetico": True},
    }


def main():
    if os.environ.get("MAQUINA_FATIA"):    # processo filho do render em paralelo na CPU: só desenha
        linha = json.loads((TRAB / "linha.json").read_text(encoding="utf-8"))
        render(linha)
        return
    from cartelas import audio as AU
    from qa import antes_do_render as Q

    TRAB.mkdir(parents=True, exist_ok=True)
    total_passos = 3 if A.stills else (5 if A.previa else 8)
    estilo = ROTEIRO.get("estilo", "")

    passo(1, total_passos, "conferência do roteiro")
    erros, avisos = confere_roteiro()
    # Personagem do canal antes do primeiro vídeo: a IA pulava a folha e usava o boneco de exemplo (17/11/2026).
    apr = ROTEIRO.get("apresentador", True)
    if apr and not ROTEIRO.get("amostra"):
        from personagem_novo import EXEMPLOS, personagem_do_canal
        nome = apr.get("personagem") if isinstance(apr, dict) else None
        if not personagem_do_canal() and (not nome or nome in EXEMPLOS):
            erros.append("o canal ainda não tem personagem próprio (só os de exemplo do kit). O QUE FAZER: crie o "
                         "personagem do canal com `python personagem_novo.py <nome> --descricao \"...\" --cores '{...}'`"
                         " (a partir de kit/), mostre a folha.png ao usuário e rode de novo: o apresentador passa a ser ele.")
    if not Q.relatorio(erros, avisos, "CONFERÊNCIA DO ROTEIRO"):
        raise SystemExit("\nCorrija os erros acima no roteiro.json e rode de novo.")

    blocos = ROTEIRO["blocos"]
    vcfg = ROTEIRO.get("voz") or {}
    prov = A.voz or vcfg.get("provedor") or CFG["voz"]["provedor"]
    voz_id = A.voz_id or (vcfg.get("voz") if not A.voz or A.voz == vcfg.get("provedor") else None) or \
        CFG["voz"].get(prov, {}).get("voz", "")
    passo(2, total_passos, f"voz ({prov}{', ' + voz_id if voz_id else ''})")
    if A.seco:
        AU.gerar_vozes(blocos, prov, voz_id, AUD, seco=True)
        print("SECO_OK: nada foi gravado.")
        return
    tem_voz = all(not b.get("fala") or AU.arquivo_bloco(AUD, i, b["fala"], prov, voz_id).is_file()
                  for i, b in enumerate(blocos))
    if A.previa or (A.stills and not tem_voz):
        print("sem voz: tempos pelo ritmo médio da fala (prévia)")
        arqs = None
    else:
        arqs = AU.gerar_vozes(blocos, prov, voz_id, AUD)
    narr, janelas, total = AU.juntar(blocos, arqs)

    passo(3 if not A.stills else 2, total_passos, "tempo de cada palavra")
    wav = None
    if arqs:
        from maquina import som as S
        wav = AUD / "narrador.wav"
        import numpy as np
        S.gravar_wav(wav, np.stack([narr, narr], axis=1))
    falado, casadas, n_pal = AU.palavras(blocos, janelas, wav, cpu=A.cpu)
    linha = monta_linha(janelas, falado, total)
    AU.gravar_linha(TRAB / "linha.json", linha)

    if A.stills:
        passo(3, total_passos, "quadros-marco")
        render(linha, so_marcos=True)
        print(f"\nSTILLS_OK {TRAB / 'folha.jpg'}  (um quadro por bloco, na ordem do roteiro)")
        return

    passo(4 if arqs else 3, total_passos, "trava antes do render")
    erros, avisos = Q.duracao(total, "amostra" if ROTEIRO.get("amostra") else "teste" if ROTEIRO.get("teste") else estilo)
    # Gancho com o tempo real da voz (o texto já foi conferido no passo 1) e viradas com os tempos reais.
    from qa.gancho import viradas
    e, av = Q.gancho(janelas[0]["t1"], bool(blocos[0].get("tela")), inicio_fala_s=janelas[0]["t0"])
    erros, avisos = erros + e, avisos + av + viradas(blocos, janelas)
    if arqs:
        cortes = [(a["t1"] + b["t0"]) / 2 for a, b in zip(janelas, janelas[1:])]
        erros += Q.emendas(narr, AU.SR, cortes)
        avisos += Q.semelhanca(casadas, n_pal)
    if not Q.relatorio(erros, avisos) and not A.previa:
        raise SystemExit("\nO render não começou: corrija os erros acima (a prévia sem voz ignora esta trava).")

    passo(5 if arqs else 4, total_passos, "trilha e masterização")
    clima = ROTEIRO.get("clima", "tenso" if estilo in ("historia-real",) else "leve")
    AU.mixar(narr, linha, AUD / "mix.wav", clima=clima, musica=ROTEIRO.get("musica", True))
    roda("masterização", [KIT / "masterizar.py", AUD / "mix.wav", "-o", AUD / "mix_norm.wav"])

    passo(6 if arqs else 5, total_passos, f"render ({total:.1f} s de vídeo, {FPS} fps)")
    resumo, video = render(linha)
    if A.previa:
        prev = video.with_name(f"{NOME}_PREVIA_sem_voz.mp4")
        video.replace(prev)
        print(f"\nPREVIA_OK {prev}")
        return

    passo(7, total_passos, "conferência do vídeo")
    roda("áudio do vídeo", [KIT / "masterizar.py", "--verificar", video])
    roda("grade de QA", [KIT / "qa_grade.py", video, "--zona"])

    passo(8, total_passos, "capa e pacote das redes")
    from cartelas import visual as V
    capa = V.capa(TRAB / "capa.jpg", ROTEIRO.get("capa") or ROTEIRO.get("titulo", ""), V.tema(ROTEIRO.get("tema")),
                  ROTEIRO.get("capa_destaque", []), ROTEIRO.get("capa_rotulo"))
    if A.sem_pacote:
        print(f"\nVIDEO_OK {video}\nCAPA {capa}")
        return
    post = BASE / "post.json"
    if not post.is_file():
        post = TRAB / "post.json"
        post.write_text(json.dumps(post_padrao(), ensure_ascii=False, indent=1), encoding="utf-8")
    cmd = [KIT / "pacote_redes.py", "--nome", NOME, "--video", video, "--capa", capa, "--carimbar", "--legendas", post]
    if ROTEIRO.get("proximo"):
        cmd += ["--gancho", ROTEIRO["proximo"]]
    else:
        cmd += ["--parte", str(ROTEIRO.get("parte", 1))]
    roda("pacote das redes", cmd)
    print(f"\nVIDEO_OK {video}")


if __name__ == "__main__":
    from erros import rodar_amigavel
    rodar_amigavel(main)
