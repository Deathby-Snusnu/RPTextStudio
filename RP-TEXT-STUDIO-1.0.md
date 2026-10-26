# RP Text Studio 1.0: universeller AddOn-Katalog

## Leitprinzip
**Maximale Flexibilität für Entwickler, minimaler Aufwand für Anwender.**
PaladinRP, JaegerRP, DruidenRP, HexerRP und alle zukünftigen RP-AddOns
verwenden denselben Installations- und Update-Mechanismus. Klassen wie Magier,
Krieger, Priester, Schamane und Schurke sind Metadaten und benötigen keine
Sonderlogik im Installer.

## Erste Implementierung
`addon_catalog.py` liest und validiert `addon_catalog.json`.
Der Katalog enthält Anzeigename, eindeutige ID, GitHub-Repository,
Klassen und unterstützte Clientprofile. Ein leeres `supported_clients`
bedeutet **nicht bestätigt**, nicht *alle Clients kompatibel*.
Neue AddOns lassen sich als Metadaten ergänzen. Noch erfolgt keine
automatische Aktualisierung des Katalogs und keine GUI-Anbindung.

## Vertrauensmodell
Ein Katalog ist nie selbst ein Freibrief zur Installation. Versionierte
Artefakte, überprüfte Quellen, WoW-Kompatibilität, Abhängigkeiten und
Installationsberechtigungen müssen gesondert validiert werden.
Aktuell sind Einträge bewusst auf `Deathby-Snusnu/<AddOn-ID>` beschränkt.
Fremde Publisher erfordern zukünftig eine ausdrückliche Vertrauensfreigabe.
Keine Ausführung von Metadaten als Code.

## Entwicklungsphasen
1. Validierter Katalog als Grundlage (dieser PR).
2. Dynamische GUI-Listen und durchgängige Umstellung vorhandener fest
   codierter Sechser-Listen; Portabilität in PyInstaller prüfen.
3. Download öffentlicher, verifizierter stabiler Releases ohne GitHub CLI
   oder Benutzeranmeldung; Entwicklungsstände nur im Expertenmodus.
4. Automatisch erkannte WoW-Installationen mit expliziter Clientfreigabe.
5. Sichere und komfortable Updates inkl. unveränderter Standarddateien,
   separater eigener Textsammlungen, Konfliktvorschau und Rollback.
6. Windows-Setup, Selbstupdate und reproduzierbare End-to-End-Tests.

## Nutzerakzeptanz
Ein erstmaliger Windows-Anwender kann das Setup herunterladen, seine WoW-
Installation auswählen und ein kompatibles RP-AddOn installieren, ohne Git,
Python, Staging, TOC-Dateien oder Branches kennen zu müssen.

## PR #29: Katalogintegration in den bisherigen Anwender-Modus

Die AddOn-Übersicht zeigt jetzt lesbare Namen aus dem lokalen Katalog.
Installations-, Versionsprüfungs- und GitHub-Staging-Aktionen verwenden intern
weiterhin die eindeutige AddOn-ID. Die vorhandenen Nutzeraktionen bleiben
unverändert. Der Bestand wird für jede ausgewählte WoW-Installation getrennt
ermittelt. Auch die Funktion für die Erstinstallation fehlender AddOns bezieht
ihre Liste aus dem Katalog, statt sechs Namen im Python-Code zu hinterlegen.

**Wichtig:** Die Katalogdatei ist weiterhin lokal mitgeliefert. Neue Einträge
setzen zurzeit ein aktualisiertes Katalogpaket voraus. Ein abgesicherter
Online-Katalog, GUI-basierte Kompatibilitätsfreigaben, Release-Downloads ohne
GitHub-CLI und eine Ein-Klick-Installation folgen später. Bei beschädigtem
Katalog wird nicht mit ungeprüften Quellen installiert.

### Windows-Live-Test

1. In Testkopie vom Branch `feature/catalog-driven-addon-manager-pr29`
   `python -m unittest discover -s tests -p "test_catalog_driven_manager.py" -v` ausführen.
2. RP Text Studio starten, Anwenderverwaltung öffnen und zwei getrennte
   erkannte WoW-Installationen nacheinander auswählen.
3. Anzeigenamen und Installationsstatus der sechs bestehenden AddOns prüfen.
4. Paladin RP markieren, Versionsprüfung und die bestehende Staging-Vorschau
   durchführen. Der Ordnername muss weiterhin `PaladinRP` lauten.
5. Ein syntaktisch gültiges `MagierRP`-Element in die Katalogdatei einer
   isolierten Testkopie eintragen, Anwendung neu starten: Es soll ohne neue
   Python-Sonderlogik in der Übersicht erscheinen. Vor einer echten
   Installation benötigt es allerdings ein geprüftes Repository-Paket und
   eine ausdrückliche Freigabe der Client-Kompatibilität.

Dieser Schritt ist bewusst eine Erweiterung der bestehenden Anwenderoberfläche,
noch kein vollständiger Endnutzer-Installer.
