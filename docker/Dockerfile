FROM python:3.12-slim

RUN apt update && apt -y install build-essential

RUN python -m pip install uv

COPY uv.lock /uv.lock
COPY pyproject.toml /pyproject.toml

RUN uv sync --locked

RUN mkdir /src

WORKDIR /src
