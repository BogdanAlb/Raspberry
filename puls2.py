import time
import board
import busio
import digitalio
from adafruit_mcp3xxx.mcp3008 import MCP3008
from adafruit_mcp3xxx.analog_in import AnalogIn
import matplotlib.pyplot as plt

# Initializare interfata SPI hardware
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D8)  # CE0 = GPIO8
mcp = MCP3008(spi, cs)

# Citire canal 0 (OUTPUT AD8232 conectat la CH0)
chan = AnalogIn(mcp, 0)  # Foloseste canalul 0 direct

# Liste pentru grafic
ecg_values = []
timestamps = []

# Setează timpul de începere
start_time = time.time()

print("Citire semnal ECG pentru 15 secunde...")

# Începe citirea datelor pentru 15 secunde
while time.time() - start_time < 15:  # rulează 15 secunde
    val = chan.value       # între 0 și 65535
    t = time.time() - start_time
    print(f"Timp: {t:.2f}s | Semnal ADC: {val}")
    ecg_values.append(val)
    timestamps.append(t)
    time.sleep(0.01)  # 100 Hz

print("Timpul s-a încheiat. Se generează graficul...")

# Afisare grafic
plt.plot(timestamps, ecg_values)
plt.title("Semnal ECG de la AD8232")
plt.xlabel("Timp (s)")
plt.ylabel("Valoare ADC")
plt.grid(True)
plt.show()
