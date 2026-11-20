# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Molde de pessoa em recorte de papel e o BonecoPapel (mesma API do maquina.rig.Boneco: desenhar, mao, poses por
parte). `BonecoGotico` continua como nome antigo.

Lê a configuração do personagem do kit (o bloco "molde" de `personagens/<nome>/personagem.json`: cores, roupa,
cabelo, cílios) e monta o boneco em peças de papel colorido: cabeça redonda ou oval, olho de papel recortado (ou de
botão, ou em fenda), sobrancelha em tirinha, nariz de bolinha, bochecha de papel de seda, cabelo em peça com a
franja cortada na tesoura, roupa e membros em tiras largas. Cada parte é uma peça solta: projeta a sombra dura na
peça de baixo (sempre pro mesmo lado da tela, em qualquer giro) e, no stop motion, é "recolocada" com um tremidinho
a cada pose. A proporção do corpo (tamanho da cabeça, largura e altura) vem do `corpo` do estilo.json.

Mundo do molde: pés em y=1000, centro x=500, 1000 unidades de altura (a mesma convenção do molde de recorte, então
`altura` em desenhar() significa a mesma coisa nos dois estilos).

Pose: a mesma do rig ({"parte": {"rot", "dx", "dy", "sx", "sy"}}, visema, piscar, olhar, estica, pulo, corpo_rot,
sorriso) e mais:
  medo: 0..1   sobrancelha de dentro sobe, olho arregala com pupila pequena, boca entreabre, ombros encolhem, treme
  t: segundos  liga o stop motion (o tremidinho de recolocar as peças); sem t, o boneco fica parado
