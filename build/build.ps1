# =========================
# build/build.ps1
# =========================

py -m PyInstaller `
--clean `
--onefile `
--windowed `
--icon=assets/icon.ico `
--add-binary "bin/PresentMon.exe;bin" `
--add-data "assets;assets" `
main.py