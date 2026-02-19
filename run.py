"""
run.py
Master startup script — starts both FastAPI backend and Streamlit frontend.
Run with: python run.py

This starts:
1. FastAPI backend on http://localhost:8000
2. Streamlit frontend on http://localhost:8501
"""

import subprocess
import sys
import time
import os
import threading
import webbrowser

def run_backend():
    """Start FastAPI backend."""
    print("🚀 Starting FastAPI backend on http://localhost:8000 ...")
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "backend.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ])

def run_frontend():
    """Start Streamlit frontend."""
    time.sleep(3)  # Wait for backend to start
    print("🌐 Starting Streamlit frontend on http://localhost:8501 ...")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "frontend/app.py",
        "--server.port", "8501",
        "--server.headless", "false",
        "--browser.gatherUsageStats", "false"
    ])

def open_browser():
    """Open browser after services start."""
    time.sleep(6)
    print("🌍 Opening browser...")
    webbrowser.open("http://localhost:8501")

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║         SAR NARRATIVE GENERATOR - BARCLAYS AML SUITE        ║
║              AI-Powered | Fully Local | Secure               ║
╚══════════════════════════════════════════════════════════════╝

Starting services...
""")

    # Run backend and frontend in separate threads
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    frontend_thread = threading.Thread(target=run_frontend, daemon=True)
    browser_thread = threading.Thread(target=open_browser, daemon=True)

    backend_thread.start()
    frontend_thread.start()
    browser_thread.start()

    print("""
╔══════════════════════════════════════════════════════════════╗
║  ✅ Backend API: http://localhost:8000                       ║
║  ✅ Frontend UI: http://localhost:8501                       ║
║  ✅ API Docs:    http://localhost:8000/docs                  ║
║                                                              ║
║  Press Ctrl+C to stop all services                          ║
╚══════════════════════════════════════════════════════════════╝
""")

    try:
        backend_thread.join()
        frontend_thread.join()
    except KeyboardInterrupt:
        print("\n👋 Shutting down SAR Generator...")
        sys.exit(0)
