# =========================
# core/stats.py
# =========================

fps_history = []

def add_fps(value):

    fps_history.append(value)

    if len(fps_history) > 300:
        fps_history.pop(0)


def get_average_fps():

    if not fps_history:
        return 0

    return sum(fps_history) / len(fps_history)