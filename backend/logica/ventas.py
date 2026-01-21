from backend.db.conexion import conectar_db, conectar_mydb
from datetime import datetime

def busqueda_descuento():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("SELECT tipoDescuento, valorDescuento FROM descuento")
    resultados = cursor.fetchall()

    conn.close()
    return resultados  # lista de tuplas [(tipo, valor), ...]



def verificacion_encargado_local(rut_empleado):
    cursor = conectar_db()
    cursor = cursor.cursor()

    cursor.execute("SELECT idTipoEmpleado FROM empleado WHERE rut = ?", (rut_empleado,))
    empleado = cursor.fetchone()

    cursor.close()

    if empleado and empleado[0] == 1 or empleado and empleado[0] == 3:  # Suponiendo que el tipo de empleado es el tercer campo
        return True
    else:
        return False

from datetime import datetime

def registrar_venta(subtotal, productos, descuento_total, metodo_pago, rut_empleado):
    conn = conectar_db()
    cursor = conn.cursor()

    # Calcular total final
    total_final = subtotal - descuento_total

    # Insertar cabecera de la venta
    cursor.execute("""
          insert into 
    boleta (
      "fechaHora", 
      "rutEmpleado", 
      subtotal, 
      descuento, 
      "totalFinal", 
      "medioPago"
    )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),rut_empleado, subtotal, descuento_total, total_final, metodo_pago))

    id_boleta = cursor.lastrowid

    # Insertar detalle de productos
    for prod in productos:
        cantidad = prod["cantidad"]
        precio = prod["precio"]
        merma = prod.get("merma", 0)
        total_producto = (cantidad * precio) - merma

        cursor.execute("""
            insert into 
  "detalleBoleta" (
    "idBoleta", 
    "idSeccionRopa", 
    cantidad, 
    "precioUnitario", 
    "totalItem"
  )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id_boleta, prod["nombre"], cantidad, precio, total_producto))

    conn.commit()
    conn.close()
    return id_boleta


#def descuento_inventario()

def crear_boleta(rut_cliente, items, rut_empleado=None):
    """
    Crea una boleta en la base de datos.
    
    :param rut_cliente: RUT del cliente.
    :param items: Lista de tuplas (id_producto, cantidad).
    :param rut_empleado: RUT del empleado que atiende (opcional).
    :return: ID de la boleta creada.
    """
    conn = conectar_db()
    cursor = conn.cursor()

    # Insertar cabecera de boleta
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO boleta (rut_cliente, rut_empleado, fecha)
        VALUES (?, ?, ?)
    """, (rut_cliente, rut_empleado, fecha))
    
    boleta_id = cursor.lastrowid

    total_boleta = 0

    # Insertar detalle de boleta
    for id_producto, cantidad in items:
        cursor.execute("SELECT precio FROM producto WHERE id = ?", (id_producto,))
        producto = cursor.fetchone()
        
        if not producto:
            print(f"Producto {id_producto} no encontrado.")
            continue

        precio_unitario = producto[0]

        # Aplicar descuento si corresponde
        descuento = 0
        if rut_empleado:
            descuento = aplicacion_descuento_trabajador(rut_empleado) or 0

        precio_final = precio_unitario * (1 - descuento)
        subtotal = precio_final * cantidad
        total_boleta += subtotal

        cursor.execute("""
            INSERT INTO detalle_boleta (boleta_id, producto_id, cantidad, precio_unitario, descuento, subtotal)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (boleta_id, id_producto, cantidad, precio_unitario, descuento, subtotal))

    # Actualizar total en boleta
    cursor.execute("UPDATE boleta SET total = ? WHERE id = ?", (total_boleta, boleta_id))

    conn.commit()
    cursor.close()
    conn.close()

    return boleta_id

def calcular_precio_total(precio_unitario, cantidad, es_trabajador):
    """
    Calcula el precio total de un producto considerando la cantidad y si el cliente es un trabajador.
    
    :param precio_unitario: Precio unitario del producto.
    :param cantidad: Cantidad de productos.
    :param es_trabajador: Booleano que indica si el cliente es un trabajador.
    :return: Precio total con descuento si aplica.
    """
    precio_con_descuento = aplicacion_descuento_trabajador(precio_unitario, es_trabajador)
    precio_total = precio_con_descuento * cantidad
    return round(precio_total, 2)


    from datetime import datetime

def registrar_venta(
    subtotal,
    productos,
    descuento_total,
    metodo_pago,
    rut_empleado,
):
    conexion = conectar_mydb()
    cursor = conexion.cursor()

    try:
        fecha = datetime.now()
        total = subtotal - descuento_total

        # 1️⃣ Insertar venta
        sql_venta = """
            INSERT INTO ventas (fecha, rut_empleado, metodo_pago, subtotal, descuento, total)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            sql_venta,
            (fecha, rut_empleado, metodo_pago, subtotal, descuento_total, total),
        )

        id_venta = cursor.lastrowid

        # 2️⃣ Insertar detalle de venta
        sql_detalle = """
            INSERT INTO detalle_venta
            (id_venta, id_producto, nombre_producto, cantidad, precio_unitario, total_producto)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        for p in productos:
            cursor.execute(
                sql_detalle,
                (
                    id_venta,
                    p["id"],              # id del producto
                    p["nombre"],
                    p["cantidad"],
                    p["precio"],
                    p["cantidad"] * p["precio"],
                ),
            )

        conexion.commit()
        return True

    except Exception as e:
        conexion.rollback()
        print("Error al registrar venta:", e)
        return False

    finally:
        cursor.close()
        conexion.close()
