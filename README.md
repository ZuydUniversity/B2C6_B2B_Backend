# B2C6_Backend B2B
Studenten repository voor Backend voor het vak B2C6 DevOps. De backend wordt gemaakt in Python. Elke klas heeft 1 repository voor Backend.

Note van Hartie
Voor de SQL nieuwe tabellen aanmaken:
Een nieuwe querry maken en dan deze code erin plakken

CREATE TABLE notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patient(id)
);

CREATE TABLE images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    file_path VARCHAR(255),
    description TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patient(id)
);



