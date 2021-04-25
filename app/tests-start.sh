#! /usr/bin/env bash
set -e

module=${1:-app/tests}

# Add in some basic data
TEST_DB=true python app/initial_data.py

# Run the tests
pytest --cov=app --cov-report=term-missing ${module}
