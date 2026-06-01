import re
from typing import Any


class DataPreprocessor:
    def __init__(
        self,
        records: list[dict],
        required_fields: list[str],
        text_fields: list[str],
        min_words: int = 3
    ):
        self.records = records
        self.required_fields = required_fields
        self.text_fields = text_fields
        self.min_words = min_words

    def execute(self) -> list[dict]:
        cleaned_records = self.clean_records()
        normalized_records = self.normalize_records(cleaned_records)
        non_empty_records = self.remove_empty_records(normalized_records)
        valid_records = self.validate_records(non_empty_records)

        return valid_records

    def clean_records(self) -> list[dict]:
        cleaned_records = []

        for record in self.records:
            cleaned_record = {}

            for key, value in record.items():
                if isinstance(value, str):
                    cleaned_record[key] = self.clean_text(value)
                else:
                    cleaned_record[key] = value

            cleaned_records.append(cleaned_record)

        return cleaned_records

    def clean_text(self, text: Any) -> str:
        if text is None:
            return ""

        text = str(text)

        text = text.replace("\n", " ")
        text = text.replace("\r", " ")
        text = text.replace("\t", " ")

        text = re.sub(r"[^\w\sąćęłńóśźżĄĆĘŁŃÓŚŹŻ.,!?;:()/-]", " ", text)
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def normalize_records(self, records: list[dict]) -> list[dict]:
        normalized_records = []

        for record in records:
            normalized_record = {}

            for key, value in record.items():
                normalized_key = self.normalize_key(key)
                normalized_record[normalized_key] = value

            normalized_records.append(normalized_record)

        return normalized_records

    def normalize_key(self, key: str) -> str:
        key = str(key).strip().lower()

        replacements = {
            "ą": "a",
            "ć": "c",
            "ę": "e",
            "ł": "l",
            "ń": "n",
            "ó": "o",
            "ś": "s",
            "ż": "z",
            "ź": "z",
            " ": "_",
            "-": "_"
        }

        for old, new in replacements.items():
            key = key.replace(old, new)

        key = re.sub(r"_+", "_", key)

        return key.strip("_")

    def remove_empty_records(self, records: list[dict]) -> list[dict]:
        non_empty_records = []

        for record in records:
            if self.is_empty_record(record):
                continue

            non_empty_records.append(record)

        return non_empty_records

    def is_empty_record(self, record: dict) -> bool:
        for value in record.values():
            if value is None:
                continue

            if str(value).strip() != "":
                return False

        return True

    def validate_records(self, records: list[dict]) -> list[dict]:
        valid_records = []

        for record in records:
            if not self.has_required_fields(record):
                continue

            if not self.is_valid_for_embedding(record):
                continue

            valid_records.append(record)

        return valid_records

    def has_required_fields(self, record: dict) -> bool:
        for field in self.required_fields:
            if field not in record:
                return False

            if record[field] is None:
                return False

            if str(record[field]).strip() == "":
                return False

        return True

    def is_valid_for_embedding(self, record: dict) -> bool:
        text = self.join_text_fields(record)

        words = text.split()

        if len(words) < self.min_words:
            return False

        return True

    def join_text_fields(self, record: dict) -> str:
        values = []

        for field in self.text_fields:
            value = record.get(field, "")

            if value is None:
                continue

            value = str(value).strip()

            if value:
                values.append(value)

        return " ".join(values)