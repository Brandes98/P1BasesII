import json

from db import Database

class AppService:

    def __init__(self, database: Database):
        self.database = database

    def test(self, data):
        """
        JSON EXAMPLE:
        {
            "idAutor": 1,
            "num_encuesta": 1,
            "token": "1"
        }
        """
        #idAutor = data["idAutor"]
        #num_encuesta = data["num_encuesta"]
        token = data["Token"]
        #return self.database.verify_token_creator_survey(idAutor, num_encuesta, token)
        return self.database.verify_token_create_surveys(token)

    # Métodos
    # Autenticación y Autorización
    def insert_user(self, user_data):
        return self.database.insert_user(user_data)

    def login_user(self, user_data):
        return self.database.login_user(user_data)

    # Usuarios
    def get_users(self):
        return self.database.get_users()
    
    # Encuestas
    def insert_survey(self, data):
        return self.database.insert_survey(data)

    def get_public_surveys(self, page=1, limit=10):
        return self.database.get_public_surveys(page, limit)
    
    def get_specific_survey(self, id):
        return self.database.get_specific_survey(id)
    
    def update_survey(self, id, data):
        return self.database.update_survey(id, data)
    
    def delete_survey(self, id, data):
        return self.database.delete_survey(id, data)

    def publish_survey(self, id, data):
        return self.database.publish_survey(id, data)