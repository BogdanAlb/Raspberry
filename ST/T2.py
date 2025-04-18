import 
import time

m = max30102.MAX30102()

try:
    print("Citire valori MAX30102... Ctrl+C pentru a opri.")
    while True:
        red, ir = m.read_sequential()
        if red and ir:
            print(f"Red: {red[-1]}, IR: {ir[-1]}")
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nOprire test.")
except Exception as e:
    print(f"Eroare: {e}")
