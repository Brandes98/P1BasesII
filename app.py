import datetime
import json
import os
import time
from pymongo import MongoClient
from bson import ObjectId
from app_service import AppService
from db import Database
from flask import Flask, request, jsonify
import redis
from flask import jsonify
from flask import abort

#pasen esto a un archivo .env
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
    
    try:
        appService.insert_user(nombre, idRol, correo, contrasena, fechaCreacion, fechaNacimiento, genero, idPais)
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

# Autenticación y Autorización
@app.route("/auth/login", methods=["POST"])
def login():
    user_data = request.form.to_dict()
    user = appService.login(user_data)
    if user:
        return jsonify(user)
    else:
        abort(401)
        
# Usuarios
@app.route("/users", methods=["GET"])
def get_users():
    users = appService.get_users()
    return jsonify(users)
