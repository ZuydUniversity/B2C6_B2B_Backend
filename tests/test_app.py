import pytest
import json
from unittest.mock import patch, MagicMock
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_patients(client):
    with patch('app.mysql.connector.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = [
            {"id": 1, "first_name": "John", "last_name": "Doe", "birth_date": "2000-01-01", "gender": "M"}
        ]
        mock_connect.return_value = mock_conn
        
        response = client.get('/api/patients')
        
        assert response.status_code == 200
        assert response.json == [
            {"id": 1, "first_name": "John", "last_name": "Doe", "birth_date": "2000-01-01", "gender": "M"}
        ]

def test_get_results(client):
    with patch('app.mysql.connector.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = [
            {"id": 1, "patient_id": 1, "type": "Radiologie", "date": "2023-01-01 00:00:00"}
        ]
        mock_connect.return_value = mock_conn
        
        response = client.get('/api/results')
        
        assert response.status_code == 200
        assert response.json == [
            {"id": 1, "patient_id": 1, "type": "Radiologie", "date": "2023-01-01 00:00:00"}
        ]

def test_get_result_by_id(client):
    with patch('app.mysql.connector.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = {
            "id": 1, "patient_id": 1, "type": "Radiologie", "date": "2023-01-01 00:00:00"
        }
        mock_connect.return_value = mock_conn

        response = client.get('/api/results/1')
        
        assert response.status_code == 200
        assert response.json == {
            "id": 1,
            "patient_id": 1,
            "type": "Radiologie",
            "date": "2023-01-01 00:00:00",
            "details": {},
            "blood_chemistry": []
        }

def test_login_success(client):
    with patch('app.mysql.connector.connect') as mock_connect, \
         patch('app.bcrypt.check_password_hash') as mock_check_password_hash:
        
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = (1, 'dokterUno@gmail.com', 'nep1', '$2a$12$oYr5vPvrOGtin/H8T3pc1OmmqIMVp5OqIvQnCzC38N//ShBaX82Sm')
        mock_connect.return_value = mock_conn
        mock_check_password_hash.return_value = True
        
        response = client.post('/login', json={
            'email': 'dokterUno@gmail.com',
            'password': 'w8w',
            'employeeNumber': 'nep1'
        })
        
        assert response.status_code == 200
        assert response.json == {'message': 'Login successful'}

def test_login_failure(client):
    with patch('app.mysql.connector.connect') as mock_connect, \
         patch('app.bcrypt.check_password_hash') as mock_check_password_hash:
        
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = None
        mock_connect.return_value = mock_conn
        mock_check_password_hash.return_value = False
        
        response = client.post('/login', json={
            'email': 'wrong@example.com',
            'password': 'wrongpassword',
            'employeeNumber': '54321'
        })
        
        assert response.status_code == 401
        assert response.json == {'message': 'Invalid email, employeeNumber, or password'}
