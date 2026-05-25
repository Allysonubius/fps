# =========================
# overlay/graphs.py
# =========================

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt

class FPSGraph(QWidget):

    def __init__(self):

        super().__init__()

        self.values = []

    def add_value(self, value):

        self.values.append(value)

        if len(self.values) > 100:
            self.values.pop(0)

        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setPen(QColor("#00ff99"))

        if len(self.values) < 2:
            return

        width = self.width()
        height = self.height()

        step = width / len(self.values)

        for i in range(len(self.values) - 1):

            x1 = int(i * step)
            y1 = height - int(self.values[i])

            x2 = int((i + 1) * step)
            y2 = height - int(self.values[i + 1])

            painter.drawLine(x1, y1, x2, y2)