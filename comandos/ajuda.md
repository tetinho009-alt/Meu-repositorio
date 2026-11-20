<!-- © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C -->
# Ajuda: travou, não entendeu ou deu erro

Use quando o usuário disser "não entendi", "me ajuda", "travei", "deu erro", "o que eu faço agora?", ou colar uma
mensagem de erro.

## Como responder

1. **Uma coisa por vez.** Diga só o próximo passo, em uma ou duas frases, e espere ele dizer que fez. Nada de lista
   de dez comandos.
2. **Palavra técnica vem traduzida.** Terminal é "a janela onde se digitam comandos"; chave de API é "uma senha que
   a ferramenta te dá pra outra ferramenta usar"; `.env` é "um arquivo de senhas que fica só no seu computador".
3. **Erro: você resolve, ele não.** No modo agente, leia o erro, descubra a causa e corrija sozinho. Conte em uma
   frase o que era ("faltava instalar o ffmpeg, já instalei") e siga de onde parou. Se a correção precisar dele
   (aceitar uma permissão, abrir um site, pagar um plano), diga exatamente onde clicar.
4. **Nunca julgue a pergunta.** Pergunta repetida recebe a mesma paciência. Quem pergunta mais aprende mais rápido:
   diga isso uma vez, na primeira dúvida.
5. **Não peça senha nem chave na conversa.** Chave de voz vai pela janela (`python chave.py`). Se ele colar uma chave
   aqui por engano, peça que apague essa chave no site, crie outra e use a janela.

## Dúvidas comuns

| Ele diz | Você responde |
|---|---|
| "O que é esse pedido de permissão?" | O que o comando faz, em meia frase, e se pode aceitar. |
| "Demorou, travou?" | Quanto falta, pelo que o comando mostra. Render longo roda em segundo plano: avise o tempo antes. |
| "A voz acabou" | `python chave.py --conferir` mostra o saldo e a data em que renova; ofereça a voz grátis até lá. |
| "Ficou feio / não gostei" | Peça o número da cena (da folha) e o que ele queria no lugar. Anote em `canal/aprendizados.md`. |
| "Quero mudar o canal" | `comandos/instalar.md`, só nas perguntas que ele quer mudar. |
