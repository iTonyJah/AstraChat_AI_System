# Карта репозитория Astra Studio

## 📁 Обзор архитектуры

Это **микросервисная AI-платформа** с агентной архитектурой для корпоративного использования. Состоит из фронтенда (React/TypeScript), бэкенда (Python/FastAPI) и набора специализированных сервисов.

---

## 🗂️ Структура репозитория

### **1. `/frontend`** — Веб-интерфейс (React + TypeScript)
```
frontend/
├── src/
│   ├── pages/           # Страницы приложения
│   │   ├── ChatPage.tsx              # Чат с AI
│   │   ├── UnifiedChatPage.tsx       # Унифицированный чат (основной)
│   │   ├── DocumentsPage.tsx         # Управление документами
│   │   ├── KnowledgeBasePage.tsx     # База знаний
│   │   ├── HistoryPage.tsx           # История диалогов
│   │   ├── ProjectPage.tsx           # Проекты
│   │   ├── PromptGalleryPage.tsx     # Галерея промтов
│   │   ├── SettingsPage.tsx          # Настройки
│   │   ├── VoicePage.tsx             # Голосовое взаимодействие
│   │   ├── TranscriptionPage.tsx     # Транскрибация
│   │   ├── CreationsPage.tsx         # Генерация изображений
│   │   ├── LoginPage.tsx             # Авторизация
│   │   └── ProfilePage.tsx           # Профиль
│   │
│   ├── components/      # UI компоненты
│   │   ├── AgentConstructorPanel.tsx # Конструктор агентов
│   │   ├── AgentSelector.tsx         # Выбор агента
│   │   ├── ChatInputBar.tsx          # Поле ввода чата
│   │   ├── ChatGearAgentsPanel.tsx   # Панель агентов
│   │   ├── ChatGearMcpPanel.tsx      # MCP интеграция
│   │   ├── DocumentSearchPanel.tsx   # Поиск документов
│   │   └── ... (50+ компонентов)
│   │
│   ├── hooks/           # React хуки
│   │   ├── useFollowUpSuggestions.ts
│   │   ├── useChatContextUsage.ts
│   │   ├── useImageCreations.ts
│   │   └── ...
│   │
│   ├── mcp/             # MCP (Model Context Protocol)
│   │   ├── plugins/     # Плагины MCP
│   │   ├── hooks/       # MCP хуки
│   │   └── utils/       # Утилиты MCP
│   │
│   ├── utils/           # Утилиты фронтенда
│   ├── config/          # Конфигурация
│   ├── constants/       # Константы
│   └── contexts/        # React контексты
│
├── public/              # Статические файлы
└── package.json         # Зависимости npm
```

**За что отвечает:** Весь пользовательский интерфейс, взаимодействие с API бэкенда, WebSocket соединения для realtime-обновлений.

---

