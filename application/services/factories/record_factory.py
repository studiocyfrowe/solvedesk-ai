class RecordFactory:
    def __init__(self):
        pass
    
    @staticmethod
    def find_field(record: dict, names: list[str]) -> str | None:
        for key in record.keys():
            normalized_key = key.lower()

            for name in names:
                if name in normalized_key:
                    return key

        return None

    @staticmethod
    def get_id(record: dict) -> str | None:
        id_field = RecordFactory.find_field(record, ["id"])

        if not id_field:
            return None

        value = record.get(id_field)

        if value is None or str(value).strip() == "":
            return None

        return str(value)

    @staticmethod
    def to_faq(record: dict) -> dict | None:
        question_field = RecordFactory.find_field(
            record,
            ["question", "pytanie", "title", "name"]
        )

        answer_field = RecordFactory.find_field(
            record,
            ["answer", "odpowiedz", "odpowiedź", "solution", "response"]
        )

        if not question_field:
            return None

        question = record.get(question_field) or ""
        answer = record.get(answer_field) if answer_field else ""

        return {
            "id": RecordFactory.get_id(record),
            "question": str(question),
            "answer": str(answer or "")
        }