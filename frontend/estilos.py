def aplicar_estilos(widget, theme="light"):
    if theme == "dark":
        bg_main = "#000000"
        text_main = "#FFFFFF"
        input_bg = "#636e72"
        input_border = "#dfe6e9"
        sidebar_bg = "#1E2324"
        sidebar_border = "#101010"
        list_bg = "#2D3436"
        list_border = "#dfe6e9"
        card_bg = "rgba(255,255,255,0.1)"
        scrollbar_bg = "#2D3436"
    else:
        bg_main = "#FFFFFF"
        text_main = "#2D3436"
        input_bg = "#FFFFFF"
        input_border = "#2D3436"
        sidebar_bg = "#FFFFFF"
        sidebar_border = "#2D3436"
        list_bg = "#FFFFFF"
        list_border = "#2D3436"
        card_bg = "rgba(0,0,0,0.05)"
        scrollbar_bg = "#FFFFFF"

    estilo = f"""
        /* -----------------------
           Fondo general
        ----------------------- */
        QMainWindow, QWidget {{
            background-color: {bg_main};
            color: {text_main};
            font-family: "Segoe UI", "Arial", sans-serif;
        }}

        /* -----------------------
           Botones principales
        ----------------------- */
        QPushButton {{
            background-color: #F4D03F;     /* amarillo claro */
            color: #2D3436;                /* negro */
            border: none;
            padding: 10px 20px;
            font-size: 15px;
            font-weight: bold;
            border-radius: 10px;
        }}
        QPushButton:hover {{
            background-color: #D4AC0D;     /* amarillo oscuro */
        }}
        QPushButton:pressed {{
            background-color: #C49A0C;
        }}

        /* -----------------------
           Etiquetas
        ----------------------- */
        QLabel {{
            font-size: 16px;
            color: {text_main};
            font-weight: 500;
            background-color: transparent;
        }}

        /* -----------------------
           Inputs
        ----------------------- */
        QLineEdit {{
            background-color: {input_bg};
            color: {text_main};
            border: 2px solid {input_border};
            padding: 8px;
            font-size: 14px;
            border-radius: 8px;
        }}
        QLineEdit:focus {{
            border: 2px solid #F4D03F;
        }}

        /* -----------------------
           Sidebar
        ----------------------- */
        QFrame#sidebar {{
            background-color: {sidebar_bg};
            border-right: 2px solid {sidebar_border};
        }}

        /* -----------------------
           Listas
        ----------------------- */
        QListWidget {{
            background-color: {list_bg};
            color: {text_main};
            border: 1px solid {list_border};
            border-radius: 8px;
        }}

        /* -----------------------
           Scrollbars verticales
        ----------------------- */
        QScrollBar:vertical {{
            background: {scrollbar_bg};
            width: 12px;
            margin: 0px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical {{
            background: #F4D03F;
            min-height: 20px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: #D4AC0D;
        }}

        /* -----------------------
           Tarjetas del Dashboard
        ----------------------- */
        QFrame {{
            border-radius: 20px;
            border: none;
            background-color: {card_bg};
        }}
        QLabel.card-title {{
            font-size: 18px;
            font-weight: bold;
            color: {text_main};
        }}
        QLabel.card-number {{
            font-size: 16px;
            color: {text_main};
        }}

        /* -----------------------
           Botones del menú (sin heredar global)
        ----------------------- */
        QPushButton.menu-btn {{
            all: unset;
        }}

        /* -----------------------
           Efecto sombra sutil para tarjetas
        ----------------------- */
        QFrame:hover {{
            background-color: rgba(244,208,63,0.15);
        }}

        /* -----------------------
           Mensaje Inferior (Hint)
        ----------------------- */
        QLabel#mensajeInferior {{
            font-size: 14px;
            color: #636e72;
            font-style: italic;
            margin-top: 10px;
        }}

        /* -----------------------
           Tooltips
        ----------------------- */
        QToolTip {{
            background-color: #2D3436;
            color: #ffffff;
            border: 1px solid #F4D03F;
            padding: 5px;
            border-radius: 4px;
        }}
    """
    widget.setStyleSheet(estilo)
