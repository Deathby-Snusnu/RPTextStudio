# Fehlende RP-AddOns erstmals installieren

Die AddOn-Verwaltung bietet zusätzlich zur Einzelinstallation die
Schaltfläche **AddOns auswählen und installieren…**.

## Ablauf

1. Bestätigte WoW-Installation mit vorhandener `Interface/AddOns`-Struktur wählen.
2. Interface-Nummer in **Interface-Profil…** hinterlegen; eine Interface-Nummer allein bestätigt keine Kompatibilität des AddOns mit dem Client.
3. Release- oder Entwicklungs-Kanal einstellen und **AddOns auswählen und installieren…** klicken.
4. Gewünschte fehlende AddOns in der zunächst unmarkierten Liste auswählen,
   **Auswahl vorbereiten** klicken und den Download bestätigen. Die
   ZIP-Pakete werden **außerhalb von WoW** geladen und validiert; vorhandene
   AddOn-Verzeichnisse werden nicht berührt.
5. Erst danach **Ausgewählte AddOns jetzt installieren…** klicken, die gemeinsame
   Vorschau prüfen und ausdrücklich **Installieren** bestätigen.

Der mitgelieferte Katalog enthält `DruidenRP`, `HexerRP`, `JaegerRP`,
`MagierRP`, `PaladinRP`, `RPChatMod` und `RPControlCenter`. Für den gewählten
Kanal muss ein passendes Repository-Paket verfügbar sein.

## Bestandsschutz und Sicherheitsregeln

- Ausschließlich **fehlende** AddOn-Ordner werden angelegt; bereits vorhandene Ordner bleiben bytegleich, einschließlich eigener RP-Texte und Einstellungen.
- Die `## Interface:`-Zeile neuer TOC-Dateien wird anhand des gespeicherten Profils angepasst. Dies garantiert **keine** tatsächliche API-Kompatibilität. Bei nicht bestätigter Kombination ist die Zustimmung ausdrücklich eine Testfreigabe.
- Vor der Installation werden **alle ausgewählten** fehlenden Pakete vorbereitet und geprüft; vor dem eigentlichen Kopieren erfolgen nochmals Prüfungen, ob die Pläne unverändert und die AddOns weiterhin fehlend sind.
- Der Installer schreibt pro Paket Wiederherstellungsinformationen im Backup-Verzeichnis. Bei einem Fehler während des Batches versucht er, alle zuvor neu installierten Pakete in umgekehrter Reihenfolge zurückzunehmen. Falls eine Rückabwicklung fehlschlägt, wird der Fehler ausdrücklich gemeldet.
- Staging-Ordner werden beim Schließen des Dialogs oder nach erfolgreicher Sammelinstallation beseitigt. Nach einem Installationsfehler bleibt der vorbereitete Stand bis zum Schließen verfügbar.
- Ein vollständig fehlender `Interface/AddOns`-Ordner wird derzeit **nicht** automatisch erzeugt. Ein vorhandener, leerer Ordner wird unterstützt.

## Tests

Im RPTextStudio-Quellverzeichnis:

```powershell
python -m unittest discover -s tests -p "test_batch_addon_install.py" -v
python -m unittest discover -s tests -p "test_guided_addon_selection.py" -v
```

Die Tests ersetzen keinen Windows- oder Clienttest. Für den ersten Praxistest
ausschließlich eine separate WoW-Testinstallation verwenden.
