import sqlite3

DB_PATH = "reuso.db"



def sincronizar_productos(cursor):
    """Sincroniza los productos del sistema antiguo a la nueva tabla."""
    try:
        # Verificar si existe la tabla antigua 'rangoPrecio' para evitar errores
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='rangoPrecio'"
        )
        if not cursor.fetchone():
            return

        # Migrar datos: codigo, nombre (construido), precio
        # Se asume 'Generica' como marca y stock 0 si no está en la nueva tabla.
        # INSERT OR IGNORE evita duplicados si el código ya existe.
        cursor.execute(
            """
            INSERT OR IGNORE INTO productos (codigo, nombre, precio, marca, stock)
            SELECT 
                r.codigoBarra,
                s.nombreSeccionRopa || ' de ' || f.nombreFamilia,
                r.precio,
                'Generica',
                0
            FROM rangoPrecio r
            JOIN seccionropa s ON r.idSeccionRopa = s.idSeccionRopa
            JOIN familiaRopa f ON s.idFamiliaRopa = f.idFamiliaRopa
            WHERE r.codigoBarra IS NOT NULL AND r.codigoBarra != ''
        """
        )
    except Exception as e:
        print(f"Error sincronizando productos: {e}")


def obtener_marcas():
    """Retorna una lista de nombres de marcas ordenadas alfabéticamente."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM marcas ORDER BY nombre ASC")
    marcas = [row[0] for row in cursor.fetchall()]
    conn.close()
    return marcas


def agregar_nueva_marca(nombre):
    """Inserta una nueva marca. Retorna True si éxito, False si ya existe o error."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO marcas (nombre) VALUES (?)", (nombre,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"Error agregando marca: {e}")
        return False


def editar_marca(nombre_actual, nuevo_nombre):
    """Edita el nombre de una marca existente."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE marcas SET nombre = ? WHERE nombre = ?",
            (nuevo_nombre, nombre_actual),
        )
        cursor.execute(
            "UPDATE productos SET marca = ? WHERE marca = ?",
            (nuevo_nombre, nombre_actual),
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"Error editando marca: {e}")
        return False


def eliminar_marca(nombre, eliminar_productos=False):
    """Elimina una marca por su nombre. Opcionalmente elimina sus productos."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        if eliminar_productos:
            cursor.execute("DELETE FROM productos WHERE marca = ?", (nombre,))
            accion = "Eliminación Completa"
            detalle = f"Se eliminó la marca '{nombre}' y todos sus productos."
        else:
            accion = "Eliminación Marca"
            detalle = f"Se eliminó la marca '{nombre}' (productos conservados)."

        cursor.execute(
            "INSERT INTO auditoria_marcas (accion, detalle) VALUES (?, ?)",
            (accion, detalle),
        )

        cursor.execute("DELETE FROM marcas WHERE nombre = ?", (nombre,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error eliminando marca: {e}")
        return False


def obtener_historial_auditoria():
    """Retorna el historial de eliminaciones."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT fecha, accion, detalle FROM auditoria_marcas ORDER BY id DESC"
        )
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error historial: {e}")
        return []
