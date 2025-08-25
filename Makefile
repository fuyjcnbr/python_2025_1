.PHONY: tests

typing:
	uv run mypy python_2025_1 --config pyproject.toml
tests:
# 	rm -f .pytest_cache
# 	rm -rf tests/isolated/__pycache__
	uv run python -m pytest tests
lint:
	uv run ruff check python_2025_1 --config pyproject.toml
