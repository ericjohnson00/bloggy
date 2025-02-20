from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/posts')
def get_posts():
    conn = get_db()
    posts = conn.execute('SELECT * FROM posts ORDER BY created_date DESC').fetchall()
    conn.close()
    
    posts_list = []
    for post in posts:
        post_dict = dict(post)
        post_dict['images'] = json.loads(post_dict['images']) if post_dict['images'] else []
        posts_list.append(post_dict)
    
    return jsonify(posts_list)

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
    
    if 'images[]' in request.files:
        files = request.files.getlist('images[]')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                images.append(filename)
    
    conn = get_db()
    conn.execute('INSERT INTO posts (title, content, author, images) VALUES (?, ?, ?, ?)',
                (title, content, author, json.dumps(images)))
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
    
    post = conn.execute('SELECT images FROM posts WHERE id = ?', (post_id,)).fetchone()
    if post and post['images']:
        images = json.loads(post['images'])
        for image in images:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image))
            except:
                pass
    
    conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)