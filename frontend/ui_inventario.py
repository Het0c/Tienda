from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSpacerItem, QSizePolicy, QScrollArea, QLineEdit, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from backend.logica.inventario import consultar_inventario_ropa

def crear_pagina_inventario():
    pagina = QWidget()

    fondo = QLabel(pagina)
    fondo.setPixmap(QPixmap("frontend/assets/fondo_inventario.png"))
    fondo.setScaledContents(True)
    fondo.setGeometry(0, 0, pagina.width(), pagina.height())
    pagina.resizeEvent = lambda event: fondo.setGeometry(0, 0, pagina.width(), pagina.height())

    layout_principal = QVBoxLayout(pagina)
    layout_principal.setAlignment(Qt.AlignCenter)
    layout_principal.setContentsMargins(40, 40, 40, 40)

    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setStyleSheet("background: transparent; border: none;")

    tarjeta = QFrame()
    tarjeta.setMinimumWidth(700)
    tarjeta.setStyleSheet("""
        QFrame {
            background-color: rgba(255, 255, 255, 0.85);
            border-radius: 12px;
            padding: 20px;
        }
        QLabel {
            font-size: 14px;
            color: #2D3436;
        }
    """)

    tarjeta_layout = QVBoxLayout(tarjeta)
    tarjeta_layout.setAlignment(Qt.AlignTop)

    etiqueta = QLabel("Gestión de Productos")
    etiqueta.setAlignment(Qt.AlignCenter)
    etiqueta.setStyleSheet("font-weight: bold; font-size: 16px;")
    tarjeta_layout.addWidget(etiqueta)

    # 🔍 Barra de búsqueda con botones
    barra_busqueda = QFrame()
    barra_busqueda.setStyleSheet("background-color: transparent;")
    barra_layout = QHBoxLayout(barra_busqueda)
    barra_layout.setContentsMargins(0, 0, 0, 0)
    barra_layout.setSpacing(10)

    campo_busqueda = QLabel("Buscador")
    campo_busqueda.setStyleSheet("font-weight: bold; font-size: 14px;")

    input_busqueda = QLineEdit()
    input_busqueda.setPlaceholderText("Escribe el nombre de la prenda...")
    input_busqueda.setStyleSheet("""
        QLineEdit {
            background-color: white;
            border: 1px solid #BDBDBD;
            border-radius: 6px;
            padding: 6px;
            font-size: 13px;
        }
    """)

    btn_agregar = QPushButton("Agregar")
    btn_agregar.setStyleSheet("""
        QPushButton {
            background-color: #A8E6CF;
            color: #2D3436;
            border: none;
            padding: 6px 12px;
            font-size: 13px;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #81D4A3;
        }
    """)

    btn_eliminar = QPushButton("Eliminar")
    btn_eliminar.setStyleSheet("""
        QPushButton {
            background-color: #FF8A80;
            color: #2D3436;
            border: none;
            padding: 6px 12px;
            font-size: 13px;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #FF6E6E;
        }
    """)

    barra_layout.addWidget(campo_busqueda)
    barra_layout.addWidget(input_busqueda)
    barra_layout.addWidget(btn_agregar)
    barra_layout.addWidget(btn_eliminar)
    tarjeta_layout.addWidget(barra_busqueda)

    #  Botón Mover debajo y centrado
    btn_mover = QPushButton("Mover")
    btn_mover.setStyleSheet("""
        QPushButton {
            background-color: #FFF9C4;
            color: #2D3436;
            border: none;
            padding: 6px 12px;
            font-size: 13px;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #FFF176;
        }
    """)
    mover_layout = QHBoxLayout()
    mover_layout.setAlignment(Qt.AlignRight)
    mover_layout.addWidget(btn_mover)
    tarjeta_layout.addLayout(mover_layout)

    #  Contenedor de resultados
    contenedor_scroll = QWidget()
    contenedor_layout = QHBoxLayout(contenedor_scroll)
    contenedor_layout.setAlignment(Qt.AlignTop)
    tarjeta_layout.addWidget(contenedor_scroll)
    tarjeta_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    scroll_area.setWidget(tarjeta)
    layout_principal.addWidget(scroll_area)

    #  Función para crear columnas
    def crear_columna(titulo, datos):
        columna = QVBoxLayout()
        label = QLabel(titulo)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-weight: bold;")
        columna.addWidget(label)
        for dato in datos:
            item = QLabel(str(dato))
            item.setStyleSheet("padding: 6px;")
            columna.addWidget(item)
        return columna

    #  Función para mostrar resultados
    def mostrar_inventario(inventario):
        while contenedor_layout.count():
            item = contenedor_layout.takeAt(0)
            if item.layout():
                while item.layout().count():
                    subitem = item.layout().takeAt(0)
                    widget = subitem.widget()
                    if widget:
                        widget.deleteLater()
            elif item.widget():
                item.widget().deleteLater()

        prenda = [i["Prenda"] for i in inventario]
        piso1 = [i["Primer piso"] for i in inventario]
        piso2 = [i["Segundo Piso"] for i in inventario]
        total = [i["Total Stock"] for i in inventario]

        contenedor_layout.addLayout(crear_columna("Prenda", prenda))
        contenedor_layout.addLayout(crear_columna("Primer piso", piso1))
        contenedor_layout.addLayout(crear_columna("Segundo piso", piso2))
        contenedor_layout.addLayout(crear_columna("Total Stock", total))

    #  Función reactiva
    def actualizar_inventario(texto):
        inventario = consultar_inventario_ropa(texto)
        mostrar_inventario(inventario)

    input_busqueda.textChanged.connect(actualizar_inventario)
    mostrar_inventario(consultar_inventario_ropa(""))

    return pagina