### **2. `/backend`** — Основной бэкенд (Python/FastAPI)
```
backend/
├── agents/              # AI агенты на LangGraph
│   ├── base_agent.py              # Базовый класс агента
│   ├── langgraph_orchestrator.py  # Оркестратор агентов (79KB)
│   ├── document_agent.py          # Работа с документами
│   ├── mcp_agent.py               # Интеграция с MCP
│   ├── prompt_enhancement_agent.py # Улучшение промтов
│   └── summarization_agent.py     # Суммаризация текстов
│
├── orchestrator/        # Оркестрация запросов
│   └── __init__.py      # Логика маршрутизации между агентами
│
├── routes/              # API эндпоинты (284KB всего)
│   ├── chat.py          # Чат (50KB)
│   ├── documents.py     # Документы (55KB)
│   ├── rag.py           # RAG запросы (30KB)
│   ├── agents.py        # Управление агентами
│   ├── mcp.py           # MCP инструменты
│   ├── image_generation.py # Генерация изображений
│   ├── transcription.py # Транскрибация
│   ├── voice.py         # Голосовые функции
│   ├── models.py        # Управление моделями
│   ├── memory.py        # Память/история
│   └── ... (еще 10 файлов)
│
├── mcp/                 # Model Context Protocol
│   ├── plugins/         # Плагины (Atlassian, WebSearch)
│   ├── transports/      # Транспортные уровни
│   ├── credentials/     # Управление учетными данными
│   ├── agent_loop.py    # Цикл агента
│   ├── platform.py      # Платформенная логика
│   └── session_manager.py # Менеджер сессий
│
├── tools/               # Инструменты для агентов
│   ├── agent_tools.py
│   ├── prompt_tools.py
│   ├── summarization_tools.py
│   └── system_tools.py
│
├── database/            # Работа с БД
│   ├── mongodb/         # MongoDB (диалоги, история)
│   ├── postgresql/      # PostgreSQL + pgvector (RAG)
│   ├── minio/           # MinIO (файловое хранилище)
│   ├── init_db.py       # Инициализация БД
│   └── memory_service.py # Сервис памяти
│
├── llm_providers/       # Провайдеры LLM
│   ├── cloud_provider.py # Облачные модели
│   └── local_provider.py # Локальные модели
│
├── rag_query/           # RAG логика
│   ├── strategies/      # Стратегии поиска
│   └── chunking/        # Методы чанкования
│
├── realtime/            # WebSocket соединения
│
├── auth/                # Аутентификация и авторизация
│
├── services/            # Бизнес-логика сервисов
│
├── settings/            # Настройки системы
│   ├── logging/         # Логирование
│   └── cef_logger/      # CEF логгер
│
├── utils/               # Общие утилиты
│
├── uploads/             # Загруженные файлы
│   ├── presentations/   # Презентации
│   └── presentation_templates/ # Шаблоны
│
└── silero_models/       # Модели Silero (TTS)
    ├── ru/              # Русские голоса
    └── en/              # Английские голоса
```

**За что отвечает:** Основная бизнес-логика, оркестрация AI-агентов, обработка запросов к LLM, управление RAG, интеграция с внешними сервисами через MCP.

---

### **3. Микросервисы (SVC-*)**

#### **`/SVC-RAG`** — RAG сервис
```
SVC-RAG/
├── app/
│   ├── api/endpoints/
│   │   ├── search.py        # Поиск по векторам
│   │   ├── kb.py            # База знаний
│   │   ├── project_rag.py   # Проектный RAG
│   │   ├── memory_rag.py    # Memory RAG
│   │   ├── documents.py     # Документы
│   │   └── health.py        # Health check
│   ├── services/            # Бизнес-логика RAG
│   ├── database/            # Векторная БД
│   └── clients/             # Клиенты внешних сервисов
└── config/config.yml        # Конфигурация
```
**За что отвечает:** Индексация документов, векторный поиск, гибридный поиск (векторный + лексический), иерархия чанков.

---

#### **`/SVC-RAG-MODELS`** — Модели для RAG
```
SVC-RAG-MODELS/
├── app/
│   ├── services/            # Сервисы эмбеддингов
│   └── dependencies/        # Зависимости моделей
└── config/config.yml
```
**За что отвечает:** Эмбеддинги и реранкинг моделей для RAG.

---

#### **`/SVC-SPEECH-RECG`** — Распознавание речи (STT)
```
SVC-SPEECH-RECG/
├── app/
│   ├── api/endpoints/
│   │   └── whisperx.py      # WhisperX транскрибация
│   ├── services/            # Сервисы распознавания
│   └── utils/               # Утилиты
└── config/config.yml
```
**За что отвечает:** Транскрибация аудио в текст через WhisperX.

---

#### **`/SVC-SPEECH-SYNT`** — Синтез речи (TTS)
```
SVC-SPEECH-SYNT/
├── app/
│   ├── api/endpoints/
│   │   └── tts.py           # TTS синтез
│   ├── dependencies/
│   │   └── silero_handler.py # Обработчик Silero
│   └── services/            # Сервисы синтеза
└── config/config.yml
```
**За что отвечает:** Синтез речи из текста (Silero TTS с несколькими голосами).

---

#### **`/SVC-SPEECH-DIAR`** — Диаризация спикеров
```
SVC-SPEECH-DIAR/
├── app/
│   ├── api/endpoints/
│   │   └── diarization.py   # Разделение спикеров
│   └── services/            # Сервисы диаризации
└── config/config.yml
```
**За что отвечает:** Автоматическое разделение речи по говорящим.

---

