import json

from db import Database

class AppService:

    def __init__(self, database: Database):
        self.database = database

    def get_paises(self):
        paises = self.database.get_paises()
        return paises