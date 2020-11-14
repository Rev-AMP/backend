#!/usr/bin/env bash

set -ex

mypy app
black app --check
isort --recursive --check-only app
flake8
