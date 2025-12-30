import sqlite3
import shutil
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLineEdit,
    QSplitter,
    QFrame,
    QMessageBox,
    QDialog,
    QDateEdit,
    QCheckBox,
    QInputDialog,
)
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QPixmap, QTransform, QTextDocument
from PyQt5.QtCore import Qt, QUrl, QDate
from backend.logica.ventas import verificacion_encargado_local


def buscar_productos_db(filtro=""):
    try:
        with sqlite3.connect("reuso.db") as conn:
            cursor = conn.cursor()
            if filtro:
                f = f"%{filtro}%"
                cursor.execute(
                    "SELECT codigo, nombre, stock, precio FROM productos WHERE nombre LIKE ? OR codigo LIKE ?",
                    (f, f),
                )
                return cursor.fetchall()
            return []
    except Exception as e:
        print(f"Error DB: {e}")
        return []


def init_db_facturas():
    os.makedirs("facturas_img", exist_ok=True)
    with sqlite3.connect("reuso.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS facturas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                ruta TEXT
            )
        """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS factura_productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                factura_id INTEGER,
                producto_codigo TEXT,
                FOREIGN KEY(factura_id) REFERENCES facturas(id)
            )
        """
        )
        conn.commit()


def guardar_factura_sistema(ruta_origen, productos_asociados=None):
    try:
        if not os.path.exists(ruta_origen):
            return False

        nombre_archivo = os.path.basename(ruta_origen)
        fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        nuevo_nombre = f"{fecha_str}_{nombre_archivo}"
        destino = os.path.join("facturas_img", nuevo_nombre)

        shutil.copy2(ruta_origen, destino)

        with sqlite3.connect("reuso.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO facturas (fecha, ruta) VALUES (?, ?)",
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), destino),
            )
            factura_id = cursor.lastrowid

            if productos_asociados:
                data = [(factura_id, codigo) for codigo in productos_asociados]
                cursor.executemany(
                    "INSERT INTO factura_productos (factura_id, producto_codigo) VALUES (?, ?)",
                    data,
                )

            conn.commit()
        return True
    except Exception as e:
        print(f"Error guardando factura: {e}")
        return False


def eliminar_factura_sistema(factura_id):
    try:
        with sqlite3.connect("reuso.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ruta FROM facturas WHERE id = ?", (factura_id,))
            row = cursor.fetchone()
            if row:
                ruta = row[0]
                if os.path.exists(ruta):
                    try:
                        os.remove(ruta)
                    except:
                        pass
            cursor.execute(
                "DELETE FROM factura_productos WHERE factura_id = ?", (factura_id,)
            )
            cursor.execute("DELETE FROM facturas WHERE id = ?", (factura_id,))
            conn.commit()
        return True
    except Exception as e:
        print(f"Error eliminando factura: {e}")
        return False


def obtener_historial_facturas(fecha_filtro=None):
    with sqlite3.connect("reuso.db") as conn:
        cursor = conn.cursor()
        query = "SELECT id, fecha, ruta FROM facturas"
        params = []

        if fecha_filtro:
            # Se asume formato YYYY-MM-DD en la base de datos (datetime)
            query += " WHERE date(fecha) = ?"
            params.append(fecha_filtro)

        query += " ORDER BY id DESC"
        cursor.execute(query, params)
        return cursor.fetchall()


