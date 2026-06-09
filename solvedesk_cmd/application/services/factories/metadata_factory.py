class MetadataFactory:
    def __init__(self):
        pass
    
    @staticmethod
    def create(record: dict) -> dict:
        metadata = {}

        for key, value in record.items():
            if value is None:
                metadata[key] = ""
            elif isinstance(value, (str, int, float, bool)):
                metadata[key] = value
            else:
                metadata[key] = str(value)

        return metadata