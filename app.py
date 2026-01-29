from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import random
import json
from datetime import datetime
from ml_model import get_dropout_percentage, can_user_signup
from languages import get_text, get_available_languages

# Python 3.14 compatibility fix for Flask
import sys
if sys.version_info >= (3, 13):
    import pkgutil
    if not hasattr(pkgutil, 'get_loader'):
        # Add stub for deprecated get_loader
        pkgutil.get_loader = lambda name: None

DATABASE = 'hexecutioners.db'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'pdf', 'png'}

app = Flask(__name__)
app.secret_key = 'your_secret_key_change_this'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table if it doesn't exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if not cursor.fetchone():
        conn.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
    
    # Create game_scores table if it doesn't exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='game_scores'")
    if not cursor.fetchone():
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
    
    # Create documents table if it doesn't exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='documents'")
    if not cursor.fetchone():
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
    
    # Create assessments table if it doesn't exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assessments'")
    if not cursor.fetchone():
        conn.execute('''
            CREATE TABLE assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                age TEXT NOT NULL,
                passed12th TEXT NOT NULL,
                gender TEXT NOT NULL,
                familyMembers TEXT NOT NULL,
                earningMembers TEXT NOT NULL,
                highestEducation TEXT NOT NULL,
                familyHealthCondition TEXT NOT NULL,
                familySupport TEXT NOT NULL,
                dailyChores TEXT NOT NULL,
                groupActivities TEXT NOT NULL,
                sportsRating INTEGER NOT NULL,
                communicationRating INTEGER NOT NULL,
                technologyComfort TEXT NOT NULL,
                pastProgram TEXT NOT NULL,
                reasonForJoining TEXT NOT NULL,
                dailyCommitment TEXT NOT NULL,
                travelComfort TEXT NOT NULL,
                workExperience TEXT NOT NULL,
                healthCondition TEXT NOT NULL,
                programBenefit TEXT NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
    
    conn.commit()
    conn.close()

# Initialize database on app startup
try:
    init_db()
except Exception as e:
    print(f"Warning: Database initialization error: {e}")

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    # If not logged in, show welcome page with new user / returning user options
    response = make_response(render_template('welcome.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/pre-assessment')
def pre_assessment():
    # If already logged in, redirect to dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    # Get language from query parameter or default to English
    lang = request.args.get('lang', 'en')
    if lang not in ['en', 'hi', 'kn']:
        lang = 'en'
    
    return render_template('pre_assessment.html', lang=lang)

@app.route('/submit-pre-assessment', methods=['POST'])
def submit_pre_assessment():
    """
    Submit pre-assessment form with contact and personal details
    Run LightGBM ML model to determine dropout risk
    """
    try:
        data = request.json
        
        # Log raw frontend data
        print("\n" + "="*100)
        print("FRONTEND DATA RECEIVED - RAW JSON:")
        print("="*100)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("="*100 + "\n")
        
        # Get language from request
        lang = data.get('language', 'en')
        
        # Get dropout percentage from ML model
        dropout_percentage = get_dropout_percentage(data)
        can_signup = can_user_signup(dropout_percentage, threshold=70)
        
        # Store in session for use during signup
        session['pre_assessment_data'] = data
        session['dropout_percentage'] = dropout_percentage
        session['can_signup'] = can_signup
        session['language'] = lang
        
        print(f"Assessment submitted - Dropout risk: {dropout_percentage}%, Can signup: {can_signup}")
        
        return jsonify({
            'success': True,
            'dropout_percentage': dropout_percentage,
            'can_signup': can_signup
        })
    
    except Exception as e:
        print(f"Pre-assessment error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/submit-pre-login-assessment', methods=['POST'])
def submit_pre_login_assessment():
    """
    Submit pre-login assessment and run ML model to determine dropout risk
    (Legacy endpoint - kept for backward compatibility)
    """
    return submit_pre_assessment()

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
            
            # Create assessments table if it doesn't exist
            conn = get_db_connection()
            conn.execute('''
                CREATE TABLE IF NOT EXISTS assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    age TEXT NOT NULL,
                    passed12th TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    familyMembers TEXT NOT NULL,
                    earningMembers TEXT NOT NULL,
                    highestEducation TEXT NOT NULL,
                    familyHealthCondition TEXT NOT NULL,
                    familySupport TEXT NOT NULL,
                    dailyChores TEXT NOT NULL,
                    groupActivities TEXT NOT NULL,
                    sportsRating INTEGER NOT NULL,
                    communicationRating INTEGER NOT NULL,
                    technologyComfort TEXT NOT NULL,
                    pastProgram TEXT NOT NULL,
                    reasonForJoining TEXT NOT NULL,
                    dailyCommitment TEXT NOT NULL,
                    travelComfort TEXT NOT NULL,
                    workExperience TEXT NOT NULL,
                    healthCondition TEXT NOT NULL,
                    programBenefit TEXT NOT NULL,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            conn.commit()
            
            # Check if user has completed assessment (post-login assessment)
            assessment = conn.execute(
                'SELECT id FROM assessments WHERE user_id = ?',
                (user['id'],)
            ).fetchone()
            conn.close()
            
            if not assessment:
                return redirect(url_for('assessment'))
            
            return redirect(url_for('dashboard'))
        else:
            lang = session.get('language', 'en')
            return render_template('login.html', error=get_text('invalid_credentials', lang), lang=lang)
    
    lang = session.get('language', 'en')
    return render_template('login.html', lang=lang)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        
        try:
            user_id = conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                        (username, email, hashed_password)).lastrowid
            
            # Store pre-assessment data for new user
            assessment_data = session.get('pre_assessment_data', {})
            conn.execute(
                '''INSERT INTO assessments (
                    user_id, age, passed12th, gender, familyMembers, earningMembers,
                    highestEducation, familyHealthCondition, familySupport, dailyChores,
                    groupActivities, sportsRating, communicationRating, technologyComfort,
                    pastProgram, reasonForJoining, dailyCommitment, travelComfort,
                    workExperience, healthCondition, programBenefit
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    user_id,
                    assessment_data.get('age'),
                    assessment_data.get('passed12th'),
                    assessment_data.get('gender'),
                    assessment_data.get('familyMembers'),
                    assessment_data.get('earningMembers'),
                    assessment_data.get('highestEducation'),
                    assessment_data.get('familyHealthCondition'),
                    assessment_data.get('familySupport'),
                    assessment_data.get('dailyChores'),
                    assessment_data.get('groupActivities'),
                    int(assessment_data.get('sportsRating', 0)),
                    int(assessment_data.get('communicationRating', 0)),
                    assessment_data.get('technologyComfort'),
                    assessment_data.get('pastProgram'),
                    assessment_data.get('reasonForJoining'),
                    assessment_data.get('dailyCommitment'),
                    assessment_data.get('travelComfort'),
                    assessment_data.get('workExperience'),
                    assessment_data.get('healthCondition'),
                    assessment_data.get('programBenefit')
                )
            )
            
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except Exception as e:
            conn.close()
            lang = session.get('language', 'en')
            return render_template('signup.html', error=str(e), lang=lang)
    
    lang = session.get('language', 'en')
    return render_template('signup.html', lang=lang)

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
    
    lang = session.get('language', 'en')
    return render_template('dashboard.html', username=session['username'], game_scores=game_scores, lang=lang)

@app.route('/games')
def games():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    lang = session.get('language', 'en')
    return render_template('games.html', username=session['username'], lang=lang)

@app.route('/game/number-guess')
def number_guess():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    lang = session.get('language', 'en')
    return render_template('number_guess.html', lang=lang)

@app.route('/game/memory')
def memory_game():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    lang = session.get('language', 'en')
    return render_template('memory.html', lang=lang)

@app.route('/game/trivia')
def trivia_game():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    lang = session.get('language', 'en')
    return render_template('trivia.html', lang=lang)

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

@app.route('/change-language', methods=['POST'])
def change_language():
    data = request.json
    lang = data.get('language', 'en')
    session['language'] = lang
    return jsonify({'success': True})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/assessment')
def assessment():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Check if user has already completed assessment
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            age TEXT NOT NULL,
            passed12th TEXT NOT NULL,
            gender TEXT NOT NULL,
            familyMembers TEXT NOT NULL,
            earningMembers TEXT NOT NULL,
            highestEducation TEXT NOT NULL,
            familyHealthCondition TEXT NOT NULL,
            familySupport TEXT NOT NULL,
            dailyChores TEXT NOT NULL,
            groupActivities TEXT NOT NULL,
            sportsRating INTEGER NOT NULL,
            communicationRating INTEGER NOT NULL,
            technologyComfort TEXT NOT NULL,
            pastProgram TEXT NOT NULL,
            reasonForJoining TEXT NOT NULL,
            dailyCommitment TEXT NOT NULL,
            travelComfort TEXT NOT NULL,
            workExperience TEXT NOT NULL,
            healthCondition TEXT NOT NULL,
            programBenefit TEXT NOT NULL,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    
    existing_assessment = conn.execute(
        'SELECT id FROM assessments WHERE user_id = ?',
        (session['user_id'],)
    ).fetchone()
    conn.close()
    
    if existing_assessment:
        return redirect(url_for('dashboard'))
    
    lang = session.get('language', 'en')
    return render_template('assessment.html', lang=lang)

@app.route('/submit-assessment', methods=['POST'])
def submit_assessment():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    try:
        data = request.json
        
        conn = get_db_connection()
        
        # Create table if it doesn't exist
        conn.execute('''
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                age TEXT NOT NULL,
                passed12th TEXT NOT NULL,
                gender TEXT NOT NULL,
                familyMembers TEXT NOT NULL,
                earningMembers TEXT NOT NULL,
                highestEducation TEXT NOT NULL,
                familyHealthCondition TEXT NOT NULL,
                familySupport TEXT NOT NULL,
                dailyChores TEXT NOT NULL,
                groupActivities TEXT NOT NULL,
                sportsRating INTEGER NOT NULL,
                communicationRating INTEGER NOT NULL,
                technologyComfort TEXT NOT NULL,
                pastProgram TEXT NOT NULL,
                reasonForJoining TEXT NOT NULL,
                dailyCommitment TEXT NOT NULL,
                travelComfort TEXT NOT NULL,
                workExperience TEXT NOT NULL,
                healthCondition TEXT NOT NULL,
                programBenefit TEXT NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()
        
        conn.execute(
            '''INSERT INTO assessments (
                user_id, age, passed12th, gender, familyMembers, earningMembers,
                highestEducation, familyHealthCondition, familySupport, dailyChores,
                groupActivities, sportsRating, communicationRating, technologyComfort,
                pastProgram, reasonForJoining, dailyCommitment, travelComfort,
                workExperience, healthCondition, programBenefit
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                session['user_id'],
                data.get('age'),
                data.get('passed12th'),
                data.get('gender'),
                data.get('familyMembers'),
                data.get('earningMembers'),
                data.get('highestEducation'),
                data.get('familyHealthCondition'),
                data.get('familySupport'),
                data.get('dailyChores'),
                data.get('groupActivities'),
                int(data.get('sportsRating', 0)),
                int(data.get('communicationRating', 0)),
                data.get('technologyComfort'),
                data.get('pastProgram'),
                data.get('reasonForJoining'),
                data.get('dailyCommitment'),
                data.get('travelComfort'),
                data.get('workExperience'),
                data.get('healthCondition'),
                data.get('programBenefit')
            )
        )
        conn.commit()
        conn.close()
        
        print(f"Assessment submitted for user {session['user_id']}")
        return jsonify({'success': True, 'message': 'Assessment submitted successfully'})
    
    except Exception as e:
        print(f"Assessment error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/skip-assessment', methods=['POST'])
def skip_assessment():
    if 'user_id' not in session:
        return jsonify({'success': False}), 401
    
    try:
        conn = get_db_connection()
        
        # Create table if it doesn't exist
        conn.execute('''
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                age TEXT NOT NULL,
                passed12th TEXT NOT NULL,
                gender TEXT NOT NULL,
                familyMembers TEXT NOT NULL,
                earningMembers TEXT NOT NULL,
                highestEducation TEXT NOT NULL,
                familyHealthCondition TEXT NOT NULL,
                familySupport TEXT NOT NULL,
                dailyChores TEXT NOT NULL,
                groupActivities TEXT NOT NULL,
                sportsRating INTEGER NOT NULL,
                communicationRating INTEGER NOT NULL,
                technologyComfort TEXT NOT NULL,
                pastProgram TEXT NOT NULL,
                reasonForJoining TEXT NOT NULL,
                dailyCommitment TEXT NOT NULL,
                travelComfort TEXT NOT NULL,
                workExperience TEXT NOT NULL,
                healthCondition TEXT NOT NULL,
                programBenefit TEXT NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()
        
        # Mark assessment as skipped
        conn.execute(
            '''INSERT INTO assessments (
                user_id, age, passed12th, gender, familyMembers, earningMembers,
                highestEducation, familyHealthCondition, familySupport, dailyChores,
                groupActivities, sportsRating, communicationRating, technologyComfort,
                pastProgram, reasonForJoining, dailyCommitment, travelComfort,
                workExperience, healthCondition, programBenefit
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (session['user_id'], 'skipped', 'skipped', 'skipped', 'skipped', 'skipped',
             'skipped', 'skipped', 'skipped', 'skipped', 'skipped', 0, 0, 'skipped',
             'skipped', 'skipped', 'skipped', 'skipped', 'skipped', 'skipped', 'skipped')
        )
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Skip assessment error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

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
    
    lang = session.get('language', 'en')
    return render_template('profile.html', user=user, documents=doc_dict, lang=lang)

@app.route('/user-details')
def user_details():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    
    lang = session.get('language', 'en')
    return render_template('user_details.html', user=user, lang=lang)

@app.route('/upload-documents-page')
def upload_documents_page():
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
    
    documents = conn.execute(
        'SELECT * FROM documents WHERE user_id = ? AND document_type IN (?, ?) ORDER BY uploaded_at DESC',
        (session['user_id'], 'Aadhar Card', '12th Marksheet')
    ).fetchall()
    conn.close()
    
    doc_dict = {}
    for doc in documents:
        doc_dict[doc['document_type']] = doc
    
    return render_template('upload_documents.html', documents=doc_dict)

@app.route('/upload-document', methods=['POST'])
def upload_document():
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        if 'document' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['document']
        doc_type = request.form.get('document_type')
        
        print(f"Upload attempt - File: {file.filename}, Type: {doc_type}, User: {session['user_id']}")
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type. Only JPG, PNG, and PDF allowed'}), 400
        
        if not doc_type:
            return jsonify({'success': False, 'error': 'Document type not specified'}), 400
        
        # Create user upload folder
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(session['user_id']))
        os.makedirs(user_folder, exist_ok=True)
        print(f"User folder created: {user_folder}")
        
        # Generate secure filename
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        filename = secure_filename(f"{doc_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}")
        filepath = os.path.join(user_folder, filename)
        
        # Save file
        file.save(filepath)
        print(f"File saved to: {filepath}")
        
        # Verify file was saved
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'File save failed'}), 500
        
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
        
        print(f"Document saved to database successfully")
        return jsonify({'success': True, 'message': f'{doc_type} uploaded successfully'})
    
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

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

@app.route('/grid-escape')
def grid_escape():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    lang = session.get('language', 'en')
    return render_template('grid_escape.html', lang=lang)

@app.route('/pattern-lock')
def pattern_lock():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    lang = session.get('language', 'en')
    return render_template('pattern_lock.html', lang=lang)

@app.route('/chart-detective')
def chart_detective():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    lang = session.get('language', 'en')
    return render_template('chart_detective.html', lang=lang)

@app.route('/learning-modules')
def learning_modules():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    lang = session.get('language', 'en')
    return render_template('learning_modules.html', lang=lang)

@app.route('/leaderboard')
def leaderboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get all users with their scores
    users = conn.execute(
        '''SELECT u.id, u.username, 
           COALESCE(SUM(CAST(gs.score AS INTEGER)), 0) as total_score,
           COUNT(DISTINCT gs.id) as games_played
        FROM users u
        LEFT JOIN game_scores gs ON u.id = gs.user_id
        GROUP BY u.id
        ORDER BY total_score DESC'''
    ).fetchall()
    
    conn.close()
    
    lang = session.get('language', 'en')
    return render_template('leaderboard.html', users=users, current_user_id=session['user_id'], lang=lang)

@app.route('/skill-performance')
def skill_performance():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get user's game scores to calculate skills
    game_scores = conn.execute(
        'SELECT game_name, score FROM game_scores WHERE user_id = ? ORDER BY game_name',
        (session['user_id'],)
    ).fetchall()
    
    conn.close()
    
    lang = session.get('language', 'en')
    return render_template('skill_performance.html', game_scores=game_scores, lang=lang)

if __name__ == '__main__':
    init_db()
    app.run(debug=False)

