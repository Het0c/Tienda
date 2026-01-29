import os
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for,session
from datetime import datetime
#from werkzeug.security import check_password_hash       

app = Flask(__name__)
app.secret_key = "clave_secreta"
UPLOAD_FOLDER = 'uploads'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Conexión a MySQL
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="nuevo_usuario",
        password="tuclave",
        database="tienda_online"
    )

@app.route('/')
def index():
    # Si el usuario ya está en sesión, mostrar index
    if "username" in session:
        return render_template("index.html", username=session["username"])
    # Si no, redirigir al login
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT RUT, PASSWORD FROM usuario WHERE RUT = %s", (username,))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()

        # Validación con hash
        if usuario and usuario["PASSWORD"] == password: #check_password_hash( , password):
            session["username"] = username
            return redirect(url_for("index"))
        else:
            return "Usuario o contraseña incorrectos"

    if "username" in session:
        return redirect(url_for("index"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)  # Eliminar sesión
    return redirect(url_for("login"))





@app.route('/roles', methods=['POST', 'GET'])
def roles():
    #obtener datos de usuarios y roles
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT rut, digito_ver, nombre, id_rol, password
        FROM usuario;
    """)
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('roles.html', usuarios=usuarios)
    


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

    return render_template('subir_factura.html')

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)

