@echo off
REM ── Botty Flasher — Build .exe ──────────────────────────
REM
REM Compila flash_botty.py a un unico .exe con PyInstaller.
REM El .exe incluye TODO el proyecto Botty empaquetado dentro
REM (botty/*, scripts/*, pyproject.toml, requirements.txt).
REM
REM Requisitos:
REM   pip install pyinstaller paramiko
REM
REM Uso:
REM   scripts\build_exe.bat
REM   dist\flash_botty.exe
REM ─────────────────────────────────────────────────────────

setlocal enabledelayedexpansion
set PROJECT_DIR=%~dp0..
set SCRIPT_DIR=%~dp0

echo ====================================
echo  Botty Flasher — Build .exe
echo ====================================
echo.

REM ── Verificar dependencias ──
where pyinstaller >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] pyinstaller no encontrado.
    echo   Instala: pip install pyinstaller
    pause
    exit /b 1
)

python -c "import paramiko" 2>nul
if %ERRORLEVEL% neq 0 (
    echo [AVISO] paramiko no instalado.
    echo   Se necesita para conectar por SSH.
    echo   Instala: pip install paramiko
    echo.
    choice /C SN /M "Continuar de todas formas?"
    if errorlevel 2 exit /b 1
)

REM ── Limpiar builds anteriores ──
if exist "%PROJECT_DIR%\build" rmdir /s /q "%PROJECT_DIR%\build"
if exist "%PROJECT_DIR%\dist" rmdir /s /q "%PROJECT_DIR%\dist"

REM ── Compilar con .spec ──
echo.
echo Compilando a .exe (usando flash_botty.spec)...
echo.
cd /d "%PROJECT_DIR%"

pyinstaller ^
    --clean ^
    --noconfirm ^
    "%SCRIPT_DIR%flash_botty.spec"

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] La compilacion fallo.
    echo   Revisa los errores arriba.
    pause
    exit /b 1
)

REM ── Resultado ──
echo.
echo ====================================
echo  COMPILACION EXITOSA
echo ====================================
echo.
if exist "%PROJECT_DIR%\dist\flash_botty.exe" (
    echo  Ejecutable: %PROJECT_DIR%\dist\flash_botty.exe
    for %%I in ("%PROJECT_DIR%\dist\flash_botty.exe") do echo  Tamano: %%~zI bytes
) else (
    echo  [ERROR] No se encontro el .exe generado
    pause
    exit /b 1
)
echo.
echo  Modos de uso:
echo    flash_botty.exe                    Auto-detecta la Pi
echo    flash_botty.exe --ip 10.0.0.2      USB Gadget / IP directa
echo    flash_botty.exe --ip 192.168.1.100 Red local
echo    flash_botty.exe --drive D:         Tarjeta SD
echo    flash_botty.exe --force            Forzar instalacion completa
echo    flash_botty.exe --help             Ayuda completa
echo.
echo  El .exe es autocontenido:
echo    - Botty completo dentro
echo    - Paramiko para SSH
echo    - No necesita Python en el PC
echo.
pause
