FROM python:3.10.5-alpine3.16

WORKDIR /clutter-bot

COPY pyproject.toml pyproject.toml

RUN apk add --no-cache git && pip install --no-cache-dir poetry && poetry install --no-dev

COPY ./clutter ./clutter

CMD [ "python3.10", "clutter" ]