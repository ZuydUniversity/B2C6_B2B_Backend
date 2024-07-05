from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
CORS(app)  # Sta cross-origin requests toe
bcrypt = Bcrypt(app)

# Configuratie voor de MySQL-databaseverbinding
db_config = {
    'user': 'admin',
    'password': 'geheim',  # Wijzig dit naar het wachtwoord van je MySQL-database
    'host': '20.73.242.86',
    'port': 3306,
    'database': 'casusdb'  # Wijzig dit naar de naam van je MySQL-database
}

def get_db_connection():
    """Functie om een nieuwe databaseverbinding te krijgen"""
    conn = mysql.connector.connect(**db_config)
    return conn

@app.route('/api/patients', methods=['GET'])
def get_patients():
    """Haalt patienten op uit database"""
    try:
        conn = get_db_connection()
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
        conn = get_db_connection()
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
        conn = get_db_connection()
        
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
    
@app.route('/login', methods=['POST'])
def login():
    """Controleert inloggegevens met databasegegevens"""
    data = request.get_json()
    email = data['email']
    wachtwoord = data['wachtwoord']
    personeelsnummer = data['personeelsnummer']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s AND personeelsnummer = %s", (email, personeelsnummer))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and bcrypt.check_password_hash(user[3], wachtwoord):
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'message': 'Invalid email, personeelsnummer, or password'}), 401
    except Error as e:
        print(f"Error during query execution: {e}")
        return jsonify({'message': 'Internal server error'}), 500

# Vanaf hier start de CRUD voor Notities
@app.route('/api/notes', methods=['POST'])
def create_note():
    """Maak een nieuwe notitie aan"""
    data = request.get_json()
    patient_id = data['patient_id']
    content = data['content']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notes (patient_id, content) VALUES (%s, %s)", (patient_id, content))
        conn.commit()
        note_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({"id": note_id, "patient_id": patient_id, "content": content}), 201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/notes', methods=['GET'])
def get_notes():
    """Haalt alle notities op"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM notes")
        notes = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(notes)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/notes/<int:note_id>', methods=['GET'])
def get_note_by_id(note_id):
    """Haalt een specifieke notitie op"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM notes WHERE id = %s", (note_id,))
        note = cursor.fetchone()
        cursor.close()
        conn.close()
        if not note:
            return jsonify({"error": "Note not found"}), 404
        return jsonify(note)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Update een bestaande notitie"""
    data = request.get_json()
    content = data['content']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE notes SET content = %s WHERE id = %s", (content, note_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"id": note_id, "content": content}), 200
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Verwijder een notitie"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id = %s", (note_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return '', 204
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# Vanaf hier CRUD code voor Afbeeldingen
@app.route('/api/images', methods=['POST'])
def create_image():
    """Upload een nieuwe afbeelding"""
    data = request.get_json()
    patient_id = data['patient_id']
    file_path = data['file_path']  # Dit moet de bestandslocatie zijn waar je de afbeelding opslaat
    description = data['description']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO images (patient_id, file_path, description) VALUES (%s, %s, %s)", (patient_id, file_path, description))
        conn.commit()
        image_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({"id": image_id, "patient_id": patient_id, "file_path": file_path, "description": description}), 201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/images', methods=['GET'])
def get_images():
    """Haalt alle afbeeldingen op"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM images")
        images = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(images)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/images/<int:image_id>', methods=['GET'])
def get_image_by_id(image_id):
    """Haalt een specifieke afbeelding op"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM images WHERE id = %s", (image_id,))
        image = cursor.fetchone()
        cursor.close()
        conn.close()
        if not image:
            return jsonify({"error": "Image not found"}), 404
        return jsonify(image)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/images/<int:image_id>', methods=['PUT'])
def update_image(image_id):
    """Update een bestaande afbeelding"""
    data = request.get_json()
    description = data['description']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE images SET description = %s WHERE id = %s", (description, image_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"id": image_id, "description": description}), 200
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/images/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    """Verwijder een afbeelding"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM images WHERE id = %s", (image_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return '', 204
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
