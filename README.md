# ClassTiles — öffentliche Website

Landing-Page, Modul-Seiten, Handbücher und Rechtstexte der App **ClassTiles**, gehostet über
GitHub Pages unter [classtiles.de](https://classtiles.de).

**Deutsch (maßgeblich):** `index.html`, `preise.html`, `notenschluessel-rechner.html`,
`modul-*.html` (6), `handbuecher.html`, `handbuch-*.html`,
`digitalisierung-ki.html`, `ki-handbuecher.html`, `ki-handbuch-*.html`, `ki-material.html`, `ki-werkstatt.html`, `ki-skills.html`, `ki-simulation.html`, `ki-merkblatt.html`,
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

Gemeinsam sind allen Seiten nur Kopfleiste, Fußzeile, CSS, das Inline-Skript und der Meta-Block —
die liegen in `tools/shell/` und werden mit `tools/apply-shell.py` in alle Seiten geschrieben:

```bash
python3 tools/apply-shell.py          # Shell in alle Seiten zurückschreiben
python3 tools/apply-shell.py --check  # nur prüfen (Exit-Code 1 bei Abweichung)
python3 tools/pages/sitemap.py        # sitemap.xml neu erzeugen (--check zum Prüfen)
python3 tools/check-links.py          # interne Links, Anker, Fremdressourcen
python3 -m unittest discover -s tools/tests -v
```

**Nach jeder neuen oder umbenannten Seite** gehören beide Läufe dazu — `apply-shell.py` setzt den
Meta-Block, `sitemap.py` nimmt die Seite ins Inhaltsverzeichnis auf. Vergisst man den zweiten,
schlägt `test_sitemap_ist_auf_dem_stand` fehl.

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

Wie die drei Passagen überschrieben sind, entscheidet der Band: In `KURZ` steht jede als
(Überschrift, Anker). Band 4 führt weder „Die Idee in einem Satz" noch „Die Methode" und
liefert dort „Was am Ende dasteht" und „Drei Eigenschaften, die den Alltag entscheiden" —
eine erfundene Überschrift über einem wörtlichen Zitat wäre genau die Verschiebung, die das
Schneiden vermeiden soll.

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

## Preisseite und Rechner

Zwei Seiten gibt es **nur auf Deutsch**, mit Absicht:

`preise.html` nennt den Preis der Vollversion. Er steht im Quelltext an **einer** Stelle
(`jsonld.PREIS_VOLLVERSION`); `test_der_preis_steht_nur_an_einer_stelle` vergleicht ihn mit dem
Fließtext der Seite, damit Text und strukturierte Daten nicht auseinanderlaufen. Das Angebot ist
eine `AggregateOffer` von 0 bis zum Vollpreis — beides stimmt: Der Download kostet nichts und
reicht dauerhaft für eine Klasse, die Vollversion ist ein einmaliger In-App-Kauf. Die Aussagen
zum Frei-Umfang stammen aus der Paywall der App (`ClassCreationGate`, `TabCreationGate`,
`ExportGate`): eine Klasse, ein Reiter, kein Export.

`notenschluessel-rechner.html` rechnet Punkte in Noten um. Sie ist die einzige Seite mit eigenem
Skript, und daran hängen drei Regeln:

- **Nichts wird auf dem Gerät abgelegt** — kein Cookie, und auch nicht der Browser-Speicher.
  § 25 TDDDG erfasst das Ablegen unabhängig von der Technik; ein „merke die letzte Einstellung"
  würde das Cookie-Banner erzwingen. `TestKeinSpeicherAufDemGeraet` prüft das für alle Seiten,
  und zwar nur innerhalb von `<script>`-Blöcken: Die KI-Seiten zeigen Prompts, die dem Modell
  genau das verbieten — im Fließtext ist das Wort ein Verbot, kein Zugriff.
- **Das Skript darf nicht mit `(function()` beginnen.** `apply-shell.py` erkennt seinen
  Skriptblock daran; ein zweites Skript mit demselben Anfang würde den Ersatz auf sich ziehen
  und alles bis zum Cloudflare-Kommentar verschlucken, Fußzeile inklusive
  (`test_der_shell_skriptblock_kommt_genau_einmal_vor`).
- **Rechnen und Anzeige sind getrennt** durch die Marke `// ---- Anzeige ----`.
  `tools/tests/test_rechner.py` löst alles davor heraus und führt es in **Node** aus. Das ist
  die einzige Stelle im Repo, die mehr als `python3` braucht — ohne Node überspringt sich der
  Test, statt rot zu werden. Eine Nachbildung der Formel in Python wäre keine Prüfung: Sie
  würde bei jedem Denkfehler genauso falsch rechnen wie die Seite.

Beide Seiten hängen in der **Fußzeile** (Spalte „Handbücher & Werkzeuge") bzw. der
**Kopfleiste** — und damit einen Klick von jeder Seite entfernt. Das ist kein Schmuck:
`tools/tests/test_erreichbarkeit.py` rechnet aus dem fertigen HTML aus, wie viele Verweise auf
eine Seite zeigen und wie tief sie von der Startseite liegt, und lässt für die beiden
Sucheingänge nur Klicktiefe 1 zu. Der Rechner hing nach seinem ersten PR an **einem** Verweis
als letzter Aufzählungspunkt in der Modulseite: für Leser unauffindbar, für Google eine Seite
ohne internes Gewicht. `check-links.py` fand daran nichts — es prüft, ob Verweise ins Leere
gehen, nicht, ob eine Seite genug davon abbekommt.

Die drei ClassTiles-Tabellen im Rechner (1–6, mit Tendenzen, Oberstufe 0–15) sind Kopien aus
`PointsGradingKey+Defaults.swift` im App-Repo. Ändern sie sich dort, müssen sie hier mit —
`test_rechnet_mit_den_tabellen_der_app` hält sie fest, damit das auffällt.

## Was Suchmaschinen lesen

Alles, was für Google und fürs Teilen in Messengern nötig ist, steckt im **Meta-Block** — einem
der fünf Blöcke, die `apply-shell.py` schreibt. Er reicht im Seitenkopf vom ersten `<link>` bis
zum Seitensymbol und enthält canonical, hreflang, Open Graph und die strukturierten Daten.
Titel und Beschreibung gehören weiterhin der Seite; der Block **liest** sie nur und reicht sie
weiter (`test_titel_und_beschreibung_gehoeren_der_seite` bewacht das).

Vier Regeln, die man nicht sieht, wenn man sie bricht — Google verwirft still:

- **canonical** nennt „/" als gültige Startseite, nicht „/index.html". Der Server liefert beide.
- **hreflang** gibt es nur für **echte** Sprachpaare (`shell.is_paired`). `TWIN` schickt jede nur
  deutsche Seite — Handbücher, der ganze KI-Bereich — auf eine englische Hinweisseite. Als
  Sprachverweis wäre das falsch: die eine Hinweisseite kann nicht auf zwölf deutsche zurückzeigen,
  und Google verwirft solche Gruppen mitsamt der einen echten Zuordnung darin.
- Jede Gruppe nennt **sich selbst**, den Zwilling und `x-default` (deutsch, weil maßgeblich).
- **Keine erfundenen Angaben.** Kein `aggregateRating` ohne Bewertungen; die Fragen der
  strukturierten Daten werden aus dem Markup der Support-Seite **gelesen**, nicht gepflegt.

`tools/jsonld.py` baut die strukturierten Daten, `tools/pages/og_image.py` die Vorschaubilder
(1200×630 PNG, braucht die Systemschrift von macOS), `tools/pages/sitemap.py` das
Inhaltsverzeichnis. `robots.txt` steht von Hand in der Wurzel und nennt die Sitemap.

Der Meta-Block lädt **nichts** von fremden Servern: `<link rel="canonical">` und
`<link rel="alternate">` sind Angaben über die Seite, keine eingebundene Ressource, und das
Vorschaubild liegt unter `assets/`. `tools/check-links.py` prüft beides — es lässt diese beiden
`rel`-Werte durch, aber nur mit einer Adresse auf classtiles.de.

Angemeldet wird die Sitemap einmalig in der **Google Search Console**
(`https://classtiles.de/sitemap.xml`). Ohne diese Anmeldung dauert es Wochen, bis Google sie von
selbst findet.

`google8c86af4b4455c27c.html` in der Wurzel ist Googles Bestätigungsdatei für die Search Console
und **darf nicht gelöscht oder umbenannt werden** — sonst verliert die Search Console die
Bestätigung und mit ihr alle Daten. Sie gehört nicht zur Website: `shell.pages()` übergeht sie
(`shell.BESTAETIGUNGSDATEI`), weil sie weder Kopfleiste noch Meta-Block trägt und
`apply-shell.py` sonst abbrechen würde. Zwei Tests bewachen beides.

## Grundsätze

- **Kein externer Request** außer dem Cookie-freien Cloudflare-Beacon: keine Webfont, kein CDN,
  kein iframe, kein Formulardienst. Nur so bleibt die Seite ohne Cookie-Banner (§ 25 TDDDG) und
  die Aussage der Datenschutzerklärung wahr. `tools/check-links.py` prüft das mit.
- Die Kapitelanker der Handbücher (`#kapitel-3`) sind eine öffentliche Schnittstelle und dürfen
  sich zwischen Auflagen nicht ändern.
- Maßgeblich ist die deutsche Fassung; Englisch ist eine Convenience-Übersetzung.
