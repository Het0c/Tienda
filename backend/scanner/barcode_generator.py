

import sqlite3
import random

# Conexión a la base
conn = sqlite3.connect("reuso.db")
cursor = conn.cursor()


cursor.execute("""
SELECT r.idRangoPrecio,
       upper(substr(s.nombreSeccionRopa,1,1)) ||
       upper(substr(s.nombreSeccionRopa,length(s.nombreSeccionRopa),1)) ||
       "-" ||
       upper(substr(f.nombreFamilia,1,1)) ||
       "-" ||
       r.idRangoPrecio ||
       "-" AS prefijo
FROM seccionropa s
INNER JOIN familiaRopa f ON f.idFamiliaRopa = s.idFamiliaRopa
INNER JOIN rangoPrecio r ON s.idSeccionRopa = r.idSeccionRopa
""")

registros = cursor.fetchall()

for idRangoPrecio, prefijo in registros:
    numero = f"{random.randint(0, 9999):04d}"
    codigo = prefijo + numero


    cursor.execute("""
    UPDATE rangoPrecio
    SET codigoBarra = ?
    WHERE idRangoPrecio = ?
    """, (codigo, idRangoPrecio))

    print(f"Actualizado idRangoPrecio {idRangoPrecio} -> {codigo}")

conn.commit()
conn.close()
