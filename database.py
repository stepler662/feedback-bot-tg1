import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT,
            category TEXT,
            question TEXT,
            answer TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_question(user_id, username, category, question):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO questions (user_id, username, category, question)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, category, question))
    conn.commit()
    conn.close()

def get_unread_questions():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, user_id, username, category, question
        FROM questions
        WHERE answer IS NULL
    ''')
    questions = cursor.fetchall()
    conn.close()
    return questions

def save_answer(question_id, answer):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE questions
        SET answer = ?
        WHERE id = ?
    ''', (answer, question_id))
    conn.commit()
    conn.close()

def get_user_id_by_question_id(question_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user_id FROM questions WHERE id = ?
    ''', (question_id,))
    user_id = cursor.fetchone()
    conn.close()
    return user_id[0] if user_id else None