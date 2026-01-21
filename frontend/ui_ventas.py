from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QSpacerItem,
    QSizePolicy,
    QHBoxLayout,
    QLineEdit,
    QFrame,
    QPushButton,
    QComboBox,
    QMessageBox,
    QInputDialog,
    QFormLayout,
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import sys
import sqlite3
from datetime import datetime
from backend.logica.inventario import obtener_producto_por_codigo
from backend.logica.ventas import (
    busqueda_descuento,
    verificacion_encargado_local,
    registrar_venta,
)
from frontend.ui_clientes import agregar_compra_db, calcular_deuda_cliente


#  Ventana de pago en blanco
class VentanaPago(QWidget):
    def __init__(
        self,
        subtotal=0,
        productos=None,
        descuento_total=0,
        metodo_pago="Efectivo",
        rut_empleado=None,
        cliente_girasol=None,
    ):
        super().__init__()
        self.setWindowTitle("Procesar Pago")
        self.setMinimumSize(400, 300)

        self.subtotal = subtotal
        self.productos = productos if productos else []
        self.descuento_total = descuento_total
        self.metodo_pago = metodo_pago
        self.rut_empleado = rut_empleado
        self.cliente_girasol = cliente_girasol

        layout = QVBoxLayout()
        mensaje = QLabel("Ventana de pago")
        mensaje.setAlignment(Qt.AlignCenter)
        mensaje.setStyleSheet("font-size: 18px; font-weight: bold; color: #2D3436;")
        layout.addWidget(mensaje)

        # Si es crédito, solicitar Pie
        self.input_pie = None
        if self.metodo_pago == "Crédito Girasol":
            layout.addWidget(QLabel(f"Clienta: {self.cliente_girasol['nombre']}"))
            layout.addWidget(
                QLabel(f"Total Venta: ${int(self.subtotal - self.descuento_total)}")
            )

            form_pie = QFormLayout()
            self.input_pie = QLineEdit()
            self.input_pie.setPlaceholderText("Ingrese monto del pie")
            self.input_pie.setStyleSheet("padding: 6px; font-size: 14px;")
            form_pie.addRow("Pie Inicial ($):", self.input_pie)
            layout.addLayout(form_pie)

        btn_confirmar = QPushButton("Confirmar Pago")
        btn_confirmar.setStyleSheet(
            """
            QPushButton {
                background-color: #27AE60;
                color: white;
                font-size: 16px;
                padding: 8px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #219150;
            }
        """
        )
        btn_confirmar.clicked.connect(self.confirmar_pago)
        layout.addWidget(btn_confirmar)

        self.setLayout(layout)

    def confirmar_pago(self):
        try:
            # Lógica específica para Crédito Girasol
            if self.metodo_pago == "Crédito Girasol":
                if not self.input_pie.text().strip().isdigit():
                    QMessageBox.warning(
                        self, "Error", "Ingrese un monto de pie válido."
                    )
                    return

                pie = int(self.input_pie.text())
                total_final = int(self.subtotal - self.descuento_total)

                if pie >= total_final:
                    QMessageBox.warning(
                        self,
                        "Error",
                        "El pie no puede ser mayor o igual al total. Use otro método de pago.",
                    )
                    return

                # Registrar el crédito en la base de datos de clientes
                fecha_hoy = datetime.now().strftime("%Y-%m-%d")
                # Concatenar nombres de productos para el historial
                nombres_prods = ", ".join([p["nombre"] for p in self.productos])

                if not agregar_compra_db(
                    self.cliente_girasol["rut"],
                    fecha_hoy,
                    nombres_prods,
                    total_final,
                    pie,
                ):
                    raise Exception(
                        "No se pudo registrar el crédito en la base de datos de clientes."
                    )

            registrar_venta(
                self.subtotal,
                self.productos,
                self.descuento_total,
                self.metodo_pago,
                self.rut_empleado,
            )
            QMessageBox.information(
                self,
                "Pago confirmado",
                "El pago ha sido procesado y la venta registrada.",
            )
            self.close()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Ocurrió un problema al registrar la venta:\n{e}"
            )


# Función para marcar el método de pago seleccionado
def seleccionar_metodo(seleccionado, todos, frame_efectivo):
    for btn in todos:
        btn.setChecked(btn == seleccionado)
    frame_efectivo.setVisible(seleccionado.text() == "Efectivo")


