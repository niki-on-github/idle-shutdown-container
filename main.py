import time
import os
import psutil
import requests
import subprocess
import threading
from pynvml import nvmlInit, nvmlDeviceGetCount, nvmlDeviceGetHandleByIndex, nvmlDeviceGetUtilizationRates
from fastapi import FastAPI, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from uvicorn import Server
from uvicorn.config import Config

shutdown_requested = False

api_app = FastAPI()
security = HTTPBasic()

@api_app.get("/health")
def health_check():
    return {"status": "healthy"}

@api_app.post("/poweroff")
def power_off(credentials: HTTPBasicCredentials = Depends(security)):
    global shutdown_requested
    username = os.getenv("API_USERNAME")
    password = os.getenv("API_PASSWORD")
    
    if username is None or password is None:
        return {"error": "API credentials not configured"}, 503
    
    if credentials.username != username or credentials.password != password:
        return {"error": "Invalid credentials"}, 401
    
    shutdown_requested = True
    return {"message": "Shutdown initiated"}

def start_api_server():
    config = Config(app=api_app, host="0.0.0.0", port=int(os.getenv("API_PORT", "8000")))
    server = Server(config=config)
    server.run()

def get_int_env(key: str, default: int) -> int:
    try:
        value = int(os.getenv(key, str(default)))
    except ValueError:
        value = default
    return value

def get_cpu_usage():
    return psutil.cpu_percent(interval=2)

def get_gpu_usage():
    try:
        nvmlInit()
        gpus = []
        for i in range(nvmlDeviceGetCount()):
            handle = nvmlDeviceGetHandleByIndex(i)
            util = nvmlDeviceGetUtilizationRates(handle)
            gpus.append(util.gpu)
        return gpus
    except Exception as e:
        print(e)
        return []

def host_has_ssh_sessions() -> bool:
    output = subprocess.check_output(['who', '/host/run/utmp'])
    if b'ssh' in output or b'pts' in output:
        print("SSH sessions detected")
        return True
    else:
        return False

def power_off_system():
    time.sleep(1)
    if os.path.exists("/host/nix"):
        os.system("chroot /host /nix/var/nix/profiles/system/sw/bin/poweroff")
    elif os.path.exists("/host/usr/sbin"):
        os.system("chroot /host /usr/sbin/poweroff")
    else:
        print("ERROR: power off for your host is not implemented or /host is not mounted")

if __name__ == "__main__":
    interval = get_int_env("INTERVAL_SECONDS", 10)
    idle_time = get_int_env("IDLE_TIME_SECONDS", 500)
    cpu_idle = get_int_env("CPU_IDLE_THRESHOLD_PERCENT", 20)
    gpu_idle = get_int_env("GPU_IDLE_THRESHOLD_PERCENT", 5)
    surplus_url = os.environ.get('SURPLUS_CHECK_URL')
    idle_detection_enabled = os.getenv("ENABLE_IDLE_DETECTION", "false").lower() == "true"
    username = os.getenv("API_USERNAME")
    password = os.getenv("API_PASSWORD")
    last_active = time.time()
    os.system("id -a")

    api_enabled = username is not None and password is not None
    print(f"API enabled: {api_enabled}")
    print(f"API enabled on port {os.getenv('API_PORT', '8000')}")

    if api_enabled:
        api_thread = threading.Thread(target=start_api_server)
        api_thread.daemon = True
        api_thread.start()
        print("API server started in background thread")
    else:
        print("API disabled: credentials not set, skipping API server")

    while True:
        time.sleep(interval)
        if shutdown_requested:
            print("System shutdown requested via API")
            time.sleep(5)
            power_off_system()
            shutdown_requested = False
            continue

        if idle_detection_enabled:
            cpu = get_cpu_usage()
            gpu = get_gpu_usage()
            gpu_txt = [str(x) + "%" for x in gpu]
            if len(gpu_txt) == 1:
                gpu_txt = gpu_txt[0]
            print(f"CPU: {cpu}%", f"GPU: {gpu_txt}")
            if cpu > cpu_idle:
                last_active = time.time()
                continue

            if any(x > gpu_idle for x in gpu):
                last_active = time.time()
                continue

            if surplus_url:
                try:
                    surplus = "True" in str(requests.get(surplus_url, verify=False).json())
                except Exception as ex:
                    surplus = False
                    print(ex)
                if surplus:
                    print("surplus ignore idle")
                    last_active = time.time()
                    continue

            if host_has_ssh_sessions():
                last_active = time.time()
                continue

            if time.time() - last_active > idle_time:
                print("System is Idle")
                power_off_system()
