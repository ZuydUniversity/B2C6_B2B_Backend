from flask import Flask, jsonify
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Sta cross-origin requests toe

# Configuratie voor de MySQL-databaseverbinding
db_config = {
    'user': 'root',
    'password': 'Kanker123!',  # Wijzig dit naar het wachtwoord van je MySQL-database
    'host': 'localhost',
    'database': 'jdb'  # Wijzig dit naar de naam van je MySQL-database
}

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
            "name": result["name"],
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
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)  # Start de Flask server op poort 5000
