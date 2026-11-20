<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Identidade visual: arte por código ou por IA de imagem

Carregue quando o usuário precisar de **arte** para a identidade do canal: mascote, poses, logo, perfil, banner,
destaques e capas.

## Os dois caminhos (o usuário escolhe na instalação)

1. **O kit faz de graça (recomendado).** `kit/idv/gerar_idv.py` desenha a identidade inteira por código a partir do
   `marca.json` do canal: logo e variações, perfil, banner do YouTube, destaques, modelos de capa, post e cards, e o
   manual. Exemplo completo em `exemplos/canal-pronto/` (o canal "Bicho Esquisito", com o mascote Bubi desenhado
   por código). Instruções em `kit/idv/README.md`.
2. **ChatGPT (precisa de assinatura).** Prompts prontos, uma peça por prompt, em
   `modelos/prompts-chatgpt-identidade.md`, para usar no site ou app do ChatGPT ou no Codex. A arte volta para o
   `kit/idv`, que escreve o texto e monta as peças.

## Regras que valem nos dois

- **Nada de texto na imagem gerada.** Nome do canal, série, "PARTE 1" e a pergunta do voto entram pelo gerador, com a
  fonte certa e sem erro de acento. A IA de imagem erra Ç, Ã e Í.
- **Uma folha do personagem primeiro**, e ela anexada como referência em todos os pedidos seguintes: consistência vem
  da referência, não do texto.
- **Fundo verde chapado (#00FF00)** em vez de "transparente"; magenta (#FF00FF) se o personagem tiver verde. O
  `gerar_idv.py recortar` tira o fundo.
- **Cores com hex e nome** ("coral #FF6B4A"). A correção fina vem no editor.
- **Estilo descrito, nunca nome de estúdio ou artista.** Copiar estilo de marca ou canal conhecido é risco de
  direito autoral e de parecer cópia.
- **Escolha pela miniatura:** reduza para 64 px; se o personagem não se reconhece, gere de novo.
- **Registre a origem** de cada arte (qual IA, quando) no `MANUAL_IDV.md` ou na bíblia da série.

## Personagens do kit e personagens próprios

O motor de animação anima personagens **feitos de partes** (corpo, braços, pernas, olhos, bocas). Os personagens que
vêm no kit (`lola` e `nico`, estilo cápsula) já estão prontos para animar. Um personagem gerado por IA como imagem
inteira serve de capa e de referência de desenho, mas não anima sozinho: para animar, a IA monta as partes a partir
dele (`metodo/visual.md`, seção A1, e `kit/construir_boneco.py`).

## Depois de gerar

1. Recorte o fundo (`gerar_idv.py recortar`) e confira a borda com zoom.
2. Corrija as cores para os hex da marca.
3. Exporte PNG com 1000 px ou mais no lado maior.
4. Jogue no `marca.json` (logo ilustrado, ícone, poses do mascote, pose de cada série) e rode
   `gerar_idv.py tudo`; abra `conferencia.jpg`.
