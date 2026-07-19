FROM python:3.11-slim

# 1. Установка системных зависимостей для Pillow, FontTools и графики
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    fonts-liberation \
    fonts-dejavu-core \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# 2. Настройка рабочей директории
WORKDIR /app

# 3. Клонирование репозитория напрямую в текущую папку (/app)
RUN git clone https://github.com/iTonyJah/Office-PowerPoint-MCP-Server .

# 4. Обновление pip и установка зависимостей Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. Создание папки для презентаций и настройка прав для безопасного пользователя
RUN useradd -m -u 1000 --no-log-init mcpuser && \
    mkdir -p /output && \
    chown -R mcpuser:mcpuser /app /output

# 7. Переключение контекста на не-root пользователя
USER mcpuser

# Открываем порт для сетевого транспорта наружу
EXPOSE 8000

# 7. Официальный сетевой запуск: uvicorn запускает объект mcp через фабрику http_app
CMD ["uvicorn", "ppt_mcp_server:mcp.http_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
