from abc import ABC, abstractmethod

class AuthProvider(ABC):
    @abstractmethod
    def verify(self, token: str) -> dict:
        pass