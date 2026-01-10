import typer
from rich import print

from devopstoolbox.k8s import certificates, jobs, pods, services
from devopstoolbox.misc import base64, generate, validate

__version__ = "DevOpsToolbox v0.1.0"

app = typer.Typer(no_args_is_help=True)
k8s_app = typer.Typer(no_args_is_help=True)
misc_app = typer.Typer(no_args_is_help=True)

app.add_typer(k8s_app, name="k8s", help="Kubernetes utilities")
app.add_typer(misc_app, name="misc", help="Utilities")

misc_app.add_typer(generate.app, name="generate", help="Generate utilities")
misc_app.add_typer(validate.app, name="validate", help="tools for validation files")
misc_app.add_typer(base64.app, name="base64", help="Encode or decode string to base64")

k8s_app.add_typer(pods.app, name="pods", help="Manager Pods")
k8s_app.add_typer(jobs.app, name="jobs", help="Manager Jobs")
k8s_app.add_typer(services.app, name="services", help="Manager Services")
k8s_app.add_typer(certificates.app, name="certificates", help="Manager Certificates")


@app.command()
def version():
    """Show tool version"""
    print(__version__)


if __name__ == "__main__":
    app()