#  Página de ventas
def crear_pagina_ventas(sesion):

    pagina = QWidget()
    pagina.setWindowTitle("Registro de Ventas")
    pagina.setMinimumSize(900, 600)
    pagina.setStyleSheet("background-color: white;")
    fondo = QLabel(pagina)
    fondo.setPixmap(QPixmap("frontend/assets/"))
    fondo.setScaledContents(True)
    fondo.setGeometry(0, 0, pagina.width(), pagina.height())
    pagina.resizeEvent = lambda event: fondo.setGeometry(
        0, 0, pagina.width(), pagina.height()
    )

    layout_principal = QHBoxLayout(pagina)
    layout_principal.setContentsMargins(40, 40, 40, 40)
    layout_principal.setSpacing(30)

    

    # Sección izquierda
    seccion_izquierda = QFrame()
    seccion_izquierda.setMinimumWidth(500)
    seccion_izquierda.setMinimumWidth(400)
    seccion_izquierda.setStyleSheet(
        "background-color: rgba(255,255,255,0.85); border-radius: 12px;"
    )
    layout_izquierda = QVBoxLayout(seccion_izquierda)

    # Botón Volver
    btn_volver = QPushButton("⬅ Volver al Menú")
    btn_volver.setCursor(Qt.PointingHandCursor)
    btn_volver.setFixedWidth(160)
    btn_volver.setStyleSheet(
        "background-color: #2D3436; color: white; border-radius: 5px; padding: 8px; font-weight: bold;"
    )
    layout_izquierda.addWidget(btn_volver, alignment=Qt.AlignLeft)
    pagina.btn_volver = btn_volver

    etiqueta = QLabel("Registro de Ventas")
    etiqueta.setAlignment(Qt.AlignCenter)
    etiqueta.setStyleSheet("font-size: 18px; font-weight: bold; color: #2D3436;")
    layout_izquierda.addWidget(etiqueta)

    # Barra buscadora
    # Barra buscadora
    buscador = QLineEdit()
    buscador.setPlaceholderText("Escanee o ingrese código de barra...")
    buscador.setStyleSheet(
        "padding: 6px; font-size: 14px; border: 1px solid #BDBDBD; border-radius: 4px;"
    )
    layout_izquierda.addWidget(buscador)

    lista_productos = QListWidget()
    lista_productos.setStyleSheet("background-color: white; border-radius: 6px;")
    layout_izquierda.addWidget(lista_productos)

    productos = []
    subtotal = 0

    # Funciones dinámicas
    def actualizar_totales():

        total_input.setText(f"${int(subtotal)}")
        subtotal_input.setText(f"${int(subtotal)}")

    # --- Funciones dinámicas ---
    def actualizar_totales():
        total_input.setText(f"${int(subtotal)}")
        subtotal_input.setText(f"${int(subtotal)}")

    # Nueva función: crea una tarjeta visual para cada producto
    def crear_tarjeta_producto(prod):
        frame = QFrame()
        frame.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border: 1px solid #BDBDBD;
                border-radius: 8px;
            }
        """
        )
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)

        # Nombre del producto
        lbl_nombre = QLabel(prod["nombre"])
        lbl_nombre.setStyleSheet("font-size: 16px; font-weight: bold; color: #2D3436;")
        layout.addWidget(lbl_nombre)

        # Cantidad, precio y total en una fila
        fila_info = QHBoxLayout()
        lbl_cantidad = QLabel(f"Cantidad: {prod['cantidad']}")
        lbl_cantidad.setObjectName("cantidad")
        lbl_precio = QLabel(f"Precio: ${prod['precio']}")
        lbl_precio.setStyleSheet("color: #0984e3; font-weight: bold;")
        lbl_total = QLabel(f"Total: ${prod['cantidad'] * prod['precio']}")
        lbl_total.setObjectName("total")

        fila_info.addWidget(lbl_cantidad)
        fila_info.addStretch()
        fila_info.addWidget(lbl_precio)
        fila_info.addWidget(lbl_total)
        layout.addLayout(fila_info)

        # Botón eliminar
        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.setFixedSize(80, 30)
        btn_eliminar.setStyleSheet(
            """
            QPushButton {
                background-color: #FF8A80;
                color: #2D3436;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #FF6E6E;
            }
        """
        )
        layout.addWidget(btn_eliminar, alignment=Qt.AlignRight)

        return frame

    # Modificada: ahora usa tarjetas en vez de texto plano
    def agregar_producto(nombre, cantidad, precio):
        nonlocal subtotal
        for i, prod in enumerate(productos):
            if prod["nombre"] == nombre and prod["precio"] == precio:
                prod["cantidad"] += cantidad
                subtotal += cantidad * precio
                item = lista_productos.item(i)
                widget = lista_productos.itemWidget(item)
                widget.findChild(QLabel, "cantidad").setText(
                    f"Cantidad: {prod['cantidad']}"
                )
                widget.findChild(QLabel, "total").setText(
                    f"Total: ${prod['cantidad'] * prod['precio']}"
                )
                actualizar_totales()
                return

        productos.append({"nombre": nombre, "cantidad": cantidad, "precio": precio})
        subtotal += cantidad * precio
        item = QListWidgetItem()
        frame = crear_tarjeta_producto(productos[-1])
        item.setSizeHint(frame.sizeHint())
        lista_productos.addItem(item)
        lista_productos.setItemWidget(item, frame)
        actualizar_totales()

    def buscar_por_codigo():
        codigo = buscador.text().strip()
        if codigo:
            prenda = obtener_producto_por_codigo(codigo)
            if prenda:
                nombre, precio = prenda
                agregar_producto(nombre, 1, precio)
                buscador.clear()
            else:
                print("Producto no encontrado")

    buscador.returnPressed.connect(buscar_por_codigo)

    # Sección derecha
    seccion_derecha = QFrame()
    seccion_derecha.setFixedWidth(400)
    seccion_derecha.setMinimumWidth(600)
    seccion_derecha.setStyleSheet(
        "background-color: rgba(255,255,255,0.85); border-radius: 12px;"
    )
    layout_derecha = QVBoxLayout(seccion_derecha)
    layout_derecha.setAlignment(Qt.AlignTop)

    # --- Selector Tipo de Venta ---
    lbl_tipo_venta = QLabel("TIPO DE VENTA")
    lbl_tipo_venta.setAlignment(Qt.AlignCenter)
    lbl_tipo_venta.setStyleSheet(
        "font-size: 22px; font-weight: 900; color: #2D3436; margin-top: 10px;"
    )
    layout_derecha.addWidget(lbl_tipo_venta)

    combo_tipo_venta = QComboBox()
    combo_tipo_venta.addItems(["Venta Normal", "Venta Clienta Girasol"])
    combo_tipo_venta.setCursor(Qt.PointingHandCursor)
    combo_tipo_venta.setStyleSheet(
        """
        QComboBox {
            padding: 12px;
            border-radius: 8px;
            font-size: 20px;
            font-weight: bold;
            border: 2px solid #0984e3;
            color: #2D3436;
        }
        QComboBox::drop-down {
            border: none;
        }
    """
    )
    layout_derecha.addWidget(combo_tipo_venta)

    # Frame para datos de clienta girasol (oculto por defecto)
    frame_cliente = QFrame()
    frame_cliente.setVisible(False)
    frame_cliente.setStyleSheet(
        "background-color: #e1f5fe; border-radius: 6px; padding: 5px;"
    )
    layout_cliente = QVBoxLayout(frame_cliente)

    lbl_cliente_info = QLabel("Ninguna clienta seleccionada")
    lbl_cliente_info.setStyleSheet("font-weight: bold; color: #0277bd;")

    btn_buscar_cliente = QPushButton("🔍 Buscar Clienta")
    btn_buscar_cliente.setCursor(Qt.PointingHandCursor)
    btn_buscar_cliente.setStyleSheet(
        "background-color: #0288d1; color: white; border-radius: 4px; padding: 4px;"
    )

    layout_cliente.addWidget(lbl_cliente_info)
    layout_cliente.addWidget(btn_buscar_cliente)
    layout_derecha.addWidget(frame_cliente)

    cliente_seleccionado = None

    def buscar_cliente_db():
        texto, ok = QInputDialog.getText(
            pagina, "Buscar Clienta", "Ingrese RUT o Nombre de la clienta:"
        )
        if ok and texto:
            texto_busqueda = f"%{texto.strip()}%"
            with sqlite3.connect("clientes.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT nombre, rut FROM clientes WHERE rut LIKE ? OR nombre LIKE ?",
                    (texto_busqueda, texto_busqueda),
                )
                rows = cursor.fetchall()

                if rows:
                    # Tomamos el primero encontrado
                    row = rows[0]
                    nonlocal cliente_seleccionado
                    cliente_seleccionado = {"nombre": row[0], "rut": row[1]}
                    lbl_cliente_info.setText(f"{row[0]}\n{row[1]}")

                    # Validar deuda
                    deuda = calcular_deuda_cliente(row[1])
                    if deuda > 50000:  # Umbral de advertencia
                        QMessageBox.warning(
                            pagina,
                            "⚠️ Deuda Pendiente Alta",
                            f"La clienta {row[0]} tiene una deuda pendiente de ${deuda:,}.\n\nPor favor verifique su situación antes de otorgar un nuevo crédito.",
                        )
                else:
                    QMessageBox.warning(
                        pagina, "No encontrado", "Clienta no encontrada."
                    )

    btn_buscar_cliente.clicked.connect(buscar_cliente_db)
    layout_derecha.addSpacing(10)

    total_label = QLabel("Total")
    total_label.setAlignment(Qt.AlignCenter)
    total_label.setStyleSheet("font-size: 20px; font-weight: bold;")
    layout_derecha.addWidget(total_label)

    total_input = QLineEdit()
    total_input.setReadOnly(True)
    total_input.setText(f"${int(subtotal)}")
    total_input.setAlignment(Qt.AlignCenter)
    total_input.setStyleSheet(
        "font-size: 24px; background-color: white; border-radius: 6px;"
    )
    layout_derecha.addWidget(total_input)

    layout_derecha.addSpacing(20)

    subtotal_label = QLabel("Subtotal")
    subtotal_label.setAlignment(Qt.AlignCenter)
    subtotal_label.setStyleSheet("font-size: 16px; font-weight: bold;")
    layout_derecha.addWidget(subtotal_label)

    subtotal_input = QLineEdit()
    subtotal_input.setReadOnly(True)
    subtotal_input.setText(f"${int(subtotal)}")
    subtotal_input.setAlignment(Qt.AlignCenter)
    subtotal_input.setStyleSheet(
        "font-size: 18px; background-color: white; border-radius: 6px;"
    )
    layout_derecha.addWidget(subtotal_input)

    layout_derecha.addSpacing(20)

    # Métodos de pago
    metodo_label = QLabel("Método de pago")
    metodo_label.setAlignment(Qt.AlignCenter)
    metodo_label.setStyleSheet("font-size: 16px; font-weight: bold;")
    layout_derecha.addWidget(metodo_label)

    botones_metodo = QHBoxLayout()
    botones_metodo.setSpacing(5)

    btn_efectivo = QPushButton("Efectivo")
    btn_tarjeta = QPushButton("Débito/Crédito")
    btn_transferencia = QPushButton("Transferencia")
    btn_credito = QPushButton("Crédito Girasol")
    btn_credito.setVisible(False)  # Oculto por defecto

    botones = [btn_efectivo, btn_tarjeta, btn_transferencia]
    botones = [btn_efectivo, btn_tarjeta, btn_transferencia, btn_credito]

    for btn in botones:
        btn.setCheckable(True)
        btn.setStyleSheet(
            """
            QPushButton {
                background-color: #dfe6e9;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:checked {
                background-color: #74b9ff;
                font-weight: bold;
            }
        """
        )
        botones_metodo.addWidget(btn)

    layout_derecha.addLayout(botones_metodo)

    # Lógica cambio tipo venta
    def cambiar_tipo_venta(index):
        nonlocal cliente_seleccionado
        if index == 1:  # Venta Clienta Girasol
            frame_cliente.setVisible(True)
            btn_credito.setVisible(True)
            combo_tipo_venta.setStyleSheet(
                """
                QComboBox {
                    padding: 12px;
                    border-radius: 8px;
                    font-size: 20px;
                    font-weight: bold;
                    border: 2px solid #e17055;
                    background-color: #ffeaa7;
                    color: #d63031;
                }
            """
            )
        else:
            frame_cliente.setVisible(False)
            btn_credito.setVisible(False)
            cliente_seleccionado = None
            lbl_cliente_info.setText("Ninguna clienta seleccionada")
            if btn_credito.isChecked():
                btn_efectivo.setChecked(True)
                seleccionar_metodo(btn_efectivo, botones, frame_efectivo)

            combo_tipo_venta.setStyleSheet(
                """
                QComboBox {
                    padding: 12px;
                    border-radius: 8px;
                    font-size: 20px;
                    font-weight: bold;
                    border: 2px solid #0984e3;
                    background-color: white;
                    color: #2D3436;
                }
            """
            )

    combo_tipo_venta.currentIndexChanged.connect(cambiar_tipo_venta)

    # Campo de pago en efectivo
    frame_efectivo = QFrame()
    frame_efectivo.setVisible(False)
    layout_efectivo = QVBoxLayout(frame_efectivo)

    input_pago = QLineEdit()
    input_pago.setPlaceholderText("Monto entregado")
    input_pago.setStyleSheet(
        "background-color: white; border-radius: 6px; padding: 6px;"
    )
    input_pago.setAlignment(Qt.AlignCenter)

    input_vuelto = QLineEdit()
    input_vuelto.setReadOnly(True)
    input_vuelto.setPlaceholderText("Vuelto")
    input_vuelto.setStyleSheet(
        "background-color: white; border-radius: 6px; padding: 6px;"
    )
    input_vuelto.setAlignment(Qt.AlignCenter)

    layout_efectivo.addWidget(input_pago)
    layout_efectivo.addWidget(input_vuelto)
    layout_derecha.addWidget(frame_efectivo)

    def calcular_vuelto():
        try:
            monto = float(input_pago.text())
            vuelto = monto - subtotal
            input_vuelto.setText(
                f"${int(vuelto)}" if vuelto >= 0 else "Monto insuficiente"
            )
        except ValueError:
            input_vuelto.setText("")

    input_pago.textChanged.connect(calcular_vuelto)

    # --- DESCUENTO GENERAL ---
    descuento_label = QLabel("Descuento")
    descuento_label.setAlignment(Qt.AlignCenter)
    descuento_label.setStyleSheet("font-size: 16px; font-weight: bold;")
    layout_derecha.addWidget(descuento_label)

    combo_descuento = QComboBox()
    combo_descuento.addItem("Sin descuento", 0.0)
    for tipo, valor in busqueda_descuento():
        combo_descuento.addItem(f"{tipo}", valor)
    combo_descuento.setStyleSheet(
        "background-color: white; border-radius: 6px; padding: 6px;"
    )
    layout_derecha.addWidget(combo_descuento)

    def verificar_gerente():
        rut, ok = QInputDialog.getText(
            pagina,
            "Autorización requerida",
            "Escanee el código de barra del gerente (RUT):",
        )
        if not ok or not rut:
            return False
        resultado = verificacion_encargado_local(rut)
        if resultado in (1, 3):  # 1=Gerente, 3=Encargado
            return True
        QMessageBox.warning(
            pagina,
            "Acceso denegado",
            "Solo un gerente/encargado puede autorizar descuentos.",
        )
        return False

    def aplicar_descuento():
        if verificar_gerente():
            valor = combo_descuento.currentData()
            descuento = subtotal * valor
            total_con_descuento = subtotal - descuento
            total_input.setText(f"${int(total_con_descuento)}")

    combo_descuento.currentIndexChanged.connect(aplicar_descuento)

    # --- MERMA POR PRODUCTO ---
    merma_label = QLabel("Merma")
    merma_label.setAlignment(Qt.AlignCenter)
    merma_label.setStyleSheet("font-size: 16px; font-weight: bold;")
    layout_derecha.addWidget(merma_label)

    combo_merma = QComboBox()
    combo_merma.addItems(["0%", "5%", "10%", "20%", "30%"])
    layout_derecha.addWidget(combo_merma)

    def aplicar_merma():
        item = lista_productos.currentItem()
        if not item:
            QMessageBox.warning(
                pagina, "Atención", "Seleccione un producto para aplicar la merma."
            )
            return

        index = lista_productos.row(item)
        prod = productos[index]

        porcentaje = int(combo_merma.currentText().replace("%", ""))
        descuento = prod["precio"] * prod["cantidad"] * (porcentaje / 100)
        prod["merma"] = descuento
        if verificar_gerente():
            item.setText(
                f"{prod['nombre']} — Cantidad: {prod['cantidad']} — Precio: ${prod['precio']} — Merma: ${int(descuento)} — Total: {(prod['cantidad'] * prod['precio']) - int(descuento)}"
            )

            # recalcular subtotal
            nuevo_subtotal = sum(
                (p["cantidad"] * p["precio"]) - p.get("merma", 0) for p in productos
            )
            nonlocal subtotal
            subtotal = nuevo_subtotal
            actualizar_totales()

    combo_merma.currentIndexChanged.connect(
        aplicar_merma,
    )

    # Conectar botones con lógica de selección
    btn_efectivo.clicked.connect(
        lambda: seleccionar_metodo(btn_efectivo, botones, frame_efectivo)
    )
    btn_tarjeta.clicked.connect(
        lambda: seleccionar_metodo(btn_tarjeta, botones, frame_efectivo)
    )
    btn_transferencia.clicked.connect(
        lambda: seleccionar_metodo(btn_transferencia, botones, frame_efectivo)
    )
    btn_credito.clicked.connect(
        lambda: seleccionar_metodo(btn_credito, botones, frame_efectivo)
    )

    layout_derecha.addStretch()

    # Botón "Cancelar Venta"
    btn_cancelar = QPushButton("Cancelar Venta")
    btn_cancelar.setCursor(Qt.PointingHandCursor)
    btn_cancelar.setStyleSheet(
        """
        QPushButton {
            background-color: #ff7675;
            color: white;
            font-size: 16px;
            padding: 10px;
            border-radius: 6px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #d63031;
        }
    """
    )

    def cancelar_venta():
        nonlocal subtotal, cliente_seleccionado

        if not productos and subtotal == 0:
            return

        respuesta = QMessageBox.question(
            pagina,
            "Cancelar Venta",
            "¿Estás seguro de que deseas cancelar la venta y limpiar todos los campos?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if respuesta == QMessageBox.Yes:
            productos.clear()
            subtotal = 0
            cliente_seleccionado = None

            lista_productos.clear()
            actualizar_totales()

            combo_tipo_venta.setCurrentIndex(0)  # Restablece a Venta Normal
            lbl_cliente_info.setText("Ninguna clienta seleccionada")

            for btn in botones:
                btn.setChecked(False)
            frame_efectivo.setVisible(False)

            input_pago.clear()
            input_vuelto.clear()
            combo_descuento.setCurrentIndex(0)
            combo_merma.setCurrentIndex(0)

            buscador.setFocus()

    btn_cancelar.clicked.connect(cancelar_venta)
    layout_derecha.addWidget(btn_cancelar)

    # Botón "Pagar"
    boton_pagar = QPushButton("Pagar")
    boton_pagar.setStyleSheet(
        """
        QPushButton {
            background-color: #27AE60;
            color: white;
            font-size: 16px;
            padding: 10px;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #219150;
        }
    """
    )

    def abrir_pago():
        # Detectar método de pago
        if btn_efectivo.isChecked():
            metodo = "Efectivo"
        elif btn_tarjeta.isChecked():
            metodo = "Tarjeta"
        elif btn_transferencia.isChecked():
            metodo = "Transferencia"
        elif btn_credito.isChecked():
            metodo = "Crédito Girasol"
        else:
            metodo = "Sin seleccionar"

        # Validar crédito
        if metodo == "Crédito Girasol" and not cliente_seleccionado:
            QMessageBox.warning(
                pagina,
                "Atención",
                "Debe seleccionar una clienta para usar Crédito Girasol.",
            )
            return

        # Calcular descuento actual
        valor_descuento = combo_descuento.currentData()
        descuento_total = subtotal * valor_descuento

        # Obtener rut del empleado desde sesi
        rut_empleado = sesion.usuario

        pagina.ventana_pago = VentanaPago(
            subtotal=subtotal,
            productos=productos,
            descuento_total=descuento_total,
            metodo_pago=metodo,
            rut_empleado=rut_empleado,
            cliente_girasol=cliente_seleccionado,
        )
        pagina.ventana_pago.show()

    # 👇 Conectar después de definir todo
    boton_pagar.clicked.connect(abrir_pago)
    layout_derecha.addWidget(boton_pagar)

    layout_principal.addWidget(seccion_izquierda)
    layout_principal.addWidget(seccion_derecha)
    layout_principal.addWidget(seccion_izquierda, 1)
    layout_principal.addWidget(seccion_derecha, 2)

    return pagina


# Ejecutar la ventana de ventas
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = crear_pagina_ventas()
    ventana.show()

