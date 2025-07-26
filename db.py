# db.py
import sqlite3
from datetime import datetime

DB_NAME = 'tasks.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            priority INTEGER CHECK(priority BETWEEN 0 AND 10),
            soft_deadline TEXT,
            hard_deadline TEXT,
            completed INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def add_task(title, priority, soft_deadline, hard_deadline):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO tasks (title, priority, soft_deadline, hard_deadline)
        VALUES (?, ?, ?, ?)
    ''', (title, priority, soft_deadline, hard_deadline))
    conn.commit()
    conn.close()

def get_all_tasks():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM tasks ORDER BY priority DESC')
    rows = c.fetchall()
    conn.close()
    return rows

def delete_task(task_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

def mark_task_completed(task_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    completion_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute('UPDATE tasks SET completed = 1 ,completion_time = ? where id = ?',(completion_time,task_id,))
    conn.commit()
    conn.close()

def get_active_tasks():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM tasks WHERE completed = 0 ORDER BY priority DESC')
    rows = c.fetchall()
    conn.close()
    return rows

def get_completed_tasks():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM tasks WHERE completed = 1 ORDER BY hard_deadline DESC')
    rows = c.fetchall()
    conn.close()
    return rows

def add_new_columns():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    try:
        c.execute('ALTER TABLE tasks ADD COLUMN completion_time TEXT')
        conn.commit()
        print("成功添加")
    except sqlite3.OperationalError as e:
        print("列已经存在",e)
    finally:
        conn.close()

    