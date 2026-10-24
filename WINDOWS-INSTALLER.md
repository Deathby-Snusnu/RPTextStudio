# Windows-Installer für RP Text Studio

Ein eigenständiges Windows-Setup kann auf einem Windows-Rechner mit Python 3.11–3.13 und Inno Setup 6 erzeugt werden.

## Voraussetzungen

- Python und `py` oder `python` im PATH
- Inno Setup 6 mit `ISCC.exe` im PATH oder unter dem Standardpfad in Program Files
- Zugriff auf PyPI für den erstmaligen PyInstaller/PySide6-Build

## Erstellung

Im RPTextStudio-Verzeichnis `build_installer.bat` ausführen. Das Skript ruft erst `build_exe.bat` auf und beendet sich bei einem Fehler. Danach baut Inno Setup das Installationspaket unter `installer-dist/RPTextStudio-Setup-0.2.0.exe`. Die Version 0.2.0 ist ein geplanter Zielwert; vor dem Release muss sie mit der tatsächlich freigegebenen Anwendungsversion abgeglichen werden.

## Verhalten

- Pro-Benutzer-Installation nach `%LOCALAPPDATA%\Programs\RPTextStudio`, ohne Administratorrechte
- Startmenüeintrag und optionale Desktopverknüpfung
- Deinstallation über Windows „Installierte Apps“
- Bestehende Einstellungen und gemerkte WoW-Pfade unter `%LOCALAPPDATA%\RPTextStudio` bleiben erhalten
- WoW-Clients, AddOns, Projektordner und Backups bleiben grundsätzlich außerhalb des Setups und werden nicht verändert
- Erneute Installation mit derselben `AppId` ist als Upgrade desselben Programms vorgesehen

## Manuelle Abnahme unter Windows

1. `build_installer.bat` ausführen und prüfen, ob EXE und Setup vorhanden sind.
2. Paket auf separatem Windows-Testbenutzer installieren.
3. Startmenüeintrag sowie optionale Desktopverknüpfung prüfen.
4. Anwendung öffnen und eine AddOn-Projektwurzel lesen.
5. WoW-Installationspfad speichern, Anwendung schließen und Setup erneut installieren.
6. Prüfen, ob die Einstellung nach dem Upgrade erhalten geblieben ist.
7. Über Windows „Installierte Apps“ deinstallieren.
8. Prüfen, ob EXE/Startmenüeintrag weg sind, die RPTextStudio-Einstellungen und alle WoW-Dateien aber erhalten blieben.

## Einschränkungen

Das Setup wurde in diesem GitHub-Branch erstellt, aber der EXE- und Installer-Build wurde hier **nicht unter Windows ausgeführt**. Die Paketierung und alle Upgrade- und Uninstall-Szenarien müssen daher vor einem Release auf Windows getestet werden. Der Installer bringt keine automatische Aktualisierung aus GitHub mit. Eine Code-Signatur ist nicht enthalten; Windows SmartScreen kann bei nicht signierten Downloads warnen.
