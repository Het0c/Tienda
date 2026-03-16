from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QShortcut,
)
from PyQt5.QtGui import QPixmap, QKeySequence, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QPoint
from backend.logica.user import verificar_contraseña, verificacion_admin, Sesion
import os

debug = True  # Mantener global, pero no crea widgets


class LoadingButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._original_text = text
        self._is_loading = False
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)

    def start_loading(self):
        self._is_loading = True
        self.setText("")
        self.setEnabled(False)
        self._timer.start(25)
        self.update()

    def stop_loading(self):
        self._is_loading = False
        self.setText(self._original_text)
        self.setEnabled(True)
        self._timer.stop()
        self.update()

    def _rotate(self):
        self._angle = (self._angle + 15) % 360
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        if self._is_loading:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)

            w = self.width()
            h = self.height()

            painter.setPen(QPen(QColor("#2D3436"), 3))

            radius = 10
            rect_x = int(w / 2 - radius)
            rect_y = int(h / 2 - radius)

            painter.drawArc(
                rect_x, rect_y, radius * 2, radius * 2, -self._angle * 16, -270 * 16
            )


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
            font-size: 32px;
            font-weight: bold;
            padding: 10px;
            border-radius: 8px;
        """
        )

        # Usuario
        self.user_container = QWidget()
        self.user_container.setFixedWidth(420)
        user_layout = QHBoxLayout(self.user_container)
        user_layout.setContentsMargins(0, 0, 0, 0)
        user_layout.setSpacing(8)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Usuario")
        self.user_input.setStyleSheet(
            """
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.9);
                border: 1px solid #BDBDBD;
                padding: 12px;
                font-size: 18px;
                border-radius: 6px;
            }
        """
        )

        self.lbl_user_icon = QLabel("👤")
        self.lbl_user_icon.setFixedSize(50, 48)
        self.lbl_user_icon.setAlignment(Qt.AlignCenter)
        self.lbl_user_icon.setStyleSheet(
            """
            background-color: rgba(255, 255, 255, 0.9);
            border: 1px solid #BDBDBD;
            border-radius: 6px;
            font-size: 24px;
        """
        )

        user_layout.addWidget(self.user_input)
        user_layout.addWidget(self.lbl_user_icon)

        # Contraseña
        self.pass_container = QWidget()
        self.pass_container.setFixedWidth(420)
        pass_layout = QHBoxLayout(self.pass_container)
        pass_layout.setContentsMargins(0, 0, 0, 0)
        pass_layout.setSpacing(8)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Contraseña")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setStyleSheet(
            """
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.9);
                border: 1px solid #BDBDBD;
                padding: 12px;
                font-size: 18px;
                border-radius: 6px;
            }
        """
        )

        self.btn_ver_pass = QPushButton("👁")
        self.btn_ver_pass.setFixedSize(50, 48)
        self.btn_ver_pass.setCursor(Qt.PointingHandCursor)
        self.btn_ver_pass.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.9);
                border: 1px solid #BDBDBD;
                border-radius: 6px;
                font-size: 24px;
            }
            QPushButton:hover {
                background-color: #dfe6e9;
            }
        """
        )
        self.btn_ver_pass.clicked.connect(self.toggle_password)

        pass_layout.addWidget(self.pass_input)
        pass_layout.addWidget(self.btn_ver_pass)

        # Etiqueta de error (oculta por defecto)
        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet(
            "color: #FF5252; font-size: 16px; font-weight: bold; margin-top: 10px;"
        )
        self.lbl_error.setAlignment(Qt.AlignCenter)

        # Botón ingresar
        self.login_btn = LoadingButton("Ingresar")
        self.login_btn.setFixedWidth(420)
        self.login_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #F4D03F;
                color: #2D3436;
                border: none;
                padding: 15px;
                font-size: 20px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #D4AC0D;
            }
            QPushButton:disabled {
                background-color: #BDC3C7; /* Gris si está deshabilitado */
            }
        """
        )
        self.login_btn.clicked.connect(self.validar_login)

        # Conectar validación de campos
        self.user_input.textChanged.connect(self.verificar_campos)
        self.pass_input.textChanged.connect(self.verificar_campos)

        # Configuración de Enter: Usuario -> Contraseña -> Validar
        self.user_input.returnPressed.connect(self.pass_input.setFocus)
        self.pass_input.returnPressed.connect(self.validar_login)

        contenedor.addWidget(titulo)
        contenedor.addSpacing(20)
        contenedor.addWidget(self.user_container)
        contenedor.addWidget(self.pass_container)
        contenedor.addWidget(self.lbl_error)
        contenedor.addWidget(self.login_btn)

        layout_principal.addLayout(contenedor)

        # Forzar maximizado correctamente
        QTimer.singleShot(5, self._mostrar_maximizado_correcto)

        # Verificar estado inicial
        self.verificar_campos()

    # ---------------------------------------------------------
    def _mostrar_maximizado_correcto(self):
        self.show()  # asegurar que la ventana existe
        self.setWindowState(Qt.WindowNoState)
        self.showNormal()
        QTimer.singleShot(25, lambda: self.setWindowState(Qt.WindowMaximized))
        self.raise_()
        self.activateWindow()
        QTimer.singleShot(60, lambda: self.user_input.setFocus())

    def toggle_password(self):
        if self.pass_input.echoMode() == QLineEdit.Password:
            self.pass_input.setEchoMode(QLineEdit.Normal)
            self.btn_ver_pass.setText("🔒")
        else:
            self.pass_input.setEchoMode(QLineEdit.Password)
            self.btn_ver_pass.setText("👁")

    def verificar_campos(self):
        self.lbl_error.setText("")  # Limpiar error al escribir
        usr = self.user_input.text().strip()
        psswd = self.pass_input.text().strip()
        self.login_btn.setEnabled(bool(usr) and bool(psswd))

    # ---------------------------------------------------------
    def validar_login(self):
        # Si está cargando, ignorar
        if getattr(self.login_btn, "_is_loading", False):
            return

        usr = self.user_input.text().strip()
        psswd = self.pass_input.text().strip()

        if not usr or not psswd:
            if debug:
                self.ss.iniciar_sesion("demo", False)
                self.on_login_success(self.ss)
                self.close()
                QMessageBox.warning(
                    self, "Modo debug", "Solo presentado en la versión Demo."
                )
                return
            else:
                self.lbl_error.setText("Por favor completa todos los campos.")
                return

        # Iniciar animación y bloquear inputs
        self.login_btn.start_loading()
        self.user_input.setEnabled(False)
        self.pass_input.setEnabled(False)
        self.btn_ver_pass.setEnabled(False)

        # Simular proceso de verificación (800ms) para ver la animación
        QTimer.singleShot(800, lambda: self._verificar_credenciales(usr, psswd))

    def _verificar_credenciales(self, usr, psswd):

        try:
            if verificar_contraseña(usr, psswd):

                es_admin = verificacion_admin(usr)
                self.ss.iniciar_sesion(usr, es_admin)

                self.on_login_success(self.ss)
                QTimer.singleShot(600, self.close)

            else:
                self._login_error("Usuario o contraseña incorrectos.")

        except Exception as e:

            print("ERROR LOGIN:", e)

            self._login_error(
                "No se pudo conectar al sistema.\nIntenta nuevamente."
            )
    def _login_error(self, mensaje):

        self.login_btn.stop_loading()

        self.user_input.setEnabled(True)
        self.pass_input.setEnabled(True)
        self.btn_ver_pass.setEnabled(True)

        self.pass_input.setFocus()

        self.lbl_error.setText(mensaje)

        self.animar_shake(self.pass_container)
        
    def animar_shake(self, widget):
        anim = QPropertyAnimation(widget, b"pos", self)
        anim.setDuration(300)
        pos_inicial = widget.pos()

        # Definir keyframes para el movimiento izquierda-derecha
        anim.setKeyValueAt(0, pos_inicial)
        anim.setKeyValueAt(0.2, pos_inicial + QPoint(-10, 0))
        anim.setKeyValueAt(0.4, pos_inicial + QPoint(10, 0))
        anim.setKeyValueAt(0.6, pos_inicial + QPoint(-10, 0))
        anim.setKeyValueAt(0.8, pos_inicial + QPoint(10, 0))
        anim.setKeyValueAt(1, pos_inicial)

        anim.start()
        self._anim_shake = anim
