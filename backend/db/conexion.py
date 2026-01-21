import sqlite3
import os

connection = sqlite3.connect('reuso.db')
cursor = connection.cursor()
if connection:
    print("Conexión exitosa a la base de datos SQLite.")
else:
    print("Error al conectar a la base de datos SQLite.")

# mostrar datos de la tabla empleado
# cursor.execute("SELECT * FROM empleado")
# rows = cursor.fetchall()
# for row in rows:
#     print(row)



def conectar_db():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "..", "..", "reuso.db")  # Ajusta según tu estructura
    print("Conectando a:", os.path.abspath(db_path))  # Para depurar
    return sqlite3.connect(db_path)


import mysql.connector

def obtener_rut_usuario(usuario):
    """
    Consulta la base de datos MySQL y devuelve el RUT del usuario.
    
    :param usuario: nombre de usuario (string)
    :return: rut (string) o None si no existe
    """
    try:
        # Conexión a la base de datos
        conn = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="nuevo_usuario",
        password="tuclave",
        database="tienda_online"
        )
        cursor = conn.cursor()

        # Consulta: suponemos que tu tabla se llama 'usuarios'
        query = "SELECT rut, digito_ver, nombre, id_rol, password FROM tienda_online.usuario WHERE rut = %s"
        cursor.execute(query, (usuario,))

        resultado = cursor.fetchone()

        cursor.close()
        conn.close()

        if resultado:
            return resultado[0]  # El RUT
        else:
            return None
    except mysql.connector.Error as err:
        print(f"Error al consultar la base de datos: {err}")
        return None


def conectar_mydb():
    """
    Consulta la base de datos MySQL y devuelve el RUT del usuario.
    
    :param usuario: nombre de usuario (string)
    :return: rut (string) o None si no existe
    """
    return mysql.connector.connect(
        # Conexión a la base de datos

        host="localhost",
        port=3306,
        user="nuevo_usuario",
        password="tuclave",
        database="tienda_online"
        ,
        autocommit=True
        )
