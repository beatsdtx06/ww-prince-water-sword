@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Manage-Mod.ps1" -Action Install %*
set "result=%ERRORLEVEL%"
echo.
pause
exit /b %result%
