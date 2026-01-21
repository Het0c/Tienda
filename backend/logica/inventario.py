from backend.db.conexion import conectar_db

def consultar_inventario_ropa(search):
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM v_inventario
        WHERE LOWER(prenda) LIKE LOWER(?)
    """, ('%' + search + '%',))

    resultados = cursor.fetchall()
    conn.close()

    inventario = []
    for fila in resultados:
        prenda, piso1, piso2, total = fila
        inventario.append({
            "Prenda": prenda,
            "Primer piso": piso1,
            "Segundo Piso": piso2,
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




