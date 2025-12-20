import typer
from rich.console import Console
from rich.table import Table
from kubernetes import client, config, watch


app = typer.Typer(no_args_is_help=True)
console = Console()
config.load_kube_config()

@app.command()
def list(namespace: str = "default", all_namespaces: bool = False):
    """List pods"""
    scope = "all namespaces" if all_namespaces else f"namespace {namespace}"
    console.print(f"[bold blue]Listing pods in {scope}...[/bold blue]")

    try:
        v1 = client.CoreV1Api()
        pods = (
            v1.list_pod_for_all_namespaces(watch=False)
            if all_namespaces
            else v1.list_namespaced_pod(namespace, watch=False)
        )

        table = Table(title=f"Pods in {scope}")
        table.add_column("Namespace", style="cyan", justify="center")
        table.add_column("Pod Name", style="green", justify="center")
        table.add_column("Restart Count", justify="center")

        for pod in pods.items:
            statuses = pod.status.container_statuses or []
            restart_count = sum((status.restart_count or 0) for status in statuses)
            table.add_row(pod.metadata.namespace or "-", pod.metadata.name, str(restart_count))

        console.print(table)
    except
      print(f"Something was wrong with the kubernets access: err")


