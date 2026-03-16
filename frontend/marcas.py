import sqlite3

DB_PATH = "reuso.db"



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
    """Actualiza el nombre de una marca."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE marcas SET nombre = ? WHERE nombre = ?",
            (nuevo_nombre, nombre_actual),
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # Nombre duplicado
    except Exception as e:
        print(f"Error editando marca: {e}")
        return False


def eliminar_marca(nombre):
    """Elimina una marca por su nombre."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM marcas WHERE nombre = ?", (nombre,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error eliminando marca: {e}")
        return False
