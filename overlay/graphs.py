from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QFont
from PyQt6.QtCore import Qt

class FPSGraph(QWidget):
    def __init__(self):
        super().__init__()
        self.values = [0] * 50
        self.max_val = 144
        self.min_val = 0
        # Registradores de picos
        self.peak_max = 0
        self.peak_min = 999

    def add_value(self, value):
        val = float(value)
        self.values.append(val)
        if len(self.values) > 50:
            self.values.pop(0)
        
        # Atualiza picos históricos
        if val > self.peak_max: self.peak_max = val
        if val > 0 and val < self.peak_min: self.peak_min = val
            
        # Atualiza escala dinâmica para os picos
        self.max_val = max(60, max(self.values) * 1.2)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width, height = self.width(), self.height()
        step = width / (len(self.values) - 1)

        # 1. Desenhar Grade de Fundo (Y-axis labels)
        painter.setPen(QColor(255, 255, 255, 30))
        painter.setFont(QFont("Consolas", 7))
        
        # Linha de topo e label
        painter.drawText(5, 10, f"{int(self.max_val)}")
        painter.drawLine(0, 0, width, 0)
        
        # Linha de meio
        painter.drawText(5, height // 2, f"{int(self.max_val/2)}")
        painter.drawLine(0, height // 2, width, height // 2)

        # 2. Caminho do Gráfico
        path = QPainterPath()
        path.moveTo(0, height)
        for i, val in enumerate(self.values):
            x = i * step
            y = height - (val / self.max_val * height)
            path.lineTo(x, y)
        path.lineTo(width, height)
        path.closeSubpath()

        # 3. Preenchimento Gradiente
        brush = QBrush(QColor(0, 255, 153, 60))
        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(path)

        # 4. Linha de FPS
        painter.setPen(QPen(QColor("#00ff99"), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        line_path = QPainterPath()
        for i, val in enumerate(self.values):
            x = i * step
            y = height - (val / self.max_val * height)
            if i == 0: line_path.moveTo(x, y)
            else: line_path.lineTo(x, y)
        painter.drawPath(line_path)

        # 5. Marcadores de Pico (Texto no canto)
        painter.setPen(QColor("#FFFFFF"))
        painter.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        painter.drawText(width - 50, 15, f"MAX:{int(self.peak_max)}")
        painter.drawText(width - 50, 30, f"MIN:{int(self.peak_min)}")