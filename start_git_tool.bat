@echo off
cd /d "%~dp0"
python "git_tool.py"
if errorlevel 1 (
  echo.
  echo Failed to start git_tool.py.
)
pause
