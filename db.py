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

    def get_paises(self):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT * FROM Paises;"
        )
        self.conn.commit()
        data = cursor.fetchall()
        cursor.close()
        return data