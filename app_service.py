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

    def login(self, user_data):
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
    
    # Preguntas de encuestas
    def insert_question(self, id, data):
        return self.database.insert_question(id, data)
    
    def get_questions(self, id):
        return self.database.get_questions(id)
    
    def update_question(self, id, questionId, data):
        return self.database.update_question(id, questionId, data)
    
    def delete_question(self, id, questionId, data):
        return self.database.delete_question(id, questionId, data)
    def post_response(self, id, data):
        return self.database.post_response(id, data)
    def get_responses(self, id):
        return self.database.get_responses(id)
    def post_encuestado(self, data):
        return self.database.post_encuestado(data)
    def get_encuestados(self, data):
        return self.database.get_encuestados(data)
    def get_encuestado(self,data, id):
        return self.database.get_encuestado(data, id)
    def actualizar_encuestado(self, id, data):
        return self.database.actualizar_encuestado(id, data)
    def eliminar_encuestado(self, id):
        return self.database.eliminar_encuestado(id)
    def get_analytics(self, id):
        return self.database.get_analytics(id)