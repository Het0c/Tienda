import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFontDatabase, QFont
from frontend.ui_dashboard import Dashboard
from frontend.login import LoginWindow


def iniciar_dashboard(session):
    ventana = Dashboard(session)
    ventana.showMaximized()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Cargar fuente personalizada
    QFontDatabase.addApplicationFont("frontend/assets/fonts/DMSerifText-Regular.ttf")

    # Aplicar fuente global
    app.setFont(QFont("Baskervville", 12))

    # Iniciar login
    login = LoginWindow(on_login_success=iniciar_dashboard)
    login.showMaximized()

    sys.exit(app.exec_())
