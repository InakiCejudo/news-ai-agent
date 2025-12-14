from db import get_db_connection

def insert_post(title, summary, image_url=None):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        'INSERT INTO posts (title, summary, image_url) VALUES (?, ?, ?)',
        (title, summary, image_url)
    )
    conn.commit()
    post_id = c.lastrowid
    conn.close()
    return post_id

def get_posts():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts ORDER BY created_at DESC').fetchall()
    conn.close()
    return [dict(post) for post in posts]
