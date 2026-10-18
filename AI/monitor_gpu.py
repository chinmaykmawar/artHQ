import time
import psutil
import subprocess

def monitor_gpu(filename="gpu_usage.log", interval=1):
    with open(filename, "w") as f:
        f.write("starting GPU Monitoring...\n")
    psutil.cpu_percent(interval=None)
    while True:
        cpu_usage = psutil.cpu_percent(interval=None)
        cpu_per_core = psutil.cpu_percent(interval=None, percpu=True)
        ram = psutil.virtual_memory()

        result = subprocess.run(
        [
        "nvidia-smi",
        "--query-gpu="
        "utilization.gpu,"
        "memory.used,"
        "memory.total,"
        "temperature.gpu,"
        "power.draw,"
        "power.limit,"
        "clocks.gr,"
        "clocks.mem",
        "--format=csv,noheader,nounits",
        ],
        capture_output=True,
        text=True,
        )
        timestamp = time.strftime("%H:%M:%S")
        with open(filename, "a") as f:
            f.write(
                f"{timestamp} | "
                f"CPU: {cpu_usage}% | "
                f"CPU Cores: {cpu_per_core}% | "
                f"RAM: {ram.percent}% "
                f"({ram.used / (1024**3):.2f}/"
                f"{ram.total / (1024**3):.2f} GB) | "
                f"GPU: {result.stdout.strip()}\n"
            )

        time.sleep(interval)
        
monitor_gpu()