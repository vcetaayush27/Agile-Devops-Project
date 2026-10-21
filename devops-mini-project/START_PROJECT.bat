@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv314\Scripts\python.exe" call SETUP_WINDOWS.bat
if errorlevel 1 goto failed
.venv314\Scripts\python.exe -c "import sys; sys.exit(sys.version_info[:2] != (3, 14))"
if errorlevel 1 goto failed
.venv314\Scripts\python.exe run.py
if errorlevel 1 goto failed
exit /b 0
:failed
echo Run SETUP_WINDOWS.bat from a terminal to inspect the installation error.
pause
exit /b 1
