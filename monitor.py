import time
import os
import psutil
import subprocess
from pynvml import nvmlInit, nvmlDeviceGetCount, nvmlDeviceGetHandleByIndex, \
    nvmlDeviceGetUtilizationRates

def get_float_env(key: str, default: float) -> float:
    try:
        value = float(os.getenv(key, str(default)))
    except ValueError:
        value = default

    return value

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

"""
This require proper setup with ClientAliveInterval and ClientAliveCountMax
"""
def host_has_ssh_sessions() -> bool:
    output = subprocess.check_output(['who', '/host/run/utmp'])
    if b'ssh' in output or b'pts' in output:
        print("SSH sessions detected")
        return True
    else:
        return False

if __name__ == "__main__":
    interval = get_int_env("INTERVAL_SECONDS", 10)
    idle_time = get_int_env("IDLE_TIME_SECONDS", 500)
    cpu_idle = get_int_env("CPU_IDLE_THRESHOLD_PERCENT", 20)
    gpu_idle = get_int_env("GPU_IDLE_THRESHOLD_PERCENT", 5)
    last_active = time.time()
    os.system("id -a")
    while True:
        time.sleep(interval)
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

        if host_has_ssh_sessions():
            last_active = time.time()
            continue

        if time.time() - last_active > idle_time:
            print("System is Idle")
            time.sleep(1)
            if os.path.exists("/host/nix"):
                os.system("chroot /host /nix/var/nix/profiles/system/sw/bin/poweroff")
            elif os.path.exists("/host/usr/sbin"):
                os.system("chroot /host /usr/sbin/poweroff")
            else:
                print("ERROR: power off for your host is not implemented or /host is not mounted")
