@echo off
chcp 65001 >nul
echo ========================================
echo   📦 打包为单文件 exe
echo ========================================
echo.

cd /d "%~dp0backend"

REM 安装 PyInstaller
echo 📥 安装 PyInstaller...
pip install pyinstaller -q

REM 构建单文件 exe
echo 🔨 正在打包（约 1-2 分钟）...
pyinstaller --onefile ^
  --name "EasyShop" ^
  --add-data "app;app" ^
  --add-data "..\frontend\dist;frontend\dist" ^
  --add-data "keys;keys" ^
  --add-data ".env;." ^
  --add-data "..\frontend\dist\assets;frontend\dist\assets" ^
  --hidden-import "uvicorn.logging" ^
  --hidden-import "uvicorn.loops.auto" ^
  --hidden-import "uvicorn.protocols.http.auto" ^
  --hidden-import "alipay" ^
  --collect-all "app" ^
  run_server.py

echo.
if %errorlevel% equ 0 (
    echo ✅ 打包成功！
    echo 📍 文件位置: dist\EasyShop.exe
    echo 📦 大小: 
    for %%I in (dist\EasyShop.exe) do echo    %%~zI 字节
    echo.
    echo 复制以下文件到老师的 U 盘：
    echo   1. dist\EasyShop.exe
    echo   2. frontend\dist\ （整个文件夹）
    echo   3. backend\.env
    echo   4. backend\keys\ （整个文件夹）
) else (
    echo ❌ 打包失败，查看上方错误信息
)

pause
