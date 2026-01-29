from backend.db.conexion import conectar_db

def consultar_inventario_ropa(search):
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM prenda
        WHERE LOWER(nombre) LIKE LOWER(?)
    """, ('%' + search + '%',))

    resultados = cursor.fetchall()
    conn.close()

    inventario = []
    for fila in resultados:
        id, prenda,tipo, marca, precio, total = fila
        inventario.append({
            "id": id,
            "Prenda": prenda,
            "tipo": tipo,
            "Marca": marca,
            "Precio": precio,
            "Total Stock": total
        })
    return inventario


def obtener_producto_por_codigo(codigo_barra):
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""SELECT nombre ,precio  FROM prenda
    WHERE id_prenda = ?""", (codigo_barra,))
    prenda = cursor.fetchone()

    conn.close()
    return prenda  # devuelve (nombre, cantidad, precio) o None si no existe




