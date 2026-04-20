@echo off
setlocal
cd /d "%~dp0"

echo ==============================================
echo  BUILD EXE WINDOWS - FATTURE XML
echo ==============================================

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist FattureXML.spec del /q FattureXML.spec

if not exist venv (
    py -m venv venv
    if errorlevel 1 goto :error
)

call venv\Scripts\activate.bat
if errorlevel 1 goto :error

py -m pip install --upgrade pip
if errorlevel 1 goto :error

if exist requirements.txt (
    py -m pip install -r requirements.txt
    if errorlevel 1 goto :error
)

py -m pip install pyinstaller
if errorlevel 1 goto :error

pyinstaller --noconfirm --clean --onefile --name FattureXML main.py
if errorlevel 1 goto :error

if not exist dist\FattureXML.exe goto :error

if not exist dist\da_analizzare mkdir dist\da_analizzare
if not exist dist\analizzati mkdir dist\analizzati
if not exist dist\errori mkdir dist\errori

echo.
echo BUILD COMPLETATA.
echo EXE: dist\FattureXML.exe
echo.
echo Cartelle create in dist:
echo - da_analizzare
echo - analizzati
echo - errori
echo.
pause
exit /b 0

:error
echo.
echo ERRORE DURANTE LA BUILD.
pause
exit /b 1
