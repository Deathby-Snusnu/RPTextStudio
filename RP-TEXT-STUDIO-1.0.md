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
