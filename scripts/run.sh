#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR/.."

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
    pip install -r requirements.txt
fi

echo "Launching ErgoTerm..."
exec python main.py
