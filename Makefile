lint:
	ruff check src tests --no-fix

lint-fix:
	ruff check src tests --fix


typecheck:
	mypy src tests
