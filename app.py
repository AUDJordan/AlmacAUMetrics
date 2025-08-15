from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os

app = Flask(__name__)

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS production (
            id SERIAL PRIMARY KEY,
            date TEXT,
            room TEXT,
            shift TEXT,
            works_order TEXT,
            product_code TEXT,
            last_unit_number INTEGER,
            hourly_target INTEGER,
            daily_target INTEGER,
            ops TEXT,
            time TEXT,
            vial_number TEXT,
            shipper_number TEXT,
            unit_number TEXT,
            hourly_produced INTEGER,
            zed1_rejects INTEGER,
            zed2_rejects INTEGER,
            zed_percent REAL,
            machine_rejects REAL,
            scale_rejects REAL,
            print_rejects REAL,
            notes TEXT
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def overview():
    if request.method == 'POST':
        fields = ['date', 'room', 'shift', 'works_order', 'product_code', 'last_unit_number',
                  'hourly_target', 'daily_target', 'ops', 'time', 'vial_number', 'shipper_number',
                  'unit_number', 'hourly_produced', 'zed1_rejects', 'zed2_rejects', 'zed_percent',
                  'machine_rejects', 'scale_rejects', 'print_rejects', 'notes']
        values = [request.form.get(field) for field in fields]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"""INSERT INTO production ({", ".join(fields)})
            VALUES ({", ".join(["%s"] * len(fields))})""",
            values
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('overview'))
    return render_template('overview.html')

@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM production')
    data = cursor.fetchall()

    summary = {
        'hourly_produced': sum(row[14] or 0 for row in data),
        'zed1_rejects': sum(row[15] or 0 for row in data),
        'zed2_rejects': sum(row[16] or 0 for row in data),
        'zed_percent': round(sum(row[17] or 0 for row in data), 2),
        'machine_rejects': round(sum(row[18] or 0 for row in data), 2),
        'scale_rejects': round(sum(row[19] or 0 for row in data), 2),
        'print_rejects': round(sum(row[20] or 0 for row in data), 2)
    }

    cursor.close()
    conn.close()
    return render_template('metrics_dashboard.html', data=data, summary=summary)

@app.route('/bavs_report')
def bavs_report():
    return render_template('bavs_report.html')

@app.route('/blister_report')
def blister_report():
    return render_template('blister_report.html')

@app.route('/changeover_report')
def changeover_report():
    return render_template('changeover_report.html')

@app.route('/metrics_dashboard')
def metrics_dashboard():
    return render_template('metrics_dashboard.html')

@app.route('/changeover_dashboard')
def changeover_dashboard():
    return render_template('changeover_dashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
