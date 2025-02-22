from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import json
import pytz

from flask_mail import Mail, Message
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
# In app.py
DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
TIMEZONE = pytz.timezone('America/Chicago')  # Central Time

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Your Gmail address
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # Your App Password
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

mail = Mail(app)

# Ensure upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Security configurations
# app.config['SERVER_NAME'] = 'swampstoner.com'
# app.config['PREFERRED_URL_SCHEME'] = 'https'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_current_time():
    return datetime.now(TIMEZONE)

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT NOT NULL,
            images TEXT,
            created_date TIMESTAMP DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now', 'localtime'))
        )
    ''')
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/posts')
def get_posts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 6, type=int)  # Number of posts per page
    
    conn = get_db()
    
    # Get total number of posts
    total_posts = conn.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get paginated posts
    posts = conn.execute(
        'SELECT * FROM posts ORDER BY created_date DESC LIMIT ? OFFSET ?',
        (per_page, offset)
    ).fetchall()
    
    # Convert rows to dictionaries
    posts_list = []
    for post in posts:
        post_dict = dict(post)
        post_dict['images'] = json.loads(post_dict['images']) if post_dict['images'] else []
        posts_list.append(post_dict)
    
    # Calculate total pages
    total_pages = (total_posts + per_page - 1) // per_page
    
    conn.close()
    
    return jsonify({
        'posts': posts_list,
        'total_pages': total_pages,
        'current_page': page,
        'per_page': per_page,
        'total_posts': total_posts
    })

@app.route('/api/post/<int:post_id>')
def get_post(post_id):
    conn = get_db()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()
    
    if post is None:
        return jsonify({'error': 'Post not found'}), 404
    
    post_dict = dict(post)
    post_dict['images'] = json.loads(post_dict['images']) if post_dict['images'] else []
    return jsonify(post_dict)

@app.route('/api/post', methods=['POST'])
def create_post():
    title = request.form.get('title')
    content = request.form.get('content')
    author = request.form.get('author')
    images = []
    
    # Handle multiple image uploads
    if 'images[]' in request.files:
        files = request.files.getlist('images[]')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                images.append(filename)
    
    conn = get_db()
    current_time = get_current_time().strftime('%Y-%m-%d %H:%M:%S')
    conn.execute('INSERT INTO posts (title, content, author, images, created_date) VALUES (?, ?, ?, ?, ?)',
                (title, content, author, json.dumps(images), current_time))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/post/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    title = request.form.get('title')
    content = request.form.get('content')
    author = request.form.get('author')
    
    conn = get_db()
    post = conn.execute('SELECT images FROM posts WHERE id = ?', (post_id,)).fetchone()
    current_images = json.loads(post['images']) if post and post['images'] else []
    
    # Handle new image uploads
    if 'images[]' in request.files:
        files = request.files.getlist('images[]')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                current_images.append(filename)
    
    conn.execute('UPDATE posts SET title = ?, content = ?, author = ?, images = ? WHERE id = ?',
                (title, content, author, json.dumps(current_images), post_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/post/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    conn = get_db()
    
    # Get images to delete
    post = conn.execute('SELECT images FROM posts WHERE id = ?', (post_id,)).fetchone()
    if post and post['images']:
        images = json.loads(post['images'])
        # Delete image files
        for image in images:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image))
            except:
                pass
    
    conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# @app.route('/')
# def index():
#     return send_from_directory('.', 'index.html')

# Keep these routes
@app.route('/links')
def links():
    return render_template('links.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# Keep this route (this is the one we want to use)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)



@app.route('/api/posts/all')
def get_all_posts():
    conn = get_db()
    posts = conn.execute('SELECT * FROM posts ORDER BY created_date DESC').fetchall()
    conn.close()
    
    # Convert rows to dictionaries
    posts_list = []
    for post in posts:
        post_dict = dict(post)
        post_dict['images'] = json.loads(post_dict['images']) if post_dict['images'] else []
        posts_list.append(post_dict)
    
    return jsonify(posts_list)




# Add this new route:
@app.route('/api/send-message', methods=['POST'])
def send_message():
    try:
        data = request.json
        msg = Message('New Message from SwamPStoner Blog',
                     sender=app.config['MAIL_DEFAULT_SENDER'],
                     recipients=[app.config['MAIL_USERNAME']])
        
        msg.body = f"""
        New message from SwamPStoner Blog:
        
        Name: {data.get('name')}
        Email: {data.get('email')}
        Message:
        {data.get('message')}
        """
        
        mail.send(msg)
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error sending email: {str(e)}")  # For debugging
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)