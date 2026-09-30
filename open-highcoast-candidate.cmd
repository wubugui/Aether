@echo off
cd /d "%~dp0"
start "Aether Highcoast Editor" "%~dp0.tools\godot\Godot_v4.5.1-stable_win64.exe" --editor --path "%~dp0." "res://captures/candidate_highcoast36c/World36c.tscn"
