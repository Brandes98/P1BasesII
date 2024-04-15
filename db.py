from pymongo import MongoClient
from flask import request, jsonify
from bson import ObjectId
from datetime import datetime
import psycopg2
import json

survey_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["NumeroEncuesta", "Titulo", "IdAutor", "Autor", "FechaCreacion", "FechaActualizacion", "Disponible", "Preguntas"],
        "properties": {
            "NumeroEncuesta": {
                "bsonType": "int",
                "description": "must be an integer and is required"
            },
            "Titulo": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "IdAutor": {
                "bsonType": "int",
                "description": "must be an integer and is required"
            },
            "Autor": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "FechaCreacion": {
                "bsonType": "date",
                "description": "must be a datetime object and is required"
            },
            "FechaActualizacion": {
                "bsonType": "date",
                "description": "must be a datetime object and is required"
            },
            "Disponible": {
                "bsonType": "int",
                "description": "must be an integer and is required"
            },
            "Preguntas": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["Numero", "Categoria", "Pregunta"],
                    "properties": {
                        "Numero": {
                            "bsonType": "int",
                            "description": "must be an integer and is required"
                        },
                        "Categoria": {
                            "bsonType": "string",
                            "description": "must be a string and is required"
                        },
                        "Pregunta": {
                            "bsonType": "string",
                            "description": "must be a string and is required"
                        },
                        "Opciones": {
                            "bsonType": "array",
                            "items": {
                                "bsonType": ["string", "int"],
                                "description": "must be an array of strings or integers"
                            },
                            "description": "optional field, required for certain categories"
                        }
                    }
                },
                "description": "must be an array of questions and is required"
            }
        }
    }
}

answer_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["NumeroEncuesta", "IdEncuestado", "Nombre", "Correo", "FechaRealizado", "Preguntas"],
        "properties": {
            "NumeroEncuesta": {
                "bsonType": "int",
                "description": "must be an integer and is required"
            },
            "IdEncuestado": {
                "bsonType": "int",
                "description": "must be an integer and is required"
            },
            "Nombre": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "Correo": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "FechaRealizado": {
                "bsonType": "date",
                "description": "must be a datetime object and is required"
            },
            "Preguntas": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["Numero", "Categoria", "Pregunta", "Respuesta"],
                    "properties": {
                        "Numero": {
                            "bsonType": "int",
                            "description": "must be an integer and is required"
                        },
                        "Categoria": {
                            "bsonType": "string",
                            "description": "must be a string and is required"
                        },
                        "Pregunta": {
                            "bsonType": "string",
                            "description": "must be a string and is required"
                        },
                        "Respuesta": {
                            "bsonType": ["string", "array", "int"],
                            "description": "must be a string, an array, or an integer, depending on the question type"
                        }
                    }
                },
                "description": "must be an array of answers and is required"
            }
        }
    }
}

class Database:
    def __init__(
            self, database="db_name", host="db_host", user="db_user", 
            password="db_pass", port="db_port", uri="mongodb:mongoadmin:mongosecretmongodb:27017/"):
        
        # PostgreSQL
        self.conn = psycopg2.connect(
            database=database, host=host, user=user, password=password, port=port)
       
        # MongoDB
        self.client = MongoClient(uri)
        self.db = self.client[database]
        self.encuestas = self.create_or_update_collection("encuestas", survey_schema)
        self.respuestas = self.create_or_update_collection("respuestas", answer_schema)
        self.insert_surveys_mongodb()
        self.insert_answers_mongodb()

    def create_or_update_collection(self, collection_name, schema):
        schema_for_db = {'validator': schema}  
        if collection_name not in self.db.list_collection_names():
            self.db.create_collection(collection_name, **schema_for_db)
        else:
            self.db.command('collMod', collection_name, **schema_for_db)
        return self.db[collection_name]

    # Métodos
    # Insertar datos MongoDB
    def insert_surveys_mongodb(self):
        for i in range(5):
            with open ('data_surveys.jsonl', 'r') as file:
                for line in file:
                    data = json.loads(line)
                    data['FechaCreacion'] = datetime.fromisoformat(data['FechaCreacion'])
                    data['FechaActualizacion'] = datetime.fromisoformat(data['FechaActualizacion'])
                    self.encuestas.insert_one(data)

    def insert_answers_mongodb(self):
        for i in range(15):
            with open ('data_answers.jsonl', 'r') as file:
                for line in file:
                    data = json.loads(line)
                    data['FechaRealizado'] = datetime.fromisoformat(data['FechaRealizado'])
                    self.respuestas.insert_one(data)

    # Autenticación y Autorización
    def insert_user(self, user_data):
        cursor = self.conn.cursor()
        cursor.execute(
            f"CALL INSERTAR_USUARIO('{user_data['Nombre']}', '{user_data['idRol']}', '{user_data['Correo']}', '{user_data['Contrasenna']}', '{user_data['FechaCreacion']}', '{user_data['FechaNacimiento']}', '{user_data['Genero']}', '{user_data['idPais']}');"
        )   
        self.conn.commit()
        cursor.close()

    def login_user(self, user_data):
        cursor = self.conn.cursor()
        token = None
        fecha = datetime.now()
        cursor.execute(
            "CALL LOGIN_USUARIO(%s, %s, %s, %s);",
            (user_data['Correo'], user_data['Contrasenna'], fecha, token)
        )
        # Obtener el valor de salida actualizado
        token = cursor.fetchone()[0]
        cursor.close()
        return token   

    # Usuarios
    def get_users(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT (U.id, U.Nombre, R.Nombre, U.Correo, U.FechaCreacion, U.FechaNacimiento, OBTENER_GENERO(U.Genero), P.Nombre) FROM Usuarios AS U INNER JOIN Roles AS R ON U.idRol = R.id INNER JOIN Paises AS P ON U.idPais = P.id;")
        users = cursor.fetchall()
        cursor.close()
        return users
    
    # Encuestas
    def insert_survey(self, data):
        try:
            token = data.pop('token', None)  # Optionally remove a token key
            data['FechaCreacion'] = datetime.fromisoformat(data['FechaCreacion'])
            data['FechaActualizacion'] = datetime.fromisoformat(data['FechaActualizacion'])
            result = self.encuestas.insert_one(data)
            return result.inserted_id  # Return the ID of the inserted document
        except Exception as e:
            raise Exception(f"An error occurred during survey insertion: {str(e)}")

    def get_surveys(self, page=1, limit=10):
        offset = (page - 1) * limit
        surveys = self.encuestas.find().skip(offset).limit(limit)
        result = []
        for survey in surveys:
            survey['_id'] = str(survey['_id'])
            result.append(survey)
        return result

    
    def get_specific_survey(self, id):
        survey = self.encuestas.find_one({"NumeroEncuesta": id})
        survey['_id'] = str(survey['_id'])
        return survey
    
    def update_survey(self, id, data):
        token = data.pop('token', None)
        self.encuestas.update_one({"NumeroEncuesta": id}, {"$set": data})
        return data
    
    def delete_survey(self, id, token):
        self.encuestas.delete_one({"NumeroEncuesta": id})

    def publish_survey(self, id, token):
        self.encuestas.update_one({"NumeroEncuesta": id}, {"$set": {"Disponible": 1}})