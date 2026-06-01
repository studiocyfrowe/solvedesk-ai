from pathlib import Path
from dotenv import load_dotenv
from domain.models.env_config import EnvConfig
from domain.ports.env_builder import EnvBuilder
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
        env_path = Path(self.env_file)
        env_data = {}

        if env_path.exists():

            for line in env_path.read_text(
                encoding="utf-8"
            ).splitlines():

                if "=" in line:
                    env_key, env_value = line.split("=", 1)
                    env_data[env_key] = env_value

        env_data[key] = value

        env_content = "\n".join(
            f"{env_key}={env_value}"
            for env_key, env_value in env_data.items()
        )

        env_path.write_text(
            env_content + "\n",
            encoding="utf-8"
        )

    def execute(self) -> EnvConfig:
        self.create_env_file()
        self.load_env()

        return self.get_env_config()

        