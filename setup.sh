#!/usr/bin/env bash
# Linux / macOS: creates venv, installs deps, copies .env
set -e
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
echo "Done. Run:  source venv/bin/activate && python main.py"
