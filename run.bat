@echo off
chcp 65001 >nul
echo ========================================
echo   EasyShop - E-Commerce Platform
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo.
    echo Please install Python 3.9+ first, or use:
    echo   backend\dist\EasyShop.exe  (no Python needed)
    echo.
    pause
    exit /b
)

python --version
echo.

REM Check if port 8000 is in use
netstat -ano | findstr ":8000 " | findstr LISTENING >nul
if %errorlevel% equ 0 (
    echo [WARNING] Port 8000 is already in use!
    echo Please close the other program first, then try again.
    pause
    exit /b
)

echo [1/2] Installing dependencies (this may take a moment)...
cd /d "%~dp0backend"
echo   Using python -m pip for better compatibility...
python -m pip install --no-cache-dir -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo   Trying China mirror (清华源)...
    python -m pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    if %errorlevel% neq 0 (
        echo.
        echo [ERROR] Failed to install dependencies!
        echo Possible fixes:
        echo   1. Run as Administrator
        echo   2. Use: backend\dist\EasyShop.exe  (no Python needed)
        echo   3. Or manually: cd backend ^&^& pip install -r requirements.txt
        pause
        exit /b
    )
)
echo.

REM Start server
echo [2/2] Starting server...
echo.
echo ========================================
echo   Open browser: http://localhost:8000
echo.
echo   Admin:  admin / Admin123456
echo   User:   testuser / Test123456
echo ========================================
echo.
echo   Press Ctrl+C to stop the server
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Server failed to start!
    pause
)
