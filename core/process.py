import subprocess
import os

processes = {}

def start_background_process(name, path):

    global processes

    if name in processes:
        return

    if not os.path.exists(path):
        print(f"[ERROR] File not found: {path}")
        return

    try:

        startupinfo = subprocess.STARTUPINFO()

        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        process = subprocess.Popen(
            [path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            shell=True,
            startupinfo=startupinfo,
            creationflags=(
                subprocess.CREATE_NO_WINDOW
            )
        )

        processes[name] = process

        print(f"[PROCESS STARTED] {name}")

    except Exception as e:

        print(f"[PROCESS ERROR] {e}")