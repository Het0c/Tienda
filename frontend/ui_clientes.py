from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QDialog,
    QLineEdit,
    QHBoxLayout,
    QMessageBox,
)
from PyQt5.QtCore import Qt, QTimer


# --- Ventana de autorización ---
class VentanaAutorizacion(QDialog):
    def __init__(self, tabla, fila):
        super().__init__()
        self.setWindowTitle("Autorización requerida")
        self.setMinimumSize(350, 200)
        self.tabla = tabla
        self.fila = fila

        self.setStyleSheet(
            """
            QDialog {
                background-color: rgba(255,255,255,0.95);
                border-radius: 12px;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2D3436;
            }
            QLineEdit {
                background-color: white;
                border: 1px solid #BDBDBD;
                border-radius: 6px;
                padding: 6px;
                font-size: 14px;
            }
        """
        )

        layout = QVBoxLayout(self)

        label = QLabel("Ingrese código de administrador")
        layout.addWidget(label)

        self.input_codigo = QLineEdit()
        self.input_codigo.setPlaceholderText("Escanee o ingrese código...")
        layout.addWidget(self.input_codigo)

        btn_autorizar = QPushButton("Autorizar")
        btn_autorizar.setStyleSheet(
            """
            QPushButton {
                background-color: #74b9ff;
                color: white;
                font-size: 14px;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #0984e3;
            }
        """
        )
        layout.addWidget(btn_autorizar)

        btn_autorizar.clicked.connect(self.autorizar)

    def autorizar(self):
        if self.input_codigo.text().strip():
            # Por ahora cualquier código es válido
            self.accept()
            VentanaDetalle(self.tabla, self.fila).exec_()
        else:
            self.reject()


# --- Ventana de detalle y cambio de contraseña ---
class VentanaDetalle(QDialog):
    def __init__(self, tabla, fila):
        super().__init__()
        self.setWindowTitle("Detalle del Usuario")
        self.setMinimumSize(400, 300)
        self.tabla = tabla
        self.fila = fila

        self.setStyleSheet(
            """
            QDialog {
                background-color: rgba(255,255,255,0.95);
                border-radius: 12px;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2D3436;
            }
            QLineEdit {
                background-color: white;
                border: 1px solid #BDBDBD;
                border-radius: 6px;
                padding: 6px;
                font-size: 14px;
            }
        """
        )

        layout = QVBoxLayout(self)

        # Datos del trabajador (solo lectura)
        nombre = self.tabla.item(fila, 0).text()
        rut = self.tabla.item(fila, 1).text()
        cargo = self.tabla.item(fila, 2).text()

        layout.addWidget(QLabel(f"Nombre: {nombre}"))
        layout.addWidget(QLabel(f"RUT: {rut}"))
        layout.addWidget(QLabel(f"Cargo: {cargo}"))

        # Campo de contraseña
        layout.addWidget(QLabel("Nueva Contraseña"))
        password_layout = QHBoxLayout()
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setPlaceholderText("Ingrese nueva contraseña")

        btn_ver = QPushButton("👁")
        btn_ver.setFixedSize(30, 30)
        btn_ver.setStyleSheet("background-color: #dfe6e9; border-radius: 6px;")

        password_layout.addWidget(self.input_password)
        password_layout.addWidget(btn_ver)
        layout.addLayout(password_layout)

        # Botones Guardar y Cancelar
        botones_layout = QHBoxLayout()
        btn_guardar = QPushButton("Guardar")
        btn_cancelar = QPushButton("Cancelar")

        btn_guardar.setStyleSheet(
            """
            QPushButton {
                background-color: #27AE60;
                color: white;
                font-size: 14px;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #219150;
            }
        """
        )

        btn_cancelar.setStyleSheet(
            """
            QPushButton {
                background-color: #FF8A80;
                color: #2D3436;
                font-size: 14px;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #FF6E6E;
            }
        """
        )

        botones_layout.addWidget(btn_guardar)
        botones_layout.addWidget(btn_cancelar)
        layout.addLayout(botones_layout)

        # Conectar botones
        btn_guardar.clicked.connect(self.guardar_cambios)
        btn_cancelar.clicked.connect(self.close)
        btn_ver.clicked.connect(self.ver_password_temporal)

    def guardar_cambios(self):
        confirmacion = QMessageBox.question(
            self,
            "Confirmar cambios",
            "¿Deseas guardar la nueva contraseña?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirmacion == QMessageBox.Yes:
            print(
                f"Contraseña guardada: {self.input_password.text()}"
            )  # Aquí irá la lógica de BD
            self.close()

    def ver_password_temporal(self):
        self.input_password.setEchoMode(QLineEdit.Normal)
        QTimer.singleShot(
            2000, lambda: self.input_password.setEchoMode(QLineEdit.Password)
        )


# --- Página de clientes con tabla ---
def crear_pagina_clientes():
    pagina = QWidget()
    layout = QVBoxLayout(pagina)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(20)

    # Botón Volver
    btn_volver = QPushButton("⬅ Volver al Menú")
    btn_volver.setCursor(Qt.PointingHandCursor)
    btn_volver.setFixedWidth(160)
    btn_volver.setStyleSheet(
        "background-color: #2D3436; color: white; border-radius: 5px; padding: 8px; font-weight: bold;"
    )
    layout.addWidget(btn_volver, alignment=Qt.AlignLeft)
    pagina.btn_volver = btn_volver

    etiqueta = QLabel("Lista de Clientas")
    etiqueta.setAlignment(Qt.AlignCenter)
    etiqueta.setStyleSheet("font-size: 18px; font-weight: bold; color: #2D3436;")
    layout.addWidget(etiqueta)

    tabla = QTableWidget()
    tabla.setColumnCount(4)
    tabla.setHorizontalHeaderLabels(["Nombre", "RUT", "Cargo", "Acción"])
    tabla.horizontalHeader().setStretchLastSection(True)
    tabla.verticalHeader().setVisible(False)

    tabla.setStyleSheet(
        """
        QTableWidget {
            gridline-color: #BDBDBD;
            font-size: 14px;
            background-color: rgba(255,255,255,0.85);
            border-radius: 8px;
        }
        QHeaderView::section {
            background-color: #ECEFF1;
            font-weight: bold;
            padding: 4px;
            border: 1px solid #BDBDBD;
        }
    """
    )

    datos = [
        ("Juan Pérez", "12.345.678-9", "Gerente"),
        ("María González", "9.876.543-2", "Vendedora"),
        ("Carlos López", "21.234.567-8", "Cajero"),
        ("Ana Torres", "18.765.432-1", "Supervisora"),
    ]

    def agregar_fila(nombre, rut, cargo):
        fila = tabla.rowCount()
        tabla.insertRow(fila)
        tabla.setItem(fila, 0, QTableWidgetItem(nombre))
        tabla.setItem(fila, 1, QTableWidgetItem(rut))
        tabla.setItem(fila, 2, QTableWidgetItem(cargo))

        btn_accion = QPushButton("...")
        btn_accion.setFixedSize(30, 25)
        btn_accion.setStyleSheet(
            "background-color: #dfe6e9; border-radius: 4px; font-weight: bold;"
        )
        tabla.setCellWidget(fila, 3, btn_accion)

        btn_accion.clicked.connect(
            lambda _, f=fila: VentanaAutorizacion(tabla, f).exec_()
        )

    for nombre, rut, cargo in datos:
        agregar_fila(nombre, rut, cargo)

    layout.addWidget(tabla)
    pagina.setLayout(layout)

    pagina.tabla_clientes = tabla
    pagina.agregar_fila = agregar_fila
    return pagina
