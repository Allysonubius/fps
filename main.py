import sys
import os
import multiprocessing

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

# Seus módulos
from overlay.overlay import FPSOverlay
from hotkeys.hotkeys import register_hotkeys
from core.sensors import initialize_hardware
from core.fps import start_presentmon
from core.network import start_network_monitor

# =========================
# RESOURCE PATH
# =========================

def resource_path(relative_path):
    # Tenta pegar o atributo, se não existir, usa o diretório atual
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

# =========================
# MAIN
# =========================

def main():
    # Freeze support é essencial para multiprocessing no Windows
    multiprocessing.freeze_support()
    
    app = QApplication(sys.argv)

    # ICON
    icon_path = resource_path("assets/icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # HARDWARE
    lhm_dll = resource_path("bin/LibreHardwareMonitor/LibreHardwareMonitorLib.dll")
    if os.path.exists(lhm_dll):
        initialize_hardware(lhm_dll)
    else:
        print("[LHM ERROR] DLL de hardware não encontrada")

    # =========================
    # FPS TRACKER (Apenas EXE)
    # =========================
    
    # Inicia o monitoramento (chama sua função no core.fps que usa o PresentMon.exe)
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

if __name__ == "__main__":
    main()