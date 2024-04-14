from pymongo import MongoClient
import psycopg2
from bson import ObjectId
from datetime import datetime

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

    # Métodos
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