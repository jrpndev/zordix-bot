#!/bin/bash

# Instala Python (Ubuntu/Debian)
echo "Atualizando o sistema e instalando Python..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip

# Verifica se o Python foi instalado corretamente
if ! command -v python3 &>/dev/null; then
    echo "Erro: Python não foi instalado corretamente."
    exit 1
fi

# Cria e ativa um ambiente virtual
echo "Criando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

# Instala as dependências do requirements.txt
echo "Instalando dependências do requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# Executa o script index.py
echo "Executando o script index.py..."
python -m api.index
