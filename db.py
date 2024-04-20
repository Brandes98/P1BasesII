from pymongo import MongoClient
from flask import request, jsonify
from bson import ObjectId
from datetime import datetime
from json_schemas import survey_schema, answer_schema
import psycopg2
import json
import redis
import os
from bson import json_util

class Database:
    def __init__(
            self, database="db_name", host="db_host", user="db_user", 
            password="db_pass", port="db_port", uri="mongodb:mongoadmin:mongosecretmongodb:27017/",
            redis_host='redis', redis_port=6379, redis_db=0):
        self.conn = None
        # PostgreSQL
        self.conn = psycopg2.connect(
            database=database, host=host, user=user, password=password, port=port)
       
        # MongoDB
        self.client = MongoClient(uri)
        self.db = self.client[database]

        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

        self.encuestas = self.create_or_update_collection("encuestas", survey_schema)
        self.encuestas.create_index([("NumeroEncuesta", 1)], unique=True)
        self.respuestas = self.create_or_update_collection("respuestas", answer_schema)

        self.insert_surveys_mongodb()
        self.insert_answers_mongodb()

    # Métodos
    def get_connection(self):
        if self.conn is None:
            self.conn = psycopg2.connect(
                database=os.getenv("DB_NAME"),
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                port=os.getenv("DB_PORT")
            )
        return self.conn
    
    def get_mongo_conection(self):
        if self.client is None:
            self.client = MongoClient(mongo_uri = f"mongodb://mongoadmin:mongosecret@mongodb:27017/")
        return self.client
    
    def get_redis_connection(self):
        if self.redis_client is None:
            self.redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)
        return self.redis_client
    
    # funcion para insertar usuario (registrar)
    def insert_user(self, nombre, idRol, correo, contrasena, fechaCreacion, fechaNacimiento, genero, idPais):
        cursor = self.conn.cursor()
        try:
            cursor.execute("CALL insertar_usuario(%s, %s, %s, %s, %s, %s, %s, %s)", (
                nombre, idRol, correo, contrasena, fechaCreacion, fechaNacimiento, genero, idPais))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()

    def create_or_update_collection(self, collection_name, schema):
        schema_for_db = {'validator': schema}  
        if collection_name not in self.db.list_collection_names():
            self.db.create_collection(collection_name, **schema_for_db)
        else:
            self.db.command('collMod', collection_name, **schema_for_db)
        return self.db[collection_name]

    # Métodos
    # Insertar datos MongoDB
    def insert_surveys_mongodb(self):
        if self.encuestas.count_documents({}) == 0:
            with open('data_surveys.jsonl', 'r') as file:
                for line in file:
                    data = json.loads(line)
                    data['FechaCreacion'] = datetime.fromisoformat(data['FechaCreacion'])
                    data['FechaActualizacion'] = datetime.fromisoformat(data['FechaActualizacion'])
                    self.encuestas.insert_one(data)

    def insert_answers_mongodb(self):
        if self.respuestas.count_documents({}) == 0:
            with open('data_answers.jsonl', 'r') as file:
                for line in file:
                    data = json.loads(line)
                    data['FechaRealizado'] = datetime.fromisoformat(data['FechaRealizado'])
                    self.respuestas.insert_one(data)

    # Verificar data
    def verify_author(self, idAutor):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM Usuarios WHERE id = %s;", (idAutor,))
        user = cursor.fetchone()
        cursor.close()
        return True if user else False

    # Verificar token
    def get_token(self, token):
    # First, attempt to retrieve the token's role ID from Redis cache
        cached_role_id = self.redis_client.get(f"token:{token}")
        if cached_role_id:
            return int(cached_role_id)  # Convert to int because Redis stores data as strings

        # If the role ID is not in the cache, query the database
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT U.idRol FROM Logs AS L INNER JOIN Usuarios AS U ON L.IdUsuario = U.id WHERE L.Token = %s;", (token,))
            user = cursor.fetchone()
        finally:
            cursor.close()

        # Check if the query returned a result
        if user:
            role_id = user[0]
            # Cache the result in Redis with an expiration (e.g., 10 minutes)
            self.redis_client.setex(f"token:{token}", 600, role_id)
            return role_id

        # If no user is found, optionally cache this negative result to prevent database hits for invalid tokens
        self.redis_client.setex(f"token:{token}", 600, 0)
        return 0

    
    def verify_token_admin(self, token):
        return self.get_token(token) == 1
    
    def verify_token_active(self, token):
        cached_active_status = self.redis_client.get(f"token_active:{token}")
        if cached_active_status is not None:
            return cached_active_status == 'true' 
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT U.id FROM Logs AS L INNER JOIN Usuarios AS U ON L.IdUsuario = U.id WHERE L.Token = %s AND L.FechaLogOut IS NULL;", (token,))
            user = cursor.fetchone()
        finally:
            cursor.close()

        is_active = True if user else False

        self.redis_client.setex(f"token_active:{token}", 300, 'true' if is_active else 'false')

        return is_active
        
    def verify_token_create_surveys(self, token):
        return self.get_token(token) in [1, 2]
    
    def verify_token_user(self, idAutor, token):
        cache_key = f"token_user:{token}:{idAutor}"
        cached_user = self.redis_client.get(cache_key)
        if cached_user:
            return json.loads(cached_user)  

        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT U.id, U.idRol FROM Logs AS L
                INNER JOIN Usuarios AS U ON L.IdUsuario = U.id
                WHERE L.Token = %s AND U.id = %s AND L.FechaLogOut IS NULL;
            """, (token, idAutor))
            user = cursor.fetchone()
        finally:
            cursor.close()
        if user:
            self.redis_client.setex(cache_key, 600, json.dumps(user))  
            return user

        self.redis_client.setex(cache_key, 600, json.dumps(None))
        return None

    def verify_token_creator_survey(self, idAutor, num_encuesta, token):
        user = self.verify_token_user(idAutor, token)
        author = self.verify_author(idAutor)
        if not user or not author:
            return False 
        if user[1] == 1:
            return True
        elif user[1] == 2:
            survey = self.encuestas.find_one({"NumeroEncuesta": num_encuesta, "IdAutor": idAutor})
            return survey["IdAutor"] == user[0]
        return False

    # Autenticación y Autorización
    def login_user(self, user_data):
        cursor = self.conn.cursor()
        token = None
        fecha = datetime.now()
        cursor.execute(
            "SELECT LOGIN_USUARIO(%s, %s, %s, %s);",
            (user_data['Correo'], user_data['Contrasenna'], fecha, token)
        )
        # Obtener el valor de salida actualizado
        token = cursor.fetchone()[0]
        cursor.close()
        return token 
    
    def insert_user(self, nombre, idRol, correo, contrasena, fechaCreacion, fechaNacimiento, genero, idPais):
        cursor = self.conn.cursor()
        try:
            cursor.execute("CALL insertar_usuario(%s, %s, %s, %s, %s, %s, %s, %s)", (
                nombre, idRol, correo, contrasena, fechaCreacion, fechaNacimiento, genero, idPais))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()

    # Usuarios
    def get_users(self):
        cache_key = "all_users"

        # Attempt to retrieve the list of users from Redis
        cached_users = self.redis_client.get(cache_key)
        if cached_users:
            # Parse the JSON into Python data structures
            users = json.loads(cached_users)
            # Return the data
            return jsonify({"status": "success", "data": users}), 200

        # Execute the query on the database
        cursor = self.conn.cursor()
        cursor.execute("""
                SELECT U.id, U.Nombre, R.Nombre AS RoleName, U.Correo, U.FechaCreacion, 
                    U.FechaNacimiento, OBTENER_GENERO(U.Genero) AS Gender, P.Nombre AS Country
                FROM Usuarios AS U
                INNER JOIN Roles AS R ON U.idRol = R.id
                INNER JOIN Paises AS P ON U.idPais = P.id;
            """)
        users = cursor.fetchall()
        cursor.close()

        # Check if the query returned no results
        if users is None:
            # Return a 500 error if the query failed unexpectedly
            return jsonify({"status": "error", "message": "Error interno del servidor al recuperar usuarios"}), 500

        # Convert users from tuples to lists and handle datetime conversion
        updated_users = []
        for user in users:
            user_list = list(user)
            user_list[4] = user_list[4].strftime("%Y-%m-%dT%H:%M:%S") if user_list[4] else None
            user_list[5] = user_list[5].strftime("%Y-%m-%dT%H:%M:%S") if user_list[5] else None
            updated_users.append(user_list)

        # Store the result in Redis and return
        self.redis_client.setex(cache_key, 3600, json.dumps(updated_users))
        return jsonify({"status": "success", "data": updated_users}), 200
    
    def get_user(self, id):
        cache_key = f"user:{id}"
        cached_user = self.redis_client.get(cache_key)
        if cached_user:
            return json.loads(cached_user)

        cursor = self.conn.cursor()
        cursor.execute("""
                SELECT U.id, U.Nombre, R.Nombre AS RoleName, U.Correo, U.FechaCreacion, 
                    U.FechaNacimiento, OBTENER_GENERO(U.Genero) AS Gender, P.Nombre AS Country
                FROM Usuarios AS U
                INNER JOIN Roles AS R ON U.idRol = R.id
                INNER JOIN Paises AS P ON U.idPais = P.id
                WHERE U.id = %s;
            """, (id,))
        user = cursor.fetchone()
        cursor.close()
        
        if user is None:
            # Return a 500 error if the query failed unexpectedly
            return jsonify({"status": "error", "message": "Error interno del servidor al recuperar usuarios"}), 500

        # Convert users from tuples to lists and handle datetime conversion
        user = list(user)
        user[4] = user[4].strftime("%Y-%m-%dT%H:%M:%S") if user[4] else None
        user[5] = user[5].strftime("%Y-%m-%dT%H:%M:%S") if user[5] else None

        return jsonify(user), 200

    def update_user(self, id, data):
        cursor = self.conn.cursor()
        cursor.execute("""
                SELECT U.id FROM Usuarios AS U WHERE U.id = %s;""", (id,))
        user = cursor.fetchone()
        cursor.execute("""
                UPDATE Usuarios SET 
                Nombre = %s, 
                Correo = %s, 
                Contrasenna = %s, 
                FechaNacimiento = %s, 
                Genero = %s, 
                idPais = %s 
                WHERE id = %s;
            """, (data['Nombre'], data['Correo'], data['Contrasenna'], data['FechaNacimiento'], data['Genero'], data['idPais'], id))
        self.conn.commit()
        cursor.close()

        cache_key = f"user:{id}"
        self.redis_client.delete(cache_key)
        if user:
            return jsonify({"status": "success", "message": "Usuario actualizado correctamente"}), 200
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404
    
    def delete_user(self, id, data):
        cursor = self.conn.cursor()
        cursor.execute("""
                SELECT U.id FROM Usuarios AS U WHERE U.id = %s;""", (id,))
        user = cursor.fetchone()
        cursor.execute("""
                DELETE FROM Usuarios WHERE id = %s;
            """, (id,))
        self.conn.commit()
        cursor.close()

        cache_key = f"user:{id}"
        self.redis_client.delete(cache_key)
        if user:
            return jsonify({"status": "success", "message": "Usuario eliminado correctamente"}), 200
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404
    
    # Encuestas
    def login(self, user_data):
        cursor = self.conn.cursor()
        cursor.execute("SELECT log_in(%s, %s);", (user_data["Correo"], user_data["Contrasenna"]))
        user = cursor.fetchone()
        cursor.close()
        return user
    
    def insert_survey(self, data):
        try:
            token = data.pop("Token", None)
            if not token:
                raise ValueError("Token is required")
    
            cache_key = f"token_permission:{token}"
            
            permission_cached = self.redis_client.get(cache_key)
            
            if permission_cached:
                if permission_cached == 'denied':
                    raise Exception("You don't have permission to create this survey from cache.")
            else:
                if self.verify_token_create_surveys(token):
                    self.redis_client.setex(cache_key, 600, 'allowed')  
                else:
                    self.redis_client.setex(cache_key, 600, 'denied') 
                    raise Exception("You don't have permission to create this survey.")
            
            data['FechaCreacion'] = datetime.fromisoformat(data['FechaCreacion'])
            data['FechaActualizacion'] = datetime.fromisoformat(data['FechaActualizacion'])
            insert_result = self.encuestas.insert_one(data)
            return insert_result
        except ValueError as ve:
            raise ValueError(str(ve))
        except Exception as e:
            raise Exception(f"An error occurred during survey insertion: {str(e)}")

    def datetime_converter(o):
        if isinstance(o, datetime):
            return o.isoformat()
        
    def get_public_surveys(self, page=1, limit=10):
        offset = (page - 1) * limit
        surveys = self.encuestas.find({"Disponible": 1}).skip(offset).limit(limit)
        result = []
        for survey in surveys:
            survey['_id'] = str(survey['_id'])
            result.append(survey)
        return result

    def get_specific_survey(self, id):
        cache_key = f"survey:{id}"
        cached_survey = self.redis_client.get(cache_key)
        if cached_survey:
            return json.loads(cached_survey)  
        survey = self.encuestas.find_one({"NumeroEncuesta": id})
        if survey:
            survey['_id'] = str(survey['_id'])  
            self.redis_client.setex(cache_key, 3600, json.dumps(survey))
        else:
            survey = None
            self.redis_client.setex(cache_key, 3600, json.dumps(None))
        return survey
    
    def update_survey(self, id, data):
        token = data.pop('Token', None)
        idAutor = data.get('IdAutor')
        if not self.verify_token_creator_survey(idAutor, id, token):
            return None  
        data['FechaCreacion'] = datetime.fromisoformat(data['FechaCreacion'])
        data['FechaActualizacion'] = datetime.fromisoformat(data['FechaActualizacion'])
        update_result = self.encuestas.update_one({"NumeroEncuesta": id}, {"$set": data})
        if update_result.modified_count == 0:
            return None 
        cache_key = f"survey:{id}"
        updated_survey = self.encuestas.find_one({"NumeroEncuesta": id})
        if updated_survey:
            updated_survey['_id'] = str(updated_survey['_id']) 
            self.redis_client.setex(cache_key, 3600, json.dumps(updated_survey)) 
        else:
            self.redis_client.delete(cache_key) 
        return updated_survey
    
    def delete_survey(self, id, data):
        token = data.pop('Token', None)
        idAutor = data.get('IdAutor')
        if not self.verify_token_creator_survey(idAutor, id, token):
            return False  
        delete_result = self.encuestas.delete_one({"NumeroEncuesta": id})
        if delete_result.deleted_count == 0:
            return False  
        cache_key = f"survey:{id}"
        self.redis_client.delete(cache_key)  
        return True

    def publish_survey(self, id, data):
        token = data.pop('Token', None)
        idAutor = data.get('IdAutor')
        if not self.verify_token_creator_survey(idAutor, id, token):
            return False  
        update_result = self.encuestas.update_one({"NumeroEncuesta": id}, {"$set": {"Disponible": 1}})
        if update_result.modified_count == 0:
            return False  
        cache_key = f"survey:{id}"
        updated_survey = self.encuestas.find_one({"NumeroEncuesta": id})
        if updated_survey:
            updated_survey['_id'] = str(updated_survey['_id']) 
            self.redis_client.setex(cache_key, 3600, json.dumps(updated_survey))  
        else:
            self.redis_client.delete(cache_key)  
        return True

    # Preguntas de encuestas
    def insert_question(self, id, data):
        """
        JSON EXAMPLE:
        {
            "IdAutor": 1,
            "Token": "1",
            "Preguntas": {
                "Numero": 0,
                "Categoria": "SiNo",
                "Pregunta": "¿Tiene hambre?"
            }
        }
        """
 
        token = data.pop('Token', None)
        idAutor = data.get('IdAutor')
        if not self.verify_token_creator_survey(idAutor, id, token):
            return False  
        cache_key = f"survey_questions:{id}"
        cached_survey = self.redis_client.get(cache_key)

        if cached_survey:
            survey_questions = json.loads(cached_survey)
        else:
            survey_questions = self.encuestas.find_one({"NumeroEncuesta": id}, {"Preguntas": 1})
            if not survey_questions:
                return False  
        max_number = max((q['Numero'] for q in survey_questions['Preguntas']), default=0)
        for question in data['Preguntas']:
            max_number += 1
            question['Numero'] = max_number
            survey_questions['Preguntas'].append(question)
        update_result = self.encuestas.update_one(
            {"NumeroEncuesta": id},
            {"$set": {"Preguntas": survey_questions['Preguntas']}}
        )
        if update_result.modified_count == 0:
            return False  
        self.redis_client.setex(cache_key, 3600, json.dumps(survey_questions['Preguntas'])) 
        return True

    def get_questions(self, id):
        cache_key = f"survey_questions:{id}"
        cached_questions = self.redis_client.get(cache_key)
        if cached_questions:
            return json.loads(cached_questions)
        survey_questions = self.encuestas.find_one({"NumeroEncuesta": id}, {"_id": 0, "Preguntas": 1})
        if survey_questions and 'Preguntas' in survey_questions:
            self.redis_client.setex(cache_key, 3600, json.dumps(survey_questions['Preguntas'])) 
            return survey_questions['Preguntas']
        self.redis_client.setex(cache_key, 600, json.dumps(None))  
        return None
    
    def update_question(self, id, questionId, data):
        token = data.pop('Token', None)
        idAutor = data.get('IdAutor')
        if not self.verify_token_creator_survey(idAutor, id, token) or len(data["Preguntas"]) != 1:
            return None
        survey_questions = self.encuestas.find_one({"NumeroEncuesta": id}, {"_id": 0, "Preguntas": 1})
        if not survey_questions:
            return None 
        for question in survey_questions['Preguntas']:
            if question['Numero'] == questionId:
                question.update(data['Preguntas'][0])
                update_result = self.encuestas.update_one(
                    {"NumeroEncuesta": id, "Preguntas.Numero": questionId},
                    {"$set": {"Preguntas.$": data['Preguntas'][0]}}
                )
                if update_result.modified_count == 0:
                    return None 
                cache_key = f"survey_questions:{id}"
                self.redis_client.delete(cache_key)  
                self.redis_client.setex(cache_key, 3600, json.dumps(survey_questions['Preguntas'])) 
                return data['Preguntas'][0]  
        return None  
    
    def delete_question(self, id, questionId, data):
        token = data.pop('Token', None)
        idAutor = data.get('IdAutor')
        if not self.verify_token_creator_survey(idAutor, id, token):
            return None 
        survey = self.encuestas.find_one({"NumeroEncuesta": id}, {"_id": 0, "Preguntas": 1})
        if not survey:
            return None 
        updated_questions = [question for question in survey['Preguntas'] if question['Numero'] != questionId]
        if len(updated_questions) == len(survey['Preguntas']):
            return None
        self.encuestas.update_one(
            {"NumeroEncuesta": id},
            {"$set": {"Preguntas": updated_questions}}
        )

        cache_key = f"survey_questions:{id}"
        self.redis_client.delete(cache_key)
        self.redis_client.setex(cache_key, 3600, json.dumps(updated_questions)) 

        return updated_questions 

    #verificado
    def post_response(self, id, data):
        token = data.pop('Token', None)
        if not self.verify_token_active(token):
            return None  # Return None if the token is not active

        # Convert the datetime string to a datetime object
        data['FechaRealizado'] = datetime.fromisoformat(data['FechaRealizado'])
        
        # Insert the response data into the database
        insert_result = self.respuestas.insert_one(data)
        if insert_result.inserted_id:
            # Cache key for the survey's responses summary
            cache_key = f"survey_responses_summary:{id}"

            # Fetch updated response statistics or metadata
            updated_summary = self.fetch_response_summary(id)

            # Update the cache with the new summary
            self.redis_client.setex(cache_key, 3600, json.dumps(updated_summary))  # Cache for 1 hour

            return data
        return None
    
    def fetch_response_summary(self, survey_id):
    # Count responses for the survey
        response_count = self.respuestas.count_documents({"NumeroEncuesta": survey_id})

        # Fetch the latest response
        latest_response_cursor = self.respuestas.find({"NumeroEncuesta": survey_id}).sort('FechaRealizado', -1).limit(1)
        latest_response = list(latest_response_cursor)
        latest = latest_response[0] if latest_response else None

        # If 'latest' is not None, prepare it for JSON serialization (if needed)
        if latest:
            latest['_id'] = str(latest['_id'])
            if isinstance(latest.get('FechaRealizado'), datetime):
                latest['FechaRealizado'] = latest['FechaRealizado'].isoformat()

        summary = {
            "response_count": response_count,
            "latest_response": latest
        }
        return summary
    
#verificado
    def get_responses(self, id):
        cache_key = f"survey_responses:{id}"
        cached_responses = self.redis_client.get(cache_key)
        if cached_responses:
            return json.loads(cached_responses)

        responses = self.respuestas.find({"NumeroEncuesta": id})
        result = []
        for response in responses:
            response['_id'] = str(response['_id'])  # Convert ObjectId to string
            result.append(response)

        # Use json_util to serialize MongoDB documents including datetime fields
        serialized_data = json.dumps(result, default=json_util.default)

        self.redis_client.setex(cache_key, 3600, serialized_data)
        return result
    

    def post_encuestado(self, data):
        cursor = self.conn.cursor()
        try:
            # Ensure date is in the correct format
            try:
                data['FechaNacimiento'] = datetime.fromisoformat(data['FechaNacimiento'])
            except ValueError as e:
                return {"error": f"Incorrect date format: {e}"}

            # Execute SQL command to insert new user
            try:
                cursor.execute("""
                    INSERT INTO Usuarios (Nombre, idRol, Correo, Contrasenna, FechaCreacion, FechaNacimiento, Genero, idPais)
                    VALUES (%s, %s, %s, %s, NOW(), %s, %s, %s) RETURNING id;
                """, (data['Nombre'], 3, data['Correo'], data['Contrasenna'], data['FechaNacimiento'], data['Genero'], data['idPais']))
                user = cursor.fetchone()
            except psycopg2.Error as e:
                self.conn.rollback()  # Rollback the transaction in case of error
                return {"error": f"Database error: {e.pgerror}"}

            if user:
                # Update cache to include new user data if needed
                cache_key = "users_list"
                cached_users = self.redis_client.get(cache_key)
                if cached_users:
                    users_list = json.loads(cached_users)
                    users_list.append(data)  # Consider storing a sanitized version of data
                    self.redis_client.setex(cache_key, 3600, json.dumps(users_list))

                return {"success": True, "id": user[0]}
            else:
                return {"error": "User was not inserted successfully."}

        finally:
            cursor.close()
    
    def datetime_serializer(self,obj):
            """Custom JSON serializer for datetime objects."""
            if isinstance(obj, datetime):
                return obj.isoformat()  # Convert datetime to ISO 8601 string.

    def get_encuestados(self,data): # requiere token
        token = data.pop('Token', None)
        idAutor = data.get('IdAutor')
        if self.verify_token_creator_survey(idAutor, id, token):
            cursor = self.conn.cursor()
            cursor.execute("SELECT (U.id, U.Nombre, U.Correo, U.FechaCreacion, U.FechaNacimiento, OBTENER_GENERO(U.Genero), P.Nombre) FROM Usuarios AS U INNER JOIN Paises AS P ON U.idPais = P.id WHERE U.idRol = 3;")
            respondents = cursor.fetchall()
            cursor.close()
            return respondents
        return None
    
    def get_encuestado(self,data, id):
        token = data.pop('Token', None)
        idAutor = data.get('IdAutor')
        if self.verify_token_creator_survey(idAutor, id, token):
            cursor = self.conn.cursor()
            cursor.execute("SELECT (U.id, U.Nombre, U.Correo, U.FechaCreacion, U.FechaNacimiento, OBTENER_GENERO(U.Genero), P.Nombre) FROM Usuarios AS U INNER JOIN Paises AS P ON U.idPais = P.id WHERE U.idRol = 3 AND U.id = %s;", (id,))
            respondent = cursor.fetchone()
            cursor.close()
            return respondent
        return None
    
    def actualizar_encuestado(self, id, data):
        token = data.pop('Token', data)
        idAutor = data.get('IdAutor')
        
        # Verify if the user has permission to update the respondent's details
        if not self.verify_token_creator_survey(idAutor, data, token):
            return False  # Return False if the token verification fails or user has no permission

        # Proceed to update the database
        cursor = self.conn.cursor()
        print("Updating database with:", data['Nombre'], data['Correo'], data['Contrasenna'], data['FechaNacimiento'], data['Genero'], data['idPais'], id)
        cursor.execute("""
                UPDATE Usuarios SET 
                Nombre = %s, 
                Correo = %s, 
                Contrasenna = %s, 
                FechaNacimiento = %s, 
                Genero = %s, 
                idPais = %s 
                WHERE id = %s;
            """, (data['Nombre'], data['Correo'], data['Contrasenna'], data['FechaNacimiento'], data['Genero'], data['idPais'], id))
        cursor.close()
            
            # Cache key for this specific respondent
        cache_key = f"encuestado:{id}"
            
            # Invalidate or update the cache after updating the respondent's details
            # Assuming the cache should now hold the updated details
        self.redis_client.setex(cache_key, 3600, json.dumps(data))  # Cache the updated data for 1 hour

        return True
        
    def eliminar_encuestado(self, id):
        token = request.headers.get("Token", None)
        if not self.verify_token_active(token):
            return False  # Return False if the token is not valid or active

        try:
            with self.conn.cursor() as cursor:
                # Execute SQL command to delete the user based on id
                cursor.execute("DELETE FROM Usuarios WHERE id = %s;", (id,))
                self.conn.commit()  # Commit the transaction to finalize the deletion

                # Invalidate the cache if the deletion was successful
                if cursor.rowcount > 0:
                    # Cache key for the respondent
                    cache_key = f"encuestado:{id}"
                    # Remove the cached data for the deleted respondent
                    self.redis_client.delete(cache_key)
                    return True  # Return True if the deletion affected at least one row
                else:
                    return False  # Return False if no rows were affected (user not found)

        except Exception as e:
            # If an exception occurred, rollback any changes and print the error
            self.conn.rollback()
            print(f"Error deleting respondent: {e}")
            return False

def get_analytics(self, id):
    cache_key = f"survey_analytics:{id}"
    cached_survey = self.redis_client.get(cache_key)
    if cached_survey:
        return json.loads(cached_survey)
    survey = self.encuestas.find_one({"NumeroEncuesta": id})
    if survey:
        survey['_id'] = str(survey['_id']) 
        self.redis_client.setex(cache_key, 3600, json.dumps(survey)) 
        return survey
    return None
