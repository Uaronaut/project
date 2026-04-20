import pytest
import json
from app import app

@pytest.fixture
def client():
    """Тестовый клиент Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Здесь можно создать отдельную тестовую БД
        yield client

def test_get_empty_notes(client):
    """GET /api/notes — сначала заметок нет"""
    rv = client.get('/api/notes')
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data['notes'] == []

def test_create_note(client):
    """POST /api/notes — создание заметки"""
    rv = client.post('/api/notes',
                     data=json.dumps({'title': 'Test', 'content': 'Content'}),
                     content_type='application/json')
    assert rv.status_code == 201
    data = json.loads(rv.data)
    assert 'id' in data

def test_get_one_note(client):
    """GET /api/notes/<id> — получение одной заметки"""
    # Сначала создадим заметку
    rv = client.post('/api/notes',
                     data=json.dumps({'title': 'Get me', 'content': 'Hello'}),
                     content_type='application/json')
    note_id = json.loads(rv.data)['id']
    
    rv = client.get(f'/api/notes/{note_id}')
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data['title'] == 'Get me'

def test_update_note(client):
    """PUT /api/notes/<id> — обновление заметки"""
    # Создаём
    rv = client.post('/api/notes',
                     data=json.dumps({'title': 'Old', 'content': 'Old content'}),
                     content_type='application/json')
    note_id = json.loads(rv.data)['id']
    
    # Обновляем
    rv = client.put(f'/api/notes/{note_id}',
                    data=json.dumps({'title': 'New', 'content': 'New content'}),
                    content_type='application/json')
    assert rv.status_code == 200
    
    # Проверяем
    rv = client.get(f'/api/notes/{note_id}')
    data = json.loads(rv.data)
    assert data['title'] == 'New'

def test_delete_note(client):
    """DELETE /api/notes/<id> — удаление заметки"""
    rv = client.post('/api/notes',
                     data=json.dumps({'title': 'To delete', 'content': ''}),
                     content_type='application/json')
    note_id = json.loads(rv.data)['id']
    
    rv = client.delete(f'/api/notes/{note_id}')
    assert rv.status_code == 200
    
    # Проверяем, что заметки нет
    rv = client.get(f'/api/notes/{note_id}')
    assert rv.status_code == 404

def test_note_not_found(client):
    """GET несуществующей заметки — 404"""
    rv = client.get('/api/notes/9999')
    assert rv.status_code == 404