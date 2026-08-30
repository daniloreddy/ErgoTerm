#!/bin/bash
set -e
cd "$(dirname "$0")/.."

if [ -d "venv" ]; then
    VENV_DIR="venv"
elif [ -d ".venv" ]; then
    VENV_DIR=".venv"
else
    VENV_DIR="venv"
    echo "==> Creating virtual environment '$VENV_DIR'..."
    python3 -m venv "$VENV_DIR"
    CREATED=1
fi

if [ -f "$VENV_DIR/Scripts/activate" ]; then
    source "$VENV_DIR/Scripts/activate"
elif [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
else
    echo "[ERROR] venv activate script not found in '$VENV_DIR'."
    exit 1
fi

if [ -n "$CREATED" ]; then
    python -m pip install --upgrade pip
    pip install -r requirements.txt -r requirements.dev.txt
fi

echo "==> ruff format (check)"
ruff format --check ergo_api_client.py main.py test_api_client.py

echo "==> ruff check"
ruff check ergo_api_client.py main.py test_api_client.py

echo "==> mypy"
mypy ergo_api_client.py main.py

echo "==> pytest"
python -m pytest test_api_client.py -v