"""
import json
import math
import random
from pathlib import Path

import numpy as np
import skia

from . import tinta as T
from ._rig import Cinematica

KIT = Path(__file__).resolve().parents[1]
CORPO = T.ESTILO["corpo"]
OLHO = {"ponto": "botao", "aberto": "recortado", "redondo": "recortado", "pesado": "fenda"}.get(
    T.ESTILO.get("rosto", {}).get("olho", "recortado"), T.ESTILO.get("rosto", {}).get("olho", "recortado"))   # recortado | botao | fenda
# espessura de braço, perna, pescoço e mão; o corpo estreito (largura < 1) achataria o membro junto, então compensa
MEMBRO = float(CORPO.get("membro", 1.2)) / min(1.0, CORPO["largura"])
MAO = CORPO.get("mao", "curta")            # curta | luva
PE = CORPO.get("pe", "tenis")              # tenis | bota | redondo
# Mão por variante: dedos (lado do polegar pro mindinho: deslocamento x, comprimento), raio dos dedos, meia largura e
# altura da palma
MAOS = {"curta": dict(dedos=[(-10, 25), (-3.5, 30), (3.5, 29), (10, 24)], raio=1.45, palma=(13, 34)),
        "luva": dict(dedos=[(-9, 17), (0, 20), (9, 17)], raio=2.1, palma=(16, 32))}
# Trava de mão na caminhada (qa/maos.py liga): mão que cai mais que `limite` dentro da silhueta do corpo é mão atrás
# das costas ou na barriga
QA_MAOS = {"ligado": False, "medidas": [], "plano": None, "t": None, "limite": 0.3}
# Configuração padrão do molde (cada personagem.json sobrescreve só o que muda)
PADRAO = dict(pele="#E8B48A", pele_sombra="#C98F68", cabelo="#2E1E18", roupa="#4A42A6", roupa_esc="#37308A",
              calca="#2C3150", calca_esc="#20243C", sapato="#F5F5F8", sola="#C9CAD6", iris="#6B4428",
              roupa_tipo="moletom", sapato_tipo="tenis", cabelo_estilo="franja", cilios=False, acessorio="#E8C04A")
CX = 500.0
EYE_Y, EYE_SEP = 222.0, 56.0
BOCA_Y = 314.0
PESCOCO = (CX, 392.0)
OMBRO = 84.0
NUCA_Y = 392.0


def _ombro(l):
    return (CX + l * 57, 452.0)


def _cotovelo(l):
    return (CX + l * 63, 600.0)


def _punho(l):
    return (CX + l * 65, 736.0)


def _quadril(l):
    return (CX + l * 25, 712.0)


def _joelho(l):
    return (CX + l * 26, 842.0)


def _tornozelo(l):
    return (CX + l * 25, 962.0)


# Ordem de desenho: pernas atrás do tronco, braços por cima dele (a manga cobre o ombro), cabeça por cima dos braços.
# As pernas são filhas do quadril (o quadril leva as pernas no contrapposto e o IK mantém os pés no chão).
RIG = [
    ("cabelo_tras", "cabeca", PESCOCO),
    ("perna_e", "quadril", _quadril(-1)), ("canela_e", "perna_e", _joelho(-1)), ("tenis_e", "canela_e", _tornozelo(-1)),
    ("perna_d", "quadril", _quadril(1)), ("canela_d", "perna_d", _joelho(1)), ("tenis_d", "canela_d", _tornozelo(1)),
    ("quadril", "corpo", (CX, 712.0)), ("tronco", "corpo", (CX, 712.0)),
    ("braco_e", "tronco", _ombro(-1)), ("antebraco_e", "braco_e", _cotovelo(-1)), ("mao_e", "antebraco_e", _punho(-1)),
    ("braco_d", "tronco", _ombro(1)), ("antebraco_d", "braco_d", _cotovelo(1)), ("mao_d", "antebraco_d", _punho(1)),
    ("orelhas", "cabeca", PESCOCO), ("cabeca", "tronco", PESCOCO),
    ("olho_e", "cabeca", (CX - EYE_SEP, EYE_Y)), ("olho_d", "cabeca", (CX + EYE_SEP, EYE_Y)),
    ("iris_e", "olho_e", (CX - EYE_SEP, EYE_Y)), ("iris_d", "olho_d", (CX + EYE_SEP, EYE_Y)),
    ("palpebra_e", "olho_e", (CX - EYE_SEP, EYE_Y)), ("palpebra_d", "olho_d", (CX + EYE_SEP, EYE_Y)),
    ("sobrancelha_e", "cabeca", (CX - EYE_SEP, EYE_Y - 48)), ("sobrancelha_d", "cabeca", (CX + EYE_SEP, EYE_Y - 48)),
    ("boca", "cabeca", (CX, BOCA_Y)),
    ("cabelo", "cabeca", PESCOCO),
]
# Cadeias de IK: (osso de cima, osso de baixo, ponto final no repouso, dobra: +1 a junta vai pra fora do corpo)
CADEIAS = {
    "mao_e": ("braco_e", "antebraco_e", _punho(-1), 1), "mao_d": ("braco_d", "antebraco_d", _punho(1), 1),
    "pe_e": ("perna_e", "canela_e", _tornozelo(-1), 1), "pe_d": ("perna_d", "canela_d", _tornozelo(1), 1),
}
# Repouso natural (somado por baixo da pose): peso na perna esquerda, quadril sobe desse lado, ombro desce, cabeça
# inclina, cotovelo com leve dobra, mão relaxada perto da coxa, o pé livre um pouco à frente (mais baixo na tela).
REPOUSO = {"quadril": {"rot": -4.0, "dx": -9}, "tronco": {"rot": 2.6, "dx": -5}, "cabeca": {"rot": 4.0},
           "braco_e": {"rot": 4}, "braco_d": {"rot": -6}, "antebraco_e": {"rot": -9}, "antebraco_d": {"rot": 12},
           "mao_e": {"rot": -6, "dedos": 0.35}, "mao_d": {"rot": 8, "dedos": 0.45}}
REPOUSO_PES = {"pe_e": (CX - 24, 962.0), "pe_d": (CX + 44, 974.0)}


# ---------------------------------------------------------------- configuração vinda do personagem de sempre

def _pasta_personagens():
    try:
        from config import pasta
        return pasta("personagens")
    except Exception:  # fora do kit (teste isolado): a pasta padrão
        return KIT / "personagens"


def ler_config(nome):
    """Configuração do personagem: PADRAO + o bloco "molde" de `personagens/<nome>/personagem.json`."""
    arq = _pasta_personagens() / nome / "personagem.json"
    if not arq.exists():
        raise FileNotFoundError(f"personagem sem configuração: {arq}")
    molde = json.loads(arq.read_text(encoding="utf-8")).get("molde")
    if not molde:
        raise ValueError(f"{arq} não tem o bloco \"molde\" (cores, roupa e cabelo)")
    return {**PADRAO, **molde}


def _lum(cor):
    r, g, b = T.rgb(cor)
    return (0.3 * r + 0.59 * g + 0.11 * b) / 255


class Paleta:
    """As cores do molde viradas em papel colorido (mais vivas, puxadas de leve pra caixa de papéis do canal)."""

    def __init__(self, cfg):
        self.pele = T.pele_papel(cfg["pele"])
        self.pele_esc = T.escurece(T.mistura(self.pele, (150, 40, 50), 0.12), 0.84)
        self.cabelo = T.papel_cor(cfg["cabelo"], sat=0.3, luz=(0.06, 0.74), matiz=False)
        self.roupa = T.papel_cor(cfg["roupa"], luz=(0.12, 0.8))
        self.roupa_esc = T.escurece(self.roupa, 0.76)
        self.calca = T.papel_cor(cfg["calca"], luz=(0.08, 0.6))
        self.sapato = T.escurece(T.papel_cor(cfg["sapato"], luz=(0.05, 0.42)), 0.9)
        self.sola = T.mistura(self.sapato, (235, 235, 230), 0.55)
        self.iris = T.mistura(T.papel_cor(cfg["iris"], luz=(0.08, 0.4), matiz=False), T.TINTA, 0.45)
        self.branco = T.mistura(T.PAPEL, (255, 255, 255), 0.6)
        self.mechas = cfg.get("mechas")                       # cor das mechas claras no cabelo longo (ou None)
        self.boca = T.mistura((92, 20, 38), T.TINTA, 0.3)
        self.bochecha = T.mistura(self.pele, (232, 92, 112), 0.5)


# ---------------------------------------------------------------- geometria

def _espelha(pts, l):
    return [(CX + l * (x - CX), y) for x, y in pts]


ROSTOS = {"coracao": "gota", "longo": "oval", "redondo": "redondo"}   # nomes de moldes antigos
NARIZES = {"arrebitado": "bolinha", "comprido": "triangulo", "largo": "meia_lua"}
CAB_C, CAB_RX, CAB_RY = (CX, 214.0), 134.0, 140.0   # cabeça de papel: centro e raios


def _cabeca_pts(rosto="redondo", idosa=False):
    """Contorno da cabeça de papel: redonda, oval (um pouco mais alta que larga) ou gota (bochecha mais cheia
    embaixo). Nunca o rosto comprido de queixo fino."""
    rosto = ROSTOS.get(rosto, rosto)
    rx, ry = {"oval": (126.0, 146.0), "gota": (128.0, 142.0)}.get(rosto, (CAB_RX, CAB_RY))
    cx, cy = CAB_C
    out = []
    for a in np.linspace(0, 2 * np.pi, 72, endpoint=False):
        x, y = math.cos(a), math.sin(a)
        k = 1.0
        if rosto == "gota":
            k = 0.9 + 0.16 * (y + 1) / 2
        elif rosto == "oval":
            k = 1.0 - 0.05 * max(0.0, y) ** 2
        if idosa and y > 0.3:
            k *= 1.03
        out.append((cx + rx * k * x, cy + ry * y))
    return np.array(out)


def _olho_branco(l, k, abre=1.0):
    """O oval claro do olho recortado (arregala no medo)."""
    ox = CX + l * EYE_SEP
    rx, ry = 22 + 4 * k, (25 + 7 * k) * abre
    return T.elipse(ox, EYE_Y, rx, max(2.0, ry), 32)


class _Mod:
    POSE_BASE = None
    CX = CX
    BOCA_Y = BOCA_Y


class BonecoPapel:
    """Boneco de recorte de papel. `BonecoPapel("<pasta>")` lê o personagem.json e monta em papel; a API é a do
    maquina.rig.Boneco."""

    def __init__(self, nome, cfg=None, semente=None, vetor=False):
        self._cin = Cinematica()
        self.nome = nome
        self.cfg = cfg or ler_config(nome)
        self.pal = Paleta(self.cfg)
        self.fem = bool(self.cfg.get("cilios"))
        self.idosa = _lum(self.cfg["cabelo"]) > 0.62
        self.rugas = int(self.cfg.get("rugas", 1 if self.idosa else 0))   # 2 = rosto muito marcado
        self.estilo_cabelo = self.cfg.get("cabelo_estilo", "franja")
        self.semente = semente if semente is not None else T._sem(nome) % 100000
        self.rig = {p: (pai, piv) for p, pai, piv in RIG}
        self.ordem = [p for p, _, _ in RIG]
        self.pes = (CX, 1000.0)
        self.mod = _Mod
        # saia/camisola/vestido (cfg["saia"] = cor, cfg["saia_comp"] = 0 no joelho .. 1 no tornozelo): presa no quadril,
        # desenhada por cima das pernas e por baixo da blusa; a barra acompanha as canelas a cada pose
        self.saia = self.cfg.get("saia")
        if self.saia:
            self.rig["saia"] = ("quadril", (CX, 712.0))
            self.ordem.insert(self.ordem.index("tronco"), "saia")
            self.cor_saia = T.papel_cor(self.saia, luz=(0.08, 0.6))
            self.comp_saia = float(self.cfg.get("saia_comp", 0.55))
        for k in ("rig", "ordem", "pes", "mod"):
            setattr(self._cin, k, getattr(self, k))
        self.cache = T.Cache()
        self.vetor = vetor          # True: pinta os caminhos ao vivo (nítido em qualquer zoom, ~4x mais lento na GPU)

    # cinemática do rig
    def _local(self, parte, pose):
        return self._cin._local(parte, pose)

    def _mundo(self, parte, pose, cache):
        return self._cin._mundo(parte, pose, cache)

    def _raiz(self, x, y, altura, pose):
        """Raiz do corpo com a proporção do estilo: altura e largura (escala em x em volta dos pés)."""
        m = self._cin._raiz(x, y, altura * CORPO["alto"], pose)
        s = skia.Matrix.Translate(x, y)
        s.preScale(CORPO["largura"], 1.0)
        s.preTranslate(-x, -y)
        return skia.Matrix.Concat(s, m)

    def _base(self, pose):
        """Monta a pose final: repouso natural por baixo (somado), o medo no corpo, a pose pedida e por fim o IK
        (pose["ik"] = {"mao_e": (x, y[, ângulo da mão]), "pe_d": (x, y)...} em coordenadas do molde). Sem pedir, os pés
        ficam plantados no chão pelo IK. pose["repouso"] = 0 desliga o repouso (pose crua, como no rig antigo)."""
        pose = {k: (dict(v) if isinstance(v, dict) else v) for k, v in (pose or {}).items()}
        cab = pose.setdefault("cabeca", {})   # tamanho da cabeça do estilo, em volta do pescoço
        cab["sx"] = cab.get("sx", 1.0) * CORPO["cabeca"] / CORPO["largura"]   # a largura do corpo não achata o rosto
        cab["sy"] = cab.get("sy", 1.0) * CORPO["cabeca"]

        def soma(parte, v, peso=1.0):
            atual = pose.get(parte) if isinstance(pose.get(parte), dict) else {}
            junto = dict(atual)
            for kk, vv in v.items():
                if kk in ("dx", "dy", "rot"):
                    junto[kk] = atual.get(kk, 0.0) + vv * peso
                elif kk not in atual:
                    junto[kk] = vv
            pose[parte] = junto

        rep = float(pose.get("repouso", 1.0))
        if rep:
            for parte, v in REPOUSO.items():
                soma(parte, v, rep)
        cur = float(self.cfg.get("curvada", 0.0))
        if cur:   # costas curvadas de cansaço: cabeça baixa e pra frente, ombro caído, peito fechado
            for parte, v in {"cabeca": {"dy": 16, "rot": 3}, "tronco": {"sy": 0.975, "rot": 1.5}, "braco_e": {"dy": 8, "rot": 3},
                             "braco_d": {"dy": 8, "rot": -3}}.items():
                soma(parte, v, cur)
        k = float(pose.get("medo", 0.0))
        if k > 0:
            t = pose.get("t", 0.0)
            tr = 0.9 * k * (math.sin(t * 47.0) + 0.6 * math.sin(t * 83.0 + 1.3))
            for parte, v in {"braco_e": {"dy": -14 * k}, "braco_d": {"dy": -14 * k}, "cabeca": {"dy": 12 * k, "rot": tr},
                             "tronco": {"sx": 1 - 0.03 * k}}.items():
                soma(parte, v)
        ik = {}
        if rep:
            for pe, alvo in REPOUSO_PES.items():
                osso = CADEIAS[pe][0]
                if "rot" not in (pose.get(osso) or {}) or osso in (pose.get("_rep_ossos") or ()):
                    ik[pe] = alvo
        ik.update(pose.get("ik") or {})
        if ik:
            self._resolve_ik(pose, ik)
        return pose

    def _resolve_ik(self, pose, alvos):
        """IK de 2 ossos (lei dos cossenos) em coordenadas do molde, já com a matriz do pai (tronco, quadril)."""
        for chave, alvo in alvos.items():
            if chave not in CADEIAS or alvo is None:
                continue
            o1, o2, fim, dobra = CADEIAS[chave]
            l = -1 if chave.endswith("_e") else 1
            pai = self.rig[o1][0]
            m_pai = self._mundo(pai, pose, {"_raiz": skia.Matrix()}) if pai in self.rig else skia.Matrix()
            j0 = self.rig[o1][1]
            j1 = self.rig[o2][1]
            q1 = pose.get(o1) or {}
            p0 = _xy(m_pai.mapXY(j0[0] + q1.get("dx", 0.0), j0[1] + q1.get("dy", 0.0)))
            ux, uy = _xy(m_pai.mapXY(1.0, 0.0))
            ox, oy = _xy(m_pai.mapXY(0.0, 0.0))
            rot_pai = math.degrees(math.atan2(uy - oy, ux - ox))
            L0 = math.hypot(j1[0] - j0[0], j1[1] - j0[1])
            L1 = math.hypot(fim[0] - j1[0], fim[1] - j1[1])
            tx, ty = alvo[0], alvo[1]
            dx_, dy_ = tx - p0[0], ty - p0[1]
            dist = max(abs(L0 - L1) + 1.0, min(L0 + L1 - 0.5, math.hypot(dx_, dy_)))
            base = math.atan2(dy_, dx_)
            cosa = (L0 * L0 + dist * dist - L1 * L1) / (2 * L0 * dist)
            a = math.acos(max(-1.0, min(1.0, cosa)))
            # dobra pra fora do corpo: no braço/perna esquerdos (l=-1) a junta vai pra -x
            cand = [base + a, base - a]
            ang0 = max(cand, key=lambda g: (math.cos(g) * L0) * l * dobra)
            kx, ky = p0[0] + L0 * math.cos(ang0), p0[1] + L0 * math.sin(ang0)
            ang1 = math.atan2(ty - ky, tx - kx)
            r0 = math.atan2(j1[1] - j0[1], j1[0] - j0[0])
            r1 = math.atan2(fim[1] - j1[1], fim[0] - j1[0])
            rot1 = math.degrees(ang0 - r0) - rot_pai
            rot2 = math.degrees(ang1 - r1) - math.degrees(ang0 - r0)
            pose[o1] = {**(pose.get(o1) or {}), "rot": _norm(rot1)}
            pose[o2] = {**(pose.get(o2) or {}), "rot": _norm(rot2)}
            filho = "mao" + chave[3:] if chave.startswith("mao") else "tenis" + chave[2:]
            if len(alvo) > 2 and alvo[2] is not None:   # ângulo absoluto da mão/pé (graus; 90 = apontando pra baixo)
                rot3 = alvo[2] - 90 - math.degrees(ang1 - r1)
                pose[filho] = {**(pose.get(filho) or {}), "rot": _norm(rot3)}
            elif chave.startswith("pe"):  # pé reto no chão
                pose[filho] = {**(pose.get(filho) or {}), "rot": _norm(-(rot_pai + rot1 + rot2))}

    def no_molde(self, x, y, altura, pose, ponto_tela):
        """Ponto da tela -> coordenadas do molde (pra mirar o IK numa coisa da cena: a boca de outro personagem,
        a maçaneta, o batente)."""
        m = self._raiz(x, y, altura, self._base({k: v for k, v in (pose or {}).items() if k != "ik"}))
        inv = skia.Matrix()
        m.invert(inv)
        return _xy(inv.mapXY(*ponto_tela))

    def boca_tela(self, x, y, altura, pose=None):
        pose = self._base(pose)
        m = self._mundo("boca", pose, {"_raiz": self._raiz(x, y, altura, pose)})
        return _xy(m.mapXY(CX, BOCA_Y))

    def mao(self, lado, x, y, altura, pose=None):
        """Onde está a palma da mão ("e"/"d") na tela nesta pose, e o ângulo da mão (graus)."""
        pose = self._base(pose)
        parte = f"mao_{lado}"
        m = self._mundo(parte, pose, {"_raiz": self._raiz(x, y, altura, pose)})
        wx, wy = _punho(-1 if lado == "e" else 1)
        px, py = m.mapXY(wx, wy + 26)
        cx, cy = m.mapXY(wx, wy)
        return (px, py), math.degrees(math.atan2(py - cy, px - cx)) - 90

    # ------------------------------------------------------------ partes
    # ------------------------------------------------------------ partes (peças de papel)
    def _monta(self, parte, var, expr):
        P = self.pal
        s = self.semente
        d = T.Desenho()
        lado = -1 if parte.endswith("_e") else 1
        sid = T._sem(s, parte) % 100000
        # Com saia/camisola, a coxa e o quadril ficam por baixo do pano: pintados da cor da saia. Assim, quando o joelho
        # sobe na corrida e passa da barra, o que aparece é o pano dobrando por cima da perna, nunca a "aba cor de pele".
        veste = self.cor_saia if self.saia else P.calca
        if parte.startswith("perna"):
            (hx, hy), (kx, ky) = _quadril(lado), _joelho(lado)
            r_quad = (21 if self.fem else 19) * MEMBRO
            self._membro(d, (hx, hy - 14), (kx, ky), r_quad, 14 * MEMBRO, veste, sid)
        elif parte.startswith("canela"):
            (kx, ky), (ax, ay) = _joelho(lado), _tornozelo(lado)
            self._membro(d, (kx, ky), (ax, ay), 14 * MEMBRO, 10.5 * MEMBRO, P.calca, sid)
            b = 13 * MEMBRO   # barra da calça: uma tira de papel mais escura
            T.peca(d, T.quina([(ax - b, ay - 16), (ax + b, ay - 16), (ax + b + 1, ay + 2), (ax - b - 1, ay + 2)], True, 4),
                   T.escurece(P.calca, 0.78), sid + 3, sombra=0.5)
        elif parte.startswith("tenis"):
            self._pe(d, lado, sid)
        elif parte.startswith("braco"):
            (sx, sy), (ex, ey) = _ombro(lado), _cotovelo(lado)
            self._membro(d, (sx, sy), (ex, ey), 17 * MEMBRO, 12.5 * MEMBRO, P.roupa, sid)
        elif parte.startswith("antebraco"):
            self._antebraco(d, lado, sid)
        elif parte.startswith("mao"):
            self._mao(d, lado, sid, expr.get("dedos", 0.35))
        elif parte == "quadril":
            # largo o bastante para cobrir as duas coxas (com membro grosso, a coxa passaria da borda)
            w = max(54 if self.fem else 46, 25 + (21 if self.fem else 19) * MEMBRO + 3)
            pts = [(CX - w, 672), (CX + w, 672), (CX + w + 2, 730), (CX + 6, 740), (CX, 732), (CX - 6, 740), (CX - w - 2, 730)]
            T.peca(d, T.quina(pts, True, 5), veste, sid, sombra=0)
        elif parte == "tronco":
            self._tronco(d, sid, costas=expr.get("costas", False))
        elif parte == "orelhas":
            for l in (-1, 1):
                ox = CX + l * 126
                T.peca(d, T.elipse(ox + l * 8, 228, 20, 27, 24), P.pele, sid + l, sombra=0)
                T.peca(d, T.elipse(ox + l * 10, 230, 9, 14, 16), P.pele_esc, sid + 5 + l, sombra=0, fio=0)
        elif parte == "cabeca":
            self._cabeca(d, sid, expr)
        elif parte == "cabelo":
            self._cabelo(d, sid, frente=True, costas=expr.get("costas", False))
        elif parte == "cabelo_tras":
            self._cabelo(d, sid, frente=False)
        elif parte.startswith("sobrancelha"):
            self._sobrancelha(d, lado, sid, expr)
        elif parte == "boca":
            self._boca(d, sid, expr)
        return d

    def _membro(self, d, a, b, r0, r1, cor, sid, **_):
        """Tira de papel de ponta redonda entre duas juntas. A junta fica coberta pela ponta redonda da peça de cima
        (como boneco de papel preso com colchete), então cotovelo e joelho dobram sem abrir buraco."""
        ax, ay = a
        bx, by = b
        ang = math.atan2(by - ay, bx - ax)
        n = 10
        cap_a = [(ax + r0 * math.cos(ang + math.pi / 2 + math.pi * k / n), ay + r0 * math.sin(ang + math.pi / 2 + math.pi * k / n))
                 for k in range(n + 1)]
        cap_b = [(bx + r1 * math.cos(ang - math.pi / 2 + math.pi * k / n), by + r1 * math.sin(ang - math.pi / 2 + math.pi * k / n))
                 for k in range(n + 1)]
        T.peca(d, np.array(cap_a + cap_b), cor, sid, sombra=0)

    def _antebraco(self, d, l, sid):
        P = self.pal
        (ex, ey), (wx, wy) = _cotovelo(l), _punho(l)
        self._membro(d, (ex, ey), (wx, wy - 8), 12.5 * MEMBRO, 9.5 * MEMBRO, P.roupa, sid)
        b = 10.5 * MEMBRO   # punho da manga: tira mais escura colada por cima
        T.peca(d, T.quina([(wx - b, wy - 18), (wx + b, wy - 18), (wx + b + 1, wy + 1), (wx - b - 1, wy + 1)], True, 4),
               P.roupa_esc, sid + 5, sombra=0.5)

    def _pe(self, d, l, sid):
        """Calçado de papel na variante do estilo (tênis, bota ou pé redondo), com a sola numa tira clara. A sola fica
        reta no y=997 (o IK planta o pé no chão por ela)."""
        P = self.pal
        x0 = CX + l * 25
        k = MEMBRO
        if PE == "bota":
            pts = [(x0 - l * 15 * k, 928), (x0 - l * 18 * k, 996), (x0 + l * 30, 998), (x0 + l * 58, 994), (x0 + l * 66, 978),
                   (x0 + l * 50, 962), (x0 + l * 18 * k, 950), (x0 + l * 15 * k, 928)]
        elif PE == "redondo":
            pts = [(x0 - l * 16 * k, 952), (x0 - l * 22 * k, 990), (x0 + l * 10, 998), (x0 + l * 48, 997), (x0 + l * 70, 984),
                   (x0 + l * 62, 962), (x0 + l * 34, 952), (x0 + l * 12, 946)]
        else:   # tênis de bico curto e alto
            pts = [(x0 - l * 13 * k, 950), (x0 - l * 17 * k, 994), (x0 + l * 30, 997), (x0 + l * 62, 994), (x0 + l * 76, 980),
                   (x0 + l * 72, 966), (x0 + l * 46, 962), (x0 + l * 20, 954), (x0 + l * 12, 946)]
        T.peca(d, T.catmull(pts, True, 6), P.sapato, sid, sombra=0)
        xs = [p[0] for p in pts]
        sola = [(min(xs) + 2, 986), (max(xs) - 3, 984), (max(xs) - 6, 997), (min(xs) + 4, 998)]
        T.peca(d, T.quina(sola, True, 5), P.sola, sid + 3, sombra=0.4)

    def _mao(self, d, l, sid, dobra):
        """Mão de papel presa no pulso (curta: quatro dedos curtos; luva: três dedos gordos); `dobra` 0 (aberta) ..
        1 (fechada). Cada dedo é uma peça; a palma vem por cima."""
        P = self.pal
        wx, wy = _punho(l)
        V = MAOS.get(MAO, MAOS["curta"])
        pw, ph = V["palma"][0] * MEMBRO ** 0.5, V["palma"][1]
        palma = [(wx - pw + 2, wy - 2), (wx + pw - 2, wy - 2), (wx + pw, wy + ph * 0.72), (wx + pw * 0.62, wy + ph),
                 (wx - pw * 0.62, wy + ph), (wx - pw, wy + ph * 0.68)]
        dedos = [(l * dxk * pw / 13, comp) for dxk, comp in V["dedos"]]   # do lado do polegar pro mindinho
        for k, (dxk, comp) in enumerate(dedos):
            x, y = wx + dxk, wy + ph - 4
            ang = math.radians(-dxk * 0.5)
            pts = [(x, y)]
            for j, f in enumerate((0.42, 0.33, 0.25)):
                ang += math.radians(dobra * (28 + 14 * j)) * (-l)
                px, py = pts[-1]
                pts.append((px + math.sin(ang) * comp * f, py + math.cos(ang) * comp * f))
            esq, dir_ = [], []
            raios = [v * V["raio"] * MEMBRO ** 0.5 for v in (4.1, 3.9, 3.6, 3.0)]
            for j in range(len(pts)):
                ax, ay = pts[min(j + 1, len(pts) - 1)]
                bx, by = pts[max(j - 1, 0)]
                nn = math.hypot(ax - bx, ay - by) or 1
                nx, ny = (ay - by) / nn, -(ax - bx) / nn
                esq.append((pts[j][0] + nx * raios[j], pts[j][1] + ny * raios[j]))
                dir_.append((pts[j][0] - nx * raios[j], pts[j][1] - ny * raios[j]))
            ponta = (pts[-1][0] + (pts[-1][0] - pts[-2][0]) * 0.2, pts[-1][1] + (pts[-1][1] - pts[-2][1]) * 0.2)
            T.peca(d, T.catmull(esq + [ponta] + dir_[::-1], True, 4), P.pele, sid + 20 + k, sombra=0.35, borda=0.6)
        e = pw / 11   # polegar acompanha a largura da palma
        polegar = [(wx + l * 10 * e, wy + 8), (wx + l * 21 * e, wy + 18), (wx + l * 24 * e, wy + 32 - 8 * dobra),
                   (wx + l * 17 * e, wy + 36 - 8 * dobra), (wx + l * 8 * e, wy + 26)]
        T.peca(d, T.catmull(polegar, True, 4), P.pele, sid + 40, sombra=0.35, borda=0.6)
        T.peca(d, T.catmull(palma, True, 5), P.pele, sid + 41, sombra=0.5, borda=0.8)

    def _barra_saia(self, m, pose, cache):
        """Pontos da barra (no molde do quadril) para cada perna: joelho + comp * (tornozelo - joelho), em degraus
        de 6 unidades (para o cache de partes)."""
        inv = skia.Matrix()
        m.invert(inv)
        r = []
        for l, parte in ((-1, "canela_e"), (1, "canela_d")):
            mc = self._mundo(parte, pose, cache)
            jx, jy = _xy(mc.mapXY(*_joelho(l)))
            tx, ty = _xy(mc.mapXY(*_tornozelo(l)))
            jx, jy = _xy(inv.mapXY(jx, jy))
            tx, ty = _xy(inv.mapXY(tx, ty))
            k = self.comp_saia
            hx, hy = jx + k * (tx - jx), jy + k * (ty - jy)
            r.append((round(hx / 6) * 6, round(hy / 6) * 6))
        return tuple(r)

    def _pinta_saia(self, c, m, pose, cache, var, esc, sombra=None):
        barra = self._barra_saia(m, pose, cache)
        chave = ("saia", barra)
        self.cache.pega(chave, lambda d: self._saia(d, barra)).pinta_em(c, esc, sombra)

    def _saia(self, d, barra):
        (ex, ey), (dx_, dy_) = barra
        sid = T._sem(self.semente, "saia") % 100000
        esq, dir_ = (ex, ey), (dx_, dy_)
        if esq[0] > dir_[0]:
            esq, dir_ = dir_, esq
        aba = 44 + 26 * self.comp_saia                  # o pano abre em A e passa da canela pra fora
        xl = min(esq[0] - aba, CX - 76)
        xr = max(dir_[0] + aba, CX + 76)
        yl, yr = esq[1], dir_[1]

        def barra_y(f):    # altura da barra entre as duas canelas, com ondas de pano (3 bocas de prega)
            return yl + (yr - yl) * f + 7 * math.sin(f * math.pi * 3.0 + 0.6)

        # o cós cobre o quadril inteiro (±56): nada do quadril aparece dos lados, embaixo da blusa
        topo = [(CX - 50, 676), (CX - 59, 722), (CX - 63, 760)]
        lado_e = [(xl + (CX - 63 - xl) * 0.45, 760 + (yl - 760) * 0.5), (xl, yl - 6)]
        fundo = [(xl + (xr - xl) * f, barra_y(f) + 4) for f in (0.08, 0.26, 0.44, 0.62, 0.8, 0.94)]
        lado_d = [(xr, yr - 6), (xr - (xr - CX - 63) * 0.45, 760 + (yr - 760) * 0.5)]
        topo_d = [(CX + 63, 760), (CX + 59, 722), (CX + 50, 676)]
        pts = topo + lado_e + fundo + lado_d + topo_d
        fill = T.peca(d, T.catmull(pts, True, 6), self.cor_saia, sid, sombra=0)
        sub = T.Desenho()   # barra: uma faixa de papel mais escura colada na borda de baixo
        faixa = [(xl - 10, barra_y(0.0) - 16)] + [(xl + (xr - xl) * f, barra_y(f) - 14) for f in (0.25, 0.5, 0.75)] + \
                [(xr + 10, barra_y(1.0) - 16), (xr + 10, max(yl, yr) + 60), (xl - 10, max(yl, yr) + 60)]
        T.peca(sub, np.array(faixa), T.escurece(self.cor_saia, 0.8), sid + 1, sombra=0.4)
        d.recorte(fill, sub)
        return d

    def _tronco(self, d, sid, costas=False):
        P = self.pal
        g = MEMBRO ** 0.7
        pesc = [(CX - 25 * g, 330), (CX + 23 * g, 330), (CX + 27 * g, 406), (CX - 29 * g, 406)]
        T.peca(d, T.quina(pesc, True, 6), P.pele, sid + 1, sombra=0)
        if self.fem:   # cintura marcada e quadril mais largo
            meia = [(CX + 17, 390), (CX + 38, 410), (CX + 56, 434), (CX + 64, 462), (CX + 58, 508), (CX + 44, 584), (CX + 39, 630),
                    (CX + 52, 690), (CX + 56, 718), (CX, 724)]
        else:
            meia = [(CX + 18, 390), (CX + 40, 410), (CX + 60, 432), (CX + 70, 460), (CX + 63, 506), (CX + 52, 580), (CX + 45, 650),
                    (CX + 50, 716), (CX, 722)]
        pts = meia + [(2 * CX - x, y) for x, y in reversed(meia[:-1])]
        fill = T.peca(d, T.catmull(pts, True, 6), P.roupa, sid, sombra=0)
        if costas:   # de costas: só a gola por trás
            T.peca(d, T.catmull([(CX - 40, 392), (CX, 386), (CX + 40, 392), (CX + 34, 420), (CX, 426), (CX - 34, 420)], True, 6),
                   P.roupa_esc, sid + 5, sombra=0.6)
            return
        if self.cfg.get("roupa_tipo") == "blusa":
            T.peca(d, T.quina([(CX - 26, 394), (CX, 456), (CX + 26, 394)], True, 6), P.pele, sid + 3, sombra=0.5)
            for k, y in enumerate((492, 548, 604, 660)):   # botões: bolinhas de papel
                T.peca(d, T.elipse(CX + 1, y, 6.5, 6.5, 16), T.mistura(P.roupa, (255, 255, 255), 0.5), sid + 10 + k, sombra=0.5,
                       borda=0.3, fio=0)
            for l in (-1, 1):  # gola em duas abas
                T.peca(d, T.quina([(CX + l * 26, 392), (CX + l * 4, 450), (CX + l * 44, 420)], True, 5), P.roupa_esc,
                       sid + 20 + l, sombra=0.7)
        else:
            # capuz amontoado atrás do pescoço, cordões em tirinha e o bolso canguru (uma peça mais escura)
            cap = [(CX - 50, 412), (CX - 28, 386), (CX, 382), (CX + 28, 386), (CX + 50, 412), (CX + 30, 428), (CX, 434), (CX - 30, 428)]
            T.peca(d, T.catmull(cap, True, 6), P.roupa_esc, sid + 5, sombra=0.8)
            cordao = T.mistura(P.roupa, (255, 255, 255), 0.55)
            for l in (-1, 1):
                T.linha(d, [(CX + l * 14, 426), (CX + l * 17, 474), (CX + l * 14, 514)], 4.0, 0, sid + 6 + l, cor=cordao)
            bolso = [(CX - 32, 620), (CX + 32, 620), (CX + 52, 664), (CX + 52, 696), (CX - 52, 696), (CX - 52, 664)]
            T.peca(d, T.quina(bolso, True, 5), T.escurece(P.roupa, 0.86), sid + 9, sombra=0.6)
        # barra da blusa: faixa de papel mais escura em baixo
        sub = T.Desenho()
        T.peca(sub, np.array([(CX - 90, 700), (CX + 90, 696), (CX + 90, 760), (CX - 90, 760)]), P.roupa_esc, sid + 30, sombra=0.4)
        d.recorte(fill, sub)

    def _cabeca(self, d, sid, expr):
        P = self.pal
        medo = expr.get("medo", 0.0)
        T.peca(d, _cabeca_pts(self.cfg.get("rosto", "redondo"), self.idosa), P.pele, sid, sombra=0)
        if expr.get("costas"):   # de costas: só a nuca (o cabelo vem por cima)
            return
        self._nariz_e_marcas(d, sid, medo)

    def _nariz_e_marcas(self, d, sid, medo):
        P = self.pal
        if self.cfg.get("bochecha", True):   # bochecha: dois círculos de papel de seda rosado
            for l in (-1, 1):
                T.mancha(d, T.elipse(CX + l * 82, 284, 22, 17, 24), P.bochecha, 170, semente=sid + 50 + l)
        nariz = NARIZES.get(self.cfg.get("nariz"), self.cfg.get("nariz", "bolinha"))
        ny = 266
        if nariz == "triangulo":
            pts = [(CX - 12, ny - 16), (CX + 14, ny - 10), (CX + 2, ny + 16)]
            T.peca(d, T.quina(pts, True, 5), P.pele_esc, sid + 80, sombra=0.6, borda=0.6)
        elif nariz == "meia_lua":
            pts = [(CX - 18 + 36 * u, ny - 2 + 18 * math.sin(math.pi * u)) for u in np.linspace(0, 1, 12)]
            T.peca(d, np.array(pts), P.pele_esc, sid + 80, sombra=0.6, borda=0.6)
        else:
            T.peca(d, T.elipse(CX + 2, ny, 13, 11, 20), P.pele_esc, sid + 80, sombra=0.6, borda=0.5)
        rug = T.escurece(P.pele, 0.78)
        if self.idosa or self.rugas >= 1:   # idade: do nariz pro canto da boca; testa marcada só em quem é mais velho
            n = 0 if self.rugas < 2 and not self.idosa else (2 if self.rugas < 2 else 3)
            for k in range(n):
                T.linha(d, [(CX - 40, 122 + 12 * k), (CX - 10, 117 + 12 * k), (CX + 18, 121 + 12 * k), (CX + 40, 117 + 12 * k)],
                        3.2, 0, sid + 90 + k, cor=rug, alfa=210)
            for l in (-1, 1):
                T.linha(d, [(CX + l * 30, 288), (CX + l * 42, 312), (CX + l * 40, 334)], 3.4, 0, sid + 100 + l, cor=rug, alfa=210)
                if self.rugas >= 2:   # pé de galinha: três tirinhas no canto do olho
                    for k in range(3):
                        T.linha(d, [(CX + l * 88, EYE_Y - 10 + 10 * k), (CX + l * 104, EYE_Y - 14 + 13 * k)], 2.6, 0,
                                sid + 110 + 3 * l + k, cor=rug, alfa=200, suave=False)

    def _sobrancelha(self, d, l, sid, expr):
        """Sobrancelha: uma tirinha grossa de papel do cabelo; no medo a ponta de dentro sobe."""
        P = self.pal
        k = expr.get("medo", 0.0)
        ox = CX + l * EYE_SEP
        dentro = (ox - l * 24, EYE_Y - 42 - 16 * k)
        meio = (ox - l * 2, EYE_Y - 50 - 8 * k)
        fora = (ox + l * 28, EYE_Y - 42 + 4 * k)
        cor = T.escurece(P.cabelo, 0.8) if not self.idosa else T.mistura(P.cabelo, T.TINTA, 0.25)
        q = T.catmull([dentro, meio, fora], False, 6)
        nrm = np.array([0.0, 1.0])
        larg = np.linspace(11, 7, len(q))[:, None]
        pts = np.vstack([q - nrm * larg / 2, (q + nrm * larg / 2)[::-1]])
        T.peca(d, pts, cor, sid, sombra=0.6, borda=0.5)

    def _boca(self, d, sid, expr):
        """Boca de papel recortado: aberta é um buraco escuro (com tirinha de dente e língua quando cabe); fechada é
        uma tirinha, ou o lábio colado em cima."""
        P = self.pal
        v, k = expr.get("visema", "R"), expr.get("medo", 0.0)
        x, y = CX, BOCA_Y
        abre = {"A": (17, 22), "E": (24, 10), "I": (22, 6), "O": (12, 16), "U": (8, 10), "F": (18, 5)}.get(v)
        if abre is None and k > 0.15:
            abre = (10 + 7 * k, 7 + 12 * k)
        if abre:
            fx, fy = {"cheia": (0.9, 1.0), "fina": (1.12, 0.85), "murcha": (0.8, 0.85)}.get(self.cfg.get("labios"), (1.0, 1.0))
            lx, ly = abre[0] * fx, abre[1] * fy
            pts = [(x - lx, y), (x - lx * 0.5, y - ly * 0.5), (x + lx * 0.4, y - ly * 0.55), (x + lx, y + 1),
                   (x + lx * 0.5, y + ly * 0.75), (x - lx * 0.4, y + ly * 0.8)]
            fill = T.peca(d, T.catmull(pts, True, 6), P.boca, sid, sombra=0.4, borda=0.6)
            sub = T.Desenho()
            if v in ("E", "I", "F") or ly > 14:
                T.peca(sub, np.array([(x - lx, y - ly), (x + lx, y - ly), (x + lx, y - ly * 0.25), (x - lx, y - ly * 0.2)]),
                       P.branco, sid + 1, sombra=0.3, fio=0)
            if ly > 12:
                T.peca(sub, T.elipse(x + 2, y + ly * 0.75, lx * 0.6, ly * 0.4, 16), T.mistura(P.boca, (226, 96, 110), 0.55), sid + 2,
                       sombra=0, fio=0)
            d.recorte(fill, sub)
            return
        if v == "feliz":
            T.linha(d, [(x - 28, y - 4), (x - 10, y + 6), (x + 12, y + 5), (x + 30, y - 6)], 6.0, 0, sid + 3, cor=P.boca)
            return
        labios = self.cfg.get("labios")
        if labios == "cheia":      # lábio cheio: peça rosada colada, com a tirinha escura no meio
            T.peca(d, T.catmull([(x - 17, y + 2), (x - 6, y - 4), (x, y - 1), (x + 6, y - 4), (x + 17, y + 2), (x + 8, y + 12),
                                 (x - 8, y + 12)], True, 6), T.mistura(P.boca, (220, 100, 110), 0.5), sid + 6, sombra=0.4, borda=0.5)
            T.linha(d, [(x - 15, y + 3), (x, y + 4), (x + 15, y + 3)], 2.6, 0, sid + 4, cor=P.boca)
            return
        if labios == "fina":       # tirinha fina e comprida, cantos caídos
            T.linha(d, [(x - 28, y + 9), (x - 14, y + 2), (x + 14, y + 2), (x + 28, y + 9)], 4.4, 0, sid + 4, cor=P.boca)
            return
        if labios == "murcha":     # boca murcha: tirinha curta e franzida
            T.linha(d, [(x - 17, y + 6), (x - 6, y + 2), (x + 7, y + 2), (x + 17, y + 6)], 4.6, 0, sid + 4, cor=P.boca)
            return
        T.linha(d, [(x - 24, y + 4), (x - 8, y), (x + 10, y + 1), (x + 23, y + 5)], 5.0, 0, sid + 4, cor=P.boca)

    def _tampa_cabelo(self, franja):
        """Peça do alto da cabeça: arco por cima do crânio e a linha da testa (`franja`, da direita pra esquerda)."""
        cx, cy = CAB_C
        rx, ry = CAB_RX + 12, CAB_RY + 12
        arco = [(cx + rx * math.cos(a), cy + ry * math.sin(a)) for a in np.linspace(math.radians(170), math.radians(370), 24)]
        return np.array(arco + franja)

    def _cabelo(self, d, sid, frente, costas=False):
        """Cabelo em peças de papel: a franja é cortada na tesoura (zigue-zague, reta de lado, ou em ondas), os cachos
        são bolinhas de papel, o coque é um disco, o longo é uma peça atrás com a ponta em ondas."""
        P = self.pal
        e = self.estilo_cabelo
        rnd = random.Random(self.semente * 7 + (1 if frente else 2))
        cor = P.cabelo
        escuro = T.escurece(cor, 0.78)
        cx, cy = CAB_C
        if not frente:
            if e == "longo":   # a peça de trás: desce até o meio das costas, a ponta cortada em ondas
                pts = [(cx - 150, 150), (cx - 158, 300), (cx - 156, 470)]
                for k in range(7):
                    u = k / 6
                    pts.append((cx - 156 + 312 * u, 560 + (24 if k % 2 else 0)))
                pts += [(cx + 156, 470), (cx + 158, 300), (cx + 150, 150), (cx, 50)]
                T.peca(d, T.catmull(pts, True, 5), escuro, sid, sombra=0)
            elif e == "coque":   # nuca de quem usa coque: o cabelo puxado cobre o crânio por trás
                T.peca(d, T.elipse(cx, cy - 6, CAB_RX + 8, CAB_RY + 4, 48), escuro, sid + 70, sombra=0)
            return
        if costas and e != "longo":   # de costas: o cabelo cobre a nuca inteira
            nuca = [(cx + (CAB_RX + 10) * math.cos(a), cy - 8 + (CAB_RY + 8) * math.sin(a)) for a in np.linspace(0, 2 * np.pi, 40, endpoint=False)]
            nuca = [(x, min(y, 318 + 10 * math.sin(x / 20))) for x, y in nuca]
            T.peca(d, np.array(nuca), cor, sid + 71, sombra=0)
            if e == "coque":
                T.peca(d, T.elipse(cx + 4, 64, 50, 42, 36), cor, sid + 1, sombra=1.0)
            return
        if e == "longo":
            franja = [(cx + 132, 250), (cx + 112, 160), (cx + 60, 120), (cx + 10, 126), (cx + 2, 110), (cx - 40, 128),
                      (cx - 96, 150), (cx - 120, 220), (cx - 136, 250)]
            T.peca(d, self._tampa_cabelo(franja), cor, sid, sombra=0)
            for l in (-1, 1):   # as duas cortinas que descem do lado do rosto
                lado = [(cx + l * 112, 160), (cx + l * 150, 190), (cx + l * 156, 330), (cx + l * 146, 420), (cx + l * 120, 404),
                        (cx + l * 112, 300)]
                T.peca(d, T.catmull(lado, True, 5), cor, sid + 5 + l, sombra=0.8)
            if P.mechas:   # mechas claras: tiras coladas por cima
                mc = T.papel_cor(P.mechas, sat=0.1, luz=(0.7, 0.92))
                for k, l in enumerate((-1, 1)):
                    T.linha(d, [(cx + l * 40, 100), (cx + l * 110, 150), (cx + l * 140, 260), (cx + l * 140, 380)], 9.0, 0, sid + 30 + k, cor=mc)
            return
        if e == "coque":
            T.peca(d, T.elipse(cx + 4, 64, 50, 42, 36), cor, sid + 1, sombra=1.0)
            T.peca(d, T.elipse(cx + 4, 64, 22, 18, 20), escuro, sid + 2, sombra=0.4, fio=0)
            franja = [(cx + 134, 210), (cx + 118, 150), (cx + 70, 112), (cx, 104), (cx - 70, 112), (cx - 118, 150), (cx - 134, 210)]
            T.peca(d, self._tampa_cabelo(franja), cor, sid, sombra=0)
            return
        if e == "curto":   # curto e liso, franja reta cortada de lado (uma tesourada só, em diagonal)
            franja = [(cx + 140, 222), (cx + 128, 150), (cx + 80, 140), (cx + 10, 132), (cx - 60, 118), (cx - 110, 132), (cx - 140, 222)]
            T.peca(d, self._tampa_cabelo(franja), cor, sid, sombra=0)
            return
        if e == "cacheado":   # cachos: bolinhas de papel em volta do alto da cabeça
            for k in range(13):
                u = k / 12
                a = math.pi * (0.92 + 1.16 * u)
                r = CAB_RX + 6 + 8 * math.sin(k * 2.3)
                bx, by = cx + r * math.cos(a), cy - 10 + (CAB_RY + 4) * math.sin(a)
                rr = rnd.uniform(34, 44)
                T.peca(d, T.elipse(bx, by, rr, rr * 0.94, 24), cor if k % 2 else escuro, sid + 40 + k, sombra=0.7)
            return
        # franja em zigue-zague: o corte de tesoura que mais "lê" papel
        franja = [(cx + 138, 230), (cx + 130, 160)]
        n = 7
        for k in range(n + 1):
            u = k / n
            x = cx + 116 - 232 * u
            y = 128 + (26 if k % 2 else 0) + rnd.uniform(-4, 4)
            franja.append((x, y))
        franja += [(cx - 130, 160), (cx - 138, 230)]
        T.peca(d, self._tampa_cabelo(franja), cor, sid, sombra=0)

    def _olho(self, var, l, expr):
        """Olho de papel em 3 camadas: fundo (o oval claro recortado), a pupila (recortada pelo oval, anda com o
        olhar) e a tampa (pálpebra de papel de pele na piscada, cílio em pontinhas)."""
        P = self.pal
        k = expr.get("medo", 0.0)
        pisc = expr.get("piscar", 0.0)
        sid = T._sem(self.semente, "olho", l) % 100000
        ox = CX + l * EYE_SEP
        fundo, iris, tampa = T.Desenho(), T.Desenho(), T.Desenho()
        escuro = T.mistura(P.iris, T.TINTA, 0.35)
        if OLHO == "botao":   # bolinha escura com brilho; arregala no medo; piscada vira tirinha
            r = 13 + 5 * k
            clip = T.caminho(T.elipse(ox, EYE_Y, r + 9, r + 9, 24))
            if k > 0.3:
                T.peca(fundo, T.elipse(ox, EYE_Y, r + 6, r + 6, 28), P.branco, sid, sombra=0.5, borda=0.4)
            if pisc < 0.5:
                T.peca(iris, T.elipse(ox, EYE_Y, r, r * 1.08, 28), escuro, sid + 3, sombra=0.4, borda=0.4)
                iris.pinta(T.caminho(T.elipse(ox - r * 0.3, EYE_Y - r * 0.35, r * 0.28, r * 0.28, 12)), T.tinta_paint(P.branco))
            else:
                T.linha(tampa, [(ox - 16, EYE_Y), (ox, EYE_Y + 5), (ox + 16, EYE_Y)], 5.0, 0, sid + 4, cor=escuro)
            return fundo, clip, iris, tampa
        if OLHO == "fenda":   # meia-lua caída de sono: a tampa de cima fica sempre um pouco fechada
            base_tampa = 0.42 * (1 - k)
        else:
            base_tampa = 0.0
        branco = _olho_branco(l, k)
        branco_p = T.peca(fundo, branco, P.branco, sid, sombra=0.6, borda=0.5)
        r_i = 11.5 - 2.5 * k
        T.peca(iris, T.elipse(ox, EYE_Y + 2, r_i, r_i * 1.1, 24), escuro, sid + 3, sombra=0, borda=0.3, fio=0)
        iris.pinta(T.caminho(T.elipse(ox - 3.5, EYE_Y - 2, 3.4, 3.4, 12)), T.tinta_paint(P.branco))
        cobre = base_tampa + pisc * (1 - base_tampa)
        b = np.asarray(branco)
        topo, base = b[:, 1].min() - 2, b[:, 1].max() + 2
        if cobre > 0.02:
            yb = topo + (base - topo) * cobre
            lid = [(ox - 34, topo - 12), (ox + 34, topo - 12), (ox + 34, yb), (ox, yb + 3), (ox - 34, yb)]
            sub = T.Desenho()
            T.peca(sub, np.array(lid), T.escurece(P.pele, 0.92), sid + 5, sombra=0.6, borda=0.5)
            tampa.recorte(branco_p, sub)
        if self.fem and cobre < 0.9:   # cílios: três pontinhas de papel escuro no canto de fora
            for j in range(3):
                x = ox + l * (8 + 7 * j)
                y = topo + 4 + 3 * j + (base - topo) * cobre
                T.peca(tampa, np.array([(x - l * 3, y + 2), (x + l * 3, y), (x + l * 9, y - 9)]), T.TINTA, sid + 9 + j, sombra=0, fio=0,
                       corte=False)
        return fundo, branco_p, iris, tampa

    def _qa_maos(self, pose):
        """Desenha sozinhos o corpo (tronco, quadril, saia) e cada mão e mede quanto da mão cai dentro da silhueta do
        corpo. Na corrida só conta de costas (de frente o braço dobrado passa na frente do peito de propósito); mão
        listada em pose["atras"] é intencional."""
        ciclo, costas = pose.get("_ciclo"), bool(pose.get("costas"))
        if ciclo == "correr" and not costas:
            return
        atras = set(pose.get("atras") or ())

        def mascara(partes):
            sup = skia.Surface(700, 1150)
            cc = sup.getCanvas()
            cc.clear(skia.Color(0, 0, 0, 0))
            self.desenhar(cc, 350, 1100, 1000, pose, partes=partes)
            return sup.makeImageSnapshot().toarray()[:, :, 3] > 40
        corpo = mascara({"tronco", "quadril", "saia"})
        for lado in ("e", "d"):
            if f"mao_{lado}" in atras:
                continue
            mao = mascara({f"mao_{lado}"})
            n = int(mao.sum())
            if n:
                QA_MAOS["medidas"].append(dict(plano=QA_MAOS["plano"], t=QA_MAOS["t"], lado=lado, nome=self.nome, ciclo=ciclo,
                                               costas=costas, frac=round(float((mao & corpo).sum()) / n, 3)))

    # partes que ganham o tremidinho de recolocar no stop motion (o rosto anda junto com a cabeça)
    TREME = ("tronco", "quadril", "cabeca", "cabelo", "cabelo_tras", "orelhas", "braco_e", "braco_d", "antebraco_e", "antebraco_d",
             "perna_e", "perna_d", "canela_e", "canela_d")
    ROSTO = ("olho", "iris", "palpebra", "sobrancelha", "boca")

    def desenhar(self, c, x, y, altura, pose=None, partes=None):
        if QA_MAOS["ligado"] and partes is None and (pose or {}).get("_ciclo"):
            self._qa_maos(pose)
        pose = self._base(pose)
        t = pose.get("t")
        var = 0
        altura = altura * float(self.cfg.get("alto", 1.0))
        s = altura / 1000.0
        sx, sy = T.sombra_px(altura)
        somb_corpo = (sx * 0.75, sy * 0.75) if partes is None else None   # sombra da peça sobre a de baixo (px da tela)
        somb_rosto = (sx * 0.3, sy * 0.3) if partes is None else None
        if partes is None and T.com_sombra():   # a sombra no chão: uma elipse de papel escuro, dura, puxada pro lado da sombra
            c.drawOval(skia.Rect.MakeLTRB(x - 110 * s + sx * 2, y - 9 * s, x + 110 * s + sx * 2, y + 12 * s),
                       skia.Paint(AntiAlias=True, Color=T.cor_sombra(0.8)))
        cache = {"_raiz": self._raiz(x, y, altura, pose)}
        esc = None if self.vetor else 1.15 * c.getTotalMatrix().getMaxScale() * altura / 1000.0
        medo = round(float(pose.get("medo", 0.0)) * 10) / 10
        visema = pose.get("visema", "R")
        piscar = round(float(pose.get("piscar", 0.0)) * 4) / 4
        ox, oy = pose.get("olhar", (0.0, 0.0))
        ordem = self.ordem
        costas = bool(pose.get("costas"))
        if costas:   # de costas: sem rosto, cabelo de trás por cima de tudo (a nuca e as costas cobertas)
            ordem = [p for p in ordem if not p.startswith(("olho", "iris", "palpebra", "sobrancelha", "boca", "cabelo"))]
            ordem = ordem + ["cabelo_tras"] + (["cabelo"] if self.estilo_cabelo != "longo" else [])
        if pose.get("na_frente"):  # partes que passam na frente do rosto (mão na boca, braço na frente da cara)
            frente = [p for p in ordem if p in pose["na_frente"]]
            ordem = [p for p in ordem if p not in frente] + frente
        for parte in ordem:
            if partes is not None and parte not in partes:
                continue
            if parte.startswith("iris") or parte.startswith("palpebra"):
                continue
            if isinstance(pose.get(parte), dict) and pose[parte].get("some"):
                continue
            m = self._mundo(parte, pose, cache)
            c.save()
            c.concat(m)
            if t is not None and parte in self.TREME:   # recoloca a peça: um tico fora do lugar a cada pose
                dx, dy, g = T.recoloca(t, (self.semente, parte), amp=0.7, giro=0.45)
                px, py = self.rig[parte][1]
                c.translate(px + dx, py + dy)
                c.rotate(g)
                c.translate(-px, -py)
            rosto = parte.startswith(self.ROSTO)
            somb = somb_rosto if rosto else somb_corpo
            if parte.startswith("olho"):
                l = -1 if parte.endswith("_e") else 1
                chave = (parte, medo, piscar)
                cam = self.cache.m.get(chave)
                if cam is None:
                    cam = self._olho(var, l, {"medo": medo, "piscar": piscar})
                    self.cache.m[chave] = cam
                fundo, branco, iris, tampa = cam
                fundo.pinta_em(c, esc, somb)
                c.save()
                c.clipPath(branco, doAntiAlias=True)
                c.concat(self._local("iris" + parte[4:], pose))
                c.translate(ox * 9, oy * 6)
                iris.pinta_em(c, esc)
                c.restore()
                tampa.pinta_em(c, esc)
            elif parte == "saia":
                self._pinta_saia(c, m, pose, cache, var, esc, somb)
            elif parte == "boca" and pose.get("sorriso"):
                self.cache.pega(("boca", "feliz"), lambda d: self._boca(d, T._sem(self.semente, "boca") % 100000,
                                                                       {"visema": "feliz"})).pinta_em(c, esc, somb)
            else:
                expr = {}
                if parte == "cabeca":
                    expr = {"medo": medo, "costas": costas}
                elif parte == "cabelo":
                    expr = {"costas": costas}
                elif parte.startswith("sobrancelha"):
                    expr = {"medo": medo}
                elif parte == "boca":
                    expr = {"medo": medo, "visema": visema}
                elif parte.startswith("mao"):
                    expr = {"dedos": round(float((pose.get(parte) or {}).get("dedos", 0.35)) * 5) / 5}
                elif parte == "tronco" and costas:
                    expr = {"costas": True}
                chave = (parte,) + tuple(sorted(expr.items()))
                self.cache.pega(chave, lambda d, p=parte, e=expr: d.ops.extend(self._monta(p, var, e).ops)).pinta_em(c, esc, somb)
            c.restore()


BonecoGotico = BonecoPapel   # nome antigo


def pose_medo(k=1.0, t=0.0, **extra):
    """Pose de medo pronta (soma com o que vier em extra)."""
    p = {"medo": k, "t": t, "olhar": (0.25 * math.sin(t * 9.0), -0.1)}
    p.update(extra)
    return p


def _xy(p):
    return (p.x(), p.y()) if hasattr(p, "x") else (p[0], p[1])


def _norm(g):
    return (g + 180.0) % 360.0 - 180.0


# ---------------------------------------------------------------- biblioteca de poses
# Coordenadas do molde (pés em y=1000, centro x=500): boca (500, 314), peito (500, 470), ombros y=452, quadril y=712.
# Cada função devolve uma pose completa; `t` liga o stop motion e o tremor, `extra` soma por cima.

def _pose(t, medo, **kw):
    p = {"t": t, "medo": medo, "olhar": (0.25 * math.sin(t * 9.0), -0.1)}
    p.update(kw)
    return p


def pose_repouso(t=0.0, **extra):
    """Repouso natural: contrapposto (o padrão do BonecoPapel, aqui explícito pra quem quiser partir dele)."""
    return _pose(t, 0.0, **extra)


def pose_mao_na_boca(t=0.0, lado="d", **extra):
    """Medo: a mão tapa a boca, a outra segura o próprio cotovelo; ombros pra cima, olho arregalado."""
    o = "e" if lado == "d" else "d"
    l = 1 if lado == "d" else -1
    p = _pose(t, 1.0, na_frente=[f"braco_{lado}", f"antebraco_{lado}", f"mao_{lado}"],
              ik={f"mao_{lado}": (CX + l * 10, 352, -90 - l * 10), f"mao_{o}": (CX + l * 26, 566, 0 if l > 0 else 180)},
              **{f"mao_{lado}": {"dedos": 0.15}, f"mao_{o}": {"dedos": 0.85}, "cabeca": {"dy": 8, "rot": -3 * l}})
    p.update(extra)
    return p


def pose_abracando(t=0.0, **extra):
    """Medo: abraçando o próprio corpo, cabeça baixa, joelhos pra dentro."""
    p = _pose(t, 1.0, ik={"mao_e": (CX + 44, 498, 10), "mao_d": (CX - 40, 512, 170), "pe_e": (CX - 14, 962), "pe_d": (CX + 22, 966)},
              mao_e={"dedos": 0.7}, mao_d={"dedos": 0.7}, cabeca={"dy": 14, "rot": -5}, tronco={"sy": 0.98},
              olhar=(-0.3, 0.35))
    p.update(extra)
    return p


def pose_protegendo(t=0.0, lado="d", **extra):
    """Medo: o braço estica de lado protegendo alguém atrás; a outra mão agarra a roupa no peito; olha pra ameaça."""
    l = 1 if lado == "d" else -1
    o = "e" if lado == "d" else "d"
    p = _pose(t, 1.0, ik={f"mao_{lado}": (CX + l * 236, 556, 90 - l * 70), f"mao_{o}": (CX - l * 6, 470, 90 + l * 70),
                          f"pe_{lado}": (CX + l * 58, 962), f"pe_{o}": (CX - l * 36, 962)},
              **{f"mao_{lado}": {"dedos": 0.0}, f"mao_{o}": {"dedos": 0.9}, "tronco": {"rot": 3 * l}, "cabeca": {"rot": -6 * l}},
              olhar=(-0.9 * l, 0.0))
    p.update(extra)
    return p


def pose_recuando(t=0.0, **extra):
    """Medo: recuando, peso no pé de trás, um pé à frente, as duas mãos abertas na frente do peito."""
    p = _pose(t, 1.0, ik={"mao_e": (CX - 74, 430, -80), "mao_d": (CX + 80, 418, -100), "pe_e": (CX - 34, 958), "pe_d": (CX + 46, 978)},
              mao_e={"dedos": 0.0}, mao_d={"dedos": 0.05}, quadril={"dx": -8, "rot": -2}, tronco={"rot": -2.5, "sy": 0.98},
              cabeca={"dy": 6, "rot": 4}, estica=0.985)
    p.update(extra)
    return p


def pose_de_joelhos(t=0.0, **extra):
    """Medo: encolhido de joelhos, abraçando os joelhos, cabeça enfiada. As coxas apontam pra câmera (encurtadas)."""
    p = _pose(t, 1.0, pulo=-205, repouso=0.0,
              perna_e={"rot": 6, "sy": 0.42}, perna_d={"rot": -6, "sy": 0.42}, canela_e={"sy": 0.22, "rot": -8},
              canela_d={"sy": 0.22, "rot": 8}, tenis_e={"sy": 0.6}, tenis_d={"sy": 0.6},
              tronco={"rot": 2, "sy": 0.9}, cabeca={"dy": 34, "rot": 7},
              ik={"mao_e": (CX + 30, 650, 20), "mao_d": (CX - 26, 664, 160)}, mao_e={"dedos": 0.8}, mao_d={"dedos": 0.8},
              olhar=(0.4, 0.2))
    p.update(extra)
    return p


def pose_batente(t=0.0, lado="e", **extra):
    """Medo: agarrado ao batente (a mão alta do lado, dedos fechados), o corpo encostado atrás, espiando."""
    l = 1 if lado == "d" else -1
    o = "e" if lado == "d" else "d"
    p = _pose(t, 1.0, ik={f"mao_{lado}": (CX + l * 196, 360, -90 + l * 20), f"mao_{o}": (CX + l * 4, 476, 90 - l * 60),
                          f"pe_{lado}": (CX + l * 40, 962), f"pe_{o}": (CX - l * 30, 962)},
              **{f"mao_{lado}": {"dedos": 1.0}, f"mao_{o}": {"dedos": 0.9}, "tronco": {"rot": 4 * l}, "cabeca": {"rot": 9 * l, "dx": l * 6}},
              olhar=(l * 0.9, 0.0))
    p.update(extra)
    return p


POSES_MEDO = {"mao_na_boca": pose_mao_na_boca, "abracando": pose_abracando, "protegendo": pose_protegendo,
              "recuando": pose_recuando, "de_joelhos": pose_de_joelhos, "batente": pose_batente}
