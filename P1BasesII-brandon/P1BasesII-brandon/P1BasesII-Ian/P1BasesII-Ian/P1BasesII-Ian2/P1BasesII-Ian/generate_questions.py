from faker import Faker
import random

jsonAutoresInfo = [
            {
                "Nombre": "AdminCR",
                "id" : 1
            },
            {
                "Nombre": "EncuestasMX",
                "id" : 2
            }
]

jsonFormatoEncuestas = {
	"NumeroEncuesta": 0,
	"Titulo": "",
	"IdAutor": 0,
	"Autor": "",
	"FechaCreacion": "",
	"FechaActualizacion": "",
	"Disponible": 1,
	"Preguntas": []
}

jsonFormatosPreguntas = [{
                            "Numero": 0,
                            "Categoria": "Abiertas",
                            "Pregunta": ""
                        },
                        {
                            "Numero": 0,
                            "Categoria": "EleccionSimples",
                            "Pregunta": "",
                            "Opciones": []
                        },
                        {
                            "Numero": 0,
                            "Categoria": "EleccionMultiples",
                            "Pregunta": "",
                            "Opciones": []
                        },
                        {
                            "Numero": 0,
                            "Categoria": "EscalaCalificacion",
                            "Pregunta": "",
                            "Opciones": []
                        },
                        {
                            "Numero": 0,
                            "Categoria": "SiNo",
                            "Pregunta": ""
                        },
                        {
                            "Numero": 0,
                            "Categoria": "Numericas",
                            "Pregunta": ""
                        }
]

def generate_options_number():
    fake = Faker()
    rnd = random.Random()
    min = rnd.randint(1, 5)
    max = rnd.randint(6, 10)
    opciones = [min, max]
    return [min, max]

def generate_options_word():
    fake = Faker()
    rnd = random.Random()
    cant_opciones = rnd.randint(4, 6)
    opciones = []
    for i in range(1, cant_opciones+1):
        opcion = fake.word()
        opciones.append(opcion)
    return opciones

def generate_questions():
    fake = Faker()
    rnd = random.Random()
    cant_preguntas = rnd.randint(5, 10)
    preguntas = []
    for i in range(1, cant_preguntas+1):
        tipo_pregunta = rnd.randint(0, 5)
        pregunta = jsonFormatosPreguntas[tipo_pregunta].copy()
        if tipo_pregunta in [1, 2, 3]:
            pregunta["Opciones"] = generate_options_number() if tipo_pregunta == 3 else generate_options_word()
        pregunta["Numero"] = i
        pregunta["Pregunta"] = fake.sentence()
        preguntas.append(pregunta)
    return preguntas

def generate_surveys():
    fake = Faker()
    rnd = random.Random()
    cant_encuestas = 10
    encuestas = []
    for i in range(1, cant_encuestas+1):
        encuesta = jsonFormatoEncuestas.copy()
        encuesta["NumeroEncuesta"] = i
        encuesta["Titulo"] = fake.sentence()
        encuesta["IdAutor"] = rnd.choice(jsonAutoresInfo)["id"]
        encuesta["Autor"] = jsonAutoresInfo[encuesta["IdAutor"] - 1]["Nombre"]
        encuesta["FechaCreacion"] = fake.date()
        encuesta["FechaActualizacion"] = fake.date()
        encuesta["Disponible"] = 1
        encuesta["Preguntas"] = generate_questions()
        encuestas.append(encuesta)
    return encuestas