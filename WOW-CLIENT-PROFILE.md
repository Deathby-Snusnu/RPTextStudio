# WoW-Client-Profile und TOC-Vorschau

## Bedienung
Öffne **AddOns → Anwender: Installierte AddOns prüfen…**. Wähle deine erkannte WoW-Installation aus und klicke auf **Interface-Profil…**. Gib die Interface-Nummer ein, die der *tatsächlich gestartete Spielclient* liefert:

```lua
/dump select(4, GetBuildInfo())
```

Das Profil wird pro Installation im lokalen Benutzerprofil unter
`%LOCALAPPDATA%\RPTextStudio\client_profiles.json` gespeichert und verändert
keine AddOn-Dateien. Ohne `LOCALAPPDATA` wird stattdessen
`~\.rptextstudio\client_profiles.json` verwendet. Die Profilnummer wird nicht
aus dem Verzeichnisnamen als aktuelle Patchnummer abgeleitet.

Ein lokal installiertes AddOn in der Tabelle auswählen und **TOC-Vorschau…** klicken. Der Dialog zeigt die bisherige und die vorgeschlagene `## Interface:`-Zeile sowie den Kompatibilitätsstatus, ohne etwas zu schreiben.

## Wichtige Trennung

- **AddOn-Version:** Repository-Version.
- **Client-Interface:** Versionsnummer des lokal gestarteten WoW-Clients.
- **AddOn-Kompatibilität:** separate Freigabe. Der Code deklariert für die
  sechs bisherigen AddOns einen Eintrag `forever`; für MagierRP gibt es in
  dieser Zuordnung keinen Eintrag. Andere erkannte Clienttypen werden nicht
  automatisch als kompatibel eingestuft. Ein benutzerdefinierter
  Forever-Ordner wird auch nicht anhand seines Namens allein als geprüft
  erkannt. Ein Eintrag oder eine Interface-Nummer ersetzt keinen Clienttest.
- **TOC-Vorschau:** dient nur der Information. Ein neuer Eintrag kann die fehlende WoW-API-Kompatibilität nicht herstellen.

`preview_toc(..., compatible=True)` erzeugt selbst nur den angepassten
TOC-Inhalt und schreibt keine Datei. Die getrennte, ausdrücklich bestätigte
Installation verwendet diese Vorschau nach Prüfung des WoW-Profils; sie sichert
den vorherigen AddOn-Ordner und verändert erst dann die Installation. Siehe
[sichere GitHub-Installation](SAFE-GITHUB-INSTALL.md) und
[Erstinstallation](FIRST-INSTALL-RP-ADDONS.md).

## Tests

```powershell
python -m unittest discover -s tests -p "test_wow_client_profiles.py" -v
```

Den Befehl im RPTextStudio-Quellverzeichnis ausführen. Ein Windows-Praxistest
mit den jeweils eingesetzten Clients bleibt zusätzlich erforderlich.


## Updates bei abweichender TOC-Interface-Nummer

Die Versionsprüfung vergleicht Versionsnummern unabhängig von der `## Interface`-Zeile.
Eine Abweichung wird zusätzlich als Hinweis angezeigt und verhindert nicht,
dass ein vorhandenes AddOn zur Aktualisierung ausgewählt wird.
Bei der Installation bleiben Paketprüfung, Änderungsvorschau, Bestandsschutz,
Backup und ausdrückliche Bestätigung erforderlich. Das gespeicherte
Interface-Profil des **tatsächlich ausgewählten WoW-Clients** wird für die
TOC-Anpassung verwendet. Eine Änderung dieser Metadaten beweist keine
Laufzeitkompatibilität mit beliebigen anderen WoW-Versionen.