#### **`/SVC-OCR`** — Оптическое распознавание символов
```
SVC-OCR/
├── app/
│   ├── api/endpoints/
│   │   └── ocr.py           # OCR обработка
│   └── services/            # Сервисы OCR
└── config/config.yml
```
**За что отвечает:** Извлечение текста из изображений и сканов.

---

### **4. `/llm-svc`** — LLM инференс сервис
```
llm-svc/
├── app/
│   ├── api/                 # API эндпоинты
│   ├── services/            # Сервисы инференса
│   ├── models/              # Модели данных
│   ├── middleware/          # Middleware
│   └── utils/               # Утилиты
├── models/                  # Файлы моделей
└── config/config.yml
```
**За что отвечает:** Единый сервис для инференса больших языковых моделей (локальных и облачных).

---

### **5. `/mcp-powerpoint`** — MCP сервер для PowerPoint
```
mcp-powerpoint/
├── tools/                   # MCP инструменты
├── utils/                   # Утилиты
├── ppt_mcp_server.py        # Сервер MCP
└── setup_mcp.py             # Настройка
```
**За что отвечает:** Интеграция с PowerPoint через MCP (создание, редактирование презентаций).

---

### **6. `/mcp-websearch`** — MCP веб-поиск
```
mcp-websearch/
└── Dockerfile
```
**За что отвечает:** Поиск в интернете через MCP протокол.

---

### **7. `/surya_models`** — Модели Surya OCR
```
surya_models/
├── text_detection/          # Детекция текста
└── text_recognition/        # Распознавание текста
```
**За что отвечает:** Модели для OCR (Surya).

---

### **8. `/assets`** — Статические ресурсы
- Логотипы, изображения для документации

---

### **9. `/docs`** — Документация
- Дополнительная документация проекта

---

## 🔧 Конфигурационные файлы

| Файл | Описание |
|------|----------|
| `docker-compose.yml` | Основная конфигурация Docker |
| `docker-compose-backend.yml` | Бэкенд сервисы |
| `docker-compose-frontend.yml` | Фронтенд |
| `docker-compose-llm-svc.yml` | LLM сервис |
| `docker-compose.gpu.yml` | GPU конфигурация |
| `MAIN.env`, `localhost.env`, `env.main` | Переменные окружения |
| `requirements.txt` | Python зависимости |
| `frontend/package.json` | npm зависимости |

---

## 🏗️ Архитектурные компоненты

### **Агентная архитектура (LangGraph)**
- **Агент-оркестратор** — координирует работу специализированных агентов
- **DocumentAgent** — работа с документами
- **MCPAgent** — внешние интеграции
- **PromptEnhancementAgent** — улучшение промтов
- **SummarizationAgent** — суммаризация

### **RAG система**
**Стратегии поиска:**
- Векторный
- Лексический
- Гибридный
- Графовый

**Методы чанкования:**
- Иерархическое
- Фиксированное
- По разметке
- Семантическое

### **Хранение данных**
- **MongoDB** — диалоги, история
- **PostgreSQL + pgvector** — векторная БД для RAG
- **MinIO** — файловое хранилище

---

## 📊 Ключевые файлы

| Компонент | Файл | Размер | Назначение |
|-----------|------|--------|------------|
| Оркестратор | `backend/agents/langgraph_orchestrator.py` | 79KB | Координация агентов |
| Чат роуты | `backend/routes/chat.py` | 51KB | Обработка чата |
| Документы роуты | `backend/routes/documents.py` | 55KB | Управление документами |
| Unified Chat | `frontend/src/pages/UnifiedChatPage.tsx` | 225KB | Главный компонент чата |
| Prompt Gallery | `frontend/src/pages/PromptGalleryPage.tsx` | 93KB | Галерея промтов |
| Settings | `frontend/src/pages/SettingsPage.tsx` | 63KB | Настройки приложения |

---

## 🚀 Основные технологии

- **Backend:** Python, FastAPI, LangGraph
- **Frontend:** React, TypeScript, Material-UI
- **ML:** WhisperX, Silero TTS, Surya OCR
- **Базы данных:** MongoDB, PostgreSQL + pgvector, MinIO
- **Инфраструктура:** Docker, Docker Compose
- **Протоколы:** WebSocket, MCP (Model Context Protocol)

---

Эта карта охватывает всю структуру репозитория и объясняет назначение каждого компонента. Если нужны детали по конкретному модулю — дайте знать!
