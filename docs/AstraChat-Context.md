# Контекст проекта AstraChat AI System

## О проекте

ВКР в магистратуре "Машинное обучение". Прикладная задача — написать MCP-сервер для генерации презентаций (.pptx) на платформе AstraChat.

**Репозитории:**
- Основной: https://github.com/NeKonnnn/Astra-Studio (держатель — научный руководитель)
- Рабочий (CPU-ноутбук): https://github.com/iTonyJah/AstraChat_AI_System/tree/local/cpu-setup

**Научный руководитель:** держатель основного проекта NeKonnnn/Astra-Studio.

---

## Аппаратная платформа

- Lenovo ThinkPad E14 Gen 5, AMD Ryzen (x86_64, AVX2/FMA3)
- ОЗУ: 16 ГБ + zram 8 ГБ (lzo-rle) + SWAP 17.7 ГБ
- ОС: Fedora (SELinux), Docker перенесён на /home
- Инференс: CPU-only (без GPU)

---

## Архитектура системы
```text
Пользователь → AstraChat Frontend (React, :3000)
↓
AstraChat Backend (FastAPI, :8000)
↓
MCP Agent Loop (backend/mcp/agent_loop.py)
↓
MCP PowerPoint Server (mcp-powerpoint, :8020→8000)
↓
python-pptx → создание PPTX
↓
LibreOffice headless → PPTX → PDF
↓
pypdfium2 → PDF → PNG
↓
Base64 PNG → Vision LLM (DashScope)
↓
Описание/проверка слайдов
```


---

## Этапы разработки

### Этап 1: Развёртывание инфраструктуры ✅

- Перевод архитектуры с CUDA на CPU-инференс
- Разрешение конфликтов SELinux
- Настройка сетевого alias `llm-service` для `llm-svc`
- Подключение локальной LLM: `qwen2.5-coder-7b-instruct-q5_k_m.gguf` (стабильна на CPU)
- Подключение облачной LLM: Alibaba Cloud DashScope через OpenAI-совместимый API
- Верификация MCP-протокола на эталонном сервере WebSearch

### Этап 2: MCP PowerPoint — базовые инструменты ✅

- Развёрнут MCP-сервер PowerPoint на базе `python-pptx`
- Модульная архитектура: 10 модулей в `tools/`
- 33 инструмента: создание, слайды, текст, таблицы, фигуры, диаграммы, дизайн, шаблоны, гиперссылки, коннекторы, мастер-слайды, переходы
- Автоматическое сохранение файлов в `./assets/pptx_output/`
- Health-check и мониторинг

### Этап 3: Vision Module — модуль видения слайдов ✅

**Цель:** LLM должна видеть, какие слайды получаются, и корректировать их.

**Что сделано:**

1. **`mcp-powerpoint/tools/vision_tools.py`** — новый модуль с 3 инструментами:
   - `export_presentation_pdf` — экспорт PPTX → PDF через LibreOffice
   - `get_presentation_preview` — рендер слайдов в PNG с base64 для vision-LLM
   - `get_slide_preview` — рендер одного конкретного слайда

2. **Dockerfile mcp-powerpoint** — добавлены:
   - `libreoffice-impress` (конвертация PPTX → PDF)
   - `pypdfium2` (конвертация PDF → PNG)
   - Шрифты: Liberation, DejaVu, Carlito (Calibri), Caladea (Cambria)

3. **`docker-compose.yml`** — добавлены:
   - Volume: `./assets/pptx_preview:/preview`
   - Env: `PPTX_OUTPUT_DIR=/output`, `PPTX_PREVIEW_DIR=/preview`

4. **`backend/mcp/result_parser.py`** — патч:
   - Извлечение `image_base64` из JSON-результатов MCP-инструментов
   - Удаление base64 из текста, чтобы не раздувать контекст LLM

5. **`backend/mcp/agent_loop.py`** — патч:
   - Сбор изображений из результатов MCP-инструментов (`parsed.images`)
   - Инжекция изображений как `user`-сообщение с `image_url` перед следующим вызовом LLM

6. **Middleware fix** в `ppt_mcp_server.py`:
   - Убран перехват GET `/mcp` (ломал SSE-стрим)
   - Добавлена нормализация `/mcp` → `/mcp/` (убирал 307 redirect)
   - Убран POST-bypass (возвращал не-JSON-RPC ответ)

**Результат:** Vision-модель `qwen3-vl-plus-2025-09-23` успешно описывает содержимое слайдов.

---

## Текущая структура MCP PowerPoint

```text
mcp-powerpoint/
├── ppt_mcp_server.py # главный сервер + middleware
├── Dockerfile # LibreOffice + pypdfium2 + шрифты
├── requirements.txt # python-pptx, mcp[cli]==1.8.0, Pillow, fonttools, fastapi, pypdfium2
├── pyproject.toml
└── tools/
├── presentation_tools.py # 7 инструментов
├── content_tools.py # 8 инструментов
├── structural_tools.py # 4 инструмента
├── professional_tools.py # 3 инструмента
├── template_tools.py # 6 инструментов
├── hyperlink_tools.py # 1 инструмент
├── chart_tools.py # 1 инструмент
├── connector_tools.py # 1 инструмент
├── master_tools.py # 1 инструмент
├── transition_tools.py # 1 инструмент
└── vision_tools.py # 3 инструмента (НОВЫЙ)
```


