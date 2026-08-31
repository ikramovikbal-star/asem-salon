@echo off
cd /d "%~dp0"

if not exist venv (
    python -m venv venv
)

call venv\Scripts\activate

python -m pip install --upgrade pip
pip install -r requirements.txt

if not exist .env (
    copy .env.example .env >nul
    echo.
    echo Создан файл .env
    echo Откройте его и укажите ADMIN_PASSWORD.
    echo.
)

python app.py
pause
