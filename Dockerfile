# Usa uma imagem leve do Python
FROM python:3.9-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Define variáveis de ambiente para logs e Python otimizado
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Cria um usuário não-root para segurança
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Copia e instala dependências separadamente para cache eficiente
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação para o diretório de trabalho
COPY src ./src

# Altera a permissão para o usuário não-root
RUN chown -R appuser:appgroup /app

# Muda para o usuário não-root
USER appuser

# Expõe a porta usada pela aplicação
EXPOSE 8000

# Comando para rodar a aplicação FastStream
CMD ["faststream", "run", "--factory", "src.main:main", "--c=''"]