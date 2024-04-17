from pymongo import MongoClient
from flask import request, jsonify
from bson import ObjectId
from datetime import datetime
from json_schemas import survey_schema, answer_schema
import psycopg2
import json

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
        self.encuestas.create_index([("NumeroEncuesta", 1)], unique=True)
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
        if self.encuestas.count_documents({}) == 0:
            with open('data_surveys.jsonl', 'r') as file:
                for line in file:
                    data = json.loads(line)
                    data['FechaCreacion'] = datetime.fromisoformat(data['FechaCreacion'])
                    data['FechaActualizacion'] = datetime.fromisoformat(data['FechaActualizacion'])
                    self.encuestas.insert_one(data)

    def insert_answers_mongodb(self):
        if self.respuestas.count_documents({}) == 0:
            with open('data_answers.jsonl', 'r') as file:
                for line in file:
                    data = json.loads(line)
                    data['FechaRealizado'] = datetime.fromisoformat(data['FechaRealizado'])
                    self.respuestas.insert_one(data)

    # Verificar data
    def verify_author(self, idAutor):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM Usuarios WHERE id = %s;", (idAutor,))
        user = cursor.fetchone()
        cursor.close()
        return True if user else False

    # Verificar token
    def get_token(self, token):
        cursor = self.conn.cursor()
        cursor.execute("SELECT U.idRol FROM Logs AS L INNER JOIN Usuarios AS U ON L.IdUsuario = U.id WHERE L.Token = %s;", (token,))
        user = cursor.fetchone()
        cursor.close()
        return user[0] if user else 0
    
    def verify_token_admin(self, token):
        return self.get_token(token) == 1
    
    def verify_token_active(self, token):
        cursor = self.conn.cursor()
        cursor.execute("SELECT U.id FROM Logs AS L INNER JOIN Usuarios AS U ON L.IdUsuario = U.id WHERE L.Token = %s AND L.FechaLogOut IS NULL;", (token,))
        user = cursor.fetchone()
        cursor.close()
        return True if user else False
    
    def verify_token_create_surveys(self, token):
        return self.get_token(token) in [1, 2]
    
    def verify_token_user(self, idAutor, token):
        cursor = self.conn.cursor()
        cursor.execute("SELECT U.id, U.idRol FROM Logs AS L INNER JOIN Usuarios AS U ON L.IdUsuario = U.id WHERE L.Token = %s AND U.id = %s AND L.FechaLogOut IS NULL;", (token, idAutor))
        user = cursor.fetchone()
        cursor.close()
        return user if user else None

    def verify_token_creator_survey(self, idAutor, num_encuesta, token):
        user = self.verify_token_user(idAutor, token)
        author = self.verify_author(idAutor)
        if not user or not author:
            return False 
        if user[1] == 1:
            return True
        elif user[1] == 2:
            survey = self.encuestas.find_one({"NumeroEncuesta": num_encuesta, "IdAutor": idAutor})
            return survey["IdAutor"] == user[0]
        return False

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
            token = data.pop("Token", 0)
            if token == 0:
                raise ValueError("Token is required")
            
            if self.verify_token_create_surveys(token):
                data['FechaCreacion'] = datetime.fromisoformat(data['FechaCreacion'])
                data['FechaActualizacion'] = datetime.fromisoformat(data['FechaActualizacion'])
                insert_result = self.encuestas.insert_one(data)
                return insert_result
            else:
                raise Exception("You don't have permission to create this survey.")
        except Exception as e:
            raise Exception(f"An error occurred during survey insertion: {str(e)}")

    def get_public_surveys(self, page=1, limit=10):
        offset = (page - 1) * limit
        surveys = self.encuestas.find({"Disponible": 1}).skip(offset).limit(limit)
        result = []
        for survey in surveys:
            survey['_id'] = str(survey['_id'])
            result.append(survey)
        return result

    
    def get_specific_survey(self, id):
        survey = self.encuestas.find_one({"NumeroEncuesta": id})
        if survey:
            survey['_id'] = str(survey['_id'])
        else:
            survey = None
        return survey
    
    def update_survey(self, id, data):
        token = data.pop('Token', None)
        idAutor = data.get('IdAutor')
        if self.verify_token_creator_survey(idAutor, id, token):
            data['FechaCreacion'] = datetime.fromisoformat(data['FechaCreacion'])
            data['FechaActualizacion'] = datetime.fromisoformat(data['FechaActualizacion'])
            self.encuestas.update_one({"NumeroEncuesta": id}, {"$set": data})
            return data
        return None
    
    def delete_survey(self, id, data):
        token = data.pop('Token', None)
        idAutor = data.get('IdAutor')
        if self.verify_token_creator_survey(idAutor, id, token):
            self.encuestas.delete_one({"NumeroEncuesta": id})
            return True
        return False


    def publish_survey(self, id, data):
        token = data.pop('Token', None)
        idAutor = data.get('IdAutor')
        if self.verify_token_creator_survey(idAutor, id, token):
            self.encuestas.update_one({"NumeroEncuesta": id}, {"$set": {"Disponible": 1}})
            return True
        return False
    
    # Preguntas de encuestas
    def insert_question(self, id, data):
        """
        JSON EXAMPLE:
        {
            "IdAutor": 1,
            "Token": "1",
            "Preguntas": {
                "Numero": 0,
                "Categoria": "SiNo",
                "Pregunta": "¿Tiene hambre?"
            }
        }
        """
        token = data.pop('Token', None)
        idAutor = data.get('IdAutor')
        if self.verify_token_creator_survey(idAutor, id, token):
            survey_questions = self.encuestas.find_one({"NumeroEncuesta": id}, {"Preguntas": 1})
            max_number = self.encuestas.aggregate([
                {'$match': {'NumeroEncuesta': id}},
                {'$unwind': '$Preguntas'},
                {'$group': {
                    '_id': '$_id',
                    'maxNumero': {'$max': '$Preguntas.Numero'}
                }},
                {'$project': { 
                    '_id': 0,  
                    'maxNumero': 1 
                }}
            ])
            max_number = list(max_number)[0]['maxNumero'] if max_number else 0
            for question in data['Preguntas']:
                max_number += 1
                question['Numero'] = max_number
                survey_questions['Preguntas'].append(question)
            self.encuestas.update_one(
                                                {"NumeroEncuesta": id},
                                                {"$set": {"Preguntas": survey_questions['Preguntas']}}
                                            )
            return True
        return False

    def get_questions(self, id):
        survey_questions = self.encuestas.find_one({"NumeroEncuesta": id}, {"_id": 0, "Preguntas": 1})
        return survey_questions if survey_questions else None
    
    def update_question(self, id, questionId, data):
        token = data.pop('Token', None)
        idAutor = data.get('IdAutor')
        if self.verify_token_creator_survey(idAutor, id, token) and len(data["Preguntas"]) == 1:
            survey = self.encuestas.find_one({"NumeroEncuesta": id}, {"_id": 0, "Preguntas": 1})
            for question in survey['Preguntas']:
                if question['Numero'] == questionId:
                    question.update(data['Preguntas'][0])
                    self.encuestas.update_one(
                        {"NumeroEncuesta": id, "Preguntas.Numero": questionId},
                        {"$set": {"Preguntas.$": data['Preguntas'][0]}}
                    )
                    return data['Preguntas'][0]
        return None
    
    def delete_question(self, id, questionId, data):
        token = data.pop('Token', None)
        idAutor = data.get('IdAutor')
        if self.verify_token_creator_survey(idAutor, id, token):
            survey = self.encuestas.find_one({"NumeroEncuesta": id}, {"_id": 0, "Preguntas": 1})
            for question in survey['Preguntas']:
                if question['Numero'] == questionId:
                    survey['Preguntas'].remove(question)
                    self.encuestas.update_one(
                        {"NumeroEncuesta": id},
                        {"$set": {"Preguntas": survey['Preguntas']}}
                    )
                    return survey['Preguntas']
        return None
    def post_response(self, id, data):
        token = data.pop('Token', None)
        if self.verify_token_active(token):
            data['FechaRealizado'] = datetime.fromisoformat(data['FechaRealizado'])
            self.respuestas.insert_one(data)
            return data
        return None
    def get_responses(self, id):
        responses = self.respuestas.find({"NumeroEncuesta": id})
        result = []
        for response in responses:
            response['_id'] = str(response['_id'])
            result.append(response)
        return result
    # sin probar
    def post_encuestado(self, data):
        cursor = self.conn.cursor()
        data['FechaNacimiento'] = datetime.fromisoformat(data['FechaNacimiento'])
        cursor.execute("INSERT INTO Usuarios (Nombre, idRol, Correo, Contrasenna, FechaCreacion, FechaNacimiento, Genero, idPais) VALUES (%s, %s, %s, %s, %s, NOW(), %s, %s) RETURNING id;", (data['Nombre'], 3, data['Correo'], data['Contrasenna'], data['FechaNacimiento'], data['Genero'], data['idPais']))
        user = cursor.fetchone()
        cursor.close()
        return True if user else False

    def get_encuestados(self): # requiere token
        respondents = self.respuestas.find()
        result = []
        for respondent in respondents:
            respondent['_id'] = str(respondent['_id'])
            result.append(respondent)
        return result
    def get_encuestado(self, id):
        respondent = self.respuestas.find_one({"NumeroEncuesta": id})
        if respondent:
            respondent['_id'] = str(respondent['_id'])
        else:
            respondent = None
        return respondent
    def get_encuestado_by_token(self, token):
        respondent = self.respuestas.find
        if respondent:
            respondent['_id'] = str(respondent['_id'])
        else:
            respondent = None
        return respondent
    def actualizar_encuestado(self, id, data):
        token = data.pop('Token', None)
        if self.verify_token_active(token):
            self.respuestas.update_one({"NumeroEncuesta": id}, {"$set": data})
            return data
        return None
    def eliminar_encuestado(self, id):
        token = data.pop('Token', None)
        if self.verify_token_active(token):
            self.respuestas.delete_one({"NumeroEncuesta": id})
            return True
        return False
    def get_analytics(self, id):
        survey = self.encuestas.find_one({"NumeroEncuesta": id})
        if survey:
            survey['_id'] = str(survey['_id'])
        else:
            survey = None
        return survey