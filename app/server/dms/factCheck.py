from server.models.factCheck.GPT_factCheck import verify_gpt
from server.models.factCheck.local_factCheck import verify_by_local_model 
from server.models.factCheck.nli_factCheck import verify
from server.models.factCheck.MedFact.factCheck import factCheck


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

async def medfact(params: dict) -> dict:
    params = dict(params)
    print(params["claim"])
    res = factCheck(claim = params["claim"], state=params["state"], current_step=params["current_step"])    
    return res

async def fact_check_by_gpt(params: dict) -> dict:
    params = dict(params)
    print(params["claim"])
    res = verify_gpt(params["claim"])
    
    return res

async def fact_check_by_local_model(params: dict) -> dict:
    params = dict(params)
    res = verify_by_local_model(params["claim"])
    return res

async def fact_check_by_nli(params: dict) -> dict:
    params = dict(params)
    res = verify(params["claim"])
    return res

# async def retrieve_question_by_id(id: str) -> dict:
#     # id thường là để query từ database
#     sample = {"question": "What is it?", "answer": "This is my house!"}
#     return question_helper(sample)