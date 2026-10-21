@echo off
setlocal
cd /d "%~dp0"
set "PYTHON_CMD=py -3.14"
%PYTHON_CMD% -c "import sys; sys.exit(sys.version_info[:2] != (3, 14))" >nul 2>&1
if errorlevel 1 set "PYTHON_CMD=python"
%PYTHON_CMD% -c "import sys; sys.exit(sys.version_info[:2] != (3, 14))" >nul 2>&1
if errorlevel 1 goto missing
if not exist ".venv314\Scripts\python.exe" %PYTHON_CMD% -m venv .venv314
if errorlevel 1 goto failed
.venv314\Scripts\python.exe -c "import sys; sys.exit(sys.version_info[:2] != (3, 14))"
if errorlevel 1 goto wrongenv
.venv314\Scripts\python.exe -m pip install -r requirements-dev.txt
if errorlevel 1 goto failed
echo Setup finished. Run START_PROJECT.bat next.
exit /b 0
:missing
echo Install Python 3.14 and enable Add Python to PATH, then reopen your terminal.
exit /b 1
:wrongenv
echo .venv314 uses another Python version. Rename that folder and rerun setup.
exit /b 1
:failed
echo Setup failed. Read the error above. Check internet access and Python installation.
exit /b 1
