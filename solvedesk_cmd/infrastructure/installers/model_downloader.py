import typer
import subprocess
from pathlib import Path
from rich.progress import Progress

class ModelDownloader():
    def __init__(self,
            model_repo: Path | str,
            models_dir: Path | str):
        self.model_repo = str(model_repo)
        self.models_dir = str(models_dir)

    def combine_url(self):
        if isinstance(self.model_repo, tuple):
            self.model_repo = self.model_repo[0]

        models_path = Path(self.models_dir)

        models_path.mkdir(
            parents=True,
            exist_ok=True
        )

        repo_name = self.model_repo.rstrip("/").split("/")[-1]

        model_local_path = models_path / repo_name
        config_file = model_local_path / "config.json"

        return config_file, model_local_path

    def execute(self):
        config_file, model_local_path = self.combine_url()

        if config_file.exists():
            typer.echo("Embedding model already exists — skipping download")
            return model_local_path

        if model_local_path.exists():
            typer.echo("Model directory already exists, but config file is missing")
            typer.echo(f"Path: {model_local_path}")
            raise typer.Exit(code=1)

        typer.echo("Downloading embedding model...")

        result = subprocess.run(
            [
                "git",
                "-c",
                "http.version=HTTP/1.1",
                "clone",
                "--depth",
                "1",
                self.model_repo,
                str(model_local_path)
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            typer.echo("Model download failed")
            typer.echo(result.stderr)
            raise typer.Exit(code=1)

        typer.echo(f"Model downloaded: {model_local_path}")

        return model_local_path