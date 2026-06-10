import json
import pandas as pd

from io import BytesIO, StringIO
from solvedesk_cmd.application.dependencies import get_record_factory, get_metadata_factory

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
        type = str(type).strip().lower()

        if content and extension:
            issues = self._load_from_file(content, extension)
        else:
            issues = self.source.fetch()

        processed = 0
        
        record_factory = get_record_factory()
        metadata_factory = get_metadata_factory()

        for issue in issues:
            match type:
                case "know-base" | "faq":
                    record = record_factory.to_faq(issue)

                case "helpdesk":
                    record = record_factory.to_helpdesk(issue)

                case _:
                    print(f"Nieznany typ danych: {type}")
                    continue

            if record is None:
                print(f"Pominięto rekord bez pytania: {issue}")
                continue

            doc_id = record["id"]

            if doc_id is None:
                print(f"Pominięto rekord bez ID: {issue}")
                continue

            question = record["question"]
            answer = record["answer"]

            if not question.strip():
                print(f"Puste pytanie dla ID: {doc_id}")
                continue

            text = f"""
            Pytanie: {question}
            Odpowiedź: {answer}
            """.strip()

            emb = self.embedder.embed(text)
            metadata = metadata_factory.create(issue)

            self.vector_store.add_new(
                doc_id=doc_id,
                embedding=emb,
                document=text,
                metadata=metadata
            )

            processed += 1

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