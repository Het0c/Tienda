import hashlib
from backend.db.conexion import conectar_db


def hashear_contraseña(contraseña):
    hash_obj = hashlib.sha256(contraseña.encode('utf-8'))
    return hash_obj.hexdigest()

def registrar_contraseña(rut_empleado, contraseña):
    conn = conectar_db()
    cursor = conn.cursor()

    hash_pswd = hashear_contraseña(contraseña)

    cursor.execute("""
        UPDATE empleado
        SET pass = ?
        WHERE rut = ?
    """, (hash_pswd, rut_empleado))

    conn.commit()
    conn.close()

def verificar_contraseña(rut_empleado, contraseña):
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("SELECT pass FROM empleado WHERE rut = ?", (rut_empleado,))
    resultado = cursor.fetchone()

    if resultado is None:
        return False  # El empleado no existe

    hash_almacenado = resultado[0]
    hash_ingresado = hashear_contraseña(contraseña)

    return hash_almacenado == hash_ingresado

def verificacion_admin(rut_empleado):
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("SELECT idTipoEmpleado FROM empleado WHERE rut = ?", (rut_empleado,))
    resultado = cursor.fetchone()

    if resultado and resultado[0] == 1 or resultado and resultado[0] == 3:  # Suponiendo que el tipo de empleado 1 es admin
        return True
    return False


class Sesion:
    def __init__(self):
        self.usuario = None
        self.es_admin = False

    def iniciar_sesion(self, usuario, es_admin=False):
        self.usuario = usuario
        self.es_admin = es_admin

    def cerrar_sesion(self): #falta crear cerrado de sesion, arqueo, etc
        self.usuario = None
        self.es_admin = False

    def esta_autenticado(self):
        return self.usuario is not None
