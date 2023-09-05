from server.models.factCheck.GPT_factCheck import verify
from server.models.factCheck.local_factCheck import verify_by_local_model 

# def factCheck_helper(data) -> dict:
#     return {
#         "claim": data["claim"],
#         "model": data["model"],
#     }

# async def retrieve_questions():
#     questions = []
#     sample1 = {"question": "What is it?", "answer": "This is my house!"}
#     questions.append(question_helper(sample1))
#     sample2 = {"question": "What is it?", "answer": "I don't know!"}
#     questions.append(question_helper(sample2))
#     return questions

async def fact_check_by_gpt(params: dict) -> dict:
    params = dict(params)
    res = verify(params["claim"])
    return res

async def fact_check_by_local_model(params: dict) -> dict:
    params = dict(params)
    res = verify_by_local_model(params["claim"])
    return res

# async def retrieve_question_by_id(id: str) -> dict:
#     # id thường là để query từ database
#     sample = {"question": "What is it?", "answer": "This is my house!"}
#     return question_helper(sample)