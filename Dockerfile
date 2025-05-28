FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN touch README.md

RUN poetry config virtualenvs.create false \
    && poetry install --only=main --no-interaction --no-ansi --no-root


RUN useradd -m myuser
USER myuser

COPY src .
COPY entrypoint.sh /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
