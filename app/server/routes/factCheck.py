from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder

from server.dms.factCheck import (
    fact_check_by_gpt,
    fact_check_by_local_model,
    fact_check_by_nli,
    medfact
)

from server.utils.response import (
    ErrorResponseModel,
    ResponseModel,
)

from server.models.fact import factSchema, medFact

router = APIRouter()

# @router.get("/", response_description="questions retrieved")
# async def get_questions():
#     questions = await retrieve_questions()
#     if questions:
#         return ResponseModel(questions, "questions data retrieved successfully")
#     return ResponseModel(questions, "Empty list returned")

# @router.get("/{id}", response_description="question data retrieved")
# async def get_question_by_id(id):
#     question = await retrieve_question_by_id(id)
#     if question:
#         return ResponseModel(question, "question data retrieved successfully")
#     return ErrorResponseModel("An error occurred.", 404, "question doesn't exist.")

@router.post("/medfact", response_description="Medfact")
async def get_question_by_params(params: medFact = Body(...)):
    # print("Received params")
    # print(params)
    params = jsonable_encoder(params)
    # print("Parse params")
    # print(params)
    factCheck = await medfact(params)
    return ResponseModel(factCheck, "Fact checked successfully.")

@router.post("/gpt", response_description="Verify a fact")
async def get_question_by_params(params: factSchema = Body(...)):
    params = jsonable_encoder(params)
    factCheck = await fact_check_by_gpt(params)
    return ResponseModel(factCheck, "Fact checked successfully.")

@router.post("/nli", response_description="Verify a fact by nli")
async def get_question_by_params(params: factSchema = Body(...)):
    params = jsonable_encoder(params)
    factCheck = await fact_check_by_nli(params)
    return ResponseModel(factCheck, "Fact checked successfully.")

@router.post("/local", response_description="Verify a fact")
async def get_question_by_params(params: factSchema = Body(...)):
    params = jsonable_encoder(params)
    factCheck = await fact_check_by_local_model(params)
    return ResponseModel(factCheck, "Fact checked successfully.")
