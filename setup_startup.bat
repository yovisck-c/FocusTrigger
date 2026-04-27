@echo off
title FocusTrigger - Setup
color 0A

echo ============================================
echo    FOCUSTRIGGER - Setup de Instalacao
echo ============================================
echo.

:: Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Instale em: https://www.python.org/downloads/
    echo Marque "Add Python to PATH" durante a instalacao.
    pause
    exit /b 1
)
echo [OK] Python encontrado.

:: Instala dependências
echo.
echo Instalando dependencias...
pip install pystray pillow requests --quiet
if errorlevel 1 (
    echo [AVISO] Erro ao instalar pystray/pillow.
    echo O app vai funcionar sem icone na bandeja.
)
echo [OK] Dependencias prontas.

:: Copia FocusTrigger.py para pasta definitiva
set DEST=%APPDATA%\FocusTrigger
if not exist "%DEST%" mkdir "%DEST%"
copy /Y "%~FocusTrigger.py" "%DEST%\FocusTrigger.py" >nul
echo [OK] Arquivos copiados para %DEST%

:: Pergunta sobre API Key (opcional)
echo.
echo ============================================
echo  API KEY da Anthropic (OPCIONAL)
echo ============================================
echo  Sem a API key, o app usa questoes fixas.
echo  Com ela, o Claude gera questoes novas toda hora!
echo  Obtenha em: https://console.anthropic.com
echo ============================================
set /p APIKEY="Cole sua API Key aqui (ou ENTER para pular): "
if not "%APIKEY%"=="" (
    echo %APIKEY%> "%DEST%\apikey.txt"
    echo [OK] API Key salva.
) else (
    echo [OK] Sem API Key - usando questoes do banco local.
)

:: Cria script VBS para rodar invisível (sem janela preta)
set VBS=%DEST%\FocusTrigger_launcher.vbs
echo Set WshShell = CreateObject("WScript.Shell") > "%VBS%"
echo WshShell.Run "python ""%DEST%\FocusTrigger.py""", 0, False >> "%VBS%"

:: Adiciona ao startup do Windows (HKCU - sem precisar de admin)
set STARTUP_KEY=HKCU\Software\Microsoft\Windows\CurrentVersion\Run
reg add "%STARTUP_KEY%" /v "FocusTrigger" /t REG_SZ /d "wscript.exe \"%VBS%\"" /f >nul
echo [OK] FocusTrigger configurado para iniciar com o Windows.

echo.
echo Iniciando FocusTrigger agora...
start "" wscript.exe "%VBS%"

echo.
echo ============================================
echo  INSTALACAO CONCLUIDA!
echo ============================================
echo.
echo  - FocusTrigger esta rodando em background
echo  - Um pop-up aparecera a cada 1 hora
echo  - Procure o icone verde na bandeja (canto
echo    inferior direito) para Pausar ou Sair
echo  - Para desinstalar: rode desinstalar.bat
echo.
echo  DICA: Clique direito no icone da bandeja
echo  para PAUSAR durante os jogos!
echo.
pause
