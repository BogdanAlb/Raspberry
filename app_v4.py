import time
import board
import busio
import digitalio
import psycopg2
import logging
from adafruit_mcp3xxx.mcp3008 import MCP3008
from adafruit_mcp3xxx.analog_in import AnalogIn
import adafruit_mlx90614
from heartrate_monitor import HeartRateMonitor
import threading
import argparse

# Configurare logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# Configurare baza de date
DB_URL = "postgresql://neondb_owner:npg_L3fiTW6qKSDw@ep-icy-dawn-a4kubr5f.us-east-1.aws.neon.tech/neondb?sslmode=require"
PATIENT_ID = 5
DURATION = 10

# Initializare MCP3008 (ECG)
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D8)
mcp = MCP3008(spi, cs)
ecg_chan = AnalogIn(mcp, 0)

# Initializare MLX90614 (Temperatura)
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
mlx = adafruit_mlx90614.MLX90614(i2c)

# Argumente pentru MAX30102
parser = argparse.ArgumentParser(description="Read and print data from MAX30102")
parser.add_argument("-r", "--raw", action="store_true", help="print raw data instead of calculation result")
parser.add_argument("-t", "--time", type=int, default=DURATION, help="duration in seconds to read from sensor")
args = parser.parse_args()

# Variabile globale pentru puls și SpO2
pulse_rate = 0
spo2_level = 0
pulse_lock = threading.Lock()

# Funcție pentru thread-ul senzorului MAX30102
def read_pulse(duration):
    global pulse_rate, spo2_level
    hrm = HeartRateMonitor(print_raw=False, print_result=False)
    hrm.start_sensor()
    logging.info("Senzorul MAX30102 a fost pornit.")
    
    start_time = time.time()
    try:
        while time.time() - start_time < duration:
            with pulse_lock:
                pulse_rate = round(hrm.bpm, 2)
                spo2_level = round(hrm.spo2, 2)
            logging.info(f"Pulse: {pulse_rate} bpm | SpO2: {spo2_level}%")
            time.sleep(1)
    finally:
        hrm.stop_sensor()
        logging.info("Senzorul MAX30102 a fost oprit.")

# Conectare la baza de date
conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

# Verificare profil pacient
cur.execute("SELECT id FROM patient_profiles WHERE id = %s;", (PATIENT_ID,))
if not cur.fetchone():
    cur.execute("INSERT INTO patient_profiles (id) VALUES (%s);", (PATIENT_ID,))
    conn.commit()
    print(f"Profilul pacientului cu ID {PATIENT_ID} a fost adăugat.")

print(f"Incepem colectarea datelor timp de {DURATION} secunde...")

# Pornire thread pentru MAX30102
pulse_thread = threading.Thread(target=read_pulse, args=(DURATION,))
pulse_thread.start()

start_time = time.time()
while time.time() - start_time < DURATION:
    ecg_val = ecg_chan.value / 65535 * 3.3
    temp_obj = mlx.object_temperature

    with pulse_lock:
        current_pulse = float(pulse_rate)
        current_spo2 = float(spo2_level)

    print(f"ECG: {ecg_val:.3f} V | Temp: {temp_obj:.2f} °C | Pulse: {current_pulse:.0f} bpm | SpO₂: {current_spo2:.0f} %")

    # Evităm valori aberante
    if current_pulse > 250 or current_spo2 > 100:
        logging.warning("Valori suspecte detectate, sar linia...")
        time.sleep(1)
        continue

    cur.execute("""
        INSERT INTO parameters (patient_profile_id, ecg, temperature, pulse, spo2)
        VALUES (%s, %s, %s, %s, %s);
    """, (
        PATIENT_ID,
        float(ecg_val),
        float(temp_obj),
        current_pulse,
        current_spo2
    ))
    conn.commit()
    time.sleep(1)

pulse_thread.join()
print("Datele au fost salvate cu succes.")

cur.close()
conn.close()
