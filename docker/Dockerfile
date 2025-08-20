FROM python:3.12-slim

RUN apt update && apt -y install build-essential

RUN python -m pip install mypy uv pytest "numpy>=2.3"

RUN mkdir /src

WORKDIR /src
