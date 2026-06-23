@echo off
call .venv\Scripts\activate.bat 2>nul || (
    echo Ambiente virtual nao encontrado. Execute install.bat primeiro.
    pause
    exit /b 1
)
python run.py
