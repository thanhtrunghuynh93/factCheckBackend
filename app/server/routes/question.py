from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder

from server.dms.question import (
    retrieve_question_by_params,
    retrieve_question_by_id,
    retrieve_questions,
)
from server.utils.response import (
    ErrorResponseModel,
    ResponseModel,
)
from server.models.question import QuestionsSchema

router = APIRouter()

@router.get("/", response_description="questions retrieved")
async def get_questions():
    questions = await retrieve_questions()
    if questions:
        return ResponseModel(questions, "questions data retrieved successfully")
    return ResponseModel(questions, "Empty list returned")

@router.get("/{id}", response_description="question data retrieved")
async def get_question_by_id(id):
    question = await retrieve_question_by_id(id)
    if question:
        return ResponseModel(question, "question data retrieved successfully")
    return ErrorResponseModel("An error occurred.", 404, "question doesn't exist.")


@router.post("/", response_description="question data added into the database")
async def get_question_by_params(params: QuestionsSchema = Body(...)):
    params = jsonable_encoder(params)
    question = await retrieve_question_by_params(params)
    return ResponseModel(question, "question added successfully.")