import json

from db import Database

class AppService:

    def __init__(self, database: Database):
        self.database = database

    # Métodos
    # Autenticación y Autorización
   # def insert_user(self, user_data):
       # self.database.insert_user(user_data)
    # En AppService
    
    def insert_user(self, nombre, idRol, correo, contrasena, fechaCreacion, fechaNacimiento, genero, idPais):
        return self.database.insert_user(nombre, idRol, correo, contrasena, fechaCreacion, fechaNacimiento, genero, idPais)



    # Usuarios
    def get_users(self):
        return self.database.get_users()
    
    #log in
    def login(self, user_data):
        return self.database.login(user_data)