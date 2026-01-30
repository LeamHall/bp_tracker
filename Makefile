# Makefile

SHELL = /usr/bin/bash

.PHONY: test clean all help

test:
	python -m unittest discover -s test -p "test_*.py"

clean:
	find . -type f -name "*.pyc" -exec rm {} \;
	find . -type f -name "*.swp" -exec rm {} \;

all: clean test
	python -m black . -l79
	coverage run -m unittest discover -s test -p "test_*.py"
	coverage report -m
	-flake8

help:
	@echo "Available targets:"
	@echo "  test   - Run tests with unittest"
	@echo "  clean  - Remove generated files (.pyc, .swp)"
	@echo "  all    - Run clean, test, format with black, coverage, and flake8"
	@echo "  help   - Show this help message"
