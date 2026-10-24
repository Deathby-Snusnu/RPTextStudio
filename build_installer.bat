@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo [1/3] Build RPTextStudio.exe ...
call "%~dp0build_exe.bat"
if errorlevel 1 goto :failed

if not exist "%~dp0dist\RPTextStudio.exe" (
  echo FEHLER: EXE nicht gefunden.
  goto :failed
)

echo [2/3] Inno Setup Compiler finden ...
set "ISCC="
where ISCC.exe >nul 2>&1
if not errorlevel 1 set "ISCC=ISCC.exe"
if not defined ISCC if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC (
  echo FEHLER: Inno Setup 6 fehlt. Installer von https://jrsoftware.org/isinfo.php installieren.
  goto :failed
)

echo [3/3] Windows-Installer erstellen ...
"%ISCC%" "%~dp0installer.iss"
if errorlevel 1 goto :failed

echo.
echo Installationspaket im Verzeichnis installer-dist erstellt.
endlocal
exit /b 0

:failed
echo.
echo FEHLER: Windows-Setup konnte nicht erstellt werden.
endlocal
exit /b 1
