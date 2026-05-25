# =========================
# core/monitor.py
# =========================

from screeninfo import get_monitors

def get_monitor_data():

    monitors = []

    for m in get_monitors():

        monitors.append({
            "width": m.width,
            "height": m.height,
            "x": m.x,
            "y": m.y
        })

    return monitors