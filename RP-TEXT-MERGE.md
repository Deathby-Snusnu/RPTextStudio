# RP-Text-Merge: schreibgeschützte Vorschau für die gesamte RP-AddOn-Familie

Diese erste Ausbaustufe integriert **keine Dateien automatisch**. Der konservative Drei-Wege-Vergleich verwendet den vorhandenen Lua-Textlisten-Parser, ohne Lua-Code auszuführen.

## Unterstützte RP-AddOns

- **JaegerRP:** `data/Texts.lua`, `locales/{deDE,enUS,frFR}/Texts.lua`
- **DruidenRP:** `data/Texts.lua`, `locales/{deDE,enUS,frFR}/Texts.lua`
- **HexerRP:** `locales/{deDE,enUS,frFR}/Texts.lua`
- **MagierRP:** Die generische Vorschau kann literale Textlisten aus
  `locales/{deDE,enUS,frFR}` verarbeiten, soweit der Parser sie erkennt.
  Ein MagierRP-spezifischer End-to-End-Test ist hier nicht belegt.
- **PaladinRP:** Textlisten in `data/*.lua` und `locales/{deDE,enUS,frFR}/*.lua`, beispielsweise `Blessings.lua`, `Seals.lua`, `Auras.lua`
- **RPChatMod:** Textlisten in `data/*.lua` und `locales/{deDE,enUS,frFR}/*.lua`, beispielsweise `Races.lua`, `RaceClass.lua`, `Classes.lua`
- **RPControlCenter:** der aktuelle Stand enthält keine vergleichbaren RP-Textlisten; das Control Center bleibt unverändert und wird später nur bei vorhandenen unterstützten Textlisten berücksichtigt.

Die Merge-Engine ist **nicht auf JaegerRP-Namen oder Dateinamen festgelegt**, sondern vergleicht literale Lua-Textlisten unter strukturierten Pfaden. Sie erkennt auch die verschachtelten Schlüssel von PaladinRP und RPChatMod, beispielsweise `addon.localeData.deDE.Blessings.MIGHT.ziel` und `addon.localeData.deDE.raceTexts.Dwarf.HELLO.gruppe`.

## Drei erforderliche Stände

1. **Baseline:** unveränderte vorherige Version der Repo-Textdatei
2. **Lokal:** vom Spieler veränderte Textdatei
3. **Neu:** aktuelle Repo-Textdatei

Aufruf für eine unterstützte Textdatei aus dem RPTextStudio-Quellverzeichnis:

```powershell
python preview_rp_text_merge.py .\alt\Blessings.lua .\lokal\Blessings.lua .\neu\Blessings.lua
```

## Konservative Regeln

- Eigene RP-Texte, einschließlich Sternchen-`/me`-Emotes, bleiben vollständig erhalten.
- Nur Texte, die in der alten Repo-Version **nicht existierten** und lokal ebenfalls nicht vorhanden sind, werden zur Ergänzung vorgeschlagen.
- Entfernte oder umgeschriebene alte Standardtexte werden nicht erneut eingefügt.
- Neue Textschlüssel, verschwundene Listen und nicht sicher analysierbare Strukturen sind **manuell zu prüfende Konflikte**.
- Programmcode, Konfiguration, gespeicherte Variablen und Lua-Ausdrücke werden nicht zusammengeführt.
- Die Engine erstellt nur eine Vorschau und einen möglichen Ergebnisdatensatz; sie schreibt **keine Dateien**.

## Grenzen der Vorschau

Die automatische Beschaffung einer vertrauenswürdigen Baseline, das
Durchlaufen sämtlicher AddOn-Dateien und eine GUI-Konfliktansicht sind nicht
Bestandteil dieser Vorschau. Die getrennte Installationsfunktion schreibt
keinen automatischen Text-Merge. Ein unbekannter Ausgangsstand darf nicht
durch einen Zwei-Wege-Merge ersetzt werden.

## Offline-Tests

```powershell
python -m unittest discover -s tests -p "test_rp_text_merge.py" -v
```

Den Befehl im RPTextStudio-Quellverzeichnis ausführen.
Diese Tests decken sowohl JaegerRP-/DruidenRP-/HexerRP-artige `texts`-Listen als auch PaladinRP- und RPChatMod-Schlüsselstrukturen ab. Ein aktueller End-to-End-Test mit realen Repository-Dateien unter Windows ist hier nicht belegt.
