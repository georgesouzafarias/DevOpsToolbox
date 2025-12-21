import typer
from kubernetes import client, config
from rich.console import Console
from rich.table import Table

app = typer.Typer(no_args_is_help=True)
console = Console()
config.load_kube_config()


@app.command()
def list(namespace: str = "default", all_namespaces: bool = False):
    """List services"""
    scope = "all namespaces" if all_namespaces else f"namespace {namespace}"
    console.print(f"[bold blue]Listing pods in {scope}...[/bold blue]")

    try:
        v1 = client.CoreV1Api()
        services = (
            v1.list_service_for_all_namespaces(watch=False)
            if all_namespaces
            else v1.list_namespaced_service(namespace, watch=False)
        )

        table = Table(title=f"Pods in {scope}")
        table.add_column("Namespace", style="cyan", justify="center")
        table.add_column("Service Name", style="green", justify="center")
        table.add_column("Service IP", justify="center")
        table.add_column("Internal Traffic Policy", justify="center")

        for service in services.items:
            table.add_row(
                service.metadata.namespace or "-",
                service.metadata.name,
                service.spec.type,
                service.spec.internal_traffic_policy or "none",
            )

        console.print(table)
    except Exception as err:
        console.print(f"[bold red]Error accessing Kubernetes:[/bold red] \n\n{err}")
