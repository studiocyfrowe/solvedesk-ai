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
        id_field = RecordFactory.find_field(
            record,
            ["id", "unnamed: 0", "index"]
        )

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
        
    @staticmethod
    def to_helpdesk(record: dict) -> dict | None:
        title_field = RecordFactory.find_field(
            record,
            ["issue_name", "title", "name", "temat", "problem", "subject"]
        )

        symptoms_field = RecordFactory.find_field(
            record,
            ["issue_symptoms", "symptoms", "sympthoms", "description", "opis", "body"]
        )

        solution_field = RecordFactory.find_field(
            record,
            ["issue_solution", "solution", "answer", "odpowiedz", "odpowiedź", "resolution"]
        )

        if not title_field and not symptoms_field:
            return None

        title = record.get(title_field) if title_field else ""
        symptoms = record.get(symptoms_field) if symptoms_field else ""
        solution = record.get(solution_field) if solution_field else ""

        question_parts = []

        if title:
            question_parts.append(str(title))

        if symptoms:
            question_parts.append(str(symptoms))

        question = " - ".join(question_parts)

        return {
            "id": RecordFactory.get_id(record),
            "question": question,
            "answer": str(solution or "")
        }