import sqlite3
import barcode
from barcode.writer import ImageWriter
import random
import string
import os

# Conexión a la base
conn = sqlite3.connect("reuso.db")
cursor = conn.cursor()

# Crear carpeta si no existe
os.makedirs("barcodes", exist_ok=True)

# Verificar si la columna ya existe
try:
    cursor.execute("ALTER TABLE rangoPrecio ADD COLUMN codigoBarra TEXT")
except sqlite3.OperationalError:
    pass  # Ya existe

# Obtener registros
cursor.execute("SELECT idRangoPrecio FROM rangoPrecio")
registros = cursor.fetchall()

# Generar y asignar código aleatorio
def generar_codigo_barra():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

for (idRango,) in registros:
    codigo = generar_codigo_barra()

    # Generar imagen del código
    code128 = barcode.get('code128', codigo, writer=ImageWriter())
    code128.save(f"barcodes/{codigo}")

    # Actualizar en la base
    cursor.execute("""
        UPDATE rangoPrecio SET codigoBarra = ? WHERE idRangoPrecio = ?
    """, (codigo, idRango))

conn.commit()
conn.close()
