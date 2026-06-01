from pathlib import Path
import typer
import subprocess

def install_requirements() -> bool:
    requirements = Path("requirements2.txt")

    if not requirements.exists():
        typer.echo("requirements.txt not found\n")
        return False

    typer.echo("Installing Python dependencies...\n")

    try:

        result = subprocess.run(
            [
                "pip",
                "install",
                "-r",
                "requirements2.txt"
            ],
            check=True,
            text=True,
            capture_output=True
        )

        typer.echo(result.stdout)

        typer.echo(
            "\nDependencies installed successfully\n"
        )

        return True

    except subprocess.CalledProcessError as e:

        typer.echo("\nPIP INSTALL ERROR\n")

        typer.echo("STDOUT:\n")
        typer.echo(e.stdout)

        typer.echo("\nSTDERR:\n")
        typer.echo(e.stderr)

        return False