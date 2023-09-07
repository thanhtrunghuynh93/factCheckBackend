from pydantic import BaseModel

class factSchema(BaseModel):
    claim: str = "World-renowned singer Celine Dion died or revealed new personal health developments in late July 2023."
    # model: str = "GPT"