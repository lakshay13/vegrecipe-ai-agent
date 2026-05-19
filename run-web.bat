@echo off
title VegRecipe AI Agent - Web App
cd /d "%~dp0"
echo Starting VegRecipe AI Agent Web App...
echo.
echo Opening browser at http://localhost:8501
start http://localhost:8501
"C:\Users\lakshays\AppData\Local\Programs\Python\Python312\Scripts\streamlit.exe" run app.py --server.port=8501 --server.headless=false
pause
