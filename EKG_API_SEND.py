import time
import board
import busio
import digitalio
from adafruit_mcp3xxx.mcp3008 import MCP3008
from adafruit_mcp3xxx.analog_in import AnalogIn
import requests
from flask import Flask, request, jsonify
import psycopg2
import threading

# Initializare interfata SPI hardware
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D8)  # CE0 = GPIO8
mcp = MCP3008(spi, cs)

# Citire canal 0 (OUTPUT AD8232 conectat la CH0)
chan = AnalogIn(mcp, 0)  # Foloseste canalul 0 direct

# Conexiunea la baza de date (modifică cu setările tale)
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="ecg_db",
        user="user",  # Schimbă cu utilizatorul tău PostgreSQL
        password="password"  # Schimbă cu parola ta
    )
    return conn

# Flask API pentru primirea datelor
app = Flask(__name__)

@app.route('/api/send_ecg', methods=['POST'])
def send_ecg():
    # Preia datele trimise în format JSON
    data = request.get_json()
    timestamp = data.get('timestamp')
    value = data.get('value')

    if not timestamp or not value:
        return jsonify({"error": "Missing data"}), 400

    # Salvează datele în baza de date
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO ecg_data (timestamp, value) VALUES (%s, %s)", (timestamp, value))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Data saved successfully"}), 200

# Funcție pentru a rula serverul Flask pe un thread separat
def run_flask():
    app.run(host='0.0.0.0', port=5000, use_reloader=False)  # use_reloader=False pentru a evita dubla rulare

# Funcție pentru colectarea și trimiterea datelor ECG
def collect_and_send_data():
    api_url = "http://localhost:5000/api/send_ecg"  # URL-ul API-ului (asigură-te că este corect)

    start_time = time.time()
    print("Citire semnal ECG pentru 15 secunde...")

    while time.time() - start_time < 15:  # rulează 15 secunde
        val = chan.value       # între 0 și 65535
        t = time.time() - start_time
        print(f"Timp: {t:.2f}s | Semnal ADC: {val}")

        # Trimite datele către API
        data = {
            "timestamp": t,
            "value": val
        }

        try:
            response = requests.post(api_url, json=data)
            if response.status_code == 200:
                print("Date trimise cu succes!")
            else:
                print(f"Eroare la trimiterea datelor: {response.status_code}")
        except Exception as e:
            print(f"Exception: {e}")
        
        time.sleep(0.01)  # 100 Hz

if __name__ == '__main__':
    # Crearea și lansarea thread-urilor pentru Flask și colectarea datelor
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    collect_and_send_data()
