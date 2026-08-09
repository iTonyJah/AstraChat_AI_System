FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Системные зависимости: LibreOffice, шрифты, графика
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice-impress \
    fontconfig \
    fonts-liberation \
    fonts-dejavu \
    fonts-crosextra-carlito \
    fonts-crosextra-caladea \
    libgl1 \
    && rm -rf /var/lib/apt/lists/* \
    && fc-cache -f

WORKDIR /app

# Копируем проект
COPY . /app

# Python-зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Папки для презентаций и предпросмотров
RUN mkdir -p /output /preview

EXPOSE 8000

CMD ["python", "-u", "ppt_mcp_server.py"]