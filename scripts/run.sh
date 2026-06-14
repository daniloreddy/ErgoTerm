#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR/.."

if [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "[ERROR] Virtual environment 'venv' not found."
    echo "Please create it first using: python3 -m venv venv"
    exit 1
fi

echo "Activating virtual environment and launching ErgoTerm..."
if command -v python &> /dev/null; then
    python main.py
elif command -v python3 &> /dev/null; then
    python3 main.py
else
    echo "[ERROR] Python interpreter not found in the environment."
    exit 1
fi
