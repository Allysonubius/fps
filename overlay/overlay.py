# =========================================================
# IMPORTS
# =========================================================

import sys
import os

from core.network import network_data
from core.ram import get_ram_clock

from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QSystemTrayIcon,
    QMenu,
    QApplication,
    QTabWidget,
    QSizePolicy
)

from PyQt6.QtGui import (
    QFont,
    QAction,
    QIcon
)

from PyQt6.QtCore import (
    Qt,
    QTimer,
    pyqtSignal,
    QSize
)

from core.fps import fps_data
from core.sensors import get_hardware_data

from overlay.draggable import DraggableMixin
from overlay.themes import THEMES
from overlay.graphs import FPSGraph


# =========================================================
# RESOURCE PATH
# =========================================================

def resource_path(relative_path):

    try:
        base_path = sys._MEIPASS

    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(
        base_path,
        relative_path
    )


# =========================================================
# STATUS COLORS
# =========================================================

def get_status_icon(value, warning, critical):

    try:
        value = float(value)

    except:
        value = 0

    if value < warning:

        return "[SAFE]"

    elif value < critical:

        return "[WARN]"

    return "[CRIT]"


# =========================================================
# OVERLAY
# =========================================================

class FPSOverlay(QWidget, DraggableMixin):

    toggle_signal = pyqtSignal()

    # =====================================================
    # INIT
    # =====================================================

    def __init__(self):

        super().__init__()

        self.theme = THEMES["neon"]

        self.current_tab = 0

        # =================================================
        # SIGNAL
        # =================================================

        self.toggle_signal.connect(
            self.toggle_overlay
        )

        # =================================================
        # WINDOW
        # =================================================

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        # =================================================
        # MAIN LAYOUT
        # =================================================

        self.main_layout = QVBoxLayout()

        self.main_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.main_layout.setSpacing(0)

        # =================================================
        # CONTAINER
        # =================================================

        self.container = QWidget()

        self.container_layout = QVBoxLayout()

        self.container_layout.setContentsMargins(
            8,
            8,
            8,
            8
        )

        self.container_layout.setSpacing(6)

        # =================================================
        # HEADER
        # =================================================

        self.header = QLabel(
            "FPS OVERLAY • REALTIME MONITOR"
        )

        self.header.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.header.setFont(
            QFont("Consolas", 10)
        )

        # =================================================
        # TABS
        # =================================================

        self.tabs = QTabWidget()

        self.tabs.setDocumentMode(True)

        self.tabs.currentChanged.connect(
            self.on_tab_changed
        )

        # =================================================
        # COMPACT TAB
        # =================================================

        self.compact_tab = QWidget()

        compact_layout = QVBoxLayout()

        compact_layout.setContentsMargins(
            4,
            4,
            4,
            4
        )

        compact_layout.setSpacing(2)

        self.compact_label = QLabel()


        self.compact_label.setFont(
            QFont("Consolas", 10)
        )

        self.compact_label.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        self.compact_label.setWordWrap(False)

        self.compact_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )

        compact_layout.addWidget(
            self.compact_label
        )

        compact_layout.addStretch()

        self.compact_tab.setLayout(
            compact_layout
        )

        # =================================================
        # DETAILED TAB
        # =================================================

        self.detailed_tab = QWidget()

        detailed_layout = QVBoxLayout()

        detailed_layout.setContentsMargins(
            4,
            4,
            4,
            4
        )

        detailed_layout.setSpacing(4)

        self.info_label = QLabel()

        self.info_label.setFont(
            QFont("Cascadia Mono", 9)
        )

        self.info_label.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        self.info_label.setWordWrap(False)

        self.info_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )

        detailed_layout.addWidget(
            self.info_label
        )

        # =================================================
        # GRAPH CONTAINER
        # =================================================

        self.graph_container = QWidget()

        self.graph_container.setMinimumHeight(85)

        self.graph_container.setMaximumHeight(85)

        self.graph_container.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        graph_layout = QVBoxLayout()

        graph_layout.setContentsMargins(
            6,
            4,
            6,
            4
        )

        graph_layout.setSpacing(2)

        # =================================================
        # GRAPH TITLE
        # =================================================

        self.graph_title = QLabel(
            "FPS HISTORY • PRESENTMON REALTIME"
        )

        self.graph_title.setFont(
            QFont("Consolas", 8)
        )

        self.graph_title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        # =================================================
        # GRAPH
        # =================================================

        self.graph = FPSGraph()

        self.graph.setMinimumHeight(55)

        self.graph.setMaximumHeight(55)

        self.graph.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        # =================================================
        # GRAPH STYLING
        # =================================================

        self.graph_container.setStyleSheet("""
            background-color: rgba(255, 255, 255, 28);
        """)

        graph_layout.addWidget(
            self.graph_title
        )

        graph_layout.addWidget(
            self.graph
        )

        self.graph_container.setLayout(
            graph_layout
        )

        detailed_layout.addWidget(
            self.graph_container
        )

        detailed_layout.addStretch()

        self.detailed_tab.setLayout(
            detailed_layout
        )

        # =================================================
        # ABOUT TAB
        # =================================================

        self.about_tab = QWidget()

        about_layout = QVBoxLayout()

        about_layout.setContentsMargins(
            6,
            6,
            6,
            6
        )

        about_layout.setSpacing(4)

        self.about_label = QLabel(
            """FPS Overlay

Realtime Performance Monitor

Developer:
Allyson

GitHub:
github.com/Allysonubius
"""
        )

        self.about_label.setFont(
            QFont("Consolas", 10)
        )

        self.about_label.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        self.about_label.setWordWrap(True)

        self.about_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )

        about_layout.addWidget(
            self.about_label
        )

        about_layout.addStretch()

        self.about_tab.setLayout(
            about_layout
        )

        # =================================================
        # ADD TABS
        # =================================================

        self.tabs.addTab(
            self.compact_tab,
            "Compact"
        )

        self.tabs.addTab(
            self.detailed_tab,
            "Detailed"
        )

        self.tabs.addTab(
            self.about_tab,
            "About"
        )

        # =================================================
        # ADD WIDGETS
        # =================================================

        self.container_layout.addWidget(
            self.header
        )

        self.container_layout.addWidget(
            self.tabs
        )

        self.container.setLayout(
            self.container_layout
        )

        self.main_layout.addWidget(
            self.container
        )

        self.setLayout(
            self.main_layout
        )

        # =================================================
        # THEME
        # =================================================

        self.apply_theme()

        # =================================================
        # TIMER
        # =================================================

        self.timer = QTimer()

        self.timer.timeout.connect(
            self.update_overlay
        )

        self.timer.start(500)

        # =================================================
        # OVERLAY STATE
        # =================================================

        self.overlay_visible = True

        # =================================================
        # TRAY
        # =================================================

        self.setup_tray()

        # =================================================
        # INITIAL SIZE
        # =================================================

        QTimer.singleShot(
            0,
            lambda: self.apply_tab_state(0)
        )

    # =========================================================
    # APPLY TAB STATE
    # =========================================================

    def apply_tab_state(self, index):

        self.graph_container.setVisible(
            index == 1
        )

        # =====================================================
        # COMPACT
        # =====================================================

        if index == 0:

            width = 320
            height = 360

        # =====================================================
        # DETAILED
        # =====================================================

        elif index == 1:

            width = 340
            height = 800

        # =====================================================
        # ABOUT
        # =====================================================

        else:

            width = 300
            height = 230

        self.setMinimumSize(
            QSize(0, 0)
        )

        self.setMaximumSize(
            QSize(16777215, 16777215)
        )

        self.resize(
            width,
            height
        )

        self.setFixedSize(
            width,
            height
        )

        self.layout().activate()

        self.container.adjustSize()

        self.tabs.adjustSize()

        self.adjustSize()

        self.updateGeometry()

        self.repaint()

    # =========================================================
    # TAB CHANGED
    # =========================================================

    def on_tab_changed(self, index):

        self.current_tab = index

        QTimer.singleShot(
            0,
            lambda: self.apply_tab_state(index)
        )

    # =========================================================
    # SHOW EVENT
    # =========================================================

    def showEvent(self, event):

        super().showEvent(event)

        QTimer.singleShot(
            0,
            lambda: self.apply_tab_state(
                self.current_tab
            )
        )

    # =========================================================
    # THEME
    # =========================================================

    def apply_theme(self):

        self.setStyleSheet("""
            QWidget {
                background: transparent;
            }
        """)

        self.container.setStyleSheet("""
            QWidget {
                background-color: rgba(15, 15, 15, 95);
                border-radius: 10px;
            }
        """)

        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background: transparent;
            }}

            QTabBar::tab {{
                background: rgba(20, 20, 20, 100);
                color: {self.theme["text"]};
                padding: 6px 12px;
                margin: 2px;
                font-weight: bold;
            }}

            QTabBar::tab:selected {{
                background: {self.theme["accent"]};
                color: black;
            }}
        """)

        self.header.setStyleSheet(f"""
            QLabel {{
                color: {self.theme["accent"]};
                font-weight: bold;
                background: transparent;
            }}
        """)

        self.graph_title.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-weight: bold;
                background: transparent;
            }}
        """)

        self.compact_label.setStyleSheet(f"""
            QLabel {{
                color: {self.theme["text"]};
                font-weight: bold;
                background: transparent;
            }}
        """)

        self.info_label.setStyleSheet(f"""
            QLabel {{
                color: {self.theme["text"]};
                font-weight: bold;
                background: transparent;
            }}
        """)

        self.about_label.setStyleSheet(f"""
            QLabel {{
                color: {self.theme["text"]};
                font-weight: bold;
                background: transparent;
            }}
        """)

    # =========================================================
    # SYSTEM TRAY
    # =========================================================

    def setup_tray(self):

        if not QSystemTrayIcon.isSystemTrayAvailable():

            print("[TRAY] não suportado")

            return

        self.tray = QSystemTrayIcon(self)

        icon_path = resource_path(
            "assets/icon.ico"
        )

        self.tray.setIcon(
            QIcon(icon_path)
        )

        self.tray.setToolTip(
            "FPS Overlay"
        )

        menu = QMenu()

        toggle_action = QAction(
            "Mostrar/Ocultar Overlay",
            self
        )

        toggle_action.triggered.connect(
            self.toggle_overlay
        )

        exit_action = QAction(
            "Finalizar",
            self
        )

        exit_action.triggered.connect(
            self.close_app
        )

        menu.addAction(toggle_action)

        menu.addSeparator()

        menu.addAction(exit_action)

        self.tray.setContextMenu(menu)

        self.tray.show()

        print("[TRAY] iniciado")

    # =========================================================
    # UPDATE OVERLAY
    # =========================================================

    def update_overlay(self):

        try:

            hw = get_hardware_data()

            fps = fps_data.get(
                "fps",
                0
            )

            frametime = fps_data.get(
                "frametime",
                0
            )

            process = fps_data.get(
                "process",
                "Unknown"
            )

            # =================================================
            # GRAPH LIMIT
            # =================================================

            fps = max(0, min(fps, 500))

            self.graph.add_value(fps)

            # =================================================
            # STATUS ICONS
            # =================================================

            cpu_temp_icon = get_status_icon(
                hw.get("cpu_temp", 0),
                75,
                90
            )

            gpu_temp_icon = get_status_icon(
                hw.get("gpu_temp", 0),
                75,
                90
            )

            gpu_hotspot_icon = get_status_icon(
                hw.get("gpu_hotspot", 0),
                90,
                105
            )

            cpu_usage_icon = get_status_icon(
                hw.get("cpu_usage", 0),
                80,
                95
            )

            gpu_usage_icon = get_status_icon(
                hw.get("gpu_usage", 0),
                90,
                98
            )

            ram_usage_icon = get_status_icon(
                hw.get("ram_usage", 0),
                75,
                90
            )

            cpu_power_icon = get_status_icon(
                hw.get("cpu_power", 0),
                100,
                180
            )

            gpu_power_icon = get_status_icon(
                hw.get("gpu_power", 0),
                200,
                320
            )

            frametime_icon = get_status_icon(
                frametime,
                20,
                40
            )

            ping_icon = get_status_icon(
                network_data["ping"],
                80,
                150
            )

            # =================================================
            # RAM CLOCK STATUS
            # =================================================

            ram_clock = get_ram_clock()

            ideal_ram_clock = 3600

            if ram_clock < ideal_ram_clock:

                ram_clock_icon = (
                    f"[BAIXO/IDEAL: "
                    f"{ideal_ram_clock}MHz]"
                )

            elif ram_clock <= 3600:

                ram_clock_icon = "[IDEAL]"

            else:

                ram_clock_icon = "[OVERCLOCK]"

            # =================================================
            # COMPACT
            # =================================================

            compact_text = f"""
🎮 FPS        : {fps:.0f}
🕒 Frametime  : {frametime:.1f}ms {frametime_icon}

🌐 PING : {network_data["ping"]:>3} ms {ping_icon}
⬇ DOWN : {network_data["download_mbps"]:>6.2f} Mbps
⬆ UP   : {network_data["upload_mbps"]:>6.2f} Mbps

🌡 CPU Temp   : {hw.get("cpu_temp", 0):.0f}°C {cpu_temp_icon}
⚙ CPU Usage  : {hw.get("cpu_usage", 0):.0f}% {cpu_usage_icon}

🎮 GPU Temp   : {hw.get("gpu_temp", 0):.0f}°C {gpu_temp_icon}
📈 GPU Usage  : {hw.get("gpu_usage", 0):.0f}% {gpu_usage_icon}

🧠 RAM Used   : {hw.get("ram_used", 0):.1f}GB
💾 RAM Total  : {hw.get("ram_total", 0):.1f}GB
📊 RAM Usage  : {hw.get("ram_usage", 0):.0f}% {ram_usage_icon}

⚡ RAM CLOCK  : {ram_clock:.0f}MHz {ram_clock_icon}
"""

            self.compact_label.setText(
                compact_text
            )

            # =================================================
            # DETAILED
            # =================================================

            # =================================================
            # DETAILED
            # =================================================

            detailed_text = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🖥 CPU : {hw.get("cpu_name", "Unknown")}

