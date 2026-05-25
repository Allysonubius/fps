# =========================
# config/config.py
# =========================

import json

with open("config/settings.json", "r") as f:

    SETTINGS = json.load(f)