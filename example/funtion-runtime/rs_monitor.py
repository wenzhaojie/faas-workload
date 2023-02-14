import subprocess
import os
import psutil

FUNCTION_NAME = os.environ.get("FUNCTION_NAME", "default")

def get_function_resource() -> dict:
    """
    返回当前函数docker内的资源限制:
    res = {'vcpus': 1.0, 'memory': 100.0}
    表示1个vcpu, 100MB内存。
    """
    # cat /sys/fs/cgroup/memory/memory.limit_in_bytes (1GB = 1073741824)
    # cat /sys/fs/cgroup/cpu/cpu.cfs_quota_us （1vcpu = 100000）

    show_memory_cmd = "cat /sys/fs/cgroup/memory/memory.limit_in_bytes"
    show_cfs_quota_us_cmd = "cat /sys/fs/cgroup/cpu/cpu.cfs_quota_us"
    show_cfs_period_us_cmd = "cat /sys/fs/cgroup/cpu/cpu.cfs_period_us"
    show_hostname_cmd = "cat /etc/hostname"
    memory = int(subprocess.getoutput(show_memory_cmd)) / 1024 / 1024 # MB
    cfs_quota_us = int(subprocess.getoutput(show_cfs_quota_us_cmd)) 
    cfs_period_us = int(subprocess.getoutput(show_cfs_period_us_cmd)) 
    host_name = str(subprocess.getoutput(show_hostname_cmd))

    if cfs_quota_us != -1: # 说明在容器里
        res = {
            "cpu": cfs_quota_us / cfs_period_us,
            "memory": min(int(psutil.virtual_memory().total / (1024.0 * 1024.0)), int(memory)), # MB
            "host_name": host_name,
            "node_name": os.environ.get("MY_NODE_NAME")
        }
    else: # 不在容器里
        res = {
            "cpu": psutil.cpu_count(),
            "memory": int(psutil.virtual_memory().total / (1024.0 * 1024.0)),
            "host_name": host_name,
            "node_name": host_name
        }
    return res

if __name__ == "__main__":
    print(get_function_resource())