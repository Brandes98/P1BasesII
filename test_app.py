import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify, request, abort
from app_service import AppService
from datetime import datetime
import json

def create_app(test_config=None):
    app = Flask(__name__)

    if test_config:
        app.config.update(test_config)

    def datetime_converter(o):
        if isinstance(o, datetime):
            return o.__str__()
        
    @app.route("/auth/login", methods=["POST"])
    def login():
            try:
                user_data = request.form.to_dict()
                user = AppService.login(user_data)
                if user:
                    return jsonify(user)
                else:
                    # This should be triggered when login fails due to incorrect credentials or user not found
                    return jsonify({"error": "User not found or no permission to delete"}), 401
            except Exception as e:
                # This should only be triggered by unexpected errors, not by incorrect login attempts
                return jsonify({"error": str(e)}), 500

    # Autenticación y Autorización
    @app.route("/auth/register", methods=["POST"])
    def insert_user():
        user_data = request.get_json()
        try:
            AppService.insert_user(user_data)
            return jsonify({"status": "success", "message": "User registered successfully"}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400  # or appropriate error code, e.g., 500 for server errors

        
    @app.route("/users", methods=["GET"])
    def get_users():
        try:
            users = AppService.get_users()
            return jsonify(users), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/users/<int:id>", methods=["GET"])
    def get_user(id):
        try:
            user = AppService.get_user(id)
            if not user:
                return jsonify({"error": "User not found"}), 404  # Ensuring a 404 is returned if no user is found
            return jsonify(user), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500  # Ensure any exceptions are caught and return a 500

    
    @app.route("/users/<int:id>", methods=["PUT"])
    def update_user(id):
        data = request.get_json()
        try:
            data = AppService.update_user(id, data)
            if data is None:
                return jsonify({"error": "User not found"}), 404
            return data
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    @app.route("/users/<int:id>", methods=["DELETE"])
    def delete_user(id):
        try:
            data = request.get_json()
            flag = AppService.delete_user(id, data)
            if flag:
                return "Usuario eliminado", 200
            return jsonify({"error": "User not found or no permission to delete"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/surveys", methods=["POST"])
    def insert_survey():
        try:
            data_with_token = request.get_json()
            result = AppService.insert_survey(data_with_token)
            if result.inserted_id:
                data_with_token['_id'] = str(result.inserted_id)
                return jsonify(data_with_token), 201
            else:
                return jsonify({"error": "Failed to insert survey"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/surveys/page=<int:num_page>", methods=["GET"])
    def get_public_surveys(num_page):
        page = int(request.args.get('page', num_page))
        limit = int(request.args.get('limit', 5))

        if page < 1 or limit < 1:
            return jsonify({"error": "Invalid page or limit value"}), 400

        try:
            surveys = AppService.get_public_surveys(page, limit)
            return jsonify(surveys)
        except ValueError:
            return jsonify({"error": "Invalid page or limit value"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/surveys/<int:id>", methods=["GET"])
    def get_specific_survey(id):
        try:
            survey = AppService.get_specific_survey(id)
            if survey:
                return jsonify(survey)
            else:
                return jsonify({"error": "Survey not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    @app.route("/surveys/<int:id>", methods=["PUT"])
    def update_survey(id):
        data = request.get_json()
        try:
            data = AppService.update_survey(id, data)
            if data is None:
                return jsonify({"error": "Survey not found"}), 404
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/surveys/<int:id>", methods=["DELETE"])
    def delete_survey(id):
        try:
            data = request.get_json() 
            flag = AppService.delete_survey(id, data)
            if flag:
                return "Encuesta eliminada", 200
            return jsonify({"error": "Survey not found or no permission to delete"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/surveys/<int:id>/publish", methods=["POST"])
    def publish_survey(id):
        try:
            data = request.get_json()
            flag = AppService.publish_survey(id, data)
            if flag:
                return "Encuesta publicada", 200
            return jsonify({"error": "Survey not found or no permission to publish"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/respondents', methods=["POST"])
    def post_encuestado():
        data = request.get_json()
        result = AppService.post_encuestado(data)
        if result:
            return jsonify(data), 201
        else:
            return jsonify({"error": "Failed to insert response"}), 400
    @app.route("/respondents", methods=["GET"])
    def get_encuestados():
        try:
            data = request.get_json()
            respondents = AppService.get_encuestados(data)
            if respondents:
                return str(respondents)
            else:
                return jsonify({"error": "Failed to get respondents"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    @app.route("/respondents/<int:id>", methods=["GET"])
    def get_encuestado(id):
        try:
            data = request.get_json()
            respondents = AppService.get_encuestado(data, id)
            if respondents:
                return str(respondents)
            else:
                return jsonify({"error": "Failed to get respondents"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    @app.route("/respondents/<int:id>", methods=["PUT"])
    def actualizar_encuestado(id):
        try:
            data = request.get_json()
            respondents = AppService.actualizar_encuestado(id,data)
            if respondents:
                return str(respondents)
            else:
                return jsonify({"error": "Failed to get respondents"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    @app.route("/respondents/<int:id>", methods=["DELETE"])
    def eliminar_encuestado(id):
        try:
            respondent = AppService.eliminar_encuestado(id)
            return str(respondent)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

#-----------------mongodb------------------------------------------------------
    @app.route('/surveys/<int:id>/questions', methods=['POST'])
    def insert_question(id):
        data = request.get_json()
        success = AppService.insert_question(id, data)
        if success:
            return '', 201
        else:
            return jsonify({'error': 'Failed to insert question'}), 400
    @app.route("/surveys/<int:id>/questions", methods=["GET"])
    def get_questions(id):
        key = f"survey_questions:{id}"
        try:
            survey = AppService.get_questions(id)
            if survey:
                Database.redis_client.setex(key, 3600, json.dumps(survey))
                return jsonify(survey.get("Preguntas", []))
            return jsonify({"error": "Survey not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    @app.route("/surveys/<int:id>/questions/<int:questionId>", methods=["PUT"])
    def update_question(id, questionId):
        data = request.get_json()
        try:
            data_db = AppService.update_question(id, questionId, data)
            if data_db is None:
                return jsonify({"error": "Question not found or no permission to update"}), 404
            if '_id' in data_db:
                data_db['_id'] = str(data_db['_id'])
            return data_db
        except Exception as e:
            return jsonify({"error": str(e)}), 
    @app.route("/surveys/<int:id>/questions/<int:questionId>", methods=["DELETE"])
    def delete_question(id, questionId):
        try:
            data = request.get_json()
            data_db = AppService.delete_question(id, questionId, data)
            if data_db:
                return "Pregunta eliminada\n" + str(data_db), 200
            return jsonify({"error": "Question not found or no permission to delete"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
#-----------------responses------------------------------------------------------
    @app.route("/surveys/<int:id>/responses", methods=["POST"])
    def post_response(id):
        try:
            data = request.get_json()
            result = AppService.post_response(id, data)
            if result:
                return str(data), 201
            else:
                return jsonify({"error": "Failed to insert response"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    @app.route("/surveys/<int:id>/responses", methods=["GET"])
    def get_responses(id):
        try:
            responses = AppService.get_responses(id)
            return str(responses)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app({'TESTING': True})
    return app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

# Autenticación y Autorización
def test_login_success(client):
    user_data = {"Correo": "user@example.com", "Contrasenna": "correctpassword"}
    token = "someauthtoken"
    with patch('app_service.AppService.login', return_value={"token": token}):
        response = client.post('/auth/login', data=user_data)
        assert response.status_code == 200
        assert json.loads(response.data) == {"token": token}

def test_login_failed(client):
    user_data = {"Correo": "user@example.com", "Contrasenna": "wrongpassword"}
    with patch('app_service.AppService.login', return_value=None):  # Simulate failed login
        response = client.post('/auth/login', data=user_data)
        assert response.status_code == 401
        assert json.loads(response.data) == {"error": "User not found or no permission to delete"}

def test_login_internal_error(client):
    user_data = {"Correo": "user@example.com", "Contrasenna": "password"}
    with patch('app_service.AppService.login', side_effect=Exception("Database connection failed")):
        response = client.post('/auth/login', data=user_data)
        assert response.status_code == 500
        assert "error" in json.loads(response.data)

def test_register_user_success(client):
    user_data = {
        "nombre": "John Doe", "idRol": 1, "correo": "john@example.com",
        "contrasena": "securepassword", "fechaCreacion": "2023-01-01",
        "fechaNacimiento": "1990-01-01", "genero": "M", "idPais": 1
    }
    with patch('app_service.AppService.insert_user', return_value=None):
        response = client.post('/auth/register', json=user_data)
        assert response.status_code == 201
        assert json.loads(response.data) == {"status": "success", "message": "User registered successfully"}

def test_register_user_failure(client):
    user_data = {
        "nombre": "Jane Doe"
        # missing required fields
    }
    with patch('app_service.AppService.insert_user', side_effect=Exception("Failed to insert user")):
        response = client.post('/auth/register', json=user_data)
        assert response.status_code == 400
        assert json.loads(response.data) == {"error": "Failed to insert user"}

# Usuarios
def test_get_users_from_database_success(client):
    users_data = [{"id": 1, "Nombre": "John Doe", "RoleName": "Administrator", "Correo": "john@example.com", "FechaCreacion": "2023-01-01T00:00:00", "FechaNacimiento": "1990-01-01T00:00:00", "Gender": "Male", "Country": "USA"}]
    with patch('app_service.AppService.get_users', return_value=users_data):
        response = client.get('/users')
        assert response.status_code == 200
        assert json.loads(response.data) == users_data

def test_get_users_no_results(client):
    with patch('app_service.AppService.get_users', return_value=[]):
        response = client.get('/users')
        assert response.status_code == 200
        assert json.loads(response.data) == []

def test_get_users_internal_error(client):
    with patch('app_service.AppService.get_users', side_effect=Exception("Database error")):
        response = client.get('/users')
        assert response.status_code == 500
        assert json.loads(response.data) == {"error": "Database error"}

def test_get_user_from_database_success(client, app):
    # User data fetched from the database, represented as a raw dictionary instead of a jsonify response
    user_data = {"id": 1, "Nombre": "John Doe", "RoleName": "Administrator", "Correo": "john@example.com"}
    
    with patch('app_service.AppService.get_user', return_value=user_data):
        response = client.get('/users/1')
        assert response.status_code == 200
        assert json.loads(response.data) == user_data

def test_get_user_not_found(client, app):
    with patch('app_service.AppService.get_user', return_value=None):  # Simulate no user found
        response = client.get('/users/999')
        assert response.status_code == 404
        assert json.loads(response.data) == {"error": "User not found"}

def test_get_user_internal_error(client, app):
    with patch('app_service.AppService.get_user', side_effect=Exception("Internal server error")):
        response = client.get('/users/1')
        assert response.status_code == 500
        assert json.loads(response.data) == {"error": "Internal server error"}

def test_update_user_success(client, app):
    user_data = {"Nombre": "Jane Doe", "Correo": "jane@example.com", "Contrasenna": "newpassword123", "FechaNacimiento": "1985-05-16", "Genero": "F", "idPais": "US"}
    with app.app_context(), \
         patch('app_service.AppService.update_user', return_value=jsonify({"status": "success", "message": "Usuario actualizado correctamente"})):
        response = client.put('/users/1', json=user_data)
        assert response.status_code == 200
        assert json.loads(response.data) == {"status": "success", "message": "Usuario actualizado correctamente"}

def test_update_user_not_found(client, app):
    user_data = {"Nombre": "John Doe", "Correo": "john@example.com", "Contrasenna": "newpassword456", "FechaNacimiento": "1985-05-16", "Genero": "M", "idPais": "US"}
    with app.app_context():
        with patch('app_service.AppService.update_user', return_value=None):  # Simulate user not found by returning None
            response = client.put('/users/99', json=user_data)
            assert response.status_code == 404
            assert json.loads(response.data) == {"error": "User not found"}

def test_update_user_internal_error(client, app):
    user_data = {"Nombre": "Alice Doe", "Correo": "alice@example.com", "Contrasenna": "password789", "FechaNacimiento": "1990-07-22", "Genero": "F", "idPais": "CA"}
    with app.app_context(), \
         patch('app_service.AppService.update_user', side_effect=Exception("Database connection failed")):
        response = client.put('/users/2', json=user_data)
        assert response.status_code == 500
        assert json.loads(response.data) == {"error": "Database connection failed"}

def test_delete_user_success(client):
    with patch('app_service.AppService.delete_user', return_value=True):
        response = client.delete('/users/1', json={"Token": "valid-token"})
        assert response.status_code == 200
        assert response.data.decode() == "Usuario eliminado"

def test_delete_user_not_found(client):
    with patch('app_service.AppService.delete_user', return_value=False):
        response = client.delete('/users/99', json={"Token": "invalid-token"})
        assert response.status_code == 404
        assert json.loads(response.data) == {"error": "User not found or no permission to delete"}

def test_delete_user_internal_error(client):
    with patch('app_service.AppService.delete_user', side_effect=Exception("Database connection failed")):
        response = client.delete('/users/1', json={"Token": "valid-token"})
        assert response.status_code == 500
        assert json.loads(response.data) == {"error": "Database connection failed"}

# Encuestas
def test_insert_survey_success(client):
    # Mocking the necessary parts of the service and the database
    with patch('app_service.AppService.insert_survey') as mock_insert:
        # Setup the mock to mimic MongoDB's insert_one return value
        mock_insert.return_value = MagicMock(inserted_id="507f1f77bcf86cd799439011")
        # Define the payload that would be sent to the endpoint
        payload = {"question": "What is your favorite color?", "Token": "valid-token", "FechaCreacion": "2023-01-01T00:00:00", "FechaActualizacion": "2023-01-01T00:00:00"}
        # Make a POST request
        response = client.post('/surveys', json=payload)
        # Assert that the response matches our expectations
        payload['_id'] = "507f1f77bcf86cd799439011"  # The mock inserted ID
        assert response.status_code == 201
        assert json.loads(response.data) == payload

def test_insert_survey_no_token(client):
    # Scenario testing what happens if the token is missing
    with patch('app_service.AppService.insert_survey', side_effect=ValueError("Token is required")):
        payload = {"question": "What is your preference?"}  # No Token included
        response = client.post('/surveys', json=payload)
        assert response.status_code == 500
        assert json.loads(response.data) == {"error": "Token is required"}

def test_insert_survey_permission_denied(client):
    # Testing permission denied scenario
    with patch('app_service.AppService.insert_survey', side_effect=Exception("You don't have permission to create this survey.")):
        payload = {"question": "What do you think about our service?", "Token": "invalid-token"}
        response = client.post('/surveys', json=payload)
        assert response.status_code == 500
        assert json.loads(response.data) == {"error": "You don't have permission to create this survey."}

def test_insert_survey_unexpected_error(client):
    # Testing generic error handling
    with patch('app_service.AppService.insert_survey', side_effect=Exception("Unexpected error occurred")):
        payload = {"Titulo": "Feedback?", "Token": 3, "IdAutor": 123}
        response = client.post('/surveys', json=payload)
        assert response.status_code == 500
        assert json.loads(response.data) == {"error": "Unexpected error occurred"}

def test_get_public_surveys_success(client):
    # Mock the service layer method that handles fetching public surveys
    with patch('app_service.AppService.get_public_surveys') as mock_get_surveys:
        # Set up the mock to return a list of survey dictionaries
        mock_get_surveys.return_value = [
            {"_id": "1", "title": "Customer Feedback"},
            {"_id": "2", "title": "Product Review"}
        ]
        # Make a GET request to the route handling public surveys
        response = client.get('/surveys/page=1')
        # Assert that the status code is 200 OK and the JSON response contains the surveys
        assert response.status_code == 200
        # Convert response.data from bytes to JSON and validate the content
        response_data = json.loads(response.data)
        assert response_data == [
            {"_id": "1", "title": "Customer Feedback"},
            {"_id": "2", "title": "Product Review"}
        ]

def test_get_public_surveys_no_data(client):
    # Mock the service layer method when no surveys are available
    with patch('app_service.AppService.get_public_surveys') as mock_get_surveys:
        mock_get_surveys.return_value = []
        # Make a GET request to check for empty page results
        response = client.get('/surveys/page=2')
        assert response.status_code == 200
        # Ensure the JSON response is an empty list
        assert json.loads(response.data) == []

def test_get_public_surveys_success(client):
    with patch('app_service.AppService.get_public_surveys') as mock_service:
        mock_service.return_value = [{"id": 2, "name": "Survey DB"}]
        response = client.get('/surveys/page=1')
        assert response.status_code == 200
        assert json.loads(response.data) == [{"id": 2, "name": "Survey DB"}]

def test_get_public_surveys_invalid_parameters(client):
    response = client.get('/surveys/page=0')  # Assuming '0' is considered an invalid page number
    assert response.status_code == 400
    assert json.loads(response.data) == {"error": "Invalid page or limit value"}

def test_get_public_surveys_internal_error(client):
    with patch('app_service.AppService.get_public_surveys', side_effect=Exception("Unexpected error")):
        response = client.get('/surveys/page=1')
        assert response.status_code == 500
        assert json.loads(response.data) == {"error": "Unexpected error"}

def test_get_specific_survey_success(client):
    survey_data = {"_id": "507f191e810c19729de860ea", "name": "Customer Feedback Survey", "NumeroEncuesta": 1}
    with patch('app_service.AppService.get_specific_survey') as mock_service:
        mock_service.return_value = survey_data
        response = client.get('/surveys/1')
        assert response.status_code == 200
        assert json.loads(response.data) == survey_data

def test_get_specific_survey_not_found(client):
    with patch('app_service.AppService.get_specific_survey', return_value=None):
        response = client.get('/surveys/1')
        assert response.status_code == 404
        assert json.loads(response.data) == {"error": "Survey not found"}

def test_get_specific_survey_internal_error(client):
    with patch('app_service.AppService.get_specific_survey', side_effect=Exception("Database connection failed")):
        response = client.get('/surveys/1')
        assert response.status_code == 500
        assert json.loads(response.data) == {"error": "Database connection failed"}

def test_update_survey_success(client):
    survey_data = {"IdAutor": 1, "Token": 1, "FechaCreacion": "2023-01-01T00:00:00", "FechaActualizacion": "2023-01-01T00:00:00"}
    updated_data = survey_data.copy()
    updated_data.update({"name": "Updated Survey"})
    with patch('app_service.AppService.update_survey') as mock_update:
        mock_update.return_value = updated_data
        response = client.put('/surveys/1', json=survey_data)
        assert response.status_code == 200
        assert json.loads(response.data) == updated_data

def test_update_survey_not_found(client):
    survey_data = {"IdAutor": 1, "Token": 1, "FechaCreacion": "2023-01-01T00:00:00", "FechaActualizacion": "2023-01-01T00:00:00"}
    with patch('app_service.AppService.update_survey', return_value=None):
        response = client.put('/surveys/1', json=survey_data)
        assert response.status_code == 404
        assert json.loads(response.data) == {"error": "Survey not found"}

def test_update_survey_internal_error(client):
    survey_data = {"IdAutor": 1, "Token": 1, "FechaCreacion": "2023-01-01T00:00:00", "FechaActualizacion": "2023-01-01T00:00:00"}
    with patch('app_service.AppService.update_survey', side_effect=Exception("Database error")):
        response = client.put('/surveys/1', json=survey_data)
        assert response.status_code == 500
        assert json.loads(response.data) == {"error": "Database error"}

def test_delete_survey_success(client):
    survey_data = {"IdAutor": 1, "Token": 1}
    with patch('app_service.AppService.delete_survey', return_value=True):
        response = client.delete('/surveys/1', json=survey_data)
        assert response.status_code == 200
        assert response.data.decode() == "Encuesta eliminada"

def test_delete_survey_not_found_or_no_permission(client):
    survey_data = {"IdAutor": 1, "Token": 1}
    with patch('app_service.AppService.delete_survey', return_value=False):
        response = client.delete('/surveys/1', json=survey_data)
        assert response.status_code == 404
        assert json.loads(response.data) == {"error": "Survey not found or no permission to delete"}

def test_delete_survey_internal_error(client):
    survey_data = {"IdAutor": 1, "Token": 1}
    with patch('app_service.AppService.delete_survey', side_effect=Exception("Database error")):
        response = client.delete('/surveys/1', json=survey_data)
        assert response.status_code == 500
        assert json.loads(response.data) == {"error": "Database error"}

def test_publish_survey_success(client):
    survey_data = {"IdAutor": 1, "Token": 1}
    with patch('app_service.AppService.publish_survey', return_value=True):
        response = client.post('/surveys/1/publish', json=survey_data)
        assert response.status_code == 200
        assert response.data.decode() == "Encuesta publicada"

def test_publish_survey_not_found_or_no_permission(client):
    survey_data = {"IdAutor": 1, "Token": 1}
    with patch('app_service.AppService.publish_survey', return_value=False):
        response = client.post('/surveys/1/publish', json=survey_data)
        assert response.status_code == 404
        assert json.loads(response.data) == {"error": "Survey not found or no permission to publish"}

def test_publish_survey_internal_error(client):
    survey_data = {"IdAutor": 1, "Token": 1}
    with patch('app_service.AppService.publish_survey', side_effect=Exception("Database error")):
        response = client.post('/surveys/1/publish', json=survey_data)
        assert response.status_code == 500
        assert json.loads(response.data) == {"error": "Database error"}


# ----------------post encuestado----------------
@pytest.fixture
def respondent_data():
    """Sample respondent data for testing."""
    return {
        "Nombre": "Juan Pérez",
        "Correo": "juan.perez@example.com",
        "Contrasenna": "contraseña123",
        "FechaNacimiento": "2023-03-05T09:53:44",
        "Genero": "O",
        "idPais": "CRC"
    }

@patch('app_service.AppService.post_encuestado')
def test_post_encuestado_success(mock_post_encuestado, client, respondent_data):
    mock_post_encuestado.return_value = True
    response = client.post('/respondents', json=respondent_data)
    assert response.status_code == 201
    assert response.get_json() == respondent_data

@patch('app_service.AppService.post_encuestado')
def test_post_encuestado_failure(mock_post_encuestado, client, respondent_data):
    mock_post_encuestado.return_value = False

    response = client.post('/respondents', data=json.dumps(respondent_data), content_type='application/json')
    assert response.status_code == 400
    assert json.loads(response.data) == {"error": "Failed to insert response"}
'''
@patch('app_service.AppService.post_encuestado')
def test_post_encuestado_exception(mock_post_encuestado, client, respondent_data):
    mock_post_encuestado.side_effect = Exception("Unexpected Error")

    response = client.post('/respondents', json=respondent_data)
    assert response.status_code == 500
    assert response.get_json() == {"error": "Unexpected Error"}
'''
#---------------get encuestados----------------
@pytest.fixture
def example_request_data():
    return {
        "Token": 1,
        "IdAutor": 1
    }

@patch('app_service.AppService.get_encuestados')
def test_get_encuestados_success(mock_get_encuestados, client, example_request_data):
    mock_get_encuestados.return_value = [{'id': 1, 'name': 'John Doe', 'email': 'john@example.com'}]
    response = client.get('/respondents', json=example_request_data)
    assert response.status_code == 200
    assert 'John Doe' in response.get_data(as_text=True)

@patch('app_service.AppService.get_encuestados')
def test_get_encuestados_failure(mock_get_encuestados, client, example_request_data):
    mock_get_encuestados.return_value = []
    response = client.get('/respondents', json=example_request_data)
    assert response.status_code == 400
    assert 'Failed to get respondents' in response.get_data(as_text=True)

@patch('app_service.AppService.get_encuestados')
def test_get_encuestados_exception(mock_get_encuestados, client, example_request_data):
    mock_get_encuestados.side_effect = Exception("Unexpected Error")
    response = client.get('/respondents', json=example_request_data)
    assert response.status_code == 500
    assert 'Unexpected Error' in response.get_data(as_text=True)
#-----------------get encuestado----------------
@pytest.fixture
def auth_data():
    return {
        "Token": 1,
        "IdAutor": 1
    }

@patch('app_service.AppService.get_encuestado')
def test_get_encuestado_success(mock_get_encuestado, client, auth_data):
    mock_get_encuestado.return_value = {'id': 1, 'name': 'John Doe'}
    response = client.get('/respondents/1', json=auth_data)
    assert response.status_code == 200
    assert 'John Doe' in response.get_data(as_text=True)

@patch('app_service.AppService.get_encuestado')
def test_get_encuestado_failure(mock_get_encuestado, client, auth_data):
    mock_get_encuestado.return_value = None
    response = client.get('/respondents/1', json=auth_data)
    assert response.status_code == 400
    assert 'Failed to get respondents' in response.get_data(as_text=True)

@patch('app_service.AppService.get_encuestado')
def test_get_encuestado_exception(mock_get_encuestado, client, auth_data):
    mock_get_encuestado.side_effect = Exception("Unexpected Error")
    response = client.get('/respondents/1', json=auth_data)
    assert response.status_code == 500
    assert 'Unexpected Error' in response.get_data(as_text=True)

#-----------------actualizar [put] encuestado----------------
@pytest.fixture
def auth_data():
    return {
        "Token": 1,
        "IdAutor": 1
    }


@patch('app_service.AppService.actualizar_encuestado')
def test_actualizar_encuestado_success(mock_actualizar, client, auth_data):
    mock_actualizar.return_value = True
    response = client.put('/respondents/1', json=auth_data)
    assert response.status_code == 200

@patch('app_service.AppService.actualizar_encuestado')
def test_actualizar_encuestado_failure(mock_actualizar, client, auth_data):
    mock_actualizar.return_value = False
    response = client.put('/respondents/1', json=auth_data)
    assert response.status_code == 400
    assert 'Failed to get respondents' in response.get_data(as_text=True)

@patch('app_service.AppService.actualizar_encuestado')
def test_actualizar_encuestado_exception(mock_actualizar, client, auth_data):
    mock_actualizar.side_effect = Exception("Unexpected Error")
    response = client.put('/respondents/1', json=auth_data)
    assert response.status_code == 500
    assert 'Unexpected Error' in response.get_data(as_text=True)
#-----------------eliminar [delete] encuestado----------------
@patch('app_service.AppService.eliminar_encuestado')
def test_eliminar_encuestado_success(mock_eliminar, client):
    mock_eliminar.return_value = True
    response = client.delete('/respondents/1')
    assert response.status_code == 200
'''
@patch('app_service.AppService.eliminar_encuestado')
def test_eliminar_encuestado_failure(mock_eliminar, client):
    mock_eliminar.return_value = False
    response = client.delete('/respondents/3')
    assert response.status_code == 400
'''
@patch('app_service.AppService.eliminar_encuestado')
def test_eliminar_encuestado_exception(mock_eliminar, client):
    mock_eliminar.side_effect = Exception("Deletion Failed")
    response = client.delete('/respondents/1')
    assert response.status_code == 500

#------mongodb------------------------------------------------------
#------preguntas------------------------------------------------------
#-----------------insert question----------------
@pytest.fixture
def question_data():
    return {
    "Token": 1,
    "IdAutor": 1,
    "Preguntas": [ 
                   {"Numero": 6, 
                   "Categoria": "EleccionSimples", 
                   "Pregunta": "Else scene sure region study or.", 
                   "Opciones": ["laugh", "always", "than", "environment", "wear"]}
    ]
}

@pytest.fixture
def client(app):
    return app.test_client()

def test_insert_question_success(client):
    with client:
        with patch('app_service.AppService.insert_question') as mock_insert:
            mock_insert.return_value = True
            response = client.post('/surveys/1/questions', json={'question': 'What is your favorite color?'})
            assert response.status_code == 201
            assert response.data == b''

def test_insert_question_failure(client):
    with client:
        with patch('app_service.AppService.insert_question') as mock_insert:
            mock_insert.return_value = False
            response = client.post('/surveys/1/questions', json={'question': 'What is your favorite color?'})
            assert response.status_code == 400
            assert json.loads(response.data) == {'error': 'Failed to insert question'}
#-----------------get questions----------------
@pytest.fixture
def client():
    app = create_app({'TESTING': True})
    with app.test_client() as client:
        return client

def test_get_questions_failure(client):
    survey_id = 1
    with patch('app_service.AppService.get_questions', return_value={}):
        response = client.get(f'/surveys/{survey_id}/questions')
        assert response.status_code == 404
        assert response.json == {"error": "Survey not found"}
#------- put question--------------------------------
def test_update_question_success(client):
    survey_id = 1
    question_id = 1
    update_data = {"Token": 1, "IdAutor": 1, "Preguntas": [{"Numero": 1, "Categoria": "EleccionSimples", "Pregunta": "¿10's GOAT?", "Opciones": ["Lebron", "Curry", "Durant", "Harden"]}]}
    with patch('app_service.AppService.update_question', return_value={'updated': True}):
        response = client.put(f'/surveys/{survey_id}/questions/{question_id}', json=update_data)
        assert response.status_code == 200
        assert response.json == {'updated': True}

def test_update_question_failure(client):
    survey_id = 1
    question_id = 1
    update_data = {"Token": 1, "IdAutor": 1, "Preguntas": [{"Numero": 1, "Categoria": "EleccionSimples", "Pregunta": "¿10's GOAT?", "Opciones": ["Lebron", "Curry", "Durant", "Harden"]}]}
    with patch('app_service.AppService.update_question', return_value=None):
        response = client.put(f'/surveys/{survey_id}/questions/{question_id}', json=update_data)
        assert response.status_code == 404
#-----------------delete question----------------
@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_delete_question_success(client):
    survey_id = 1
    question_id = 1
    data = {"Token": 1, "IdAutor": 1} 
    with patch('app_service.AppService.delete_question', return_value=True) as mock_delete:
        response = client.delete(f'/surveys/{survey_id}/questions/{question_id}', json=data)
        assert response.status_code == 200
        assert "Pregunta eliminada" in response.get_data(as_text=True)

def test_delete_question_failure(client):
    survey_id = 1
    question_id = 1
    data = {"Token": 1, "IdAutor": 1} 
    with patch('app_service.AppService.delete_question', return_value=None):
        response = client.delete(f'/surveys/{survey_id}/questions/{question_id}', json=data)
        assert response.status_code == 404
        assert "not found or no permission to delete" in response.json['error']
#-----------------responses----------------
#-----------------post response----------------
@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_post_response_failure(client):
    data = { "Token":3,"NumeroEncuesta": 1, "IdEncuestado": 3, "Nombre": "EncuestadoES", "Correo": "encuestado@dominio.com", "FechaRealizado": "2023-03-05T09:53:44", "Preguntas": [{"Numero": 1, "Categoria": "EleccionMultiples", "Pregunta": "Total history network sound skill.", "Respuesta": ["challenge", "act", "nor"]}, {"Numero": 2, "Categoria": "SiNo", "Pregunta": "Finally cup school page interest less game.", "Respuesta": 0}, {"Numero": 3, "Categoria": "Abiertas", "Pregunta": "Federal student reveal investment court.", "Respuesta": "Often land something entire rich. Event enough serious small also."}, {"Numero": 4, "Categoria": "EscalaCalificacion", "Pregunta": "Cover carry support evening spend spend expect.", "Respuesta": 7}, {"Numero": 5, "Categoria": "Numericas", "Pregunta": "Area five debate marriage certainly PM watch property.", "Respuesta": 11}, {"Numero": 6, "Categoria": "EleccionSimples", "Pregunta": "Else scene sure region study or.", "Respuesta": "always"}, {"Numero": 7, "Categoria": "EleccionMultiples", "Pregunta": "Someone bag into international piece specific.", "Respuesta": ["green", "our", "fine"]}, {"Numero": 8, "Categoria": "EscalaCalificacion", "Pregunta": "Return a cell carry.", "Respuesta": 3}, {"Numero": 1, "Categoria": "EleccionMultiples", "Pregunta": "Total history network sound skill.", "Respuesta": ["nor", "challenge", "help", "act"]}, {"Numero": 2, "Categoria": "SiNo", "Pregunta": "Finally cup school page interest less game.", "Respuesta": 0}, {"Numero": 3, "Categoria": "Abiertas", "Pregunta": "Federal student reveal investment court.", "Respuesta": "Various American nature forward upon. Include wonder threat choice expert letter. Me require issue reveal name."}, {"Numero": 4, "Categoria": "EscalaCalificacion", "Pregunta": "Cover carry support evening spend spend expect.", "Respuesta": 7}, {"Numero": 5, "Categoria": "Numericas", "Pregunta": "Area five debate marriage certainly PM watch property.", "Respuesta": 93}, {"Numero": 6, "Categoria": "EleccionSimples", "Pregunta": "Else scene sure region study or.", "Respuesta": "laugh"}, {"Numero": 7, "Categoria": "EleccionMultiples", "Pregunta": "Someone bag into international piece specific.", "Respuesta": ["our", "fine", "soon"]}, {"Numero": 8, "Categoria": "EscalaCalificacion", "Pregunta": "Return a cell carry.", "Respuesta": 6}, {"Numero": 1, "Categoria": "EleccionMultiples", "Pregunta": "Total history network sound skill.", "Respuesta": ["nor", "act"]}, {"Numero": 2, "Categoria": "SiNo", "Pregunta": "Finally cup school page interest less game.", "Respuesta": 0}, {"Numero": 3, "Categoria": "Abiertas", "Pregunta": "Federal student reveal investment court.", "Respuesta": "And carry gas lose none quickly source always. Future mean best. Fine method particularly law.\nPolitics box face recognize. Method feel teacher."}, {"Numero": 4, "Categoria": "EscalaCalificacion", "Pregunta": "Cover carry support evening spend spend expect.", "Respuesta": 9}, {"Numero": 5, "Categoria": "Numericas", "Pregunta": "Area five debate marriage certainly PM watch property.", "Respuesta": 22}, {"Numero": 6, "Categoria": "EleccionSimples", "Pregunta": "Else scene sure region study or.", "Respuesta": "environment"}, {"Numero": 7, "Categoria": "EleccionMultiples", "Pregunta": "Someone bag into international piece specific.", "Respuesta": ["our"]}, {"Numero": 8, "Categoria": "EscalaCalificacion", "Pregunta": "Return a cell carry.", "Respuesta": 10}, {"Numero": 1, "Categoria": "EleccionMultiples", "Pregunta": "Just wall you speech other.", "Respuesta": ["administration", "source", "main", "he"]}, {"Numero": 2, "Categoria": "EscalaCalificacion", "Pregunta": "Live example buy garden.", "Respuesta": 8}, {"Numero": 3, "Categoria": "SiNo", "Pregunta": "Ten personal authority single.", "Respuesta": 0}, {"Numero": 4, "Categoria": "Numericas", "Pregunta": "Lay between cover my along certain television.", "Respuesta": 88}, {"Numero": 5, "Categoria": "Numericas", "Pregunta": "Sense room get outside.", "Respuesta": 72}, {"Numero": 1, "Categoria": "EleccionMultiples", "Pregunta": "Just wall you speech other.", "Respuesta": ["he", "administration"]}, {"Numero": 2, "Categoria": "EscalaCalificacion", "Pregunta": "Live example buy garden.", "Respuesta": 4}, {"Numero": 3, "Categoria": "SiNo", "Pregunta": "Ten personal authority single.", "Respuesta": 1}, {"Numero": 4, "Categoria": "Numericas", "Pregunta": "Lay between cover my along certain television.", "Respuesta": 62}, {"Numero": 5, "Categoria": "Numericas", "Pregunta": "Sense room get outside.", "Respuesta": 10}, {"Numero": 1, "Categoria": "EleccionMultiples", "Pregunta": "Just wall you speech other.", "Respuesta": ["source", "main", "carry", "he", "administration"]}, {"Numero": 2, "Categoria": "EscalaCalificacion", "Pregunta": "Live example buy garden.", "Respuesta": 9}, {"Numero": 3, "Categoria": "SiNo", "Pregunta": "Ten personal authority single.", "Respuesta": 1}, {"Numero": 4, "Categoria": "Numericas", "Pregunta": "Lay between cover my along certain television.", "Respuesta": 20}, {"Numero": 5, "Categoria": "Numericas", "Pregunta": "Sense room get outside.", "Respuesta": 82}, {"Numero": 1, "Categoria": "Numericas", "Pregunta": "Miss alone else several receive.", "Respuesta": 22}, {"Numero": 2, "Categoria": "Numericas", "Pregunta": "Evening throughout set agency role million.", "Respuesta": 2}, {"Numero": 3, "Categoria": "Numericas", "Pregunta": "At weight cold everyone community avoid.", "Respuesta": 54}, {"Numero": 4, "Categoria": "Abiertas", "Pregunta": "Century better relate pattern card summer on.", "Respuesta": "Carry stuff role reflect debate. Key turn benefit.\nGrowth onto pick. Stand anyone provide candidate tough raise energy debate. Their magazine investment cause particular."}, {"Numero": 5, "Categoria": "EscalaCalificacion", "Pregunta": "Sing when hospital current game threat structure.", "Respuesta": 2}, {"Numero": 6, "Categoria": "SiNo", "Pregunta": "I without service always choose meeting main.", "Respuesta": 0}, {"Numero": 1, "Categoria": "Numericas", "Pregunta": "Miss alone else several receive.", "Respuesta": 67}, {"Numero": 2, "Categoria": "Numericas", "Pregunta": "Evening throughout set agency role million.", "Respuesta": 66}, {"Numero": 3, "Categoria": "Numericas", "Pregunta": "At weight cold everyone community avoid.", "Respuesta": 18}, {"Numero": 4, "Categoria": "Abiertas", "Pregunta": "Century better relate pattern card summer on.", "Respuesta": "Protect reality security partner. Easy worry toward financial land finally.\nSuccess fast soon score explain effect detail. Professional lose reveal mouth center pull wait."}, {"Numero": 5, "Categoria": "EscalaCalificacion", "Pregunta": "Sing when hospital current game threat structure.", "Respuesta": 4}, {"Numero": 6, "Categoria": "SiNo", "Pregunta": "I without service always choose meeting main.", "Respuesta": 1}, {"Numero": 1, "Categoria": "Numericas", "Pregunta": "Miss alone else several receive.", "Respuesta": 76}, {"Numero": 2, "Categoria": "Numericas", "Pregunta": "Evening throughout set agency role million.", "Respuesta": 93}, {"Numero": 3, "Categoria": "Numericas", "Pregunta": "At weight cold everyone community avoid.", "Respuesta": 37}, {"Numero": 4, "Categoria": "Abiertas", "Pregunta": "Century better relate pattern card summer on.", "Respuesta": "Job actually attorney.\nYour wait old fine suggest western. Adult gas area share specific. Social second none now someone."}, {"Numero": 5, "Categoria": "EscalaCalificacion", "Pregunta": "Sing when hospital current game threat structure.", "Respuesta": 1}, {"Numero": 6, "Categoria": "SiNo", "Pregunta": "I without service always choose meeting main.", "Respuesta": 0}, {"Numero": 1, "Categoria": "Numericas", "Pregunta": "Thus hold success note teach choice.", "Respuesta": 73}, {"Numero": 2, "Categoria": "EscalaCalificacion", "Pregunta": "Morning partner outside always heart shoulder.", "Respuesta": 6}, {"Numero": 3, "Categoria": "EscalaCalificacion", "Pregunta": "Near into anyone section Democrat kid line.", "Respuesta": 6}, {"Numero": 4, "Categoria": "EleccionSimples", "Pregunta": "Opportunity charge change account detail challenge force.", "Respuesta": "dinner"}, {"Numero": 5, "Categoria": "EleccionMultiples", "Pregunta": "Firm minute billion easy again.", "Respuesta": ["everybody", "study", "first"]}, {"Numero": 6, "Categoria": "EleccionMultiples", "Pregunta": "Blood floor author strong court.", "Respuesta": ["brother", "type", "student"]}, {"Numero": 7, "Categoria": "Numericas", "Pregunta": "Worry bring common near well.", "Respuesta": 99}, {"Numero": 1, "Categoria": "Numericas", "Pregunta": "Thus hold success note teach choice.", "Respuesta": 14}, {"Numero": 2, "Categoria": "EscalaCalificacion", "Pregunta": "Morning partner outside always heart shoulder.", "Respuesta": 6}, {"Numero": 3, "Categoria": "EscalaCalificacion", "Pregunta": "Near into anyone section Democrat kid line.", "Respuesta": 7}, {"Numero": 4, "Categoria": "EleccionSimples", "Pregunta": "Opportunity charge change account detail challenge force.", "Respuesta": "dinner"}, {"Numero": 5, "Categoria": "EleccionMultiples", "Pregunta": "Firm minute billion easy again.", "Respuesta": ["office", "talk", "study", "data"]}, {"Numero": 6, "Categoria": "EleccionMultiples", "Pregunta": "Blood floor author strong court.", "Respuesta": ["weight", "remain"]}, {"Numero": 7, "Categoria": "Numericas", "Pregunta": "Worry bring common near well.", "Respuesta": 91}, {"Numero": 1, "Categoria": "Numericas", "Pregunta": "Thus hold success note teach choice.", "Respuesta": 99}, {"Numero": 2, "Categoria": "EscalaCalificacion", "Pregunta": "Morning partner outside always heart shoulder.", "Respuesta": 7}, {"Numero": 3, "Categoria": "EscalaCalificacion", "Pregunta": "Near into anyone section Democrat kid line.", "Respuesta": 4}, {"Numero": 4, "Categoria": "EleccionSimples", "Pregunta": "Opportunity charge change account detail challenge force.", "Respuesta": "sound"}, {"Numero": 5, "Categoria": "EleccionMultiples", "Pregunta": "Firm minute billion easy again.", "Respuesta": ["office", "talk", "data", "everybody", "first", "study"]}, {"Numero": 6, "Categoria": "EleccionMultiples", "Pregunta": "Blood floor author strong court.", "Respuesta": ["brother"]}, {"Numero": 7, "Categoria": "Numericas", "Pregunta": "Worry bring common near well.", "Respuesta": 76}, {"Numero": 1, "Categoria": "EleccionMultiples", "Pregunta": "Whom upon create now near.", "Respuesta": ["attack", "situation", "face", "training"]}, {"Numero": 2, "Categoria": "Numericas", "Pregunta": "Customer water be avoid fight perhaps computer.", "Respuesta": 33}, {"Numero": 3, "Categoria": "EleccionSimples", "Pregunta": "Lay edge gas field chair.", "Respuesta": "need"}, {"Numero": 4, "Categoria": "Abiertas", "Pregunta": "Free wish space treat.", "Respuesta": "Watch keep each change. Reflect anyone whether not. Either onto television during page animal."}, {"Numero": 5, "Categoria": "SiNo", "Pregunta": "Beautiful kid own become term.", "Respuesta": 1}, {"Numero": 6, "Categoria": "Numericas", "Pregunta": "Doctor better to act seven say can behind.", "Respuesta": 28}, {"Numero": 7, "Categoria": "SiNo", "Pregunta": "Become office then table dinner stuff tell.", "Respuesta": 1}, {"Numero": 8, "Categoria": "EscalaCalificacion", "Pregunta": "Size cost event.", "Respuesta": 8}, {"Numero": 9, "Categoria": "EleccionSimples", "Pregunta": "Possible member walk magazine development per.", "Respuesta": "research"}, {"Numero": 1, "Categoria": "EleccionMultiples", "Pregunta": "Whom upon create now near.", "Respuesta": ["face", "attack", "training", "situation", "minute"]}, {"Numero": 2, "Categoria": "Numericas", "Pregunta": "Customer water be avoid fight perhaps computer.", "Respuesta": 12}, {"Numero": 3, "Categoria": "EleccionSimples", "Pregunta": "Lay edge gas field chair.", "Respuesta": "put"}, {"Numero": 4, "Categoria": "Abiertas", "Pregunta": "Free wish space treat.", "Respuesta": "Movie American eight letter. Mission course upon region.\nPlan recognize note although. Material position interesting serve anything exist. Nature billion note include writer serious."}, {"Numero": 5, "Categoria": "SiNo", "Pregunta": "Beautiful kid own become term.", "Respuesta": 0}, {"Numero": 6, "Categoria": "Numericas", "Pregunta": "Doctor better to act seven say can behind.", "Respuesta": 28}, {"Numero": 7, "Categoria": "SiNo", "Pregunta": "Become office then table dinner stuff tell.", "Respuesta": 1}, {"Numero": 8, "Categoria": "EscalaCalificacion", "Pregunta": "Size cost event.", "Respuesta": 7}, {"Numero": 9, "Categoria": "EleccionSimples", "Pregunta": "Possible member walk magazine development per.", "Respuesta": "research"}, {"Numero": 1, "Categoria": "EleccionMultiples", "Pregunta": "Whom upon create now near.", "Respuesta": ["face", "training", "minute", "attack", "situation"]}, {"Numero": 2, "Categoria": "Numericas", "Pregunta": "Customer water be avoid fight perhaps computer.", "Respuesta": 78}, {"Numero": 3, "Categoria": "EleccionSimples", "Pregunta": "Lay edge gas field chair.", "Respuesta": "factor"}, {"Numero": 4, "Categoria": "Abiertas", "Pregunta": "Free wish space treat.", "Respuesta": "Who management exist crime. Or picture federal arrive health never."}, {"Numero": 5, "Categoria": "SiNo", "Pregunta": "Beautiful kid own become term.", "Respuesta": 0}, {"Numero": 6, "Categoria": "Numericas", "Pregunta": "Doctor better to act seven say can behind.", "Respuesta": 93}, {"Numero": 7, "Categoria": "SiNo", "Pregunta": "Become office then table dinner stuff tell.", "Respuesta": 0}, {"Numero": 8, "Categoria": "EscalaCalificacion", "Pregunta": "Size cost event.", "Respuesta": 7}, {"Numero": 9, "Categoria": "EleccionSimples", "Pregunta": "Possible member walk magazine development per.", "Respuesta": "military"}]}
    with patch('app_service.AppService.post_response', return_value=False):
        response = client.post('/surveys/1/responses', json=data)
        assert response.status_code == 400
        assert "Failed to insert response" in response.json['error']
   