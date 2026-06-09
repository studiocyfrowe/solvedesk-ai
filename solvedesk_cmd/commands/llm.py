import typer

from solvedesk_cmd.application.dependencies import get_env_builder
from solvedesk_cmd.infrastructure.dependencies import get_ollama_generator

app = typer.Typer(name="llm")

@app.command(
    "init",
    help="Configure Ollama LLM connection settings"
)
def llm_init():
    typer.echo("\nSolveDesk LLM configuration\n")

    llm_host = typer.prompt(
        "LLM host URL",
        default="http://localhost:11434"
    ).rstrip("/")

    llm_model = typer.prompt(
        "LLM model name",
        default="llama3"
    )

    typer.echo("\nChecking Ollama connection...")

    ollama_generator = get_ollama_generator()
    connection = ollama_generator.check_ollama_connection()

    if not connection["success"]:
        typer.echo("\nCannot connect to Ollama host")
        typer.echo(f"Host: {llm_host}")
        typer.echo(f"Error: {connection['error']}")
        raise typer.Exit(code=1)

    typer.echo("Ollama connection OK")

    has_model = ollama_generator.check_ollama_connection()

    if not has_model:
        typer.echo("\nModel not found in Ollama")
        typer.echo(f"Model: {llm_model}")
        typer.echo("\nInstall it with:")
        typer.echo(f"ollama pull {llm_model}")
        raise typer.Exit(code=1)

    typer.echo("Ollama model OK")
    
    env_builder = get_env_builder()

    env_builder.update_env_variable(
        key="LLM_MODEL",
        value=llm_model
    )

    env_builder.update_env_variable(
        key="LLM_HOST",
        value=llm_host
    )

    typer.echo("\nOllama configuration saved\n")

    typer.echo(f"LLM_HOST={llm_host}")
    typer.echo(f"LLM_MODEL={llm_model}")

    typer.echo("\nNext command:")
    typer.echo("solvedesk run:app\n")


if __name__ == "__main__":
    app()