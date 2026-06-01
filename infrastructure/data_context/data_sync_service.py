import json
import pandas as pd
from io import BytesIO, StringIO
from application.dependencies import get_record_factory, get_metadata_factory

class DataSyncService:
    def __init__(self, source, embedder, vector_store):
        self.source = source
        self.embedder = embedder
        self.vector_store = vector_store

    def sync(
        self,
        type: str = "know-base",
        content: bytes | None = None,
        extension: str | None = None
    ):

        if content and extension:
            issues = self._load_from_file(content, extension)
        else:
            issues = self.source.fetch()

        processed = 0

        for issue in issues:
            match type:
                case "know-base" | "faq":
                    faq = get_record_factory.to_faq(issue)

                    if faq is None:
                        print(f"Pominięto rekord bez pytania: {issue}")
                        continue

                    doc_id = faq["id"]

                    if doc_id is None:
                        print(f"Pominięto rekord bez ID: {issue}")
                        continue

                    question = faq["question"]
                    answer = faq["answer"]

                    if not question.strip():
                        print(f"Puste pytanie dla ID: {doc_id}")
                        continue

                    text = f"""
                    Pytanie: {question}
                    Odpowiedź: {answer}
                    """.strip()

                    emb = self.embedder.embed(text)
                    metadata = get_metadata_factory.create(issue)

                    self.vector_store.add_new(
                        doc_id=doc_id,
                        embedding=emb,
                        document=text,
                        metadata=metadata
                    )

                    processed += 1

                case _:
                    print(f"Nieznany typ danych: {type}")
                    continue

        return processed

    def _load_from_file(self, content: bytes, extension: str) -> list[dict]:
        extension = extension.lower()

        if extension == ".json":
            data = json.loads(content.decode("utf-8"))

            if isinstance(data, dict):
                return [data]

            return data

        if extension == ".csv":
            text = content.decode("utf-8")
            df = pd.read_csv(StringIO(text))
            return df.to_dict(orient="records")

        if extension in [".xlsx", ".xls"]:
            df = pd.read_excel(BytesIO(content))
            return df.to_dict(orient="records")

        raise ValueError(f"Nieobsługiwane rozszerzenie pliku: {extension}")