@echo off
REM Build dist\dYKcrpytor.exe (PyInstaller).
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (set "PY=py") else (set "PY=python")

if not exist ".venv-win\" ("%PY%" -m venv .venv-win)
call ".venv-win\Scripts\activate.bat"

python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller pillow
python scripts\build_icons.py
pyinstaller --noconfirm --clean dYKcrpytor.spec

if exist "dist\dYKcrpytor.exe" (
  echo Done: dist\dYKcrpytor.exe
  explorer dist
) else (
  exit /b 1
)

pause
