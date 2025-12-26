import secrets
import string

import typer
from rich import print

app = typer.Typer(no_args_is_help=True)


@app.command()
def password(length: int = 16):
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    pwd = "".join(secrets.choice(alphabet) for _ in range(length))
    print(pwd)


if __name__ == "__main__":
    app()
