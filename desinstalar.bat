@echo off
title FocusTrigger - Desinstalador
color 0C

echo ============================================
echo    FOCUSTRIGGER - Desinstalacao
echo ============================================
echo.

:: Remove do startup
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "FocusTrigger" /f >nul 2>&1
echo [OK] Removido do startup do Windows.

:: Mata processo Python rodando
taskkill /F /FI "WINDOWTITLE eq FocusTrigger*" >nul 2>&1
wmic process where "commandline like '%%FocusTrigger.py%%'" delete >nul 2>&1
echo [OK] Processo encerrado.

:: Remove arquivos
set DEST=%APPDATA%\FocusTrigger
if exist "%DEST%" (
    rd /s /q "%DEST%"
    echo [OK] Arquivos removidos de %DEST%
)

echo.
echo FocusTrigger foi completamente desinstalado.
pause
