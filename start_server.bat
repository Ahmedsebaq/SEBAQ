@echo off
cd /d %~dp0
echo Starting PWA Quiz App Server...
echo Opening browser at: http://localhost:8000/index.html
echo Press Ctrl+C to stop the server
start "" "http://localhost:8000/index.html"
python -m http.server 8000
pause