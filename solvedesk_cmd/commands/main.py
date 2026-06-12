import typer
import subprocess

app = typer.Typer(name="main")

@app.command(
    "run",
    help="Run your SolveDesk API on localhost:8000"
)
def run_app(
    host: str = typer.Option(
        "127.0.0.1",
        help="Host address"
    ),
    port: int = typer.Option(
        8080,
        help="Application port"
    ),
    reload: bool = typer.Option(
        True,
        help="Enable auto reload"
    )
):
    typer.echo("\nStarting SolveDesk API...\n")

    command = [
        "uvicorn",
        "main:app",
        "--host",
        host,
        "--port",
        str(port)
    ]

    if reload:
        command.append("--reload")

    subprocess.run(command)

if __name__ == "__main__":
    app()