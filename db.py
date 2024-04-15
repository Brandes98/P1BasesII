from pymongo import MongoClient
import psycopg2
from bson import ObjectId
from datetime import datetime
import json

class Database:
    def __init__(
            self, database="db_name", host="db_host", user="db_user", 
            password="db_pass", port="db_port", uri="mongodb://localhost:27017/"):
        
        # PostgreSQL
        self.conn = psycopg2.connect(
            database=database, host=host, user=user, password=password, port=port)
       
        # MongoDB
        self.client = MongoClient(uri)
        self.db = self.client[database]
        self.encuestas = self.db["encuestas"]
        self.respuestas = self.db["respuestas"]
        #self.insert_surveys_mongodb()
        #self.insert_answers_mongodb()

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