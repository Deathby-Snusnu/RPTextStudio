# Sicherer GitHub-Download und AddOn-Installation

## Ablauf

1. **AddOns → Anwender: Installierte AddOns prüfen…** öffnen und WoW-Installation auswählen.
2. **Interface-Profil…**: Interface-Nummer aus dem tatsächlich gestarteten Client hinterlegen.
3. AddOn in der Tabelle markieren, GitHub-Kanal wählen und **AddOn herunterladen und prüfen…** anklicken. Alternativ führt **Ausgewähltes AddOn aktualisieren…** von einem installierten AddOn zur gleichen geschützten Vorschau.
4. Den Download bestätigen. Das Paket wird automatisch in einem temporären
   Ordner **außerhalb von WoW** vorbereitet und geprüft.
5. **Geprüftes Paket installieren…** klicken beziehungsweise die geführte
   Update-Vorschau verwenden. Bei abweichenden vorhandenen Dateien
   gegebenenfalls einzelne Ersetzungen bewusst auswählen; standardmäßig ist
   keine Datei markiert.
6. Anzahl neuer, geschützter und zur Ersetzung freigegebener Dateien,
   TOC-Anpassung und Kompatibilitätshinweis kontrollieren. Erst mit
   **Installieren** ausdrücklich bestätigen. Der alte AddOn-Ordner wird vor
   dem Austausch unter `Interface/AddOns/.addon-backups/<Kennung>/` gesichert.

## Strenger Bestandsschutz

- Neue Dateien aus dem Paket werden ergänzt.
- Bereits vorhandene, abweichende Dateien bleiben standardmäßig unverändert.
  Sie können einzeln zur Ersetzung durch die geprüfte Fassung freigegeben
  werden; lokale Änderungen an ausgewählten Dateien bleiben dann nur im Backup.
- Die vollständige `.toc`-Datei wird nach Vorschau und Bestätigung aus dem
  geprüften GitHub-Paket übernommen, einschließlich `## Version:` und neuer
  Lua-Ladeeinträge. Nur `## Interface:` wird an das WoW-Client-Profil angepasst.
  Frühere eigene TOC-Änderungen bleiben im vollständigen Backup erhalten.
  Die TOC muss nicht einzeln als geschützte Datei freigegeben werden.
- Zusätzliche lokale Dateien, unbekannte Dateiendungen und nicht zur
  Ersetzung ausgewählte persönliche Lua-Textlisten bleiben erhalten.
- Die angezeigte Vorschau wird direkt vor der Installation nochmals durch Dateihashes validiert.
- Die Installation verwendet einen temporären Ordner im Zielverzeichnis und sichert den vorherigen Stand. Ein Rollback kann über die vorhandene `addon_manager.rollback(...)`-Funktion mit dem Sicherungspfad durchgeführt werden.

**Wichtige Einschränkung:** Die TOC wird vollständig aktualisiert, aber ohne
ausdrückliche Dateiauswahl erfolgt kein vollständiges Update vorhandener
Lua-Programmdateien. Ohne vertrauenswürdige
frühere Baseline lässt sich nicht zwischen geändertem Originalcode und
Benutzeränderungen unterscheiden. Die [Text-Merge-Vorschau](RP-TEXT-MERGE.md)
ist nicht als automatischer Schreibvorgang eingebunden. Eine reine
TOC-Änderung stellt keine WoW-API-Kompatibilität her. Nicht bestätigte
Clienttypen erfordern eine bewusste manuelle Testentscheidung.

## Windows-Abnahme

Im RPTextStudio-Quellverzeichnis:

```powershell
python -m unittest discover -s tests -p "test_safe_github_install.py" -v
```

Zusätzlich auf einem separaten Testclient installieren, lokalisierte Texte
bewusst verändern, neue GitHub-Dateien ergänzen, TOC-Interface kontrollieren
und Sicherung/Restore prüfen. Die automatischen Tests ersetzen keine
Windows-Abnahme oder einen Ingame-Test.

## Gezielt freigegebene Updates

Der Anwenderdialog bietet bei abweichenden bereits vorhandenen Dateien eine zusätzliche
Dateiauswahl. **Standard: alle Kontrollkästchen aus.** Nur bewusst markierte Dateien
werden durch die verifizierte Version aus dem GitHub-Staging ersetzt. Die UI zeigt
anschließend die Anzahl der freigegebenen Ersetzungen. Die unveränderte, erneut
geprüfte Dateiauswahl wird vor dem Tausch in ein vollständiges AddOn-Backup unter
`Interface/AddOns/.addon-backups/` gesichert. Bei Installationsfehlern erfolgt
bestmöglich ein Rollback. Unmarkierte Dateien bleiben unverändert.

### Manueller Windows-Test auf einer Kopie (empfohlen)

1. WoW schließen. **Gesamten** `Interface/AddOns/PaladinRP`-Ordner extern sichern.
2. Den aktuellen RP-Text-Studio-Quellstand oder eine nachweislich daraus
   gebaute EXE starten. Eine ältere EXE kann einen anderen Stand enthalten.
3. AddOns → Anwender-Verwaltung; korrekten WoW-Client und das zuvor gespeicherte
   Interface-Profil kontrollieren. PaladinRP wählen, Kanal **Entwicklungsstand**.
4. **AddOn herunterladen und prüfen…**, anschließend **Geprüftes Paket installieren…**.
5. Abweichende Dateien erscheinen einzeln und
   **ungewählt**. Zum Test nur bekannte unveränderte Originaldateien markieren;
   insbesondere eigene Textlisten nicht ohne vorherige Kontrolle ersetzen.
6. Im zweiten Bestätigungsdialog die Dateianzahl kontrollieren, Installation
   bewusst freigeben und danach die ausgewählten Dateien prüfen. Die
   angepasste `## Interface:`-Nummer beweist keine Funktionskompatibilität
   zum WoW-Client.
7. Bei Bedarf die vollständige Sicherung unter `.addon-backups/<Kennung>/PaladinRP`
   zurückspielen (WoW geschlossen). Das Backup vor der Installation nicht löschen.

Für Regressionstests: `python -m unittest discover -s tests -p "test_safe_github_install.py" -v`.
Ein TOC-only-Update (neue Version/Ladeeinträge bei bereits vorhandenen Lua-Dateien)
führt nun ebenfalls zur Installationsvorschau und wird mit Backup angewendet.
Nach dem Einspielen WoW vollständig neu starten und die geladenen AddOns prüfen.
Es erfolgt **keine automatische Drei-Wege-Zusammenführung** lokaler Texte.
