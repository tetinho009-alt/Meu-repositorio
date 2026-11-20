# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Molde do estilo cápsula: personagem em partes para recorte digital. Cada personagem é só uma configuração
(cores e acessórios); a forma é a mesma para todos.

Estilo: corpo e cabeça numa peça só em forma de feijão, olhos grandes ovais com um brilho, sem nariz, boca por
visema, braços e pernas de mangueira (tubo com ponta redonda) e mão redonda com polegar. Cor chapada com uma sombra
dura (tom mais escuro da própria cor) e contorno fino num tom mais escuro da própria cor, nunca preto. A roupa é uma
faixa de cor por cima do corpo; o acessório (óculos, laço, boné, cachecol, topete) diferencia cada personagem.
Para trocar o clima (comédia, drama, terror) basta trocar a paleta no personagem.json.

Coordenadas do "mundo" em px: pés em y = 1000, centro x = 500. Cada parte é uma lista de elementos SVG
(`el(path, cor, ...)`); `construir_boneco.py` desenha cada parte (Skia ou VectorCraft) e exporta um PNG transparente
por parte. `RIG` diz a ordem de desenho, o pai e o pivô de cada parte; é o mesmo para todos os personagens e tem os
mesmos nomes de parte que o `rig.Boneco` usa. Partes que não existem no estilo (orelhas, cabelo de trás, quadril e a
cabeça separada) saem como PNG transparente, para nenhuma cena quebrar.

