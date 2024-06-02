lint:
	ruff check src tests --no-fix

lint-fix:
	ruff check src tests --fix


typecheck:
	mypy src tests

test:
	pytest -svv

test-cov:
	coverage run -m pytest
	coverage report -m