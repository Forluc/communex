from flask import Flask, render_template
import sqlite3
from psutil import cpu_percent, virtual_memory
import time

app = Flask(__name__)


def create_table():
    conn = sqlite3.connect('monitoring_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS performance_data (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            cpu_percent REAL,
            ram_percent REAL
        )
    ''')
    conn.commit()
    conn.close()


@app.route('/')
def index():
    return ('Добро пожаловать! <br>'
            'Для мониторинга CPU и RAM перейдите по ссылке: /monitoring <br>'
            'Для просмотра истории CPU и RAM перейдите по ссылке: /history')


@app.route('/monitoring')
def monitoring():
    create_table()
    conn = sqlite3.connect('monitoring_data.db')
    cursor = conn.cursor()

    cpu = cpu_percent(interval=1)
    ram = virtual_memory().percent

    timestamp = time.ctime()
    cursor.execute('INSERT INTO performance_data (timestamp, cpu_percent, ram_percent) VALUES (?, ?, ?)',
                   (timestamp, cpu, ram))
    conn.commit()
    conn.close()

    return f'CPU: {cpu}% <br> RAM: {ram}%'


@app.route('/history')
def history():
    conn = sqlite3.connect('monitoring_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM performance_data')
    data = cursor.fetchall()

    conn.close()

    timestamps = [row[1] for row in data]
    cpu_percentages = [row[2] for row in data]
    ram_percentages = [row[3] for row in data]

    return render_template('history.html', timestamps=timestamps, cpu_percentages=cpu_percentages,
                           ram_percentages=ram_percentages)


if __name__ == '__main__':
    app.run(debug=True)
