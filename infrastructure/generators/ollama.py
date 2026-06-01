import requests

class OllamaGenerator():
    def __init__(
        self, 
        llm_host: str,
        llm_model: str
    ):
        self.llm_host = llm_host
        self.llm_model = llm_model
    
    def check_ollama_connection(self) -> dict:
        try:
            response = requests.get(
                f"{self.llm_host}/api/tags",
                timeout=5
            )

            response.raise_for_status()

            return {
                "success": True,
                "data": response.json()
            }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }

    def check_ollama_model(self, models_data: dict) -> bool:
        models = models_data.get("models", [])

        model_names = [
            model.get("name")
            for model in models
        ]

        return (
            self.llm_model in model_names
            or f"{self.llm_model}:latest" in model_names
        )