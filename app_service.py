import json

from db import Database

class AppService:

    def __init__(self, database: Database):
        self.database = database

    # Métodos
    # Autenticación y Autorización
    def insert_user(self, user_data):
        self.database.insert_user(user_data)

    def login_user(self, user_data):
        return self.database.login_user(user_data)

    # Usuarios
    def get_users(self):
        return self.database.get_users()
    
    # Encuestas
    def insert_survey(self, data):
        return self.database.insert_survey(data)

    def get_surveys(self, page=1, limit=10):
        return self.database.get_surveys(page, limit)
    
    def get_specific_survey(self, id):
        return self.database.get_specific_survey(id)
    
    def update_survey(self, id, data):
        self.database.update_survey(id, data)
    
    def delete_survey(self, id, token):
        self.database.delete_survey(id, token)

    def publish_survey(self, id, token):
        self.database.publish_survey(id, token)