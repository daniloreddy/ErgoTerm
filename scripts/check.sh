#!/bin/bash
set -e
cd "$(dirname "$0")/.."

echo "==> ruff format"
./venv/bin/ruff format ergo_api_client.py main.py test_api_client.py

echo "==> ruff check"
./venv/bin/ruff check ergo_api_client.py main.py test_api_client.py

echo "==> mypy"
./venv/bin/mypy ergo_api_client.py main.py

echo "==> pytest"
./venv/bin/python -m pytest test_api_client.py -v
