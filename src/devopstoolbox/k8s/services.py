import typer
from rich.console import Console

app = typer.Typer(no_args_is_help=True)
console = Console()

@app.command()
def list_services(namespace: str = "default"):
    """
    List all Services
    """
    console.print(f"[Listing service in {namespace}...")