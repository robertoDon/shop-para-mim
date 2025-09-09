@echo off
echo 🚀 Iniciando Sistema Shop Pra Mim
echo ==============================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado. Por favor, instale o Python.
    pause
    exit /b 1
)

REM Instalar dependências
echo 📦 Verificando dependências...
pip install -r requirements.txt >nul 2>&1

echo ✅ Dependências verificadas!
echo.

REM Iniciar o servidor
echo 🌟 Sistema disponível em: http://localhost:5001
echo 📱 Funciona no celular, tablet e computador!
echo.
echo Para parar o sistema, pressione Ctrl+C
echo ==============================================
echo.

python app.py
pause