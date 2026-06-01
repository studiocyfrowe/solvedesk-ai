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

        else:
            if not model_local_path.exists():
                typer.echo("Downloading embedding model...")
                with Progress() as progress:

                    task = progress.add_task(
                        "[green]Downloading model...",
                        total=None
                    )

                    process = subprocess.Popen(
                        [
                            "git",
                            "clone",
                            self.model_repo,
                            model_local_path
                        ],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )

                    while process.poll() is None:
                        progress.update(task, advance=1)

                    if process.returncode != 0:
                        raise Exception("Model download failed")

                typer.echo(f"Model downloaded: {model_local_path}")

            else:
                typer.echo("Model already exists — skipping download")