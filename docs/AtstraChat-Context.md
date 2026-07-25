# Контекст проекта AstraChat AI System

## О проекте
Моя ВКР в магистратуре "Машинное обучение". Прикладная задача — написать MCP-сервер для генерации презентаций (.pptx) на платформе AstraChat.

Репозитории:
- Основной: https://github.com/iTonyJah/AstraChat_AI_System
- Рабочий (CPU-ноутбук): https://github.com/iTonyJah/AstraChat_AI_System/tree/local/cpu-setup

## Что уже сделано (этап развёртывания)

### 1. Аппаратная платформа
- Ноутбук Lenovo ThinkPad E14 Gen 5, AMD Ryzen (x86_64, AVX2/FMA3)
- ОЗУ: 16 ГБ + zram 8 ГБ (lzo-rle) + SWAP 17.7 ГБ
- Docker перенесён на /home (корневой раздел был забит)

### 2. Развёртывание и адаптация
- Перевёл всю архитектуру с CUDA на CPU-инференс (убрал NVIDIA-директивы из docker-compose.yml)
- Разрешил конфликты SELinux (контекст svirt_sandbox_file_t)
- Настроил сетевой alias llm-service для llm-svc в astrachat-network
- Сбросил битые сессионные лимиты в MongoDB через mongosh

### 3. Интеграция LLM
Скачаны и проверены две модели GGUF:
- **Qwen3.5-9B-q4_k_m.gguf** (5.63 ГБ) — ❌ нестабильна на CPU, вызывает Signal 11 (SEGV) в libggml-cpu.so
- **qwen2.5-coder-7b-instruct-q5_k_m.gguf** (5.44 ГБ) — ✅ стабильна, генерирует Markdown на русском

Конфигурация:
- Путь: /app/models/llm/qwen2.5-coder-7b-instruct-q5_k_m.gguf
- Порт llm-service: 8002 (внутри контейнера 8000)
- Backend: llama.cpp, CPU-инференс (gpu_layers: 0)
- Контекст: 2048 токенов

### 4. Интеграция облачной LLM (Alibaba Cloud DashScope)
Подключена внешняя модель **Qwen-Flash** через OpenAI-совместимый API:

**Настройки `.env`:**
```env
DASHSCOPE_API_KEY=sk-ws-...
LLM_PROVIDER_DASHSCOPE_KIND=openai-compat
LLM_PROVIDER_DASHSCOPE_BASE_URL=https://ws-jcvu5jctl27w30kh.ap-southeast-1.maas.aliyuncs.com/compatible-mode
LLM_PROVIDER_DASHSCOPE_API_KEY_ENV=DASHSCOPE_API_KEY
LLM_PROVIDER_DASHSCOPE_ENABLED=true
LLM_PROVIDER_DASHSCOPE_STATIC_MODEL=qwen-flash
DEFAULT_LLM_PROVIDER=DASHSCOPE
```

### 5. MCP веб-поиска (эталонный пример)
Добавил в docker-compose.yml контейнер mcp-websearch:
```yaml
mcp-websearch:
  build:
    context: ./mcp-websearch
    dockerfile: Dockerfile
  ports:
    - "8013:3000"
  environment:
    - MODE=http
    - DEFAULT_SEARCH_ENGINE=duckduckgo
```

## Текущий статус проекта

### ✅ Архитектура полностью работоспособна
- 12 микросервисов запущены
- Локальная LLM (`qwen2.5-coder-7b`) активна в ОЗУ
- Облачная LLM (`Qwen-Flash`) подключена как провайдер по умолчанию
- MCP-протокол верифицирован на эталонном сервере WebSearch
- Веб-интерфейс доступен на порту `3000`

### ✅ Инфраструктура готова к разработке MCP-PPTX
- Агентная архитектура (`MCPAgent`) протестирована
- Механизм подключения внешних инструментов через backend-конфигурацию отлажен
- Понятен паттерн интеграции MCP-серверов в AstraChat

# Создаём тег для этапа 2
git tag -a v0.2-mcp-powerpoint -m "Этап 2: MCP-сервер PowerPoint интегрирован

Результаты:
✓ MCP-сервер PowerPoint развёрнут и доступен в UI
✓ Автоматическое сохранение файлов на хост-машину
✓ Нормализация путей (решена проблема дублирования директорий)
✓ Настроен health-check и мониторинг

Следующие шаги:
- Стабилизация выбора инструментов агентом
- PDF-экспорт через LibreOffice
- Темы и шаблоны оформления
- Интеграция генерации изображений"

# Отправляем тег
git push origin v0.2-mcp-powerpoint

### Версионирование и контроль изменений

Проект использует Git-flow стратегию с семантическими тегами для фиксации 
этапов разработки ВКР:

| Версия | Дата | Описание |
|--------|------|----------|
| v0.1-mcp-websearch | 2026-07-XX | Этап 1: интеграция MCP WebSearch |
| **v0.2-mcp-powerpoint** | **2026-07-25** | **Этап 2: MCP PowerPoint (текущий)** |
| v0.3-pdf-export | TBD | Этап 3: PDF-экспорт и темы |
| v1.0-final | TBD | Финальная версия для защиты |

Каждый тег сопровождается подробным commit message с техническими деталями, 
что обеспечивает:
- Полную воспроизводимость окружения
- Возможность отката к любой точке разработки
- Документирование принятых архитектурных решений
- Прозрачность для научного руководителя