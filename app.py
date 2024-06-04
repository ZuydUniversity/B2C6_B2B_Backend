from flask import Flask, jsonify
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS

# Initialiseer de Flask applicatie
app = Flask(__name__)
CORS(app)  # Sta cross-origin requests toe

# Configuratie voor de MySQL-databaseverbinding
db_config = {
    'user': 'root',
    'password': 'Pipodeclown123',  # Wijzig dit naar het wachtwoord van je MySQL-database
    'host': 'localhost',
    'database': 'jbd2'  # Wijzig dit naar de naam van je MySQL-database
}

# Route voor de startpagina
@app.route('/')
def index():
    return "Welkom bij mijn applicatie!"

# Route om alle resultaten op te halen
@app.route('/api/results', methods=['GET'])
def get_results():
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

# Route om een specifiek resultaat op te halen op basis van ID
@app.route('/api/results/<int:result_id>', methods=['GET'])
def get_result_by_id(result_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM results WHERE id = %s", (result_id,))
        result = cursor.fetchone()
        cursor.close()
        
        if not result:
            conn.close()
            return jsonify({"error": "Result not found"}), 404
        
        # Initialiseer de responsstructuur
        response = {
            "id": result["id"],
            "name": result["name"],
            "type": result["type"],
            "date": result["date"].strftime('%Y-%m-%d %H:%M:%S'),
            "details": {},
            "blood_chemistry": []
        }

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
        return jsonify({"error": str(e)}), 500

# Route om alle patiënten op te halen
@app.route('/api/patients', methods=['GET'])
def get_patients():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM patient")
        patients = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(patients)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# Route om een specifieke patiënt op te halen op basis van ID
@app.route('/api/patients/<int:patient_id>', methods=['GET'])
def get_patient_by_id(patient_id):
    try:
        print(f"Fetching patient with ID: {patient_id}")
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM patient WHERE PatientId = %s", (patient_id,))
        patient = cursor.fetchone()
        cursor.close()
        
        if not patient:
            print("Patient not found")
            conn.close()
            return jsonify({"error": "Patient not found"}), 404
        
        # Print de sleutels van het resultaat om te debuggen
        print("Patient keys:", patient.keys())

        response = {
            "PatientId": patient["PatientId"],
            "PatientVoornaam": patient["PatientVoornaam"],
            "PatientAchternaam": patient["PatientAchternaam"],
            "PatientGeboortedatum": patient["PatientGeboortedatum"].strftime('%Y-%m-%d'),
            "PatientGeslacht": patient["PatientGeslacht"],
            "PatientDiagnose": patient["PatientDiagnose"],
            "PatientContactpersoon": patient["PatientContactpersoon"],
            "PatientContactpersoontelefoonnummer": patient["PatientContactpersoontelefoonnummer"]  # Voeg de ontbrekende kolom toe
        }
        
        conn.close()
        return jsonify(response)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# Start de Flask server
if __name__ == '__main__':
    app.run(port=5000)
