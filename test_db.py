from datetime import datetime
import os
import pytest
from db import Database

# docker-compose exec app poetry run pytest test_db.py

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

mongo_username = os.getenv("MONGO_INITDB_ROOT_USERNAME")
mongo_password = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
mongo_uri = f"mongodb://{mongo_username}:{mongo_password}@mongodb:27017/"

db = Database(database=DB_NAME, host=DB_HOST, user=DB_USER, password=DB_PASSWORD, port=DB_PORT, uri=mongo_uri)

# se inserta un usuario
def test_insert_user():
    result = db.insert_user("Ken", 1, "ken@gmail.com", "qwerty123", "2023-04-15 02:56:24.314201", "1990-01-01", "M", "CRC")
    assert result is not None 


def test_login_user():
    result = db.login_user({"Correo": "admin@dominio.com", "Contrasenna": "contrasenna123"})
    assert result is not None

# se crea nueva coleccion
def test_create_or_update_collection():
    result = db.create_or_update_collection("nuevaSurvey", {"title": "Survey nueva", "published": False})
    assert result is not None

# inserta una encuesta
def test_insert_surveys_mongodb():
    result = db.insert_surveys_mongodb()
    assert result is None # no tomamos en cuenta el resultado, porque solo insertamos una dentro de la funcion

# se insertan respuestas
def test_insert_answers_mongodb():
    result = db.insert_answers_mongodb()
    assert result is None # no tomamos en cuenta el resultado, porque solo insertamos una dentro de la funcion

# se verifica si el autor existe, prueba positiva y negativa
def test_verify_author():
    result = db.verify_author(1)
    assert result is True
    negativeResult = db.verify_author(-1)
    assert negativeResult is False

# con el token se verifica el rol del usuario
def test_get_token():  
    result = db.get_token(1)
    assert result is not None

# se verifica si el token es de un administrador
def test_verify_token_admin():
    result = db.verify_token_admin(1)
    assert result is not None

# se verifica si el token es de un usuario activo
def test_verify_token_active():
    result = db.verify_token_active(1)
    assert result is True
    negativeResult = db.verify_token_active(200)
    assert negativeResult is False

def test_verify_token_user():
    result = db.verify_token_user(1, 1)
    assert result is not None

# se verifica si el id de la encuesta corresponde al id del creador de la encuesta
def test_verify_token_creator_survey(): 
    result = db.verify_token_creator_survey(1, 1, 1)
    assert result is True
    negativeResult = db.verify_token_creator_survey(20, 1, 2)
    assert negativeResult is False

# se verifica si el token es de un creador de encuestas (rol 1 o 2)
def test_verify_token_create_surveys():
    result = db.verify_token_create_surveys(1)
    assert result is True
    negativeResult = db.verify_token_create_surveys(30)
    assert negativeResult is False

def test_get_users():
    result = db.get_users()
    assert result is not None

def test_get_public_surveys():
    result = db.get_public_surveys(1, 2)
    assert isinstance(result, list)
    for survey in result:
        assert 'Disponible' in survey and survey['Disponible'] == 1

def test_publish_survey():
    data = {
        'Token': 1,
        'IdAutor': 1
    }
    result = db.publish_survey(1, data)
    assert result is not None

def test_insert_question():
    data = {
        'Token': 1,
        'IdAutor': 2,
        'Preguntas': [
            {
                'Numero': 33,
                'Categoria': 'EleccionSimples',
                'Pregunta': 'si?'
            }
        ]
    }
    result = db.insert_question(4, data)
    assert result is not None

def test_get_questions():
    result = db.get_questions(4)
    assert result is not None


def test_fetch_response_summary():
    result = db.fetch_response_summary(5)
    assert result is not None


def test_get_responses():  
    result = db.get_responses(5)
    assert result is not None

def test_post_encuestado():
    data = {
        'Nombre': 'Ken Wow',
        'Correo': 'nuevo.correo@gmail.com',
        'Contrasenna': 'nuevacontrasenna',
        'FechaNacimiento': '2000-01-01',
        'Genero': 'M',
        'idPais': 'CRC',
    }
    result = db.post_encuestado(data)
    assert 'success' in result and result['success'] is True

