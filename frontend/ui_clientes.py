import sqlite3
import json
from datetime import datetime
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
    QHeaderView,
    QFormLayout,
    QAbstractItemView,
    QMenu,
    QFileDialog,
    QInputDialog,
    QComboBox,
    QCheckBox,
)
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QTextDocument
from PyQt5.QtCore import Qt
from backend.logica.ventas import verificacion_encargado_local
from backend.db.conexion import conectar_mydb

# --- Base de Datos SQLite ---
def init_db():
    with sqlite3.connect("clientes.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                rut TEXT UNIQUE NOT NULL,
                telefono TEXT,
                direccion TEXT
            )
        """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS historial_credito (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rut_cliente TEXT NOT NULL,
                fecha TEXT,
                producto TEXT,
                total INTEGER,
                pie INTEGER,
                cuota1 TEXT DEFAULT 'Pendiente',
                cuota2 TEXT DEFAULT 'Pendiente',
                FOREIGN KEY(rut_cliente) REFERENCES clientes(rut)
            )
        """
        )
        conn.commit()


def guardar_cliente_db(nombre, rut, telefono, direccion):
    try:
        with sqlite3.connect("clientes.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO clientes (nombre, rut, telefono, direccion) VALUES (?, ?, ?, ?)",
                (nombre, rut, telefono, direccion),
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"Error BD: {e}")
        return False


def actualizar_cliente_db(rut, nombre, telefono, direccion):
    try:
        with sqlite3.connect("clientes.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE clientes SET nombre=?, telefono=?, direccion=? WHERE rut=?",
                (nombre, telefono, direccion, rut),
            )
            conn.commit()
        return True
    except Exception as e:
        print(f"Error actualizando cliente: {e}")
        return False


def contar_clientes_db(filtro="", solo_deudores=False):
    conn = conectar_mydb()
    cursor = conn.cursor()

    query = "SELECT COUNT(*) FROM cliente"
    params = []

    if filtro:
        query += " WHERE nombre LIKE %s OR rut LIKE %s"
        params.extend([f"%{filtro}%", f"%{filtro}%"])

    cursor.execute(query, params)
    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()
    return total



def obtener_clientes_paginados(pagina, por_pagina, filtro="", orden_col="nombre", orden_dir="ASC", solo_deudores=False):
    offset = (pagina - 1) * por_pagina
    conn = conectar_mydb()
    cursor = conn.cursor()

    query = "SELECT nombre, rut ||'-'|| digito_ver, celular, direccion FROM cliente"
    params = []

    if filtro:
        query += " WHERE nombre LIKE %s OR rut LIKE %s"
        params.extend([f"%{filtro}%", f"%{filtro}%"])

    query += f" ORDER BY {orden_col} {orden_dir} LIMIT %s OFFSET %s"
    params.extend([por_pagina, offset])

    cursor.execute(query, params)
    data = cursor.fetchall()

    cursor.close()
    conn.close()
    return data



def agregar_compra_db(rut, fecha, producto, total, pie):
    try:
        with sqlite3.connect("clientes.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO historial_credito (rut_cliente, fecha, producto, total, pie) VALUES (?, ?, ?, ?, ?)",
                (rut, fecha, producto, total, pie),
            )
            conn.commit()
        return True
    except Exception as e:
        print(f"Error BD Historial: {e}")
        return False


def actualizar_cuota_db(id_compra, columna, estado):
    try:
        with sqlite3.connect("clientes.db") as conn:
            cursor = conn.cursor()
            if columna not in ["cuota1", "cuota2"]:
                return False
            query = f"UPDATE historial_credito SET {columna} = ? WHERE id = ?"
            cursor.execute(query, (estado, id_compra))
            conn.commit()
        return True
    except Exception as e:
        print(f"Error actualizando cuota: {e}")
        return False


def eliminar_cliente_db(rut):
    try:
        with sqlite3.connect("clientes.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM historial_credito WHERE rut_cliente = ?", (rut,)
            )
            cursor.execute("DELETE FROM clientes WHERE rut = ?", (rut,))
            conn.commit()
        return True
    except Exception as e:
        print(f"Error eliminando cliente: {e}")
        return False


def obtener_historial_db(rut):
    with sqlite3.connect("clientes.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, fecha, producto, total, pie, cuota1, cuota2 FROM historial_credito WHERE rut_cliente = ? ORDER BY id DESC",
            (rut,),
        )
        return cursor.fetchall()


def obtener_compra_db(id_compra):
    with sqlite3.connect("clientes.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM historial_credito WHERE id = ?", (id_compra,))
        return cursor.fetchone()


