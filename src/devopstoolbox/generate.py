import secrets
import string
import typer
from rich import print

app = typer.Typer(no_args_is_help=True)


@app.command()
def password(length: int = 16):
    # Generates a random cryptographic password of specified length, if not specified then by default it is 16
    alphabet = string.ascii_letters + string.digits + string.punctuation #combines all the alphabets,digits and special characters
    pwd = "".join(secrets.choice(alphabet) for _ in range(length)) #creates a random password 
    print(pwd)
if __name__ == "__main__":
    password()