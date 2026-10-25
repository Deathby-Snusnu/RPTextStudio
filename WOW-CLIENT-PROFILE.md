# WoW-Client-Profile und TOC-Vorschau

## Bedienung
Öffne **AddOns → Anwender: Installierte AddOns prüfen…**. Wähle deine erkannte WoW-Installation aus und klicke auf **Interface-Profil…**. Gib die Interface-Nummer ein, die der *tatsächlich gestartete Spielclient* liefert:

```lua
/dump select(4, GetBuildInfo())
```

Das Profil wird pro Installation ausschließlich im lokalen Benutzerprofil unter `RPTextStudio/client_profiles.json` gespeichert und verändert keine AddOn-Dateien. Die Profilnummer wird nicht aus dem Verzeichnisnamen als aktuelle Patchnummer abgeleitet.

Ein lokal installiertes AddOn in der Tabelle auswählen und **TOC-Vorschau…** klicken. Der Dialog zeigt die bisherige und die vorgeschlagene `## Interface:`-Zeile sowie den Kompatibilitätsstatus, ohne etwas zu schreiben.

## Wichtige Trennung

- **AddOn-Version:** Repository-Version.
- **Client-Interface:** Versionsnummer des lokal gestarteten WoW-Clients.
- **Getestete AddOn-Kompatibilität:** separate Freigabe. Alle sechs vorhandenen AddOns sind derzeit nur für die Forever-Zielplattform vorgesehen; die Implementierung erklärt andere erkannte Clienttypen **nicht** automatisch für kompatibel. Ein benutzerdefinierter Forever-Ordner wird auch nicht anhand seines Namens allein als geprüft eingestuft.
- **TOC-Vorschau:** dient nur der Information. Ein neuer Eintrag kann die fehlende WoW-API-Kompatibilität nicht herstellen.

Der Helper `preview_toc(..., compatible=True)` ist nur für *explizit autorisierte Vorschau* verwendbar. Es gibt in diesem PR **keinen TOC-Schreibvorgang, keinen automatischen Import und keine Installation**. Eine spätere Installation muss separat per Client und AddOn kompatibilitätsgeprüft, bestätigt und gesichert werden.

## Tests

```powershell
python -m unittest discover -s tests -p "test_wow_client_profiles.py" -v
```

Tests erstellt, nicht auf Windows ausgeführt. Die Client-Profilseite benötigt noch einen Windows-Praxistest mit Forever, Classic Era und optional Retail.
