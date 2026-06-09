import typer
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from solvedesk_cmd.application.dependencies import get_env_builder

load_dotenv()

app = typer.Typer(help="config")

REPO_DIR : str = 'https://github.com/studiocyfrowe/solvedesk-ai'

@app.command(
    "init",
    help="Create a new SolveDesk project"
)
def init_solvedesk():

    typer.secho(
        "\n[INFO] SolveDesk AI - Project Generator\n",
        fg=typer.colors.CYAN,
        bold=True
    )

    project_name = typer.prompt(
        "[INPUT] Project name"
    )

    project_desc = typer.prompt(
        "[INPUT] Project description",
        default="Local RAG knowledge base"
    )

    repo_url = REPO_DIR

    typer.echo("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    typer.echo("[INFO] Configuration")
    typer.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    typer.echo(f"[DETAILS] Name        : {project_name}")
    typer.echo(f"[DETAILS] Description : {project_desc}")
    typer.echo(f"[DETAILS] Template    : {repo_url}")

    if not typer.confirm(
        "\n[CONFIRM] Continue project creation?"
    ):
        raise typer.Exit()

    typer.echo("\n[STATUS] Downloading template...\n")

    target_dir = Path.cwd() / project_name

    result = subprocess.run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            repo_url,
            str(target_dir)
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        typer.secho(
            "\n[STATUS] Project creation failed\n",
            fg=typer.colors.RED
        )

        typer.echo(result.stderr)

        raise typer.Exit(code=1)

    env_builder = get_env_builder()

    env_builder.update_env_variable(
        key="PROJECT_NAME",
        value=project_name
    )

    env_builder.update_env_variable(
        key="PROJECT_DESCRIPTION",
        value=project_desc
    )

    typer.secho(
        "\n[STATUS] Project created successfully\n",
        fg=typer.colors.GREEN,
        bold=True
    )

    typer.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    typer.echo("[INFO] Project information")
    typer.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    typer.echo(f"[DETAILS] Location : {target_dir}")
    typer.echo(f"[DETAILS] Name     : {project_name}")
    typer.echo(f"[DETAILS] Description : {project_desc}")

    typer.echo("\nNext steps:\n")

    typer.secho(
        f"cd {project_name}",
        fg=typer.colors.YELLOW
    )

    typer.secho(
        "solvedesk db init",
        fg=typer.colors.YELLOW
    )

    typer.secho(
        "solvedesk llm init",
        fg=typer.colors.YELLOW
    )

    typer.secho(
        "solvedesk run:app",
        fg=typer.colors.YELLOW
    )

    typer.echo("\nHappy coding!\n")


if __name__ == "__main__":
    app()