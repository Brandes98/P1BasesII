import generate_questions as gq
import generate_answers as ga
import json

def create_json(name, data):
    with open("data_" + name + ".jsonl", "w") as file:
        for item in data:
            file.write(json.dumps(item) + "\n")

def create_json_mongo_data():
    surveys = gq.generate_surveys()
    answers = ga.generate_answers(surveys)
    create_json("surveys", surveys)
    create_json("answers", answers)
