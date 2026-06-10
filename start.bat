@echo off
cd /d "%~dp0whisper-writer"
call venv\Scripts\activate
python run.py
