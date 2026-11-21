@echo off
REM Windows: creates venv, installs deps, copies .env
python -m venv venv
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist .env copy .env.example .env
echo Done. Run:  venv\Scripts\activate  then  python main.py
