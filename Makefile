.PHONY: tests

typing:
	mypy python_2025_1
tests:
# 	rm -f .pytest_cache
# 	rm -rf tests/isolated/__pycache__
	python -m pytest tests
