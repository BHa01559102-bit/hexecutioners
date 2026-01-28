from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import random
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_change_this'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

DATABASE = 'users.db'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'pdf', 'png'}

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
        conn.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE game_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                game_name TEXT NOT NULL,
                score INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        conn.execute('''
            CREATE TABLE documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                document_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()
        conn.close()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            return render_template('signup.html', error='Passwords do not match')
        
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                        (username, email, hashed_password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('signup.html', error='Username or email already exists')
    
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Create table if it doesn't exist
    conn.execute('''
        CREATE TABLE IF NOT EXISTS game_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            game_name TEXT NOT NULL,
            score INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    
    scores = conn.execute(
        'SELECT game_name, MAX(score) as best_score FROM game_scores WHERE user_id = ? GROUP BY game_name',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    
    game_scores = {score['game_name']: score['best_score'] for score in scores}
    
    return render_template('dashboard.html', username=session['username'], game_scores=game_scores)

@app.route('/games')
def games():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('games.html', username=session['username'])

@app.route('/game/number-guess')
def number_guess():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('number_guess.html')

@app.route('/game/memory')
def memory_game():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('memory.html')

@app.route('/game/trivia')
def trivia_game():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('trivia.html')

@app.route('/api/save-score', methods=['POST'])
def save_score():
    if 'user_id' not in session:
        return jsonify({'success': False}), 401
    
    data = request.json
    game_name = data.get('game_name')
    score = data.get('score')
    
    conn = get_db_connection()
    
    # Create table if it doesn't exist
    conn.execute('''
        CREATE TABLE IF NOT EXISTS game_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            game_name TEXT NOT NULL,
            score INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.execute(
        'INSERT INTO game_scores (user_id, game_name, score) VALUES (?, ?, ?)',
        (session['user_id'], game_name, score)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Create documents table if it doesn't exist
    conn.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            document_type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    documents = conn.execute(
        'SELECT * FROM documents WHERE user_id = ? ORDER BY uploaded_at DESC',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    
    doc_dict = {}
    for doc in documents:
        doc_dict[doc['document_type']] = doc
    
    return render_template('profile.html', user=user, documents=doc_dict)

@app.route('/upload-document', methods=['POST'])
def upload_document():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    if 'document' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['document']
    doc_type = request.form.get('document_type')
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Invalid file type. Only JPG, PNG, and PDF allowed'}), 400
    
    if not doc_type:
        return jsonify({'success': False, 'error': 'Document type not specified'}), 400
    
    # Create user upload folder
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(session['user_id']))
    os.makedirs(user_folder, exist_ok=True)
    
    # Generate secure filename
    filename = secure_filename(f"{doc_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file.filename.rsplit('.', 1)[1].lower()}")
    filepath = os.path.join(user_folder, filename)
    
    # Save file
    file.save(filepath)
    
    # Save to database
    conn = get_db_connection()
    
    # Delete old document of same type
    conn.execute('DELETE FROM documents WHERE user_id = ? AND document_type = ?', 
                 (session['user_id'], doc_type))
    
    # Insert new document
    conn.execute(
        'INSERT INTO documents (user_id, document_type, file_path) VALUES (?, ?, ?)',
        (session['user_id'], doc_type, filepath)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': f'{doc_type} uploaded successfully'})

@app.route('/download-document/<int:doc_id>')
def download_document(doc_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    doc = conn.execute(
        'SELECT * FROM documents WHERE id = ? AND user_id = ?',
        (doc_id, session['user_id'])
    ).fetchone()
    conn.close()
    
    if not doc or not os.path.exists(doc['file_path']):
        return redirect(url_for('profile'))
    
    return send_file(doc['file_path'], as_attachment=True)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
