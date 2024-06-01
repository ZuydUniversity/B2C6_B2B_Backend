from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # replace with your root password
app.config['MYSQL_DATABASE'] = 'DevOpsDB'

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DATABASE']
        )
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    wachtwoord = data['wachtwoord']
    personeelsnummer = data['personeelsnummer']

    conn = get_db_connection()
    if conn is None:
        return jsonify({'message': 'Database connection failed'}), 500

    try:
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

if __name__ == '__main__':
    app.run(debug=True)
