import clr
import os

computer = None


# =========================================================
# SAFE FLOAT
# =========================================================

def safe_float(value):

    try:
        if value is None:
            return 0.0

        return float(value)

    except:
        return 0.0


# =========================================================
# INIT HARDWARE
# =========================================================

def initialize_hardware(dll_path):

    global computer

    if not os.path.exists(dll_path):

        raise FileNotFoundError(
            f"DLL não encontrada: {dll_path}"
        )

    clr.AddReference(dll_path)

    from LibreHardwareMonitor import Hardware

    computer = Hardware.Computer()

    # =====================================================
    # ENABLE HARDWARE
    # =====================================================

    computer.IsCpuEnabled = True
    computer.IsGpuEnabled = True
    computer.IsMemoryEnabled = True
    computer.IsMotherboardEnabled = True
    computer.IsControllerEnabled = True
    computer.IsStorageEnabled = True
    computer.IsNetworkEnabled = True

    computer.Open()


# =========================================================
# PROCESS HARDWARE
# =========================================================

def process_hardware(hardware, data):

    try:

        hardware.Update()

    except:
        return

    # =====================================================
    # UPDATE SUBHARDWARE
    # =====================================================

    try:

        for subhardware in hardware.SubHardware:
            subhardware.Update()

    except:
        pass

    hw_name = str(hardware.Name).lower()
    hw_type = str(hardware.HardwareType).lower()

    # =====================================================
    # HARDWARE NAMES
    # =====================================================

    if "cpu" in hw_type:
        data["cpu_name"] = hardware.Name

    if "gpu" in hw_type:
        data["gpu_name"] = hardware.Name

    if "motherboard" in hw_type:
        data["motherboard_name"] = hardware.Name

    # =====================================================
    # SENSORS
    # =====================================================

    for sensor in hardware.Sensors:

        try:

            if sensor.Value is None:
                continue

            name = str(sensor.Name).lower()
            sensor_type = str(sensor.SensorType).lower()

            value = safe_float(sensor.Value)

            # ignora lixo
            if value <= 0:
                continue

            # =================================================
            # DEBUG CPU TEMP
            # =================================================

            if (
                "cpu" in hw_type and
                "temperature" in sensor_type
            ):

                print(
                    "[CPU TEMP SENSOR]",
                    sensor.Name,
                    "=",
                    value
                )

            # =================================================
            # CPU
            # =================================================

            if "cpu" in hw_type:

                # =============================================
                # CPU TEMP
                # =============================================

                if "temperature" in sensor_type:

                    # Ryzen geralmente usa isso
                    if (
                        "tctl" in name or
                        "tdie" in name or
                        "package" in name or
                        "ccd" in name or
                        "core" in name
                    ):

                        data["cpu_temp"] = max(
                            data["cpu_temp"],
                            value
                        )

                # =============================================
                # CPU USAGE
                # =============================================

                if "load" in sensor_type:

                    if (
                        "cpu total" in name or
                        name == "total"
                    ):

                        data["cpu_usage"] = value

                # =============================================
                # CPU CLOCK
                # =============================================

                if "clock" in sensor_type:

                    # pega maior clock dos cores
                    if (
                        "core #" in name and
                        "effective" not in name
                    ):

                        data["cpu_clock"] = max(
                            data["cpu_clock"],
                            value
                        )

                    # fallback
                    elif (
                        "cores (average)" in name and
                        "effective" not in name
                    ):

                        data["cpu_clock"] = max(
                            data["cpu_clock"],
                            value
                        )

                # =============================================
                # CPU POWER
                # =============================================

                if "power" in sensor_type:

                    if (
                        "package" in name or
                        "cpu package" in name
                    ):

                        data["cpu_power"] = max(
                            data["cpu_power"],
                            value
                        )

            # =================================================
            # GPU
            # =================================================

            if "gpu" in hw_type:

                # =============================================
                # GPU TEMP
                # =============================================

                if "temperature" in sensor_type:

                    if (
                        name == "gpu core" or
                        "gpu core" in name
                    ):

                        data["gpu_temp"] = value

                    elif (
                        "hot spot" in name or
                        "hotspot" in name
                    ):

                        data["gpu_hotspot"] = value

                # =============================================
                # GPU USAGE
                # =============================================

                if "load" in sensor_type:

                    if (
                        name == "gpu core" or
                        "gpu core" in name
                    ):

                        data["gpu_usage"] = value

                # =============================================
                # GPU CLOCK
                # =============================================

                if "clock" in sensor_type:

                    if (
                        name == "gpu core" or
                        "gpu core" in name
                    ):

                        data["gpu_core_clock"] = value

                # =============================================
                # GPU POWER
                # =============================================

                if "power" in sensor_type:

                    if (
                        "gpu package" in name or
                        "package" in name
                    ):

                        data["gpu_power"] = value

                # =============================================
                # VRAM USED
                # =============================================

                if (
                    "gpu memory used" in name or
                    "d3d dedicated memory used" in name
                ):

                    data["gpu_vram_used"] = (
                        value / 1024
                    )

                # =============================================
                # VRAM TOTAL
                # =============================================

                if (
                    "gpu memory total" in name or
                    "d3d dedicated memory total" in name
                ):

                    data["gpu_vram_total"] = (
                        value / 1024
                    )

            # =================================================
            # RAM
            # =================================================

            if (
                "memory" in hw_type or
                "genericmemory" in hw_type or
                "controller" in hw_type
            ):

                # =============================================
                # RAM USED
                # =============================================

                if "memory used" in name:

                    data["ram_used"] = value

                # =============================================
                # RAM AVAILABLE
                # =============================================

                if "memory available" in name:

                    total = (
                        data["ram_used"] + value
                    )

                    data["ram_total"] = total

                # =============================================
                # RAM USAGE
                # =============================================

                if (
                    "load" in sensor_type and
                    name == "memory"
                ):

                    data["ram_usage"] = value

                # =============================================
                # RAM CLOCK
                # =============================================

                if "clock" in sensor_type:

                    if (
                        "memory" in name or
                        "dram" in name or
                        "ram" in name
                    ):

                        # DDR = dobra
                        data["ram_clock"] = max(
                            data["ram_clock"],
                            value * 2
                        )

        except Exception as e:

            print(
                "[SENSOR READ ERROR]",
                e
            )

    # =====================================================
    # RECURSIVE SUB HARDWARE
    # =====================================================

    try:

        for subhardware in hardware.SubHardware:

            process_hardware(
                subhardware,
                data
            )

    except:
        pass


# =========================================================
# GET HARDWARE DATA
# =========================================================

def get_hardware_data():

    data = {

        "cpu_name": "Unknown",
        "gpu_name": "Unknown",
        "motherboard_name": "Unknown",

        "cpu_temp": 0.0,
        "cpu_clock": 0.0,
        "cpu_usage": 0.0,
        "cpu_power": 0.0,

        "gpu_temp": 0.0,
        "gpu_hotspot": 0.0,
        "gpu_usage": 0.0,
        "gpu_core_clock": 0.0,
        "gpu_power": 0.0,

        "gpu_vram_used": 0.0,
        "gpu_vram_total": 0.0,

        "ram_used": 0.0,
        "ram_total": 0.0,
        "ram_usage": 0.0,
        "ram_clock": 0.0,
    }

    global computer

    if computer is None:
        return data

    try:

        for hardware in computer.Hardware:

            process_hardware(
                hardware,
                data
            )

        return data

    except Exception as e:

        print("[SENSOR ERROR]", e)

        return data