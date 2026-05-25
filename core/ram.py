import subprocess

ram_clock_cache = 0.0


# =========================================================
# GET RAM CLOCK
# =========================================================

def get_ram_clock():

    global ram_clock_cache

    # =============================================
    # CACHE
    # =============================================

    if ram_clock_cache > 0:

        return ram_clock_cache

    # =============================================
    # POWERSHELL
    # =============================================

    try:

        output = subprocess.check_output(

            [
                "powershell",
                "-Command",
                "(Get-CimInstance Win32_PhysicalMemory | Select-Object -First 1 -ExpandProperty Speed)"
            ],

            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        speed = output.strip()

        if speed:

            ram_clock_cache = float(speed)

            print(
                "[RAM CLOCK]",
                ram_clock_cache,
                "MHz"
            )

            return ram_clock_cache

    except Exception as e:

        print(
            "[RAM CLOCK ERROR]",
            e
        )

    return 0.0