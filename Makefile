build: requirements.txt
	pip install -r requirements.txt

run: runner.py build
	python runner.py $(CMD)

test: test_runner.py build
	pytest -s -v test_runner.py

.PHONY: build run test