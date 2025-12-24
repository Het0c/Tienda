import cv2
from pyzbar.pyzbar import decode
import sqlite3
import numpy as np

# Conexión a la base
def buscar_producto_por_codigo(codigo):
    conn = sqlite3.connect("reuso.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sr.nombreSeccionRopa, fr.nombreFamilia, rp.precio, stock
        FROM rangoPrecio rp
        INNER JOIN seccionRopa sr ON rp.idSeccionRopa = sr.idSeccionRopa
        INNER JOIN familiaRopa fr ON sr.idFamiliaRopa = fr.idFamiliaRopa
        WHERE rp.codigoBarra = ?
    """, (codigo,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado

# Iniciar cámara
cap = cv2.VideoCapture(0)
print("Escaneando... Presiona ESC para salir")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    barcodes = decode(frame)
    for barcode in barcodes:
        codigo = barcode.data.decode('utf-8')
        producto = buscar_producto_por_codigo(codigo)

        if producto:
            nombre_seccion, nombre_familia, precio, stock = producto
            texto = f"{nombre_seccion} ({nombre_familia}) - ${precio} | Stock: {stock}"
        else:
            texto = f"Código {codigo} no encontrado"
        print(texto)
        # Dibujar en pantalla
        pts = barcode.polygon
        if len(pts) >= 4:
            pts = [(pt.x, pt.y) for pt in pts]
            cv2.polylines(frame, [np.array(pts)], True, (0, 255, 0), 2)
        x, y, w, h = barcode.rect
        cv2.putText(frame, texto, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    cv2.imshow('Escáner de código de barras', frame)

    if cv2.waitKey(1) == 27:  # ESC para salir
        break

cap.release()
cv2.destroyAllWindows()