def test_get_encuestados():
    result = db.get_encuestados()
    assert result is not None

def test_get_encuestados():
    data = {
        'Token': 1,
        'IdAutor': 1
    }
    result = db.get_encuestados(data)
    assert result is not None

def test_actualizar_encuestado():
    data = {
        'Nombre': 'Nuevo nombre',
        'Correo': 'nuevo.correo@example.com',
        'Contrasenna': 'nuevacontrasenna',
        'FechaNacimiento': '2000-01-01',
        'Genero': 'M',
        'idPais': 'CRC',
        'Token': 1,
        'IdAutor': 1
    }
    result = db.actualizar_encuestado(1, data)
    assert result is True



# SI FUNCIONA PERO SOLO SE DEBE CORRER UNA VEZ
"""
# inserta survey
#def test_insert_survey():
 #   result = db.insert_survey({"Token": 1, "NumeroEncuesta": 10, "Titulo": "Collection until poor.", "IdAutor": 1, "Autor": "AdminCR", "FechaCreacion": "2020-06-22T18:19:55", "FechaActualizacion": "1993-09-26T06:05:56", "Disponible": 1, "Preguntas": [{"Numero": 1, "Categoria": "EleccionMultiples", "Pregunta": "Whom upon create now near.", "Opciones": ["face", "minute", "training", "situation", "attack"]}, {"Numero": 2, "Categoria": "Numericas", "Pregunta": "Customer water be avoid fight perhaps computer."}, {"Numero": 3, "Categoria": "EleccionSimples", "Pregunta": "Lay edge gas field chair.", "Opciones": ["put", "already", "need", "these", "try", "factor"]}, {"Numero": 4, "Categoria": "Abiertas", "Pregunta": "Free wish space treat."}, {"Numero": 5, "Categoria": "SiNo", "Pregunta": "Beautiful kid own become term."}, {"Numero": 6, "Categoria": "Numericas", "Pregunta": "Doctor better to act seven say can behind."}, {"Numero": 7, "Categoria": "SiNo", "Pregunta": "Become office then table dinner stuff tell."}, {"Numero": 8, "Categoria": "EscalaCalificacion", "Pregunta": "Size cost event.", "Opciones": [4, 8]}, {"Numero": 9, "Categoria": "EleccionSimples", "Pregunta": "Possible member walk magazine development per.", "Opciones": ["research", "challenge", "military", "time", "tax"]}]})
  #  assert result is not None


#SOLO CORRER UNA VEZ
def test_update_question():
    id = 1
    questionId = 1
    data = {
        'Token': 1,
        'IdAutor': 1,
        'Preguntas': [
            {
                'Numero': 1,
                'Categoria': 'preguntasWow',
                'Pregunta': 'no?'
            }
        ]
    }

    result = db.update_question(id, questionId, data)

    assert result is not None
    assert result == data['Preguntas'][0]

# SI FUNCIONA PERO CORRER SOLO UNA VEZ
def test_delete_survey():
    data = {
        'Token': 2,
        'IdAutor': 2
    }
    result = db.delete_survey(2, data)
    assert result is True

# correr solo una vez
def test_delete_question():
    # 
    data = {
        'Token': 1,
        'IdAutor': 1,
    }

   
    survey_id = 1
    question_id = 2

    # Llamar a la función que se está probando
    result = db.delete_question(survey_id, question_id, data)

    assert result is not None
"""



# FALTARON

def test_post_response():
    data = {"NumeroEncuesta": 1, 
            'Token': 1,
            "IdEncuestado": 3, 
            "Nombre": "EncuestadoES", 
            "Correo": "encuestado@dominio.com", 
            "FechaRealizado": "2023-03-05T09:53:44", 
            "Preguntas": [
                {"Numero": 1, "Categoria": "EleccionMultiples", 
                 "Pregunta": "Total history network sound skill.",
                 "Respuesta": ["challenge", "act", "nor"]}]}
    result = db.post_response(1, data)
    assert result is not None


