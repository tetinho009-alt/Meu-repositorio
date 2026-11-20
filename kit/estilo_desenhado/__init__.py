# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Estilo desenhado (opcional) do kit: recorte de papel colorido. Peças com a borda cortada à mão, fibra de papel,
sombra projetada dura e cenário em camadas de diorama, nas cores da caixa de papéis do canal.

Não altera nada do estilo padrão: maquina/ e os personagens continuam iguais. Uma série no estilo desenhado liga o
estilo trocando a fábrica de bonecos:

    from estilo_desenhado import BonecoPapel as Boneco       # em vez de: from maquina.rig import Boneco
    import estilo_desenhado as G
    with G.quadro(c, t):                                   # acabamento: fibra leve, vinheta fria
        ...
"""
from .tinta import FERVE_HZ, ferve, quadro  # noqa: F401
from .personagem import BonecoGotico, BonecoPapel, ler_config, pose_medo  # noqa: F401
from .ameaca import Rasgado, Vulto  # noqa: F401
