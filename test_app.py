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

