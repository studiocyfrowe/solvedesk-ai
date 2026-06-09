from abc import ABC, abstractmethod
from solvedesk_cmd.domain.models.env_config import EnvConfig

class EnvBuilder(ABC):
    @abstractmethod
    def create_env_content(self) -> str:
        pass
    
    @abstractmethod
    def create_env_file(self) -> bool:
        pass
    
    @abstractmethod
    def load_env(self):
        pass
    
    @abstractmethod
    def get_env_config(self) -> EnvConfig:
        pass
    
    @abstractmethod
    def update_env_variable(
        key: str,
        value: str,
        env_file: str = ".env"
    ) -> None:
        pass
    
    @abstractmethod
    def execute(self) -> EnvConfig:
        pass