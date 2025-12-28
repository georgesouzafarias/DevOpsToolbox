import json
import pathlib

import rich
import typer

app = typer.Typer(no_args_is_help=True)


@app.command("json")
def validate_json(path: pathlib.Path, recursive: bool = typer.Option(False, help="Scan directories recursively for JSON files")):
    has_err = False
    total_files = 0
    valid_files = 0
    invalid_files = 0
    if not path.exists():
        rich.print(f"[bold red]✖ Path not found:[/bold red] [white]{path}[/white]")
        raise typer.Exit(1)

    if path.is_file():
        files = [path]

    else:
        pattern = "**/*.json" if recursive else "*.json"
        files = list(path.glob(pattern))

    if not files:
        rich.print(f"[yellow]⚠ No JSON files found in {path}[/yellow]")
        raise typer.Exit(0)

    for f in files:
        total_files = total_files + 1
        try:
            json.loads(f.read_text())
            rich.print(f"[bold green]✔ Valid JSON:[/bold green] [white]{f}[/white]")
            valid_files = valid_files + 1

        except json.JSONDecodeError as e:
            has_err = True
            rich.print(f"[bold red]✖ Invalid JSON:[/bold red] [white]{f}[/white]")
            rich.print(f"[red]  → Error at line [bold]{e.lineno}[/bold], column [bold]{e.colno}[/bold]: {e.msg}[/red]")
            invalid_files = invalid_files + 1
    rich.print("\n[bold blue]Summary:[/bold blue]")
    rich.print(f"  Total files checked: [white]{total_files}[/white]")
    rich.print(f"  Invalid files: [red]{invalid_files}[/red]")
    rich.print(f"  Valid files: [green]{total_files - invalid_files}[/green]")
    if has_err:
        raise typer.Exit(1)