import json
import typer
from pathlib import Path
from rich import print

# Initialize the sub-app
app = typer.Typer(no_args_is_help=True)

def check_single_file(file_path: Path):
    """
    Core logic to validate JSON syntax and report errors with line/column.
    """
    try:
        with open(file_path, "r") as file:
            json.load(file)
        print(f"[green]✅ Valid:[/green] {file_path}")
    except json.JSONDecodeError as err:
        print(f"[red]❌ Invalid:[/red] {file_path}")
        print(f"   [bold]Error:[/bold] {err.msg}")
        print(f"   [bold]Location:[/bold] Line {err.lineno}, Column {err.colno}")
        # Return False so the main command knows at least one file failed
        return False
    except Exception as e:
        print(f"[yellow]⚠️ Could not read {file_path}:[/yellow] {e}")
        return False
    return True

@app.command("json")
def validate_json(
    path: Path = typer.Argument(..., help="The path to the JSON file or directory"),
    directory: bool = typer.Option(False, "--dir", help="Scan all JSON files in the directory")
):
    """
    Validate JSON syntax for a specific file or all files in a directory.
    """
    success = True

    if directory:
        if not path.is_dir():
            print(f"[red]Error:[/red] '{path}' is not a directory. Remove --dir or provide a folder.")
            raise typer.Exit(code=1)
        
        # Find all .json files (case-insensitive)
        files = list(path.glob("**/*.json"))
        if not files:
            print(f"[yellow]No JSON files found in {path}[/yellow]")
            return

        print(f"Scanning directory: [bold]{path}[/bold] ({len(files)} files found)\n")
        for f in files:
            if not check_single_file(f):
                success = False
    else:
        if not path.is_file():
            print(f"[red]Error:[/red] File '{path}' not found or is not a file.")
            raise typer.Exit(code=1)
        success = check_single_file(path)

    # Exit with error code 1 if any file failed, so CI/CD pipelines can detect it
    if not success:
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
  
                 
                 

