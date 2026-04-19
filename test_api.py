import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_notes(client):
    """Тест получения списка заметок"""
    rv = client.get('/api/notes')
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert 'notes' in data

def test_create_note(client):
    """Тест создания заметки"""
    note_data = {
        'title': 'Test Note',
        'content': 'Test Content'
    }
    rv = client.post('/api/notes', 
                     data=json.dumps(note_data),
                     content_type='application/json')
    assert rv.status_code == 201
    data = json.loads(rv.data)
    assert 'id' in data

def test_note_not_found(client):
    """Тест обработки ошибки 404"""
    rv = client.get('/api/notes/9999')
    assert rv.status_code == 404