import secrets, typer
from solvedesk_cmd.application.dependencies import get_env_builder

app = typer.Typer(name="security")

@app.command(
    "token",
    help="Secure your SolveDesk API by configuring JWT authentication"
)
def secure_token(
    secret: str = typer.Option(
        None,
        help="JWT secret. If empty, it will be generated automatically."
    )
):
    if secret is None:
        secret = secrets.token_urlsafe(32)
        
    env_builder = get_env_builder()
    
    env_builder.update_env_variable(
        "AUTH_ENABLED",
        "true"
    )
    
    env_builder.update_env_variable(
        "JWT_SECRET",
        secret
    )

    typer.echo("JWT authentication enabled")
    typer.echo("Saved AUTH_ENABLED=true")
    typer.echo("Saved JWT_SECRET to .env")


if __name__ == "__main__":
    app()