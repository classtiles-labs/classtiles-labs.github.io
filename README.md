# ClassTiles — öffentliche Website

Landing-Page, Modul-Seiten, Handbücher und Rechtstexte der App **ClassTiles**, gehostet über
GitHub Pages unter [classtiles.de](https://classtiles.de).

**Deutsch (maßgeblich):** `index.html`, `modul-*.html` (6), `handbuecher.html`, `handbuch-*.html`,
`digitalisierung-ki.html`, `ki-handbuecher.html`, `ki-handbuch-*.html`, `ki-material.html`,
`datenschutz.html`, `impressum.html`, `nutzungsbedingungen.html`, `support.html`

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
python3 tools/pages/handbuecher.py       # handbuecher.html
python3 tools/pages/angebot.py           # digitalisierung-ki.html + die zwei EN-Hinweisseiten
python3 tools/pages/ki_handbuecher.py    # ki-handbuecher.html + ki-handbuch-*.html
python3 tools/pages/ki_kurzfassungen.py  # ki-kurzfassung-*.html
python3 tools/pages/ki_glossar.py        # ki-glossar.html
python3 tools/pages/ki_material.py       # ki-material.html
python3 tools/pages/ki_neues.py          # ki-neues.html
```

Die vier `ki_*`-Generatoren hängen voneinander ab: Kurzfassungen und Glossar verlinken Anker
der Handbuchseiten. Nach einer Änderung an einem Band deshalb `ki_handbuecher.py`,
`ki_kurzfassungen.py` und `ki_glossar.py` zusammen laufen lassen.

## Der KI-Bereich

`digitalisierung-ki.html` ist der Einstieg; darunter hängen Handbücher, Kurzfassungen,
Glossar, Material und Neues. Quelle der Bände ist **nicht** dieses Repo, sondern das Markdown
im Nachbarrepo `../Instagram` — es wird gelesen, nicht kopiert; versioniert sind hier nur das
erzeugte HTML und die PDFs unter `assets/ki/`. Welcher Band aus welcher Datei kommt, steht in
`BAENDE` in `tools/pages/ki_handbuecher.py`.

### Einen Eintrag unter „Neues" schreiben

Das ist der einzige Teil, der laufend gepflegt wird. Eine Datei anlegen, dann bauen:

```
inhalt/neues/2026-08-18-eine-kennung.md

---
titel: Worum es geht
art: Tipp                        # Neu · Tipp · Entwicklung
weiter:
  - Band 1, Kapitel 04 | ki-handbuch-workflows.html#kapitel-04
---
Markdown wie in den Handbüchern.
```

Das Datum steht im Dateinamen, nicht im Kopf — so kann es nicht auseinanderlaufen. Jeder
Eintrag trägt seinen Dateinamen als Anker (`ki-neues.html#2026-08-18-eine-kennung`); genau der
gehört in die Instagram-Bio. Ein falsches Format, eine unbekannte `art` oder ein `weiter` auf
eine fehlende Seite beenden den Lauf mit einer Meldung.

`tools/handbuchtext.py` setzt dieses Markdown für den Bildschirm. Es ist bewusst ein zweiter
Renderer neben dem der Instagram-Werkstatt (Node, `marked`): Die beiden setzen verschiedene
Medien und teilen keine CSS-Regel, und der gesamte Bau hier ist `python3 tools/…` ohne
Abhängigkeit. Die Grammatik ist auf das begrenzt, was in den Bänden vorkommt; alles andere
bricht den Lauf ab, statt still durchzurutschen.

Eine Ausnahme ist das **Claude-Cowork-Heft**: Es wurde als Druckheft gesetzt, nicht in Markdown
geschrieben, und wird deshalb von `tools/coworkweb.py` gelesen. Das Modul liefert genau dieselben
Felder wie `handbuchtext.parse()`, sodass die Leseseite auf demselben Weg entsteht. Es biegt
dabei zweierlei um: die Anker der Quelle (`id="c01"` → `id="kapitel-01"`, damit die Konvention
des Bereichs gilt) und die 17 eingebetteten Base64-Bilder, die nach `assets/ki/cowork/` als WebP
wandern — aus 2,8 MB Quelle werden 88 KB Seite plus 372 KB Bilder. Das Heft hat als einziger
Titel keine Kurzfassung; seine Quelle führt die Abschnitte nicht, aus denen eine gebaut wird.
Erkennbar ist das am fehlenden `kurz_minuten` in `BAENDE`.

Die Kapitelanker der KI-Handbücher tragen zusätzlich Abschnittsanker
(`#kapitel-00-prompt`), weil `## Die Grenze` in jedem Kapitel steht. Sie sind eine öffentliche
Schnittstelle: Glossar und Kurzfassungen verlinken sie. Zeigt ein Eintrag auf einen Anker, den
es nicht mehr gibt, bricht der jeweilige Generator ab — `tools/check-links.py` ist das zweite
Netz, nicht das erste.

Die Kurzfassungen schneiden die selbstzusammenfassenden Passagen der Bände („Die Idee in einem
Satz", „Die Methode", „Was hier nicht versprochen wird") **wörtlich** heraus, statt sie zu
paraphrasieren. Selbst geschrieben sind nur die Mitnehmpunkte in `KURZ`, und jeder davon nennt
das Kapitel, aus dem er stammt.

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
