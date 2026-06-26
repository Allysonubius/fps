# =========================
# core/fps.py
# PRESENTMON REALTIME STDOUT (SEM ARQUIVOS TEMPORÁRIOS)
# =========================

import subprocess
import threading
import os
import csv
import sys
import time
import atexit

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
# CONFIGURAÇÕES
# =========================

PROCESS_BLACKLIST = {
    "dwm.exe", "explorer.exe", "presentmon.exe", "discord.exe",
    "steamwebhelper.exe", "obs64.exe", "searchhost.exe", "widgets.exe",
    "textinputhost.exe", "startmenuexperiencehost.exe", "python.exe",
    "fpsoverlay.exe", "main.exe", "code.exe"
}

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

presentmon_path = resource_path(os.path.join("bin", "PresentMon.exe"))

# =========================
# CONTROLE DO PROCESSO
# =========================

def start_presentmon():
    global _running, process

    if _running:
        return

    if not os.path.exists(presentmon_path):
        print(f"[PresentMon ERROR] Executável não encontrado em: {presentmon_path}")
        return

    _running = True

    # Comando configurado com sessão exclusiva para evitar conflito com PresentMon zumbi
    command = [
        presentmon_path,
        "--stop_existing_session",
        "--session_name", "FPSOverlay",
        "--output_stdout"
    ]

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
        errors="ignore",
        bufsize=1,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    )

    print("[PresentMon] Monitoramento via STDOUT iniciado com sessão FPSOverlay.")
    threading.Thread(target=_reader_loop, daemon=True).start()

def stop_presentmon():
    global _running, process, fps_data
    _running = False
    
    if process:
        try:
            process.terminate()
            process.wait(timeout=1)
        except:
            process.kill()
        process = None

    fps_data.update({"fps": 0.0, "frametime": 0.0, "process": ""})
    print("[PresentMon] Processo encerrado.")

atexit.register(stop_presentmon)

# =========================
# LÓGICA DE LEITURA
# =========================

def _reader_loop():
    global process, _running
    
    current_process = None
    last_update_time = 0
    
    headers = None
    app_idx = None
    ft_idx = None

    while _running and process:
        try:
            line = process.stdout.readline()
            if not line:
                if process.poll() is not None: break
                continue

            # Limpa espaços e quebras de linha
            line = line.strip()
            
            # Pula linhas em branco ou de aviso (warnings) antes do CSV começar
            if not line or line.lower().startswith("warning") or line.lower().startswith("use"):
                continue

            row = next(csv.reader([line]))
            
            # Identificar cabeçalhos
            if headers is None and "Application" in row:
                headers = row
                app_idx = headers.index("Application")
                
                # Busca colunas de frametime cobrindo variações de letras maiúsculas/minúsculas
                for col in ["MsBetweenPresents", "msBetweenPresents", "MsInPresentAPI", "msInPresentAPI"]:
                    if col in headers:
                        ft_idx = headers.index(col)
                        break
                continue

            # Pula se o cabeçalho não foi definido ou se a linha tá incompleta
            if app_idx is None or ft_idx is None or len(row) <= max(app_idx, ft_idx):
                continue

            app = row[app_idx].strip()
            if not app or app.lower() in PROCESS_BLACKLIST or app == "<unknown>":
                continue

            # Trata casos em que o PresentMon envia "NA"
            if row[ft_idx] == "NA":
                continue

            try:
                frametime = float(row[ft_idx])
            except ValueError:
                continue

            if frametime <= 0: continue
            fps = 1000.0 / frametime

            # Lógica de Foco: foca no app ativo e atualiza os dados
            now = time.time()
            
            # Reset foco se inativo por mais de 2 segundos
            if current_process and (now - last_update_time) > 2.0:
                current_process = None

            # Atualiza o processo atual (removido o limite bugado de fps > 35)
            if current_process is None or app != current_process:
                current_process = app
            
            # Salva no dicionário global
            if app == current_process:
                fps_data["fps"] = round(fps, 1)
                fps_data["frametime"] = round(frametime, 2)
                fps_data["process"] = app
                last_update_time = now

        except Exception:
            # Sleep curto para não sobrecarregar a CPU caso haja erros contínuos de leitura
            time.sleep(0.01)