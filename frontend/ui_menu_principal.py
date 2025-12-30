from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QFrame,
)
from PyQt5.QtGui import QFont, QColor, QPainter, QPainterPath, QPen, QPixmap
from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    QPropertyAnimation,
    QEasingCurve,
    pyqtProperty,
    QParallelAnimationGroup,
    QRectF,
)
import os


def crear_pagina_menu(controlador=None):
    return Ui_MenuPrincipal(controlador=controlador)


class IconLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._zoom = 1.0

    @pyqtProperty(float)
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, value):
        self._zoom = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        w = self.width()
        h = self.height()
        painter.translate(w / 2, h / 2)
        painter.scale(self._zoom, self._zoom)
        painter.translate(-w / 2, -h / 2)
        super().paintEvent(event)


class HoverCard(QFrame):
    clicked = pyqtSignal()

    def __init__(self, nombre, accion, simbolo, parent=None):
        super().__init__(parent)
        self.setFixedSize(360, 360)
        self.accion = accion
        self.setCursor(Qt.PointingHandCursor)

        # Propiedades iniciales
        self._color_fondo = QColor(255, 255, 255, 235)  # rgba(255, 255, 255, 0.92)
        self._color_borde = QColor("#dfe6e9")
        self._ancho_borde = 1.0
        self._text_color = QColor("#2D3436")

        # Configuración básica (sin stylesheet para fondo/borde)
        self.setStyleSheet("background: transparent;")

        # Layout interno
        vbox = QVBoxLayout(self)
        vbox.setAlignment(Qt.AlignCenter)
        vbox.setContentsMargins(20, 30, 20, 30)
        vbox.setSpacing(10)

        self.lbl_simbolo = IconLabel()
        self.lbl_simbolo.setStyleSheet(
            "color: #2D3436; background: transparent; border: none;"
        )
        self.lbl_simbolo.setAlignment(Qt.AlignCenter)
        self.lbl_simbolo.setAttribute(Qt.WA_TransparentForMouseEvents)

        if simbolo.endswith(".png") and os.path.exists(simbolo):
            pix = QPixmap(simbolo)
            self.lbl_simbolo.setPixmap(
                pix.scaled(160, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            self.lbl_simbolo.setText(simbolo)
            self.lbl_simbolo.setFont(QFont("Segoe UI", 160))

        vbox.addWidget(self.lbl_simbolo)
        vbox.addStretch()  # Empuja el texto hacia abajo

        self.label = QLabel(nombre)
        self.label.setWordWrap(True)
        self.label.setFont(QFont("Segoe UI", 40, QFont.Bold))
        self.label.setStyleSheet(
            f"color: {self._text_color.name()}; background: transparent; border: none;"
        )
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setAttribute(Qt.WA_TransparentForMouseEvents)
        vbox.addWidget(self.label)

        # Animaciones
        self.anim_color = QPropertyAnimation(self, b"colorFondo")
        self.anim_borde_color = QPropertyAnimation(self, b"colorBorde")
        self.anim_borde_ancho = QPropertyAnimation(self, b"anchoBorde")
        self.anim_zoom = QPropertyAnimation(self.lbl_simbolo, b"zoom")
        self.anim_text_color = QPropertyAnimation(self, b"textColor")

        self.group = QParallelAnimationGroup(self)
        self.group.addAnimation(self.anim_color)
        self.group.addAnimation(self.anim_borde_color)
        self.group.addAnimation(self.anim_borde_ancho)
        self.group.addAnimation(self.anim_zoom)
        self.group.addAnimation(self.anim_text_color)

        for anim in [
            self.anim_color,
            self.anim_borde_color,
            self.anim_borde_ancho,
            self.anim_zoom,
            self.anim_text_color,
        ]:
            anim.setDuration(200)  # Duración suave (200ms)
            anim.setEasingCurve(QEasingCurve.OutQuad)

    # Propiedades para la animación
    @pyqtProperty(QColor)
    def colorFondo(self):
        return self._color_fondo

    @colorFondo.setter
    def colorFondo(self, val):
        self._color_fondo = val
        self.update()

    @pyqtProperty(QColor)
    def colorBorde(self):
        return self._color_borde

    @colorBorde.setter
    def colorBorde(self, val):
        self._color_borde = val
        self.update()

    @pyqtProperty(float)
    def anchoBorde(self):
        return self._ancho_borde

    @anchoBorde.setter
    def anchoBorde(self, val):
        self._ancho_borde = val
        self.update()

    @pyqtProperty(QColor)
    def textColor(self):
        return self._text_color

    @textColor.setter
    def textColor(self, val):
        self._text_color = val
        self.label.setStyleSheet(
            f"color: {val.name()}; background: transparent; border: none;"
        )

    def enterEvent(self, event):
        self.group.stop()
        self.anim_color.setEndValue(QColor("#ffffff"))
        self.anim_borde_color.setEndValue(QColor("#F4D03F"))
        self.anim_borde_ancho.setEndValue(4.0)
        self.anim_zoom.setEndValue(1.2)
        self.anim_text_color.setEndValue(QColor("#F4D03F"))
        self.group.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.group.stop()
        self.anim_color.setEndValue(QColor(255, 255, 255, 235))
        self.anim_borde_color.setEndValue(QColor("#dfe6e9"))
        self.anim_borde_ancho.setEndValue(1.0)
        self.anim_zoom.setEndValue(1.0)
        self.anim_text_color.setEndValue(QColor("#2D3436"))
        self.group.start()
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.rect().contains(event.pos()):
            self.clicked.emit()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect())
        inset = self._ancho_borde / 2
        rect.adjust(inset, inset, -inset, -inset)
        path = QPainterPath()
        path.addRoundedRect(rect, 30, 30)
        painter.setBrush(self._color_fondo)
        painter.setPen(QPen(self._color_borde, self._ancho_borde))
        painter.drawPath(path)


class Ui_MenuPrincipal(QWidget):
    navegar = pyqtSignal(str)

    def __init__(self, parent=None, controlador=None):
        super().__init__(parent)
        self.controlador = controlador
        self.setObjectName("MenuPrincipal")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.cambiar_tema("light")

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        # Grid de tarjetas
        cards_layout = QGridLayout()
        cards_layout.setSpacing(40)
        cards_layout.setAlignment(Qt.AlignCenter)

        self.cards = []

        ruta_icono_inv = os.path.join(
            os.path.dirname(__file__), "assets", "InventarioIcono.png"
        )
        ruta_icono_ventas = os.path.join(
            os.path.dirname(__file__), "assets", "VentasIcono.png"
        )
        ruta_icono_usuarios = os.path.join(
            os.path.dirname(__file__), "assets", "Usuarias.png"
        )
        ruta_icono_mercaderia = os.path.join(
            os.path.dirname(__file__), "assets", "Mercaderia.png"
        )
        ruta_icono_informes = os.path.join(
            os.path.dirname(__file__), "assets", "InformesIcono.png"
        )
        ruta_icono_facturas = os.path.join(
            os.path.dirname(__file__), "assets", "FacturasIcono.png"
        )
        cards_data = [
            ("Inventario", "inventario", ruta_icono_inv),
            ("Ventas", "ventas", ruta_icono_ventas),
            ("Informes", "arqueo", ruta_icono_informes),
            ("Clientas", "usuarios", ruta_icono_usuarios),
            ("Facturas", "facturas", ruta_icono_facturas),
            ("Ingreso de mercadería", "ingreso_mercaderia", ruta_icono_mercaderia),
        ]

        row = 0
        col = 0
        for nombre, accion, simbolo in cards_data:
            card = self.create_card(nombre, accion, simbolo)
            self.cards.append(card)
            cards_layout.addWidget(card, row, col)
            col += 1
            if col > 2:  # 3 columnas
                col = 0
                row += 1

        main_layout.addLayout(cards_layout)

    def cambiar_tema(self, tema):
        if tema == "dark":
            imagen = "fondo_venta7.png"
        else:
            imagen = "fondo_venta5.png"

        ruta_fondo = os.path.join(os.path.dirname(__file__), "assets", imagen).replace(
            "\\", "/"
        )

        self.setStyleSheet(
            f"""
            QWidget#MenuPrincipal {{
                border-image: url({ruta_fondo}) 0 0 0 0 stretch stretch;
            }}
        """
        )

    def create_card(self, nombre, accion, simbolo):
        card = HoverCard(nombre, accion, simbolo)
        card.clicked.connect(lambda: self.navegar.emit(accion))
        return card
