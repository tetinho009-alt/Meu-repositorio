@echo off
chcp 65001 >nul
title Painel do Temporada Viral (reserva)
cd /d "%~dp0"

echo O jeito normal de abrir o painel é o ícone "Temporada Viral" (área de trabalho ou menu Iniciar),
echo que abre sem esta janela preta. Este arquivo é a reserva, para quando o ícone não existir.
echo Para criar o ícone, peça no chat da IA: "cria o ícone do painel".
echo.

rem Usa o Python do sistema: primeiro o lançador "py", depois "python".
py -3 --version >nul 2>&1
if %errorlevel%==0 (
  py -3 "kit\painel\servidor.py"
  goto fim
)
python --version >nul 2>&1
if %errorlevel%==0 (
  python "kit\painel\servidor.py"
  goto fim
)

echo.
echo Não achei o Python neste computador.
echo Abra a pasta do estúdio na sua IA e peça: "instala o que falta no kit".
echo Depois, dê dois cliques neste arquivo de novo.

:fim
echo.
pause
