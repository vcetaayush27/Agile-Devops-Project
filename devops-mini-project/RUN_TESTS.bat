@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv314\Scripts\python.exe" call SETUP_WINDOWS.bat
if errorlevel 1 goto failed
.venv314\Scripts\python.exe -c "import sys; sys.exit(sys.version_info[:2] != (3, 14))"
if errorlevel 1 goto failed
.venv314\Scripts\python.exe -m pytest -q
if errorlevel 1 goto failed
echo All tests passed.
pause
exit /b 0
:failed
echo Tests or setup failed. Read the message above.
pause
exit /b 1
