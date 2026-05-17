@echo off
echo ============================================
echo  AlphaHome — Setup Database
echo ============================================
cd /d %~dp0
call venv\Scripts\activate.bat
echo [1/3] Running migrations...
python manage.py migrate
echo [2/3] Creating seed data...
python manage.py seed_data
echo [3/3] Starting server...
echo.
echo Server chay tai: http://127.0.0.1:8000
echo  Quan ly  : quanly / alphahome123
echo  Nhan vien: nhanvien / alphahome123
echo.
python manage.py runserver
pause
