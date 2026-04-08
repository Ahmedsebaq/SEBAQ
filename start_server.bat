@echo off
echo Starting PWA Quiz App Server...
echo Open your browser to: http://localhost:8000/اسئلة.html
echo Press Ctrl+C to stop the server
python -m http.server 8000
pause