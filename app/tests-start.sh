#! /usr/bin/env bash
set -e

python app/initial_data.py
pytest --cov=app --cov-report=term-missing app/tests
