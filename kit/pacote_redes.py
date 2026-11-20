# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Pacote final das redes escolhidas: uma pasta por rede com o vídeo com o CTA daquela rede, a capa daquela rede e a
legenda daquela rede, numerados na ordem de postagem. Confere as regras de cada legenda antes de gravar.

Uso:
    python pacote_redes.py --nome a_luz_da_casa_7_p1 --video ep.mp4 --parte 1 --capa capa.jpg --redes-capa \\
                           --legendas post.json [--saida entregas] [--numero 1] [--redes instagram,kwai]
    python pacote_redes.py --nome caravela --videos PASTA_IG_TIKTOK_YOUTUBE --capa capa.jpg --carimbar \\
                           --gancho "POR QUE ELA QUEIMA MESMO MORTA" --legendas post.json

Redes:  --redes instagram,tiktok,youtube_shorts,kwai (padrão: as marcadas nas preferências do canal, prefs
        redes.escolhidas; sem preferências, Instagram, TikTok e YouTube Shorts). Só as escolhidas ganham pasta, na
        ordem 01_IG, 02_TIKTOK, 03_YOUTUBE, 04_KWAI (a numeração segue as que entraram). O YouTube longo (16:9) não
        sai aqui: é o filme da série (filme_longo.py, metodo/video-longo.md), feito quando há 3 partes ou mais.
Vídeo:  --video (corpo sem CTA: o kit gera uma versão por rede com o CTA dela, cta_redes.py)
        ou --videos (pasta que já tem IG/ INSTAGRAM/, TIKTOK/, YOUTUBE/ e KWAI/ com um mp4 em cada; sem KWAI/, o Kwai
        usa o vídeo do TikTok).
Capa:   --capa base.jpg --redes-capa  usa <base>_ig.jpg, <base>_tiktok.jpg, <base>_youtube.jpg e <base>_kwai.jpg
                                      (capa.py --redes; sem a do Kwai, usa a do TikTok);
        --capa base.jpg --carimbar    carimba a faixa com o CTA de cada rede numa capa única (qualquer formato);
        --capa base.jpg               a mesma capa em todas (avisa: o estúdio entrega uma por rede).
Legenda: post.json com um bloco por rede (modelo em exemplo/post.json):
    {"instagram": {"texto": "...", "hashtags": ["#a"], "rotulo_ia": true},
     "tiktok":    {"texto": "...", "hashtags": ["#a"], "comentario_fixado": "...", "rotulo_ia": true},
     "youtube":   {"titulo": "...", "descricao": "...", "hashtags": ["#a"], "sintetico": true},
     "kwai":      {"texto": "...", "hashtags": ["#a"], "rotulo_ia": true}}
    Sem o bloco "kwai", o Kwai usa o bloco do TikTok (o público e o formato são parecidos).

