#! /usr/bin/env bash
set -e

module=${1:-app/tests}

# Initialise DB
alembic upgrade head

# Add in some basic data
python app/initial_data.py

# Run the tests
pytest --cov=app --cov-report=term-missing ${module}
