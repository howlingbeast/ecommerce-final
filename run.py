"""EasyShop 一键启动 — 双击或在项目根目录运行 python run.py"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(BASE_DIR, "backend"))
sys.path.insert(0, os.getcwd())

if sys.version_info < (3, 9):
    print("[ERROR] Python 3.9+ is required")
    print(f"        Current: {sys.version}")
    input("\nPress Enter to exit...")
    sys.exit(1)

try:
    import fastapi
except ImportError:
    print("[1/2] Installing dependencies...")
    mirrors = [
        "https://pypi.tuna.tsinghua.edu.cn/simple",
        "https://mirrors.aliyun.com/pypi/simple/",
    ]
    installed = False
    for mirror in mirrors:
        print(f"      Trying mirror: {mirror}")
        ret = os.system(f'pip install -r requirements.txt -i {mirror} --no-cache-dir')
        if ret == 0:
            installed = True
            break
    if not installed:
        print("\n[ERROR] Failed to install dependencies!")
        print("       Please run manually:")
        print("       cd backend && pip install -r requirements.txt")
        input("\nPress Enter to exit...")
        sys.exit(1)
    print()

import uvicorn

print("=" * 50)
print("  EasyShop - E-Commerce Platform")
print("=" * 50)
print()
print("  Open browser: http://localhost:8000")
print("  Admin:        admin / Admin123456")
print("  User:         testuser / Test123456")
print()
print("  [Tips] 如需前后端分离运行:")
print("  1. 终端1: python run.py")
print("  2. 终端2: cd frontend && npm run dev")
print("  3. 访问 http://localhost:5173")
print()

uvicorn.run("app.main:app", host="0.0.0.0", port=8000, log_level="info")