Regras conferidas (erro para o pacote): isca de engajamento ("comenta", "curte", "compartilha", "reposta", "marca alguém"),
hashtags acima do limite da rede, título do YouTube acima de 100 caracteres, legenda acima do limite da rede (os
limites vêm de prefs/esquema.json, redes_detalhe), sem "Ficção" nem "Fonte". Aviso (não para): opções do voto que não
aparecem no texto, legenda muito longa para o formato.
"""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(KIT))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from config import CFG, cor as cor_cfg, fonte_arquivo  # noqa: E402
from cta_redes import VERTICAIS, aviso_longo, detalhes, escolhidas, perfil_cfg, texto_cta, video_rede  # noqa: E402
from maquina.votos import _bate, sem_acento  # noqa: E402

# rede -> chave no post.json, pastas aceitas em --videos, caracteres sugeridos para o formato
POR_REDE = {
    "instagram": {"post": "instagram", "aceitas": ("IG", "INSTAGRAM", "01_IG"), "sugerido": 600},
    "tiktok": {"post": "tiktok", "aceitas": ("TIKTOK", "02_TIKTOK"), "sugerido": 300},
    "youtube_shorts": {"post": "youtube", "aceitas": ("YOUTUBE", "YOUTUBE_SHORTS", "03_YOUTUBE"), "sugerido": 800},
    "kwai": {"post": "kwai", "aceitas": ("KWAI", "04_KWAI"), "sugerido": 300},
}
# Quando falta o material próprio da rede, usa o de outra com o mesmo formato.
RESERVA = {"kwai": "tiktok"}
ISCA = re.compile(r"\b(comenta|comente|comentem|curte|curtam|curta aí|compartilha|compartilhem|reposta|repostem|marca (alguém|um amigo|"
                  r"quem)|marque (alguém|um amigo))\b", re.I)
# Link no comentário fixado derruba a distribuição (metodo/licoes.md, regra 28): o link fica só na bio
URL = re.compile(r"https?://|www\.|\b[\w-]+\.(com|com\.br|net|org|io|app|link|ly|me)\b", re.I)


def bloco_post(post, rede):
    """O bloco da legenda da rede no post.json (o Kwai reaproveita o do TikTok; o Shorts aceita 'youtube_shorts')."""
    chave = POR_REDE[rede]["post"]
    p = post.get(chave) or (post.get("youtube_shorts") if rede == "youtube_shorts" else None)
    if not p and rede in RESERVA:
        p = post.get(POR_REDE[RESERVA[rede]]["post"])
    return p


def conferir(post, opcoes=(), redes=None):
    """(erros, avisos) das legendas das redes. `redes`: [(id, detalhe)] como cta_redes.escolhidas(); padrão = as do canal."""
    erros, avisos = [], []
    for rede, det in (redes if redes is not None else escolhidas()):
        if rede not in POR_REDE:
            continue
        max_tags, max_txt, sugerido = det.get("hashtags_max", 5), det.get("legenda_max", 2200), POR_REDE[rede]["sugerido"]
        nome = det.get("rotulo", rede)
        p = bloco_post(post, rede)
        if not p:
            erros.append(f"{nome}: falta o bloco \"{POR_REDE[rede]['post']}\" da legenda no post.json")
            continue
        yt = rede == "youtube_shorts"
        texto = p.get("descricao" if yt else "texto", "")
        tudo = " ".join([texto, p.get("titulo", ""), p.get("comentario_fixado", "")])
        tags = p.get("hashtags", [])
        if ISCA.search(tudo):
            erros.append(f"{nome}: isca de engajamento ('{ISCA.search(tudo).group(0)}'); use pergunta aberta")
        if URL.search(p.get("comentario_fixado", "")):
            erros.append(f"{nome}: link no comentário fixado ('{URL.search(p['comentario_fixado']).group(0)}'); "
                         "o link fica só na bio (metodo/licoes.md, regra 28)")
        if len(tags) > max_tags:
            erros.append(f"{nome}: {len(tags)} hashtags (máximo {max_tags})")
        if any(not t.startswith("#") or " " in t for t in tags):
            erros.append(f"{nome}: hashtag mal formada em {tags}")
        if len(texto) > max_txt:
            erros.append(f"{nome}: legenda com {len(texto)} caracteres (máximo {max_txt})")
        elif len(texto) > sugerido:
            avisos.append(f"{nome}: legenda com {len(texto)} caracteres (o formato pede até ~{sugerido})")
        if not re.search(r"fic[çc][ãa]o|fonte", texto, re.I):
            erros.append(f"{nome}: falta 'Ficção' (série) ou 'Fonte' (explicativo) no texto")
        if yt and not 0 < len(p.get("titulo", "")) <= 100:
            erros.append(f"{nome}: título com {len(p.get('titulo', ''))} caracteres (1 a 100)")
        if rede in ("tiktok", "kwai") and len(tags) < 3:
            avisos.append(f"{nome}: o formato pede de 3 a 5 hashtags")
        palavras = [sem_acento(w) for w in re.split(r"[^\w]+", tudo) if w]
        for rotulo, aceitas in opcoes:
            if not any(_bate(w, sem_acento(x)) for w in palavras for x in [rotulo, *aceitas]):
                avisos.append(f"{nome}: a opção '{rotulo}' não aparece no texto (capa, vídeo e legenda falam igual)")
    return erros, avisos


def carimbar(base, destino, texto, perfil=None):
    """Faixa do CTA da rede embaixo da capa, dentro do recorte 3:4 do grid (y até 1680)."""
    img = Image.open(base).convert("RGB").resize((1080, 1920))
    d = ImageDraw.Draw(img, "RGBA")
    arq, larg_max = str(fonte_arquivo("mono")), 900
    linhas = [f"USE FONE · {texto}"]
    tam = 34
    f = ImageFont.truetype(arq, tam)
    while f.getlength(linhas[0]) > larg_max and tam > 26:
        tam -= 2
        f = ImageFont.truetype(arq, tam)
    if f.getlength(linhas[0]) > larg_max:  # CTA longo (explicativo): duas linhas, quebrando no meio das palavras
        ps = texto.split()
        meio = len(ps) // 2
        linhas = [f"USE FONE · {' '.join(ps[:meio])}", " ".join(ps[meio:])]
        while max(f.getlength(ln) for ln in linhas) > larg_max and tam > 20:
            tam -= 2
            f = ImageFont.truetype(arq, tam)
    alt_linha = tam * 1.5
    larg = max(f.getlength(ln) for ln in linhas) + 70
    alto = alt_linha * len(linhas) + 30
    y = 1640 - alto  # termina antes do fim do recorte 3:4 do grid (y 1680)
    d.rounded_rectangle(((1080 - larg) / 2, y, (1080 + larg) / 2, y + alto), radius=min(37, alto / 2),
                        fill=(*cor_cfg("destaque"), 235))
    for i, ln in enumerate(linhas):
        d.text((540, y + 15 + alt_linha * (i + 0.5)), ln, font=f, fill=(255, 255, 255), anchor="mm")
    if perfil:
        d.text((540, y + alto + 40), perfil, font=ImageFont.truetype(arq, 30), fill=(235, 232, 245), anchor="mm")
    destino.parent.mkdir(parents=True, exist_ok=True)
    img.save(destino, quality=92)


def legenda_md(rede, p, nome, video, capa, rotulo=None):
    """(markdown com o passo a passo, texto puro para colar). `rede`: instagram, tiktok, youtube_shorts ou kwai."""
    tags = " ".join(p.get("hashtags", []))
    rede = "youtube_shorts" if rede == "youtube" else rede
    if rede == "youtube_shorts":
        corpo = (f"## Título\n\n{p['titulo']}\n\n## Descrição\n\n{p['descricao']}\n\n{tags}\n\n## Ao publicar\n\n"
                 "- Público: **Não é conteúdo para crianças**.\n"
                 + ("- Marcar **conteúdo alterado ou sintético** (voz ou imagem realista feita por IA).\n"
                    if p.get("sintetico") else "")
                 + "- O Shorts usa um quadro do vídeo como capa: escolha o quadro do gancho no app.\n")
        txt = f"{p['descricao']}\n\n{tags}\n"
    else:
        txt = f"{p['texto']}\n\n{tags}\n"
        corpo = f"## Legenda\n\n{txt}\n## Ao publicar\n\n"
        if p.get("rotulo_ia"):
            corpo += {"instagram": "- Ligar o rótulo **\"Rótulo de IA\"** em Configurações avançadas.\n",
                      "kwai": "- Se o Kwai mostrar a opção de avisar que o vídeo foi feito com IA, ligue.\n"}.get(
                rede, "- Ligar o selo **\"Conteúdo gerado por IA\"**.\n")
        if p.get("comentario_fixado"):
            corpo += f"- Comentário para fixar: \"{p['comentario_fixado']}\"\n"
    titulo = rotulo or {"instagram": "Instagram (Reels)", "tiktok": "TikTok", "youtube_shorts": "YouTube Shorts",
                        "kwai": "Kwai"}.get(rede, rede)
    return f"# {nome} · {titulo}\n\n**Vídeo:** `{video.name}` · **Capa:** `{capa.name}`\n\n{corpo}", txt


def _achar_video(pasta_videos, rede):
    for r in (rede, RESERVA.get(rede)):
        if not r:
            continue
        for nome_p in POR_REDE[r]["aceitas"]:
            achado = next(iter(sorted((Path(pasta_videos) / nome_p).glob("*.mp4"))), None)
            if achado:
                return achado
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nome", required=True, help="nome do vídeo nos arquivos (ex.: a_luz_da_casa_7_p1)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--video", help="vídeo sem CTA (o kit gera uma versão por rede)")
    g.add_argument("--videos", help="pasta com as versões prontas (IG/, TIKTOK/, YOUTUBE/, KWAI/)")
    ap.add_argument("--parte", type=int, default=1)
    ap.add_argument("--gancho", help="explicativo: o gancho do próximo vídeo no CTA")
    ap.add_argument("--capa", required=True)
    c = ap.add_mutually_exclusive_group()
    c.add_argument("--redes-capa", action="store_true", help="usa <capa>_ig/_tiktok/_youtube/_kwai (capa.py --redes)")
    c.add_argument("--carimbar", action="store_true", help="carimba o CTA de cada rede numa capa única")
    ap.add_argument("--legendas", required=True, help="post.json com a legenda de cada rede")
    ap.add_argument("--episodio", help="episodio.json (confere se as opções do voto aparecem nas legendas)")
    ap.add_argument("--saida", default=str(Path(CFG["pastas"]["trabalho"]) / "entregas"))
    ap.add_argument("--numero", type=int, help="número do vídeo na semana (vai na frente do nome)")
    ap.add_argument("--redes", help="redes separadas por vírgula: instagram,tiktok,youtube_shorts,youtube_longo,kwai "
                                    "(padrão: as das preferências do canal)")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    todas = escolhidas(a.redes)
    redes = [(r, d) for r, d in todas if r in VERTICAIS]
    longo = aviso_longo(a.redes)
    if longo:
        print(longo)
    if not redes:
        raise SystemExit("ERRO: nenhuma rede de vídeo vertical escolhida, então não há pacote para montar.\n"
                         "O QUE FAZER: marque Instagram, TikTok, YouTube Shorts ou Kwai nas preferências (ou use --redes).")
    post = json.loads(Path(a.legendas).read_text(encoding="utf-8"))
    opcoes = []
    if a.episodio:
        ep = json.loads(Path(a.episodio).read_text(encoding="utf-8"))
        opcoes = [(o[0], ep.get("palavras_voto", {}).get(str(i), [])) for i, o in enumerate(ep["opcoes"], 1)]
    erros, avisos = conferir(post, opcoes, redes)
    det_todas = detalhes()
    for rede, det in redes:
        if rede in RESERVA and not post.get(POR_REDE[rede]["post"]) and bloco_post(post, rede):
            avisos.append(f"{det.get('rotulo', rede)}: sem bloco próprio no post.json; usei a legenda do "
                          f"{det_todas[RESERVA[rede]].get('rotulo', RESERVA[rede])}")
    for av in avisos:
        print("AVISO", av)
    if erros:
        print("\n".join(f"ERRO {e}" for e in erros))
        raise SystemExit("PACOTE_REPROVADO: corrija a legenda (comandos/publicar.md) e rode de novo")
    nome = f"{a.numero:02d}_{a.nome}" if a.numero else a.nome
    raiz = Path(a.saida) / nome
    perfil = perfil_cfg()
    capa = Path(a.capa)
    if not (a.redes_capa or a.carimbar):
        print("AVISO a mesma capa em todas as redes: use --redes-capa ou --carimbar para o CTA de cada rede na capa")
    for i, (rede, det) in enumerate(redes, 1):
        sufixo = VERTICAIS[rede][1]
        pasta_rede = f"{i:02d}_{det['pasta']}"
        destino = raiz / pasta_rede
        destino.mkdir(parents=True, exist_ok=True)
        pre = f"{i:02d}_{a.nome}"
        texto = texto_cta(det["cta"], a.parte, a.gancho)
        video = destino / f"{pre}_{sufixo}.mp4"
        if a.video:
            video_rede(a.video, video, texto, perfil)
        else:
            achado = _achar_video(a.videos, rede)
            if not achado:
                raise SystemExit(f"ERRO: não achei o vídeo do {det.get('rotulo', rede)} em {a.videos}\n"
                                 f"O QUE FAZER: ponha o mp4 numa destas pastas: {', '.join(POR_REDE[rede]['aceitas'])}")
            shutil.copyfile(achado, video)
        capa_rede = destino / f"{pre}_capa.jpg"
        if a.redes_capa:
            origem = capa.with_name(f"{capa.stem}_{sufixo}{capa.suffix}")
            if not origem.is_file() and rede in RESERVA:
                reserva = capa.with_name(f"{capa.stem}_{VERTICAIS[RESERVA[rede]][1]}{capa.suffix}")
                if reserva.is_file():
                    print(f"AVISO {det.get('rotulo', rede)}: sem {origem.name}; usei {reserva.name}")
                    origem = reserva
            if not origem.is_file():
                raise SystemExit(f"ERRO: falta a capa {origem.name}\nO QUE FAZER: rode capa.py --redes antes")
            shutil.copyfile(origem, capa_rede)
        elif a.carimbar:
            carimbar(capa, capa_rede, texto, perfil)
        else:
            shutil.copyfile(capa, capa_rede)
        md, txt = legenda_md(rede, bloco_post(post, rede), a.nome, video, capa_rede, det.get("rotulo"))
        nome_md = "titulo_descricao" if rede == "youtube_shorts" else "legenda"
        (destino / f"{pre}_{nome_md}.md").write_text(md, encoding="utf-8")
        (destino / f"{pre}_{nome_md}.txt").write_text(txt, encoding="utf-8")
        print(f"{pasta_rede:<11} {texto}  ->  {video.name}, {capa_rede.name}, {pre}_{nome_md}.md")
    print(f"PACOTE_OK {raiz}")
    conferir_entrega(Path(a.video) if a.video else next(iter(sorted(Path(a.videos).rglob("*.mp4"))), None), raiz)


def conferir_entrega(video, raiz):
    """Última olhada antes de entregar (qa/conferir_entrega.py): folha de 8 quadros e as 3 perguntas para a IA."""
    if not video or not Path(video).is_file():
        return
    from qa.conferir_entrega import PERGUNTAS, folha
    arq = folha(video)
    shutil.copyfile(arq, Path(raiz) / "conferencia.jpg")
    print(f"CONFERENCIA {Path(raiz) / 'conferencia.jpg'}")
    print("OBRIGATÓRIO ANTES DE ENTREGAR: abra a folha acima e responda, olhando os quadros:")
    for i, p in enumerate(PERGUNTAS, 1):
        print(f"  {i}. {p}")
    print("Se alguma resposta for não, NÃO entregue: diga ao usuário em uma linha o que faltou, corrija e rode de novo.")


if __name__ == "__main__":
    main()
