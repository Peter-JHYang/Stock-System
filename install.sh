#!/usr/bin/env bash
set -euo pipefail

echo "Creating virtualenv .venv and installing package in editable mode..."
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .

echo "Installation complete. Activate with: source .venv/bin/activate"
