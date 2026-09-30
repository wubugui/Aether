@echo off
setlocal
set "APPDATA=%~dp0evidence\userdata"
"%~dp0..\..\.tools\godot\Godot_v4.5.1-stable_win64_console.exe" --path "%~dp0project" --log-file "%~dp0evidence\manual-play.log" "res://scenes/candidate41b/Game41b.tscn"
endlocal
