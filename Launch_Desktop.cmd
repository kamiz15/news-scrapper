@echo off
title Ansu Invest Desktop App
cd /d "%~dp0"
echo Starting Ansu Invest Desktop App...
start "" /B pythonw "%~dp0launcher.pyw"
exit
