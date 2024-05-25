from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3

app = Flask(__name__)

# Inicjalizacja bazy danych
def init_db():
    with sqlite3.connect('todo.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content TEXT NOT NULL
                    )''')
        conn.commit()

init_db()

@app.route('/')
def index():
    with sqlite3.connect('todo.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM tasks")
        tasks = c.fetchall()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    task_content = request.form['content']
    with sqlite3.connect('todo.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO tasks (content) VALUES (?)", (task_content,))
        conn.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    with sqlite3.connect('todo.db') as conn:
        c = conn.cursor()
        c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    return redirect(url_for('index'))

@app.route('/update/<int:task_id>', methods=['POST'])
def update_task(task_id):
    task_content = request.form['content']
    with sqlite3.connect('todo.db') as conn:
        c = conn.cursor()
        c.execute("UPDATE tasks SET content = ? WHERE id = ?", (task_content, task_id))
        conn.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
