<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Chave da voz: Google grátis e ElevenLabs

A chave é um código que o serviço de voz te dá para o estúdio usar a voz em seu nome. Ela funciona como uma senha:
fica só neste computador, num arquivo fora da pasta do kit, e nunca vai para a conversa com a IA.

Você só precisa de **uma** das duas. Sem chave nenhuma, o estúdio ainda funciona com a Kokoro (voz grátis, sem
internet), um degrau abaixo na naturalidade.

| | Google (Gemini) | ElevenLabs |
|---|---|---|
| Preço | Grátis, com limite por dia | Paga (o plano Starter já libera uso comercial) |
| Cartão | Não pede | Pede, no site da ElevenLabs |
| Voz em português | Natural | A mais natural |
| Quando o limite acaba | O estúdio espera e tenta de novo | Você recarrega ou espera o mês virar |

## Chave grátis do Google, passo a passo

1. Abra o **Google AI Studio** no navegador: [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Entre com a sua conta do Google (a mesma do Gmail serve).
3. Se aparecer um aviso de termos na primeira vez, leia e aceite para continuar.
4. Clique em **Get API key** ou **Criar chave de API** (o nome muda conforme o idioma da tela).
5. Se ele perguntar o projeto, escolha o que aparecer primeiro ou deixe ele criar um novo.
6. A chave aparece na tela: um código comprido que começa com `AIza`. Clique no botão de copiar ao lado dela.
7. Volte para o painel, abra **Chave da voz**, cole no cartão **Google AI Studio (Gemini)** e clique em
   **Testar e salvar**.
8. Se aparecer "A chave funcionou", pronto. Em **Jeito dos vídeos › Voz**, deixe a voz em **Gemini**.

Bom saber: no plano grátis, o Google usa o texto enviado para melhorar os produtos dele. Quem não quer isso usa a
Kokoro ou a ElevenLabs.

## Chave da ElevenLabs, passo a passo

1. Crie a conta em [elevenlabs.io](https://elevenlabs.io) e assine o plano **Starter** ou acima. O plano grátis da ElevenLabs não dá
   direito de usar a voz em vídeo comercial.
2. Abra a página das chaves: [elevenlabs.io/app/developers/api-keys](https://elevenlabs.io/app/developers/api-keys) (no menu, fica em **Developers** ou em
   **Configurações › API Keys**).
3. Clique em **Create API Key** e dê um nome fácil, por exemplo `temporada viral`.
4. **Permissões (obrigatório):** a ElevenLabs cria a chave com tudo desligado. Ligue **Text to Speech: Access**,
   **Voices: Read** e **User: Read** antes de salvar. Sem o Text to Speech a chave até conecta, mas a voz falha com o
   erro `missing the permission text_to_speech`. Já criou sem? Na mesma página, clique na chave, ligue as três e salve:
   a chave continua a mesma, não precisa colar de novo.
5. Copie a chave assim que ela aparecer: a ElevenLabs mostra a chave inteira uma vez só.
6. Volte para o painel, abra **Chave da voz**, cole no cartão **ElevenLabs** e clique em **Testar e salvar**.
7. Em **Jeito dos vídeos › Voz**, troque a voz para **ElevenLabs**.

Se você usa o Claude no computador, há um caminho sem chave: o conector oficial da ElevenLabs (no Claude,
Configurações › Conectores › ElevenLabs › Conectar). Aí é só pedir no chat: `usa a ElevenLabs pelo conector`.

## Se der errado

| O que aparece | O que fazer |
|---|---|
| "Essa chave parece incompleta" | Copie de novo pelo botão de copiar do site, sem espaço no começo ou no fim |
| "recusou essa chave" | A chave foi apagada ou copiada pela metade. Crie outra no site e cole de novo |
| "Sem internet ou o serviço não respondeu" | Confira a internet e tente de novo em um minuto |
| A voz parou no meio de um vídeo | Acabou o limite do dia (Google) ou os créditos (ElevenLabs). Peça no chat: `a voz acabou, o que eu faço?` |

## Regras que protegem você

- **Nunca cole a chave no chat da IA.** Se colou por engano, apague essa chave no site, crie outra e cole aqui no
  painel.
- Não mande a chave para ninguém, nem por print.
- Antes de qualquer gasto pago, a IA mostra a estimativa e só gera com o seu "pode".
