#!/bin/bash

# Script de pornire pentru app_v4.py
# Folosire: ./app_v4.sh [durata in secunde]

# Verificam daca scriptul Python exista
if [ ! -f "app_v4.py" ]; then
 echo "Eroare: fisierul app_v4.py nu a fost gasit!"
 exit 1
fi

# Durata implicita 10 secunde
DURATA=${1:-10}

echo "Pornesc aplicatia pentru o durata de $DURATA secunde..."
python3 app_v4.py -t "$DURATA"
