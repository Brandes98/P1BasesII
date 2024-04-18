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
    # funcion para insertar usuario (registrar)
    def insert_user(self, nombre, idRol, correo, contrasena, fechaCreacion, fechaNacimiento, genero, idPais):
        cursor = self.conn.cursor()
        try:
            cursor.execute("CALL insertar_usuario(%s, %s, %s, %s, %s, %s, %s, %s)", (
                nombre, idRol, correo, contrasena, fechaCreacion, fechaNacimiento, genero, idPais))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()







    # Usuarios
    def get_users(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM OBTENER_USUARIOS();")
        users = cursor.fetchall()
        cursor.close()
        return users
    
    # log in
    def login(self, user_data):
        cursor = self.conn.cursor()
        cursor.execute("SELECT log_in(%s, %s);", (user_data["Correo"], user_data["Contrasenna"]))
        user = cursor.fetchone()
        cursor.close()
        return user
