import typer
from rich import print
from devopstoolbox import generate

from devopstoolbox.k8s import certificates, pods, services

__version__ = "DevOpsToolbox v0.1.0"

app = typer.Typer(no_args_is_help=True)
k8s_app = typer.Typer(no_args_is_help=True)

app.add_typer(k8s_app, name="k8s")
app.add_typer(generate.app, name="generate", help="Generate utilities")

k8s_app.add_typer(pods.app, name="pods", help="Manager Pods")
k8s_app.add_typer(services.app, name="services", help="Manager Services")
k8s_app.add_typer(certificates.app, name="certificates", help="Manager Certificates")


@app.command()
def version():
    """Show tool version"""
    print(__version__)


if __name__ == "__main__":
    app()
