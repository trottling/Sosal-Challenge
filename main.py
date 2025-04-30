import sys

from PyQt6.QtWidgets import QApplication

from app.app import AppUI, NoButton


def main():
    app = QApplication(sys.argv)
    no_btn_widget = NoButton()
    main_window = AppUI(no_btn_widget)
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
