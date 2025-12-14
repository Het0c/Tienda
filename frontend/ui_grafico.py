from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

def crear_pagina_grafico():
    pagina = QWidget()
    layout = QVBoxLayout(pagina)
    # Crear figura y canvas dentro del contexto Qt
    fig = Figure(figsize=(6, 4))
    canvas = FigureCanvas(fig)
    layout.addWidget(canvas)

    # Dibujar gráfico
    ax = fig.add_subplot(111)
    prendas = ["Camisa", "Pantalón", "Chaqueta", "Vestido", "Zapatos"]
    unidades = [120, 85, 60, 40, 70]
    valores = [1200000, 1275000, 1800000, 90000, 1400000]

    x = range(len(prendas))
    ancho = 0.4

    ax.bar([i - ancho/2 for i in x], unidades, width=ancho, label="Unidades", color="#81D4A3")
    ax.bar([i + ancho/2 for i in x], valores, width=ancho, label="Valor ($)", color="#FFF176")

    ax.set_xticks(x)
    ax.set_xticklabels(prendas)
    ax.set_title("Ventas por prenda - Septiembre")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)

    return pagina
