@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install-Steam-Water-Sword.ps1" -Action Restore
if errorlevel 1 pause
endlocal
