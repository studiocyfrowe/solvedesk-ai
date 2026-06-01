import requests
from domain.ports.external_data_source import ExternalDataSource

class ExternalApiSource(ExternalDataSource):
    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token

    def fetch(self) -> list[dict]:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        }
        response = requests.get(self.url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list):
            raise ValueError("API returned non-list JSON")
        return data