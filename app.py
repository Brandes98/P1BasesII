import json
import os
from pymongo import MongoClient
from bson import ObjectId
from app_service import AppService
from db import Database
from flask import Flask, request, jsonify, abort
from datetime import datetime
import redis

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

mongo_username = os.getenv("MONGO_INITDB_ROOT_USERNAME")
mongo_password = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
mongo_uri = f"mongodb://{mongo_username}:{mongo_password}@mongodb:27017/"

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

db = Database(database=DB_NAME, host=DB_HOST, user=DB_USER, password=DB_PASSWORD, port=DB_PORT, uri=mongo_uri)

app = Flask(__name__)
mongodb_client = MongoClient(mongo_uri)
appService = AppService(db)

def datetime_converter(o):
    if isinstance(o, datetime):
        return o.__str__()

# Cache
def get_cache(cache_key):
    cached_surveys = redis_client.get(cache_key)
    if cached_surveys:
        return jsonify(json.loads(cached_surveys)) 
    return None

# Cache cleaner
def cache_cleaner_surveys():
    for key in redis_client.scan_iter("surveys:*"):
        redis_client.delete(key)

def cache_cleaner_survey(id):
    redis_client.delete(f"survey:{id}")

def cache_cleaner_all_surveys(id):
    cache_cleaner_survey(id)
    cache_cleaner_surveys()

def cache_cleaner_questions(id):
    redis_client.delete(f"survey_questions:{id}")

@app.route("/")
def home():
    return "App Works!!!"

# Autenticación y Autorización
# Autenticación y Autorización
# ruta para registrar un usuario y que coloque sus datos en una pantalla
# en el boton input llama la ruta /auth/register
# en el metodo POST se llama a la funcion insert_user
@app.route("/register", methods=["GET"])
def register():
    #codigo html para resgistrar
    return """
    <form action="/auth/register" method="POST">
        <input type="text" name="Nombre" placeholder="nombre">
        <input type="text" name="idRol" placeholder="rol">
        <input type="text" name="Correo" placeholder="correo">
        <input type="password" name="Contrasenna" placeholder="password">
        <input type="text" name="FechaCreacion" placeholder="fecha de hoy">
        <input type="date" name="FechaNacimiento" placeholder="fecha nacimiento">
        <input type="text" name="Genero" placeholder="genero">
        <input type="text" name="idPais" placeholder="idPais">
        
        <input type="submit" onclick="window.location.href='/auth/register'" value="Redirect to Another Endpoint">
       
    </form>
    """

# Autenticación y Autorización
@app.route("/auth/register", methods=["POST"])
def register_user():
    user_data = request.form.to_dict()
    nombre = user_data.get("Nombre")
    idRol = int(user_data.get("idRol"))
    correo = user_data.get("Correo")
    contrasena = user_data.get("Contrasenna")
    fechaCreacion = user_data.get("FechaCreacion")
    fechaNacimiento = user_data.get("FechaNacimiento")
    genero = user_data.get("Genero")
    idPais = user_data.get("idPais")
    data = {
        "Nombre": nombre,
        "idRol": idRol,
        "Correo": correo,
        "Contrasenna": contrasena,
        "FechaCreacion": fechaCreacion,
        "FechaNacimiento": fechaNacimiento,
        "Genero": genero,
        "idPais": idPais
    }
    try:
        appService.insert_user(data)
        return "Usuario agregado"
    except Exception as e:
        return str(e), 400

# ruta para logearse
# en el boton input llama la ruta /auth/login
# en el metodo POST se llama a la funcion login
@app.route("/login", methods=["GET"])
def webLogin():
    return """
    <form action="/auth/login" method="POST">
        <input type="text" name="Correo" placeholder="correo">
        <input type="password" name="Contrasenna" placeholder="password">
        <input type="submit" onclick="window.location.href='/auth/login'" value="Redirect to Another Endpoint">
    </form>
    """

