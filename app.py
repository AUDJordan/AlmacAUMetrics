
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        date = request.form['date']
        shift = request.form['shift']
        units_produced = request.form['units_produced']
        conn = sqlite3.connect('production.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO production (date, shift, units_produced) VALUES (?, ?, ?)',
                       (date, shift, units_produced))
        conn.commit()
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
        query += ' AND date = ?'
        params.append(date_filter)
    if shift_filter:
        query += ' AND shift = ?'
        params.append(shift_filter)
    conn = sqlite3.connect('production.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

