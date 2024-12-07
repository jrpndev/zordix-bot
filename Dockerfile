# Use uma imagem base oficial do Python
FROM python:3.9-slim

# Defina o diretório de trabalho no container
WORKDIR /app

# Copie os arquivos do projeto para o container
COPY . /app

# Atualize o gerenciador de pacotes e instale dependências do sistema (se necessário)
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Instale as dependências do Python
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Exponha a porta (altere para a porta do seu serviço)
EXPOSE 8000

# Comando para executar o script
CMD ["python", "-m", "api.index"]
