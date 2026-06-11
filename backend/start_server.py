"""后台启动 Django dev server"""
import subprocess, sys, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
proc = subprocess.Popen(
    [sys.executable, "manage.py", "runserver", "0.0.0.0:8000"],
    stdout=open("server_stdout.log", "w"),
    stderr=open("server_stderr.log", "w"),
)
print(f"Starting server, PID={proc.pid}")
