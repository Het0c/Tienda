import fdb
import sqlite3
import mysql.connector
from decimal import Decimal


# -------------------------
# Utilidad: convertir Decimal
# -------------------------
def convertir_fila(row):
    nueva = []

    for v in row:
        if isinstance(v, Decimal):
            nueva.append(float(v))
        else:
            nueva.append(v)

    return tuple(nueva)


# -------------------------
# CONSULTAS
# -------------------------

# Firebird
SELECT_CLIENTE = """
SELECT 
folio,
cantidad,
fd.PRECIO,
fd.TOTAL,
detalle,
fd.CODIGOPRIN 
FROM FACV_DET fd 
"""

# Inserts
INSERT_SQLITE = """
insert into 
  "detalleBoleta" (
    "idBoleta", 
    cantidad, 
    "precioUnitario", 
    "totalItem", 
    detalle, 
    "codigoProducto"
  )

VALUES (?, ?, ?, ?, ?, ?)
"""

INSERT_MYSQL = """
INSERT INTO cliente
(rut, digito_ver, nombre, celular, direccion, actividad_economica, descripcion,fono)
VALUES (%s, %s, %s, %s, %s, %s, %s,%s)
"""


# -------------------------
# MENÚ
# -------------------------

print("=== Migración Firebird ===")
print("1) Migrar a SQLite")
print("2) Migrar a MySQL")

opcion = input("Elige destino (1/2): ").strip()

if opcion not in ["1", "2"]:
    print("❌ Opción inválida")
    exit()


# -------------------------
# Firebird
# -------------------------

fb = fdb.connect(
    host="localhost",
    port=3050,
    database="/data/DATOS001.gdb",
    user="SYSDBA",
    password="masterkey"
)

fb_cur = fb.cursor()
fb_cur.execute(SELECT_CLIENTE)


# -------------------------
# Destino
# -------------------------

if opcion == "1":

    print("➡️ Migrando a SQLite...")

    db = sqlite3.connect("reuso.db")
    cur = db.cursor()

    insert_sql = INSERT_SQLITE


else:

    print("➡️ Migrando a MySQL...")

    db = mysql.connector.connect(
        host="localhost",
        user="nuevo_usuario",
        password="tuclave",
        database="tienda_online"
    )

    cur = db.cursor()

    insert_sql = INSERT_MYSQL


# -------------------------
# Migración
# -------------------------

contador = 0


for row in fb_cur:

    row2 = convertir_fila(row)

    # Limpiar strings
    row2 = tuple(
        x.strip() if isinstance(x, str) else x
        for x in row2
    )

    cur.execute(insert_sql, row2)

    contador += 1

    if contador % 100 == 0:
        print(f"  {contador} registros...")


db.commit()


# -------------------------
# Verificación
# -------------------------

cur.execute("SELECT COUNT(*) FROM boleta")
total = cur.fetchone()[0]

print("Total insertados:", total)


# -------------------------
# Cerrar
# -------------------------

fb.close()
db.close()

print("✅ Migración terminada")
