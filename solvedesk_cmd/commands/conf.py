import os
import typer

from dotenv import load_dotenv

from application.dependencies import get_env_builder
from infrastructure.dependencies import get_installer

load_dotenv()

app = typer.Typer(help="config")

@app.command(
    "init",
    help="Initialize SolveDesk environment - install python libraries and configure project"
)
def init_solvedesk(
    project_name: str = typer.Argument(
        ...,
        help="Project name"
    ),
    project_desc: str = typer.Option(
        ...,
        "--desc",
        "--project-desc",
        help="Project description"
    )
):
    typer.echo("\nSolveDesk initialization started...\n")
    installer = get_installer()

    requirements_installed = os.getenv(
        "REQUIREMENTS_INSTALLED",
        "false"
    ).lower() == "true"
    
    env_builder = get_env_builder()

    if requirements_installed:
        typer.echo("Requirements already installed\n")

    else:
        typer.echo("Checking Python dependencies...\n")

        if_installed = installer.install_requirements()
        
        env_builder.update_env_variable(
            key="REQUIREMENTS_INSTALLED",
            value=str(if_installed).lower()
        )

        if not if_installed:
            typer.echo("Requirements installation failed")
            raise typer.Exit(code=1)

    env_builder.update_env_variable(
        key="PROJECT_NAME",
        value=project_name
    )

    env_builder.update_env_variable(
        key="PROJECT_DESCRIPTION",
        value=project_desc
    )

    typer.echo(".env created / updated")

    typer.echo("\nSolveDesk environment initialized successfully\n")

    typer.echo("Next command:")
    typer.echo("solvedesk db init\n")

    typer.echo("Available commands:")
    typer.echo("solvedesk --help\n")


if __name__ == "__main__":
    app()