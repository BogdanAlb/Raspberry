from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configurarea conexiunii la baza de date PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://neondb_owner:npg_L3fiTW6qKSDw@ep-icy-dawn-a4kubr5f.us-east-1.aws.neon.tech/neondb?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Definirea modelului bazei de date
class Temperature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ambient_temp = db.Column(db.Float, nullable=False)
    target_temp = db.Column(db.Float, nullable=False)

# Endpoint pentru primirea datelor
@app.route('/api/temperature', methods=['POST'])
def receive_temperature():
    data = request.json
    new_entry = Temperature(
        ambient_temp=data['ambient'],
        target_temp=data['target']
    )
    db.session.add(new_entry)
    db.session.commit()
    return jsonify({'message': 'Data inserted successfully'}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
