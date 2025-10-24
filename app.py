from flask import Flask, jsonify, render_template, request
import sqlite3
import json
import os

app = Flask(__name__)

# List of available database files
DATABASE_FILES = {
    'docker': '/var/lib/open-webui/webui.db',
    'main': '/home/randy/programs/py_progs/openwebui/webui.db',
    'backup': '/home/randy/programs/py_progs/openwebui/backups/webui_backup_20250918_102142.db',
    'venv': '/home/randy/programs/py_progs/openwebui/venv/lib/python3.11/site-packages/open_webui/data/webui.db'
}

def get_db_connection(db_path):
    """Create a database connection to the specified database."""
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Serve the main HTML page."""
    return render_template('index.html')

@app.route('/api/databases', methods=['GET'])
def get_databases():
    """Return the list of available databases."""
    return jsonify(DATABASE_FILES)

@app.route('/api/chats', methods=['GET'])
def get_chats():
    """Get all chat sessions from a selected database."""
    db_key = request.args.get('db', 'main') # Default to 'main' db
    db_path = DATABASE_FILES.get(db_key)
    
    if not db_path:
        return jsonify({'error': 'Invalid database selected'}), 400

    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat';")
        if cursor.fetchone() is None:
            conn.close()
            return jsonify([]) # Return empty list if chat table doesn't exist

        cursor.execute('SELECT id, title, created_at, updated_at FROM chat ORDER BY updated_at DESC')
        
        chats = [{'id': row['id'], 'title': row['title'] if row['title'] else 'Untitled Chat'} for row in cursor.fetchall()]
        
        conn.close()
        return jsonify(chats)
    
    except Exception as e:
        print(f"Error in get_chats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chats/<chat_id>', methods=['GET'])
def get_chat_messages(chat_id):
    """Get messages for a specific chat from a selected database."""
    db_key = request.args.get('db', 'main')
    db_path = DATABASE_FILES.get(db_key)

    if not db_path:
        return jsonify({'error': 'Invalid database selected'}), 400

    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT chat, title FROM chat WHERE id = ?', (chat_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return jsonify({'error': 'Chat not found'}), 404
        
        chat_data = row['chat']
        
        if chat_data:
            messages_data = json.loads(chat_data)
            messages = messages_data.get('messages', [])
            return jsonify({'title': row['title'] if row['title'] else 'Untitled Chat', 'messages': messages})
        else:
            return jsonify({'title': row['title'] if row['title'] else 'Untitled Chat', 'messages': []})
    
    except Exception as e:
        print(f"Error in get_chat_messages: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
