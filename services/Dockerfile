FROM python:3.11-slim

LABEL author=${AUTHOR}

WORKDIR /app

# Копируем ВСЁ из services/ в контейнер
COPY . .

RUN pip3 install -r requirements.txt

WORKDIR /app/ml_service

EXPOSE ${APP_PORT}

CMD uvicorn main:app --reload --port ${APP_PORT} --host 0.0.0.0