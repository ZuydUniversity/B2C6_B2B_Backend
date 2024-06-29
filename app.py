from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
CORS(app)  # Sta cross-origin requests toe
bcrypt = Bcrypt(app)

# Configuratie voor de MySQL-databaseverbinding
db_config = {
    'user': 'admin',
    'password': 'geheim',  # Wijzig dit naar het wachtwoord van je MySQL-database
    'host': 'localhost',
    'database': 'casusdb'  # Wijzig dit naar de naam van je MySQL-database
}

@app.route('/api/patients', methods=['GET'])
def get_patients():
    """Haalt patienten op uit database"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, first_name, last_name, birth_date, gender FROM patient")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(results)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/results', methods=['GET'])
def get_results():
    """Haalt alle resultaten op uit de database"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM results")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(results)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/results/<int:result_id>', methods=['GET'])
def get_result_by_id(result_id):
    """Haalt een specifiek resultaat op uit de database op basis van ID"""
    try:
        conn = mysql.connector.connect(**db_config)
        
        # Gebruik een aparte cursor voor elke query
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM results WHERE id = %s", (result_id,))
        result = cursor.fetchone()
        cursor.close()
        
        if not result:
            conn.close()
            return jsonify({"error": "Result not found"}), 404
        
        # Initialiseert de responsstructuur
        response = {
            "id": result["id"],
            "type": result["type"],
            "date": result["date"].strftime('%Y-%m-%d %H:%M:%S'),  # Formatteert datetime naar string
            "details": {},
            "blood_chemistry": []
        }

        # Haalt details op gebaseerd op het result type
        if result['type'] == 'Radiologie':
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM radiology_results WHERE result_id = %s", (result_id,))
            radiology_details = cursor.fetchone()
            cursor.close()
            if radiology_details:
                response["details"] = {
                    "aspect": radiology_details["aspect"],
                    "type": radiology_details["type"],
                    "comments": radiology_details["comments"],
                    "image": radiology_details["image"]
                }
        elif result['type'] == 'Myometrie':
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM myometry_results WHERE result_id = %s", (result_id,))
            myometry_details = cursor.fetchall()
            cursor.close()
            if myometry_details:
                response["details"] = [{
                    "aspect": detail["aspect"],
                    "type": detail["type"],
                    "score": detail["score"],
                    "average_score": detail["average_score"]
                } for detail in myometry_details]
        else:
            conn.close()
            return jsonify({"error": "Unknown result type"}), 400

        # Haalt bloedchemie resultaten op
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM blood_chemistry_results WHERE result_id = %s", (result_id,))
        blood_chemistry_results = cursor.fetchall()
        cursor.close()
        for blood_chemistry in blood_chemistry_results:
            response["blood_chemistry"].append({
                "parameter": blood_chemistry["parameter"],
                "value": blood_chemistry["value"],
                "unit": blood_chemistry["unit"],
                "reference_range": blood_chemistry["reference_range"]
            })
        
        conn.close()
        return jsonify(response)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 50
    
@app.route('/login', methods=['POST'])
def login():
    """controleerd inloggegevens met database gegevens"""
    data = request.get_json()
    email = data['email']
    password = data['password']
    employeeNumber = data['employeeNumber']

    conn = mysql.connector.connect(**db_config)
    if conn is None:
        return jsonify({'message': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s AND employeeNumber = %s", (email, employeeNumber))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and bcrypt.check_password_hash(user[3], password):
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'message': 'Invalid email, employeeNumber, or password'}), 401
    except Error as e:
        print(f"Error during query execution: {e}")
        return jsonify({'message': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(port=5000)  # Start de Flask server op poort 5000
