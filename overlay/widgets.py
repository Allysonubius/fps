# =========================
# overlay/widgets.py
# =========================

from PyQt6.QtWidgets import QLabel

class OverlayLabel(QLabel):

    def __init__(self):

        super().__init__()

        self.setText("FPS")