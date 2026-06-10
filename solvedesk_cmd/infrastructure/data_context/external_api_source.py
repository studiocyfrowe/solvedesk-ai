import requests
from solvedesk_cmd.domain.ports.external_data_source import ExternalDataSource

class ExternalApiSource(ExternalDataSource):
    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token

    def fetch(self) -> list[dict]:
        headers = {
            "Accept": "application/json"
        }

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        response = requests.get(
            self.url,
            headers=headers,
            timeout=10,
            verify=False
        )

        response.raise_for_status()

        data = response.json()

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            for key in ["data", "items", "records", "results", "issues"]:
                value = data.get(key)

                if isinstance(value, list):
                    return value

        raise ValueError(
            f"API returned non-list JSON. Keys: {list(data.keys()) if isinstance(data, dict) else type(data)}"
        )