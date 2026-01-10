from enum import Enum
from typing import Annotated

import typer
from kubernetes import client
from rich.console import Console
from rich.table import Table

from devopstoolbox.k8s import utils

app = typer.Typer(no_args_is_help=True)
console = Console()


class ResourcesChoices(str, Enum):
    cpu = "cpu"
    memory = "memory"


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
        table.add_column("Restart Count", justify="center")
        table.add_column("Age", justify="center")
        table.add_column("Status", style="green", justify="center")

        for pod in pods.items:
            statuses = pod.status.container_statuses or []
            restart_count = sum((status.restart_count or 0) for status in statuses)
            table.add_row(pod.metadata.namespace or "-", pod.metadata.name, str(restart_count), utils.calculate_age(pod.status.start_time), pod.status.phase)

        console.print(table)
    except Exception as err:
        console.print(f"[bold red]Error accessing Kubernetes:[/bold red] \n\n{err}")


@app.command()
def metrics(
    namespace: Annotated[str, typer.Option("--namespace", "-n")] = None,
    all_namespaces: Annotated[bool, typer.Option("--all-namespaces", "-A")] = False,
    sort_by: Annotated[ResourcesChoices, typer.Option("--sort-by", "-s")] = None,
    limit: Annotated[int, typer.Option("--limit", "-l")] = None,
):
    """Retrieve CPU and memory resources (requests, limits, usage) for all pods."""
    utils.load_kube_config()
    namespace = namespace or utils.get_current_namespace()
    scope = "all namespaces" if all_namespaces else f"namespace {namespace}"
    console.print(f"[bold blue]Listing pod resources in {scope}...[/bold blue]")

    metrics_by_container = {}
    try:
        metrics_by_container = utils.fetch_pod_metrics(namespace, all_namespaces)
    except Exception as e:
        console.print("[yellow]Warning: Could not fetch metrics (Metrics Server may not be installed)[/yellow]")
        console.print(f"[dim]Details: {e}[/dim]")

    try:
        v1 = client.CoreV1Api()
        pods = v1.list_pod_for_all_namespaces(watch=False) if all_namespaces else v1.list_namespaced_pod(namespace, watch=False)

        rows = []
        for pod in pods.items:
            pod_ns = pod.metadata.namespace or "-"
            pod_name = pod.metadata.name
            for container in pod.spec.containers:
                resources = container.resources
                limits = getattr(resources, "limits", None) or {}
                requests = getattr(resources, "requests", None) or {}

                key = (pod_ns, pod_name, container.name)
                usage = metrics_by_container.get(key, {})
                cpu_raw = usage.get("cpu", "0n") if usage else "0n"
                mem_raw = usage.get("memory", "0Ki") if usage else "0Ki"

                rows.append(
                    {
                        "namespace": pod_ns,
                        "pod": pod_name,
                        "container": container.name,
                        "cpu_req": requests.get("cpu", "-"),
                        "cpu_limit": limits.get("cpu", "-"),
                        "cpu_usage": utils.parse_cpu(cpu_raw) if usage else "-",
                        "cpu_percent": utils.calculate_cpu_percentage(usage.get("cpu"), limits.get("cpu")),
                        "mem_req": requests.get("memory", "-"),
                        "mem_limit": limits.get("memory", "-"),
                        "mem_usage": utils.parse_memory(mem_raw) if usage else "-",
                        "mem_percent": utils.calculate_memory_percentage(usage.get("memory"), limits.get("memory")),
                        "cpu_value": utils.parse_cpu(cpu_raw, return_number=True) if usage else 0,
                        "mem_value": utils.parse_memory(mem_raw, return_number=True) if usage else 0,
                    }
                )

        if sort_by:
            sort_key = "cpu_value" if sort_by == ResourcesChoices.cpu else "mem_value"
            rows.sort(key=lambda x: x[sort_key], reverse=True)

        if limit:
            rows = rows[:limit]

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

        for row in rows:
            table.add_row(
                row["namespace"],
                row["pod"],
                row["container"],
                row["cpu_req"],
                row["cpu_limit"],
                row["cpu_usage"],
                row["cpu_percent"],
                row["mem_req"],
                row["mem_limit"],
                row["mem_usage"],
                row["mem_percent"],
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
        table.add_column("Restart Count", justify="center")
        table.add_column("Age", justify="center")
        table.add_column("Status", style="green", justify="center")

        for pod in pods.items:
            statuses = pod.status.container_statuses or []
            restart_count = sum((status.restart_count or 0) for status in statuses)
            if pod.status.phase not in ("Running", "Succeeded"):
                table.add_row(pod.metadata.namespace or "-", pod.metadata.name, str(restart_count), utils.calculate_age(pod.status.start_time), pod.status.phase)

        console.print(table)
    except Exception as err:
        console.print(f"[bold red]Error accessing Kubernetes:[/bold red] \n\n{err}")
