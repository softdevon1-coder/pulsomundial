@echo off
chcp 65001 > nul
title PulsoMundial - Generador de Trafico Celular 4G/5G
cls
echo ============================================================
echo   PULSOMUNDIAL - GENERADOR DE TRÁFICO ORGÁNICO MÓVIL
echo ============================================================
echo.
echo [1/2] Verificando conexion con el celular Motorola por USB...

.\platform-tools\adb.exe devices | findstr /i "device$" > nul
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] No se detecto el celular autorizado por USB.
    echo Asegurate de:
    echo  1. Tener el cable USB bien enchufado a la compu.
    echo  2. Tener activa la "Depuracion por USB" y haber dado a "Permitir".
    echo  3. Tener activo "Modem USB / Compartir conexion por USB".
    echo.
    pause
    exit /b
)

echo [OK] Celular conectado y autorizado.
echo.
echo [2/2] Iniciando bot con rotacion 1 a 1 de IP celular...
echo   - 1 IP nueva de antena = 1 Visita humana con cookies
echo   - Destino: https://pulsomundial.onrender.com
echo   - Panel en vivo: https://pulsomundial.onrender.com/analytics
echo.
echo Para detener el bot en cualquier momento, cerra esta ventana o presiona Ctrl+C.
echo ============================================================
echo.

python visitor.py --mobile --rotate 1

pause
