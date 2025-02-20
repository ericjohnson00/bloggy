# init_db.py
import sqlite3
import os

def init_database():
    # Make sure the instance folder exists
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    # Connect to database (this will create it if it doesn't exist)
    conn = sqlite3.connect('instance/database.db')
    cursor = conn.cursor()

    # Create posts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        author TEXT NOT NULL,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Insert some sample data
    sample_posts = [
        ('First Post', 'This is the content of my first post.', 'Admin', '2024-02-20 10:00:00'),
        ('Second Post', 'This is another post to test with.', 'Admin', '2024-02-20 11:00:00')
    ]

    cursor.executemany('''
    INSERT INTO posts (title, content, author, created_date)
    VALUES (?, ?, ?, ?)
    ''', sample_posts)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_database()