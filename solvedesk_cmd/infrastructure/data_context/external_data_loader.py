import requests
from solvedesk_cmd.domain.ports.data_loader import DataLoader

class ExternalDataLoader(DataLoader):
    def __init__(self):
        super().__init__()

    def load(self, url):
        return super().load(url)