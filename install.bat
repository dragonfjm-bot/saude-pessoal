@echo off
echo.
echo  Saude Pessoal - Instalacao
echo  ==========================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado. Instale Python 3.11+ em https://python.org
    pause
    exit /b 1
)

echo  A criar ambiente virtual...
python -m venv .venv

echo  A ativar ambiente virtual...
call .venv\Scripts\activate.bat

echo  A instalar dependencias...
pip install -r requirements.txt --quiet

echo.
echo  Instalacao concluida!
echo  Para iniciar: python run.py
echo.
pause
