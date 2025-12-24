from conexion import conectar_db

def crear_tablas():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS tipoEmpleado (
        idTipoEmpleado INTEGER PRIMARY KEY,
        nombreTipo TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS empleado (
        rut TEXT PRIMARY KEY,
        nombre TEXT NOT NULL,
        idTipoEmpleado INTEGER NOT NULL,
        FOREIGN KEY (idTipoEmpleado) REFERENCES tipoEmpleado(idTipoEmpleado)
    );

    CREATE TABLE IF NOT EXISTS turnoCaja (
        idTurno INTEGER PRIMARY KEY,
        fecha TEXT NOT NULL,
        horaInicio TEXT NOT NULL,
        horaFin TEXT NOT NULL,
        rutEmpleado TEXT NOT NULL,
        FOREIGN KEY (rutEmpleado) REFERENCES empleado(rut)
    );

    CREATE TABLE IF NOT EXISTS relevo (
        idRelevo INTEGER PRIMARY KEY,
        idTurno INTEGER NOT NULL,
        rutRelevo TEXT NOT NULL,
        motivo TEXT,
        horaInicio TEXT NOT NULL,
        horaFin TEXT NOT NULL,
        FOREIGN KEY (idTurno) REFERENCES turnoCaja(idTurno),
        FOREIGN KEY (rutRelevo) REFERENCES empleado(rut)
    );

    -- Aquí seguirían las demás tablas: familiaRopa, seccionRopa, rangoPrecio, boleta, detalleBoleta, etc.
    """)

    conn.commit()
    conn.close()
import sqlite3

def poblar_seccion_ropa_oferta():
    conn = sqlite3.connect("reuso_tienda.db")  # Ajusta si usas otra ruta
    cursor = conn.cursor()

    try:
        # Obtener datos desde la tabla madre
        cursor.execute("SELECT idSeccionRopa, stock FROM seccionRopa")
        datos = cursor.fetchall()

        # Insertar en la tabla hija
        for id_seccion, stock in datos:
            cursor.execute("""
                INSERT INTO seccionRopaOferta (idSeccionRopa, stock)
                VALUES (?, ?)
            """, (id_seccion, stock))

        conn.commit()
        print(f"Se insertaron {len(datos)} registros en seccionRopaOferta.")

    except Exception as e:
        print("Error al poblar tabla hija:", e)

    finally:
        conn.close()


poblar_seccion_ropa_oferta()