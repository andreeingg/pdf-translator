@echo off
chcp 65001 > nul
echo.
echo ========================================
echo   PDF Pipeline - Instalacion
echo ========================================
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado.
    echo Descargalo desde https://www.python.org/downloads/
    echo Asegurate de marcar "Add Python to PATH" al instalar.
    pause
    exit /b 1
)

echo [OK] Python detectado:
python --version
echo.

:: Instalar dependencias
echo Instalando dependencias...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Fallo la instalacion de dependencias.
    pause
    exit /b 1
)

echo.
echo [OK] Instalacion completada.
echo.
echo Uso:
echo   python pdf_pipeline.py to-md  archivo.pdf
echo   python pdf_pipeline.py to-pdf archivo_ES.md
echo.
pause
