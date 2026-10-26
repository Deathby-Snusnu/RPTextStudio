@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo =============================================
echo   RP Text Studio - Windows-EXE erstellen
echo =============================================

set "VENV_DIR=%~dp0.venv"
if exist "%~dp0..\..\addons\" set "VENV_DIR=%~dp0..\..\.venv"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"
set "MANUAL=%~dp0..\..\docs\RPTextStudio\HANDBUCH.md"
if exist "%~dp0HANDBUCH.md" set "MANUAL=%~dp0HANDBUCH.md"

if not exist "%VENV_PYTHON%" (
    echo [1/4] Virtuelle Python-Umgebung erstellen ...
    where py >nul 2>&1
    if not errorlevel 1 (
        py -3 -m venv "%VENV_DIR%"
    ) else (
        where python >nul 2>&1
        if errorlevel 1 (
            echo FEHLER: Zum Erstellen der EXE wird Python benoetigt.
            echo Bitte Python 3.11 bis 3.13 installieren und erneut starten.
            goto :failed
        )
        python -m venv "%VENV_DIR%"
    )
    if errorlevel 1 (
        echo FEHLER: Die virtuelle Umgebung konnte nicht erstellt werden.
        goto :failed
    )
)

if not exist "%~dp0requirements-build.txt" (
    echo FEHLER: requirements-build.txt wurde nicht gefunden.
    goto :failed
)
if not exist "%~dp0main.py" (
    echo FEHLER: main.py wurde nicht gefunden.
    goto :failed
)
if not exist "%MANUAL%" (
    echo FEHLER: HANDBUCH.md wurde nicht gefunden.
    goto :failed
)
if not exist "%~dp0assets\rp_text_studio_icon.svg" (
    echo FEHLER: Das App-Icon wurde nicht gefunden.
    goto :failed
)

echo [2/4] Laufzeit- und Build-Abhaengigkeiten installieren ...
"%VENV_PYTHON%" -m pip install -r "%~dp0requirements-build.txt"
if errorlevel 1 (
    echo FEHLER: Die Build-Abhaengigkeiten konnten nicht installiert werden.
    goto :failed
)

echo [3/4] Windows-Icon aus dem Vektorlogo erstellen ...
"%VENV_PYTHON%" "%~dp0build_icon.py"
if errorlevel 1 (
    echo FEHLER: Das Windows-Icon konnte nicht erstellt werden.
    goto :failed
)

echo [4/4] Einzelne EXE mit Python, Qt und Handbuch erstellen ...
"%VENV_PYTHON%" -m PyInstaller --noconfirm --clean --onefile --windowed ^
    --name RPTextStudio ^
    --icon "%~dp0build\RPTextStudio.ico" ^
    --distpath "%~dp0dist" ^
    --workpath "%~dp0build\pyinstaller" ^
    --specpath "%~dp0build" ^
    --add-data "%MANUAL%;." ^
    --add-data "%~dp0addon_catalog.json;." ^
    --add-data "%~dp0assets\rp_text_studio_icon.svg;assets" ^
    "%~dp0main.py"
if errorlevel 1 (
    echo FEHLER: Die EXE konnte nicht erstellt werden.
    goto :failed
)
if not exist "%~dp0dist\RPTextStudio.exe" (
    echo FEHLER: Die erwartete EXE wurde nicht gefunden.
    goto :failed
)

echo.
echo Fertig: "%~dp0dist\RPTextStudio.exe"
echo Diese EXE laeuft ohne Python-Installation und ohne Python-Quellordner.
echo AddOn-Dateien separat ueber "Projektordner oeffnen" laden.
endlocal
exit /b 0

:failed
echo.
echo Der Build wurde abgebrochen. Fehlermeldungen siehe oben.
pause
endlocal
exit /b 1
