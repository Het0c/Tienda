import json
import sqlite3
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHBoxLayout,
    QFrame,
    QHeaderView,
    QGridLayout,
)
from PyQt5.QtCore import Qt
from datetime import date, datetime
from backend.logica.arqueo import cerrar_caja


def obtener_datos_bd():
    hoy = date.today().strftime("%Y-%m-%d")
    total_efectivo = 0
    total_tarjeta = 0  # Debito/Credito
    total_transferencia = 0
    total_gastos = 0

    try:
        with sqlite3.connect("reuso.db") as conn:
            cursor = conn.cursor()

            # Verificar si existe tabla ventas y sumar
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='ventas'"
            )
            if cursor.fetchone():
                # Se asume que la columna fecha es TEXT YYYY-MM-DD...
                cursor.execute(
                    "SELECT total, metodo_pago FROM ventas WHERE date(fecha) = ?",
                    (hoy,),
                )
                rows = cursor.fetchall()
                for total, metodo in rows:
                    if metodo == "Efectivo":
                        total_efectivo += total
                    elif metodo in ["Tarjeta", "Débito/Crédito", "Débito", "Crédito"]:
                        total_tarjeta += total
                    elif metodo == "Transferencia":
                        total_transferencia += total

            # Verificar si existe tabla gastos y sumar
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='gastos'"
            )
            if cursor.fetchone():
                cursor.execute("SELECT monto FROM gastos WHERE date(fecha) = ?", (hoy,))
                rows = cursor.fetchall()
                for (monto,) in rows:
                    total_gastos += monto

    except Exception as e:
        print(f"Error BD Arqueo: {e}")

    return total_efectivo, total_tarjeta, total_transferencia, total_gastos


