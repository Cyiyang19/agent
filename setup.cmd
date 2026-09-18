@echo off
setlocal
set "PATHEXT=.COM;.EXE;.BAT;.CMD;%PATHEXT%"
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"
if errorlevel 1 echo SETUP FAILED - read the error above.
pause
