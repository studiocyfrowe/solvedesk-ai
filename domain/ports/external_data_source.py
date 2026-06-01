from abc import ABC, abstractmethod

class ExternalDataSource(ABC):
    @abstractmethod
    def fetch(self) -> list[dict]:
        pass