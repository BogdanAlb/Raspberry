# Proiect Monitorizare Semne Vitale - Raspberry Pi

Acest proiect monitorizează semne vitale (ECG, temperatură corporală, puls și SpO₂) folosind un Raspberry Pi Zero 2 W și următorii senzori:

- **MAX30102** – Puls și SpO₂
- **MLX90614** – Temperatură fără contact
- **MCP3008 + AD8232** – Semnal ECG analogic
- **PostgreSQL** – Salvare date într-o bază de date în cloud (Neon DB)

---

## 📁 Fișiere

- `app_v3.py` – Script principal care colectează datele de la senzori și le salvează în baza de date.
- `heartrate_monitor.py` – Clasă Python pentru interacțiunea cu senzorul MAX30102.
- `app_v3.sh` – Script shell care rulează aplicația.
- `README.md` – Documentația proiectului.

---

## 🛠️ Cerințe

### Hardware

- Raspberry Pi Zero 2 W
- Senzor MAX30102
- Senzor MLX90614
- Senzor ECG AD8232 conectat la MCP3008
- Conexiune I2C, SPI, GPIO

### Software

- Python 3.x
- Pachete Python:
  - `psycopg2`
  - `adafruit-circuitpython-max30102`
  - `adafruit-circuitpython-mlx90614`
  - `adafruit-circuitpython-mcp3xxx`
  - `board`, `busio`, `digitalio`

Instalare (exemplu):

--- bash
pip3 install adafruit-circuitpython-mcp3xxx adafruit-circuitpython-mlx90614 psycopg2


---

## 🧠 Structură Bază de Date

Tabelul `patient_profiles`:

--- sql
CREATE TABLE patient_profiles (
    id SERIAL PRIMARY KEY
);

Tabelul `parameters`:

--- sql
CREATE TABLE parameters (
    id SERIAL PRIMARY KEY,
    patient_profile_id INT REFERENCES patient_profiles(id),
    ecg FLOAT,
    temperature FLOAT,
    pulse FLOAT,
    spo2 FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


---

## ⚙️ Configurare și Rulare

### 1. Adaugă în `~/.bashrc` sau `~/.zshrc`:

```bash
alias startApp="/cale/catre/app_v3.sh"
```

### 2. Fă scriptul executabil:

--- bash
chmod +x app_v3.sh
--- 

### 3. Rulează aplicația:

--- bash
startApp 15
--- 

sau fără argument (default: 10 secunde):

--- bash
startApp

---
## 📤 Trimiterea datelor

Datele sunt trimise la fiecare secundă către baza de date Neon, în tabela `parameters`, cu valorile:

- ECG (V)
- Temperatura (°C)
- Puls (bpm)
- SpO₂ (%)

---

## 📌 Note

- Datele de autentificare pentru Neon DB sunt stocate în `DB_URL`.
- Dacă pacientul cu `PATIENT_ID` nu există, este creat automat.
- Senzorul MAX30102 este rulat pe un thread separat pentru a nu bloca colectarea datelor ECG și temperatură.
- Logging-ul este activat și salvează în fișier `app.log`.

---

## 🧪 Exemplu de rulare

--- bash
$ startApp 10
Pornesc aplicația pentru o durată de 10 secunde...
Incepem colectarea datelor timp de 10 secunde...
ECG: 1.700 V | Temp: 33.95 °C | Pulse: 85 bpm | SpO₂: 97%
...
Datele au fost salvate cu succes.

---

## 📅 Autor

** Bogdan Alb & Liviu Barla ** – 
Proiect IoT / Senzori / Cloud Integration (Neon DB)

---
# HealthGuardian
# Raspberry
# Raspberry
