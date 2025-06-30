@echo off
REM Build overlay_text.exe met Avans.svg als resource
pyinstaller --onefile --windowed --add-data "Avans.svg;." overlay_text.py
pause 