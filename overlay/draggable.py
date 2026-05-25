# =========================
# overlay/draggable.py
# =========================

from PyQt6.QtCore import Qt

class DraggableMixin:

    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):

        delta = event.globalPosition().toPoint() - self.old_pos

        self.move(self.x() + delta.x(), self.y() + delta.y())

        self.old_pos = event.globalPosition().toPoint()