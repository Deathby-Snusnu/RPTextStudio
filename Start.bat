@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo =============================================
echo   RP Text Studio 0.1.8 - Start
 echo =============================================

set "VENV_DIR=%~dp0.venv"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"
set "VENV_ACTIVATE=%VENV_DIR%\Scripts\activate.bat"

if not exist "%VENV_PYTHON%" (
    echo [1/3] Virtuelle Python-Umgebung erstellen ...
    where py >nul 2>&1
    if not errorlevel 1 (
        py -3 -m venv "%VENV_DIR%"
    ) else (
        where python >nul 2>&1
        if errorlevel 1 (
            echo FEHLER: Python wurde nicht gefunden.
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

if not exist "%VENV_ACTIVATE%" (
    echo FEHLER: Die virtuelle Umgebung ist unvollstaendig.
    echo Bitte den Ordner .venv entfernen und erneut starten.
    goto :failed
)

echo [2/3] Virtuelle Umgebung aktivieren ...
call "%VENV_ACTIVATE%"
if errorlevel 1 (
    echo FEHLER: Aktivieren der virtuellen Umgebung fehlgeschlagen.
    goto :failed
)

if not exist "requirements.txt" (
    echo FEHLER: requirements.txt wurde nicht gefunden.
    goto :failed
)

echo [2/3] Abhaengigkeiten pruefen / bei Bedarf installieren ...
"%VENV_PYTHON%" -m pip install -r "requirements.txt"
if errorlevel 1 (
    echo FEHLER: Die Python-Abhaengigkeiten konnten nicht installiert werden.
    goto :failed
)

echo [3/3] RP Text Studio starten ...
"%VENV_PYTHON%" "main.py"
if errorlevel 1 (
    echo FEHLER: RP Text Studio wurde mit einem Fehler beendet.
    goto :failed
)
endlocal
exit /b 0

:failed
echo.
echo Der Start wurde abgebrochen. Fehlermeldungen siehe oben.
pause
endlocal
exit /b 1
