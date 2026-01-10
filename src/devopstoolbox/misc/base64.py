import base64 as b64
import binascii
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
    options_count = sum(1 for opt in [encode, decode, file_path] if opt is not None)
    if options_count > 1:
        print("[red]Error: Provide only one of --encode, --decode, or --file.[/red]")
        raise typer.Exit(1)

    if file_path:
        try:
            with open(file_path) as f:
                encoded = b64.b64encode(f.read().encode()).decode()
                print(encoded)
        except FileNotFoundError:
            print(f"[red]Error: File not found: {file_path}[/red]")
            raise typer.Exit(1)
        except PermissionError:
            print(f"[red]Error: Permission denied: {file_path}[/red]")
            raise typer.Exit(1)
        except IsADirectoryError:
            print(f"[red]Error: Path is a directory: {file_path}[/red]")
            raise typer.Exit(1)
    elif encode:
        encoded = b64.b64encode(encode.encode()).decode()
        print(encoded)
    elif decode:
        try:
            decoded = b64.b64decode(decode).decode()
            print(decoded)
        except binascii.Error:
            print("[red]Error: Invalid base64 string.[/red]")
            raise typer.Exit(1)
        except UnicodeDecodeError:
            print("[red]Error: Decoded content is not valid UTF-8 text.[/red]")
            raise typer.Exit(1)
