import base64 as b64
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich import print

app = typer.Typer(no_args_is_help=True)


@app.callback(invoke_without_command=True)
def main(
    encode: Annotated[Optional[str], typer.Option("--encode", "-e", help="String to encode to base64")] = None,
    decode: Annotated[Optional[str], typer.Option("--decode", "-d", help="Base64 string to decode")] = None,
    file_path: Annotated[Optional[Path], typer.Option("--file", "-f", help="File to encode to base64")] = None,
):
    """Encode or decode strings using base64."""
    if file_path:
        try:
            with open(file_path) as f:
                encoded = b64.b64encode(f.read().encode()).decode()
                print(encoded)
        except Exception:
            print("[red]Error: Invalid File Stream[/red]")
            raise typer.Exit(1)
    elif encode:
        encoded = b64.b64encode(encode.encode()).decode()
        print(encoded)
    elif decode:
        try:
            decoded = b64.b64decode(decode).decode()
            print(decoded)
        except Exception:
            print("[red]Error: Invalid base64 string.[/red]")
            raise typer.Exit(1)
