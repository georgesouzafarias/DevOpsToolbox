import base64
from typing import Annotated

import typer
from rich import print

app = typer.Typer(no_args_is_help=True)


@app.command()
def encode(encode: Annotated[str, typer.Option("--encode", "-e")]):
    """Encode String to Base64"""
    encoded = base64.b64encode(encode)
    print(encoded)
