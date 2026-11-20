<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Temporada Viral · comece aqui

Esta pasta é o seu estúdio. Você conversa com a IA, ela segue o método e entrega o vídeo pronto pras redes que você
escolher (Instagram, TikTok, YouTube, Kwai), numa pasta por rede.

## Em 3 passos

1. **Abra esta pasta na sua IA** (escolha um dos jeitos abaixo).
2. **Diga "oi".** Na primeira vez, ela pede o e-mail que você usou na compra, para ativar a licença (é pessoal e
   fica ligada a esse e-mail; o reembolso cancela a licença, e o estúdio para de funcionar). Depois ela pergunta se
   você vai pelo caminho grátis ou pelo recomendado, e faz uma entrevista sobre o seu canal, de uns 15 minutos: nome,
   tema, estilo de vídeo, jeito de falar, visual e capa.
   É uma pergunta por vez, com duas sugestões (botões no Claude Code, "a)" e "b)" nas outras IAs).
3. **Peça o primeiro vídeo.** Por exemplo, "faz um vídeo rápido" (um top 5 ou um quiz, pronto em minutos), "nova
   série" ou "explicativo sobre a caixa d'água". Ela vai etapa por etapa e só segue quando você aprova.

## O painel

Na pasta do estúdio, dois cliques em **ABRIR-PAINEL** (no Mac, `ABRIR-PAINEL.command`) abrem o painel no navegador:
o status do computador, o seu canal, as redes, o jeito dos vídeos, os vídeos prontos com a legenda de cada rede e
as métricas. Ele roda só no seu computador. Também dá para pedir à IA: "abre o painel".

## Jeitos de abrir

| Jeito | Para quem | Como |
|---|---|---|
| **App do Claude no computador** (recomendado) | Quem quer que a IA faça tudo: voz, animação, render e pacote | Veja "Abrir no app do Claude" abaixo. Sem terminal |
| **Só no celular** | Quem não tem computador e tem o plano Pro do Claude | Siga `celular/COMECE-AQUI.md`: o Claude Code na nuvem, pelo app do Claude (plano Pro e conta grátis no GitHub). A IA instala com a senha da área de membros e faz o vídeo inteiro. Sem plano pago, não dá pelo celular: use o computador |
| **Antigravity ou Codex (os dois começam grátis), ou Cursor** | Quem quer começar sem gastar (precisa de computador) ou já usa outra IA de código | Abra esta pasta nela; o `AGENTS.md` é a entrada. O Codex grátis entra com a conta grátis do ChatGPT. Antigravity no Windows: `irm https://antigravity.google/cli/install.ps1 \| iex`; no Mac: `curl -fsSL https://antigravity.google/cli/install.sh \| bash`; depois `agy` dentro da pasta |

## Abrir no app do Claude (computador)

Precisa de um plano pago do Claude (o Pro custa US$ 20 por mês). Não precisa de terminal: o app já traz o Claude
Code.

1. **Descompacte o ZIP** fora do OneDrive, do iCloud e do Dropbox, por exemplo em `C:\temporada-viral` no Windows.
   No Windows, a pasta "Documentos" costuma estar dentro do OneDrive: evite. O "Extrair tudo" do Windows cria uma
   pasta dentro da outra (`temporada-viral-v2.2\temporada-viral\`): a certa é a de dentro, a que tem o `CLAUDE.md`.
2. **Instale o app do Claude** para Windows ou Mac (claude.com/download) e entre na sua conta.
3. **Entre em Code**, no canto superior esquerdo do app, e comece um chat novo.
4. **Escolha a pasta.** Embaixo da caixa de mensagem, deixe **Local** e, no botão da pasta, clique em **Abrir
   pasta** (Open folder) e escolha a pasta `temporada-viral` (a de dentro, com o `CLAUDE.md`).
5. **Confirme que confia na pasta**, quando o app perguntar.
6. **Diga "oi".** Ela lê o `CLAUDE.md` sozinha e começa a entrevista.

### Alternativa: pelo terminal

Para quem prefere o terminal. No Windows, abra o PowerShell e cole `irm https://claude.ai/install.ps1 | iex`; no
Mac, abra o Terminal e cole `curl -fsSL https://claude.ai/install.sh | bash`. Feche e abra o terminal de novo e
confira com `claude --version`. Depois abra o terminal dentro da pasta (no Windows: abra a pasta no Explorador,
clique na barra de endereço, digite `cmd` e Enter), digite `claude` e diga "oi".

## O que tem aqui

```
canal/       o seu canal: identidade, pauta, histórico e aprendizados (o questionário preenche)
comandos/    o que a IA faz quando você pede: instalar, novo vídeo, vídeo rápido, painel, publicar, apurar votos
metodo/      o método inteiro: roteiro, voz, som, visual, montagem, capa, plataformas, segurança
modelos/     modelos de bíblia de série, roteiro, post de cada rede e calendário
exemplos/    um episódio comentado do começo ao fim (série com votação de demonstração) e um canal pronto
             (exemplos/canal-pronto: logo, foto de perfil, banner, destaques, bio e primeiros posts)
celular/     o passo a passo do celular (Claude Code na nuvem, com o plano Pro do Claude)
kit/         o código: animação 2D com luz e personagem 3D opcional (render na GPU), o motor de cartelas (top 5,
             quiz, tipografia, faceless, antes e depois), vozes uma tomada por fala,
             legenda palavra por palavra, tela de voto e apuração animada, capa e legenda de cada rede,
             publicação pelas APIs oficiais, robô de respostas e o site do placar ao vivo
LINKS.md     as ferramentas recomendadas (os links de afiliado vêm marcados)
```

## Quanto custa usar

- **Dá pra começar com R$ 0, mas só no computador:** o Antigravity (a IA grátis do Google) ou o Codex (com a
  conta grátis do ChatGPT) faz o vídeo, com a voz grátis do Google (Gemini) ou a Kokoro. Demora mais, tem limite por
  dia, e a voz é um degrau abaixo. Os dois caminhos estão em `metodo/caminhos.md`.
- **Pelo celular:** precisa do plano Pro do Claude.
- **Voz caprichada:** a ElevenLabs custa a partir de US$ 6 por mês, e o plano grátis dela não permite uso comercial.
- **IA paga, se quiser:** o plano Pro do Claude (Claude Code, o recomendado) ou um plano pago do ChatGPT, que
  aumenta o limite do Codex.
- **Site do placar (opcional):** grátis no GitHub Pages. As APIs oficiais das redes também são grátis.

Detalhes em `metodo/pilhas-e-ferramentas.md`.

## Regras que protegem a sua conta

O estúdio já segue estas regras sozinho:
- só posta pelos caminhos oficiais;
- nunca usa "comenta X ou Y";
- só usa áudio com licença;
- marca ficção e conteúdo de IA quando a rede pede.

Leia `metodo/seguranca.md` uma vez.

## Suporte

Pelos comentários da área de membros da Temporada Viral ou em contato@temporadaviral.com, até você postar a sua
primeira parte 1.

Licença de uso pessoal: veja `LICENCA_E_TERMOS.md`. Não é permitido revender nem compartilhar esta pasta.

© 2026 Temporada Viral. Todos os direitos reservados.
