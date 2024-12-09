FROM python:3.12.4

RUN apt-get update && apt-get install -y curl
# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы в рабочую директорию
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt --no-deps

COPY . .