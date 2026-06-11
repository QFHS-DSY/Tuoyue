import subprocess, sys, os
log = open(os.path.join("d:", os.sep, "erp总和", "backend", "run3.log"), "w", buffering=1)
p = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "myproject.asgi:application",
     "--host", "0.0.0.0", "--port", "1102", "--log-level", "info"],
    cwd=os.path.join("d:", os.sep, "erp总和", "backend"),
    stdout=log, stderr=subprocess.STDOUT,
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
)
print("PID:", p.pid)
