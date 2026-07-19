FROM python:3.11-slim

# 1. Установка системных зависимостей для Pillow, FontTools и графики
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-liberation \
    fonts-dejavu-core \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# 2. Настройка рабочей директории
WORKDIR /app

# Вместо одной точки копируем содержимое вложенной папки
COPY ./Office-PowerPoint-MCP-Server /app

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

# Официальный сетевой запуск: запускаем скрипт стандартно
CMD ["python", "ppt_mcp_server.py", "--transport", "http", "--port", "8000"]
