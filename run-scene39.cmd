@echo off
cd /d "%~dp0"
if not exist "captures\acceptance39\userdata" mkdir "captures\acceptance39\userdata"
set "APPDATA=%~dp0captures\acceptance39\userdata"
start "Aether Scene 39 Candidate" "%~dp0.tools\godot\Godot_v4.5.1-stable_win64.exe" --path "%~dp0." --log-file "%~dp0captures\acceptance39\interactive.log" "res://scenes/candidate39/Game39.tscn"