def crear_pagina_arqueo():
    pagina = QWidget()
    layout = QVBoxLayout(pagina)
    layout.setContentsMargins(40, 40, 40, 40)
    layout.setSpacing(30)

    # Detectar tema
    tema = "dark"
    try:
        with open("config.json", "r") as f:
            data = json.load(f)
            tema = data.get("tema", "dark")
    except:
        pass

    # Definir paleta de colores
    if tema == "dark":
        bg_card = "#2D3436"
        text_color = "white"
        header_bg = "#2D3436"
        border_color = "#636e72"
        table_bg = "#2D3436"
        alternate_bg = "#353b48"
        btn_back_bg = "#636e72"
    else:
        bg_card = "white"
        text_color = "#2D3436"
        header_bg = "#ECEFF1"
        border_color = "#BDBDBD"
        table_bg = "white"
        alternate_bg = "#F9F9F9"
        btn_back_bg = "#2D3436"

    # Botón Volver
    btn_volver = QPushButton("⬅ Volver al Menú")
    btn_volver.setCursor(Qt.PointingHandCursor)
    btn_volver.setFixedWidth(160)
    btn_volver.setStyleSheet(
        f"background-color: {btn_back_bg}; color: white; border-radius: 8px; padding: 10px; font-weight: bold; font-size: 14px;"
    )
    layout.addWidget(btn_volver, alignment=Qt.AlignLeft)
    pagina.btn_volver = btn_volver

    # Título superior
    etiqueta = QLabel("Cierre de Caja - Informe Diario")
    etiqueta.setAlignment(Qt.AlignCenter)
    etiqueta.setStyleSheet(
        f"font-size: 36px; font-weight: bold; color: {text_color}; margin-bottom: 20px;"
    )
    layout.addWidget(etiqueta)

    # Función para crear tarjetas de información
    def crear_tarjeta(titulo, icono, datos):
        card = QFrame()
        card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {bg_card};
                border-radius: 12px;
                border: 1px solid {border_color};
            }}
        """
        )
        card.setMinimumWidth(500)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)

        # Título de la tarjeta
        lbl_titulo = QLabel(f"{icono} {titulo}")
        lbl_titulo.setStyleSheet(
            f"font-size: 24px; font-weight: bold; color: {text_color}; border: none; margin-bottom: 10px;"
        )
        card_layout.addWidget(lbl_titulo)

        # Tabla
        tabla = QTableWidget()
        tabla.setRowCount(len(datos))
        tabla.setColumnCount(2)
        tabla.setHorizontalHeaderLabels(["Concepto", "Valor"])
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabla.verticalHeader().setVisible(False)
        tabla.setAlternatingRowColors(True)
        tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        tabla.setSelectionMode(QTableWidget.NoSelection)
        tabla.setFocusPolicy(Qt.NoFocus)

        # Altura ajustada al contenido
        altura = 60 * len(datos) + 50
        tabla.setMinimumHeight(altura)
        tabla.setMaximumHeight(altura)

        tabla.setStyleSheet(
            f"""
            QTableWidget {{
                background-color: {table_bg};
                color: {text_color};
                gridline-color: {border_color};
                border: none;
                font-size: 20px;
                alternate-background-color: {alternate_bg};
            }}
            QHeaderView::section {{
                background-color: {header_bg};
                color: {text_color};
                font-weight: bold;
                padding: 12px;
                border: none;
                border-bottom: 2px solid {border_color};
                font-size: 20px;
            }}
            QTableWidget::item {{
                padding: 12px;
                border-bottom: 1px solid {border_color};
            }}
        """
        )

        for fila, (concepto, valor) in enumerate(datos):
            tabla.setItem(fila, 0, QTableWidgetItem(concepto))
            item_valor = QTableWidgetItem(valor)
            item_valor.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_valor.setFlags(Qt.ItemIsEnabled)  # Solo lectura
            tabla.setItem(fila, 1, item_valor)

        card_layout.addWidget(tabla)
        return card

    # Obtener datos reales
    efectivo, tarjeta, transferencia, gastos = obtener_datos_bd()
    subtotal_ventas = efectivo + tarjeta + transferencia
    saldo_final = efectivo - gastos  # Lo que debería haber en caja física (aprox)

    datos_efectivo = [
        ("Ventas Totales (Día)", f"${subtotal_ventas:,}"),
        ("Total en Efectivo", f"${efectivo:,}"),
    ]
    datos_gastos = [
        ("Gastos del día", f"${gastos:,}"),
    ]
    datos_tarjetas = [
        ("Débito / Crédito", f"${tarjeta:,}"),
        ("Transferencias", f"${transferencia:,}"),
    ]
    datos_totales = [
        ("Saldo Final (Efectivo - Gastos)", f"${saldo_final:,}"),
    ]

    # Layout de tarjetas (Grid)
    grid = QGridLayout()
    grid.setSpacing(30)

    grid.addWidget(crear_tarjeta("Efectivo", "💵", datos_efectivo), 0, 0)
    grid.addWidget(crear_tarjeta("Tarjetas", "💳", datos_tarjetas), 0, 1)
    grid.addWidget(crear_tarjeta("Gastos", "📉", datos_gastos), 1, 0)
    grid.addWidget(crear_tarjeta("Totales", "💰", datos_totales), 1, 1)

    layout.addLayout(grid)
    layout.addStretch()

    # Botón Cerrar Caja
    btn_cerrar_caja = QPushButton("🔒 Cerrar Caja")
    btn_cerrar_caja.setCursor(Qt.PointingHandCursor)
    btn_cerrar_caja.setFixedSize(250, 60)
    btn_cerrar_caja.setStyleSheet(
        """
        QPushButton {
            background-color: #e17055;
            color: white;
            border: none;
            font-size: 20px;
            font-weight: bold;
            border-radius: 8px;
        }
        QPushButton:hover {
            background-color: #d63031;
        }
    """
    )

    def confirmar_cierre():
        msg = QMessageBox(pagina)
        msg.setWindowTitle("Confirmar cierre de caja")
        msg.setText(
            "¿Desea proceder con el arqueo y cerrar la caja?\nLos cambios serán guardados."
        )
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        if tema == "dark":
            msg.setStyleSheet("background-color: #2D3436; color: white;")

        respuesta = msg.exec_()
        if respuesta == QMessageBox.Yes:
            cerrar_caja(date.today())  # aquí pasas la fecha que necesites
            QMessageBox.information(pagina, "Éxito", "Caja cerrada correctamente.")

    btn_cerrar_caja.clicked.connect(confirmar_cierre)

    layout.addWidget(btn_cerrar_caja, alignment=Qt.AlignRight)

    return pagina
