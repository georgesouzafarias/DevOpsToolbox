import re
from datetime import datetime, timezone

import urllib3
from kubernetes import config
from kubernetes.client import CustomObjectsApi

# Hide InsecureRequestWarning when CA certificate is not configured
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_kube_config_loaded = False


def load_kube_config():
    """Load kubeconfig when K8s commands are called."""
    global _kube_config_loaded
    if _kube_config_loaded:
        return
    try:
        config.load_kube_config()
    except config.ConfigException:
        config.load_incluster_config()
    _kube_config_loaded = True


def get_current_namespace():
    """Get the current namespace from the active Kubernetes context."""
    try:
        _, active_context = config.list_kube_config_contexts()
        return active_context["context"].get("namespace", "default")
    except Exception:
        return "default"


def parse_cpu(cpu_str: str, return_number: bool = False):
    """Convert Kubernetes CPU units to human-readable format (millicores)."""
    if cpu_str.endswith("n"):
        nanocores = int(cpu_str[:-1])
        millicores = nanocores / 1_000_000
        if return_number:
            return millicores
        else:
            return f"{millicores:.2f}m"
    elif cpu_str.endswith("u"):
        microcores = int(cpu_str[:-1])
        millicores = microcores / 1_000
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
            return cores * 1000
        else:
            return f"{cores * 1000:.2f}m"


def parse_memory(mem_str: str, return_number: bool = False):
    """Convert Kubernetes memory units to human-readable format."""
    units = {"Ki": 1024, "Mi": 1024**2, "Gi": 1024**3, "Ti": 1024**4}
    match = re.match(r"^(\d+)(Ki|Mi|Gi|Ti)?$", mem_str)
    if not match:
        return 0 if return_number else mem_str
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


def calculate_cpu_percentage(usage, limit) -> float:
    """Calculate CPU usage percentage from usage and limit values."""
    if usage is None or limit is None or not (usage[:-1].isdigit() or usage.isdigit()) or not (limit[:-1].isdigit() or limit.isdigit()):
        return 0
    limit_value = parse_cpu(limit, return_number=True)
    if limit_value == 0:
        return 0
    result = parse_cpu(usage, return_number=True) / limit_value * 100
    return result


def calculate_memory_percentage(usage, limit) -> float:
    """Calculate Memory usage percentage from usage and limit values."""
    if usage is None or limit is None or not usage[:-2].isdigit() or not limit[:-2].isdigit():
        return 0
    limit_value = parse_memory(limit, return_number=True)
    if limit_value == 0:
        return 0
    result = parse_memory(usage, return_number=True) / limit_value * 100
    return result


def calculate_age(start_time):
    """Format a timedelta object into a human-readable string."""
    td = datetime.now(timezone.utc) - start_time
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if days > 0:
        return f"{days}d"
    elif days == 0 and hours > 0:
        return f"{hours}h{minutes}m"
    elif hours == 0 and minutes >= 0:
        return f"{minutes}m{seconds}s"
    else:
        return f"{seconds}s"


def fetch_pod_metrics(namespace: str = None, all_namespaces: bool = False) -> dict:
    """
    Retrieves CPU and memory usage metrics for pods from the Kubernetes Metrics Server API.
    Metrics can be fetched for a specific namespace or across all namespaces in the cluster.
    """
    custom_api = CustomObjectsApi()

    if all_namespaces:
        pod_metrics = custom_api.list_cluster_custom_object(group="metrics.k8s.io", version="v1beta1", plural="pods")
    else:
        pod_metrics = custom_api.list_namespaced_custom_object(group="metrics.k8s.io", version="v1beta1", namespace=namespace, plural="pods")

    metrics_by_container = {}
    for pod in pod_metrics.get("items", []):
        pod_name = pod.get("metadata", {}).get("name", "")
        pod_ns = pod.get("metadata", {}).get("namespace", "")
        for container in pod.get("containers", []):
            key = (pod_ns, pod_name, container.get("name"))
            metrics_by_container[key] = container.get("usage", {})

    return metrics_by_container
