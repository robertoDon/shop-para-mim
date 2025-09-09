#!/bin/bash

echo "🚀 Iniciando Sistema Shop Pra Mim"
echo "=============================================="
echo ""

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale o Python 3."
    exit 1
fi

# Instalar dependências se necessário
echo "📦 Verificando dependências..."
pip3 install -r requirements.txt > /dev/null 2>&1

echo "✅ Dependências verificadas!"
echo ""

# Iniciar o servidor
echo "🌟 Sistema disponível em: http://localhost:5001"
echo "📱 Funciona no celular, tablet e computador!"
echo ""
echo "Para parar o sistema, pressione Ctrl+C"
echo "=============================================="
echo ""

python3 app.py