def obtener_productos_factura(factura_id):
    with sqlite3.connect("reuso.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT fp.producto_codigo, p.nombre 
            FROM factura_productos fp
            LEFT JOIN productos p ON fp.producto_codigo = p.codigo
            WHERE fp.factura_id = ?
        """,
            (factura_id,),
        )
        return cursor.fetchall()


class DropLabel(QLabel):
    def __init__(self, parent=None, on_drop_callback=None):
        super().__init__(parent)
        self.on_drop_callback = on_drop_callback
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setText("Arrastra tu factura aquí\no usa el botón 'Subir Foto'")
        self.setStyleSheet(
            "color: #636e72; font-size: 16px; border: 2px dashed #b2bec3; border-radius: 8px; background-color: #f5f6fa;"
        )

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            # Tomamos el primer archivo
            if self.on_drop_callback:
                self.on_drop_callback(files[0])


class VentanaHistorialFacturas(QDialog):
    def __init__(self, parent=None, callback_ver=None):
        super().__init__(parent)
        self.setWindowTitle("Historial de Facturas")
        self.resize(800, 500)
        self.callback_ver = callback_ver
        layout = QVBoxLayout(self)

        # --- Filtros ---
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filtrar por Fecha:"))

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        filter_layout.addWidget(self.date_edit)

        self.chk_filtrar = QCheckBox("Activar Filtro")
        filter_layout.addWidget(self.chk_filtrar)

        btn_refresh = QPushButton("🔄 Actualizar")
        btn_refresh.clicked.connect(self.cargar_datos)
        filter_layout.addWidget(btn_refresh)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(
            ["ID", "Fecha de Carga", "Productos", "Ver", "Eliminar"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabla)

        self.cargar_datos()

    def cargar_datos(self):
        fecha = None
        if self.chk_filtrar.isChecked():
            fecha = self.date_edit.date().toString("yyyy-MM-dd")

        facturas = obtener_historial_facturas(fecha)
        self.tabla.setRowCount(len(facturas))
        for i, (fid, fecha, ruta) in enumerate(facturas):
            self.tabla.setItem(i, 0, QTableWidgetItem(str(fid)))
            self.tabla.setItem(i, 1, QTableWidgetItem(str(fecha)))

            # Botón Ver Productos
            btn_prods = QPushButton("📦 Ver/Imprimir")
            btn_prods.setCursor(Qt.PointingHandCursor)
            btn_prods.clicked.connect(lambda _, f=fid: self.ver_productos(f))
            self.tabla.setCellWidget(i, 2, btn_prods)

            # Botón Ver Factura
            btn_ver = QPushButton("👁️ Ver Factura")
            btn_ver.setCursor(Qt.PointingHandCursor)
            btn_ver.clicked.connect(
                lambda _, r=ruta: [self.callback_ver(r), self.accept()]
            )
            self.tabla.setCellWidget(i, 3, btn_ver)

            # Botón Eliminar
            btn_del = QPushButton("🗑")
            btn_del.setCursor(Qt.PointingHandCursor)
            btn_del.setStyleSheet(
                "background-color: #ff7675; color: white; font-weight: bold; border-radius: 4px;"
            )
            btn_del.clicked.connect(lambda _, f=fid: self.eliminar_factura(f))
            self.tabla.setCellWidget(i, 4, btn_del)

    def eliminar_factura(self, factura_id):
        pwd, ok = QInputDialog.getText(
            self,
            "Autorización Requerida",
            "Ingrese contraseña de administrador:",
            QLineEdit.Password,
        )
        if ok and pwd:
            if verificacion_encargado_local(pwd) in (1, 3):
                resp = QMessageBox.question(
                    self,
                    "Confirmar",
                    "¿Estás seguro de eliminar esta factura y su archivo?",
                    QMessageBox.Yes | QMessageBox.No,
                )
                if resp == QMessageBox.Yes:
                    if eliminar_factura_sistema(factura_id):
                        QMessageBox.information(self, "Éxito", "Factura eliminada.")
                        self.cargar_datos()
                    else:
                        QMessageBox.critical(
                            self, "Error", "No se pudo eliminar la factura."
                        )
            else:
                QMessageBox.warning(
                    self,
                    "Acceso Denegado",
                    "Contraseña incorrecta o permisos insuficientes.",
                )

    def ver_productos(self, factura_id):
        productos = obtener_productos_factura(factura_id)
        if not productos:
            QMessageBox.information(
                self, "Sin productos", "Esta factura no tiene productos asociados."
            )
            return

        html = "<h3>Productos asociados a la factura #{}</h3><ul>".format(factura_id)
        for codigo, nombre in productos:
            nom_str = nombre if nombre else "(Producto no encontrado)"
            html += f"<li><b>{codigo}</b>: {nom_str}</li>"
        html += "</ul>"

        # Diálogo personalizado para mostrar y permitir imprimir
        d = QDialog(self)
        d.setWindowTitle("Productos Asociados")
        d.resize(400, 300)
        l = QVBoxLayout(d)

        lbl = QLabel(html)
        lbl.setWordWrap(True)
        l.addWidget(lbl)

        btn_print = QPushButton("🖨️ Imprimir Lista")
        btn_print.clicked.connect(lambda: self.imprimir_lista(html))
        l.addWidget(btn_print)

        d.exec_()

    def imprimir_lista(self, html):
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            doc = QTextDocument()
            doc.setHtml(html)
            doc.print_(printer)


def crear_pagina_facturas():
    init_db_facturas()
    pagina = QWidget()
    layout = QVBoxLayout(pagina)
    layout.setContentsMargins(20, 20, 20, 20)

    # Botón Volver
    btn_volver = QPushButton("⬅ Volver al Menú")
    btn_volver.setCursor(Qt.PointingHandCursor)
    btn_volver.setFixedWidth(160)
    btn_volver.setStyleSheet(
        "background-color: #2D3436; color: white; border-radius: 5px; padding: 8px; font-weight: bold;"
    )
    layout.addWidget(btn_volver, alignment=Qt.AlignLeft)
    pagina.btn_volver = btn_volver

    # Splitter para dividir la pantalla (Izquierda: Factura, Derecha: Verificación)
    splitter = QSplitter(Qt.Horizontal)
    splitter.setHandleWidth(10)

    # --- LADO IZQUIERDO: VISUALIZADOR DE FACTURA ---
    left_frame = QFrame()
    left_frame.setStyleSheet("background-color: #dfe6e9; border-radius: 8px;")
    left_layout = QVBoxLayout(left_frame)

    lbl_titulo_img = QLabel("📄 Visualizador de Factura")
    lbl_titulo_img.setStyleSheet(
        "font-size: 18px; font-weight: bold; color: #2D3436; margin-bottom: 5px;"
    )

    # Botonera superior izquierda
    top_btns_layout = QHBoxLayout()

    btn_cargar = QPushButton("📂 Subir Foto de Factura")
    btn_cargar.setCursor(Qt.PointingHandCursor)
    btn_cargar.setStyleSheet(
        """
        QPushButton {
            background-color: #0984e3; 
            color: white; 
            font-weight: bold; 
            padding: 10px;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #74b9ff;
        }
    """
    )

    btn_historial = QPushButton("📜 Historial")
    btn_historial.setCursor(Qt.PointingHandCursor)
    btn_historial.setStyleSheet(
        """
        QPushButton {
            background-color: #636e72; 
            color: white; 
            font-weight: bold; 
            padding: 10px;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #2D3436;
        }
    """
    )
    top_btns_layout.addWidget(btn_cargar)
    top_btns_layout.addWidget(btn_historial)

    # Controles de imagen (Zoom y Rotación)
    controls_layout = QHBoxLayout()
    btn_zoom_in = QPushButton("➕ Acercar")
    btn_zoom_out = QPushButton("➖ Alejar")
    btn_rotate = QPushButton("🔄 Rotar 90°")
    btn_guardar = QPushButton("💾 Guardar en Sistema")

    for btn in [btn_zoom_in, btn_zoom_out, btn_rotate, btn_guardar]:
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(
            "background-color: #b2bec3; color: #2D3436; border-radius: 4px; padding: 6px; font-weight: bold;"
        )
        controls_layout.addWidget(btn)

    # Estilo específico para guardar
    btn_guardar.setStyleSheet(
        "background-color: #00b894; color: white; border-radius: 4px; padding: 6px; font-weight: bold;"
    )

    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setStyleSheet(
        "background-color: white; border: 1px solid #b2bec3; border-radius: 4px;"
    )

    # Usamos DropLabel en lugar de QLabel normal
    lbl_imagen = DropLabel()
    scroll_area.setWidget(lbl_imagen)

    left_layout.addWidget(lbl_titulo_img)
    left_layout.addLayout(top_btns_layout)
    left_layout.addLayout(controls_layout)
    left_layout.addWidget(scroll_area)

    # --- LADO DERECHO: VERIFICADOR DE MERCADERÍA ---
    right_frame = QFrame()
    right_frame.setStyleSheet(
        "background-color: white; border-radius: 8px; border: 1px solid #dfe6e9;"
    )
    right_layout = QVBoxLayout(right_frame)
    right_layout.setContentsMargins(15, 15, 15, 15)

    lbl_titulo_check = QLabel("🔍 Verificar Ingreso de Mercadería")
    lbl_titulo_check.setStyleSheet(
        "font-size: 18px; font-weight: bold; color: #2D3436; margin-bottom: 10px;"
    )

    search_layout = QHBoxLayout()
    input_busqueda = QLineEdit()
    input_busqueda.setPlaceholderText("Buscar producto por nombre o código...")
    input_busqueda.setStyleSheet(
        "padding: 10px; border: 1px solid #b2bec3; border-radius: 6px; font-size: 14px;"
    )

    btn_buscar = QPushButton("Buscar")
    btn_buscar.setCursor(Qt.PointingHandCursor)
    btn_buscar.setStyleSheet(
        """
        QPushButton {
            background-color: #00b894; 
            color: white; 
            font-weight: bold; 
            padding: 10px 20px;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #55efc4;
        }
    """
    )

    search_layout.addWidget(input_busqueda)
    search_layout.addWidget(btn_buscar)

    tabla = QTableWidget()
    tabla.setColumnCount(5)
    tabla.setHorizontalHeaderLabels(
        ["Asociar", "Código", "Producto", "Stock", "Precio"]
    )
    tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    tabla.setAlternatingRowColors(True)
    tabla.setStyleSheet(
        """
        QTableWidget {
            gridline-color: #dfe6e9;
            font-size: 14px;
        }
        QHeaderView::section {
            background-color: #f1f2f6;
            padding: 6px;
            border: none;
            font-weight: bold;
            color: #2D3436;
        }
    """
    )

    right_layout.addWidget(lbl_titulo_check)
    right_layout.addLayout(search_layout)
    right_layout.addWidget(tabla)

    splitter.addWidget(left_frame)
    splitter.addWidget(right_frame)
    splitter.setStretchFactor(0, 1)
    splitter.setStretchFactor(1, 1)

    layout.addWidget(splitter)

    # --- LÓGICA ---
    state = {"pixmap": None, "scale": 1.0, "angle": 0, "current_path": None}

    def actualizar_vista():
        if state["pixmap"] is None:
            return

        # Rotar
        transform = QTransform().rotate(state["angle"])
        rotated_pixmap = state["pixmap"].transformed(transform, Qt.SmoothTransformation)

        # Escalar
        w = int(rotated_pixmap.width() * state["scale"])
        h = int(rotated_pixmap.height() * state["scale"])

        if w > 0 and h > 0:
            scaled_pixmap = rotated_pixmap.scaled(
                w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            lbl_imagen.setPixmap(scaled_pixmap)
            lbl_imagen.adjustSize()

    def modificar_zoom(factor):
        state["scale"] *= factor
        actualizar_vista()

    def rotar_imagen():
        state["angle"] = (state["angle"] + 90) % 360
        actualizar_vista()

    def cargar_imagen_desde_ruta(path):
        if not path:
            return

        pixmap = QPixmap(path)
        if pixmap.isNull():
            QMessageBox.warning(
                pagina, "Error", "No se pudo cargar la imagen seleccionada."
            )
            return

        # Escalar si es muy grande para mejorar rendimiento, manteniendo aspecto
        if pixmap.width() > 1200:
            pixmap = pixmap.scaledToWidth(1200, Qt.SmoothTransformation)

        state["pixmap"] = pixmap
        state["scale"] = 1.0
        state["angle"] = 0
        state["current_path"] = path
        actualizar_vista()

    def cargar_factura_dialogo():
        path, _ = QFileDialog.getOpenFileName(
            pagina,
            "Seleccionar Factura",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.pdf)",
        )
        if path:
            cargar_imagen_desde_ruta(path)

    def guardar_factura_actual():
        if not state["current_path"]:
            QMessageBox.warning(
                pagina, "Atención", "No hay ninguna factura cargada para guardar."
            )
            return

        productos_seleccionados = []
        for i in range(tabla.rowCount()):
            item = tabla.item(i, 0)
            if item.checkState() == Qt.Checked:
                # El código está en la columna 1
                codigo = tabla.item(i, 1).text()
                productos_seleccionados.append(codigo)

        if guardar_factura_sistema(state["current_path"], productos_seleccionados):
            QMessageBox.information(
                pagina, "Éxito", "Factura guardada en el sistema correctamente."
            )
        else:
            QMessageBox.critical(pagina, "Error", "No se pudo guardar la factura.")

    def abrir_historial():
        dialog = VentanaHistorialFacturas(pagina, callback_ver=cargar_imagen_desde_ruta)
        dialog.exec_()

    def buscar_mercaderia():
        texto = input_busqueda.text().strip()
        if not texto:
            return

        productos = buscar_productos_db(texto)
        tabla.setRowCount(len(productos))
        for i, (cod, nom, stock, precio) in enumerate(productos):
            # Checkbox para asociar
            item_check = QTableWidgetItem()
            item_check.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item_check.setCheckState(Qt.Unchecked)
            tabla.setItem(i, 0, item_check)

            tabla.setItem(i, 1, QTableWidgetItem(str(cod)))
            tabla.setItem(i, 2, QTableWidgetItem(str(nom)))
            tabla.setItem(i, 3, QTableWidgetItem(str(stock)))
            tabla.setItem(i, 4, QTableWidgetItem(f"${precio}"))

        if not productos:
            QMessageBox.information(
                pagina,
                "Sin resultados",
                "No se encontraron productos con ese criterio.",
            )

    # Conectar callback del DropLabel
    lbl_imagen.on_drop_callback = cargar_imagen_desde_ruta

    btn_cargar.clicked.connect(cargar_factura_dialogo)
    btn_buscar.clicked.connect(buscar_mercaderia)
    btn_zoom_in.clicked.connect(lambda: modificar_zoom(1.2))
    btn_zoom_out.clicked.connect(lambda: modificar_zoom(0.8))
    btn_rotate.clicked.connect(rotar_imagen)
    btn_guardar.clicked.connect(guardar_factura_actual)
    btn_historial.clicked.connect(abrir_historial)
    input_busqueda.returnPressed.connect(buscar_mercaderia)

    return pagina
