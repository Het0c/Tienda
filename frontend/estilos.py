def aplicar_estilos(widget):
    widget.setStyleSheet(
        """
        /* -----------------------
           Fondo general
        ----------------------- */
        QMainWindow, QWidget {
            background-color: #FFFFFF;
            font-family: "Segoe UI", "Arial", sans-serif;
        }

        /* -----------------------
           Botones principales
        ----------------------- */
        QPushButton {
            background-color: #F4D03F;     /* amarillo claro */
            color: #2D3436;                /* negro */
            border: none;
            padding: 10px 20px;
            font-size: 15px;
            font-weight: bold;
            border-radius: 10px;
        }
        QPushButton:hover {
            background-color: #D4AC0D;     /* amarillo oscuro */
        }
        QPushButton:pressed {
            background-color: #C49A0C;
        }

        /* -----------------------
           Etiquetas
        ----------------------- */
        QLabel {
            font-size: 16px;
            color: #2D3436;
            font-weight: 500;
            background-color: transparent;
        }

        /* -----------------------
           Inputs
        ----------------------- */
        QLineEdit {
            background-color: #FFFFFF;
            border: 2px solid #2D3436;
            padding: 8px;
            font-size: 14px;
            border-radius: 8px;
        }
        QLineEdit:focus {
            border: 2px solid #F4D03F;
        }

        /* -----------------------
           Sidebar
        ----------------------- */
        QFrame#sidebar {
            background-color: #FFFFFF;
            border-right: 2px solid #2D3436;
        }

        /* -----------------------
           Listas
        ----------------------- */
        QListWidget {
            background-color: #FFFFFF;
            border: 1px solid #2D3436;
            border-radius: 8px;
        }

        /* -----------------------
           Scrollbars verticales
        ----------------------- */
        QScrollBar:vertical {
            background: #FFFFFF;
            width: 12px;
            margin: 0px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background: #F4D03F;
            min-height: 20px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical:hover {
            background: #D4AC0D;
        }

        /* -----------------------
           Tarjetas del Dashboard
        ----------------------- */
        QFrame {
            border-radius: 20px;
            border: none;
            background-color: rgba(0,0,0,0.05);
        }
        QLabel.card-title {
            font-size: 18px;
            font-weight: bold;
            color: #2D3436;
        }
        QLabel.card-number {
            font-size: 16px;
            color: #2D3436;
        }

        /* -----------------------
           Botones del menú (sin heredar global)
        ----------------------- */
        QPushButton.menu-btn {
            all: unset;
        }

        /* -----------------------
           Efecto sombra sutil para tarjetas
        ----------------------- */
        QFrame:hover {
            background-color: rgba(244,208,63,0.15);
        }

        /* -----------------------
           Mensaje Inferior (Hint)
        ----------------------- */
        QLabel#mensajeInferior {
            font-size: 14px;
            color: #636e72;
            font-style: italic;
            margin-top: 10px;
        }
    """
    )
