@echo off
title IA PARK

cd /d "D:\Estudios_CSA\Grado_Ingenieria_Sistemas_de_TIC\2026-2027_TFG\VS\IA Park\IA Park"

echo ==========================================
echo          IA PARK - INICIANDO
echo ==========================================
echo.

REM Arrancar servidor FastAPI en otra ventana
start "IA PARK - SERVIDOR" cmd /k "python -m uvicorn app:app --reload"

REM Esperar 2 segundos para que arranque el servidor
timeout /t 2 /nobreak >nul

REM Abrir IA Park en Google Chrome
start chrome "http://127.0.0.1:8000"

exit