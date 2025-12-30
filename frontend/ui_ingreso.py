import sqlite3
import json
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QMessageBox,
    QStackedWidget,
    QSizePolicy,
    QInputDialog,
    QMenu,
    QDialog,
    QTableWidget,
    QTableWidgetItem,
)
from PyQt5.QtCore import Qt
from backend.logica.marcas import (
    obtener_marcas,
    agregar_nueva_marca,
    editar_marca,
    eliminar_marca,
    obtener_historial_auditoria,
)
from backend.logica.ventas import verificacion_encargado_local


def obtener_info_producto(codigo):
    try:
        conn = sqlite3.connect("reuso.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT nombre, stock, precio FROM productos WHERE codigo = ?", (codigo,)
        )
        row = cursor.fetchone()
        conn.close()
        return row
    except Exception as e:
        print(f"Error BD: {e}")
        return None


def agregar_stock_bd(codigo, cantidad):
    try:
        conn = sqlite3.connect("reuso.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT nombre, stock FROM productos WHERE codigo = ?", (codigo,)
        )
        row = cursor.fetchone()
        if row:
            nombre, stock_actual = row
            nuevo_stock = stock_actual + cantidad
            cursor.execute(
                "UPDATE productos SET stock = ? WHERE codigo = ?", (nuevo_stock, codigo)
            )
            conn.commit()
            conn.close()
            return True, nombre, stock_actual, nuevo_stock
        conn.close()
        return False, "Producto no encontrado", 0, 0
    except Exception as e:
        return False, str(e), 0, 0


def obtener_resumen_marca(marca):
    try:
        conn = sqlite3.connect("reuso.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT stock, precio FROM productos WHERE nombre LIKE ?", (f"%{marca}%",)
        )
        rows = cursor.fetchall()
        conn.close()

        total_stock = sum(row[0] for row in rows if row[0] is not None)
        total_valor = sum(
            (row[0] * row[1])
            for row in rows
            if row[0] is not None and row[1] is not None
        )
        return total_stock, total_valor
    except Exception as e:
        print(f"Error resumen marca: {e}")
        return 0, 0


class VentanaAuditoria(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Historial de Auditoría")
        self.resize(900, 600)

        # Detectar tema
        tema = "dark"
        try:
            with open("config.json", "r") as f:
                data = json.load(f)
                tema = data.get("tema", "dark")
        except:
            pass

        # Estilos según tema
        if tema == "dark":
            self.setStyleSheet(
                """
                QDialog { background-color: #2D3436; color: white; }
                QLabel { color: white; }
                QTableWidget { background-color: #2D3436; alternate-background-color: #353b48; color: white; gridline-color: #636e72; border: 1px solid #636e72; }
                QHeaderView::section { background-color: #2D3436; color: white; border: 1px solid #636e72; padding: 4px; }
                QTableWidget::item:selected { background-color: #F4D03F; color: black; }
            """
            )
        else:
            self.setStyleSheet(
                """
                QDialog { background-color: white; color: black; }
                QLabel { color: #2D3436; }
                QTableWidget { background-color: white; color: black; gridline-color: #dfe6e9; }
                QHeaderView::section { background-color: #dfe6e9; padding: 4px; border: none; font-weight: bold; color: black; }
            """
            )

        layout = QVBoxLayout(self)

        # Cabecera con título y botón eliminar
        header_layout = QHBoxLayout()

        lbl_titulo = QLabel("Registro de Cambios y Eliminaciones")
        lbl_titulo.setStyleSheet(
            "font-size: 18px; font-weight: bold; margin-bottom: 10px;"
        )
        header_layout.addWidget(lbl_titulo)
        header_layout.addStretch()

        btn_eliminar = QPushButton("🗑 Eliminar Historial")
        btn_eliminar.setCursor(Qt.PointingHandCursor)
        btn_eliminar.setStyleSheet(
            "background-color: #ff7675; color: white; font-weight: bold; padding: 8px 15px; border-radius: 6px; border: none;"
        )
        btn_eliminar.clicked.connect(self.eliminar_historial)
        header_layout.addWidget(btn_eliminar)

        layout.addLayout(header_layout)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["Fecha", "Acción", "Detalle"])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.setAlternatingRowColors(True)

        layout.addWidget(self.tabla)
        self.cargar_datos()

    def cargar_datos(self):
        datos = obtener_historial_auditoria()
        self.tabla.setRowCount(len(datos))

        for i, (fecha, accion, detalle) in enumerate(datos):
            self.tabla.setItem(i, 0, QTableWidgetItem(str(fecha)))
            self.tabla.setItem(i, 1, QTableWidgetItem(str(accion)))
            self.tabla.setItem(i, 2, QTableWidgetItem(str(detalle)))

    def eliminar_historial(self):
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            "¿Estás seguro de que deseas eliminar todo el historial de auditoría?\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            pwd, ok = QInputDialog.getText(
                self,
                "Autorización requerida",
                "Ingrese contraseña de administrador:",
                QLineEdit.Password,
            )
            if not ok or not pwd:
                return

            if verificacion_encargado_local(pwd) not in (1, 3):
                QMessageBox.warning(
                    self,
                    "Acceso denegado",
                    "Contraseña incorrecta o permisos insuficientes.",
                )
                return

            try:
                conn = sqlite3.connect("reuso.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM auditoria")
                conn.commit()
                conn.close()
                self.cargar_datos()

                # Guardar registro en log separado
                try:
                    with open("log_eliminaciones.txt", "a", encoding="utf-8") as f:
                        f.write(
                            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] El administrador '{pwd}' eliminó el historial de auditoría.\n"
                        )
                except Exception as e:
                    print(f"Error al escribir en log: {e}")

                QMessageBox.information(
                    self, "Éxito", "El historial ha sido eliminado correctamente."
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"No se pudo eliminar el historial: {e}"
                )


