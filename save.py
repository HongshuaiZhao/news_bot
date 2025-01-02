import os
import sqlite3

NEWS_DATA_DIR = 'news_data'

conn = sqlite3.connect('news_database.db')
conn.isolation_level = None
cursor = conn.cursor()


def column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    for column in cursor.fetchall():
        if column[1] == column_name:
            return True
    return False


# Check and create the news table if it doesn't exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='news'")
table_exists = cursor.fetchone() is not None

if not table_exists:
    cursor.execute('''
    CREATE TABLE news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        link TEXT UNIQUE,
        content TEXT,
        channel TEXT
    )
    ''')
else:
    # Add channel column if it doesn't exist
    if not column_exists(cursor, 'news', 'channel'):
        cursor.execute('ALTER TABLE news ADD COLUMN channel TEXT')

# Check and create the images table if it doesn't exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='images'")
images_table_exists = cursor.fetchone() is not None

if not images_table_exists:
    cursor.execute('''
    CREATE TABLE images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        news_id INTEGER,
        image_path TEXT,
        FOREIGN KEY (news_id) REFERENCES news(id)
    )
    ''')

for channel_name in os.listdir(NEWS_DATA_DIR):
    channel_path = os.path.join(NEWS_DATA_DIR, channel_name)
    if os.path.isdir(channel_path):
        for folder_name in os.listdir(channel_path):
            folder_path = os.path.join(channel_path, folder_name)
            if os.path.isdir(folder_path):
                try:
                    with open(os.path.join(folder_path, 'title.txt'), 'r', encoding='utf-8') as f:
                        title = f.read().strip()
                    with open(os.path.join(folder_path, 'link.txt'), 'r', encoding='utf-8') as f:
                        link = f.read().strip()
                    with open(os.path.join(folder_path, 'content.txt'), 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Check if the link already exists in the database
                    cursor.execute('SELECT id FROM news WHERE link = ?', (link,))
                    result = cursor.fetchone()
                    if result:
                        news_id = result[0]
                        # Update existing record with channel information
                        cursor.execute('''
                        UPDATE news SET title = ?, content = ?, channel = ? WHERE id = ?
                        ''', (title, content, channel_name, news_id))
                    else:
                        # Insert a new record including channel information
                        cursor.execute('''
                        INSERT INTO news (title, link, content, channel)
                        VALUES (?, ?, ?, ?)
                        ''', (title, link, content, channel_name))
                        news_id = cursor.lastrowid

                    # Delete existing images for this news item
                    cursor.execute('DELETE FROM images WHERE news_id = ?', (news_id,))

                    # Insert new images
                    for file_name in os.listdir(folder_path):
                        if file_name.startswith('image_') and file_name.endswith('.jpg'):
                            image_path_relative = os.path.relpath(os.path.join(folder_path, file_name),
                                                                  start=NEWS_DATA_DIR)
                            cursor.execute('''
                            INSERT INTO images (news_id, image_path)
                            VALUES (?, ?)
                            ''', (news_id, image_path_relative))
                except Exception as e:
                    print(f'Error processing {folder_path}: {e}')
                    conn.rollback()

conn.close()