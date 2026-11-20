#!/bin/bash
# Painel do Temporada Viral (Mac), reserva: o jeito normal é o app "Temporada Viral" (em Aplicativos e na Mesa),
# que abre sem o Terminal. Este arquivo serve para quando o app não existir.
cd "$(dirname "$0")" || exit 1

echo "O jeito normal de abrir o painel é o app Temporada Viral (Aplicativos ou Mesa), sem esta janela."
echo "Para criar o app, peça no chat da IA: \"cria o ícone do painel\"."
echo ""

if command -v python3 >/dev/null 2>&1; then
  python3 kit/painel/servidor.py
elif command -v python >/dev/null 2>&1; then
  python kit/painel/servidor.py
else
  echo ""
  echo "Não achei o Python neste computador."
  echo "Abra a pasta do estúdio na sua IA e peça: \"instala o que falta no kit\"."
fi

echo ""
read -n 1 -s -r -p "Aperte qualquer tecla para fechar esta janela."