def crear_pagina_ingreso():
    pagina = QWidget()
    layout = QVBoxLayout(pagina)
    layout.setContentsMargins(40, 40, 40, 40)
    layout.setSpacing(20)
    layout.setAlignment(Qt.AlignTop)

    # Botón Volver
    btn_volver = QPushButton("⬅ Volver al Menú")
    btn_volver.setCursor(Qt.PointingHandCursor)
    btn_volver.setFixedWidth(160)
    btn_volver.setStyleSheet(
        "background-color: #2D3436; color: white; border-radius: 5px; padding: 8px; font-weight: bold;"
    )
    layout.addWidget(btn_volver, alignment=Qt.AlignLeft)
    pagina.btn_volver = btn_volver

    # Stack para manejar las vistas (Marcas -> Ingreso)
    stack = QStackedWidget()
    layout.addWidget(stack)

    # ==========================================
    # PÁGINA 1: SELECCIÓN DE MARCA
    # ==========================================
    page_marcas = QWidget()
    layout_marcas = QVBoxLayout(page_marcas)
    layout_marcas.setAlignment(Qt.AlignTop)

    # Cabecera con título y botón de agregar
    header_marcas = QHBoxLayout()

    lbl_titulo_marcas = QLabel("Seleccione la Marca")
    lbl_titulo_marcas.setStyleSheet("font-size: 24px; font-weight: bold;")

    lbl_hint = QLabel("(Clic derecho para editar/eliminar)")
    lbl_hint.setObjectName("mensajeInferior")
    lbl_hint.setAlignment(Qt.AlignCenter)

    btn_historial = QPushButton("📜 Historial")
    btn_historial.setCursor(Qt.PointingHandCursor)
    btn_historial.setStyleSheet(
        """
        QPushButton { background-color: #636e72; color: white; font-weight: bold; padding: 8px 15px; border-radius: 6px; }
        QPushButton:hover { background-color: #2D3436; }
    """
    )
    btn_historial.clicked.connect(lambda: VentanaAuditoria(pagina).exec_())

    btn_nueva_marca = QPushButton("➕ Nueva Marca")
    btn_nueva_marca.setCursor(Qt.PointingHandCursor)
    btn_nueva_marca.setStyleSheet(
        """
        QPushButton {
            background-color: #0984e3;
            color: white;
            font-weight: bold;
            padding: 8px 15px;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #74b9ff;
        }
    """
    )

    header_marcas.addStretch()
    header_marcas.addWidget(lbl_titulo_marcas)
    header_marcas.addStretch()
    header_marcas.addWidget(btn_historial)
    header_marcas.addWidget(btn_nueva_marca)

    layout_marcas.addLayout(header_marcas)
    layout_marcas.addSpacing(20)

    grid_marcas = QGridLayout()
    grid_marcas.setSpacing(20)
    # Configurar para que las celdas se expandan uniformemente
    for i in range(3):
        grid_marcas.setRowStretch(i, 1)
        grid_marcas.setColumnStretch(i, 1)

    # Variable para guardar estado
    marca_seleccionada = {"nombre": ""}

    def ir_a_ingreso(nombre_marca):
        marca_seleccionada["nombre"] = nombre_marca
        lbl_marca_actual.setText(f"Marca: {nombre_marca}")

        stock, valor = obtener_resumen_marca(nombre_marca)
        lbl_resumen_stock.setText(f"Total Prendas: {stock}")
        lbl_resumen_valor.setText(f"Valor Total: ${valor:,}")

        stack.setCurrentIndex(1)
        input_codigo.setFocus()

    def mostrar_menu_contextual(pos, marca, btn):
        menu = QMenu(btn)
        action_editar = menu.addAction("Editar")
        action_eliminar = menu.addAction("Eliminar")

        action = menu.exec_(btn.mapToGlobal(pos))

        if action == action_editar:
            nuevo_nombre, ok = QInputDialog.getText(
                pagina, "Editar Marca", "Nuevo nombre:", text=marca
            )
            if ok and nuevo_nombre.strip():
                nuevo_nombre = nuevo_nombre.strip()
                if editar_marca(marca, nuevo_nombre):
                    QMessageBox.information(pagina, "Éxito", "Marca actualizada.")
                    cargar_marcas()
                else:
                    QMessageBox.warning(
                        pagina,
                        "Error",
                        "No se pudo actualizar (posiblemente ya existe).",
                    )

        elif action == action_eliminar:
            # Cuadro de diálogo personalizado
            msg = QMessageBox(pagina)
            msg.setWindowTitle("Eliminar Marca")
            msg.setText(f"¿Deseas eliminar la marca '{marca}'?")
            msg.setInformativeText(
                "Elige qué hacer con los productos asociados a esta marca:"
            )
            msg.setIcon(QMessageBox.Question)

            # Botones con roles específicos
            btn_conservar = msg.addButton("Conservar productos", QMessageBox.ActionRole)
            btn_eliminar_todo = msg.addButton(
                "Eliminar marca y productos", QMessageBox.DestructiveRole
            )
            btn_cancelar = msg.addButton("Cancelar", QMessageBox.RejectRole)

            msg.exec_()

            if msg.clickedButton() != btn_cancelar:
                if msg.clickedButton() == btn_eliminar_todo:
                    # Segunda confirmación de seguridad
                    segunda_conf = QMessageBox.warning(
                        pagina,
                        "⚠️ Acción Irreversible",
                        f"¡Atención!\nEstás a punto de eliminar la marca '{marca}' y TODOS sus productos del inventario.\n\n¿Estás absolutamente seguro?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No,
                    )
                    if segunda_conf != QMessageBox.Yes:
                        return

                eliminar_prods = msg.clickedButton() == btn_eliminar_todo
                if eliminar_marca(marca, eliminar_productos=eliminar_prods):
                    cargar_marcas()
                else:
                    QMessageBox.warning(
                        pagina, "Error", "No se pudo eliminar la marca."
                    )

    def cargar_marcas():
        # Limpiar grid
        while grid_marcas.count():
            item = grid_marcas.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        marcas = obtener_marcas()

        row, col = 0, 0
        for marca in marcas:
            btn = QPushButton(marca)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.setMinimumHeight(150)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(
                """
                QPushButton {
                    background-color: white;
                    color: #2D3436;
                    font-size: 24px;
                    font-weight: bold;
                    border-radius: 15px;
                    border: 1px solid #dfe6e9;
                }
                QPushButton:hover {
                    background-color: #f1f2f6;
                    border: 2px solid #0984e3;
                    color: #0984e3;
                }
            """
            )
            btn.clicked.connect(lambda _, m=marca: ir_a_ingreso(m))
            btn.setContextMenuPolicy(Qt.CustomContextMenu)
            btn.customContextMenuRequested.connect(
                lambda pos, m=marca, b=btn: mostrar_menu_contextual(pos, m, b)
            )
            grid_marcas.addWidget(btn, row, col)
            col += 1
            if col > 2:  # 3 columnas
                col = 0
                row += 1

    def solicitar_nueva_marca():
        nombre, ok = QInputDialog.getText(
            pagina, "Nueva Marca", "Ingrese el nombre de la nueva marca:"
        )
        if ok and nombre.strip():
            nombre = nombre.strip()
            if agregar_nueva_marca(nombre):
                QMessageBox.information(
                    pagina, "Éxito", f"Marca '{nombre}' agregada correctamente."
                )
                cargar_marcas()
            else:
                QMessageBox.warning(
                    pagina,
                    "Error",
                    "No se pudo agregar la marca (posiblemente ya existe).",
                )

    btn_nueva_marca.clicked.connect(solicitar_nueva_marca)

    # Cargar inicialmente
    cargar_marcas()

    layout_marcas.addLayout(grid_marcas)
    layout_marcas.addStretch()
    layout_marcas.addWidget(lbl_hint)
    stack.addWidget(page_marcas)

    # ==========================================
    # PÁGINA 2: FORMULARIO DE INGRESO
    # ==========================================
    page_ingreso = QWidget()
    layout_ingreso = QVBoxLayout(page_ingreso)
    layout_ingreso.setAlignment(Qt.AlignTop)

    # Botón para cambiar marca
    btn_cambiar = QPushButton("⬅ Cambiar Marca")
    btn_cambiar.setCursor(Qt.PointingHandCursor)
    btn_cambiar.setStyleSheet(
        "color: #0984e3; font-weight: bold; border: none; text-align: left;"
    )
    btn_cambiar.clicked.connect(lambda: stack.setCurrentIndex(0))
    layout_ingreso.addWidget(btn_cambiar, alignment=Qt.AlignLeft)

    # Título
    titulo = QLabel("Ingreso de Mercadería")
    titulo.setStyleSheet("font-size: 24px; font-weight: bold;")
    titulo.setAlignment(Qt.AlignCenter)
    layout_ingreso.addWidget(titulo)

    lbl_marca_actual = QLabel("Marca: -")
    lbl_marca_actual.setStyleSheet("font-size: 18px; font-weight: bold;")
    lbl_marca_actual.setAlignment(Qt.AlignCenter)
    layout_ingreso.addWidget(lbl_marca_actual)

    # Resumen de la marca
    resumen_layout = QHBoxLayout()
    resumen_layout.setAlignment(Qt.AlignCenter)

    lbl_resumen_stock = QLabel("Total Prendas: 0")
    lbl_resumen_stock.setStyleSheet(
        "font-size: 16px; color: #2D3436; margin-right: 20px;"
    )

    lbl_resumen_valor = QLabel("Valor Total: $0")
    lbl_resumen_valor.setStyleSheet(
        "font-size: 16px; color: #2D3436; font-weight: bold;"
    )

    resumen_layout.addWidget(lbl_resumen_stock)
    resumen_layout.addWidget(lbl_resumen_valor)
    layout_ingreso.addLayout(resumen_layout)

    layout_ingreso.addSpacing(20)

    # Tarjeta contenedora
    card = QFrame()
    card.setStyleSheet(
        "background-color: rgba(255,255,255,0.9); border-radius: 12px; padding: 20px;"
    )
    card_layout = QVBoxLayout(card)
    card_layout.setSpacing(15)

    # Buscador
    lbl_buscar = QLabel("Código del Producto:")
    lbl_buscar.setStyleSheet("font-size: 16px; font-weight: bold; color: #2D3436;")
    card_layout.addWidget(lbl_buscar)

    input_codigo = QLineEdit()
    input_codigo.setPlaceholderText("Escanee o ingrese código...")
    input_codigo.setStyleSheet(
        "padding: 8px; font-size: 14px; border: 1px solid #BDBDBD; border-radius: 6px;"
    )
    card_layout.addWidget(input_codigo)

    btn_buscar = QPushButton("Buscar")
    btn_buscar.setCursor(Qt.PointingHandCursor)
    btn_buscar.setStyleSheet(
        "background-color: #0984e3; color: white; padding: 8px; border-radius: 6px; font-weight: bold;"
    )
    card_layout.addWidget(btn_buscar)

    # Info del producto (oculto al inicio)
    info_frame = QFrame()
    info_frame.setVisible(False)
    info_layout = QVBoxLayout(info_frame)
    info_layout.setSpacing(10)

    lbl_nombre = QLabel("Producto: -")
    lbl_nombre.setStyleSheet("font-size: 18px; font-weight: bold; color: #2D3436;")
    lbl_stock = QLabel("Stock Actual: -")
    lbl_stock.setStyleSheet("font-size: 16px; color: #636e72;")
    lbl_precio = QLabel("Precio Actual: -")
    lbl_precio.setStyleSheet("font-size: 16px; color: #636e72;")

    info_layout.addWidget(lbl_nombre)
    info_layout.addWidget(lbl_stock)
    info_layout.addWidget(lbl_precio)

    lbl_cantidad = QLabel("Cantidad a ingresar:")
    lbl_cantidad.setStyleSheet(
        "font-size: 16px; font-weight: bold; margin-top: 10px; color: #2D3436;"
    )
    input_cantidad = QLineEdit()
    input_cantidad.setPlaceholderText("Ej: 10")
    input_cantidad.setStyleSheet(
        "padding: 8px; font-size: 14px; border: 1px solid #BDBDBD; border-radius: 6px;"
    )

    btn_confirmar = QPushButton("Confirmar Ingreso")
    btn_confirmar.setCursor(Qt.PointingHandCursor)
    btn_confirmar.setStyleSheet(
        "background-color: #27AE60; color: white; padding: 10px; border-radius: 6px; font-weight: bold; font-size: 16px;"
    )

    info_layout.addWidget(lbl_cantidad)
    info_layout.addWidget(input_cantidad)
    info_layout.addWidget(btn_confirmar)

    card_layout.addWidget(info_frame)
    layout_ingreso.addWidget(card)
    layout_ingreso.addStretch()
    stack.addWidget(page_ingreso)

    # --- Lógica ---
    def buscar():
        codigo = input_codigo.text().strip()
        if not codigo:
            return

        datos = obtener_info_producto(codigo)
        if datos:
            nombre, stock, precio = datos
            lbl_nombre.setText(f"Producto: {nombre}")
            lbl_stock.setText(f"Stock Actual: {stock}")
            lbl_precio.setText(f"Precio Actual: ${precio}")
            info_frame.setVisible(True)
            input_cantidad.clear()
            input_cantidad.setFocus()
        else:
            QMessageBox.warning(pagina, "No encontrado", "El producto no existe.")
            info_frame.setVisible(False)

    def confirmar():
        codigo = input_codigo.text().strip()
        cant_txt = input_cantidad.text().strip()
        if not cant_txt.isdigit() or int(cant_txt) <= 0:
            QMessageBox.warning(pagina, "Error", "Cantidad inválida.")
            return

        cantidad = int(cant_txt)
        ok, nombre, stock_ant, stock_new = agregar_stock_bd(codigo, cantidad)
        if ok:
            QMessageBox.information(
                pagina,
                "Éxito",
                f"Stock actualizado en {marca_seleccionada['nombre']}.\n{nombre}: {stock_ant} -> {stock_new}",
            )
            input_codigo.clear()
            input_cantidad.clear()
            info_frame.setVisible(False)
            input_codigo.setFocus()
        else:
            QMessageBox.critical(pagina, "Error", f"Error al actualizar: {nombre}")

    btn_buscar.clicked.connect(buscar)
    input_codigo.returnPressed.connect(buscar)
    btn_confirmar.clicked.connect(confirmar)
    input_cantidad.returnPressed.connect(confirmar)

    return pagina
