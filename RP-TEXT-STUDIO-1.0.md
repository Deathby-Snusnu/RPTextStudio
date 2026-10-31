# RP Text Studio 1.0: universeller AddOn-Katalog

> **Planungs- und Implementierungsnotiz:** Dieses Dokument hält Entwürfe und
> einzelne Entwicklungsschritte fest. Es ist kein aktuelles Bedienhandbuch;
> maßgeblich für den Funktionsstand sind die [README](README.md), das
> [Bedienungshandbuch](../../docs/RPTextStudio/HANDBUCH.md) und die
> verlinkten Feature-Dokumente. Aussagen zu damals geplanten oder noch nicht
> enthaltenen Funktionen beziehen sich auf den jeweiligen Entwicklungsstand.

Der aktuelle Quellstand bindet den lokalen Katalog bereits an die
Anwenderverwaltung an, unterstützt öffentliche GitHub-Abfragen ohne CLI
und bietet bestätigte Installations- und Updatevorschauen. Die folgenden
Phasen und PR-Abschnitte sind historische Planungsstände, keine aktuelle
Liste noch fehlender Funktionen.

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

## PR #30: Öffentliche GitHub-Releases ohne CLI und Konto

`github_updates._api` und `github_staging._download` verwenden für
öffentliche Repositories jetzt direkt HTTPS mit einem User-Agent.
Ein GitHub-Token ist optional und wird nur genutzt, wenn er bewusst über
`GH_TOKEN` oder `GITHUB_TOKEN` gesetzt wurde. Normale Nutzer müssen
weder GitHub CLI noch `gh auth login` installieren oder ausführen.

Die Anwenderoberfläche wählt für die Download-Vorschau eigenständig einen
temporären Staging-Ordner. Eine ausdrückliche Freigabe vor dem Download und
die bestehende geschützte Installationsvorschau bleiben erhalten.
Entwicklungskanäle sind weiterhin ein Expertenpfad.

**Noch offen:** Einen vollständigen Ein-Klick-Installationsassistenten mit
automatischer Versionsauswahl, Kompatibilitätsfreigabe, Aufräumlogik und
Downloadfortschritt benötigt einen weiteren PR. Der vorliegende Schritt
entfernt die Account-/CLI-Hürde, ohne die bestehenden Sicherheitsprüfungen
zu umgehen. GitHub kann für anonyme Abrufe eigene Rate-Limits anwenden.

### Test unter Windows
- `python -m pytest tests/test_public_github_access.py tests/test_github_updates.py tests/test_github_staging.py -q`
- Mit **öffentlichem** GitHub-Repository, ohne `GH_TOKEN`, `GITHUB_TOKEN`
  und ohne GitHub CLI, die Versionsprüfung im Programm starten.
- Ein AddOn zur Vorbereitung auswählen; es darf keine Ordnerauswahl
  und keine GitHub-Anmeldung verlangen. WoW muss bis zur separat
  bestätigten Installation unverändert bleiben.
- Zurücksetzen/Abbrechen in der geschützten Installationsvorschau prüfen.
