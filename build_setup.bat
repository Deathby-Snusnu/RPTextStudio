@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo [1/3] Aktuelle EXE erstellen ...
call "%~dp0build_exe.bat"
if errorlevel 1 goto :failed

if not exist "%~dp0dist\RPTextStudio.exe" goto :failed
if not exist "%~dp0build_version.issinc" goto :failed
if not exist "%~dp0build_info.json" goto :failed

echo [2/3] Inno Setup 6 suchen ...
set "ISCC="
where ISCC.exe >nul 2>&1
if not errorlevel 1 set "ISCC=ISCC.exe"
if not defined ISCC if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC (
    echo FEHLER: Inno Setup 6 fehlt.
    goto :failed
)

echo [3/3] Installer aus exakt dieser EXE bauen ...
"%ISCC%" "%~dp0installer.iss"
if errorlevel 1 goto :failed

echo.
echo Setup erfolgreich erstellt. Build-Identitaet:
type "%~dp0build_info.json"
endlocal
exit /b 0

:failed
echo FEHLER: Setup nicht erstellt. Kein vorhandenes Paket als aktuell betrachten.
endlocal
exit /b 1
