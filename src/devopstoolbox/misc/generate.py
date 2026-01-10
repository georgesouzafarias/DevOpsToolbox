import secrets
import string
from typing import Annotated

import typer
from rich import print

app = typer.Typer()


@app.callback(invoke_without_command=True)
def password(length: Annotated[int, typer.Option("--length", "-l", help="Password length")] = 16):
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    pwd = "".join(secrets.choice(alphabet) for _ in range(length))
    print(pwd)
