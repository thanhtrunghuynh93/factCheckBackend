def question_helper(question) -> dict:
    return {
        "question": question["question"],
        "answer": question["answer"],
    }


async def retrieve_questions():
    questions = []
    sample1 = {"question": "What is it?", "answer": "This is my house!"}
    questions.append(question_helper(sample1))
    sample2 = {"question": "What is it?", "answer": "I don't know!"}
    questions.append(question_helper(sample2))
    return questions

async def retrieve_question_by_params(params: dict) -> dict:
    params = dict(params)
    return params

async def retrieve_question_by_id(id: str) -> dict:
    # id thường là để query từ database
    sample = {"question": "What is it?", "answer": "This is my house!"}
    return question_helper(sample)