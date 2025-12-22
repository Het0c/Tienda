from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QStackedWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from frontend.ui_inventario import crear_pagina_inventario

def crear_pagina_menu(controlador=None):
    return Ui_MenuPrincipal(controlador=controlador)


class Ui_MenuPrincipal(QWidget):

    def __init__(self, parent=None, controlador=None):
        super().__init__(parent)
        self.controlador = controlador
        self.setObjectName("MenuPrincipal")


        # 👉 Fondo aplicado vía stylesheet (no se pierde al cambiar páginas)
        self.setStyleSheet("""
            QWidget#MenuPrincipal {
                background-image: url(frontend/assets/fondo_venta1.png);
                background-repeat: no-repeat;
                background-position: center;
                background-attachment: fixed;
            }
        """)

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        # Contenedor de páginas
        self.stacked = QStackedWidget(self)
        main_layout.addWidget(self.stacked)

        # Página inicial (menú con tarjetas)
        self.menu_page = QWidget()
        cards_layout = QHBoxLayout(self.menu_page)
        cards_layout.setSpacing(40)
        cards_layout.setAlignment(Qt.AlignCenter)

        cards_data = [
            ("Inventario", "inventario"),
            ("Ventas", "ventas"),
            ("Arqueo", "arqueo"),
            ("Usuarios", "usuarios"),
        ]

        for nombre, accion in cards_data:
            card = self.create_card(nombre, accion)
            cards_layout.addWidget(card)

        self.stacked.addWidget(self.menu_page)  # índice 0 → menú

    def create_card(self, nombre, accion):
        frame = QFrame()
        frame.setFixedSize(180, 180)
        frame.setStyleSheet("""
            QFrame {
                background-color: #ECF0F1;
                border-radius: 18px;
            }
            QFrame:hover {
                background-color: #AAB7B8;
            }
        """)

        vbox = QVBoxLayout(frame)
        vbox.setAlignment(Qt.AlignCenter)

        label = QLabel(nombre)
        label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        label.setStyleSheet("color: #2D3436;")
        label.setAlignment(Qt.AlignCenter)
        vbox.addWidget(label)

        boton = QPushButton(frame)
        boton.setStyleSheet("background: transparent; border: none;")
        boton.setCursor(Qt.PointingHandCursor)
        boton.setFixedSize(180, 180)
        boton.clicked.connect(lambda _, a=accion: self.card_clicked(a))

        return frame

    def card_clicked(self, accion):
        if accion == "inventario":
            # Crear página inventario y mostrarla dentro del stacked
            inventario_page = crear_pagina_inventario()
            self.stacked.addWidget(inventario_page)
            self.stacked.setCurrentWidget(inventario_page)
        elif self.controlador:
            if accion == "ventas":
                self.controlador.abrir_ventas(self.stacked)
            elif accion == "arqueo":
                self.controlador.abrir_arqueo(self.stacked)
            elif accion == "usuarios":
                self.controlador.abrir_usuarios(self.stacked)
        else:
            print(f"Acción '{accion}' no disponible (controlador no inicializado)")
