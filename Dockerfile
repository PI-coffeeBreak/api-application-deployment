FROM python:3.12.9-alpine3.21

WORKDIR /app

RUN apk add --no-cache postgresql-dev

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--log-config", "logging_config.json"]
