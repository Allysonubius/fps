import sys
import os
import multiprocessing

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from overlay.overlay import FPSOverlay
from hotkeys.hotkeys import register_hotkeys
from core.sensors import initialize_hardware

from core.fps import start_presentmon
from core.network import start_network_monitor

# =========================
# RESOURCE PATH
# =========================

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# =========================
# MAIN
# =========================

def main():
    app = QApplication(sys.argv)

    # ICON
    icon_path = resource_path("assets/icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # HARDWARE
    dll_path = resource_path(
        "bin/LibreHardwareMonitor/LibreHardwareMonitorLib.dll"
    )

    if os.path.exists(dll_path):
        initialize_hardware(dll_path)
    else:
        print("[LHM ERROR] DLL não encontrada")

    # =========================
    # FPS TRACKER START
    # =========================
    start_presentmon()
    
    # =========================
    # NETWORK MONITOR
    # =========================

    start_network_monitor()

    # =========================
    # OVERLAY
    # =========================
    overlay = FPSOverlay()
    overlay.show()

    # HOTKEYS
    register_hotkeys(overlay)

    # LOOP
    sys.exit(app.exec())


# ENTRYPOINT
if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()