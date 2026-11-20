# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Apresentador animado das cartelas: um personagem do kit (personagens/<nome>) que fala junto com a voz.

No roteiro.json: "apresentador": {"personagem": "nico", "lado": "e", "altura": 470}. Sem esse campo, o vídeo sai
só com as cartelas, como antes.

Boca pela fala (visema palavra a palavra), piscada irregular, respiração e um gesto por tipo de bloco: susto no
gancho, aponta para o item, pula na revelação e acena no voto, no CTA e no fim. Fica no canto de baixo, do lado
oposto à coluna de botões das redes, com os pés abaixo da faixa da legenda.
"""
import math

import skia

from maquina.desenho import H, W, ZS, cheio, ease, radial
from maquina.rig import MEDO, Boneco, piscadas, piscar, respira, visema

PADRAO = {"personagem": "nico", "lado": "e", "altura": 470}


class Apresentador:
    def __init__(self, cfg):
        cfg = cfg if isinstance(cfg, dict) else {"personagem": str(cfg)}
        if not cfg.get("personagem"):  # sem nome no roteiro: o personagem do canal (personagem_novo.py), senão o Nico
            from personagem_novo import personagem_do_canal
            cfg = {**cfg, "personagem": personagem_do_canal() or PADRAO["personagem"]}
        self.cfg = {**PADRAO, **cfg}
        self.b = Boneco(self.cfg["personagem"])
        self.alt = float(self.cfg["altura"])
        esquerda = self.cfg["lado"] != "d"
        self.x = ZS["x0"] + self.alt * 0.30 if esquerda else ZS["x1"] - self.alt * 0.30
        self.olha = 1.0 if esquerda else -1.0       # para onde fica o conteúdo
        self.pe = H - 175
        self.pisca = piscadas(600.0, semente=13)

    @staticmethod
    def _janelas(palavras):
        """[(t, palavra)] -> [(ini, fim, palavra)], cada palavra até a próxima (no máximo 0,45 s)."""
        out = []
        for i, (tp, p) in enumerate(palavras):
            prox = palavras[i + 1][0] if i + 1 < len(palavras) else tp + 0.45
            out.append((tp, min(prox - 0.02, tp + 0.45), p))
        return out

    def _gesto(self, tipo, u, t):
        s = self.olha
        lado_c, lado_o = ("d", "e") if s > 0 else ("e", "d")      # braço do lado do conteúdo e o outro
        sinal_c = -1 if lado_c == "d" else 1
        pose = {}
        fala = 0.5 + 0.5 * math.sin(t * 3.1)
        pose[f"braco_{lado_o}"] = {"rot": -sinal_c * (8 + 6 * fala)}
        pose[f"braco_{lado_c}"] = {"rot": sinal_c * (18 + 14 * fala)}
        pose[f"antebraco_{lado_c}"] = {"rot": sinal_c * (20 + 10 * fala)}
        e = ease(u / 0.25)
        if tipo == "gancho":
            susto = math.exp(-u / 0.5)
            pose.update({k: {kk: vv * (0.4 + 0.6 * susto) for kk, vv in v.items()} for k, v in MEDO.items()})
            pose[f"braco_{lado_c}"] = {"rot": sinal_c * (60 + 50 * susto)}
            pose[f"braco_{lado_o}"] = {"rot": -sinal_c * (60 + 50 * susto)}
            pose[f"antebraco_{lado_c}"] = {"rot": sinal_c * 50}
            pose[f"antebraco_{lado_o}"] = {"rot": -sinal_c * 50}
            pose["pulo"] = 60 * math.sin(min(u / 0.35, 1) * math.pi) if u < 0.35 else 0.0
        elif tipo in ("item", "texto", "imagem", "quiz", "antes_depois"):
            pose[f"braco_{lado_c}"] = {"rot": sinal_c * (40 + 85 * e)}
            pose[f"antebraco_{lado_c}"] = {"rot": sinal_c * (10 - 8 * math.sin(u * 5) * e)}
        elif tipo == "revela":
            pulo = math.sin(min(u / 0.5, 1) * math.pi)
            pose["pulo"] = 110 * pulo
            pose["estica"] = 1 + 0.06 * pulo - 0.08 * math.exp(-((u - 0.5) / 0.08) ** 2)
            for lado, sg in ((lado_c, sinal_c), (lado_o, -sinal_c)):
                pose[f"braco_{lado}"] = {"rot": sg * (150 * e)}
                pose[f"antebraco_{lado}"] = {"rot": sg * 15}
            pose["visema"] = "feliz"
        elif tipo in ("voto", "cta", "fim"):
            pose[f"braco_{lado_c}"] = {"rot": sinal_c * (150 * e)}
            pose[f"antebraco_{lado_c}"] = {"rot": sinal_c * (25 * math.sin(u * 9))}
        return pose

    def desenhar(self, c, t, b, T):
        u = t - b["seg0"]
        entra = 1.0  # já em cena no quadro 0: entrar deslizando deixava a miniatura sem personagem
        pose = self._gesto(b["tipo"], u, t)
        if "visema" not in pose:
            pose["visema"] = visema(t, self._janelas(b["palavras"]))
            if pose["visema"] == "R" and b["tipo"] in ("fim", "cta", "voto") and t > b["t1"]:
                pose["visema"] = "feliz"
        pose["piscar"] = piscar(t, self.pisca)
        pose["tronco"] = respira(t)
        pose["olhar"] = (0.55 * self.olha, -0.15) if b["tipo"] in ("item", "quiz", "imagem") else (0.0, 0.0)
        pose["corpo_rot"] = 2.0 * math.sin(t * 1.3) * self.olha
        x = self.x - self.olha * (1 - entra) * self.alt * 0.9
        # luz de chão com a cor da marca: o personagem não fica flutuando no escuro
        c.drawRect(skia.Rect(0, 0, W, H), radial(x, self.pe, self.alt * 0.55, [(T["destaque2"], 70), (T["destaque2"], 0)]))
        c.drawOval(skia.Rect.MakeLTRB(x - self.alt * 0.28, self.pe - 12, x + self.alt * 0.28, self.pe + 16),
                   cheio(T["destaque2"], 90, blur=10))
        self.b.desenhar(c, x, self.pe, self.alt, pose)
