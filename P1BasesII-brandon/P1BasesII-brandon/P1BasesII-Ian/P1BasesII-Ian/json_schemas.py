survey_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        #"additionalProperties": False,
        "required": ["NumeroEncuesta", "Titulo", "IdAutor", "Autor", "FechaCreacion", "FechaActualizacion", "Disponible", "Preguntas"],
        "properties": {
            "NumeroEncuesta": {
                "bsonType": "int",
                "description": "must be an integer and is required"
            },
            "Titulo": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "IdAutor": {
                "bsonType": "int",
                "description": "must be an integer and is required"
            },
            "Autor": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "FechaCreacion": {
                "bsonType": "date",
                "description": "must be a datetime object and is required"
            },
            "FechaActualizacion": {
                "bsonType": "date",
                "description": "must be a datetime object and is required"
            },
            "Disponible": {
                "bsonType": "int",
                "description": "must be an integer and is required"
            },
            "Preguntas": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["Numero", "Categoria", "Pregunta"],
                    "properties": {
                        "Numero": {
                            "bsonType": "int",
                            "description": "must be an integer and is required"
                        },
                        "Categoria": {
                            "bsonType": "string",
                            "description": "must be a string and is required"
                        },
                        "Pregunta": {
                            "bsonType": "string",
                            "description": "must be a string and is required"
                        },
                        "Opciones": {
                            "bsonType": "array",
                            "items": {
                                "bsonType": ["string", "int"],
                                "description": "must be an array of strings or integers"
                            },
                            "description": "optional field, required for certain categories"
                        }
                    }
                },
                "description": "must be an array of questions and is required"
            }
        }
    }
}

answer_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        #"additionalProperties": False,
        "required": ["NumeroEncuesta", "IdEncuestado", "Nombre", "Correo", "FechaRealizado", "Preguntas"],
        "properties": {
            "NumeroEncuesta": {
                "bsonType": "int",
                "description": "must be an integer and is required"
            },
            "IdEncuestado": {
                "bsonType": "int",
                "description": "must be an integer and is required"
            },
            "Nombre": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "Correo": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "FechaRealizado": {
                "bsonType": "date",
                "description": "must be a datetime object and is required"
            },
            "Preguntas": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["Numero", "Categoria", "Pregunta", "Respuesta"],
                    "properties": {
                        "Numero": {
                            "bsonType": "int",
                            "description": "must be an integer and is required"
                        },
                        "Categoria": {
                            "bsonType": "string",
                            "description": "must be a string and is required"
                        },
                        "Pregunta": {
                            "bsonType": "string",
                            "description": "must be a string and is required"
                        },
                        "Respuesta": {
                            "bsonType": ["string", "array", "int"],
                            "description": "must be a string, an array, or an integer, depending on the question type"
                        }
                    }
                },
                "description": "must be an array of answers and is required"
            }
        }
    }
}