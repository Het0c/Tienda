from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHBoxLayout,
)
from PyQt5.QtCore import Qt
from datetime import date
from backend.logica.arqueo import cerrar_caja


def crear_pagina_arqueo():
    pagina = QWidget()
    layout = QVBoxLayout(pagina)
    layout.setContentsMargins(20, 10, 20, 20)
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

    # Título superior
    etiqueta = QLabel("Cierre de Caja - Informe Diario")
    etiqueta.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
    etiqueta.setStyleSheet("font-size: 18px; font-weight: bold; color: #2D3436;")
    layout.addWidget(etiqueta)

    # --- Sección Efectivo ---
    tabla_efectivo = QTableWidget()
    tabla_efectivo.setRowCount(2)
    tabla_efectivo.setColumnCount(2)
    tabla_efectivo.setHorizontalHeaderLabels(["Concepto", "Valor"])
    tabla_efectivo.horizontalHeader().setStretchLastSection(True)
    tabla_efectivo.verticalHeader().setVisible(False)

    datos_efectivo = [
        ("Subtotal ventas", "$4.500.000"),
        ("Total en efectivo", "$2.350.000"),
    ]
    for fila, (concepto, valor) in enumerate(datos_efectivo):
        tabla_efectivo.setItem(fila, 0, QTableWidgetItem(concepto))
        tabla_efectivo.setItem(fila, 1, QTableWidgetItem(valor))

    tabla_efectivo.setStyleSheet(
        """
        QTableWidget {
            gridline-color: #BDBDBD;
            font-size: 14px;
        }
        QHeaderView::section {
            background-color: #ECEFF1;
            font-weight: bold;
            padding: 4px;
            border: 1px solid #BDBDBD;
        }
    """
    )
    layout.addWidget(QLabel("Sección Efectivo"))
    layout.addWidget(tabla_efectivo)

    # --- Sección Gastos ---
    tabla_gastos = QTableWidget()
    tabla_gastos.setRowCount(1)
    tabla_gastos.setColumnCount(2)
    tabla_gastos.setHorizontalHeaderLabels(["Concepto", "Valor"])
    tabla_gastos.horizontalHeader().setStretchLastSection(True)
    tabla_gastos.verticalHeader().setVisible(False)

    datos_gastos = [
        ("Gastos del día", "$300.000"),
    ]
    for fila, (concepto, valor) in enumerate(datos_gastos):
        tabla_gastos.setItem(fila, 0, QTableWidgetItem(concepto))
        tabla_gastos.setItem(fila, 1, QTableWidgetItem(valor))

    tabla_gastos.setStyleSheet(
        """
        QTableWidget {
            gridline-color: #BDBDBD;
            font-size: 14px;
        }
        QHeaderView::section {
            background-color: #ECEFF1;
            font-weight: bold;
            padding: 4px;
            border: 1px solid #BDBDBD;
        }
    """
    )
    layout.addWidget(QLabel("Sección Gastos"))
    layout.addWidget(tabla_gastos)

    # --- Sección Ventas con tarjetas ---
    tabla_tarjetas = QTableWidget()
    tabla_tarjetas.setRowCount(2)
    tabla_tarjetas.setColumnCount(2)
    tabla_tarjetas.setHorizontalHeaderLabels(["Concepto", "Valor"])
    tabla_tarjetas.horizontalHeader().setStretchLastSection(True)
    tabla_tarjetas.verticalHeader().setVisible(False)

    datos_tarjetas = [
        ("Ventas con débito", "$1.200.000"),
        ("Ventas con crédito", "$950.000"),
    ]
    for fila, (concepto, valor) in enumerate(datos_tarjetas):
        tabla_tarjetas.setItem(fila, 0, QTableWidgetItem(concepto))
        tabla_tarjetas.setItem(fila, 1, QTableWidgetItem(valor))

    tabla_tarjetas.setStyleSheet(
        """
        QTableWidget {
            gridline-color: #BDBDBD;
            font-size: 14px;
        }
        QHeaderView::section {
            background-color: #ECEFF1;
            font-weight: bold;
            padding: 4px;
            border: 1px solid #BDBDBD;
        }
    """
    )
    layout.addWidget(QLabel("Sección Ventas con Tarjetas"))
    layout.addWidget(tabla_tarjetas)

    # --- Sección Totales ---
    tabla_totales = QTableWidget()
    tabla_totales.setRowCount(1)
    tabla_totales.setColumnCount(2)
    tabla_totales.setHorizontalHeaderLabels(["Concepto", "Valor"])
    tabla_totales.horizontalHeader().setStretchLastSection(True)
    tabla_totales.verticalHeader().setVisible(False)

    datos_totales = [
        ("Saldo final", "$6.400.000"),
    ]
    for fila, (concepto, valor) in enumerate(datos_totales):
        tabla_totales.setItem(fila, 0, QTableWidgetItem(concepto))
        tabla_totales.setItem(fila, 1, QTableWidgetItem(valor))

    tabla_totales.setStyleSheet(
        """
        QTableWidget {
            gridline-color: #BDBDBD;
            font-size: 14px;
        }
        QHeaderView::section {
            background-color: #ECEFF1;
            font-weight: bold;
            padding: 4px;
            border: 1px solid #BDBDBD;
        }
    """
    )
    layout.addWidget(QLabel("Sección Totales"))
    layout.addWidget(tabla_totales)

    # Botón "Cerrar caja" en la parte inferior derecha
    contenedor_boton = QHBoxLayout()
    contenedor_boton.setAlignment(Qt.AlignRight)

    btn_cerrar_caja = QPushButton("Cerrar caja")
    btn_cerrar_caja.setFixedSize(140, 40)
    btn_cerrar_caja.setStyleSheet(
        """
        QPushButton {
            background-color: #FF8A80;
            color: #2D3436;
            border: none;
            font-size: 14px;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #FF6E6E;
        }
    """
    )

    def confirmar_cierre():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Confirmar cierre de caja")
        msg.setText(
            "¿Desea proceder con el arqueo y cerrar la caja?\nLos cambios serán guardados."
        )
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        respuesta = msg.exec_()
        if respuesta == QMessageBox.Yes:
            cerrar_caja(date.today())  # aquí pasas la fecha que necesites

    btn_cerrar_caja.clicked.connect(confirmar_cierre)

    contenedor_boton.addWidget(btn_cerrar_caja)
    layout.addLayout(contenedor_boton)
    # DASDEWD

    return pagina
