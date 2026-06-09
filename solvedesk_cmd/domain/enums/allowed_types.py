from enum import Enum

class AllowedTypes(Enum):
    KNOW_BASE = "know_base",
    FAQ = "faq",
    HELPDESK = "helpdesk"
    
    @classmethod
    def to_list(cls) -> list[str]:
        return [item.value for item in cls]