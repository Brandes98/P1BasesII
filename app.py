import json
import os
from pymongo import MongoClient
from bson import ObjectId
from app_service import AppService
from db import Database
from flask import Flask, request, jsonify
import redis

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

mongo_username = os.getenv("MONGO_INITDB_ROOT_USERNAME")
mongo_password = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
mongo_uri = f"mongodb://{mongo_username}:{mongo_password}@db:27017/"

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

db = Database(database=DB_NAME, host=DB_HOST, user=DB_USER, password=DB_PASSWORD, port=DB_PORT, uri=mongo_uri)

app = Flask(__name__)
mongodb_client = MongoClient(mongo_uri)
appService = AppService(db)

@app.route("/")
def home():
    return "App Works!!!"

# Autenticación y Autorización
@app.route("/auth/register", methods=["POST"])
def insert_user():
    user_data = request.get_json()
    appService.insert_user(user_data)
    return user_data

# Usuarios
@app.route("/users", methods=["GET"])
def get_users():
    users = appService.get_users()
    return jsonify(users)
