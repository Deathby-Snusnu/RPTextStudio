@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "STUDIO_EXE="
if exist "%~dp0dist\RPTextStudio.exe" set "STUDIO_EXE=%~dp0dist\RPTextStudio.exe"
if exist "%~dp0RPTextStudio.exe" set "STUDIO_EXE=%~dp0RPTextStudio.exe"
if defined STUDIO_EXE goto :start_exe

echo =============================================
echo   RP Text Studio 0.1.9 - Start
 echo =============================================

set "VENV_DIR=%~dp0.venv"
if exist "%~dp0..\..\addons\" set "VENV_DIR=%~dp0..\..\.venv"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"

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

if not exist "requirements.txt" (
    echo FEHLER: requirements.txt wurde nicht gefunden.
    goto :failed
)

echo [2/3] Abhaengigkeiten pruefen / bei Bedarf installieren ...
"%VENV_PYTHON%" -c "import PySide6" >nul 2>&1
if not errorlevel 1 goto :dependencies_ready
"%VENV_PYTHON%" -m pip install -r "requirements.txt"
if errorlevel 1 (
    echo FEHLER: Die Python-Abhaengigkeiten konnten nicht installiert werden.
    goto :failed
)

:dependencies_ready
echo [3/3] RP Text Studio starten ...
"%VENV_PYTHON%" "main.py" %*
if errorlevel 1 (
    echo FEHLER: RP Text Studio wurde mit einem Fehler beendet.
    goto :failed
)
endlocal
exit /b 0

:start_exe
echo RP Text Studio als EXE starten ...
"%STUDIO_EXE%" %*
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
