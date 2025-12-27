from typing import Annotated

import typer
from kubernetes.client import CustomObjectsApi
from rich.console import Console
from rich.table import Table

from devopstoolbox.k8s import utils

app = typer.Typer(no_args_is_help=True)
console = Console()
custom_api = CustomObjectsApi()


@app.command()
def list(namespace: Annotated[str, typer.Option("--namespace", "-n")] = None, all_namespaces: Annotated[bool, typer.Option("--all-namespaces", "-A")] = False):
    """List cert-manager certificates with renewal time and status."""
    namespace = namespace or utils.get_current_namespace()
    scope = "all namespaces" if all_namespaces else f"namespace {namespace}"
    console.print(f"[bold blue]Listing certificates resources in {scope}...[/bold blue]")

    try:
        if all_namespaces:
            certificates = custom_api.list_cluster_custom_object(group="cert-manager.io", version="v1", plural="certificates")
        else:
            certificates = custom_api.list_namespaced_custom_object(group="cert-manager.io", version="v1", namespace=namespace, plural="certificates")

        table = Table(title=f"List Certificates in {scope}")
        table.add_column("Namespace", style="cyan", justify="center")
        table.add_column("Name", style="cyan", justify="center")
        table.add_column("Renewal Time", style="green", justify="center")
        table.add_column("Status", style="green", justify="center")

        for certificate in certificates.get("items", []):
            status = certificate.get("status", {})
            renewal_time = status.get("renewalTime", "-")
            conditions = status.get("conditions", [{}])
            condition_type = conditions[0].get("type", "-") if conditions else "-"
            table.add_row(namespace, certificate["metadata"]["name"], renewal_time, condition_type)
        console.print(table)
    except Exception as e:
        print("Error accessing Cert API. Ensure Certificate Server is installed.")
        print(f"Details: {e}")
        return


@app.command()
def not_ready(namespace: Annotated[str, typer.Option("--namespace", "-n")] = None, all_namespaces: Annotated[bool, typer.Option("--all-namespaces", "-A")] = False):
    """List certificates that are not in Ready state."""
    namespace = namespace or utils.get_current_namespace()
    scope = "all namespaces" if all_namespaces else f"namespace {namespace}"
    console.print(f"[bold blue]Listing certificates resources in {scope}...[/bold blue]")

    try:
        if all_namespaces:
            certificates = custom_api.list_cluster_custom_object(group="cert-manager.io", version="v1", plural="certificates")
        else:
            certificates = custom_api.list_namespaced_custom_object(group="cert-manager.io", version="v1", namespace=namespace, plural="certificates")

        table = Table(title=f"List Certificates in {scope}")
        table.add_column("Namespace", style="cyan", justify="center")
        table.add_column("Name", style="cyan", justify="center")
        table.add_column("Renewal Time", style="green", justify="center")
        table.add_column("Status", style="green", justify="center")

        for certificate in certificates.get("items", []):
            status = certificate.get("status", {})
            renewal_time = status.get("renewalTime", "-")
            conditions = status.get("conditions", [{}])
            condition_type = conditions[0].get("type", "-") if conditions else "-"
            if condition_type != "Ready":
                table.add_row(namespace, certificate["metadata"]["name"], renewal_time, condition_type)
        console.print(table)
    except Exception as e:
        print("Error accessing Cert API. Ensure Certificate Server is installed.")
        print(f"Details: {e}")
        return
