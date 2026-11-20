<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Vídeo longo 16:9 (opcional)

O padrão do canal continua sendo o vertical, nas redes escolhidas. O vídeo longo é uma **opção**: a série pronta, ou um
bloco de 3 partes, vira um "filme" horizontal para o YouTube. Quem decide fazer é o usuário. Ofereça quando a série
tiver 3 partes decididas, sem empurrar.

## Formato

- **1920x1080, 60 fps** (30 fps sem placa de vídeo), de 5 a 15 min.
- **As partes já decididas, emendadas.** A tela de voto e o CTA de cada parte saem; a história corre direto.
- **Abertura própria,** sem voz até os 5 s, com o nome da série. No fim, **um único** CTA, sem cauda de produto.
- **Capa 1280x720** no estilo da série, com rosto grande, texto curto e a parte ou temporada.
- **Título e descrição longos, com capítulos** (00:00 Parte 1, 04:10 Parte 2…). O link vai com UTM próprio:
  `utm_source=youtube&utm_medium=descricao&utm_content=<serie>-longo`.

## Como fazer sem refazer a série

O longo **não é o vertical recortado**. É a mesma cena com a câmera recomposta para 16:9. Para sair barato:

1. **Câmera que funciona nos dois formatos.** Desde o roteiro, componha os planos com o cenário mais largo que o
   quadro vertical. O horizontal mostra mais dos lados e menos de cima e de baixo: personagem e ação ficam no meio
   da altura, nada importante no topo nem no pé do quadro vertical, e o fundo continua para os lados. Use `W` e `H` (de `maquina.desenho`) em vez de 1080 e 1920
   escritos no código, para o mesmo `quadro(c, t)` servir aos dois tamanhos.
2. **Tela re-diagramada.** Legenda, selo e intertítulo são posicionados por `W` e `H`. A tela de voto e o CTA não
   entram no longo.
3. **Render em 16:9.** Copie o `kit/config.json` para `kit/config_16x9.json`, troque `render.largura` por 1920 e
   `render.altura` por 1080, e renderize cada parte sem o trecho do voto:

   ```
   set MAQUINA_CONFIG=config_16x9.json        (Windows; no Mac/Linux: export MAQUINA_CONFIG=config_16x9.json)
   python <episodio>/ep.py                    (o mesmo script da parte, com outro nome de saída)
   ```

   No estilo desenhado, a interface aceita `W` e `H` como parâmetro, mas os cenários foram desenhados para o quadro em
   pé: renderize um plano de teste em 16:9 antes de prometer o longo de uma série gótica. Em qualquer estilo, confira
   a folha de quadros-marco do 16:9 antes do render inteiro. Plano que só funciona em pé é recomposto, nunca
   esticado.
4. **Emendar, capitular e fazer a capa:**

   ```
   python filme_longo.py --serie "Nome da Série" --saida trabalho/longo \
       --parte trabalho/p1_16x9.mp4 "Parte 1" --parte trabalho/p2_16x9.mp4 "Parte 2" --parte trabalho/p3_16x9.mp4 "Parte 3" \
       --fim trabalho/fim_16x9.mp4 --capa-texto "ELE VOLTOU" --link "<seu link com UTM>"
   ```

   Saem o filme, a `capa_youtube.jpg` e a `descricao.md`, com o título, os capítulos já cronometrados e o link. Um
   vídeo vertical na lista é recusado.

## Antes de subir

- Capítulos: o primeiro em 00:00, pelo menos 3 e cada um com 10 s ou mais; sem isso, o YouTube não mostra. A
  ferramenta já junta a abertura ao primeiro capítulo e o fim ao último.
- O mesmo rótulo de IA e de ficção das partes (`metodo/seguranca.md`).
- Confirmação do usuário antes de publicar, como em todo vídeo.
