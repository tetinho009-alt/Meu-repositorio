# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Gerador do estilo próprio do canal (mundo do recorte de papel colorido): as respostas da conversa de instalação +
uma semente viram um `estilo.json` único (a caixa de papéis, o corte da tesoura, a sombra projetada, a textura da
fibra, a proporção do corpo, o elenco, as fontes e a capa) que o motor inteiro lê.

    python -m estilo_desenhado.estilo --respostas respostas.json            # sorteia e grava kit/estilo.json
    python -m estilo_desenhado.estilo --respostas respostas.json --semente 7  # repete um sorteio
    python -m estilo_desenhado.estilo --perguntas                           # lista as perguntas e as opções

A mesma semente com as mesmas respostas gera o mesmo estilo, então dá para refazer a qualquer momento.

Travas de cada sorteio (se falhar, sorteia de novo com a semente seguinte):
- nada de papel bege-sépia ou creme envelhecido (nem no fundo nem na caixa de papéis), nada de tinta quase preta
  arroxeada e nada das fontes condensadas pesadas de cartaz;
- contraste: o papel escuro sobre o papel claro e o texto da capa sobre o fundo legíveis no celular;
- as duas cores do voto bem diferentes entre si; os papéis da caixa diferentes entre si.
"""
import argparse
import colorsys
import json
import math
import os
import random
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
ARQ = KIT / "estilo.json"

PERGUNTAS = {
    "clima": ("Qual o clima da série?", {
        "sombrio": "medo de verdade, noite, silêncio",
        "melancolico": "triste, saudade, perda",
        "absurdo": "estranho e engraçado ao mesmo tempo",
        "nostalgico": "lembrança, infância, tempo que passou"}),
    "lugar": ("Onde e quando ela se passa?", {
        "interior_90": "cidade do interior nos anos 90",
        "cidade_hoje": "cidade grande, hoje",
        "litoral": "litoral, vila de pescador",
        "sertao": "sertão, seca, estrada de terra",
        "futuro_proximo": "daqui a alguns anos"}),
    "recorte": ("Como é o corte do papel?", {
        "tesoura": "tesoura comum, borda quase reta com quinas de quem corta à mão",
        "rasgado": "rasgado à mão, borda irregular com a fibra aparecendo",
        "picote": "tesoura de picotar, borda em zigue-zague miúdo",
        "estilete": "estilete, corte limpo e quinas vivas"}),
    "cor": ("Qual a temperatura das cores?", {
        "fria": "azul-petróleo, verde-musgo, vinho e um mostarda",
        "quente": "vinho, terracota, laranja queimado e mostarda",
        "sobria": "papéis escuros e fechados, pouca cor",
        "destaque": "tudo em azul-acinzentado e uma cor só gritando"}),
    "proporcao": ("Como são os personagens?", {
        "cabecudo": "cabeça grande, corpo curto",
        "alongado": "compridos e magros",
        "realista": "proporção de gente de verdade",
        "arredondado": "fofos, cheios, redondos"}),
    "ameaca": ("O que assusta (ou move) a história?", {
        "criatura": "um ser que não é deste mundo",
        "presenca": "algo que não se vê, só se sente",
        "objeto": "uma coisa que não devia estar ali",
        "pessoa": "alguém de carne e osso"}),
    "textura": ("Qual a textura do papel?", {
        "fibra": "papel com fibra aparente",
        "cartolina": "cartolina lisa e fosca",
        "seda": "camadas de papel de seda, a de trás aparecendo",
        "reciclado": "papel reciclado, com pintinhas"}),
}
# respostas de estilos antigos (antes do papel) -> a opção mais próxima de agora
_ANTIGAS = {"traco": ("recorte", {"nanquim": "tesoura", "lapis": "estilete", "caneta": "estilete", "pincel": "rasgado"}),
            "textura": ("textura", {"papel_velho": "fibra", "vhs": "reciclado", "pelicula": "fibra", "limpo": "cartolina"}),
            "cor": ("cor", {"dessaturada": "sobria"})}

# Fontes de título por clima (SIL OFL ou Apache, baixadas do repositório oficial do Google Fonts): letras gordas e
# arredondadas, que parecem recortadas. Ficam fora as góticas e as condensadas pesadas de cartaz.
GF = "https://raw.githubusercontent.com/google/fonts/main"
FONTES = {
    "LuckiestGuy-Regular.ttf": f"{GF}/apache/luckiestguy/LuckiestGuy-Regular.ttf",
    "TitanOne-Regular.ttf": f"{GF}/ofl/titanone/TitanOne-Regular.ttf",
    "LilitaOne-Regular.ttf": f"{GF}/ofl/lilitaone/LilitaOne-Regular.ttf",
    "RubikDirt-Regular.ttf": f"{GF}/ofl/rubikdirt/RubikDirt-Regular.ttf",
    "BowlbyOneSC-Regular.ttf": f"{GF}/ofl/bowlbyonesc/BowlbyOneSC-Regular.ttf",
    "Sniglet-ExtraBold.ttf": f"{GF}/ofl/sniglet/Sniglet-ExtraBold.ttf",
    "CaveatBrush-Regular.ttf": f"{GF}/ofl/caveatbrush/CaveatBrush-Regular.ttf",
    "Chewy-Regular.ttf": f"{GF}/apache/chewy/Chewy-Regular.ttf",
    "Bangers-Regular.ttf": f"{GF}/ofl/bangers/Bangers-Regular.ttf",
    "Bungee-Regular.ttf": f"{GF}/ofl/bungee/Bungee-Regular.ttf",
    "Shrikhand-Regular.ttf": f"{GF}/ofl/shrikhand/Shrikhand-Regular.ttf",
    "Rye-Regular.ttf": f"{GF}/ofl/rye/Rye-Regular.ttf",
    "CourierPrime-Bold.ttf": f"{GF}/ofl/courierprime/CourierPrime-Bold.ttf",
    "SpaceMono-Bold.ttf": f"{GF}/ofl/spacemono/SpaceMono-Bold.ttf",
    "SpecialElite-Regular.ttf": f"{GF}/apache/specialelite/SpecialElite-Regular.ttf",
    "PatrickHand-Regular.ttf": f"{GF}/ofl/patrickhand/PatrickHand-Regular.ttf",
}
TITULO = {
    "sombrio": ("LuckiestGuy-Regular.ttf", "TitanOne-Regular.ttf", "RubikDirt-Regular.ttf", "BowlbyOneSC-Regular.ttf"),
    "melancolico": ("LilitaOne-Regular.ttf", "Sniglet-ExtraBold.ttf", "CaveatBrush-Regular.ttf"),
    "absurdo": ("Chewy-Regular.ttf", "Bangers-Regular.ttf", "Bungee-Regular.ttf", "Shrikhand-Regular.ttf"),
    "nostalgico": ("TitanOne-Regular.ttf", "Sniglet-ExtraBold.ttf", "Rye-Regular.ttf", "Shrikhand-Regular.ttf"),
}
TEXTO = ("CourierPrime-Bold.ttf", "SpaceMono-Bold.ttf", "SpecialElite-Regular.ttf", "PatrickHand-Regular.ttf")

# Nomes do elenco. Ficam de fora os nomes de séries de terror de outros canais (ver comandos/criar-estilo.md).
NOMES_F = ("Iara", "Malu", "Jade", "Cecília", "Tainá", "Isis", "Yasmin", "Estela", "Noemi", "Olívia", "Pietra", "Rosa")
NOMES_M = ("Otávio", "Ravi", "Ícaro", "Vicente", "Murilo", "Ulisses", "Caetano", "Renan", "Samuel", "Igor", "Elias", "Breno")
NOMES_VELHA = ("Dona Lurdes", "Dona Nair", "Dona Iolanda", "Dona Celeste", "Dona Odete", "Dona Albertina")
NOMES_VELHO = ("Seu Jair", "Seu Lauro", "Seu Osvaldo", "Seu Abílio", "Seu Durval", "Seu Ernesto")
PELES = ("#F2D3BC", "#E9BE9C", "#D9A27C", "#C68A62", "#A86F4C", "#8A5638", "#6E432B", "#523020")
CABELOS = ("#1A1416", "#2E1E14", "#4A3020", "#6B4426", "#8C5A2E", "#B07A42", "#C9A060", "#3A2A2A")
IRIS = ("#3A2416", "#5A3A1E", "#3E4A2A", "#2E4258", "#5A5A52")

# Caixas de papel por temperatura: (matiz, luz, saturação) de cada papel colorido. O sorteio tira 5 de cada caixa e
# mexe um pouco em cada um, então dois canais nunca saem com a mesma caixa.
CAIXAS = {
    "fria": [(196, 0.32, 0.62), (220, 0.30, 0.55), (84, 0.33, 0.46), (170, 0.30, 0.50), (350, 0.32, 0.58), (43, 0.52, 0.74)],
    "quente": [(352, 0.32, 0.60), (12, 0.42, 0.62), (25, 0.46, 0.74), (43, 0.52, 0.75), (194, 0.30, 0.60), (88, 0.31, 0.44)],
    "sobria": [(200, 0.22, 0.40), (348, 0.26, 0.42), (82, 0.30, 0.32), (215, 0.36, 0.30), (40, 0.42, 0.48), (170, 0.18, 0.34)],
    "destaque": [(208, 0.16, 0.22), (215, 0.30, 0.18), (200, 0.42, 0.20), (225, 0.24, 0.30), (195, 0.54, 0.14)],
}
VIVAS = [(352, 0.46, 0.80), (14, 0.50, 0.82), (44, 0.54, 0.86), (165, 0.40, 0.70), (130, 0.40, 0.60)]   # a cor que grita

# ---------------------------------------------------------------- cor


def _hls(h, l, s):
    r, g, b = colorsys.hls_to_rgb((h % 360) / 360, max(0, min(1, l)), max(0, min(1, s)))
    return [int(round(v * 255)) for v in (r, g, b)]


def _lab(c):
    def lin(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(v) for v in c[:3])
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def delta_e(a, b):
    return math.dist(_lab(a), _lab(b))


def luminancia(c):
    def lin(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(v) for v in c[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a, b):
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def _hexa(c):
    return "#%02X%02X%02X" % tuple(c[:3])


def _sepia(c):
    """Bege-sépia ou creme envelhecido (claro, puxado pro amarelo-marrom)."""
    h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in c[:3]))
    return 25 <= h * 360 <= 62 and l >= 0.62 and s >= 0.08


def _na_faixa_reservada(papel, tinta, papeis=()):
    """Papel sépia/creme (fundo ou papel da caixa) ou tinta quase preta arroxeada/neutra: fora do sorteio."""
    h2, l2, s2 = colorsys.rgb_to_hls(*(v / 255 for v in tinta))
    tinta_preta = l2 < 0.11 and (s2 < 0.18 or 250 <= h2 * 360 <= 345)
    return _sepia(papel) or tinta_preta or any(_sepia(p) for p in papeis)

# ---------------------------------------------------------------- sorteio


def _mexe(r, h, l, s, dh=8, dl=0.04, ds=0.06):
    return _hls(h + r.uniform(-dh, dh), l + r.uniform(-dl, dl), s + r.uniform(-ds, ds))


def _paleta(r, R):
    """A caixa de papéis (5 cores vivas), o papel claro das etiquetas, o papel escuro (o "preto" do recorte), a cor
    da sombra projetada e as cores do voto."""
    cor, clima = R["cor"], R["clima"]
    caixa = list(CAIXAS[cor])
    r.shuffle(caixa)
    papeis = [_mexe(r, *p) for p in caixa[:5]]
    if clima == "absurdo":   # absurdo: papéis mais claros e mais saturados
        papeis = [_hls(*_hls_de(p, dl=0.08, ds=0.12)) for p in papeis]
    if cor == "destaque":
        destaque = _mexe(r, *r.choice(VIVAS), dh=6, dl=0.03, ds=0.05)
    else:   # a cor que grita é o papel mais saturado da caixa, um pouco mais aceso
        base = max(papeis, key=lambda p: colorsys.rgb_to_hls(*(v / 255 for v in p))[2])
        destaque = _hls(*_hls_de(base, dl=0.08, ds=0.10))
    # o "preto" do recorte: azulado, esverdeado ou vinho bem escuro (nunca arroxeado)
    th = r.choice((r.uniform(200, 228), r.uniform(158, 178), r.uniform(348, 362)))
    tinta = _hls(th, r.uniform(0.10, 0.14), r.uniform(0.30, 0.46))
    # papel claro das etiquetas: gelo azulado, menta, rosado ou limão pálido (nunca creme)
    ph = r.choice((r.uniform(188, 216), r.uniform(145, 172), r.uniform(336, 356), r.uniform(68, 84)))
    papel = _hls(ph, r.uniform(0.87, 0.93), r.uniform(0.22, 0.42))
    sombra = _hls(th, 0.05, 0.45)
    puxa = _hls(th, 0.24, 0.32)                      # tom da noite (fundo dos planos abertos)
    apoio = min(papeis, key=lambda p: luminancia(p))  # o papel mais escuro da caixa (mato, parede do fundo)
    # segunda cor do voto: o papel da caixa mais longe da primeira
    segunda = max(papeis, key=lambda p: delta_e(p, destaque))
    segunda = _hls(*_hls_de(segunda, dl=0.06, ds=0.08))
    sat = {"sombrio": (0.98, 1.04), "melancolico": (0.92, 0.98), "absurdo": (1.06, 1.14), "nostalgico": (1.0, 1.06)}[clima]
    return dict(papel=papel, tinta=tinta, sombra=sombra, puxa=puxa, apoio=apoio, destaque=destaque,
                opcoes=[destaque, segunda], papeis=papeis), dict(tom=[1.0, 1.0, 1.0], saturacao=round(r.uniform(*sat), 3))


def _hls_de(c, dl=0.0, ds=0.0):
    h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in c[:3]))
    return h * 360, min(0.62, l + dl), min(0.92, s + ds)


def _acabamento(r, R):
    """Acabamento do quadro: fibra por cima (leve, a fibra forte já vem assada em cada peça), vinheta, grão,
    pintinhas do reciclado e quanto as camadas de neblina deixam passar (papel de seda)."""
    t = R["textura"]
    base = {"fibra": dict(papel=(0.16, 0.24), vinheta=(0.18, 0.32), grao=(0.02, 0.04), fibras=(0.9, 1.2), manchas=(0.1, 0.3), seda=(0.5, 0.6)),
            "cartolina": dict(papel=(0.06, 0.12), vinheta=(0.15, 0.28), grao=(0.015, 0.03), fibras=(0.3, 0.5), manchas=(0.0, 0.1), seda=(0.4, 0.5)),
            "seda": dict(papel=(0.10, 0.16), vinheta=(0.18, 0.3), grao=(0.02, 0.035), fibras=(0.5, 0.8), manchas=(0.05, 0.2), seda=(0.72, 0.85)),
            "reciclado": dict(papel=(0.18, 0.26), vinheta=(0.18, 0.32), grao=(0.03, 0.05), fibras=(0.7, 1.0), manchas=(0.6, 1.0), seda=(0.5, 0.6))}[t]
    out = {k: round(r.uniform(*v), 3) for k, v in base.items()}
    out["efeito"] = None
    return out


def _recorte(r, R):
    """O corte das peças (borda: quanto a borda foge da linha, em px de uma peça de 1000 px; passo: tamanho de cada
    trecho reto da tesoura) e a sombra projetada (dura, deslocada pra baixo e pro lado; px de uma peça de 1000 px)."""
    v = {"tesoura": dict(borda=(1.2, 1.8), passo=(11, 16)), "rasgado": dict(borda=(2.0, 2.8), passo=(4, 6)),
         "picote": dict(borda=(1.8, 2.4), passo=(5, 7)), "estilete": dict(borda=(0.3, 0.6), passo=(22, 32))}[R["recorte"]]
    out = {k: round(r.uniform(*x), 2) for k, x in v.items()}
    ang = math.radians(r.uniform(40, 62)) * 1.0
    lado = r.choice((1, -1))
    dist = r.uniform(7.0, 10.0)
    out.update(tipo=R["recorte"], sombra_dx=round(lado * dist * math.cos(ang), 2), sombra_dy=round(dist * math.sin(ang), 2),
               sombra_alfa=round(r.uniform(0.42, 0.58), 3))
    return out


def _corpo(r, R):
    v = {"cabecudo": dict(cabeca=(1.45, 1.6), largura=(1.0, 1.1), alto=(0.84, 0.9)),
         "alongado": dict(cabeca=(0.9, 0.98), largura=(0.78, 0.86), alto=(1.04, 1.1)),
         "realista": dict(cabeca=(0.8, 0.86), largura=(0.96, 1.04), alto=(0.98, 1.03)),
         "arredondado": dict(cabeca=(1.18, 1.28), largura=(1.36, 1.5), alto=(0.88, 0.94))}[R["proporcao"]]
    out = {k: round(r.uniform(*x), 3) for k, x in v.items()}
    out.update(_corpo_formas(random.Random(f"{sorted(out.items())}-corpo"), R))
    return out


def _corpo_formas(r, R):
    """Espessura de membro, mão e pé. Gerador próprio (não mexe no resto do sorteio). Recorte de papel não tem mão de
    dedo comprido nem membro fino: mão de luva ou de dedos curtos, membro em tira larga."""
    membro = {"cabecudo": (1.3, 1.45), "alongado": (1.2, 1.3), "realista": (1.2, 1.35), "arredondado": (1.5, 1.7)}
    maos = {"cabecudo": ("luva", "curta"), "alongado": ("curta", "luva"), "realista": ("curta", "luva"), "arredondado": ("luva",)}
    pes = {"cabecudo": ("redondo", "bota"), "alongado": ("bota", "tenis"), "realista": ("tenis", "bota"),
           "arredondado": ("redondo", "bota")}
    p = R["proporcao"]
    return dict(membro=round(r.uniform(*membro[p]), 3), mao=r.choice(maos[p]), pe=r.choice(pes[p]))


def _elenco(r, R, pal):
    """Três personagens novos: protagonista (18 a 30), alguém de meia-idade e alguém mais velho. Roupas tiradas da
    caixa de papéis do canal."""
    papeis = list(pal["papeis"])
    r.shuffle(papeis)
    roupas = papeis[:3] + [pal["destaque"]]
    r.shuffle(roupas)
    escuros = sorted(pal["papeis"], key=luminancia)

    def molde(cab_estilo, cilios, pele, cabelo, roupa, **extra):
        esc = [max(0, int(v * 0.74)) for v in roupa]
        calca = r.choice(escuros[:3])
        calca = _hls(*_hls_de(calca, dl=-0.05))
        extra.setdefault("labios", r.choice(("cheia", "fina")))
        return dict(pele=pele, pele_sombra=_hexa([int(v * 0.84) for v in _rgb(pele)]), cabelo=cabelo, roupa=_hexa(roupa),
                    roupa_esc=_hexa(esc), calca=_hexa(calca), calca_esc=_hexa([int(v * 0.78) for v in calca]),
                    sapato=_hexa(pal["tinta"]), sola="#221C1A", iris=r.choice(IRIS), roupa_tipo=r.choice(("moletom", "blusa")),
                    sapato_tipo=r.choice(("tenis", "sapatilha")), cabelo_estilo=cab_estilo, cilios=cilios,
                    rosto=r.choice(("oval", "redondo", "gota")), nariz=r.choice(("bolinha", "meia_lua", "triangulo")),
                    bochecha=r.random() < 0.6, **extra)

    fem = r.random() < 0.5
    prot = dict(nome=r.choice(NOMES_F if fem else NOMES_M), papel="protagonista",
                molde=molde(r.choice(("longo", "coque", "cacheado")) if fem else r.choice(("curto", "cacheado")), fem, r.choice(PELES),
                            r.choice(CABELOS), roupas[0], olheira=0.0))
    fem2 = r.random() < 0.5
    meio = dict(nome=r.choice(NOMES_F if fem2 else NOMES_M), papel="adulto",
                molde=molde(_outro(r, ("longo", "cacheado", "coque") if fem2 else ("curto", "cacheado"), prot["molde"]["cabelo_estilo"]),
                            fem2, r.choice(PELES), _outro(r, CABELOS, prot["molde"]["cabelo"]), roupas[1], rugas=1, olheira=0.0))
    fem3 = r.random() < 0.5
    velho = dict(nome=r.choice(NOMES_VELHA if fem3 else NOMES_VELHO), papel="idoso",
                 molde=molde(r.choice(("coque", "curto")) if fem3 else "curto", fem3, r.choice(PELES), r.choice(("#D8DCE0", "#BEC2C6", "#E6E8EA")),
                             roupas[2], rugas=2, labios="murcha", curvada=round(r.uniform(0.3, 0.8), 2), olheira=0.0))
    if meio["nome"] == prot["nome"]:
        meio["nome"] = r.choice([n for n in (NOMES_F if fem2 else NOMES_M) if n != prot["nome"]])
    return [prot, meio, velho]


def _outro(r, opcoes, evita):
    """Sorteia evitando repetir o do protagonista (dois personagens com o mesmo cabelo confundem quem assiste)."""
    resto = [o for o in opcoes if o != evita]
    return r.choice(resto or list(opcoes))


def _rgb(c):
    if isinstance(c, str):
        c = c.lstrip("#")
        return [int(c[k:k + 2], 16) for k in (0, 2, 4)]
    return list(c)


def _cenario(R, semente):
    """Quanto o cenário é puxado para a caixa de papéis (puxa), quanto a arquitetura entorta (torto: 0 reta, 1 casa
    torta de papel dobrado), o primeiro plano do plano aberto e a lua. Gerador próprio, não mexe no resto do sorteio."""
    r = random.Random(f"{semente}-cenario")
    cl = R["clima"]
    torto = {"sombrio": (0.35, 0.7), "melancolico": (0.25, 0.55), "absurdo": (0.9, 1.4), "nostalgico": (0.15, 0.4)}[cl]
    molduras = {"sombrio": ("mato", "nenhuma"), "melancolico": ("mato", "nenhuma"), "absurdo": ("nenhuma", "mato"),
                "nostalgico": ("mato", "nenhuma")}[cl]
    return dict(puxa=round(r.uniform(0.82, 0.92), 3), torto=round(r.uniform(*torto), 3), moldura=r.choice(molduras),
                lua_lado=r.choice((1, -1)), lua_tam=round(r.uniform(0.8, 1.35), 3), corvos=False)


def _rosto(r, R):
    """Olho de papel do elenco: botão (bolinha escura), recortado (oval claro com a pupila colada) ou fenda (meia-lua
    caída de sono)."""
    return dict(olho=r.choice({"sombrio": ("recortado", "botao"), "melancolico": ("recortado", "fenda"),
                               "absurdo": ("botao", "recortado"), "nostalgico": ("recortado", "botao")}[R["clima"]]))


def _capa(r, R, pal):
    layout = r.choice(("etiqueta", "colagem", "faixa"))
    escuro = min(pal["papeis"], key=luminancia)
    fundo = _hls(*_hls_de(escuro, dl=-0.06))
    return dict(layout=layout, fundo=fundo, titulo=pal["papel"], destaque=pal["destaque"])


def normaliza(respostas):
    """Respostas de estilo antigo (traço, papel velho, VHS...) viram a opção mais próxima do mundo do papel."""
    R = dict(respostas)
    for velho, (novo, mapa) in _ANTIGAS.items():
        if velho in R and (novo not in R or R[novo] in mapa):
            R[novo] = mapa.get(R[velho], R[velho]) if velho != novo else mapa.get(R[novo], R[novo])
    return {k: R[k] for k in PERGUNTAS if k in R}


def sortear(respostas, semente):
    R = normaliza(respostas)
    for k in PERGUNTAS:
        if k not in R:
            raise ValueError(f"falta a resposta de {k} (opções: {', '.join(PERGUNTAS[k][1])})")
        if R[k] not in PERGUNTAS[k][1]:
            raise ValueError(f"resposta inválida para {k}: {R[k]!r} (opções: {', '.join(PERGUNTAS[k][1])})")
    for tentativa in range(200):
        s = semente + tentativa
        r = random.Random(s)
        pal, grad = _paleta(r, R)
        if _na_faixa_reservada(pal["papel"], pal["tinta"], pal["papeis"]):
            continue
        if contraste(pal["papel"], pal["tinta"]) < 4.5 or delta_e(*pal["opcoes"]) < 35:
            continue
        if min(delta_e(a, b) for i, a in enumerate(pal["papeis"]) for b in pal["papeis"][i + 1:]) < 12:
            continue
        rec = _recorte(r, R)
        # "traco" fica no arquivo para quem lê estilo antigo; no papel ele não ferve nem hachura
        traco = dict(larg=1.0, fervura=0.0, pena=1.0, hachura=1.0, alfa=255, ferve_hz=12, angulo_hachura=0.0)
        estilo = dict(versao=2, mundo="papel", semente=s, respostas=R, paleta=pal, gradacao=grad, acabamento=_acabamento(r, R),
                      recorte=rec, traco=traco, corpo=_corpo(r, R), rosto=_rosto(r, R),
                      fontes=dict(titulo=r.choice(TITULO[R["clima"]]), texto=r.choice(TEXTO)),
                      capa=_capa(r, R, pal), elenco=_elenco(r, R, pal), cenario=_cenario(R, s))
        c = estilo["capa"]
        if contraste(c["fundo"], c["titulo"]) < 4.5:
            continue
        return estilo
    raise RuntimeError("nenhum sorteio passou nas travas; mude uma resposta")

# ---------------------------------------------------------------- leitura


_ATUAL = None
PADRAO = dict(clima="sombrio", lugar="interior_90", recorte="tesoura", cor="fria", proporcao="cabecudo", ameaca="presenca",
              textura="fibra")


def carregar(arq=None):
    """O estilo do canal (kit/estilo.json). Sem o arquivo, um estilo de demonstração (semente 1). Estilo gravado antes
    do mundo do papel (sem "recorte") é refeito com as mesmas respostas e a mesma semente: o motor só desenha papel."""
    global _ATUAL
    if arq is None and _ATUAL is not None:
        return _ATUAL
    p = Path(arq or os.environ.get("ESTILO_JSON") or ARQ)   # ESTILO_JSON: testar outro estilo sem trocar o do canal
    if p.is_file():
        e = json.loads(p.read_text(encoding="utf-8"))
        if e.get("mundo") != "papel":
            e = sortear({**PADRAO, **e.get("respostas", {})}, int(e.get("semente", 1)))
    else:
        e = sortear(PADRAO, 1)
    if arq is None:
        _ATUAL = e
    return e


def gravar(estilo, arq=None):
    p = Path(arq) if arq else ARQ
    p.write_text(json.dumps(estilo, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def baixar_fontes(estilo, destino):
    """Baixa só as fontes que o estilo usa (com o texto da licença ao lado)."""
    import urllib.request
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    for nome in {estilo["fontes"]["titulo"], estilo["fontes"]["texto"]}:
        alvo = destino / nome
        if alvo.is_file() or nome not in FONTES:
            continue
        url = FONTES[nome]
        req = urllib.request.Request(url, headers={"User-Agent": "kit-series"})
        with urllib.request.urlopen(req, timeout=120) as r:
            alvo.write_bytes(r.read())
        lic = url.rsplit("/", 1)[0] + ("/LICENSE.txt" if "/apache/" in url else "/OFL.txt")
        try:
            with urllib.request.urlopen(urllib.request.Request(lic, headers={"User-Agent": "kit-series"}), timeout=60) as r:
                (destino / (Path(nome).stem + "-LICENCA.txt")).write_bytes(r.read())
        except OSError:
            pass


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--respostas", help="JSON com uma resposta por pergunta")
    ap.add_argument("--semente", type=int, help="padrão: sorteada")
    ap.add_argument("--perguntas", action="store_true")
    ap.add_argument("--saida", help=f"padrão: {ARQ}")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if a.perguntas or not a.respostas:
        for k, (q, ops) in PERGUNTAS.items():
            print(f"{k}: {q}")
            for o, d in ops.items():
                print(f"    {o}: {d}")
        return
    respostas = json.loads(Path(a.respostas).read_text(encoding="utf-8"))
    semente = a.semente if a.semente is not None else random.SystemRandom().randrange(1, 10 ** 6)
    e = sortear(respostas, semente)
    p = gravar(e, a.saida)
    try:
        sys.path.insert(0, str(KIT))
        from config import pasta
        baixar_fontes(e, pasta("fontes"))
    except Exception as erro:  # sem internet: o estilo fica gravado e as fontes baixam depois
        print(f"fontes não baixadas agora ({erro}); rode de novo com internet", file=sys.stderr)
    print(f"ESTILO_OK {p} semente {e['semente']}")


if __name__ == "__main__":
    main()
