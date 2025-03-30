from flask import Flask, request, jsonify
import psycopg2
from datetime import datetime

app = Flask(__name__)

db_conn = psycopg2.connect(
    dbname="neondb",
    user="neondb_owner",
    password="npg_L3fiTW6qKSDw",
    host="ep-icy-dawn-a4kubr5f.us-east-1.aws.neon.tech",
    sslmode="require"
)

cursor = db_conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS sensor_data (
        id SERIAL PRIMARY KEY,
        temperature FLOAT,
        heart_rate FLOAT,
        ecg INTEGER,
        timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );
""")
db_conn.commit()

@app.route('/sensor', methods=['POST'])
def receive_data():
    data = request.get_json()
    temperature = data.get('temperature')
    heart_rate = data.get('heart_rate')
    ecg = data.get('ecg')

    if temperature is None or heart_rate is None or ecg is None:
        return jsonify({'status': 'error', 'message': 'Lipsesc unele câmpuri'}), 400

    cursor.execute("""
        INSERT INTO sensor_data (temperature, heart_rate, ecg)
        VALUES (%s, %s, %s);
    """, (temperature, heart_rate, ecg))
    db_conn.commit()

    return jsonify({'status': 'success'}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
