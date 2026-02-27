install:
	pip install -r requirements.txt

test:
	pytest tests/

lint:
	flake8 ecopulse_ai

format:
	black ecopulse_ai tests

run:
	python -m ecopulse_ai.main
