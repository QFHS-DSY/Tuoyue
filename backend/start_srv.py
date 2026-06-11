import subprocess, sys, os
os.chdir(r"D:\erp总和\backend")
proc = subprocess.Popen([sys.executable, "manage.py", "runserver", "0.0.0.0:8000"], stdout=open("server_stdout.log","w"), stderr=open("server_stderr.log","w"))
print(f"Started PID={proc.pid}")