def calcular_deuda_cliente(rut):
    historial = obtener_historial_db(rut)
    deuda = 0
    # historial: [(id, fecha, producto, total, pie, cuota1, cuota2), ...]
    for _, _, _, total, pie, c1, c2 in historial:
        saldo = total - pie
        valor_cuota = saldo / 2
        if c1 != "Pagada":
            deuda += valor_cuota
        if c2 != "Pagada":
            deuda += valor_cuota
    return int(deuda)


# --- Ventana para agregar nueva clienta ---
class VentanaAgregarClienta(QDialog):
    def __init__(self, parent=None, callback_agregar=None):
        super().__init__(parent)
        self.setWindowTitle("Ingresar Nueva Clienta - Crédito Girasol")
        self.setMinimumSize(400, 300)
        self.callback_agregar = callback_agregar

        # Detectar tema
        tema = "dark"
        try:
            with open("config.json", "r") as f:
                data = json.load(f)
                tema = data.get("tema", "dark")
        except:
            pass

        if tema == "dark":
            self.setStyleSheet(
                """
                QDialog { background-color: #2D3436; color: white; }
                QLabel { font-size: 14px; font-weight: bold; color: white; }
                QLineEdit { padding: 8px; border: 1px solid #636e72; border-radius: 6px; font-size: 14px; background-color: #636e72; color: white; }
                QPushButton { padding: 10px; border-radius: 6px; font-weight: bold; font-size: 14px; }
            """
            )
        else:
            self.setStyleSheet(
                """
                QDialog { background-color: white; }
                QLabel { font-size: 14px; font-weight: bold; color: #2D3436; }
                QLineEdit { padding: 8px; border: 1px solid #BDBDBD; border-radius: 6px; font-size: 14px; }
                QPushButton { padding: 10px; border-radius: 6px; font-weight: bold; font-size: 14px; }
            """
            )

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        self.input_nombre = QLineEdit()
        self.input_rut = QLineEdit()
        self.input_telefono = QLineEdit()
        self.input_direccion = QLineEdit()

        form_layout.addRow("Nombre Completo:", self.input_nombre)
        form_layout.addRow("RUT:", self.input_rut)
        form_layout.addRow("Número Teléfono:", self.input_telefono)
        form_layout.addRow("Dirección:", self.input_direccion)

        layout.addLayout(form_layout)
        layout.addSpacing(20)

        btn_guardar = QPushButton("Guardar Clienta")
        btn_guardar.setCursor(Qt.PointingHandCursor)
        btn_guardar.setStyleSheet(
            "background-color: #27AE60; color: white; border: none;"
        )
        btn_guardar.clicked.connect(self.guardar)
        layout.addWidget(btn_guardar)

    def guardar(self):
        nombre = self.input_nombre.text().strip()
        rut = self.input_rut.text().strip()
        telefono = self.input_telefono.text().strip()
        direccion = self.input_direccion.text().strip()

        if not nombre or not rut:
            QMessageBox.warning(
                self, "Datos incompletos", "El Nombre y el RUT son obligatorios."
            )
            return

        if guardar_cliente_db(nombre, rut, telefono, direccion):
            if self.callback_agregar:
                self.callback_agregar(nombre, rut, telefono, direccion)
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "Error",
                "No se pudo guardar la clienta.\nPosiblemente el RUT ya existe.",
            )


