@echo off
REM Build script to run Streamlit app as a standalone application
cd /d %~dp0
call .venv\Scripts\activate
start "Streamlit NSE App" .venv\Scripts\python.exe -m streamlit run app2.py
