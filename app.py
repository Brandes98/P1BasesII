import json
import os
from pymongo import MongoClient
from bson import ObjectId
from app_service import AppService
from db import Database
from flask import Flask, request, jsonify
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

def invalidate_cache():
    for key in redis_client.scan_iter("surveys:*"):
        redis_client.delete(key)

def datetime_converter(o):
    if isinstance(o, datetime):
        return o.__str__()

@app.route("/")
def home():
    return "App Works!!!"

# Autenticación y Autorización
@app.route("/auth/register", methods=["POST"])
def insert_user():
    user_data = request.get_json()
    appService.insert_user(user_data)
    return user_data

@app.route("/auth/login", methods=["POST"])
def login_user():
    user_data = request.get_json()
    token = appService.login_user(user_data)
    return token

# Usuarios
@app.route("/users", methods=["GET"])
def get_users():
    users = appService.get_users()
    return jsonify(users)

# Encuestas
@app.route("/surveys", methods=["POST"])
def insert_survey():
    try:
        data = request.get_json()
        inserted_id = appService.insert_survey(data)
        data['_id'] = str(inserted_id) 
        return jsonify(data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/surveys/page=<int:num_page>", methods=["GET"])
def get_surveys(num_page):
    page = int(request.args.get('page', num_page))
    limit = int(request.args.get('limit', 10))
    cache_key = f"surveys:{page}:{limit}"

    # Try to fetch the result from cache
    cached_surveys = redis_client.get(cache_key)
    if cached_surveys:
        return jsonify(json.loads(cached_surveys))  # Load JSON string from cache and convert to JSON

    # If not cached, fetch from the database
    try:
        surveys = appService.get_surveys(page, limit)
        # Serialize with custom datetime handler
        serialized_data = json.dumps(surveys, default=datetime_converter)
        redis_client.setex(cache_key, 3600, serialized_data)  # Cache for 1 hour
        return jsonify(surveys)
    except ValueError:
        return jsonify({"error": "Invalid page or limit value"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/surveys/<int:id>", methods=["GET"])
def get_specific_survey(id):
    survey = appService.get_specific_survey(id)
    return survey

@app.route("/surveys/<int:id>", methods=["PUT"])
def update_survey(id):
    data = request.get_json()
    appService.update_survey(id, data)
    return data

@app.route("/surveys/<int:id>", methods=["DELETE"])
def delete_survey(id):
    token = request.get_json()
    appService.delete_survey(id, token)
    return "Encuesta eliminada"

@app.route("/surveys/<int:id>/publish", methods=["POST"])
def publish_survey(id):
    token = request.get_json()
    appService.publish_survey(id)
    return "Encuesta publicada"