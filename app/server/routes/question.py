from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder

from server.dms.question import (
    add_question,
    delete_question,
    retrieve_question,
    retrieve_questions,
    update_question,
    retrieve_questions_type
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

@router.get("/question_type/{question_type}", response_description="questions by type retrieved")
async def get_questions_type(question_type):
    questions = await retrieve_questions_type(question_type)
    if questions:
        return ResponseModel(questions, "questions data retrieved successfully")
    return ResponseModel(questions, "Empty list returned")


@router.get("/{id}", response_description="question data retrieved")
async def get_question_data(id):
    question = await retrieve_question(id)
    if question:
        return ResponseModel(question, "question data retrieved successfully")
    return ErrorResponseModel("An error occurred.", 404, "question doesn't exist.")


@router.post("/", response_description="question data added into the database")
async def add_question_data(question: QuestionsSchema = Body(...)):
    questions = jsonable_encoder(question)
    question = await add_question(question)
    return ResponseModel(question, "question added successfully.")


@router.delete("/{id}", response_description="question data deleted from the database")
async def delete_question_data(id: str):
    deleted_question = await delete_question(id)
    if deleted_question:
        return ResponseModel(
            "question with id: {} removed".format(id), "question deleted successfully"
        )
    return ErrorResponseModel(
        "An error occurred", 404, "question with id {0} doesn't exist".format(id)
    )
