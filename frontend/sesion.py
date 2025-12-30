class Sesion:
    def __init__(self):
        self.usuario = None   # nombre de usuario
        self.rut = None       # rut del empleado
        self.es_admin = False
        self.activa = False

    def iniciar_sesion(self, usuario, es_admin, rut=None):
        self.usuario = usuario
        self.es_admin = es_admin
        self.rut = rut
        self.activa = True

    def cerrar_sesion(self):
        self.usuario = None
        self.rut = None
        self.es_admin = False
        self.activa = False
