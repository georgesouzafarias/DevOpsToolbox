from pathlib import Path
from typing import Annotated

import typer
import yaml as pyyaml
from rich.console import Console
from rich.table import Table

app = typer.Typer(no_args_is_help=True)
console = Console()


def validate_yaml_file(file_path: Path) -> tuple[bool, str]:
    """Validate a single YAML file and return (is_valid, error_message)."""
    try:
        with open(file_path) as f:
            list(pyyaml.safe_load_all(f))
        return True, ""
    except pyyaml.YAMLError as e:
        if hasattr(e, "problem_mark"):
            mark = e.problem_mark
            return False, f"Line {mark.line + 1}, Column {mark.column + 1}: {e.problem}"
        return False, str(e)
    except Exception as e:
        return False, str(e)


@app.command()
def yaml(
    file: Annotated[Path, typer.Option("--file", "-f", exists=True, file_okay=True, dir_okay=False, resolve_path=True)] = None,
    directory: Annotated[Path, typer.Option("--directory", "-d", exists=True, file_okay=False, dir_okay=True, resolve_path=True)] = None,
):
    """Validate YAML files for syntax errors."""
    if file is None and directory is None:
        console.print("[red]Error: You must provide either a file or a directory.[/red]")
        raise typer.Exit(1)

    if file and directory:
        console.print("[red]Error: Provide either a file or a directory, not both.[/red]")
        raise typer.Exit(1)

    files_to_validate = []
    if file:
        files_to_validate.append(file)
    elif directory:
        files_to_validate.extend(directory.glob("**/*.yaml"))
        files_to_validate.extend(directory.glob("**/*.yml"))

    if not files_to_validate:
        console.print("[yellow]No YAML files found.[/yellow]")
        raise typer.Exit(0)

    table = Table(title="YAML Validation Results")
    table.add_column("File", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Error", style="red")

    valid_count = 0
    invalid_count = 0

    for yaml_file in sorted(files_to_validate):
        is_valid, error = validate_yaml_file(yaml_file)
        if is_valid:
            valid_count += 1
            table.add_row(str(yaml_file), "[green]Valid[/green]", "")
        else:
            invalid_count += 1
            table.add_row(str(yaml_file), "[red]Invalid[/red]", error)

    console.print(table)
    console.print(f"\n[bold]Summary:[/bold] {valid_count} valid, {invalid_count} invalid")

    if invalid_count > 0:
        raise typer.Exit(1)
