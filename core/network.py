import psutil
import threading
import time
from ping3 import ping

network_data = {
    "download_mbps": 0.0,
    "upload_mbps": 0.0,
    "ping": 0
}

last_sent = 0
last_recv = 0

running = False


# =========================================================
# NETWORK LOOP
# =========================================================

def network_loop():

    global last_sent
    global last_recv

    while running:

        try:

            counters = psutil.net_io_counters()

            sent = counters.bytes_sent
            recv = counters.bytes_recv

            # =================================================
            # FIRST RUN
            # =================================================

            if last_sent == 0:

                last_sent = sent
                last_recv = recv

                time.sleep(1)

                continue

            # =================================================
            # SPEED
            # =================================================

            upload_speed = sent - last_sent
            download_speed = recv - last_recv

            last_sent = sent
            last_recv = recv

            # bytes -> megabits
            network_data["download_mbps"] = (
                download_speed * 8 / 1024 / 1024
            )

            network_data["upload_mbps"] = (
                upload_speed * 8 / 1024 / 1024
            )

            # =================================================
            # PING
            # =================================================

            result = ping(
                "8.8.8.8",
                timeout=1
            )

            if result is not None:

                network_data["ping"] = int(
                    result * 1000
                )

        except Exception as e:

            print("[NETWORK ERROR]", e)

        time.sleep(1)


# =========================================================
# START
# =========================================================

def start_network_monitor():

    global running

    if running:
        return

    running = True

    thread = threading.Thread(
        target=network_loop,
        daemon=True
    )

    thread.start()