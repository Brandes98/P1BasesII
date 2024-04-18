import json
from datetime import datetime

def insert_surveys_mongodb():
    for i in range(5):
        with open ('data_surveys.jsonl', 'r') as file:
            for line in file:
                data = json.loads(line)
                data['FechaCreacion'] = datetime.fromisoformat(data['FechaCreacion'])
                data['FechaActualizacion'] = datetime.fromisoformat(data['FechaActualizacion'])
                print(data['FechaCreacion'], data['FechaActualizacion'])
                #posts_collection.insert_one(data)

def insert_answers_mongodb():
    for i in range(15):
        with open ('data_answers.jsonl', 'r') as file:
            for line in file:
                data = json.loads(line)
                data['FechaRealizado'] = datetime.fromisoformat(data['FechaRealizado'])
                print(data['FechaRealizado'])
                #posts_collection.insert_one(data)
