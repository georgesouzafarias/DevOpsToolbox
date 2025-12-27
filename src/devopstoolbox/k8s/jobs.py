import typer
from kubernetes import client
from rich.console import Console
from rich.table import Table

from devopstoolbox.k8s import utils

app = typer.Typer(no_args_is_help=True)
console = Console()
config = utils.get_kube_config()
# custom_api = CustomObjectsApi()


@app.command()
def list(namespace: str = "default", all_namespaces: bool = False):
    """List pods"""
    scope = "all_namespaces" if all_namespaces else namespace
    console.print(f"[bold blue]Listing pods in {scope}...[/bold blue]")

    try:
        v1 = client.BatchV1Api
        jobs = v1.list_job_for_all_namespaces(watch=False) if all_namespaces else v1.list_namespaced_job(scope, watch=False)

        table = Table(title=f"Jobs in {scope}")
        table.add_column("Namespace", style="cyan", justify="center")
        table.add_column("Pod Name", style="green", justify="center")
        table.add_column("Status", style="green", justify="center")
        table.add_column("Restart Count", justify="center")

        for job in jobs.items:
            statuses = job.status.container_statuses or []
            restart_count = sum((status.restart_count or 0) for status in statuses)
            table.add_row(job.metadata.namespace or "-", job.metadata.name, job.status.phase, str(restart_count))

        console.print(table)
    except Exception as err:
        console.print(f"[bold red]Error accessing Kubernetes:[/bold red] \n\n{err}")
