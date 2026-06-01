import typer

from solvedesk_cmd.commands.conf import app as conf_cmd
from solvedesk_cmd.commands.db import app as db_cmd
from solvedesk_cmd.commands.sync import app as sync_cmd
from solvedesk_cmd.commands.llm import app as llm_cmd
from solvedesk_cmd.commands.data import app as data_cmd
from solvedesk_cmd.commands.security import app as secure_cmd
from solvedesk_cmd.commands.main import app as main_cmd

app = typer.Typer(name="solvedesk")

app.add_typer(conf_cmd, name="conf", help="SolveDesk configuration")
app.add_typer(db_cmd, name="db", help="Vector Database configuration")
app.add_typer(sync_cmd, name="sync", help="Data Loader Configuration")
app.add_typer(llm_cmd, name="llm", help="LLM Configuration")
app.add_typer(data_cmd, name="data", help="Data & Embeddings analyse")
app.add_typer(secure_cmd, name="security", help="Configure Security by JWT")
app.add_typer(main_cmd, name="main", help="SolveDesk API Launcher")

if __name__ == "__main__":
    app()