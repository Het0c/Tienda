from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QStackedWidget,
    QFrame,
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer

# Importar páginas
from frontend.ui_inventario import crear_pagina_inventario
from frontend.ui_ventas import crear_pagina_ventas
from frontend.ui_clientes import crear_pagina_clientes
from frontend.ui_grafico import crear_pagina_grafico
from frontend.ui_arqueo import crear_pagina_arqueo
from frontend.ui_menu_principal import crear_pagina_menu
from frontend.estilos import aplicar_estilos


class Dashboard(QMainWindow):
    def __init__(self, sesion):
        super().__init__()
        self.sesion = sesion
        self.setWindowTitle("Sistema de Ventas")
        self.setMinimumSize(1000, 600)

        aplicar_estilos(self)

        # ===============================
        # LAYOUT BASE
        # ===============================
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ===============================
        # SIDEBAR
        # ===============================
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setMinimumWidth(0)
        self.sidebar.setMaximumWidth(0)  # cerrado al inicio
        self.sidebar.setStyleSheet("background-color: #2D3436;")

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(10)

        # ===============================
        # BOTONES DEL SIDEBAR
        # ===============================
        # Botones principales
        self.btn_menu_principal = QPushButton(" Menú Principal")
        self.btn_inventario = QPushButton(" Inventario")
        self.btn_ventas = QPushButton(" Ventas")
        self.btn_arqueo = QPushButton(" Arqueo")
        self.btn_usuarios = QPushButton(" Usuarios")  # solo admin
        self.btn_graficos = QPushButton(" Dashboard")  # solo admin
        self.btn_logout = QPushButton(" Cerrar sesión")
        self.btn_salir = QPushButton(" Salir")

        # Función para estilizar botones
        def estilo_btn(btn):
            btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #2D3436;
                    color: white;
                    padding: 15px;
                    font-size: 18px;
                    text-align: left;
                    border: none;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #636e72;
                }
            """
            )

        # Agregar botones principales
        for btn in [
            self.btn_menu_principal,
            self.btn_inventario,
            self.btn_ventas,
            self.btn_arqueo,
        ]:
            estilo_btn(btn)
            sidebar_layout.addWidget(btn)

        # Botones admin si aplica
        if self.sesion.es_admin:
            for btnAdmin in [self.btn_usuarios, self.btn_graficos]:
                estilo_btn(btnAdmin)
                sidebar_layout.addWidget(btnAdmin)

        sidebar_layout.addStretch()  # empuja al final
        estilo_btn(self.btn_logout)
        estilo_btn(self.btn_salir)
        sidebar_layout.addWidget(self.btn_logout)
        sidebar_layout.addWidget(self.btn_salir)

        # ===============================
        # CONTENIDO PRINCIPAL
        # ===============================
        contenido = QWidget()
        contenido_layout = QVBoxLayout(contenido)
        contenido_layout.setContentsMargins(20, 20, 20, 20)
        contenido_layout.setSpacing(10)

        # Botón hamburguesa
        menu_layout = QHBoxLayout()
        self.btn_menu = QPushButton("☰")
        self.btn_menu.setFixedSize(40, 40)
        self.btn_menu.setStyleSheet(
            "font-size: 20px; background-color: #dfe6e9; border-radius: 6px;"
        )
        self.btn_menu.clicked.connect(self.toggle_sidebar)
        menu_layout.addWidget(self.btn_menu)
        menu_layout.setAlignment(Qt.AlignLeft)
        contenido_layout.addLayout(menu_layout)

        # Stacked widget para páginas
        self.stack = QStackedWidget()
        self.stack.addWidget(crear_pagina_menu())  # 0
        self.stack.addWidget(crear_pagina_inventario())  # 1
        self.stack.addWidget(crear_pagina_ventas())  # 2
        self.stack.addWidget(crear_pagina_clientes())  # 3
        self.stack.addWidget(crear_pagina_grafico())  # 4
        self.stack.addWidget(crear_pagina_arqueo())  # 5
        self.stack.setCurrentIndex(0)

        contenido_layout.addWidget(self.stack)

        # ===============================
        # CONECTAR BOTONES
        # ===============================
        self.btn_menu_principal.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_inventario.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.btn_ventas.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        self.btn_usuarios.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        self.btn_graficos.clicked.connect(lambda: self.stack.setCurrentIndex(4))
        self.btn_arqueo.clicked.connect(lambda: self.stack.setCurrentIndex(5))
        self.btn_logout.clicked.connect(self.cerrar_sesion)
        self.btn_salir.clicked.connect(self.salir)

        # ===============================
        # LAYOUT FINAL
        # ===============================
        main_layout.addWidget(self.sidebar, 0)
        main_layout.addWidget(contenido, 1)
        self.setCentralWidget(central_widget)

        # Maximizar ventana al inicio
        QTimer.singleShot(30, self._fix_dashboard_window)

    # ========================================================
    # FUNCIONES
    # ========================================================
    def _fix_dashboard_window(self):
        self.setWindowState(Qt.WindowNoState)
        self.showNormal()
        self.raise_()
        self.activateWindow()
        QTimer.singleShot(50, lambda: self.setWindowState(Qt.WindowMaximized))

    def cerrar_sesion(self):
        from frontend.login import LoginWindow

        self.close()
        self.login = LoginWindow(on_login_success=self.abrir_dashboard_nuevo)
        self.login.show()

    def abrir_dashboard_nuevo(self, sesion):
        self.new_dash = Dashboard(sesion)
        self.new_dash.showMaximized()

    def salir(self):
        import sys

        sys.exit()

    def toggle_sidebar(self):
        ancho_actual = self.sidebar.maximumWidth()
        ancho_destino = 300 if ancho_actual == 0 else 0
        anim = QPropertyAnimation(self.sidebar, b"maximumWidth")
        anim.setDuration(400)
        anim.setStartValue(ancho_actual)
        anim.setEndValue(ancho_destino)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        anim.start()
        self.animacion_sidebar = anim  # evita garbage collection
