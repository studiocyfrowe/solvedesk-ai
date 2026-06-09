import os
import typer
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from application.dependencies import get_env_builder
from infrastructure.dependencies import get_installer, get_config_manager

load_dotenv()

app = typer.Typer(help="config")

@app.command(
    "init",
    help="Initialize SolveDesk environment - install python libraries and configure project"
)
def init_solvedesk(
    project_name: str = typer.Argument(..., help="Project name"),
    project_desc: str = typer.Option(
        ...,
        "--desc",
        "--project-desc",
        help="Project description"
    ),
    repo_dir: str = typer.Option(
        None,
        "--repo-dir",
        help="Target directory for cloned repository"
    )
):
    config_manager = get_config_manager()
    repo_url = config_manager.get_repository_url()
    
    if not repo_url:
        typer.echo(
            "Repository URL not configured in database"
        )
        raise typer.Exit(code=1)

    typer.echo("\nSolveDesk initialization started...\n")

    installer = get_installer()
    env_builder = get_env_builder()

    requirements_installed = os.getenv(
        "REQUIREMENTS_INSTALLED",
        "false"
    ).lower() == "true"

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

    if repo_url:
        target_dir = repo_dir or project_name

        if Path(target_dir).exists():
            typer.echo(f"Repository directory already exists: {target_dir}")
        else:
            typer.echo(f"\nCloning repository from {repo_url}...\n")

            result = subprocess.run(
                ["git", "clone", repo_url, target_dir],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                typer.echo("Git clone failed")
                typer.echo(result.stderr)
                raise typer.Exit(code=1)

            typer.echo(f"Repository cloned to: {target_dir}")

        env_builder.update_env_variable(
            key="REPOSITORY_URL",
            value=repo_url
        )

        env_builder.update_env_variable(
            key="REPOSITORY_DIR",
            value=target_dir
        )

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