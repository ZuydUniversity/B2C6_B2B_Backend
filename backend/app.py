from flask import Flask, jsonify
from flask_cors import CORS
from flask_mysqldb import MySQL

app = Flask(__name__)
CORS(app)

# MySQL configurations
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Haha123'
app.config['MYSQL_DB'] = 'casusdb'

mysql = MySQL(app)

@app.route('/patients', methods=['GET'])
def get_patients():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, voornaam, achternaam, geboortedatum, geslacht, diagnose FROM patient")
    patient = cur.fetchall()
    cur.close()

    return jsonify([
        {"id": row[0], "voornaam": row[1], "achternaam": row[2], "geboortedatum": row[3], "geslacht": row[4], "diagnose": row[5]}
        for row in patient
    ])

if __name__ == '__main__':
    app.run(debug=True)