Opções da configuração (ver PADRAO): pele, roupa, calca, sapato, iris, cabelo (sobrancelha e topete), acessorio
(cor do acessório), acessorios (lista: oculos, laco, bone, cachecol, topete), cilios (bool). Os tons escuros saem
sozinhos da cor base; para forçar um tom, use pele_sombra, roupa_esc, calca_esc ou sapato_esc.
"""
import colorsys
import math

ESTILO = "capsula"
CX = 500.0
CHAO = 1000.0
TINTA = "#3A2A2A"          # só para quem desenha com `contorno` (o estilo cápsula usa o tom de cada cor)
CONTORNO = 7.0             # espessura do contorno, em unidades do mundo

PADRAO = dict(pele="#C98B63", roupa="#1FA39A", calca="#2F4A6B", sapato="#F0644E", iris="#2A1A14",
              cabelo="#3A2A22", acessorio="#E8553F", acessorios=[], cilios=False)
C = dict(PADRAO)

# ---------------------------------------------------------------- medidas (iguais para todo personagem)

TOPO_Y, BASE_Y = 112.0, 800.0              # alto e base do feijão
MEIO_Y = (TOPO_Y + BASE_Y) / 2
ALT_2 = (BASE_Y - TOPO_Y) / 2
LARG, LARG_DELTA = 218.0, 22.0            # meia-largura média e quanto alarga embaixo
EXPOENTE = 2.35                           # superelipse: 2 = oval, maior = mais cápsula
FAIXA_Y = 548.0                           # onde começa a roupa (no centro a borda desce um pouco)
QUADRIL_Y = 780.0

EYE_Y, EYE_SEP = 285.0, 82.0
OLHO_RX, OLHO_RY = 46.0, 58.0
PUP_RX, PUP_RY = 26.0, 34.0
BOCA_Y = 410.0
ROSTO = (CX, 335.0)                       # pivô da "cabeça": inclina o rosto sem descolar do corpo

BRACO_R, MAO_R = 25.0, 34.0
PERNA_R = 30.0


def _ombro(lado):
    return (CX + lado * 190.0, 548.0)


def _cotovelo(lado):
    sx, sy = _ombro(lado)
    return (sx + lado * 52.0, sy + 128.0)


def _mao_centro(lado):
    """Centro da mão: 162 abaixo e 8 para fora do cotovelo (é o ponto que `rig.Boneco.mao` devolve)."""
    ex, ey = _cotovelo(lado)
    return (ex + lado * 8.0, ey + 162.0)


def _quadril(lado):
    return (CX + lado * 80.0, 738.0)


def _tornozelo(lado):
    return (CX + lado * 86.0, 948.0)


# ---------------------------------------------------------------- cores

def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _hex(rgb):
    return "#%02X%02X%02X" % tuple(int(round(max(0.0, min(1.0, v)) * 255)) for v in rgb)


def tom(cor, k):
    """Mesma cor, mais escura (k < 1) e um pouco mais saturada: sombra e contorno saem daqui, nunca do preto."""
    h, s, v = colorsys.rgb_to_hsv(*_rgb(cor))
    s = min(1.0, s * (1 + (1 - k) * 0.7) + (1 - k) * 0.08)
    return _hex(colorsys.hsv_to_rgb(h, s, v * k))


def _sombra(base, chave):
    return C.get(chave) or tom(C[base], 0.80)


def _linha_cor(base):
    return tom(C[base], 0.52)


# ---------------------------------------------------------------- geometria

def _f(v):
    return f"{v:.1f}"


def poli(pts, fechar=True):
    d = "M" + " L".join(f"{_f(x)} {_f(y)}" for x, y in pts)
    return d + (" Z" if fechar else "")


def elipse_pts(cx, cy, rx, ry, n=72, a0=0.0, a1=360.0):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * k / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]


def elipse(cx, cy, rx, ry):
    return poli(elipse_pts(cx, cy, rx, ry)[:-1])


def el(d, fill=None, contorno=0.0, volume=0, perfil=None, opacidade=1.0, traco=None, peso=None):
    """Elemento SVG da parte. No estilo cápsula o contorno vem por `traco` (cor própria), não pela TINTA."""
    return dict(d=d, fill=fill, contorno=contorno, volume=volume, perfil=perfil, opacidade=opacidade, traco=traco,
                peso=peso)


def risco(d, cor, peso=CONTORNO):
    return el(d, traco=cor, peso=peso, perfil="uniform")


def _vazio():
    """Parte que não existe no estilo: um ponto sem tinta (PNG transparente)."""
    return [el(elipse(CX, 500.0, 1.0, 1.0))]


def feijao_pts(n=360):
    """Contorno do corpo (sentido horário, começando à direita). Devolve [(x, y, ângulo)]."""
    e = 2.0 / EXPOENTE
    out = []
    for k in range(n):
        a = 2 * math.pi * k / n
        c, s = math.cos(a), math.sin(a)
        sx = math.copysign(abs(c) ** e, c)
        sy = math.copysign(abs(s) ** e, s)
        w = LARG + LARG_DELTA * sy
        out.append((CX + w * sx, MEIO_Y + ALT_2 * sy, a))
    return out


def meia_largura(y):
    """Meia-largura do corpo na altura y (pela amostra do contorno)."""
    pts = feijao_pts(720)
    perto = min(pts, key=lambda p: abs(p[1] - y) + (0 if p[0] >= CX else 1e6))
    return perto[0] - CX


def recorta(pts, fora):
    """Sutherland-Hodgman contra uma fronteira curva: fica o que tem fora(x, y) <= 0."""
    if not pts:
        return []
    out = []
    for i in range(len(pts)):
        a, b = pts[i - 1], pts[i]
        fa, fb = fora(*a), fora(*b)
        if fb <= 0:
            if fa > 0:
                out.append(_corte(a, b, fora))
            out.append(b)
        elif fa <= 0:
            out.append(_corte(a, b, fora))
    return out


def _corte(a, b, fora):
    lo, hi = 0.0, 1.0
    s_lo = fora(*a) > 0
    for _ in range(30):
        m = (lo + hi) / 2
        p = (a[0] + (b[0] - a[0]) * m, a[1] + (b[1] - a[1]) * m)
        if (fora(*p) > 0) == s_lo:
            lo = m
        else:
            hi = m
    return (a[0] + (b[0] - a[0]) * hi, a[1] + (b[1] - a[1]) * hi)


def _borda_faixa(x, y):
    """Negativo dentro da roupa: a borda de cima desce um pouco no meio (a faixa abraça o corpo)."""
    u = (x - CX) / (LARG + LARG_DELTA)
    return FAIXA_Y + 20 * (1 - u * u) - y


def _crescente(pts, ang0=math.radians(28), largura=0.17, potencia=1.4):
    """Sombra dura em meia-lua do lado oposto à luz (luz vem do alto à esquerda)."""
    cx, cy = CX, MEIO_Y + 30
    fora, dentro = [], []
    inicio = min(range(len(pts)), key=lambda i: (pts[i][2] - (ang0 - math.pi / 2)) % (2 * math.pi))
    for x, y, a in pts[inicio:] + pts[:inicio]:
        k = math.cos(a - ang0)
        if k <= 0:
            continue
        s = largura * k ** potencia
        fora.append((x, y))
        dentro.append((cx + (x - cx) * (1 - s), cy + (y - cy) * (1 - s)))
    return fora + dentro[::-1]


def _tubo(p0, p1, r, n=24):
    """Contorno fechado de um tubo de ponta redonda entre p0 e p1 (braço, perna)."""
    (x0, y0), (x1, y1) = p0, p1
    a = math.degrees(math.atan2(y1 - y0, x1 - x0))
    fim = elipse_pts(x1, y1, r, r, n, a - 90, a + 90)
    ini = elipse_pts(x0, y0, r, r, n, a + 90, a + 270)
    return fim + ini


def _lados_tubo(p0, p1, r, recuo_fim=0.0):
    """Só as duas laterais do tubo (sem a ponta de p0): o contorno do cotovelo fica contínuo em qualquer ângulo."""
    (x0, y0), (x1, y1) = p0, p1
    comp = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / comp, (y1 - y0) / comp
    nx, ny = -uy, ux
    fx, fy = x1 - ux * recuo_fim, y1 - uy * recuo_fim
    return ([(x0 + nx * r, y0 + ny * r), (fx + nx * r, fy + ny * r)],
            [(x0 - nx * r, y0 - ny * r), (fx - nx * r, fy - ny * r)])


# ---------------------------------------------------------------- partes

def _tronco():
    """O feijão inteiro: pele, sombra dura, faixa de roupa, contornos e os acessórios presos ao corpo."""
    pts = feijao_pts()
    xy = [(x, y) for x, y, _ in pts]
    pele, roupa = C["pele"], C["roupa"]
    meia = _crescente(pts)
    faixa = recorta(xy, lambda x, y: _borda_faixa(x, y))
    sombra_faixa = recorta(meia, lambda x, y: _borda_faixa(x, y))
    out = [el(poli(xy), pele),
           el(poli(meia), _sombra("pele", "pele_sombra")),
           el(poli(faixa), roupa),
           el(poli(sombra_faixa), _sombra("roupa", "roupa_esc")),
           risco(poli(xy), _linha_cor("pele")),
           risco(poli(faixa), _linha_cor("roupa"))]
    acess = C.get("acessorios") or []
    if "cachecol" in acess:
        out += _cachecol()
    if "topete" in acess:
        out += _topete()
    if "bone" in acess:
        out += _bone(xy)
    if "laco" in acess:
        out += _laco()
    return out


def _borda_topo(x):
    """y do alto do corpo na coluna x."""
    pts = [p for p in feijao_pts(720) if p[1] < MEIO_Y]
    return min(pts, key=lambda p: abs(p[0] - x))[1]


def _topete():
    """Topete: um cacho de cabelo saindo do alto do corpo."""
    x0, y0 = CX - 6, _borda_topo(CX - 6) + 14
    d = [(x0 - 34, y0), (x0 - 40, y0 - 40), (x0 - 18, y0 - 82), (x0 + 22, y0 - 96), (x0 + 50, y0 - 78),
         (x0 + 34, y0 - 70), (x0 + 12, y0 - 62), (x0 + 6, y0 - 40), (x0 + 30, y0 - 20), (x0 + 30, y0)]
    cor = C["cabelo"]
    return [el(poli(_suaviza(d)), cor), risco(poli(_suaviza(d)), tom(cor, 0.55))]


def _suaviza(pts, voltas=3):
    """Chaikin: arredonda o polígono (mantém a forma fechada)."""
    for _ in range(voltas):
        novo = []
        for i in range(len(pts)):
            (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % len(pts)]
            novo += [(0.75 * x0 + 0.25 * x1, 0.75 * y0 + 0.25 * y1), (0.25 * x0 + 0.75 * x1, 0.25 * y0 + 0.75 * y1)]
        pts = novo
    return pts


def _laco():
    """Laço no alto, puxado para a direita do personagem (esquerda da tela fica livre)."""
    cx = CX + 78
    cy = _borda_topo(cx) - 4
    cor = C["acessorio"]
    linha, sombra = tom(cor, 0.52), tom(cor, 0.8)
    out = []
    for lado in (-1, 1):
        asa = [(cx, cy), (cx + lado * 30, cy - 46), (cx + lado * 72, cy - 52), (cx + lado * 82, cy - 10),
               (cx + lado * 70, cy + 34), (cx + lado * 32, cy + 36)]
        asa = _suaviza(asa, 2)
        dobra = [(cx + lado * 20, cy + 6), (cx + lado * 60, cy + 26), (cx + lado * 72, cy + 30),
                 (cx + lado * 34, cy + 34)]
        out += [el(poli(asa), cor), el(poli(_suaviza(dobra, 2)), sombra), risco(poli(asa), linha)]
    no = elipse(cx, cy, 20, 22)
    out += [el(no, cor), risco(no, linha)]
    return out


def _bone(xy):
    """Boné: a calota cobre o alto do corpo e a aba fica de frente."""
    corte = TOPO_Y + 118
    calota = recorta(xy, lambda x, y: y - corte)
    cor = C["acessorio"]
    linha = tom(cor, 0.52)
    aba = elipse(CX, corte + 2, 190, 26)
    return [el(poli(calota), cor), el(aba, tom(cor, 0.8)), risco(poli(calota), linha), risco(aba, linha),
            el(elipse(CX, TOPO_Y + 8, 14, 9), tom(cor, 0.8))]


def _cachecol():
    """Cachecol na altura do início da roupa, com uma ponta caindo."""
    xy = [(x, y) for x, y, _ in feijao_pts()]
    y0, y1 = FAIXA_Y - 46, FAIXA_Y + 18
    faixa = recorta(recorta(xy, lambda x, y: y0 + 16 * (1 - ((x - CX) / 226) ** 2) - y),
                    lambda x, y: y - (y1 + 16 * (1 - ((x - CX) / 226) ** 2)))
    cor = C["acessorio"]
    linha = tom(cor, 0.52)
    ponta = _suaviza([(CX + 60, y1 - 4), (CX + 112, y1 - 6), (CX + 120, y1 + 120), (CX + 70, y1 + 126)], 2)
    return [el(poli(ponta), tom(cor, 0.8)), risco(poli(ponta), linha), el(poli(faixa), cor), risco(poli(faixa), linha)]


def _braco(lado):
    """Ombro -> cotovelo. O ombro fica escondido atrás do corpo em qualquer giro."""
    p0, p1 = _ombro(lado), _cotovelo(lado)
    tubo = poli(_tubo(p0, p1, BRACO_R))
    return [el(tubo, C["pele"]), risco(tubo, _linha_cor("pele"))]


def _antebraco(lado):
    """Cotovelo -> mão. Sem contorno na ponta do cotovelo, para a curva do braço não ganhar um risco no meio."""
    e, m = _cotovelo(lado), _mao_centro(lado)
    pele, linha = C["pele"], _linha_cor("pele")
    recuo = math.sqrt(MAO_R ** 2 - BRACO_R ** 2)
    a, b = _lados_tubo(e, m, BRACO_R, recuo)
    ang = math.degrees(math.atan2(m[1] - e[1], m[0] - e[0]))
    abre = math.degrees(math.asin(BRACO_R / MAO_R))
    arco = elipse_pts(m[0], m[1], MAO_R, MAO_R, 40, ang + 180 - abre, ang - 180 + abre + 360)
    # polegar: bolinha do lado de dentro da mão, presa por baixo dela
    px, py = m[0] - lado * 26, m[1] - 8
    polegar = elipse(px, py, 12, 14)
    return [el(polegar, pele), risco(polegar, linha),
            el(poli(_tubo(e, m, BRACO_R)), pele),
            el(elipse(m[0], m[1], MAO_R, MAO_R), pele),
            risco(poli(a, False), linha), risco(poli(b, False), linha), risco(poli(arco, False), linha)]


def _perna(lado):
    """Perna de mangueira; a sombra dura é a do corpo caindo no alto da perna."""
    pts = _tubo(_quadril(lado), _tornozelo(lado), PERNA_R)
    sombra = recorta(pts, lambda x, y: y - (BASE_Y + 26))
    return [el(poli(pts), C["calca"]), el(poli(sombra), _sombra("calca", "calca_esc")),
            risco(poli(pts), _linha_cor("calca"))]


def _pe(lado):
    """Sapato redondo, bico um pouco para fora; a sola é a sombra dura."""
    ax, _ = _tornozelo(lado)
    cx, cy, rx, ry = ax + lado * 14, 966.0, 66.0, 42.0
    casca = [(x, min(y, CHAO)) for x, y in elipse_pts(cx, cy, rx, ry, 80)[:-1]]
    sola = recorta(casca, lambda x, y: 984.0 - y)
    cor = C["sapato"]
    return [el(poli(casca), cor), el(poli(sola), _sombra("sapato", "sapato_esc")), risco(poli(casca), _linha_cor("sapato"))]


def _olho(lado):
    ox = CX + lado * EYE_SEP
    linha = _linha_cor("pele")
    out = []
    if C.get("cilios"):
        for k, (dx, dy, ang) in enumerate(((0.55, -0.86, -62), (0.82, -0.6, -36))):
            x0, y0 = ox + lado * OLHO_RX * dx, EYE_Y + OLHO_RY * dy
            x1 = x0 + lado * 20 * math.cos(math.radians(ang))
            y1 = y0 + 20 * math.sin(math.radians(ang))
            out.append(risco(f"M{_f(x0)} {_f(y0)} L{_f(x1)} {_f(y1)}", linha, peso=8))
    branco = elipse(ox, EYE_Y, OLHO_RX, OLHO_RY)
    return out + [el(branco, "#FFFFFF"), risco(branco, linha, peso=6)]


def _iris(lado):
    ox = CX + lado * EYE_SEP
    return [el(elipse(ox, EYE_Y + 6, PUP_RX, PUP_RY), C["iris"]),
            el(elipse(ox - 9, EYE_Y - 10, 9, 10), "#FFFFFF")]


def _palpebra(lado):
    """Pálpebra fechada (piscada): pele cobrindo o olho e o risco do olho fechado."""
    ox = CX + lado * EYE_SEP
    linha = _linha_cor("pele")
    fechado = [(ox - 40, EYE_Y + 4), (ox - 20, EYE_Y + 20), (ox, EYE_Y + 25), (ox + 20, EYE_Y + 20), (ox + 40, EYE_Y + 4)]
    return [el(elipse(ox, EYE_Y, OLHO_RX + 7, OLHO_RY + 7), C["pele"]),
            risco(poli(_curva(fechado), False), linha, peso=8)]


def _curva(pts, n=8):
    """Polilinha suave passando pelos pontos (Catmull-Rom)."""
    out = []
    p = [pts[0]] + list(pts) + [pts[-1]]
    for i in range(1, len(p) - 2):
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * (2 * p[i][j] + (-p[i - 1][j] + p[i + 1][j]) * t
                                    + (2 * p[i - 1][j] - 5 * p[i][j] + 4 * p[i + 1][j] - p[i + 2][j]) * t * t
                                    + (-p[i - 1][j] + 3 * p[i][j] - 3 * p[i + 1][j] + p[i + 2][j]) * t ** 3)
                             for j in (0, 1)))
    return out + [pts[-1]]


SOBRANCELHA = (EYE_Y - 92)


def _sobrancelha(lado):
    """Tracinho grosso e reto, ponta de dentro um pouco mais alta (neutro simpático)."""
    ox = CX + lado * EYE_SEP
    x0, x1 = ox - lado * 24, ox + lado * 30
    cor = C.get("sobrancelha") or tom(C["cabelo"], 0.95)
    return [risco(f"M{_f(x0)} {_f(SOBRANCELHA - 4)} L{_f(x1)} {_f(SOBRANCELHA + 4)}", cor, peso=15)]


def _oculos():
    """Óculos redondos: aro na cor do acessório, lente com um reflexo."""
    cor = C["acessorio"]
    out = []
    for lado in (-1, 1):
        ox = CX + lado * EYE_SEP
        aro = elipse(ox, EYE_Y + 2, 64, 64)
        out += [el(aro, "#FFFFFF", opacidade=0.16), risco(aro, cor, peso=10),
                risco(f"M{_f(ox - 34)} {_f(EYE_Y - 22)} L{_f(ox - 16)} {_f(EYE_Y - 40)}", "#FFFFFF", peso=6)]
    ponte = [(CX - EYE_SEP + 62, EYE_Y - 8), (CX, EYE_Y - 20), (CX + EYE_SEP - 62, EYE_Y - 8)]
    out.append(risco(poli(_curva(ponte), False), cor, peso=10))
    return out


def _boca(v):
    """Bocas de fala e de expressão; centro em (CX, BOCA_Y). Formato de D: reta em cima, curva embaixo."""
    x, y = CX, BOCA_Y
    linha = _linha_cor("pele")
    fundo, dente, lingua = "#6B2437", "#FFFDF7", "#F07A86"

    def d_aberta(larg, alt, dy=0.0, dentes=False, ling=True, topo_curvo=0.0):
        topo = [(x - larg, y + dy), (x, y + dy + topo_curvo), (x + larg, y + dy)]
        fundo_pts = elipse_pts(x, y + dy, larg, alt, 40, 0, 180)
        forma = _curva(topo, 6) + fundo_pts[1:-1]
        out = [el(poli(forma), fundo)]
        if ling:
            out.append(el(poli(recorta(elipse_pts(x, y + dy + alt * 0.95, larg * 0.62, alt * 0.5, 40)[:-1],
                                       lambda px, py: (y + dy + 2) - py + 0 * px)), lingua))
        if dentes:
            out.append(el(poli([(x - larg * 0.8, y + dy + 2), (x + larg * 0.8, y + dy + 2),
                                (x + larg * 0.72, y + dy + alt * 0.34), (x - larg * 0.72, y + dy + alt * 0.34)]), dente))
        out.append(risco(poli(forma), linha, peso=7))
        return out

    if v == "A":
        return d_aberta(40, 52)
    if v == "E":
        return d_aberta(52, 28, dentes=True, ling=False)
    if v == "I":
        return d_aberta(48, 18, dentes=True, ling=False)
    if v == "O":
        o = elipse(x, y + 18, 28, 36)
        return [el(o, fundo), el(elipse(x, y + 38, 16, 10), lingua), risco(o, linha, peso=7)]
    if v == "U":
        u = elipse(x, y + 14, 17, 20)
        return [el(u, fundo), risco(u, linha, peso=7)]
    if v == "M":
        return [risco(poli(_curva([(x - 30, y + 6), (x, y + 10), (x + 30, y + 6)], 6), False), linha, peso=9)]
    if v == "F":
        f = _curva([(x - 34, y + 4), (x, y + 2), (x + 34, y + 4)], 6) + elipse_pts(x, y + 4, 34, 16, 30, 0, 180)[1:-1]
        return [el(poli(f), fundo), el(poli([(x - 26, y + 3), (x + 26, y + 3), (x + 24, y + 12), (x - 24, y + 12)]), dente),
                risco(poli(f), linha, peso=7)]
    if v == "feliz":
        return d_aberta(62, 54, dy=-6, dentes=True, topo_curvo=6)
    # repouso: sorrisinho
    return [risco(poli(_curva([(x - 32, y), (x, y + 14), (x + 32, y)], 8), False), linha, peso=9)]


VISEMAS = ["R", "A", "E", "I", "O", "U", "M", "F", "feliz"]


def montar(cfg):
    """Monta as partes de um personagem a partir da configuração; devolve PARTES (o RIG é o mesmo para todos)."""
    C.clear()
    C.update(PADRAO)
    C.update(cfg or {})
    if isinstance(C.get("acessorios"), str):
        C["acessorios"] = [C["acessorios"]]
    PARTES = {}
    for nome, lado in (("e", -1), ("d", 1)):
        PARTES[f"perna_{nome}"] = _perna(lado)
        PARTES[f"tenis_{nome}"] = _pe(lado)
        PARTES[f"braco_{nome}"] = _braco(lado)
        PARTES[f"antebraco_{nome}"] = _antebraco(lado)
        PARTES[f"olho_{nome}"] = _olho(lado)
        PARTES[f"iris_{nome}"] = _iris(lado)
        PARTES[f"palpebra_{nome}"] = _palpebra(lado)
        PARTES[f"sobrancelha_{nome}"] = _sobrancelha(lado)
    PARTES["quadril"] = _vazio()
    PARTES["tronco"] = _tronco()
    PARTES["orelhas"] = _vazio()
    PARTES["cabeca"] = _vazio()
    PARTES["cabelo"] = _oculos() if "oculos" in C["acessorios"] else _vazio()
    PARTES["cabelo_tras"] = _vazio()
    for v in VISEMAS:
        PARTES[f"boca_{v}"] = _boca(v)
    return PARTES


# Rig: ordem de desenho (de trás pra frente), pai e pivô (coordenadas do mundo). Braços e pernas ficam atrás do corpo,
# com o pivô (ombro, quadril) escondido dentro dele. "cabeca" gira o rosto (olhos, boca, óculos) em volta do meio
# do rosto, sem descolar do feijão.
RIG = [
    ("perna_e", "corpo", _quadril(-1)), ("perna_d", "corpo", _quadril(1)),
    ("tenis_e", "perna_e", _tornozelo(-1)), ("tenis_d", "perna_d", _tornozelo(1)),
    ("braco_e", "tronco", _ombro(-1)), ("antebraco_e", "braco_e", _cotovelo(-1)),
    ("braco_d", "tronco", _ombro(1)), ("antebraco_d", "braco_d", _cotovelo(1)),
    ("quadril", "corpo", (CX, QUADRIL_Y)), ("tronco", "corpo", (CX, QUADRIL_Y)),
    ("cabelo_tras", "cabeca", ROSTO), ("orelhas", "cabeca", ROSTO), ("cabeca", "tronco", ROSTO),
    ("olho_e", "cabeca", (CX - EYE_SEP, EYE_Y)), ("olho_d", "cabeca", (CX + EYE_SEP, EYE_Y)),
    ("iris_e", "olho_e", (CX - EYE_SEP, EYE_Y)), ("iris_d", "olho_d", (CX + EYE_SEP, EYE_Y)),
    ("palpebra_e", "olho_e", (CX - EYE_SEP, EYE_Y)), ("palpebra_d", "olho_d", (CX + EYE_SEP, EYE_Y)),
    ("sobrancelha_e", "cabeca", (CX - EYE_SEP, SOBRANCELHA)), ("sobrancelha_d", "cabeca", (CX + EYE_SEP, SOBRANCELHA)),
    ("boca", "cabeca", (CX, BOCA_Y)),
    ("cabelo", "cabeca", ROSTO),
]
