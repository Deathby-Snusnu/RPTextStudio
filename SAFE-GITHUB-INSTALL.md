# Sicherer GitHub-Download und AddOn-Installation

## Ablauf

1. **AddOns → Anwender: Installierte AddOns prüfen…** öffnen und WoW-Installation auswählen.
2. **Interface-Profil…**: Interface-Nummer aus dem tatsächlich gestarteten Client hinterlegen.
3. AddOn in der Tabelle markieren, GitHub-Kanal wählen und **Paket prüfen und bereitstellen…**.
4. Paket in einem Ordner **außerhalb von WoW** herunterladen und prüfen lassen.
5. **Geprüftes Paket installieren…** klicken. In der Vorschau die Anzahl neuer und geschützter Dateien, die TOC-Anpassung und den Kompatibilitätshinweis kontrollieren.
6. Mit **Ja** ausdrücklich bestätigen. Der alte AddOn-Ordner wird vor dem Austausch unter `Interface/AddOns/.addon-backups/<Zeitstempel>/` gesichert.

## Strenger Bestandsschutz

- Neue Dateien aus dem Paket werden ergänzt.
- Bereits vorhandene Dateien bleiben unverändert, selbst wenn GitHub eine andere Version enthält.
- Die **einzige Ausnahme** ist die `## Interface:`-Zeile der bestehenden oder neuen `.toc`-Datei: Sie wird nach Bestätigung an das gespeicherte WoW-Client-Profil angepasst. Andere TOC-Einträge bleiben erhalten.
- Zusätzliche lokale Dateien, unbekannte Dateiendungen und persönliche Lua-Textlisten bleiben erhalten.
- Die angezeigte Vorschau wird direkt vor der Installation nochmals durch Dateihashes validiert.
- Die Installation verwendet einen temporären Ordner im Zielverzeichnis und sichert den vorherigen Stand. Ein Rollback kann über die vorhandene `addon_manager.rollback(...)`-Funktion mit dem Sicherungspfad durchgeführt werden.

**Wichtige Einschränkung:** Hier wird noch **kein vollständiges Update bereits vorhandener Lua-Programmdateien** vorgenommen. Ohne vertrauenswürdige frühere Baseline lässt sich nicht zwischen geändertem Originalcode und Benutzeränderungen unterscheiden. Der Text-Merge aus PR #19 ist nicht als automatischer Schreibvorgang eingebunden. Der Installationsdialog kennzeichnet vorhandene geänderte Dateien daher als geschützt. Eine reine TOC-Änderung stellt auch keine WoW-API-Kompatibilität her. Nicht bestätigte Clienttypen erfordern eine bewusste manuelle Testentscheidung.

## Windows-Abnahme

```powershell
python -m unittest discover -s tests -p "test_safe_github_install.py" -v
```

Zusätzlich auf einem separaten Testclient installieren, lokalisierte Texte bewusst verändern, neue GitHub-Dateien ergänzen, TOC-Interface kontrollieren und Sicherung/Restore prüfen. Die automatischen Tests wurden erstellt, hier nicht auf Windows ausgeführt. Dieser Stand ist deshalb ein Draft-PR.

## Experimenteller Live-Test: gezielt freigegebene Updates (PR)

Der Anwenderdialog bietet bei abweichenden bereits vorhandenen Dateien eine zusätzliche
Dateiauswahl. **Standard: alle Kontrollkästchen aus.** Nur bewusst markierte Dateien
werden durch die verifizierte Version aus dem GitHub-Staging ersetzt. Die UI zeigt
anschließend die Anzahl der freigegebenen Ersetzungen. Die unveränderte, erneut
geprüfte Dateiauswahl wird vor dem Tausch in ein vollständiges AddOn-Backup unter
`Interface/AddOns/.addon-backups/` gesichert. Bei Installationsfehlern erfolgt
bestmöglich ein Rollback. Unmarkierte Dateien bleiben unverändert.

### Manueller Windows-Test auf einer Kopie (empfohlen)

1. WoW schließen. **Gesamten** `Interface/AddOns/PaladinRP`-Ordner extern sichern.
2. RP Text Studio aus dem Branch `feature/approved-existing-addon-updates` starten,
   zum Beispiel aus dem Repository mit `python main.py`. Eine ältere EXE enthält
   die neue Funktion noch nicht.
3. AddOns → Anwender-Verwaltung; korrekten WoW-Client und das zuvor gespeicherte
   Interface-Profil kontrollieren. PaladinRP wählen, Kanal **Entwicklungsstand**.
4. **Paket prüfen und bereitstellen…**, anschließend **Geprüftes Paket installieren…**.
5. Die fünf (oder eine andere Anzahl) abweichenden Dateien erscheinen einzeln und
   **ungewählt**. Zum Test nur bekannte unveränderte Originaldateien markieren;
   insbesondere eigene Textlisten nicht ohne vorherige Kontrolle ersetzen.
6. Im zweiten Bestätigungsdialog die Dateianzahl kontrollieren, Installation
   bewusst freigeben, anschließend `locales/deDE/Abilities.lua` auf
   `PURIFY` / `CLEANSE` prüfen; `core/Text.lua` braucht ebenfalls die neue
   Schlüsselerkennung. Die angepasste `## Interface:`-Nummer beweist keine
   Funktionskompatibilität zum WoW-Client.
7. Bei Bedarf die vollständige Sicherung unter `.addon-backups/<Kennung>/PaladinRP`
   zurückspielen (WoW geschlossen). Das Backup vor der Installation nicht löschen.

Für Regressionstests: `python -m unittest discover -s tests -p "test_safe_github_install.py" -v`.
Dieser PR enthält **keine automatische Drei-Wege-Zusammenführung** lokaler Texte.
