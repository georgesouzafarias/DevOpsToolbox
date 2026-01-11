from enum import Enum
from typing import Annotated

import typer
from kubernetes import client
from rich.console import Console
from rich.table import Table

from devopstoolbox.k8s import utils

app = typer.Typer(no_args_is_help=True)
console = Console()


class ResourcesChoice(str, Enum):
    cpu = "cpu"
    memory = "memory"


def _fetch_pod_resource_data(namespace: str, all_namespaces: bool) -> tuple[list[dict], str, bool]:
    """Fetch pod resource data including metrics.

    Args:
        namespace: The namespace to query.
        all_namespaces: If True, query all namespaces.

    Returns:
        A tuple of (rows, scope, metrics_available) where:
        - rows: List of dicts with resource data for each container
        - scope: String describing the scope (for display)
        - metrics_available: Whether metrics were successfully fetched
    """
    utils.load_kube_config()
    namespace = namespace or utils.get_current_namespace()
    scope = "all namespaces" if all_namespaces else f"namespace {namespace}"

    metrics_by_container = {}
    metrics_available = True
    try:
        metrics_by_container = utils.fetch_pod_metrics(namespace, all_namespaces)
    except Exception as e:
        metrics_available = False
        console.print("[yellow]Warning: Could not fetch metrics (Metrics Server may not be installed)[/yellow]")
        console.print(f"[dim]Details: {e}[/dim]")

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

            cpu_limit_percent = utils.calculate_cpu_percentage(usage.get("cpu"), limits.get("cpu"))
            mem_limit_percent = utils.calculate_memory_percentage(usage.get("memory"), limits.get("memory"))
            cpu_request_percent = utils.calculate_cpu_percentage(usage.get("cpu"), requests.get("cpu"))
            mem_request_percent = utils.calculate_memory_percentage(usage.get("memory"), requests.get("memory"))

            status = pod.status.phase
            restart_count = sum((status.restart_count or 0) for status in pod.status.container_statuses or [])
            age = utils.calculate_age(pod.status.start_time)

            rows.append(
                {
                    "namespace": pod_ns,
                    "pod": pod_name,
                    "container": container.name,
                    "cpu_req": requests.get("cpu", "-"),
                    "cpu_limit": limits.get("cpu", "-"),
                    "cpu_usage": utils.parse_cpu(cpu_raw) if usage else "-",
                    "cpu_percent": f"{cpu_limit_percent:.2f}%",
                    "cpu_provisioned": f"{cpu_request_percent:.2f}%",
                    "cpu_provisioned_value": cpu_request_percent,
                    "mem_req": requests.get("memory", "-"),
                    "mem_limit": limits.get("memory", "-"),
                    "mem_usage": utils.parse_memory(mem_raw) if usage else "-",
                    "mem_percent": f"{mem_limit_percent:.2f}%",
                    "mem_provisioned": f"{mem_request_percent:.2f}%",
                    "mem_provisioned_value": mem_request_percent,
                    "cpu_value": utils.parse_cpu(cpu_raw, return_number=True) if usage else 0,
                    "mem_value": utils.parse_memory(mem_raw, return_number=True) if usage else 0,
                    "statuses": status,
                    "restart_count": f"{restart_count}",
                    "age": age,
                }
            )

    return rows, scope, metrics_available


def _sort_and_limit_rows(rows: list[dict], sort_by: ResourcesChoice | None, limit: int | None) -> list[dict]:
    """Sort and limit rows based on parameters.

    Args:
        rows: List of resource data rows.
        sort_by: Sort by cpu or memory.
        limit: Maximum number of rows to return.

    Returns:
        Sorted and limited list of rows.
    """
    if sort_by:
        sort_key = "cpu_value" if sort_by == ResourcesChoice.cpu else "mem_value"
        rows = sorted(rows, key=lambda x: x[sort_key], reverse=True)

    if limit:
        rows = rows[:limit]

    return rows


