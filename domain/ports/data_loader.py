from abc import ABC, abstractmethod

class DataLoader(ABC):
    @abstractmethod
    def load(self, url: str) -> list[dict]:
        pass