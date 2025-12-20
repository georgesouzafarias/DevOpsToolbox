import typer
from rich import print

app = typer.Typer()

@app.command()
def hello(name: str = "DevOps"):
    """
    Simple test
    """
    print(f"[bold green]Hello {name}![/bold green] Welcome to your DevOpsToolbox.")

if __name__ == "__main__":
    app()