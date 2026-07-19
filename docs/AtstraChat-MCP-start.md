Структура
```text
AstraChat_AI_System/
├── mcp-pptx/                    # ← НОВАЯ ДИРЕКТОРИЯ
│   ├── Dockerfile
│   └── .dockerignore
├── docker-compose.yml           # ← Будем модифицировать
├── mcp-websearch/               # ← Уже существует (эталон)
└── ...
```

Dockerfile
```dockerfile
FROM python:3.11-slim

# Системные зависимости для Pillow и FontTools (генерация изображений и расчет шрифтов)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    fonts-liberation \
    fonts-dejavu-core \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Клонируем конкретный стабильный релиз вместо ветки main
RUN git clone --depth 1 --branch v2.0.7 https://github.com/GongRzhe/Office-PowerPoint-MCP-Server.git

# Устанавливаем зависимости через pyproject.toml
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Директория для сохранения готовых презентаций
RUN mkdir -p /output && chmod 777 /output

# Создание безопасного окружения
RUN useradd -m -u 1000 --no-log-init mcpuser && \
    mkdir -p /app /output && \
    chown -R mcpuser:mcpuser /app /output

# Смена контекста на не-root пользователя
USER mcpuser

EXPOSE 8000

# Запуск в режиме HTTP-транспорта для связи с бэкендом
CMD ["python", "ppt_mcp_server.py", "--transport", "http", "--port", "8000", "--host", "0.0.0.0"]
```

mcp-pptx/.dockerignore
```bash
.git
__pycache__
*.pyc
.env
output/
```

Скопируйте этот блок в ваш docker-compose.yml:
```yaml
  mcp-pptx:
    build:
      context: ./mcp-pptx
      dockerfile: Dockerfile
    container_name: mcp-pptx-service
    ports:
      - "8020:8000"
    volumes:
      - ./assets/pptx_output:/output
    restart: unless-stopped
    environment:
      - PPT_TEMPLATE_PATH=/app/templates
      - PYTHONUNBUFFERED=1 # Добавлено: чтобы логи контейнера не буферизировались и были видны сразу
    networks:
      - astrachat-network
```


```bash
# 1. Пересобираем и запускаем новый контейнер
docker compose up -d --build mcp-pptx

# 2. Проверяем что контейнер жив
docker ps | grep mcp-pptx
docker logs mcp-pptx --tail 50

# 3. Перезапускаем backend (чтобы он перечитал config.yml)
docker compose restart astrachat-backend

# 4. Проверяем логи backend — должно появиться:
docker logs astrachat-backend --tail 100 | grep "MCP registry"
# Ожидаем: "MCP registry loaded: enabled=True servers=['atlassian', 'websearch', 'pptx']"

# 5. Открываем AstraChat UI → Настройки → MCP
# Должен появиться сервер "Генерация презентаций (.pptx)" с 34 инструментами

# 6. Тестовый запрос через чат:
# "Создай новую презентацию с помощью MCP-инструмента pptx"
```