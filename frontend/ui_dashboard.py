from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QStackedWidget,
    QFrame,
    QLabel,
)
from PyQt5.QtCore import (
    Qt,
    QPropertyAnimation,
    QEasingCurve,
    QTimer,
    QParallelAnimationGroup,
    QPoint,
)

# Importar páginas
from frontend.ui_inventario import crear_pagina_inventario
from frontend.ui_ventas import crear_pagina_ventas
from frontend.ui_clientes import crear_pagina_clientes
from frontend.ui_grafico import crear_pagina_grafico
from frontend.ui_arqueo import crear_pagina_arqueo
from frontend.ui_menu_principal import crear_pagina_menu
from frontend.ui_ingreso import crear_pagina_ingreso
from frontend.estilos import aplicar_estilos


class AnimatedStackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_active = False
        self.m_duration = 400
        self.m_easing = QEasingCurve.OutCubic

    def setCurrentIndex(self, index):
        # Si ya es el actual o hay animación en curso, no hacer nada
        if self.currentIndex() == index or self.m_active:
            return

        # Primera carga (sin animación)
        if self.currentIndex() == -1:
            super().setCurrentIndex(index)
            return

        self.slide_to_index(index)

    def slide_to_index(self, index):
        self.m_active = True
        current_idx = self.currentIndex()
        next_idx = index

        current_widget = self.widget(current_idx)
        next_widget = self.widget(next_idx)

        width = self.frameRect().width()
        height = self.frameRect().height()

        next_widget.setGeometry(0, 0, width, height)

        # Determinar dirección
        if next_idx > current_idx:
            start_x = width
            end_x = -width
        else:
            start_x = -width
            end_x = width

        next_widget.move(start_x, 0)
        next_widget.show()
        next_widget.raise_()

        self.anim_group = QParallelAnimationGroup()

        anim_curr = QPropertyAnimation(current_widget, b"pos")
        anim_curr.setDuration(self.m_duration)
        anim_curr.setEasingCurve(self.m_easing)
        anim_curr.setStartValue(QPoint(0, 0))
        anim_curr.setEndValue(QPoint(end_x, 0))

        anim_next = QPropertyAnimation(next_widget, b"pos")
        anim_next.setDuration(self.m_duration)
        anim_next.setEasingCurve(self.m_easing)
        anim_next.setStartValue(QPoint(start_x, 0))
        anim_next.setEndValue(QPoint(0, 0))

        self.anim_group.addAnimation(anim_curr)
        self.anim_group.addAnimation(anim_next)

        def on_finished():
            super(AnimatedStackedWidget, self).setCurrentIndex(index)
            current_widget.move(0, 0)
            self.m_active = False

        self.anim_group.finished.connect(on_finished)
        self.anim_group.start()


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
        self.btn_facturas = QPushButton(" Facturas")
        self.btn_ingreso = QPushButton(" Ingreso Mercadería")
        self.btn_usuarios = QPushButton(" Usuarios")  # solo admin
        self.btn_graficos = QPushButton(" Dashboard")  # solo admin
        self.btn_logout = QPushButton(" Cerrar sesión")
        self.btn_salir = QPushButton(" Salir")

        # Agregar botones principales
        for btn in [
            self.btn_menu_principal,
            self.btn_inventario,
            self.btn_ventas,
            self.btn_arqueo,
            self.btn_facturas,
            self.btn_ingreso,
        ]:
            sidebar_layout.addWidget(btn)

        # Botones admin si aplica
        if self.sesion.es_admin:
            for btnAdmin in [self.btn_usuarios, self.btn_graficos]:
                sidebar_layout.addWidget(btnAdmin)

        sidebar_layout.addStretch()  # empuja al final

        # Estilo base para botones de salida (no cambian de estado activo)
        estilo_salida = """
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
        self.btn_logout.setStyleSheet(estilo_salida)
        self.btn_salir.setStyleSheet(estilo_salida)

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
        self.stack = AnimatedStackedWidget()
        self.menu_principal = crear_pagina_menu()
        self.menu_principal.navegar.connect(self.navegar_desde_menu)
        self.stack.currentChanged.connect(self.actualizar_botones_sidebar)
        self.stack.addWidget(self.menu_principal)  # 0

        # Páginas con botón volver
        self.page_inventario = crear_pagina_inventario()
        self.page_inventario.btn_volver.clicked.connect(
            lambda: self.stack.setCurrentIndex(0)
        )
        self.stack.addWidget(self.page_inventario)  # 1

        self.page_ventas = crear_pagina_ventas()
        self.page_ventas.btn_volver.clicked.connect(
            lambda: self.stack.setCurrentIndex(0)
        )
        self.stack.addWidget(self.page_ventas)  # 2

        self.page_clientes = crear_pagina_clientes()
        self.page_clientes.btn_volver.clicked.connect(
            lambda: self.stack.setCurrentIndex(0)
        )
        self.stack.addWidget(self.page_clientes)  # 3

        self.page_grafico = crear_pagina_grafico()
        self.page_grafico.btn_volver.clicked.connect(
            lambda: self.stack.setCurrentIndex(0)
        )
        self.stack.addWidget(self.page_grafico)  # 4

        self.page_arqueo = crear_pagina_arqueo()
        self.page_arqueo.btn_volver.clicked.connect(
            lambda: self.stack.setCurrentIndex(0)
        )
        self.stack.addWidget(self.page_arqueo)  # 5

        # Página Facturas (Placeholder)
        self.page_facturas = QWidget()
        layout_facturas = QVBoxLayout(self.page_facturas)
        lbl_facturas = QLabel("Gestión de Facturas (Próximamente)")
        lbl_facturas.setAlignment(Qt.AlignCenter)
        lbl_facturas.setStyleSheet("font-size: 20px; color: #636e72;")
        layout_facturas.addWidget(lbl_facturas)
        self.stack.addWidget(self.page_facturas)  # 6

        # Página Ingreso de Mercadería
        self.page_ingreso = crear_pagina_ingreso()
        self.page_ingreso.btn_volver.clicked.connect(
            lambda: self.stack.setCurrentIndex(0)
        )
        self.stack.addWidget(self.page_ingreso)  # 7

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
        self.btn_facturas.clicked.connect(lambda: self.stack.setCurrentIndex(6))
        self.btn_ingreso.clicked.connect(lambda: self.stack.setCurrentIndex(7))
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
        self.actualizar_botones_sidebar(0)

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

    def actualizar_botones_sidebar(self, index):
        mapping = {
            0: self.btn_menu_principal,
            1: self.btn_inventario,
            2: self.btn_ventas,
            3: self.btn_usuarios,
            4: self.btn_graficos,
            5: self.btn_arqueo,
            6: self.btn_facturas,
            7: self.btn_ingreso,
        }

        btn_activo = mapping.get(index)

        # Estilo base
        estilo_base = """
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

        # Estilo activo (resaltado)
        estilo_activo = """
            QPushButton {
                background-color: #F4D03F;
                color: #2D3436;
                padding: 15px;
                font-size: 18px;
                text-align: left;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
        """

        for btn in mapping.values():
            if btn:
                if btn == btn_activo:
                    btn.setStyleSheet(estilo_activo)
                else:
                    btn.setStyleSheet(estilo_base)

    def navegar_desde_menu(self, accion):
        rutas = {
            "inventario": 1,
            "ventas": 2,
            "usuarios": 3,
            "arqueo": 5,
            "facturas": 6,
            "ingreso_mercaderia": 7,
        }
        if accion in rutas:
            self.stack.setCurrentIndex(rutas[accion])
        else:
            print(f"Acción no implementada: {accion}")
