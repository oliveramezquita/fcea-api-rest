from formsapp.constants import (
    QUESTION_TYPE,
    STRING_TO_REMOVE,
    STRING_TO_REPLACE,
    IGNORE_KEYS,
    GROUP_BY_TYPE,
)
import re
import json
import unicodedata
import string


def parse_data(formsapp_data):
    # with open('./formsapp/assets/data_formsapp.json') as f:
    #     formsapp_data = json.load(f)

    form_questions = formsapp_data['form']['questions']
    questions = {}
    for question in form_questions:
        if question['questionType'] in QUESTION_TYPE:
            if question['question'] in list(string.ascii_uppercase):
                questions[question['_id']] = {
                    'type': 'macroinvertebrate',
                    'name': clean_text(question['question']),
                }
            else:
                questions[question['_id']] = {
                    'type': question['questionType'],
                    'name': clean_text(question['question']),
                }
            if 'parentId' in question:
                questions[question['_id']]['parent'] = parent_name(
                    question['parentId'], form_questions)
    # get_types_of_questions(questions)

    answers = formsapp_data['answer']['answers']
    data = {}
    for answer in answers:
        key_value = ignore_keys(answer.keys())
        if not key_value:
            continue

        key_name = snake(questions[answer['q']]['name'])
        parent = ""
        if 'parent' in questions[answer['q']]:
            parent = f"{snake(questions[answer['q']]['parent'])}/"

        key = f"{parent}{key_name}"
        if questions[answer['q']]['type'] in GROUP_BY_TYPE['text']:
            data[key] = answer[key_value]

        if questions[answer['q']]['type'] in GROUP_BY_TYPE['image']:
            data[key] = answer[key_value]['urls']

        if questions[answer['q']]['type'] in GROUP_BY_TYPE['macroinvertebrate']:
            if len(answer[key_value]) > 0:
                key_macroinvertebrate = f"{parent}{key_name.upper()}"
                data[key_macroinvertebrate] = " ".join(
                    m['t'].lower() for m in answer[key_value])

        if questions[answer['q']]['type'] in GROUP_BY_TYPE['select']:
            if len(answer[key_value]) == 1:
                data[key] = answer[key_value][0]['t']
            elif len(answer[key_value]) > 1:
                values = []
                for i in answer[key_value]:
                    values.append(i['t'])
                data[key] = values

        if questions[answer['q']]['type'] in GROUP_BY_TYPE['grid']:
            d = data.copy()
            grid = set_grid(clean_text(key_name), answer[key_value])
            d.update(grid)
            data = d

    return data


def get_types_of_questions(questions):
    question_types = []
    for key in questions:
        question_types.append(questions[key]['type'])
    set_res = set(question_types)
    print(list(set_res))


def parent_name(parent_id, form_questions):
    parent = [fq['question']
              for fq in form_questions if fq['_id'] == parent_id]
    return clean_text(parent[0])


def clean_text(text):
    for i in STRING_TO_REMOVE:
        new_text = text.replace(i, '')
        text = new_text
    for key in STRING_TO_REPLACE.keys():
        text = text.replace(key, STRING_TO_REPLACE[key])

    regex = r"[(][^)]*[)]"
    text = re.sub(regex, "", text, 0, re.MULTILINE)
    return text


def ignore_keys(keys):
    key_list = list(keys)
    key_result = list(set(key_list) - set(IGNORE_KEYS))
    return key_result[0] if len(key_result) > 0 else None


def snake(s):
    s = unicodedata.normalize('NFKD', s).encode(
        'ascii', 'ignore').decode('utf-8', 'ignore').lower()
    return '_'.join(
        re.sub('([A-Z][a-z]+)', r' \1',
               re.sub('([A-Z]+)', r' \1',
                      s.replace('-', ' '))).split())


def set_location(location):
    value = ''
    if 'a1' in location and location['a1'] != '':
        value += location['a1']
    if 'a2' in location and location['a2'] != '':
        value += f", {location['a2']}"
    if 'p' in location and location['p'] != '':
        value += f", {location['p']}"
    if 'c' in location and location['c'] != '':
        value += f" {location['c']}"
    if 's' in location and location['s'] != '':
        value += f", {location['s']}"

    return value.strip()


def set_grid(name, grid):
    values = {}
    if len(grid) == 1:
        for i in grid[0]['c']:
            key_name = f"{name}/{snake(i['cn'])}"
            values[key_name] = i['n']
        return values
    elif len(grid) > 1:
        grid_list = []
        for i in grid:
            temp = {}
            for j in i['c']:
                key_name = f"{name}/{snake(j['cn'])}"
                temp[key_name] = j['n']
            grid_list.append(temp)
        values[name] = grid_list
        return values
