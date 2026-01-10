import secrets
import string
from typing import Annotated

import typer
from rich import print

app = typer.Typer(no_args_is_help=True)


@app.command()
def password(length: Annotated[int, typer.Option("--length", "-l")] = 16):
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    pwd = "".join(secrets.choice(alphabet) for _ in range(length))
    print(pwd)
