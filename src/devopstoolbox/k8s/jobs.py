from typing import Annotated

import typer
from kubernetes import client
from rich.console import Console
from rich.table import Table

from devopstoolbox.k8s import utils

app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command()
def list(namespace: Annotated[str, typer.Option("--namespace", "-n")] = None, all_namespaces: Annotated[bool, typer.Option("--all-namespaces", "-A")] = False):
    """List Jobs"""
    utils.load_kube_config()
    namespace = namespace or utils.get_current_namespace()
    scope = "all namespaces" if all_namespaces else f"namespace {namespace}"
    console.print(f"[bold blue]Listing jobs in {scope}...[/bold blue]")

    try:
        v1 = client.BatchV1Api()
        jobs = v1.list_job_for_all_namespaces(watch=False) if all_namespaces else v1.list_namespaced_job(namespace=namespace, watch=False)

        table = Table(title=f"Jobs in {scope}")
        table.add_column("Namespace", style="cyan", justify="center")
        table.add_column("Job Name", style="green", justify="center")
        table.add_column("Suspended?", style="green", justify="center")
        # table.add_column("Restart Count", justify="center")

        for job in jobs.items:
            print(job.metadata.name)
            table.add_row(job.metadata.namespace or "-", job.metadata.name, f"{job.spec.suspend}")

        # for job in jobs.items:
        #     statuses = job.status.container_statuses or []
        #     restart_count = sum((status.restart_count or 0) for status in statuses)
        #     table.add_row(job.metadata.namespace or "-", job.metadata.name, job.status.phase, str(restart_count))

        console.print(table)
    except Exception as err:
        console.print(f"[bold red]Error accessing Kubernetes:[/bold red] \n\n{err}")
