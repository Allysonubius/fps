# =========================
# core/fps.py
# PRESENTMON REALTIME STDOUT
# =========================

import subprocess
import threading
import os
import csv
import sys
import time

# =========================
# GLOBAL FPS DATA
# =========================

fps_data = {
    "fps": 0.0,
    "frametime": 0.0,
    "process": ""
}

_running = False
process = None

# =========================
# PROCESS LOCK
# =========================

current_process = None
current_process_time = 0

# =========================
# BLACKLIST
# =========================

PROCESS_BLACKLIST = [

    "dwm.exe",
    "explorer.exe",
    "presentmon.exe",
    "discord.exe",
    "steamwebhelper.exe",
    "obs64.exe",
    "searchhost.exe",
    "widgets.exe",
    "textinputhost.exe",
    "startmenuexperiencehost.exe"
]

# =========================
# RESOURCE PATH
# =========================

def resource_path(relative_path):

    try:
        base_path = sys._MEIPASS

    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(
        base_path,
        relative_path
    )

# =========================
# PRESENTMON PATH
# =========================

presentmon_path = resource_path(
    os.path.join(
        "bin",
        "PresentMon.exe"
    )
)

# =========================
# START PRESENTMON
# =========================

def start_presentmon():

    global _running
    global process

    if _running:
        return

    _running = True

    # =========================
    # CHECK EXE
    # =========================

    if not os.path.exists(presentmon_path):

        print("[PresentMon ERROR]")
        print("EXE não encontrado:")
        print(presentmon_path)

        return

    # =========================
    # COMMAND
    # =========================

    command = [

        presentmon_path,

        "--stop_existing_session",

        "--output_stdout",

        "--exclude", "dwm.exe",
        "--exclude", "explorer.exe",
        "--exclude", "PresentMon.exe"
    ]

    print("[PresentMon CMD]")
    print(command)

    # =========================
    # START PROCESS
    # =========================

    process = subprocess.Popen(

        command,

        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,

        stdin=subprocess.DEVNULL,

        text=True,
        encoding="utf-8",
        errors="ignore",

        bufsize=1,

        creationflags=(
            subprocess.CREATE_NO_WINDOW
            if os.name == "nt"
            else 0
        )
    )

    print("[PresentMon] iniciado")

    # =========================
    # START THREAD
    # =========================

    threading.Thread(
        target=_reader_loop,
        daemon=True
    ).start()

# =========================
# FIND FRAME COLUMN
# =========================

def get_frametime_index(headers):

    headers_lower = [h.lower() for h in headers]

    for name in [

        "msbetweenpresents",
        "msbetweendisplaychange",
        "msinpresentapi"

    ]:

        if name in headers_lower:
            return headers_lower.index(name)

    return None

# =========================
# READER LOOP
# =========================

def _reader_loop():

    global process
    global current_process
    global current_process_time

    headers = None
    app_index = None
    ft_index = None

    print("[PresentMon] monitorando FPS realtime...")

    while True:

        try:

            # =========================
            # READ LINE
            # =========================

            line = process.stdout.readline()

            if not line:

                time.sleep(0.001)
                continue

            line = line.strip()

            if not line:
                continue

            # =========================
            # IGNORE WARNINGS
            # =========================

            if (
                line.lower().startswith("warning")
                or line.lower().startswith("use ")
                or line.lower().startswith("error:")
            ):
                continue

            # =========================
            # CSV PARSE
            # =========================

            try:
                row = next(csv.reader([line]))
            except:
                continue

            # =========================
            # HEADER
            # =========================

            if headers is None and "Application" in row:

                headers = row

                app_index = headers.index(
                    "Application"
                )

                ft_index = get_frametime_index(
                    headers
                )

                print("[HEADER OK]")
                print(headers)

                print("[APP INDEX]", app_index)
                print("[FT INDEX]", ft_index)

                continue

            if headers is None:
                continue

            if ft_index is None:
                continue

            if len(row) <= max(
                app_index,
                ft_index
            ):
                continue

            # =========================
            # APP
            # =========================

            app = row[app_index].strip()

            if not app:
                continue

            app_lower = app.lower()

            if (
                app_lower in PROCESS_BLACKLIST
                or app_lower == "<unknown>"
            ):
                continue

            # =========================
            # FRAMETIME
            # =========================

            try:
                frametime = float(
                    row[ft_index]
                )

            except:
                continue

            if frametime <= 0:
                continue

            # =========================
            # FPS
            # =========================

            fps = 1000.0 / frametime

            if fps <= 0 or fps > 1000:
                continue

            # =========================
            # PROCESS LOCK LOGIC
            # =========================

            now = time.time()

            # =========================
            # FIRST PROCESS
            # =========================

            if current_process is None:

                current_process = app
                current_process_time = now

                print(f"[LOCK] {app}")

            # =========================
            # SAME PROCESS
            # =========================

            if app == current_process:

                current_process_time = now

            # =========================
            # PROCESS SWITCH
            # =========================

            else:

                # somente troca se
                # o novo processo for relevante

                if fps > 30:

                    elapsed = (
                        now -
                        current_process_time
                    )

                    # estabilidade antes de trocar

                    if elapsed > 2.0:

                        print(
                            f"[SWITCH] "
                            f"{current_process} -> {app}"
                        )

                        current_process = app
                        current_process_time = now

            # =========================
            # UPDATE ONLY LOCKED APP
            # =========================

            if app == current_process:

                fps_data["fps"] = round(
                    fps,
                    1
                )

                fps_data["frametime"] = round(
                    frametime,
                    2
                )

                fps_data["process"] = app

        except Exception as e:

            print("[PresentMon ERROR]")
            print(e)

            time.sleep(0.1)