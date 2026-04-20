from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Инициализация БД
def init_db():
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS notes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  content TEXT,
                  created_at TEXT,
                  updated_at TEXT)''')
    conn.commit()
    conn.close()

# CRUD операции
@app.route('/api/notes', methods=['GET'])
def get_notes():
    """Получение всех заметок с пагинацией"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page - 1) * per_page
    
    conn = sqlite3.connect('notes.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM notes ORDER BY created_at DESC LIMIT ? OFFSET ?', 
              (per_page, offset))
    notes = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return jsonify({
        'page': page,
        'per_page': per_page,
        'total': len(notes),
        'notes': notes
    })

@app.route('/api/notes', methods=['POST'])
def create_note():
    """Создание заметки"""
    data = request.get_json()
    now = datetime.now().isoformat()
    
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('''INSERT INTO notes (title, content, created_at, updated_at)
                 VALUES (?, ?, ?, ?)''',
              (data['title'], data.get('content', ''), now, now))
    note_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'id': note_id, 'message': 'Note created'}), 201

@app.route('/api/notes/<int:note_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_note(note_id):
    conn = sqlite3.connect('notes.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    if request.method == 'GET':
        c.execute('SELECT * FROM notes WHERE id = ?', (note_id,))
        note = c.fetchone()
        conn.close()
        if note:
            return jsonify(dict(note))
        return jsonify({'error': 'Note not found'}), 404
        
    elif request.method == 'PUT':
        data = request.get_json()
        now = datetime.now().isoformat()
        c.execute('''UPDATE notes 
                     SET title = ?, content = ?, updated_at = ?
                     WHERE id = ?''',
                  (data['title'], data.get('content', ''), now, note_id))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Note updated'})
        
    elif request.method == 'DELETE':
        c.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Note deleted'})

# Настройка CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE')
    return response

if __name__ == '__main__':
    init_db()
    app.run(debug=True)