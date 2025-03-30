import time
import requests
import board
import busio
import digitalio
import socket

from gpiozero import LED
from adafruit_mlx90614 import MLX90614
from max30102 import MAX30102  # presupunem o bibliotecă third-party MAX30102
import spidev  # pentru AD8232 via ADC (ex: MCP3008)

# === LED-uri ===
led_wifi_on = LED(17)
led_wifi_off = LED(27)
led_transmit = LED(22)

# === Verificare conexiune WiFi ===
def check_wifi():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        led_wifi_on.on()
        led_wifi_off.off()
        return True
    except:
        led_wifi_on.off()
        led_wifi_off.on()
        return False

# === Inițializare senzori ===
i2c = busio.I2C(board.SCL, board.SDA)
mlx = MLX90614(i2c)
max30102 = MAX30102()
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

# === Citire ECG via ADC (ex: canal 0 MCP3008) ===
def read_adc(channel=0):
    r = spi.xfer2([1, (8 + channel) << 4, 0])
    value = ((r[1] & 3) << 8) + r[2]
    return value

# === Trimite datele către API ===
def send_data(temp, heart_rate, ecg_value):
    led_transmit.on()
    try:
        response = requests.post("https://exemplu.api/sensor", json={
            "temperature": temp,
            "heart_rate": heart_rate,
            "ecg": ecg_value,
        })
        print("Trimis:", response.status_code)
    except Exception as e:
        print("Eroare trimitere:", e)
    led_transmit.off()

# === Main Loop ===
def main():
    while True:
        wifi = check_wifi()
        if wifi:
            temp = mlx.object_temperature
            heart_rate = max30102.read_heart_rate()
            ecg = read_adc()
            send_data(temp, heart_rate, ecg)
        time.sleep(5)

if __name__ == "__main__":
    main()