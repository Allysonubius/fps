import keyboard

from hotkeys.bindings import HOTKEYS


def register_hotkeys(overlay):

    keyboard.add_hotkey(
        HOTKEYS["toggle_overlay"],
        lambda: overlay.toggle_signal.emit()
    )