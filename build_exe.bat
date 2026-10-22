@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo =============================================
echo   RP Text Studio - Windows-EXE erstellen
echo =============================================

set "VENV_PYTHON=%~dp0.venv\Scripts\python.exe"

if not exist "%VENV_PYTHON%" (
    echo [1/4] Virtuelle Python-Umgebung erstellen ...
    where py >nul 2>&1
    if not errorlevel 1 (
        py -3 -m venv "%~dp0.venv"
    ) else (
        where python >nul 2>&1
        if errorlevel 1 (
            echo FEHLER: Zum Erstellen der EXE wird Python benoetigt.
            echo Bitte Python 3.11 bis 3.13 installieren und erneut starten.
            goto :failed
        )
        python -m venv "%~dp0.venv"
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
if not exist "%~dp0HANDBUCH.md" (
    echo FEHLER: HANDBUCH.md wurde nicht gefunden.
    goto :failed
)
if not exist "%~dp0assets\rp_text_studio.svg" (
    echo FEHLER: Das Logo assets\rp_text_studio.svg wurde nicht gefunden.
    goto :failed
)
if not exist "%~dp0build_icon.py" (
    echo FEHLER: build_icon.py wurde nicht gefunden.
    goto :failed
)

echo [2/4] Laufzeit- und Build-Abhaengigkeiten installieren ...
"%VENV_PYTHON%" -m pip install -r "%~dp0requirements-build.txt"
if errorlevel 1 (
    echo FEHLER: Die Build-Abhaengigkeiten konnten nicht installiert werden.
    goto :failed
)

echo [3/4] Windows-Icon aus dem Projektlogo erzeugen ...
"%VENV_PYTHON%" "%~dp0build_icon.py" "%~dp0assets\rp_text_studio.svg" "%~dp0build\RPTextStudio.ico"
if errorlevel 1 (
    echo FEHLER: Das Windows-Icon konnte nicht erzeugt werden.
    goto :failed
)

echo [4/4] Einzelne EXE mit Python, Qt, Handbuch und Logo erstellen ...
"%VENV_PYTHON%" -m PyInstaller --noconfirm --clean --onefile --windowed ^
    --name RPTextStudio ^
    --icon "%~dp0build\RPTextStudio.ico" ^
    --distpath "%~dp0dist" ^
    --workpath "%~dp0build\pyinstaller" ^
    --specpath "%~dp0build" ^
    --add-data "%~dp0HANDBUCH.md;." ^
    --add-data "%~dp0assets\rp_text_studio.svg;assets" ^
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
