# ClassTiles — öffentliche Website

Landing-Page, Modul-Seiten, Handbücher und Rechtstexte der App **ClassTiles**, gehostet über
GitHub Pages unter [classtiles.de](https://classtiles.de).

**Deutsch (maßgeblich):** `index.html`, `modul-*.html` (6), `handbuecher.html`, `handbuch-*.html`,
`digitalisierung-ki.html`, `datenschutz.html`, `impressum.html`, `nutzungsbedingungen.html`,
`support.html`

**English (convenience translation):** `en/index.html`, `en/module-*.html` (6), `en/manuals.html`,
`en/digitalisation-ai.html`, `en/privacy.html`, `en/imprint.html`, `en/terms.html`,
`en/support.html`

`assets/` enthält Video, Standbilder und Screenshots (sprachneutral), `assets/handbuch/` die
Handbuch-Bilder und -PDFs.

## Pflege

Die Seiteninhalte werden **hier** gepflegt. Der Generator `scripts/legal-pages/build.py` im privaten
App-Repo hat die Seiten ursprünglich erzeugt, ist aber seit Commit `b3b72ac9` nicht mehr die Quelle
(App-Store-Badges, Cloudflare Web Analytics, Instagram-Links und mehrere Rechtstext-Korrekturen
existieren nur hier). Er wird nicht mehr benutzt.

Gemeinsam sind allen Seiten nur Kopfleiste, Fußzeile, CSS und das Inline-Skript — die liegen in
`tools/shell/` und werden mit `tools/apply-shell.py` in alle Seiten geschrieben:

```bash
python3 tools/apply-shell.py          # Shell in alle Seiten zurückschreiben
python3 tools/apply-shell.py --check  # nur prüfen (Exit-Code 1 bei Abweichung)
python3 tools/check-links.py          # interne Links, Anker, Fremdressourcen
python3 -m unittest discover -s tools/tests -v
```

Zwei Seiten werden erzeugt statt von Hand gepflegt, weil sie aus vielen gleichartigen Kacheln
bestehen:

```bash
python3 tools/pages/handbuecher.py    # handbuecher.html
python3 tools/pages/angebot.py        # digitalisierung-ki.html + die zwei EN-Hinweisseiten
```

## Ein neues Handbuch veröffentlichen

Quelle ist ein Ordner unter `~/mobai` mit `handbuch.html`, `screenshots/` und dem PDF:

```bash
python3 tools/handbuch-web.py ~/mobai/handbuch3 --slug kalender --modul 2
# Zahlen aus der Ausgabe in tools/pages/handbuecher.py eintragen, dann:
python3 tools/pages/handbuecher.py
python3 tools/apply-shell.py && python3 tools/check-links.py
```

Das PDF wird unverändert übernommen. Ein Neubau aus den WebP-Screenshots wurde versucht und wieder
verworfen: Chrome rastert beim Drucken jedes Bild in Druckauflösung neu, das Ergebnis war größer
als das Original statt kleiner.

## Grundsätze

- **Kein externer Request** außer dem Cookie-freien Cloudflare-Beacon: keine Webfont, kein CDN,
  kein iframe, kein Formulardienst. Nur so bleibt die Seite ohne Cookie-Banner (§ 25 TDDDG) und
  die Aussage der Datenschutzerklärung wahr. `tools/check-links.py` prüft das mit.
- Die Kapitelanker der Handbücher (`#kapitel-3`) sind eine öffentliche Schnittstelle und dürfen
  sich zwischen Auflagen nicht ändern.
- Maßgeblich ist die deutsche Fassung; Englisch ist eine Convenience-Übersetzung.