🎮 GPU : {hw.get("gpu_name", "Unknown")}

🧩 MB  : {hw.get("motherboard_name", "Unknown")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 PING      : {network_data["ping"]:>3} ms   {ping_icon}
⬇ DOWN      : {network_data["download_mbps"]:>6.2f} Mbps
⬆ UP        : {network_data["upload_mbps"]:>6.2f} Mbps

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎮 FPS       : {fps:.0f}
🕒 FRAME     : {frametime:.1f}ms {frametime_icon}
🧠 PROCESS   : {process}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌡 CPU TEMP  : {hw.get("cpu_temp", 0):>3.0f}°C   {cpu_temp_icon}
⚙ CPU USE   : {hw.get("cpu_usage", 0):>3.0f}%    {cpu_usage_icon}
🚀 CPU CLK   : {hw.get("cpu_clock", 0):>4.0f}MHz
⚡ CPU PWR   : {hw.get("cpu_power", 0):>3.0f}W    {cpu_power_icon}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌡 GPU TEMP  : {hw.get("gpu_temp", 0):>3.0f}°C   {gpu_temp_icon}
🔥 HOTSPOT   : {hw.get("gpu_hotspot", 0):>3.0f}°C   {gpu_hotspot_icon}
📈 GPU USE   : {hw.get("gpu_usage", 0):>3.0f}%    {gpu_usage_icon}
🚀 GPU CLK   : {hw.get("gpu_core_clock", 0):>4.0f}MHz
⚡ GPU PWR   : {hw.get("gpu_power", 0):>3.0f}W    {gpu_power_icon}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎮 VRAM USED : {hw.get("gpu_vram_used", 0):.1f}GB
💾 VRAM TOT  : {hw.get("gpu_vram_total", 0):.1f}GB

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 RAM USED  : {hw.get("ram_used", 0):.1f}GB
💾 RAM TOT   : {hw.get("ram_total", 0):.1f}GB
📊 RAM USE   : {hw.get("ram_usage", 0):>3.0f}%    {ram_usage_icon}
⚡ RAM CLK   : {ram_clock:.0f}MHz {ram_clock_icon}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
F10 = SHOW/HIDE
"""

            self.info_label.setText(
                detailed_text
            )

        except Exception as e:

            error_text = f"""OVERLAY ERROR

{str(e)}"""

            self.compact_label.setText(
                error_text
            )

            self.info_label.setText(
                error_text
            )

    # =========================================================
    # TOGGLE
    # =========================================================

    def toggle_overlay(self):

        if self.overlay_visible:

            self.hide()

            self.overlay_visible = False

        else:

            self.show()

            self.raise_()

            self.activateWindow()

            QTimer.singleShot(
                0,
                lambda: self.apply_tab_state(
                    self.current_tab
                )
            )

            self.overlay_visible = True

    # =========================================================
    # CLOSE APP
    # =========================================================

    def close_app(self):

        self.timer.stop()

        if hasattr(self, "tray"):

            self.tray.hide()

        QApplication.quit()