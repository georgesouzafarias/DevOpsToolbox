from typing import Annotated

import typer
from kubernetes import client
from kubernetes.client import CustomObjectsApi
from rich.console import Console
from rich.table import Table

from devopstoolbox.k8s import utils

app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command()
def list(namespace: Annotated[str, typer.Option("--namespace", "-n")] = None, all_namespaces: Annotated[bool, typer.Option("--all-namespaces", "-A")] = False):
    """List pods"""
    utils.load_kube_config()
    namespace = namespace or utils.get_current_namespace()
    scope = "all namespaces" if all_namespaces else f"namespace {namespace}"
    console.print(f"[bold blue]Listing pods in {scope}...[/bold blue]")

    try:
        v1 = client.CoreV1Api()
        pods = v1.list_pod_for_all_namespaces(watch=False) if all_namespaces else v1.list_namespaced_pod(namespace, watch=False)

        table = Table(title=f"Pods in {scope}")
        table.add_column("Namespace", style="cyan", justify="center")
        table.add_column("Pod Name", style="green", justify="center")
        table.add_column("Status", style="green", justify="center")
        table.add_column("Restart Count", justify="center")

        for pod in pods.items:
            statuses = pod.status.container_statuses or []
            restart_count = sum((status.restart_count or 0) for status in statuses)
            table.add_row(pod.metadata.namespace or "-", pod.metadata.name, pod.status.phase, str(restart_count))

        console.print(table)
    except Exception as err:
        console.print(f"[bold red]Error accessing Kubernetes:[/bold red] \n\n{err}")


@app.command()
def metrics(namespace: Annotated[str, typer.Option("--namespace", "-n")] = None, all_namespaces: Annotated[bool, typer.Option("--all-namespaces", "-A")] = False):
    """
    Retrieves CPU and memory resources (requests, limits, usage) for all pods.
    """
    utils.load_kube_config()
    namespace = namespace or utils.get_current_namespace()
    scope = "all namespaces" if all_namespaces else f"namespace {namespace}"
    console.print(f"[bold blue]Listing pod resources in {scope}...[/bold blue]")

    custom_api = CustomObjectsApi()
    metrics_by_container = {}
    try:
        if all_namespaces:
            pod_metrics = custom_api.list_cluster_custom_object(group="metrics.k8s.io", version="v1beta1", plural="pods")
        else:
            pod_metrics = custom_api.list_namespaced_custom_object(group="metrics.k8s.io", version="v1beta1", namespace=namespace, plural="pods")

        for pod in pod_metrics.get("items", []):
            pod_name = pod.get("metadata", {}).get("name", "")
            pod_ns = pod.get("metadata", {}).get("namespace", "")
            for container in pod.get("containers", []):
                key = (pod_ns, pod_name, container.get("name"))
                metrics_by_container[key] = container.get("usage", {})
    except Exception as e:
        console.print("[yellow]Warning: Could not fetch metrics (Metrics Server may not be installed)[/yellow]")
        console.print(f"[dim]Details: {e}[/dim]")

    try:
        v1 = client.CoreV1Api()
        pods = v1.list_pod_for_all_namespaces(watch=False) if all_namespaces else v1.list_namespaced_pod(namespace, watch=False)

        table = Table(title=f"Pod Resources in {scope}")
        table.add_column("Namespace", style="cyan", justify="center")
        table.add_column("Pod Name", style="cyan", justify="center")
        table.add_column("Container", style="cyan", justify="center")
        table.add_column("CPU Req", style="green", justify="center")
        table.add_column("CPU Limit", style="yellow", justify="center")
        table.add_column("CPU Usage", style="magenta", justify="center")
        table.add_column("CPU Usage %", style="magenta", justify="center")
        table.add_column("Mem Req", style="green", justify="center")
        table.add_column("Mem Limit", style="yellow", justify="center")
        table.add_column("Mem Usage", style="magenta", justify="center")
        table.add_column("Mem Usage %", style="magenta", justify="center")

        for pod in pods.items:
            pod_ns = pod.metadata.namespace or "-"
            pod_name = pod.metadata.name
            for container in pod.spec.containers:
                resources = container.resources
                limits = getattr(resources, "limits", None) or {}
                requests = getattr(resources, "requests", None) or {}

                key = (pod_ns, pod_name, container.name)
                usage = metrics_by_container.get(key, {})
                cpu_percent_usage = utils.calculate_cpu_percentage(usage.get("cpu"), limits.get("cpu"))
                memory_percent_usage = utils.calculate_memory_percentage(usage.get("memory"), limits.get("memory"))
                table.add_row(
                    pod_ns,
                    pod_name,
                    container.name,
                    requests.get("cpu", "-"),
                    limits.get("cpu", "-"),
                    utils.parse_cpu(usage.get("cpu", "0n")) if usage else "-",
                    cpu_percent_usage,
                    requests.get("memory", "-"),
                    limits.get("memory", "-"),
                    utils.parse_memory(usage.get("memory", "0Ki")) if usage else "-",
                    memory_percent_usage,
                )

        console.print(table)
    except Exception as err:
        console.print(f"[bold red]Error accessing Kubernetes:[/bold red] \n\n{err}")


@app.command()
def unhealthy(namespace: Annotated[str, typer.Option("--namespace", "-n")] = None, all_namespaces: Annotated[bool, typer.Option("--all-namespaces", "-A")] = False):
    """
    List pods with issues (not in Running or Succeeded state).
    """
    utils.load_kube_config()
    namespace = namespace or utils.get_current_namespace()
    scope = "all namespaces" if all_namespaces else f"namespace {namespace}"
    console.print(f"[bold blue]Listing Issued pods in {scope}...[/bold blue]")

    try:
        v1 = client.CoreV1Api()
        pods = v1.list_pod_for_all_namespaces(watch=False) if all_namespaces else v1.list_namespaced_pod(namespace, watch=False)

        table = Table(title=f"Pods in {scope}")
        table.add_column("Namespace", style="cyan", justify="center")
        table.add_column("Pod Name", style="green", justify="center")
        table.add_column("Status", style="green", justify="center")
        table.add_column("Restart Count", justify="center")

        for pod in pods.items:
            statuses = pod.status.container_statuses or []
            restart_count = sum((status.restart_count or 0) for status in statuses)
            if pod.status.phase not in ("Running", "Succeeded"):
                table.add_row(pod.metadata.namespace or "-", pod.metadata.name, pod.status.phase, str(restart_count))

        console.print(table)
    except Exception as err:
        console.print(f"[bold red]Error accessing Kubernetes:[/bold red] \n\n{err}")
