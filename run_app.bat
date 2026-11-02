@echo off
title Handwritten Answer Sheets Evaluator
echo ========================================================
echo  Starting Handwritten Answer Sheets Evaluator...
echo ========================================================
cd /d "%~dp0"
py -3.12 run_server.py
pause
