# 🔄 HOW-TO: Синхронизация ветки local/cpu-setup с upstream/main

Этот гайд описывает процесс обновления рабочей ветки с CPU-адаптациями из основного репозитория. Занимает 5-15 минут.

## 📋 Предварительные требования

- Убедиться, что все локальные изменения закоммичены
- Docker Desktop / Docker Engine запущен
- VS Code установлен (для визуального разрешения конфликтов)

---

## 🎯 Полный пайплайн обновления

### Шаг 1: Сохраняем WIP в рабочей ветке (если есть незакоммиченные изменения)

```bash
git switch local/cpu-setup
git add --all
git commit --message "chore: save WIP before syncing with upstream"
```

### Шаг 2: Обновляем main до upstream

```bash
git switch main
git fetch upstream
git merge upstream/main --no-edit
git push origin main
```

**Примечание:** Если Git пишет про локальные изменения:
```bash
git restore --staged --worktree -- .
```

Если `models/` появляется в Untracked (веса GGUF-моделей не коммитим!):
```bash
echo "models/" >> .git/info/exclude
```

### Шаг 3: Вливаем свежий main в рабочую ветку

```bash
git switch local/cpu-setup
git merge main --no-edit
```

### Шаг 4: Разрешаем конфликты (если появились)

Открываем проект в VS Code:
```bash
code .
```

**Типичные точки конфликтов:**

| Файл | Что делать |
|------|-----------|
| `backend/settings.json` | **Accept Current Change** (оставить путь к `qwen2.5-coder-7b-instruct-q5_k_m`) |
| `docker-compose.yml` | Удалить секции `deploy: resources: reservations: devices:` (CUDA) |
| `.env` | Закомментировать `CUDA_VISIBLE_DEVICES` |

**Важно:** Qwen3.5-9B вызывает Signal 11 (SEGV) на CPU — всегда оставляй стабильную модель `qwen2.5-coder-7b-instruct-q5_k_m`!

### Шаг 5: Фиксируем результат

```bash
git add --all
git commit --message "merge: sync with upstream main, keep stable CPU model settings"
git push origin local/cpu-setup
```

### Шаг 6: Проверяем работоспособность

```bash
docker compose config --quiet
docker compose up --detach --build
docker compose logs --follow llm-svc
```

---

## 📊 Быстрая шпаргалка (одной строкой)

```bash
git switch local/cpu-setup && git add --all && git commit --message "chore: pre-sync WIP"
git switch main && git fetch upstream && git merge upstream/main --no-edit && git push origin main
git switch local/cpu-setup && git merge main --no-edit
# ... решаем конфликты в VS Code ...
git add --all && git commit --message "merge: sync with upstream" && git push origin local/cpu-setup
docker compose config --quiet && docker compose up --detach --build
```

---

## 🎯 Стратегия обновлений

**Когда обновляться:**
1. ✅ Перед началом нового крупного этапа (например, перед разработкой MCP-сервера для `.pptx`)
2. ✅ По факту появления нужного функционала в upstream (новые UI-компоненты, RAG-улучшения)
3. ✅ Плановый синк раз в 1-2 недели (чтобы не накапливать гигантские merge-конфликты)

**Когда НЕ нужно:**
- ❌ Каждый день (каждый мерж требует ручного вмешательства)
- ❌ Перед дедлайном (если всё работает — не ломай)

---

## 🚀 Продвинутые лайфхаки

### Включить автоматическое запоминание решений конфликтов
```bash
git config --global rerere.enabled true
```

### Скрипт-постобработчик для удаления CUDA
Создать `scripts/fix_cuda.sh`:
```bash
#!/bin/bash
# Удаляет NVIDIA-директивы из docker-compose.yml после merge
sed --in-place '/deploy:/,/driver: nvidia/d' docker-compose.yml
```

Использование:
```bash
git merge main --no-edit && bash scripts/fix_cuda.sh
```

---

## 🐛 Troubleshooting

**Ошибка:** `error: Your local changes to the following files would be overwritten by merge`
```bash
git restore --staged --worktree -- .
```

**Ошибка:** `CONFLICT (content): Merge conflict in backend/settings.json`
```bash
code backend/settings.json
# Accept Current Change → Ctrl+S → git add backend/settings.json
```

**Docker не стартует после merge:**
```bash
docker compose config  # Проверить валидность YAML
docker compose down --volumes --remove-orphans
docker compose up --detach --build
```

---

**Время выполнения:** 5-15 минут  
**Частота:** Раз в 1-2 недели или по триггеру  
**Риск:** Низкий (всегда можно откатиться через `git reset --hard ORIG_HEAD`)

# upd. прячем /backend/settings.json в git
```bash
# Выполните один раз в терминале для активации режима скрытия файла
git update-index --assume-unchanged backend/settings.json
```
## 📋 Предварительные требования

- Убедиться, что все локальные изменения закоммичены
- Docker Desktop / Docker Engine запущен
- VS Code установлен (для визуального разрешения конфликтов)
- **Файл конфигурации скрыт от отслеживания Git** (чтобы локальные правки моделей и действия из фронтенда не попадали в статус):
  ```bash
  git update-index --assume-unchanged backend/settings.json
  ```

---

## 🎯 Полный пайплайн обновления

### Шаг 1: Сохраняем WIP в рабочей ветке (если есть незакоммиченные изменения)

```bash
git switch local/cpu-setup
git add --all
git commit --message "chore: save WIP before syncing with upstream"
```

### Шаг 2: Обновляем main до upstream

```bash
git switch main
git fetch upstream
git merge upstream/main --no-edit
git push origin main
```

### Шаг 3: Вливаем свежий main в рабочую ветку

Перед слиянием временно возвращаем видимость конфигурации, чтобы Git мог корректно применить новые глобальные ключи из upstream (если они появились):

```bash
git switch local/cpu-setup
git update-index --no-assume-unchanged backend/settings.json
git merge main --no-edit
```

### Шаг 4: Разрешаем конфликты (если появились)

Открываем проект в VS Code:
```bash
code .
```

**Типичные точки конфликтов:**

| Файл | Что делать |
|------|-----------|
| `backend/settings.json` | **Обычно мержится автоматически**. Если возник жесткий конфликт, выберите **Accept Current Change** (оставить стабильную CPU-модель) |
| `docker-compose.yml` | Удалить секции `deploy: resources: reservations: devices:` (CUDA) |
| `.env` | Закомментировать `CUDA_VISIBLE_DEVICES` |

### Шаг 5: Фиксируем результат и возвращаем скрытие файла

```bash
git add --all
git commit --message "merge: sync with upstream main, keep stable CPU model settings"
git update-index --assume-unchanged backend/settings.json
git push origin local/cpu-setup
```

### Шаг 6: Проверяем работоспособность

```bash
docker compose config --quiet
docker compose up --detach --build
docker compose logs --follow llm-svc
```

---

## 📊 Быстрая шпаргалка (одной строкой)

```bash
git switch local/cpu-setup && git add --all && git commit --message "chore: pre-sync WIP"
git switch main && git fetch upstream && git merge upstream/main --no-edit && git push origin main
git switch local/cpu-setup && git update-index --no-assume-unchanged backend/settings.json && git merge main --no-edit
# ... решаем конфликты в VS Code ...
git add --all && git commit --message "merge: sync with upstream" && git update-index --assume-unchanged backend/settings.json && git push origin local/cpu-setup
docker compose config --quiet && docker compose up --detach --build
```
