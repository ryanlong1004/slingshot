# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src

ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["python", "-m", "slingshot.api_main"]
