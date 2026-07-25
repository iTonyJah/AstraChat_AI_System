FROM python:3.11-slim

# 1. Установка системных зависимостей для графики и шрифтов
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-liberation \
    fonts-dejavu-core \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Теперь это сработает идеально, так как файлы лежат прямо в корне контекста!
COPY . /app

# Обновление pip и установка зависимостей
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Настройка папки для презентаций
RUN mkdir -p /output

EXPOSE 8000

# Чистый запуск без буферизации логов
CMD ["python", "-u", "ppt_mcp_server.py"]
