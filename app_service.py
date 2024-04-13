import json

from db import Database

class AppService:

    def __init__(self, database: Database):
        self.database = database

    # Métodos
    # Autenticación y Autorización
    def insert_user(self, user_data):
        self.database.insert_user(user_data)

    # Usuarios
    def get_users(self):
        return self.database.get_users()