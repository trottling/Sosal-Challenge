import os
import sys
from typing import Optional

from PyQt6 import uic
from PyQt6.QtCore import QThread, Qt, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget

import pyautogui


def get_rel_path(data_path: str) -> str:
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, data_path)


class AppUI(QMainWindow):
    def __init__(self, no_btn_widget: 'NoButton'):
        super().__init__()
        self.no_btn_widget = no_btn_widget
        self.ui = None
        self.load_ui()

    def load_ui(self):
        self.ui = uic.loadUi(get_rel_path("app.ui"), self)
        self.setWindowTitle("СОСАЛ???")
        self.ui.resize(1400, 650)
        self.ui.pushButton_yes.clicked.connect(self.on_yes_clicked)
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.show()
        self.no_btn_widget.ui.pushButton_no.clicked.connect(self.on_no_clicked)
        self.no_btn_widget.show()
        self.no_btn_widget.set_start_pos(self.pos().x(), self.pos().y())

    def on_yes_clicked(self):
        self.ui.stackedWidget.setCurrentIndex(1)
        self.no_btn_widget.close()

    def on_no_clicked(self):
        self.ui.stackedWidget.setCurrentIndex(2)
        self.no_btn_widget.close()


class NoButton(QWidget):
    def __init__(self):
        super().__init__()
        self.mv_worker: Optional[MoveWorker] = None
        self.ui = None
        self.load_ui()
        self.start_movement()

    def load_ui(self):
        self.ui = uic.loadUi(get_rel_path("no_btn.ui"), self)
        self.ui.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.ui.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def set_start_pos(self, x, y):
        start_x = x + 500
        start_y = y + 451
        self.ui.move(start_x, start_y)

    def start_movement(self):
        self.mv_worker = MoveWorker(self)
        self.mv_worker.move_signal.connect(self.move_button)
        self.mv_worker.start()

    def move_button(self, pos: list):
        self.ui.move(pos[0], pos[1])


class MoveWorker(QThread):
    move_signal = pyqtSignal(list)

    def __init__(self, button_widget: NoButton):
        super().__init__()
        self.button_widget = button_widget
        self.screen_width = QApplication.primaryScreen().size().width()
        self.screen_height = QApplication.primaryScreen().size().height()
        self._running = True

    def run(self):
        while self._running:
            self.msleep(10)
            mouse_x, mouse_y = pyautogui.position()
            btn_x = self.button_widget.ui.x() + self.button_widget.ui.width() // 2
            btn_y = self.button_widget.ui.y() + self.button_widget.ui.height() // 2
            delta_x = btn_x - mouse_x
            delta_y = btn_y - mouse_y
            distance = (delta_x ** 2 + delta_y ** 2) ** 0.5
            if distance > 150 or distance == 0:
                continue
            move_x = int(delta_x / distance * 25)
            move_y = int(delta_y / distance * 25)
            new_x = btn_x + move_x - self.button_widget.ui.width() // 2
            new_y = btn_y + move_y - self.button_widget.ui.height() // 2
            new_x = max(0, min(new_x, self.screen_width - self.button_widget.ui.width()))
            new_y = max(0, min(new_y, self.screen_height - self.button_widget.ui.height()))
            # Смещение от краёв экрана
            border_offset = 120
            if new_x == 0:
                new_x += border_offset
            elif new_x == self.screen_width - self.button_widget.ui.width():
                new_x -= border_offset
            if new_y == 0:
                new_y += border_offset
            elif new_y == self.screen_height - self.button_widget.ui.height():
                new_y -= border_offset
            self.move_signal.emit([new_x, new_y])

    def stop(self):
        self._running = False