**Итого: 11 модулей, 36 инструментов** (33 базовых + 3 vision)

---

## Ключевые конфигурации

### `.env` (основные переменные)

```env
# DashScope (Alibaba Cloud) — облачная LLM
DEFAULT_LLM_PROVIDER=DASHSCOPE
LLM_PROVIDER_DASHSCOPE_KIND=openai-compat
LLM_PROVIDER_DASHSCOPE_BASE_URL=https://ws-jcvu5jctl27w30kh.ap-southeast-1.maas.aliyuncs.com/compatible-mode
LLM_PROVIDER_DASHSCOPE_ENABLED=true
LLM_PROVIDER_DASHSCOPE_STATIC_MODEL=qwen3-vl-plus-2025-09-23

# MCP PowerPoint
MCP_ENABLED=true
MCP_SERVER_PPTX_ENABLED=true
MCP_SERVER_PPTX_TRANSPORT=streamable-http
MCP_SERVER_PPTX_BASE_URL=http://mcp-powerpoint:8000   # БЕЗ /mcp
MCP_SERVER_PPTX_HEALTH_PATH=/health
MCP_SERVER_PPTX_HEALTH_CHECK_ENABLED=true
```

### docker-compose.yml (сервис mcp-powerpoint)
```yaml
mcp-powerpoint:
  build:
    context: ./mcp-powerpoint
    dockerfile: Dockerfile
  container_name: astrachat-mcp-powerpoint
  user: "root"
  ports:
    - "8020:8000"
  volumes:
    - ./assets/pptx_output:/output
    - ./assets/pptx_preview:/preview
  environment:
    - PPT_TEMPLATE_PATH=/app/templates
    - PYTHONUNBUFFERED=1
    - FASTMCP_TRANSPORT=http
    - FASTMCP_HOST=0.0.0.0
    - FASTMCP_PORT=8000
    - PPTX_OUTPUT_DIR=/output
    - PPTX_PREVIEW_DIR=/preview
```

### Команды диагностики
```bash
# Статус контейнеров
docker compose ps

# Логи MCP PowerPoint
docker compose logs --tail=100 mcp-powerpoint

# Логи backend (фильтр по MCP)
docker compose logs --tail=200 astrachat-backend | grep -iE "mcp|pptx|taskgroup"

# Проверка LibreOffice
docker compose exec mcp-powerpoint soffice --version

# Проверка pypdfium2
docker compose exec mcp-powerpoint python -c "import pypdfium2, PIL; print('ok')"

# Проверка импортов backend
docker compose exec -T astrachat-backend python -c "import backend.mcp.platform, backend.mcp.agent_loop, backend.mcp.result_parser; print('ok')"

# MCP handshake тест (из /tmp чтобы избежать shadowing)
docker compose exec -T -w /tmp -e PYTHONPATH= astrachat-backend python -c "
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
async def main():
    async with streamablehttp_client('http://mcp-powerpoint:8000/mcp/') as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = await s.list_tools()
            print('OK, tools:', len(tools.tools))
asyncio.run(main())
"

# Ручной тест рендера слайдов
docker compose exec -T mcp-powerpoint python -c "
from tools.vision_tools import render_presentation_preview_impl
import json
result = render_presentation_preview_impl('/output/mcp_powerpoint_tools.pptx', dpi=96, max_slides=2, include_base64=False)
print(json.dumps({'slides': result['slides_rendered']}, ensure_ascii=False))
"
```


# Что дальше
## Ближайшие задачи:
1. Автоматический preview — добавить в системный промпт инструкцию вызывать get_presentation_preview после save_presentation
2. Проверка в обычном чате — убедиться, что vision работает не только в режиме сравнения моделей
3. ImageContent — перейти от dict с image_base64 к нативному MCP ImageContent (чище по протоколу)
4. Оптимизация base64 — ограничить max_slides=2, dpi=72 для агентного цикла, чтобы не раздувать контекст
5. 6 недостающих инструментов — get_presentation_info, get_template_file_info, list_saved_presentations, delete_saved_presentation, optimize_slide_text, get_server_info (частично уже есть как get_server_info)

## Для ВКР
* Скриншоты: запрос → вызов инструмента → ответ vision-модели → PNG-скриншоты
* Схема архитектуры (см. выше)
* Сравнение с аналогами (MCP PowerPoint от GongRzhe — 39 инструментов, монолит)

## Полезные ссылки
* MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
* FastMCP документация: https://gofastmcp.com
* python-pptx: https://python-pptx.readthedocs.io
* pypdfium2: https://pypdfium2.readthedocs.io