# ruta para logearse
# en el boton input llama la ruta /auth/login
# en el metodo POST se llama a la funcion login
@app.route("/login", methods=["POST"])
def login():
    try:
        
        user_data = request.get_json()

       
        if not user_data:
            user_data = request.form.to_dict()

        correo = user_data.get("Correo")
        contrasenna = user_data.get("Contrasenna")

        if not correo or not contrasenna:
            return jsonify({"error": "Correo and Contrasenna are required fields"}), 400

        user = appService.login(user_data)
        
        if user:
            return jsonify(user), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Autenticación y Autorización
@app.route("/auth/register", methods=["POST"])
def insert_user():
    user_data = request.get_json()
    try:
        appService.insert_user(user_data)
        return jsonify({"status": "success", "message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400  # or appropriate error code, e.g., 500 for server errors

@app.route("/auth/login", methods=["POST"])
def login_user():
    user_data = request.get_json()
    token = appService.login_user(user_data)
    return token

# Usuarios
@app.route("/users", methods=["GET"])
def get_users():
    try:
        users = appService.get_users()
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/users/<int:id>", methods=["GET"])
def get_user(id):
    try:
        user = AppService.get_user(id)
        if not user:
            return jsonify({"error": "User not found"}), 404  # Ensuring a 404 is returned if no user is found
        return jsonify(user), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Ensure any exceptions are caught and return a 500

@app.route("/users/<int:id>", methods=["PUT"])
def update_user(id):
    data = request.get_json()
    try:
        data = appService.update_user(id, data)
        if data is None:
            return jsonify({"error": "User not found"}), 404
        return data
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/users/<int:id>", methods=["DELETE"])
def delete_user(id):
    try:
        data = request.get_json()
        flag = appService.delete_user(id, data)
        if flag:
            return "Usuario eliminado", 200
        return jsonify({"error": "User not found or no permission to delete"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Encuestas
@app.route("/surveys", methods=["POST"])
def insert_survey():
    try:
        data_with_token = request.get_json()
        result = appService.insert_survey(data_with_token)
        if result.inserted_id:
            data_with_token['_id'] = str(result.inserted_id)
            return jsonify(data_with_token), 201
        else:
            return jsonify({"error": "Failed to insert survey"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/surveys/page=<int:num_page>", methods=["GET"])
def get_public_surveys(num_page):
    page = int(request.args.get('page', num_page))
    limit = int(request.args.get('limit', 5))

    cache_key = f"surveys:{page}:{limit}"
    cached_surveys = get_cache(cache_key)
    if cached_surveys:
        return cached_surveys
    
    try:
        surveys = appService.get_public_surveys(page, limit)
        serialized_data = json.dumps(surveys, default=datetime_converter)
        redis_client.setex(cache_key, 3600, serialized_data)
        return jsonify(surveys)
    except ValueError:
        return jsonify({"error": "Invalid page or limit value"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/surveys/<int:id>", methods=["GET"])
def get_specific_survey(id):
    cache_key = f"survey:{id}"
    cached_surveys = get_cache(cache_key)
    if cached_surveys:
        return cached_surveys

    try:
        survey = appService.get_specific_survey(id)
        if survey:
            serialized_data = json.dumps(survey, default=datetime_converter)
            redis_client.setex(cache_key, 3600, serialized_data)
            return jsonify(survey)
        else:
            return jsonify({"error": "Survey not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/surveys/<int:id>", methods=["PUT"])
def update_survey(id):
    data = request.get_json()
    try:
        data = appService.update_survey(id, data)
        if data is None:
            return jsonify({"error": "Survey not found"}), 404
        cache_cleaner_all_surveys(id)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/surveys/<int:id>", methods=["DELETE"])
def delete_survey(id):
    try:
        data = request.get_json() 
        flag = appService.delete_survey(id, data)
        if flag:
            cache_cleaner_all_surveys(id)
            return "Encuesta eliminada", 200
        return jsonify({"error": "Survey not found or no permission to delete"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/surveys/<int:id>/publish", methods=["POST"])
def publish_survey(id):
    try:
        data = request.get_json()
        flag = appService.publish_survey(id, data)
        if flag:
            cache_cleaner_all_surveys(id)
            return "Encuesta publicada", 200
        return jsonify({"error": "Survey not found or no permission to publish"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Preguntas de Encuestas
@app.route("/surveys/<int:id>/questions", methods=["POST"])
def insert_question(id):
    try:
        data = request.get_json()
        result = appService.insert_question(id, data)
        if result:
            cache_cleaner_all_surveys(id)
            cache_cleaner_questions(id)
            return jsonify(data), 201
        else:
            return jsonify({"error": "Failed to insert question"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/surveys/<int:id>/questions", methods=["GET"])
def get_questions(id):
    key = f"survey_questions:{id}"
    cached_questions = get_cache(key)
    if cached_questions:
        return cached_questions

    try:
        survey = appService.get_questions(id)
        if survey:
            redis_client.setex(key, 3600, json.dumps(survey))
            return jsonify(survey.get("Preguntas", []))
        return jsonify({"error": "Survey not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/surveys/<int:id>/questions/<int:questionId>", methods=["PUT"])
def update_question(id, questionId):
    data = request.get_json()
    try:
        data_db = appService.update_question(id, questionId, data)
        if data_db is None:
            return jsonify({"error": "Question not found or no permission to update"}), 404
        if '_id' in data_db:
            data_db['_id'] = str(data_db['_id'])
        cache_cleaner_all_surveys(id)
        cache_cleaner_questions(id)
        return data_db
    except Exception as e:
        return jsonify({"error": str(e)}), 

@app.route("/surveys/<int:id>/questions/<int:questionId>", methods=["DELETE"])
def delete_question(id, questionId):
    try:
        data = request.get_json()
        data_db = appService.delete_question(id, questionId, data)
        if data_db:
            cache_cleaner_all_surveys(id)
            cache_cleaner_questions(id)
            return "Pregunta eliminada\n" + str(data_db), 200
        return jsonify({"error": "Question not found or no permission to delete"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Respuestas de encuestas
@app.route("/surveys/<int:id>/responses", methods=["POST"])
def post_response(id):
    try:
        data = request.get_json()
        result = appService.post_response(id, data)
        if result:
            return str(data), 201
        else:
            return jsonify({"error": "Failed to insert response"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/surveys/<int:id>/responses", methods=["GET"])
def get_responses(id):
    try:
        responses = appService.get_responses(id)
        return str(responses)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#respondents
@app.route("/respondents", methods=["POST"])
def post_encuestado():
    try:
        data = request.get_json()
        result = appService.post_encuestado(data)
        if result:
            return str(data), 201
        else:
            return jsonify({"error": "Failed to insert response"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/respondents", methods=["GET"])
def get_encuestados():
    try:
        data = request.get_json()
        respondents = appService.get_encuestados(data)
        if respondents:
            return str(respondents)
        else:
            return jsonify({"error": "Failed to get respondents"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/respondents/<int:id>", methods=["GET"])
def get_encuestado(id):
    try:
        data = request.get_json()
        respondents = appService.get_encuestado(data, id)
        if respondents:
            return str(respondents)
        else:
            return jsonify({"error": "Failed to get respondents"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/respondents/<int:id>", methods=["PUT"])
def actualizar_encuestado(id):
    try:
        data = request.get_json()
        respondents = appService.actualizar_encuestado(id,data)
        if respondents:
            return str(respondents)
        else:
            return jsonify({"error": "Failed to get respondents"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/respondents/<int:id>", methods=["DELETE"])
def eliminar_encuestado(id):
    try:
        respondent = appService.eliminar_encuestado(id)
        return str(respondent)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#analytics
@app.route("/surveys/<int:id>/analysis", methods=["GET"])
def get_analytics(id):
    try:
        analysis = appService.get_analytics(id)
        return str(analysis)
    except Exception as e:
        return jsonify({"error": str(e)}), 500