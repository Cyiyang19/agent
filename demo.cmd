@echo off
setlocal
set "PATHEXT=.COM;.EXE;.BAT;.CMD;%PATHEXT%"
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
 echo Run setup.cmd first.
 pause
 exit /b 1
)
".venv\Scripts\python.exe" -X utf8 scripts\demo_menu.py
pause
