import re

from kubernetes import config


def get_kube_config():
    """Get Kube Config"""
    try:
        return config.load_kube_config()
    except config.ConfigException:
        return config.load_incluster_config()


def parse_cpu(cpu_str: str, return_number: bool = False):
    """Convert Kubernetes CPU units to human-readable format (millicores)."""
    if cpu_str.endswith("n"):
        nanocores = int(cpu_str[:-1])
        millicores = nanocores / 1_000_000
        if return_number:
            return millicores
        else:
            return f"{millicores:.2f}m"
    elif cpu_str.endswith("m"):
        if return_number:
            return int(cpu_str[:-1])
        else:
            return cpu_str
    else:
        cores = float(cpu_str)
        if return_number:
            return cores*1000
        else:
            return f"{cores * 1000:.2f}m"


def parse_memory(mem_str: str, return_number: bool = False):
    """Convert Kubernetes memory units to human-readable format."""
    units = {"Ki": 1024, "Mi": 1024**2, "Gi": 1024**3, "Ti": 1024**4}
    match = re.match(r"^(\d+)(Ki|Mi|Gi|Ti)?$", mem_str)
    if not match:
        return mem_str
    value = int(match.group(1))
    unit = match.group(2) or ""
    bytes_val = value * units.get(unit, 1)
    if return_number:
        return bytes_val
    else:
        if bytes_val >= 1024**3:
            return f"{bytes_val / 1024**3:.2f} Gi"
        elif bytes_val >= 1024**2:
            return f"{bytes_val / 1024**2:.2f} Mi"
        elif bytes_val >= 1024:
            return f"{bytes_val / 1024:.2f} Ki"
        return f"{bytes_val} B"


def calculate_cpu_percentage(usage, limit):
    print(f"CPU: {limit}")
    if limit is None:
        return "-"
    else:
        result = parse_cpu(usage, return_number=True) / parse_cpu(limit,return_number=True) * 100
        return f"{result:.2f}%"

def calculate_memory_percentage(usage, limit):
    print(f"Memory: {limit}")
    if limit is None:
        return "-"
    else:
        result = parse_memory(usage, return_number=True) / parse_memory(limit, return_number=True)
        return f"{result:.2f}%"
