import os
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Conexión a MySQL
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="tuclave",
        database="tienda_online"
    )

@app.route('/')
def index():
    return render_template('subir_factura.html')

@app.route('/subir_factura', methods=['POST'])
def subir_factura():
    if 'factura' not in request.files:
        return "No se seleccionó archivo"

    file = request.files['factura']
    if file.filename == '':
        return "Nombre de archivo vacío"

    # Guardar archivo en carpeta local
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # Guardar referencia en MySQL
    conn = get_connection()
    cursor = conn.cursor()
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO factura (imagen, fecha_subida) VALUES (%s, %s)", (file.filename, fecha))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
