FROM node:20-alpine

WORKDIR /app

# Устанавливаем open-websearch глобально
RUN npm install -g open-websearch@latest

# Открываем порт 3000 (стандартный для MCP HTTP transport)
EXPOSE 3000

# Запускаем в режиме HTTP (не stdio)
ENV MODE=http
ENV DEFAULT_SEARCH_ENGINE=duckduckgo
ENV ALLOWED_SEARCH_ENGINES=duckduckgo,bing,exa,brave

# Команда запуска (open-websearch в режиме HTTP слушает порт 3000)
CMD ["npx", "open-websearch@latest"]
