from pydantic import BaseModel


class QuestionsSchema(BaseModel):
    param1: str = None
    param2: str = None