from backend.db.conexion import conectar_db

def consultar_arqueo_fecha(fecha):
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT subtotal_ventas, total_efectivo, gastos_dia
        FROM arqueo_diario
        WHERE fecha = ?
    """, (fecha,))

    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        subtotal_ventas, total_efectivo, gastos_dia = resultado
        return {
            "Subtotal Ventas": subtotal_ventas,
            "Total Efectivo": total_efectivo,
            "Gastos del Día": gastos_dia
        }
    else:
        return None
    
def registrar_arqueo(fecha, subtotal_ventas, total_efectivo, gastos_dia):
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO arqueo_diario (fecha, subtotal_ventas, total_efectivo, gastos_dia)
        VALUES (?, ?, ?, ?)
    """, (fecha, subtotal_ventas, total_efectivo, gastos_dia))

    conn.commit()
    conn.close()

def cerrar_caja(fecha):
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE arqueo_diario
        SET cerrado = 1
        WHERE fecha = ?
    """, (fecha,))

    conn.commit()
    conn.close()