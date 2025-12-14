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
