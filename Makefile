# Makefile

SHELL = /usr/bin/bash

test:
	pytest -v

clean:
	find . -type f -name "*.pyc" -exec rm {} \;
	find . -type f -name "*.swp" -exec rm {} \;

all: clean test
	python -m black . -l79
	coverage run -m pytest
	coverage report -m 
	-flake8

