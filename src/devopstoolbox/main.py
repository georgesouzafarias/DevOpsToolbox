from importlib.metadata import version

import typer
from rich import print

from devopstoolbox.k8s import certificates, jobs, pods, services
from devopstoolbox.misc import base64, generate, validate

try:
    __version__ = f"DevOpsToolbox v{version('devopstoolbox')}"
except Exception:
    __version__ = "DevOpsToolbox (development)"

app = typer.Typer(no_args_is_help=True)
k8s_app = typer.Typer(no_args_is_help=True)
misc_app = typer.Typer(no_args_is_help=True)

app.add_typer(k8s_app, name="k8s", help="Kubernetes utilities")
app.add_typer(misc_app, name="misc", help="Miscellaneous utilities (password generator, base64, validation)")

misc_app.add_typer(generate.app, name="generate", help="Generate secure random passwords")
misc_app.add_typer(validate.app, name="validate", help="Validate YAML and JSON files")
misc_app.add_typer(base64.app, name="base64", help="Encode or decode base64 strings")

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
