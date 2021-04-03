#! /usr/bin/env bash
set -e

module=${1:-app/tests}

python app/initial_data.py
pytest --cov=app --cov-report=term-missing ${module}
