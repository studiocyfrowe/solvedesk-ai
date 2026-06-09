from pathlib import Path
from dotenv import load_dotenv
from solvedesk_cmd.domain.models.env_config import EnvConfig
from solvedesk_cmd.domain.ports.env_builder import EnvBuilder
import typer

class EnvBuilder(EnvBuilder):
    def __init__(
        self, 
        env_file: str = ".env"
    ):
        self.env_path = Path(env_file)
        
    def load_env(self):
        load_dotenv(dotenv_path=self.env_path)

    def create_env_content(
        self,
        model_local_path: Path | str, 
        chroma_dir: Path | str, 
        collection_name: str
    ) -> str:
        env_content = f"""MODEL_PATH={model_local_path}
            CHROMA_DIR={chroma_dir}
            COLLECTION_NAME={collection_name}
        """
        return env_content
    
    def create_env_file(self) -> bool:
        if self.env_path.exists():
            typer.echo("Plik .env już istnieje — pominięto tworzenie")
            return False

        env_content = self.create_env_content()

        self.env_path.write_text(
            env_content,
            encoding="utf-8"
        )

        typer.echo("Utworzono plik .env")

        return True

    def get_env_config(
        self,
        model_local_path: Path | str, 
        chroma_dir: Path | str, 
        collection_name: str
    ) -> EnvConfig:
        return EnvConfig(
            model_local_path=model_local_path,
            chroma_dir=chroma_dir,
            collection_name=collection_name
        )
        
    def update_env_variable(
        self,
        key: str,
        value: str
    ) -> None:
        env_data = {}

        if self.env_path.exists():
            with self.env_path.open("r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()

                    if not line or line.startswith("#"):
                        continue

                    if "=" in line:
                        env_key, env_value = line.split("=", 1)
                        env_data[env_key] = env_value

        env_data[key] = value

        with self.env_path.open("w", encoding="utf-8") as file:
            for env_key, env_value in env_data.items():
                file.write(f"{env_key}={env_value}\n")

    def execute(self) -> EnvConfig:
        self.create_env_file()
        self.load_env()

        