<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Formato sério: série no estilo desenhado

Carregue quando a série usa o estilo desenhado (`"estilo": "desenhado"` no `kit/config.json`, estilo sorteado com
`comandos/criar-estilo.md`) e o clima é sombrio ou melancólico. É o formato de mais cuidado do pacote: o traço que
ferve, a câmera que anda no cenário 3D e o silêncio entre as falas só funcionam se nada quebrar a ilusão.

## 1. O clima manda

- **Nada gráfico.** O medo vem do que não se vê: o som que para, a luz que apaga, o relance de 6 quadros.
- **Silêncio é efeito.** Um segundo sem som nenhum antes do susto vale mais que qualquer estrondo.
- **Sem cauda no fim do vídeo** (vale para todo estilo). O episódio termina no CTA da rede. O cartão de produto
  depois do voto quebra o clima justo onde a pessoa decide comentar; a chamada do seu produto vai só na voz, no meio
  (`metodo/engajamento.md`, seção 3). Mesmo com `--cauda`, o `cta_redes.py` pula a cauda quando o estilo é desenhado
  e o clima é sombrio ou melancólico.

## 2. Voz

- **Nunca mude o tempo nem o tom da voz.** Esticar e baixar o tom deixa a fala "tonta, de bêbado". O tratamento é
  só EQ leve, compressão suave e uma sala pequena (`som.voz_gotica`, que recusa qualquer outra coisa).
- **O fim da fala é o fim do som.** A consoante surda ("s", "f", "x") e a respiração vêm depois do fim da palavra.
  Tomada que o gerador cortou ainda soando ganha cauda de soltura de 180 ms no `falas.py --juntar`.
- **Fala atravessa o corte.** Na troca de plano com voz soando, a voz continua inteira por cima do corte.

## 3. Espaço e câmera

- **Com a câmera andando, só a interface fica parada na tela.** Céu, lua, nuvem, corvo, galho e mato do primeiro
  plano andam com a câmera. Nas cenas abertas, passe `ref` = a câmera do primeiro quadro do plano, e câmera que gira
  declara `cam.ceu_ref = (yaw, pitch)` do céu composto.
- **Nada flutua.** Objeto apoiado toca o apoio com ±2 px em todo quadro (`estilo_desenhado/contato.py`).
- **Mão no lugar.** Na caminhada o braço balança solto, ao contrário da perna, com a mão do lado de fora da coxa.

## 4. Capa

- O elenco recortado não pode ter fio de cabelo solto nem corte reto no meio da capa. Lado cortado reto pede destino:
  a base dissolve sozinha; topo e laterais pedem `--sangra esq|dir` ou `--dissolve topo|esq|dir` no `kit/capa.py`,
  senão a capa é recusada.

## 5. Travas antes da prévia

Rode da pasta `kit/`, nessa ordem, e só mostre a prévia com tudo passando:

| Trava | Comando | Reprova quando |
|---|---|---|
| Mãos | `python qa/maos.py` | mão do elenco cai dentro da silhueta do corpo andando ou correndo |
| Espaço | `python qa/espaco.py` (ou `qa.espaco.confere` no plano do episódio) | algo com desenho fica parado na tela com a câmera mexendo |
| Voz | `python qa/voz.py <pasta do --juntar>` | alguma fala termina num degrau seco |
| Pops | `python qa/pops.py <video.mp4> --cortes cortes.json` | objeto some ou aparece de um quadro pro outro sem corte |

Contato (objeto no apoio) entra no script do episódio, nos planos com objeto em cima de móvel: veja o uso no topo de
`kit/estilo_desenhado/contato.py`.

Depois das travas, a grade de 2 s e a prévia no celular continuam obrigatórias (`metodo/checklist.md`).
