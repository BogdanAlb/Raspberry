import board
import busio as io
import adafruit_mlx90614
import requests
from time import sleep

# Initizare I2C si  senzor
i2c = io.I2C(board.SCL, board.SDA, frequency=100000)
mlx = adafruit_mlx90614.MLX90614(i2c)

# Citire temperaturi
ambientTemp = round(mlx.ambient_temperature, 2)
targetTemp = round(mlx.object_temperature, 2)

print("Ambient Temperature:", ambientTemp, "°C")
print("Target Temperature:", targetTemp, "°C")

# Trimitere catre API
url = "http://192.168.0.137:5000/api/temperature"  # IP-ul API-ului tau

data = {
    "ambient": ambientTemp,
    "target": targetTemp
}

try:
    response = requests.post(url, json=data)
    print("Status:", response.status_code, response.json())
except Exception as e:
    print("Error sending data:", e)

sleep(1)
