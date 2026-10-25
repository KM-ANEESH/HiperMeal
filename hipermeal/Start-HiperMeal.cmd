@echo off
cd /d "%~dp0"
echo HiperMeal dashboard: http://127.0.0.1:4180
echo Keep this window open. Press Ctrl+C to stop.
"%~dp0..\..\legal-studio\.venv\Scripts\python.exe" run_local.py
pause
