@echo off

cd /d %~dp0..

echo =========================
echo BUILDING FPS OVERLAY
echo =========================

py -m PyInstaller ^
--clean ^
--noconfirm ^
--onefile ^
--windowed ^
--name FPSOverlay ^
--icon=assets/icon.ico ^
--hidden-import=wmi ^
--hidden-import=pythoncom ^
--hidden-import=win32com ^
--collect-all=pythoncom ^
--collect-all=win32com ^
--add-binary "bin/PresentMon.exe;bin" ^
--add-data "bin/LibreHardwareMonitor;bin/LibreHardwareMonitor" ^
--add-data "assets;assets" ^
main.py

echo.
echo =========================
echo BUILD FINALIZADO
echo =========================

pause