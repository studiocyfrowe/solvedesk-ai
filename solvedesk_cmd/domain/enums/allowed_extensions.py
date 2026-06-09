from enum import Enum

class AllowedExtensions(Enum):
    EXCEL = ".xlsx",
    JSON = ".json",
    CSV = ".csv"
    
    @classmethod
    def to_list(cls) -> list[str]:
        return [item.value for item in cls]