# --- Ventana para editar clienta ---
class VentanaEditarClienta(QDialog):
    def __init__(self, parent=None, datos_cliente=None, callback_guardar=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Clienta")
        self.setMinimumSize(400, 300)
        self.callback_guardar = callback_guardar
        self.rut_original = datos_cliente["rut"]

        # Detectar tema
        tema = "dark"
        try:
            with open("config.json", "r") as f:
                data = json.load(f)
                tema = data.get("tema", "dark")
        except:
            pass

        if tema == "dark":
            self.setStyleSheet(
                """
                QDialog { background-color: #2D3436; color: white; }
                QLabel { font-size: 14px; font-weight: bold; color: white; }
                QLineEdit { padding: 8px; border: 1px solid #636e72; border-radius: 6px; font-size: 14px; background-color: #636e72; color: white; }
                QPushButton { padding: 10px; border-radius: 6px; font-weight: bold; font-size: 14px; }
            """
            )
        else:
            self.setStyleSheet(
                """
                QDialog { background-color: white; }
                QLabel { font-size: 14px; font-weight: bold; color: #2D3436; }
                QLineEdit { padding: 8px; border: 1px solid #BDBDBD; border-radius: 6px; font-size: 14px; }
                QPushButton { padding: 10px; border-radius: 6px; font-weight: bold; font-size: 14px; }
            """
            )

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        self.input_nombre = QLineEdit(datos_cliente["nombre"])
        self.input_rut = QLineEdit(datos_cliente["rut"])
        self.input_rut.setReadOnly(True)  # El RUT no se debe editar fácilmente
        self.input_telefono = QLineEdit(datos_cliente["telefono"])
        self.input_direccion = QLineEdit(datos_cliente["direccion"])

        form_layout.addRow("Nombre Completo:", self.input_nombre)
        form_layout.addRow("RUT (No editable):", self.input_rut)
        form_layout.addRow("Número Teléfono:", self.input_telefono)
        form_layout.addRow("Dirección:", self.input_direccion)

        layout.addLayout(form_layout)
        layout.addSpacing(20)

        btn_guardar = QPushButton("Guardar Cambios")
        btn_guardar.setCursor(Qt.PointingHandCursor)
        btn_guardar.setStyleSheet(
            "background-color: #0984e3; color: white; border: none;"
        )
        btn_guardar.clicked.connect(self.guardar)
        layout.addWidget(btn_guardar)

    def guardar(self):
        if self.callback_guardar:
            self.callback_guardar(
                self.rut_original,
                self.input_nombre.text(),
                self.input_telefono.text(),
                self.input_direccion.text(),
            )
        self.accept()


# --- Ventana para registrar nueva compra ---
class VentanaNuevaCompra(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Compra - Crédito")
        self.setMinimumSize(350, 250)

        # Detectar tema
        tema = "dark"
        try:
            with open("config.json", "r") as f:
                data = json.load(f)
                tema = data.get("tema", "dark")
        except:
            pass

        if tema == "dark":
            self.setStyleSheet(
                """
                QDialog { background-color: #2D3436; color: white; }
                QLabel { font-weight: bold; color: white; font-size: 14px; }
                QLineEdit { padding: 6px; border: 1px solid #636e72; border-radius: 4px; font-size: 14px; background-color: #636e72; color: white; }
            """
            )
        else:
            self.setStyleSheet(
                """
                QDialog { background-color: white; }
                QLabel { font-weight: bold; color: #2D3436; font-size: 14px; }
                QLineEdit { padding: 6px; border: 1px solid #BDBDBD; border-radius: 4px; font-size: 14px; }
            """
            )

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(15)

        self.input_producto = QLineEdit()
        self.input_total = QLineEdit()
        self.input_total.setPlaceholderText("Ej: 50000")
        self.input_pie = QLineEdit()
        self.input_pie.setPlaceholderText("Ej: 10000")

        form.addRow("Producto:", self.input_producto)
        form.addRow("Total ($):", self.input_total)
        form.addRow("Pie Inicial ($):", self.input_pie)

        layout.addLayout(form)
        layout.addSpacing(20)

        btn_guardar = QPushButton("Guardar Compra")
        btn_guardar.setCursor(Qt.PointingHandCursor)
        btn_guardar.setStyleSheet(
            "background-color: #27AE60; color: white; border: none;"
        )
        btn_guardar.clicked.connect(self.guardar)
        layout.addWidget(btn_guardar)

    def guardar(self):
        if (
            not self.input_producto.text()
            or not self.input_total.text()
            or not self.input_pie.text()
        ):
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios.")
            return
        if not self.input_total.text().isdigit() or not self.input_pie.text().isdigit():
            QMessageBox.warning(self, "Error", "Total y Pie deben ser números enteros.")
            return
        self.accept()

    def get_data(self):
        return (
            self.input_producto.text().strip(),
            int(self.input_total.text().strip()),
            int(self.input_pie.text().strip()),
        )


# --- Ventana de Historial de Crédito ---
class VentanaHistorial(QDialog):
    def __init__(self, parent=None, cliente_data=None):
        super().__init__(parent)
        self.cliente = cliente_data
        self.setWindowTitle(f"Historial Crédito Girasol - {self.cliente['nombre']}")
        self.resize(900, 500)

        # Detectar tema
        tema = "dark"
        try:
            with open("config.json", "r") as f:
                data = json.load(f)
                tema = data.get("tema", "dark")
        except:
            pass

        if tema == "dark":
            self.setStyleSheet(
                """
                QDialog { background-color: #2D3436; color: white; }
                QLabel { font-size: 14px; color: white; }
                QTableWidget { background-color: #2D3436; alternate-background-color: #353b48; color: white; gridline-color: #636e72; border: 1px solid #636e72; }
                QHeaderView::section { background-color: #2D3436; color: white; border: 1px solid #636e72; padding: 6px; font-weight: bold; }
                QTableWidget::item:selected { background-color: #F4D03F; color: black; }
            """
            )
        else:
            self.setStyleSheet(
                """
                QDialog { background-color: white; }
                QLabel { font-size: 14px; color: #2D3436; }
                QTableWidget { border: 1px solid #BDBDBD; gridline-color: #eee; }
                QHeaderView::section { background-color: #ECEFF1; padding: 6px; border: 1px solid #BDBDBD; font-weight: bold; }
            """
            )

        layout = QVBoxLayout(self)

        # Cabecera con datos del cliente
        header_frame = QWidget()
        header_layout = QHBoxLayout(header_frame)

        lbl_rut = QLabel(f"<b>RUT:</b> {self.cliente['rut']}")
        lbl_tel = QLabel(f"<b>Teléfono:</b> {self.cliente['telefono']}")
        lbl_dir = QLabel(f"<b>Dirección:</b> {self.cliente['direccion']}")

        header_layout.addWidget(lbl_rut)
        header_layout.addWidget(lbl_tel)
        header_layout.addWidget(lbl_dir)
        layout.addWidget(header_frame)

        layout.addWidget(QLabel("<b>Detalle de Compras (Pie + 2 Cuotas)</b>"))

        # Botones de acción
        botones_layout = QHBoxLayout()

        btn_exportar = QPushButton("📄 Exportar PDF")
        btn_exportar.setCursor(Qt.PointingHandCursor)
        btn_exportar.setStyleSheet(
            "background-color: #e17055; color: white; padding: 6px; border-radius: 6px; font-weight: bold;"
        )
        btn_exportar.clicked.connect(self.exportar_pdf)

        btn_nueva_compra = QPushButton("➕ Registrar Nueva Compra")
        btn_nueva_compra.setCursor(Qt.PointingHandCursor)
        btn_nueva_compra.setStyleSheet(
            "background-color: #0984e3; color: white; padding: 6px; border-radius: 6px; font-weight: bold;"
        )
        btn_nueva_compra.clicked.connect(self.registrar_compra)

        botones_layout.addStretch()
        botones_layout.addWidget(btn_exportar)
        botones_layout.addWidget(btn_nueva_compra)
        layout.addLayout(botones_layout)

        # Tabla de historial
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(
            ["Fecha", "Producto", "Total", "Pie (Inicial)", "Cuota 1", "Cuota 2"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        layout.addWidget(self.tabla)

        self.tabla.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabla.customContextMenuRequested.connect(self.mostrar_menu_cuotas)

        self.cargar_datos()

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setCursor(Qt.PointingHandCursor)
        btn_cerrar.setStyleSheet(
            "background-color: #2D3436; color: white; padding: 8px; border-radius: 6px;"
        )
        btn_cerrar.clicked.connect(self.close)
        layout.addWidget(btn_cerrar, alignment=Qt.AlignRight)

    def cargar_datos(self):
        rut = self.cliente["rut"]
        historial = obtener_historial_db(rut)

        self.tabla.setRowCount(len(historial))
        for i, (id_compra, fecha, producto, total, pie, c1, c2) in enumerate(historial):
            item_fecha = QTableWidgetItem(fecha)
            item_fecha.setData(Qt.UserRole, id_compra)  # Guardamos el ID oculto

            self.tabla.setItem(i, 0, item_fecha)
            self.tabla.setItem(i, 1, QTableWidgetItem(producto))
            self.tabla.setItem(i, 2, QTableWidgetItem(f"${total}"))
            self.tabla.setItem(i, 3, QTableWidgetItem(f"${pie}"))
            self.tabla.setItem(i, 4, QTableWidgetItem(c1))
            self.tabla.setItem(i, 5, QTableWidgetItem(c2))

    def mostrar_menu_cuotas(self, pos):
        row = self.tabla.rowAt(pos.y())
        if row < 0:
            return

        item_id = self.tabla.item(row, 0)
        id_compra = item_id.data(Qt.UserRole)

        c1_estado = self.tabla.item(row, 4).text()
        c2_estado = self.tabla.item(row, 5).text()

        menu = QMenu()
        accion_c1 = None
        accion_c2 = None

        if c1_estado != "Pagada":
            accion_c1 = menu.addAction("✅ Marcar Cuota 1 como Pagada")
        if c2_estado != "Pagada":
            accion_c2 = menu.addAction("✅ Marcar Cuota 2 como Pagada")

        if accion_c1 or accion_c2:
            action = menu.exec_(self.tabla.mapToGlobal(pos))
            if action == accion_c1:
                self.cambiar_estado_cuota(id_compra, "cuota1", "Pagada")
            elif action == accion_c2:
                self.cambiar_estado_cuota(id_compra, "cuota2", "Pagada")

    def cambiar_estado_cuota(self, id_compra, columna, estado):
        if actualizar_cuota_db(id_compra, columna, estado):
            if estado == "Pagada":
                self.generar_comprobante(id_compra, columna)
            self.cargar_datos()
        else:
            QMessageBox.warning(
                self, "Error", "No se pudo actualizar el estado de la cuota."
            )

    def generar_comprobante(self, id_compra, cuota_pagada):
        compra = obtener_compra_db(id_compra)
        if not compra:
            return

        # Esquema tabla: id, rut_cliente, fecha, producto, total, pie, cuota1, cuota2
        _, rut, fecha_compra, producto, total, pie, _, _ = compra

        saldo_inicial_compra = total - pie
        valor_cuota = saldo_inicial_compra / 2

        # Deuda total actual (ya incluye el pago realizado porque se actualizó antes)
        deuda_actual = calcular_deuda_cliente(rut)

        html = f"""
        <h2 align="center">Comprobante de Pago - Crédito Girasol</h2>
        <p><b>Cliente:</b> {self.cliente['nombre']}<br>
        <b>RUT:</b> {self.cliente['rut']}<br>
        <b>Fecha Emisión:</b> {datetime.now().strftime('%d-%m-%Y %H:%M')}</p>
        <hr>
        <h3>Detalle del Pago</h3>
        <p><b>Producto:</b> {producto} (Fecha compra: {fecha_compra})<br>
        <b>Concepto:</b> Pago de {cuota_pagada.replace('cuota', 'Cuota ')}<br>
        <b>Monto Pagado:</b> ${int(valor_cuota):,}</p>
        <hr>
        <h3>Resumen de Cuenta</h3>
        <p><b>Saldo Pendiente Total:</b> ${int(deuda_actual):,}</p>
        <p align="center"><i>¡Gracias por su preferencia!</i></p>
        """

        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            document = QTextDocument()
            document.setHtml(html)
            document.print_(printer)

    def exportar_pdf(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Historial",
            f"Historial_{self.cliente['rut']}.pdf",
            "PDF Files (*.pdf)",
        )
        if not filename:
            return

        rut = self.cliente["rut"]
        historial = obtener_historial_db(rut)
        deuda_actual = calcular_deuda_cliente(rut)

        html = f"""
        <h2 align="center">Historial de Crédito Girasol</h2>
        <p><b>Cliente:</b> {self.cliente['nombre']}<br>
        <b>RUT:</b> {self.cliente['rut']}<br>
        <b>Teléfono:</b> {self.cliente['telefono']}<br>
        <b>Dirección:</b> {self.cliente['direccion']}<br>
        <b>Saldo Pendiente Total:</b> ${int(deuda_actual):,}</p>
        <hr>
        <table border="1" cellspacing="0" cellpadding="4" width="100%" style="border-collapse: collapse;">
            <thead>
                <tr style="background-color: #ECEFF1;">
                    <th>Fecha</th>
                    <th>Producto</th>
                    <th>Total</th>
                    <th>Pie</th>
                    <th>Cuota 1</th>
                    <th>Cuota 2</th>
                </tr>
            </thead>
            <tbody>
        """

        for _, fecha, producto, total, pie, c1, c2 in historial:
            html += f"""
                <tr>
                    <td align="center">{fecha}</td>
                    <td>{producto}</td>
                    <td align="right">${total}</td>
                    <td align="right">${pie}</td>
                    <td align="center">{c1}</td>
                    <td align="center">{c2}</td>
                </tr>
            """

        html += """
            </tbody>
        </table>
        <p align="center" style="font-size: 10px; margin-top: 20px;"><i>Documento generado el {}</i></p>
        """.format(
            datetime.now().strftime("%d-%m-%Y %H:%M")
        )

        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(filename)

        document = QTextDocument()
        document.setHtml(html)
        document.print_(printer)

        QMessageBox.information(self, "Éxito", "Historial exportado correctamente.")

    def registrar_compra(self):
        dialog = VentanaNuevaCompra(self)
        if dialog.exec_():
            producto, total, pie = dialog.get_data()
            fecha = datetime.now().strftime("%Y-%m-%d")

            if agregar_compra_db(self.cliente["rut"], fecha, producto, total, pie):
                QMessageBox.information(
                    self, "Éxito", "Compra registrada correctamente."
                )
                self.cargar_datos()
            else:
                QMessageBox.critical(
                    self, "Error", "No se pudo registrar la compra en la base de datos."
                )


# --- Página de clientes con tabla ---
def crear_pagina_clientes(sesion):
    pagina = QWidget()

    # Detectar tema al inicio
    tema = "dark"
    try:
        with open("config.json", "r") as f:
            data = json.load(f)
            tema = data.get("tema", "dark")
    except:
        pass

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

    # Cabecera: Título y Botón Agregar
    header_layout = QHBoxLayout()

    etiqueta = QLabel("Gestión de Clientas - Crédito Girasol")
    etiqueta.setStyleSheet("font-size: 22px; font-weight: bold;")

    btn_agregar = QPushButton("➕ Nueva Clienta")
    btn_agregar.setCursor(Qt.PointingHandCursor)
    btn_agregar.setStyleSheet(
        "background-color: #0984e3; color: white; font-weight: bold; padding: 8px 15px; border-radius: 6px; border: none;"
    )

    btn_editar = QPushButton("✏️ Editar")
    btn_editar.setCursor(Qt.PointingHandCursor)
    btn_editar.setStyleSheet(
        "background-color: #f39c12; color: white; font-weight: bold; padding: 8px 15px; border-radius: 6px; border: none;"
    )

    btn_eliminar = QPushButton("🗑 Eliminar Clienta")
    btn_eliminar.setCursor(Qt.PointingHandCursor)
    btn_eliminar.setStyleSheet(
        "background-color: #ff7675; color: white; font-weight: bold; padding: 8px 15px; border-radius: 6px; border: none;"
    )

    header_layout.addWidget(etiqueta)
    header_layout.addStretch()
    header_layout.addWidget(btn_editar)
    header_layout.addWidget(btn_eliminar)
    header_layout.addWidget(btn_agregar)

    layout.addLayout(header_layout)

    # --- Buscador y Filtros ---
    search_layout = QHBoxLayout()
    input_busqueda = QLineEdit()
    input_busqueda.setPlaceholderText("🔍 Buscar por Nombre o RUT...")

    # Estilo del buscador (se adapta mejor si quitamos el background hardcoded o lo hacemos condicional)
    # Como esta página está incrustada en el Dashboard, heredará estilos globales,
    # pero QLineEdit suele necesitar un retoque específico si el global no es suficiente.
    # Usaremos un estilo neutro que respete el tema global definido en estilos.py
    input_busqueda.setStyleSheet(
        """
        QLineEdit {
            padding: 8px;
            border-radius: 6px;
            font-size: 14px;
        }
    """
    )

    chk_deudores = QCheckBox("Solo Deudores")
    chk_deudores.setCursor(Qt.PointingHandCursor)

    # Detectar tema para el checkbox (aunque se usa más abajo para la tabla, lo adelantamos o usamos lógica simple)
    if tema == "dark":
        chk_deudores.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
    else:
        chk_deudores.setStyleSheet(
            "color: #2D3436; font-weight: bold; font-size: 14px;"
        )

    search_layout.addWidget(input_busqueda)
    search_layout.addWidget(chk_deudores)
    layout.addLayout(search_layout)

    tabla = QTableWidget()
    tabla.setColumnCount(6)
    tabla.setHorizontalHeaderLabels(
        ["Nombre", "RUT", "Teléfono", "Dirección", "Saldo Pendiente", "Historial"]
    )
    tabla.horizontalHeader().setStretchLastSection(True)
    tabla.verticalHeader().setVisible(False)
    tabla.setAlternatingRowColors(True)
    tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
    tabla.setSelectionBehavior(QAbstractItemView.SelectRows)

    if tema == "dark":
        tabla.setStyleSheet(
            """
            QTableWidget { gridline-color: #636e72; font-size: 12px; background-color: #2D3436; color: white; border-radius: 8px; border: 1px solid #636e72; }
            QTableWidget::item:selected { background-color: #F4D03F; color: black; }
            QHeaderView::section { background-color: #2D3436; font-weight: bold; padding: 8px; border: 1px solid #636e72; color: white; font-size: 12px; }
            QTableWidget::item { padding: 5px; }
        """
        )
    else:
        tabla.setStyleSheet(
            """
            QTableWidget { gridline-color: #BDBDBD; font-size: 12px; background-color: white; border-radius: 8px; }
            QHeaderView::section { background-color: #ECEFF1; font-weight: bold; padding: 8px; border: 1px solid #BDBDBD; color: #2D3436; font-size: 12px; }
        """
        )

    def agregar_fila(nombre, rut, telefono, direccion, saldo=0):
        fila = tabla.rowCount()
        tabla.insertRow(fila)
        tabla.setItem(fila, 0, QTableWidgetItem(nombre))
        tabla.setItem(fila, 1, QTableWidgetItem(rut))
        tabla.setItem(fila, 2, QTableWidgetItem(telefono))
        tabla.setItem(fila, 3, QTableWidgetItem(direccion))
        tabla.setItem(fila, 4, QTableWidgetItem(f"${saldo:,}"))

        btn_historial = QPushButton("Ver Historial")
        btn_historial.setCursor(Qt.PointingHandCursor)
        btn_historial.setStyleSheet(
            "background-color: #F4D03F; color: #2D3436; border-radius: 4px; font-weight: bold; padding: 4px;"
        )

        # Datos del cliente para pasar al historial
        cliente_data = {
            "nombre": nombre,
            "rut": rut,
            "telefono": telefono,
            "direccion": direccion,
        }

        btn_historial.clicked.connect(
            lambda: VentanaHistorial(pagina, cliente_data).exec_()
        )

        tabla.setCellWidget(fila, 5, btn_historial)

    # --- Variables de Paginación ---
    pagina.pagina_actual = 1
    pagina.items_por_pagina = 10
    pagina.total_items = 0
    pagina.columna_orden = "nombre"
    pagina.direccion_orden = "ASC"

    def cargar_datos():
        # Limpiar tabla
        tabla.setRowCount(0)

        filtro = input_busqueda.text().strip()
        solo_deudores = chk_deudores.isChecked()

        # Obtener total y datos paginados
        pagina.total_items = contar_clientes_db(filtro, solo_deudores)
        clientes = obtener_clientes_paginados(
            pagina.pagina_actual,
            pagina.items_por_pagina,
            filtro,
            pagina.columna_orden,
            pagina.direccion_orden,
            solo_deudores,
        )

        for c in clientes:
            # c = (nombre, rut, telefono, direccion)
            deuda = calcular_deuda_cliente(c[1])
            agregar_fila(c[0], c[1], c[2], c[3], deuda)

        actualizar_controles_paginacion()

    def actualizar_controles_paginacion():
        total_paginas = (
            pagina.total_items + pagina.items_por_pagina - 1
        ) // pagina.items_por_pagina
        if total_paginas == 0:
            total_paginas = 1

        lbl_paginacion.setText(
            f"Página {pagina.pagina_actual} de {total_paginas} (Total: {pagina.total_items})"
        )

        btn_anterior.setEnabled(pagina.pagina_actual > 1)
        btn_siguiente.setEnabled(pagina.pagina_actual < total_paginas)

    def cambiar_pagina(delta):
        pagina.pagina_actual += delta
        cargar_datos()

    def actualizar_headers_visuales():
        headers_base = [
            "Nombre",
            "RUT",
            "Teléfono",
            "Dirección",
            "Saldo Pendiente",
            "Historial",
        ]
        col_map = {"nombre": 0, "rut": 1, "telefono": 2, "direccion": 3}
        idx_activo = col_map.get(pagina.columna_orden, -1)

        for i, texto in enumerate(headers_base):
            if i == idx_activo:
                flecha = " ▲" if pagina.direccion_orden == "ASC" else " ▼"
                texto += flecha

            item = tabla.horizontalHeaderItem(i)
            if not item:
                item = QTableWidgetItem()
                tabla.setHorizontalHeaderItem(i, item)
            item.setText(texto)

    # Lógica de ordenamiento por columnas
    def ordenar_tabla(col_index):
        columnas = {0: "nombre", 1: "rut", 2: "telefono", 3: "direccion"}
        if col_index in columnas:
            col_nombre = columnas[col_index]
            if pagina.columna_orden == col_nombre:
                # Alternar dirección
                pagina.direccion_orden = (
                    "DESC" if pagina.direccion_orden == "ASC" else "ASC"
                )
            else:
                pagina.columna_orden = col_nombre
                pagina.direccion_orden = "ASC"
            actualizar_headers_visuales()
            cargar_datos()

    tabla.horizontalHeader().sectionClicked.connect(ordenar_tabla)

    # Conectar botón agregar
    def abrir_agregar_clienta():
        def callback_refresh(n, r, t, d):
            cargar_datos()

        dialog = VentanaAgregarClienta(pagina, callback_agregar=callback_refresh)
        dialog.exec_()

    btn_agregar.clicked.connect(abrir_agregar_clienta)

    # Lógica editar clienta
    def abrir_editar_clienta():
        row = tabla.currentRow()
        if row < 0:
            QMessageBox.warning(
                pagina, "Atención", "Seleccione una clienta para editar."
            )
            return

        datos = {
            "nombre": tabla.item(row, 0).text(),
            "rut": tabla.item(row, 1).text(),
            "telefono": tabla.item(row, 2).text(),
            "direccion": tabla.item(row, 3).text(),
        }

        def guardar_cambios(rut, nombre, telefono, direccion):
            if actualizar_cliente_db(rut, nombre, telefono, direccion):
                QMessageBox.information(
                    pagina, "Éxito", "Clienta actualizada correctamente."
                )
                cargar_datos()
            else:
                QMessageBox.critical(
                    pagina, "Error", "No se pudo actualizar la información."
                )

        dialog = VentanaEditarClienta(
            pagina, datos_cliente=datos, callback_guardar=guardar_cambios
        )
        dialog.exec_()

    btn_editar.clicked.connect(abrir_editar_clienta)

    # Lógica eliminar clienta
    def eliminar_clienta_seleccionada():
        row = tabla.currentRow()
        if row < 0:
            QMessageBox.warning(
                pagina, "Atención", "Seleccione una clienta para eliminar."
            )
            return

        nombre = tabla.item(row, 0).text()
        rut = tabla.item(row, 1).text()

        confirmacion = QMessageBox.question(
            pagina,
            "Confirmar Eliminación",
            f"¿Estás seguro de eliminar a {nombre}?\nSe borrará también su historial de crédito.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if confirmacion == QMessageBox.Yes:
            # Solicitar contraseña de administrador
            pwd, ok = QInputDialog.getText(
                pagina,
                "Autorización Requerida",
                "Ingrese contraseña de administrador:",
                QLineEdit.Password,
            )
            if not ok or not pwd:
                return

            if verificacion_encargado_local(pwd) not in (1, 3):
                QMessageBox.warning(
                    pagina,
                    "Acceso Denegado",
                    "Contraseña incorrecta o permisos insuficientes.",
                )
                return

            if eliminar_cliente_db(rut):
                tabla.removeRow(row)
                cargar_datos()  # Recargar para actualizar paginación

    btn_eliminar.clicked.connect(eliminar_clienta_seleccionada)

    # Lógica del buscador
    def on_busqueda_changed():
        pagina.pagina_actual = 1
        cargar_datos()

    input_busqueda.textChanged.connect(on_busqueda_changed)

    # Lógica del filtro de deudores
    chk_deudores.stateChanged.connect(
        lambda: [setattr(pagina, "pagina_actual", 1), cargar_datos()]
    )

    # Evento doble clic para abrir historial
    def on_doble_clic(row, column):
        nombre = tabla.item(row, 0).text()
        rut = tabla.item(row, 1).text()
        telefono = tabla.item(row, 2).text()
        direccion = tabla.item(row, 3).text()

        cliente_data = {
            "nombre": nombre,
            "rut": rut,
            "telefono": telefono,
            "direccion": direccion,
        }
        VentanaHistorial(pagina, cliente_data).exec_()

    tabla.cellDoubleClicked.connect(on_doble_clic)

    layout.addWidget(tabla)

    # --- Controles de Paginación ---
    layout_paginacion = QHBoxLayout()
    layout_paginacion.setAlignment(Qt.AlignCenter)

    # Selector de items por página
    lbl_mostrar = QLabel("Mostrar:")
    if tema == "dark":
        lbl_mostrar.setStyleSheet("color: white;")

    combo_paginacion = QComboBox()
    combo_paginacion.addItems(["10", "20", "50", "100"])
    combo_paginacion.setFixedWidth(70)
    combo_paginacion.setStyleSheet("padding: 4px; border-radius: 4px;")
    combo_paginacion.currentIndexChanged.connect(
        lambda: [
            setattr(pagina, "items_por_pagina", int(combo_paginacion.currentText())),
            setattr(pagina, "pagina_actual", 1),
            cargar_datos(),
        ]
    )

    btn_anterior = QPushButton("◀ Anterior")
    btn_anterior.setCursor(Qt.PointingHandCursor)
    btn_anterior.setStyleSheet(
        "background-color: #636e72; color: white; border-radius: 4px; padding: 6px;"
    )
    btn_anterior.clicked.connect(lambda: cambiar_pagina(-1))

    lbl_paginacion = QLabel("Página 1")
    lbl_paginacion.setStyleSheet("font-weight: bold; font-size: 14px; margin: 0 10px;")
    if tema == "dark":
        lbl_paginacion.setStyleSheet(
            "font-weight: bold; font-size: 14px; margin: 0 10px; color: white;"
        )

    btn_siguiente = QPushButton("Siguiente ▶")
    btn_siguiente.setCursor(Qt.PointingHandCursor)
    btn_siguiente.setStyleSheet(
        "background-color: #636e72; color: white; border-radius: 4px; padding: 6px;"
    )
    btn_siguiente.clicked.connect(lambda: cambiar_pagina(1))

    layout_paginacion.addWidget(lbl_mostrar)
    layout_paginacion.addWidget(combo_paginacion)
    layout_paginacion.addSpacing(15)
    layout_paginacion.addWidget(btn_anterior)
    layout_paginacion.addWidget(lbl_paginacion)
    layout_paginacion.addWidget(btn_siguiente)
    layout.addLayout(layout_paginacion)

    pagina.setLayout(layout)

    # Cargar datos iniciales
    actualizar_headers_visuales()
    cargar_datos()

    return pagina
