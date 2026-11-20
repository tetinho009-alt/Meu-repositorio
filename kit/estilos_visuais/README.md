<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Estilos visuais (14 visuais por código)

Quatorze visuais prontos que o kit desenha sozinho, sem IA de imagem, sem crédito pago e sem baixar nada: cada um
gera um vídeo vertical de 10 s (1080x1920, 30 fps), sem voz e sem som, para testar o visual antes de virar série ou
para usar como abertura, gancho ou cena. Todo texto na tela é por código.

## Como rodar (a partir de `kit/`)

1. Confira rápido um quadro antes do vídeo (segundos): `python estilos_visuais/estilos.py <estilo> --quadro 5`.
   Mostre o still ao usuário antes do render.
2. Com o "pode", grave o vídeo: `python estilos_visuais/estilos.py <estilo>`. Sai em `trabalho/estilos/<estilo>.mp4`,
   com o quadro do meio em `trabalho/estilos/stills/<estilo>.png`.
3. Para ver os nomes: `python estilos_visuais/estilos.py --lista`.

Antes de render pesado, confira o espaço livre no disco. Rode no máximo 4 estilos ao mesmo tempo (memória).

| Estilo | O que é | Tempo aproximado |
|---|---|---|
| `low_poly` | 3D facetado com flat shading: boneco andando num campo, a câmera girando | ~4 min |
| `console_antigo` | Gráfico de console dos anos 2000: 360x640 ampliado, vértice tremendo, dithering, névoa e HUD | ~5 min |
| `pov_apocalipse` | Primeira pessoa numa cidade em ruínas à noite, mão de luva com lanterna. Luz por pixel (cone da lanterna, fogo, fumaça, poças). É o mais pesado. | ~33 min, ou ~17 min com `--parte 0/2` e `--parte 1/2` em paralelo |
| `stickman` | Boneco de palito: anda, pula a caixa, corre e comemora | ~2 min |
| `sticker` | Adesivos recortados com borda branca e sombra batendo na tela, com o boneco acenando e o balão "BORA?" | ~2 min |
| `pixel_16bit` | Pixel art em 180x320 ampliado 6x, com parallax, moedas e sprite andando | ~1 min |
| `crt_retro` | A pixel art numa TV de tubo: curvatura, linhas, máscara RGB e chiado | ~3 min |
| `voxel` | Ilha de cubos com árvores e um boneco de cubos, a câmera girando | ~3 min |
| `diorama_iso` | Maquete isométrica com casas, rio, ponte, carrinho e desfoque de miniatura | ~3 min |
| `backrooms_vhs` | Corredores amarelos andados em primeira pessoa, em fita VHS com REC e data | ~4 min |
| `manga` | Página de três quadros em preto e branco com retícula, linhas de ação e balão | ~4 min |
| `anime_cel` | Cel shading de 2 tons com contorno, cabelo espetado, pétalas e céu | ~4 min |
| `recorte_papel` | Camadas de papel com sombra, em stop motion a 12 fps, com boneco de colchetes | ~4 min |
| `massinha` | Bichinho de massinha quicando, entre flores de massinha, a 12 fps | ~4 min |

Juntando o POV em partes: `ffmpeg -f concat -safe 0 -i lista.txt -c copy pov_apocalipse.mp4`, com `lista.txt`
listando `pov_parte0.mp4` e `pov_parte1.mp4` (saem em `trabalho/estilos/`).

## Adaptar para o canal

Os arquivos desta pasta são do kit e não se editam. Para mudar texto, cores, cena ou duração, crie um `.py` na pasta do
episódio que importa o motor e os estilos:

```python
import sys
sys.path.insert(0, r"<pasta do kit>/estilos_visuais")
import motor as M
from estilos import low_poly          # ou copie a função do estilo e mude o que precisar
M.rodar("saida.mp4", low_poly(), still="still.png", n=M.FPS * 12)   # 12 s
```

Peças úteis do `motor.py`:
- `boneco(pose, cores)`: personagem low poly, com corpo e roupa por cima;
- `pose_caminhada(fase)`: a caminhada;
- `texto(...)`: texto na tela;
- `desenhar(...)`: a cena 3D;
- efeitos de pós: `vhs`, `crt`, `dithering`, `meio_tom`, `granulado` e `vinheta`.

## Regras

- **Pose:** joelho só dobra para trás e cotovelo só para a frente. Os sinais são travados em `pose_caminhada` e no boneco de
  palito; pose nova passa por uma folha de quadros antes do render.
- **Sem voz e sem som de fábrica.** Para virar episódio, a narração entra pelo fluxo normal do kit (`falas.py` e a
  trilha). Som, só gerado ou com licença (`metodo/seguranca.md`).
- **Limites conhecidos:** `manga` e `anime_cel` ainda não têm rosto com olhos grandes e expressão, e é o rosto que faz
  esses estilos emocionarem. Para anime de verdade, use o estilo novela anime.
