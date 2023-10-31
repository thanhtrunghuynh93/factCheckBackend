from pydantic import BaseModel

class factSchema(BaseModel):
    claim: str = "World-renowned singer Celine Dion died or revealed new personal health developments in late July 2023."
    # model: str = "GPT"

class medFact(BaseModel):
    claim: str = "Creatine can cause abdominal cramp."
    state: str = ""
    current_step: int = 0
    done: bool = False
    