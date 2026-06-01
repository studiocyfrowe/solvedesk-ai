from enum import Enum

class ImportStatus(Enum):
    LOADED = "DATA HAS BEEN LOADED"
    ERROR = "LOADING ERROR"
    WARNING = "WARNING ERROR"