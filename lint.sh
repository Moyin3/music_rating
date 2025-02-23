#!/bin/bash
# Run black for code formatting
black .

# Run mypy for type checking
mypy .

# Run flake8 for linting, ignoring long line errors (E501)
flake8 . --ignore=E501,W503