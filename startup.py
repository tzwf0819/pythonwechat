import subprocess
import time
import os
import signal
import psutil  # 用于获取进程树并终止所有子进程
from database import create_db_and_tables

def check_database_connection():
    try:
        create_db_and_tables()
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

def start_main_app():
    # 启动 main_app
    print("Starting main app...")
    process = subprocess.Popen(["uvicorn", "main_app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"], cwd="D:\\Yida\\code\\python\\backend")
    print(f"Main app started with PID: {process.pid}")
    return process

def start_fallback_app():
    # 启动 fallback_app
    print("Starting fallback app...")
    process = subprocess.Popen(["uvicorn", "fallback_app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"], cwd="D:\\Yida\\code\\python\\backend")
    print(f"Fallback app started with PID: {process.pid}")
    return process

def stop_process(process):
    if process:
        # 获取进程 ID
        pid = process.pid
        print(f"Stopping process with PID: {pid}")
        try:
            # 使用 psutil 获取进程树并终止所有子进程
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            for child in children:
                print(f"Stopping child process with PID: {child.pid}")
                child.terminate()
            # 终止父进程
            print(f"Stopping parent process with PID: {pid}")
            parent.terminate()
            # 等待进程结束，最多等待 5 秒
            parent.wait(timeout=5)
            print(f"Process with PID: {pid} stopped successfully.")
        except psutil.NoSuchProcess:
            print(f"Process {pid} does not exist.")
        except subprocess.TimeoutExpired:
            print(f"Process {pid} did not terminate in time. Killing it.")
            parent.kill()
            parent.wait()
            print(f"Process with PID: {pid} killed.")

def main():
    current_process = None
    while True:
        if check_database_connection():
            if current_process is None or current_process.poll() is not None:
                print("Database connected. Starting main app...")
                if current_process:
                    stop_process(current_process)  # 停止 fallback_app
                current_process = start_main_app()  # 启动 main_app
            else:
                print("Main app is already running.")
        else:
            if current_process is None or current_process.poll() is not None:
                print("Database not connected. Starting fallback app...")
                if current_process:
                    stop_process(current_process)  # 停止 main_app
                current_process = start_fallback_app()  # 启动 fallback_app
            else:
                print("Fallback app is already running.")
        time.sleep(30)  # 每5分钟检查一次

if __name__ == "__main__":
    main()