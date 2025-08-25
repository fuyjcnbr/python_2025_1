


main prints "lala"


docker build --no-cache --squash -t python_hw_1 -f docker/Dockerfile .


docker run -it python_hw_1 /bin/bash

docker run -v ~/PycharmProjects/python_2025_1:/src -it python_hw_1 /bin/bash



make -B tests

uv run make tests

uv lock

.venv

uv run python_2025_1/log_analyzer.py

uv run ruff check python_2025_1 --config pyproject.toml
