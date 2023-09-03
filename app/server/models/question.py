from pydantic import BaseModel


class QuestionsSchema(BaseModel):
    question: str = None
    answer: str = None
    question_type: str = None