"""EasyShop - one-click launcher (PyInstaller bundle)"""
import sys, os, socket, subprocess

BASE_DIR = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if __name__ == '__main__':
    print("=" * 50)
    print("  EasyShop - E-Commerce Platform")
    print("=" * 50)
    print()

    # Check port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if s.connect_ex(('127.0.0.1', 8000)) == 0:
        print("  [ERROR] Port 8000 is already in use!")
        input("  Press Enter to exit...")
        sys.exit(1)
    s.close()

    print("  Starting server...")
    print("  Open browser: http://localhost:8000")
    print("  Admin: admin / Admin123456")
    print()

    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, log_level="info")
