@echo off
echo ============================================
echo  AlphaHome — Start Server Only
echo ============================================
cd /d %~dp0
call venv\Scripts\activate.bat
echo [1/1] Starting server...
echo.
echo Server chay tai: http://127.0.0.1:8000
echo.
python manage.py runserver
pause
