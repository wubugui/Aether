@echo off
cd /d "%~dp0"
start "Godot Editor" ".tools\godot\Godot_v4.5.1-stable_win64.exe" --editor --path "%~dp0."
