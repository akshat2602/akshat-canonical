FROM python:3.10-slim-bullseye
WORKDIR /canonical-test-summer-break

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get upgrade -y

RUN pip install poetry

COPY poetry.lock pyproject.toml ./
RUN poetry install --no-interaction --no-ansi

COPY . .

EXPOSE 5000
