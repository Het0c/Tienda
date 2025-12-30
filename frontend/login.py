from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
    QShortcut,
)
from PyQt5.QtGui import QPixmap, QKeySequence
from PyQt5.QtCore import Qt, QTimer
from backend.logica.user import verificar_contraseña, verificacion_admin, Sesion

debug = True  # Mantener global, pero no crea widgets


class LoginWindow(QWidget):

    def __init__(self, on_login_success):
        super().__init__()

        # Crear Sesion solo cuando se instancia la ventana
        self.ss = Sesion()

        self.es_admin = False
        self.on_login_success = on_login_success

        self.setWindowTitle("Inicio de Sesión")
        self.setMinimumSize(800, 600)

        # Ventana toplevel
        self.setWindowFlags(self.windowFlags() | Qt.Window)

        # ---------- FONDO ----------
        self.fondo = QLabel(self)
        self.fondo.setPixmap(QPixmap("frontend/assets/logo_login5.png"))
        self.fondo.setScaledContents(True)
        self.fondo.setGeometry(0, 0, self.width(), self.height())
        self.resizeEvent = lambda event: self.fondo.setGeometry(
            0, 0, self.width(), self.height()
        )

        # ---------- LAYOUT ----------
        layout_principal = QVBoxLayout(self)
        layout_principal.setAlignment(Qt.AlignCenter)

        contenedor = QVBoxLayout()
        contenedor.setAlignment(Qt.AlignCenter)

        titulo = QLabel("🔐 Iniciar sesión")
        titulo.setStyleSheet(
            """
            color: white;
            background-color: rgba(0, 0, 0, 0.5);
            font-size: 21px;
            font-weight: bold;
        """
        )

        # Usuario
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Usuario")
        self.user_input.setFixedWidth(350)
        self.user_input.setStyleSheet(
            """
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.85);
                border: 1px solid #BDBDBD;
                padding: 8px;
                font-size: 20px;
                border-radius: 4px;
            }
        """
        )

        # Contraseña
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Contraseña")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setFixedWidth(350)
        self.pass_input.setStyleSheet(
            """
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.85);
                border: 1px solid #BDBDBD;
                padding: 8px;
                font-size: 14px;
                border-radius: 4px;
            }
        """
        )

        # Botón ingresar
        self.login_btn = QPushButton("Ingresar")
        self.login_btn.setFixedWidth(350)
        self.login_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #2F80ED;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1E70D7;
            }
        """
        )
        self.login_btn.clicked.connect(self.validar_login)

        # Atajos ENTER
        QShortcut(QKeySequence(Qt.Key_Return), self).activated.connect(
            self.validar_login
        )
        QShortcut(QKeySequence(Qt.Key_Enter), self).activated.connect(
            self.validar_login
        )

        contenedor.addWidget(titulo)
        contenedor.addSpacing(10)
        contenedor.addWidget(self.user_input)
        contenedor.addWidget(self.pass_input)
        contenedor.addWidget(self.login_btn)

        layout_principal.addLayout(contenedor)

        # Forzar maximizado correctamente
        QTimer.singleShot(5, self._mostrar_maximizado_correcto)

    # ---------------------------------------------------------
    def _mostrar_maximizado_correcto(self):
        self.show()  # asegurar que la ventana existe
        self.setWindowState(Qt.WindowNoState)
        self.showNormal()
        QTimer.singleShot(25, lambda: self.setWindowState(Qt.WindowMaximized))
        self.raise_()
        self.activateWindow()
        QTimer.singleShot(60, lambda: self.user_input.setFocus())

    # ---------------------------------------------------------
    def validar_login(self):
        usr = self.user_input.text().strip()
        psswd = self.pass_input.text().strip()

        if not usr or not psswd:

                QMessageBox.warning(
                    self, "Campos incompletos", "Por favor completa todos los campos."
                )
                return
        from backend.logica.user import verificar_contraseña, verificacion_admin
        from backend.db.conexion import obtener_rut_usuario
        if verificar_contraseña(usr, psswd):
            rut = obtener_rut_usuario(usr)   # función que consulta la BD
            self.ss.iniciar_sesion(usr, rut)
            self.on_login_success(self.ss)
            self.close()

        else:
            QMessageBox.critical(
                self, "Campos incorrectos", "Usuario o contraseña incorrectos."
            )
