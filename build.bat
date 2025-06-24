@echo off

if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "nm-kill.exe" del /q "nm-kill.exe"
if exist "installer" rmdir /s /q "installer"
if exist "*.spec" del /q "*.spec"

pip install -r requirements.txt
pyinstaller --onefile --noconsole --icon=static/favicon.ico --add-data "static;static" main.py --name nm-kill --clean

if exist "dist\nm-kill.exe" (
    move "dist\nm-kill.exe" "nm-kill.exe"
) else (
    exit /b 1
)

set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\iscc.exe"
if not exist "%ISCC_PATH%" (
    goto :end
)

"%ISCC_PATH%" setup.iss
:end
