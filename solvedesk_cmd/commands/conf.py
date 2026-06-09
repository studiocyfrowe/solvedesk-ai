import os
import typer
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from solvedesk_cmd.application.dependencies import get_env_builder
from solvedesk_cmd.infrastructure.dependencies import get_installer

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
    repo_url = 'https://github.com/studiocyfrowe/solvedesk-ai'
    
    if not repo_url:
        typer.echo(
            "Repository URL not configured in database"
        )
        raise typer.Exit(code=1)

    typer.echo("\nSolveDesk initialization started...\n")

    env_builder = get_env_builder()

    if repo_url:
        target_dir = repo_dir or project_name

        if Path(target_dir).exists():
            typer.echo(f"Repository directory already exists: {target_dir}")
        else:
            typer.echo(f"\nCloning repository from {repo_url}...\n")

            result = subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    repo_url,
                    target_dir
                ],
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