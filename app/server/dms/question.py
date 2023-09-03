from server.database.mongo import database
from bson.objectid import ObjectId

questions_collection = database.get_collection("questions")

# helpers
def question_helper(question) -> dict:
    return {
        "id": str(question["_id"]),
        "question": question["question"],
        "answer": question["answer"],
        "question_type": question["question_type"],
    }


async def retrieve_questions():
    questions = []
    async for question in questions_collection.find().limit(20):
        questions.append(question_helper(question))
    return questions

async def retrieve_questions_type(question_type: str):
    questions = []
    async for question in questions_collection.find({"question_type": question_type}).limit(20):
        questions.append(question_helper(question))
    return questions

async def add_question(question_data: dict) -> dict:
    question_data = dict(question_data)

    question = await questions_collection.insert_one(question_data)

    new_question = await questions_collection.find_one({"_id": ObjectId(question.inserted_id)})
    return question_helper(new_question)

async def retrieve_question(id: str) -> dict:
    question = await questions_collection.find_one({"_id": ObjectId(id)})
    if question:
        return question_helper(question)

async def update_question(id: str, data: dict):
    if len(data) < 1:
        return False
    question = await questions_collection.find_one({"_id": ObjectId(id)})
    if question:
        updated_question = await questions_collection.update_one(
            {"_id": id}, {"$set": data}
        )
        if updated_question:
            return True
        return False

async def delete_question(id: str):
    question = await questions_collection.find_one({"_id": ObjectId(id)})
    if question:
        await questions_collection.delete_one({"_id": ObjectId(id)})
        return True