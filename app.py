import subprocess
import sys
import os
import signal
import time
import threading
import platform

def stream_output(pipe, prefix):
    """
    Reads from a pipe line by line and prints it with a given prefix.
    """
    for line in iter(pipe.readline, b''):
        try:
            decoded = line.decode('utf-8', errors='replace').strip()
            if decoded:
                print(f"[{prefix}] {decoded}", flush=True)
        except Exception:
            pass

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")
    frontend_dir = os.path.join(root_dir, "frontend")

    print(f"🚀 Starting PurpleSector from {root_dir}...")

    is_windows = platform.system().lower() == 'windows'
    python_exe = sys.executable
    npm_cmd = "npm.cmd" if is_windows else "npm"

    # 1. Start FastAPI Backend
    print("⏳ Starting FastAPI Backend on port 8000...")
    try:
        backend_process = subprocess.Popen(
            [python_exe, "-m", "uvicorn", "main:app", "--port", "8000", "--host", "127.0.0.1", "--reload"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        sys.exit(1)

    # 2. Start Vite Frontend
    print("⏳ Starting Vite Frontend on port 5173...")
    try:
        frontend_process = subprocess.Popen(
            [npm_cmd, "run", "dev"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        backend_process.terminate()
        sys.exit(1)

    # Output streaming threads (so terminal output is visible)
    bg_thread = threading.Thread(target=stream_output, args=(backend_process.stdout, "BACKEND"), daemon=True)
    bg_thread.start()

    fg_thread = threading.Thread(target=stream_output, args=(frontend_process.stdout, "FRONTEND"), daemon=True)
    fg_thread.start()

    def signal_handler(sig, frame):
        print("\n🛑 Stopping servers...", flush=True)
        if is_windows:
            # On Windows, kill process tree for node
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(frontend_process.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(backend_process.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            backend_process.terminate()
            frontend_process.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    if not is_windows:
        signal.signal(signal.SIGTERM, signal_handler)

    print("\n✅ PurpleSector is successfully running!")
    print("👉 Frontend: http://localhost:5173")
    print("👉 Backend API: http://localhost:8000")
    print("Press Ctrl+C to stop both servers.\n")
    
    try:
        while True:
            time.sleep(1)
            # If any process dies unexpectedly, terminate the other
            if backend_process.poll() is not None:
                print("\n❌ Backend stopped unexpectedly. Shutting down...", flush=True)
                signal_handler(None, None)
            if frontend_process.poll() is not None:
                print("\n❌ Frontend stopped unexpectedly. Shutting down...", flush=True)
                signal_handler(None, None)
    except KeyboardInterrupt:
        pass # Caught by signal\_handler on Windows

if __name__ == "__main__":
    main()
