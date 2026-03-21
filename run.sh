#!/bin/bash

# Navigate to the script's directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Check for the activation script in common locations
if [ -f "venv/Scripts/activate" ]; then
    # Windows-style venv (used in Git Bash)
    source venv/Scripts/activate
elif [ -f "venv/bin/activate" ]; then
    # Unix-style venv (used in Linux/macOS)
    source venv/bin/activate
else
    echo "[ERROR] Virtual environment 'venv' not found."
    echo "Please create it first using: python3 -m venv venv"
    exit 1
fi

echo "Activating virtual environment and launching ErgoTerm..."
# Try running with python, fallback to python3 if not found
if command -v python &> /dev/null; then
    python main.py
elif command -v python3 &> /dev/null; then
    python3 main.py
else
    echo "[ERROR] Python interpreter not found in the environment."
    exit 1
fi
