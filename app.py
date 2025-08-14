from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os

app = Flask(__name__)

# Database connection parameters
DB_NAME = os.getenv("DB_NAME", "your_db_name")
DB_USER = os.getenv("DB_USER", "your_db_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_db_password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS production (
            id SERIAL PRIMARY KEY,
            date TEXT NOT NULL,
            shift TEXT NOT NULL,
            units_produced INTEGER NOT NULL
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        date = request.form['date']
        shift = request.form['shift']
        units_produced = request.form['units_produced']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO production (date, shift, units_produced) VALUES (%s, %s, %s)',
            (date, shift, units_produced)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('form'))
    return render_template('form.html')

@app.route('/dashboard')
def dashboard():
    date_filter = request.args.get('date')
    shift_filter = request.args.get('shift')
    query = 'SELECT * FROM production WHERE 1=1'
    params = []
    if date_filter:
        query += ' AND date = %s'
        params.append(date_filter)
    if shift_filter:
        query += ' AND shift = %s'
        params.append(shift_filter)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('dashboard.html', data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
