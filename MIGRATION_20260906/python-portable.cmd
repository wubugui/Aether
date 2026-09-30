@echo off
setlocal
set "PYTHONNOUSERSITE=1"
set "PYTHONPATH=%~dp0external\python\user_site;%~dp0external\python\Python310\Lib\site-packages"
"%~dp0external\python\Python310\python.exe" %*
exit /b %errorlevel%

