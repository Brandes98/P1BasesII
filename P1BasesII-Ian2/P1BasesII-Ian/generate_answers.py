from faker import Faker
import random

jsonEncuestadosInfo = [
            {
                "Nombre": "EncuestasMX",
                "id" : 2,
                "Correo": "encuestas@dominio.com"
            },
            {
                "Nombre": "EncuestadoES",
                "id" : 3,
                "Correo": "encuestado@dominio.com"
            }
]

jsonFormatoRespuestas = {
	"NumeroEncuesta": 0,
	"IdEncuestado": 0,
	"Nombre": "",
    "Correo": "",
	"FechaRealizado": "",
	"Preguntas": []
}

jsonFormatoPregRespuestas = {
                        "Abiertas": {
                            "Numero": 0,
                            "Categoria": "Abiertas",
                            "Pregunta": "",
                            "Respuesta": ""
                        },
                        "EleccionSimples": {
                            "Numero": 0,
                            "Categoria": "EleccionSimples",
                            "Pregunta": "",
                            "Respuesta": ""
                        },
                        "EleccionMultiples": {
                            "Numero": 0,
                            "Categoria": "EleccionMultiples",
                            "Pregunta": "",
                            "Respuesta": []
                        },
                        "EscalaCalificacion": {
                            "Numero": 0,
                            "Categoria": "EscalaCalificacion",
                            "Pregunta": "",
                            "Respuesta": 0
                        },
                        "SiNo": {
                            "Numero": 0,
                            "Categoria": "SiNo",
                            "Pregunta": "",
                            "Respuesta": 0
                        },
                        "Numericas": {
                            "Numero": 0,
                            "Categoria": "Numericas",
                            "Pregunta": "",
                            "Respuesta": 0
                        }
}

def generate_answers(surveys):
    fake = Faker()
    rnd = random.Random()
    answers = []
    for i in range(len(surveys)):
        survey = surveys[i]
        if survey["Disponible"] == 1:
            cant_respuestas = 3
            answer = jsonFormatoRespuestas.copy()
            answer["NumeroEncuesta"] = survey["NumeroEncuesta"]
            for z in range(cant_respuestas):
                encuestado = rnd.choice(jsonEncuestadosInfo)
                answer["IdEncuestado"] = encuestado["id"]
                answer["Nombre"] = encuestado["Nombre"]
                answer["Correo"] = encuestado["Correo"]
                answer["FechaRealizado"] = fake.date_time().isoformat()
                questions = survey["Preguntas"]
                for j in range(len(questions)):
                    question = questions[j]
                    preg_resp = jsonFormatoPregRespuestas[question["Categoria"]].copy()
                    preg_resp["Numero"] = question["Numero"]
                    preg_resp["Categoria"] = question["Categoria"]
                    preg_resp["Pregunta"] = question["Pregunta"]
                    if question["Categoria"] == "Abiertas":
                        preg_resp["Respuesta"] = fake.text()
                    elif question["Categoria"] == "EleccionSimples":
                        preg_resp["Respuesta"] = rnd.choice(question["Opciones"])
                    elif question["Categoria"] == "EleccionMultiples":
                        cant_opciones = rnd.randint(1, len(question["Opciones"]))
                        preg_resp["Respuesta"] = rnd.sample(question["Opciones"], cant_opciones)
                    elif question["Categoria"] == "EscalaCalificacion":
                        preg_resp["Respuesta"] = rnd.randint(question["Opciones"][0], question["Opciones"][1])
                    elif question["Categoria"] == "SiNo":
                        preg_resp["Respuesta"] = rnd.randint(0, 1)
                    elif question["Categoria"] == "Numericas":
                        preg_resp["Respuesta"] = rnd.randint(1, 100)
                    answer["Preguntas"].append(preg_resp)
                answers.append(answer)     
    return answers