@app.command()
def list(
    namespace: Annotated[str, typer.Option("--namespace", "-n", help="Kubernetes namespace to query")] = None,
    all_namespaces: Annotated[bool, typer.Option("--all-namespaces", "-A", help="Query all namespaces")] = False,
):
    """List all pods with status, restart count, and age."""

    try:
        rows, scope, _ = _fetch_pod_resource_data(namespace, all_namespaces)

        table = Table(title=f"Pods in {scope}")
        table.add_column("Namespace", style="cyan", justify="center")
        table.add_column("Pod Name", style="green", justify="center")
        table.add_column("Restart Count", justify="center")
        table.add_column("Age", justify="center")
        table.add_column("Status", style="green", justify="center")

        for row in rows:
            table.add_row(row["namespace"], row["pod"], row["restart_count"], row["age"], row["statuses"])

        console.print(table)
    except Exception as err:
        console.print(f"[bold red]Error accessing Kubernetes:[/bold red] \n\n{err}")


@app.command()
def metrics(
    namespace: Annotated[str, typer.Option("--namespace", "-n", help="Kubernetes namespace to query")] = None,
    all_namespaces: Annotated[bool, typer.Option("--all-namespaces", "-A", help="Query all namespaces")] = False,
    sort_by: Annotated[ResourcesChoice, typer.Option("--sort-by", "-s", help="Sort results by cpu or memory usage")] = None,
    limit: Annotated[int, typer.Option("--limit", "-l", min=1, help="Limit the number of results")] = None,
):
    """Show CPU and memory metrics (requests, limits, usage) for all pods."""
    try:
        rows, scope, _ = _fetch_pod_resource_data(namespace, all_namespaces)
        console.print(f"[bold blue]Listing pod resources in {scope}...[/bold blue]")

        rows = _sort_and_limit_rows(rows, sort_by, limit)

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
def unhealthy(
    namespace: Annotated[str, typer.Option("--namespace", "-n", help="Kubernetes namespace to query")] = None,
    all_namespaces: Annotated[bool, typer.Option("--all-namespaces", "-A", help="Query all namespaces")] = False,
):
    """List pods not in Running or Succeeded state."""
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


@app.command()
def overprovisioned(
    namespace: Annotated[str, typer.Option("--namespace", "-n", help="Kubernetes namespace to query")] = None,
    all_namespaces: Annotated[bool, typer.Option("--all-namespaces", "-A", help="Query all namespaces")] = False,
    sort_by: Annotated[ResourcesChoice, typer.Option("--sort-by", "-s", help="Sort results by cpu or memory usage")] = None,
    limit: Annotated[int, typer.Option("--limit", "-l", min=1, help="Limit the number of results")] = None,
    threshold: Annotated[float, typer.Option("--threshold", "-th", min=0, help="Usage threshold percentage (default: 50)")] = 50,
):
    """Find pods where resource usage is below threshold percentage of requests."""
    try:
        rows, scope, _ = _fetch_pod_resource_data(namespace, all_namespaces)
        rows = [row for row in rows if row["cpu_provisioned_value"] < threshold or row["mem_provisioned_value"] < threshold]

        rows = _sort_and_limit_rows(rows, sort_by, limit)

        table = Table(title=f"Overprovisioned Pods in {scope} and Threshold: {threshold}%")
        table.add_column("Namespace", style="cyan", justify="center")
        table.add_column("Pod Name", style="cyan", justify="center")
        table.add_column("Container", style="cyan", justify="center")
        table.add_column("CPU Req", style="green", justify="center")
        table.add_column("CPU Limit", style="yellow", justify="center")
        table.add_column("CPU Usage", style="magenta", justify="center")
        table.add_column("CPU Usage %", style="magenta", justify="center")
        table.add_column("CPU From Request %", style="magenta", justify="center")
        table.add_column("Mem Req", style="green", justify="center")
        table.add_column("Mem Limit", style="yellow", justify="center")
        table.add_column("Mem Usage", style="magenta", justify="center")
        table.add_column("Mem Usage %", style="magenta", justify="center")
        table.add_column("Mem From Request %", style="magenta", justify="center")

        for row in rows:
            table.add_row(
                row["namespace"],
                row["pod"],
                row["container"],
                row["cpu_req"],
                row["cpu_limit"],
                row["cpu_usage"],
                row["cpu_percent"],
                row["cpu_provisioned"],
                row["mem_req"],
                row["mem_limit"],
                row["mem_usage"],
                row["mem_percent"],
                row["mem_provisioned"],
            )

        console.print(table)
    except Exception as err:
        console.print(f"[bold red]Error accessing Kubernetes:[/bold red] \n\n{err}")
