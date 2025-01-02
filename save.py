import os
import sqlite3

# 连接到 SQLite 数据库（如果数据库不存在，则会创建一个新的数据库）
conn = sqlite3.connect('news_database.db')
conn.isolation_level = None  # 使用显式事务
cursor = conn.cursor()

# 创建表
cursor.execute('''
CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    link TEXT UNIQUE,
    content TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    news_id INTEGER,
    image_path TEXT,
    FOREIGN KEY (news_id) REFERENCES news(id)
)
''')

# 遍历 news_data 目录中的所有文件夹
news_data_dir = 'news_data'
for folder_name in os.listdir(news_data_dir):
    folder_path = os.path.join(news_data_dir, folder_name)
    if os.path.isdir(folder_path):
        # 开始事务
        conn.execute('BEGIN TRANSACTION')
        try:
            # 读取 title
            with open(os.path.join(folder_path, 'title.txt'), 'r', encoding='utf-8') as f:
                title = f.read().strip()

            # 读取 link
            with open(os.path.join(folder_path, 'link.txt'), 'r', encoding='utf-8') as f:
                link = f.read().strip()

            # 读取 content
            with open(os.path.join(folder_path, 'content.txt'), 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查是否存在相同的 link
            cursor.execute('SELECT id FROM news WHERE link = ?', (link,))
            result = cursor.fetchone()
            if result:
                news_id = result[0]
                cursor.execute('''
                UPDATE news SET title = ?, content = ? WHERE id = ?
                ''', (title, content, news_id))
            else:
                cursor.execute('''
                INSERT INTO news (title, link, content)
                VALUES (?, ?, ?)
                ''', (title, link, content))
                news_id = cursor.lastrowid

            # 处理 images
            # 先删除原有图片记录
            cursor.execute('DELETE FROM images WHERE news_id = ?', (news_id,))

            # 查找并插入图片路径
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                if os.path.isfile(file_path) and file_name.lower().endswith('.jpg'):
                    print(f"Inserting image for news_id {news_id}: {file_path}")
                    cursor.execute('''
                                INSERT INTO images (news_id, image_path)
                                VALUES (?, ?)
                                ''', (news_id, file_path))

            # 提交事务
            conn.execute('COMMIT')
        except Exception as e:
            conn.execute('ROLLBACK')
            print(f"Error processing folder {folder_path}: {e}")
            raise

# 关闭连接
conn.close()
