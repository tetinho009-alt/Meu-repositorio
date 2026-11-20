<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Exemplos de 10 segundos, um por estilo

Cada pasta tem um vídeo curto (`exemplo.mp4`) e a capa (`capa.jpg`) de um dos 12 estilos, feitos no caminho grátis:
voz Kokoro, desenho por código e trilha por código, sem gastar crédito. Eles também aparecem no painel, na tela
Estilos. Servem para o dono do canal escolher o estilo vendo, e para a IA ter um ponto de partida que já funciona.

| Estilo | O que mostra | Motor | Para refazer (a partir de `kit/`) |
|---|---|---|---|
| Série 2D com voto | a Lola descobre senha na geladeira; voto no fim | rig 2D | `python ../exemplos/estilos/serie-2d-voto/cena.py` |
| Terror com voto | estrada na neblina, batidas na porta, voto | estilo desenhado | `python ../exemplos/estilos/terror-voto/cena.py` |
| POV | o vizinho novo olha nos seus olhos e dá um aviso | rig 2D | `python ../exemplos/estilos/pov/cena.py` |
| Novela | reencontro no pôr do sol, rosto corado, voto | rig 2D | `python ../exemplos/estilos/novela-anime/cena.py` |
| Explicativo 3D | a caravela-portuguesa não é uma água-viva | Blender | `python explicativo3d/exemplo/rodar.py` |
| Top 5 | 3 bichos que dormem esquisito, com apresentadora | cartelas | `python cartelas/rodar.py ../exemplos/estilos/top5` |
| Quiz | o maior planeta, contagem e revelação | cartelas | `python cartelas/rodar.py ../exemplos/estilos/quiz` |
| História real | a cidade que não parava de dançar (1518) | cartelas | `python cartelas/rodar.py ../exemplos/estilos/historia-real` |
| Antes e depois | a mesma ideia em duas capas | cartelas | `python cartelas/rodar.py ../exemplos/estilos/antes-depois` |
| Bastidores | como este tipo de vídeo sai de graça | cartelas | `python cartelas/rodar.py ../exemplos/estilos/bastidores` |
| Tipografia | frase de treino, palavra por palavra | cartelas | `python cartelas/rodar.py ../exemplos/estilos/tipografia` |
| Faceless | a cidade que some do mapa (ficção), sem rosto | cartelas | `python cartelas/rodar.py ../exemplos/estilos/faceless` |

Acrescente `--stills` para ver só os quadros-marco antes (meio minuto) e `--cpu` em computador sem placa de vídeo.
Nos de cartelas, `--sem-pacote` pula a pasta das redes.

## Como usar um exemplo como ponto de partida

1. Copie a pasta do estilo para `trabalho/` com outro nome.
2. Troque as falas (no `roteiro.json` das cartelas, ou na lista `FALAS` do `cena.py`) e, se quiser, o personagem.
3. Rode com `--stills`, aprove os quadros e rode de novo sem `--stills`.

Os exemplos têm a duração de amostra (`"amostra": true`, de 8 a 15 s). Um vídeo de verdade segue a duração do
estilo (`metodo/estilos/README.md`), e a trava antes do render confere isso.

As imagens do antes e depois, dos bastidores e do faceless são geradas por `imagens.py`, também por código.
