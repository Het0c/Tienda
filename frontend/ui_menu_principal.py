from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QFrame,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal
import os


def crear_pagina_menu(controlador=None):
    return Ui_MenuPrincipal(controlador=controlador)


class Ui_MenuPrincipal(QWidget):
    navegar = pyqtSignal(str)

    def __init__(self, parent=None, controlador=None):
        super().__init__(parent)
        self.controlador = controlador
        self.setObjectName("MenuPrincipal")
        self.setAttribute(Qt.WA_StyledBackground, True)

        ruta_fondo = os.path.join(
            os.path.dirname(__file__), "assets", "fondo_venta1.png"
        ).replace("\\", "/")

        # 👉 Fondo aplicado vía stylesheet (no se pierde al cambiar páginas)
        self.setStyleSheet(
            f"""
            QWidget#MenuPrincipal {{
                background-image: url({ruta_fondo});
                background-repeat: no-repeat;
                background-position: center;
                background-attachment: fixed;
            }}
        """
        )

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        # Grid de tarjetas
        cards_layout = QGridLayout()
        cards_layout.setSpacing(40)
        cards_layout.setAlignment(Qt.AlignCenter)

        cards_data = [
            ("Inventario", "inventario", "📦"),
            ("Ventas", "ventas", "🛒"),
            ("Arqueo", "arqueo", "💰"),
            ("Usuarios", "usuarios", "👥"),
            ("Facturas", "facturas", "🧾"),
            ("Ingreso de mercadería", "ingreso_mercaderia", "🚚"),
        ]

        row = 0
        col = 0
        for nombre, accion, simbolo in cards_data:
            card = self.create_card(nombre, accion, simbolo)
            cards_layout.addWidget(card, row, col)
            col += 1
            if col > 2:  # 3 columnas
                col = 0
                row += 1

        main_layout.addLayout(cards_layout)

    def create_card(self, nombre, accion, simbolo):
        frame = QFrame()
        frame.setFixedSize(320, 320)
        frame.setStyleSheet(
            """
            QFrame {
                background-color: rgba(255, 255, 255, 0.92);
                border-radius: 30px;
                border: 1px solid #dfe6e9;
            }
            QFrame:hover {
                background-color: #ffffff;
                border: 4px solid #F4D03F;
            }
        """
        )

        vbox = QVBoxLayout(frame)
        vbox.setAlignment(Qt.AlignCenter)
        vbox.setContentsMargins(0, 0, 0, 10)
        vbox.setSpacing(0)

        lbl_simbolo = QLabel(simbolo)
        lbl_simbolo.setFont(QFont("Segoe UI", 190))
        lbl_simbolo.setStyleSheet(
            "color: #2D3436; background: transparent; border: none;"
        )
        lbl_simbolo.setAlignment(Qt.AlignCenter)
        vbox.addWidget(lbl_simbolo)

        label = QLabel(nombre)
        label.setWordWrap(True)
        label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        label.setStyleSheet("color: #2D3436; background: transparent; border: none;")
        label.setAlignment(Qt.AlignCenter)
        vbox.addWidget(label)

        boton = QPushButton(frame)
        boton.setStyleSheet("background: transparent; border: none;")
        boton.setCursor(Qt.PointingHandCursor)
        boton.setFixedSize(320, 320)
        boton.clicked.connect(lambda _, a=accion: self.navegar.emit(a))

        return frame
