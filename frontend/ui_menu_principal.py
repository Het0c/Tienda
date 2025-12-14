from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt


def crear_pagina_menu(controlador=None):
    return Ui_MenuPrincipal(controlador=controlador)


class Ui_MenuPrincipal(QWidget):
    def __init__(self, parent=None, controlador=None):
        super().__init__(parent)
        self.controlador = controlador
        self.setObjectName("MenuPrincipal")

        # ------------------------
        # Fondo de la ventana
        # ------------------------
        self.fondo = QLabel(self)
        pixmap = QPixmap("frontend/assets/fondo_venta1.png")
        self.fondo.setPixmap(pixmap)
        self.fondo.setScaledContents(True)
        self.fondo.setGeometry(0, 0, self.width(), self.height())
        self.fondo.lower()  # Enviar al fondo

        # Ajuste dinámico de tamaño
        self.resizeEvent = lambda event: self.fondo.setGeometry(
            0, 0, self.width(), self.height()
        )

        # ------------------------
        # Layout principal centrado
        # ------------------------
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(40)
        cards_layout.setAlignment(Qt.AlignCenter)

        # ------------------------
        # Datos de las tarjetas
        # ------------------------
        cards_data = [
            ("Inventario", "inventario"),
            ("Ventas", "ventas"),
            ("Arqueo", "arqueo"),
            ("Usuarios", "usuarios"),
        ]

        for nombre, accion in cards_data:
            card = self.create_card(nombre, accion)
            cards_layout.addWidget(card)

        main_layout.addLayout(cards_layout)

    def create_card(self, nombre, accion):
        frame = QFrame()
        frame.setFixedSize(180, 180)
        frame.setStyleSheet(
            """
            QFrame {
                background-color: #ECF0F1;  /* gris claro */
                border-radius: 18px;
            }
            QFrame:hover {
                background-color: #AAB7B8;  /* gris más oscuro al hover */
            }
        """
        )

        vbox = QVBoxLayout(frame)
        vbox.setAlignment(Qt.AlignCenter)

        label = QLabel(nombre)
        label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        label.setStyleSheet("color: #2D3436;")  # texto gris oscuro
        label.setAlignment(Qt.AlignCenter)
        vbox.addWidget(label)

        # Botón invisible para capturar clics
        boton = QPushButton(frame)
        boton.setStyleSheet("background: transparent; border: none;")
        boton.setCursor(Qt.PointingHandCursor)
        boton.setFixedSize(180, 180)
        boton.clicked.connect(lambda: self.card_clicked(accion))

        return frame

    def card_clicked(self, accion):
        if self.controlador is None:
            print("⚠ No se asignó el controlador del Dashboard")
            return

        acciones = {
            "inventario": self.controlador.abrir_inventario,
            "ventas": self.controlador.abrir_ventas,
            "arqueo": self.controlador.abrir_arqueo,
            "usuarios": self.controlador.abrir_usuarios,
        }

        if accion in acciones:
            acciones[accion]()
