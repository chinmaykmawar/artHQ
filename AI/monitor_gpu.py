import time
import subprocess

def monitor_gpu(filename="gpu_usage.log", interval=1):
    with open(filename, "w") as f:
        f.write("starting GPU Monitoring...\n")
    while True:
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

        with open(filename, "a") as f:
            f.write(
                f"{time.strftime('%H:%M:%S')} | "
                f"{result.stdout.strip()}\n"
            )

        time.sleep(interval)
        
monitor_gpu()