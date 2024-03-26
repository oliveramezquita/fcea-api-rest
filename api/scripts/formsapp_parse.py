import json


def get_mapped_data():
    with open('./api/assets/data_formsapp.json') as f:
        data = json.load(f)

    form_questions = data['form']['questions']
    questions = {}
    for question in form_questions:
        questions[question['_id']] = question['question']

    answers = data['answer']['answers']

    return questions
