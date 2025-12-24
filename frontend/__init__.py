# This file marks the 'db' directory as a Python package.
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QStackedWidget
import os

class Ui_MenuPrincipal(QWidget):
    def __init__(self, parent=None, controlador=None):
        super().__init__(parent)
        self.controlador = controlador
        self.setObjectName("MenuPrincipal")

        # Ruta absoluta para asegurar que se encuentre la imagen
        ruta_fondo = os.path.join(os.path.dirname(__file__), "assets", "fondo_venta1.png")

        # Aplica el fondo al widget principal
        self.setStyleSheet(f"""
            QWidget#MenuPrincipal {{
                background-image: url({ruta_fondo});
                background-repeat: no-repeat;
                background-position: center;
                background-attachment: fixed;
            }}
        """)
