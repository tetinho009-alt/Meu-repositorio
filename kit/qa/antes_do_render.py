# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""Trava antes do render: o que já custou vídeo refeito vira conferência automática.

Cada regra aqui veio de um episódio real que deu errado (metodo/licoes.md):
- disco: render enche o disco em minutos (abaixo de 5 GB para, abaixo de 30 GB avisa);
- gancho: o primeiro bloco precisa caber nos 3 primeiros segundos, abrir uma lacuna, ter texto na tela e começar a
  falar até 0,5 s (75% sai em 10 s). Detalhes em qa/gancho.py e metodo/ganchos.md;
- viradas: um "só que..." a cada 15 s no máximo (aviso);
- duração: cada estilo tem a sua faixa (metodo/estilos/);
- palavras que a Meta pune (renda extra, ganhe dinheiro...) e isca de engajamento;
- termo em inglês fora da base de pronúncia (a voz erra; reescreva a frase);
- emenda de áudio em cima de fala (corte no meio da palavra);
- voz diferente do roteiro (a voz engole ou repete trecho).

Uso direto (da pasta kit/):
    python qa/antes_do_render.py <roteiro.json> [--duracao S] [--estilo top5]
Sai com código 1 se houver erro. Os avisos não param o render, mas a IA conta ao usuário.
"""
import json
import re
import shutil
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
if str(KIT) not in sys.path:
    sys.path.insert(0, str(KIT))

# estilo -> (mínimo, ideal_ini, ideal_fim, máximo) em segundos. Fonte: metodo/estilos/README.md
DURACAO = {
    "serie-2d-voto": (90, 105, 140, 160),
    "terror-voto": (90, 105, 135, 160),
    "pov": (90, 110, 140, 160),
    "novela-anime": (90, 120, 150, 160),
    "novela-frutas": (8, 10, 35, 45),
    "explicativo-3d": (30, 40, 65, 75),
    "tipografia": (15, 20, 40, 50),
    "faceless": (35, 45, 80, 100),
    "top5": (30, 35, 55, 70),
    "historia-real": (50, 60, 110, 150),
    "antes-depois": (15, 20, 40, 55),
    "bastidores": (25, 30, 55, 75),
    "quiz": (25, 30, 55, 70),
    "amostra": (8, 9, 12, 15),   # exemplos de 10 s de cada estilo (exemplos/estilos/)
    "teste": (3, 4, 7, 9),       # vídeo de teste de ~5 s ("teste": true no roteiro): confere o caminho sem pesar o PC
}

PROIBIDAS = re.compile(r"\b(ganhe dinheiro|ganhar dinheiro f[aá]cil|renda extra|lucre|lucrar|fature|faturar|fique rico|"
                       r"ficar rico|dinheiro garantido|views garantid\w*|seguidores garantid\w*)\b", re.I)
ISCA = re.compile(r"\b(curte e compartilha|compartilha com \d+|manda (pra|para) \d+ amigos|marca (algu[eé]m|um amigo)|"
                  r"comenta (quero|eu quero|sim)|comenta pra receber|me chama na dm|manda dm)\b", re.I)
# Palavras em inglês que aparecem muito em roteiro e a voz em português fala errado. As que estão na base de
# pronúncia (voz/pronuncia.json) são trocadas sozinhas; estas não estão: reescreva a frase.
INGLES = re.compile(r"\b(app|apps|print|post|selfie|flash|feed|like|likes|story|stories|hashtag|online|"
                    r"influencer|crush|top|fake|spoiler|game|gamer|hater|haters|vibe|design|look|mindset|"
                    r"insight|trend|trending)\b", re.I)


def disco(pasta):
    livre = shutil.disk_usage(pasta).free / 1024 ** 3
    if livre < 5:
        return [f"disco com {livre:.1f} GB livres: o render precisa de uns 5 GB. Apague testes antigos em trabalho/"], []
    if livre < 30:
        return [], [f"disco com {livre:.0f} GB livres; depois de aprovar, apague os quadros e testes do episódio"]
    return [], []


def textos(falas, telas=()):
    """Erros e avisos nos textos da voz e da tela."""
    from voz.pronuncia import fora_da_fala
    erros, avisos = [], []
    for i, f in enumerate(falas):
        if PROIBIDAS.search(f):
            erros.append(f"bloco {i + 1}: '{PROIBIDAS.search(f).group(0)}' derruba a distribuição na Meta; tire da fala")
        if ISCA.search(f):
            erros.append(f"bloco {i + 1}: '{ISCA.search(f).group(0)}' é isca de engajamento; use uma pergunta aberta")
        for termo in fora_da_fala(f):
            erros.append(f"bloco {i + 1}: '{termo}' não pode ser falado (a voz erra sempre); mostre só na tela")
        achados = sorted({m.group(0).lower() for m in INGLES.finditer(f)})
        if achados:
            avisos.append(f"bloco {i + 1}: palavra em inglês fora da base de pronúncia ({', '.join(achados)}); "
                          "reescreva em português (ex.: 'aplicativo' em vez de 'app')")
    for i, t in enumerate(telas):
        if t and PROIBIDAS.search(t):
            erros.append(f"tela do bloco {i + 1}: '{PROIBIDAS.search(t).group(0)}' é proibido na tela também")
    return erros, avisos


def duracao(segundos, estilo):
    if estilo not in DURACAO:
        return [], []
    mn, i0, i1, mx = DURACAO[estilo]
    if segundos < mn or segundos > mx:
        return [f"vídeo com {segundos:.0f} s, fora da faixa do estilo {estilo} ({mn} a {mx} s). "
                f"Ajuste o roteiro: tempo a mais vem de história (mais viradas), nunca de fala esticada"], []
    if segundos < i0 or segundos > i1:
        return [], [f"vídeo com {segundos:.0f} s; o ideal do estilo {estilo} é {i0} a {i1} s"]
    return [], []


def gancho(dur_primeiro, tem_texto, fala=None, inicio_fala_s=None, tela=None):
    """Trava do gancho (qa/gancho.py), com o limite das preferências (ganchos.gancho_max_s).

    `dur_primeiro`: segundo em que a fala do bloco 1 termina. `tem_texto`: o bloco 1 tem texto na tela.
    Com `fala`, confere também se a abertura abre lacuna; com `inicio_fala_s`, se a abertura é muda."""
    from qa import gancho as G
    erros, avisos = G.checar_tempo(dur_primeiro, inicio_fala_s)
    if fala is not None:
        e, a = G.checar_fala(fala)
        erros, avisos = erros + e, avisos + a
    if tela is not None or not tem_texto:
        e, a = G.checar_tela(tela or "")
        erros, avisos = erros + e, avisos + a
    return erros, avisos


def gancho_roteiro(blocos):
    """Gancho e viradas de um roteiro de cartelas antes da voz, com os tempos estimados pelo ritmo médio da fala."""
    from qa import gancho as G
    if not blocos:
        return [], []
    b0 = blocos[0]
    erros, avisos = G.avaliar(b0.get("fala", ""), b0.get("tela", ""), G.estimar_s(b0.get("fala", "")), G.INICIO_PADRAO)
    janelas, t = [], G.INICIO_PADRAO
    for i, b in enumerate(blocos):
        t1 = G.estimar_s(b.get("fala", ""), t) or t
        janelas.append({"t0": t, "t1": t1})
        t = t1 + float(b.get("contagem", 0) or 0) + float(b.get("pausa", 0.35 if i < len(blocos) - 1 else 0.6))
    return erros, avisos + G.viradas(blocos, janelas)


def emendas(amostras, sr, cortes, limiar_db=-30.0):
    """Corte de áudio em cima de fala: RMS em ±10 ms do corte acima de `limiar_db` do pico (p99)."""
    import numpy as np
    x = np.abs(np.asarray(amostras, dtype=np.float64))
    if not len(x):
        return []
    ref = np.percentile(x, 99) + 1e-9
    ruins = []
    for t in cortes:
        i = int(t * sr)
        j = x[max(0, i - sr // 100): i + sr // 100]
        if len(j) and 20 * np.log10(np.sqrt(np.mean(j ** 2)) / ref + 1e-12) > limiar_db:
            ruins.append(round(t, 2))
    return [f"emenda em cima de fala em {', '.join(map(str, ruins))} s: a palavra sai cortada. Refaça o bloco"] \
        if ruins else []


def semelhanca(casadas, total):
    if total and casadas / total < 0.85:
        return [f"só {100 * casadas / total:.0f}% das palavras da voz batem com o roteiro: a voz pode ter engolido ou "
                "repetido um trecho. Ouça os blocos marcados e refaça os que estiverem errados"]
    return []


def relatorio(erros, avisos, titulo="CONFERÊNCIA ANTES DO RENDER"):
    print(f"\n== {titulo}")
    for e in erros:
        print(f"  ERRO  {e}")
    for a in avisos:
        print(f"  AVISO {a}")
    if not erros and not avisos:
        print("  tudo certo")
    return not erros


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("roteiro")
    ap.add_argument("--duracao", type=float)
    ap.add_argument("--estilo")
    a = ap.parse_args()
    r = json.loads(Path(a.roteiro).read_text(encoding="utf-8"))
    blocos = r.get("blocos", [])
    erros, avisos = disco(Path(a.roteiro).parent)
    e, av = textos([b.get("fala", "") for b in blocos], [b.get("tela", "") for b in blocos])
    erros += e
    avisos += av
    if blocos and "fala" in blocos[0]:
        e, av = gancho_roteiro(blocos)
        erros += e
        avisos += av
    estilo = a.estilo or r.get("estilo")
    if a.duracao:
        e, av = duracao(a.duracao, estilo)
        erros += e
        avisos += av
    sys.exit(0 if relatorio(erros, avisos) else 1)


if __name__ == "__main__":
    from erros import rodar_amigavel
    rodar_amigavel(main)
