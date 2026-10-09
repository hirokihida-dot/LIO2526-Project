.PHONY: run test

run:
	env -u PYTHONPATH .venv/bin/python app/app.py

test:
	env -u PYTHONPATH .venv/bin/pytest -q
