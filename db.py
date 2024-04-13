from pymongo import MongoClient
import psycopg2
from bson import ObjectId

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

    # Usuarios
    def get_users(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM OBTENER_USUARIOS();")
        users = cursor.fetchall()
        cursor.close()
        return users