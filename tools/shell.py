"""Kopfleiste, Fußzeile, CSS und Skripte der Website — an einer Stelle.

Bis Commit b3b72ac9 wurden diese Blöcke von scripts/legal-pages/build.py im App-Repo erzeugt.
Der Generator ist seither nicht mehr die Quelle (App-Store-Badges, Cloudflare, Instagram und
mehrere Rechtstext-Korrekturen existieren nur hier). Gepflegt wird ab jetzt dieses Modul:
es kennt die Shell, kennt aber bewusst keinen Seiteninhalt.
"""
import html
import os
import posixpath
import re

import jsonld

HERE = os.path.dirname(os.path.abspath(__file__))

CSS = open(os.path.join(HERE, "shell", "site.css"), encoding="utf-8").read()
ICON = open(os.path.join(HERE, "shell", "app-icon.datauri.txt"), encoding="utf-8").read().strip()

# ---------- Adresse der Website ----------
# Ohne Schrägstrich am Ende; canonical_of() hängt ihn an. Suchmaschinen brauchen absolute URLs:
# ein relativer canonical-Verweis wäre wirkungslos.
SITE = "https://classtiles.de"

# Vorschaubild beim Teilen (Open Graph). Liegt auf unserem eigenen Server — beim Aufruf der Seite
# wird es nicht geladen, nur von Diensten abgerufen, in denen jemand den Link teilt.
OG_BILD = {"de": "assets/og-classtiles-de.png", "en": "assets/og-classtiles-en.png"}
OG_BILD_GROESSE = (1200, 630)
OG_ALT = {
    "de": "ClassTiles — Notenverwaltung für Lehrkräfte, auf iPad, iPhone und Mac",
    "en": "ClassTiles — grade management for teachers, on iPad, iPhone and Mac",
}
OG_LOCALE = {"de": "de_DE", "en": "en_US"}

# Erster Eintrag im Navigationspfad (Brotkrumen).
START_LABEL = {"de": "Start", "en": "Home"}

# Bestätigungsdateien fremder Dienste liegen in der Wurzel, gehören aber nicht zur Website: sie
# tragen keine Kopfleiste, keinen Meta-Block und dürfen nicht in die Sitemap. Der Name ist von
# Google vorgegeben (google<hex>.html) und darf sich nicht ändern, sonst verliert die Search
# Console die Bestätigung. Das Muster ist absichtlich eng — eine echte Seite namens
# „google-tipps.html" würde weiter gepflegt.
BESTAETIGUNGSDATEI = re.compile(r'^google[0-9a-f]{8,}\.html$')


def pages(root):
    """Die gepflegten Seiten der Website — deutsche in der Wurzel, englische in en/.

    Eine Stelle für alle Werkzeuge: apply-shell, check-links, sitemap und die Tests müssen
    dieselbe Liste sehen, sonst prüft das eine, was das andere gar nicht schreibt.
    """
    out = [n for n in sorted(os.listdir(root))
           if n.endswith(".html") and not BESTAETIGUNGSDATEI.match(n)]
    endir = os.path.join(root, "en")
    if os.path.isdir(endir):
        out += ["en/" + n for n in sorted(os.listdir(endir)) if n.endswith(".html")]
    return out

# ---------- Navigation ----------
# (href, Beschriftung) der Kopfleiste. Sie zeigt, was Besucher suchen; die Rechtstexte stehen
# vollständig im Fuß jeder Seite — das Impressum bleibt damit von überall einen Klick entfernt.
# Der href ist relativ zur jeweiligen Sprachfassung: eine deutsche Seite liegt in der Wurzel,
# eine englische in /en/ — beide verlinken „ihre" Dateien ohne Präfix.
NAV = {
    # „Preise" steht nur in der deutschen Leiste: Die Seite gibt es nur auf Deutsch, weil sie
    # einen Euro-Preis nennt. Die englische Leiste bleibt bei vier Einträgen.
    "de": [("index.html#module", "Module"), ("handbuecher.html", "Handbücher"),
           ("digitalisierung-ki.html", "Digitalisierung &amp; KI"), ("preise.html", "Preise"),
           ("support.html", "Support")],
    "en": [("index.html#module", "Modules"), ("manuals.html", "Manuals"),
           ("digitalisation-ai.html", "Digitalisation &amp; AI"), ("support.html", "Support")],
}

# Welcher Navigationseintrag wird auf welcher Seite hervorgehoben. Eine Modulseite hebt „Module"
# hervor, eine Handbuchseite „Handbücher" — der Reiter steht für den Bereich, nicht für die Datei.
ACTIVE = {
    "support.html": "support.html",
    "en/support.html": "support.html",
}
for _f in ("index.html", "modul-notenverwaltung.html", "modul-kalender.html", "modul-planung.html",
           "modul-gruppen.html", "modul-dokumentation.html", "modul-klassengeschaefte.html"):
    ACTIVE[_f] = "index.html#module"
for _f in ("index.html", "module-grades.html", "module-calendar.html", "module-planning.html",
           "module-groups.html", "module-documentation.html", "module-tasks.html"):
    ACTIVE["en/" + _f] = "index.html#module"
ACTIVE["preise.html"] = "preise.html"
ACTIVE["handbuecher.html"] = "handbuecher.html"
ACTIVE["handbuch-notenverwaltung.html"] = "handbuecher.html"
ACTIVE["handbuch-gruppen-sitzordnung.html"] = "handbuecher.html"
ACTIVE["en/manuals.html"] = "manuals.html"
ACTIVE["en/digitalisation-ai.html"] = "digitalisation-ai.html"
# notenschluessel-rechner.html steht mit Absicht NICHT hier: Der Rechner ist ein Seiteneingang
# aus der Suche, kein Bereich der Website. Ohne Eintrag hebt er keinen Reiter hervor und seine
# Brotkrume bleibt Start → Notenschlüssel-Rechner.

# Der KI-Bereich ist ein Baum unter „Digitalisierung & KI": Regal, Bände und die Blätter für
# die Klasse heben alle denselben Reiter hervor.
KI_SEITEN = ["digitalisierung-ki.html", "ki-handbuecher.html", "ki-material.html",
             "ki-glossar.html", "ki-neues.html", "ki-werkstatt.html", "ki-lernspiel.html",
             "ki-skills.html", "ki-simulation.html"]
KI_BAENDE = ("workflows", "materialwerkstatt", "ablauf", "uebungsseiten", "assistent", "cowork")
# Das Cowork-Heft hat keine Kurzfassung — siehe tools/pages/ki_kurzfassungen.py.
KI_KURZFASSUNGEN = KI_BAENDE[:-1]
KI_SEITEN += [f"ki-handbuch-{s}.html" for s in KI_BAENDE]
KI_SEITEN += [f"ki-kurzfassung-{s}.html" for s in KI_KURZFASSUNGEN]
for _f in KI_SEITEN:
    ACTIVE[_f] = "digitalisierung-ki.html"

# Sprachpaare. Schlüssel ist der Dateiname ohne Sprachverzeichnis.
TWIN = {
    "index.html": "index.html",
    "support.html": "support.html",
    "datenschutz.html": "privacy.html",
    "impressum.html": "imprint.html",
    "nutzungsbedingungen.html": "terms.html",
    "modul-notenverwaltung.html": "module-grades.html",
    "modul-kalender.html": "module-calendar.html",
    "modul-planung.html": "module-planning.html",
    "modul-gruppen.html": "module-groups.html",
    "modul-dokumentation.html": "module-documentation.html",
    "modul-klassengeschaefte.html": "module-tasks.html",
    "handbuecher.html": "manuals.html",
    "digitalisierung-ki.html": "digitalisation-ai.html",
}
TWIN.update({v: k for k, v in TWIN.items() if k not in ("index.html", "support.html")})

# Die Handbücher selbst gibt es nur auf Deutsch; die englische Fassung ist die Hinweisseite.
TWIN["handbuch-notenverwaltung.html"] = "manuals.html"
TWIN["handbuch-gruppen-sitzordnung.html"] = "manuals.html"

# Ebenso der KI-Bereich: Die Inhalte richten sich an deutschsprachige Schulen, der englische
# Zwilling ist für alle Seiten die Hinweisseite.
for _f in KI_SEITEN[1:]:
    TWIN[_f] = "digitalisation-ai.html"

LANG_LABEL = {"de": ("English", "en"), "en": ("Deutsch", "de")}

IG_URL = "https://www.instagram.com/classtiles/"
IG_LABEL = {"de": "ClassTiles auf Instagram", "en": "ClassTiles on Instagram"}

MODULES = {
    "de": [("modul-notenverwaltung.html", "Notenverwaltung"), ("modul-kalender.html", "Kalender"),
           ("modul-planung.html", "Planung"), ("modul-gruppen.html", "Gruppen &amp; Sitzordnung"),
           ("modul-dokumentation.html", "Dokumentation"),
           ("modul-klassengeschaefte.html", "Klassengeschäfte")],
    "en": [("module-grades.html", "Grades"), ("module-calendar.html", "Calendar"),
           ("module-planning.html", "Planning"), ("module-groups.html", "Groups &amp; seating"),
           ("module-documentation.html", "Documentation"), ("module-tasks.html", "Class Tasks")],
}

LEGAL = {
    "de": [("datenschutz.html", "Datenschutz"), ("impressum.html", "Impressum"),
           ("nutzungsbedingungen.html", "Nutzungsbedingungen"), ("support.html", "Support &amp; FAQ")],
    "en": [("privacy.html", "Privacy"), ("imprint.html", "Legal notice"),
           ("terms.html", "Terms of use"), ("support.html", "Support &amp; FAQ")],
}

# Die Handbuchseiten liegen alle in der Wurzel; aus /en/ heraus brauchen sie deshalb „../".
# Der Notenschlüssel-Rechner steht hier mit: Er ist ein Werkzeug für Besucher, und die Fußzeile
# ist der einzige Ort, der auf ALLEN Seiten erscheint. Ohne diesen Eintrag hing er an einem
# einzigen Verweis tief in der Modulseite — für Leser unauffindbar, und für Google eine Seite
# ohne internes Gewicht.
MANUALS = {
    "de": [("handbuch-notenverwaltung.html", "Notenverwaltung"),
           ("handbuch-gruppen-sitzordnung.html", "Gruppen &amp; Sitzordnung"),
           ("handbuecher.html", "Alle Handbücher"),
           ("notenschluessel-rechner.html", "Notenschlüssel-Rechner")],
    "en": [("../handbuch-notenverwaltung.html", "Notenverwaltung (DE)"),
           ("../handbuch-gruppen-sitzordnung.html", "Gruppen &amp; Sitzordnung (DE)"),
           ("manuals.html", "All manuals"),
           ("../notenschluessel-rechner.html", "Notenschlüssel-Rechner (DE)")],
}

FOOTER_TEXT = {
    "de": dict(
        blurb="Notenverwaltung für Lehrkräfte. Läuft lokal auf deinem Gerät. Kein Nutzerkonto, "
              "kein Tracking, keine Werbung.",
        social="ClassTiles auf Instagram", modules="Module",
        manuals="Handbücher &amp; Werkzeuge",
        legal="Rechtliches",
        note="Diese Seite setzt keine Cookies. Besucherzahlen werden anonym und Cookie-frei mit "
             "Cloudflare Web Analytics gemessen. Details in der Datenschutzerklärung."),
    "en": dict(
        blurb="Grade management for teachers. Runs locally on your device — no user account, "
              "no tracking, no ads.",
        social="ClassTiles on Instagram", modules="Modules",
        manuals="Manuals &amp; tools", legal="Legal",
        note="This site sets no cookies. Visitor numbers are measured anonymously and cookie-free "
             "with Cloudflare Web Analytics — see the privacy policy for details. English is a "
             "convenience translation — the German version is the legally binding one."),
}

# Der Instagram-Hinweis erklärt eine bewusste rechtliche Entscheidung und bleibt im Quelltext.
IG_COMMENT = {
    "de": """        <!-- Reiner Profillink: Das Icon liegt inline im Dokument, beim Seitenaufruf wird nichts
             von Meta geladen. Kein Embed und kein Follow-Button — die würden eine Einwilligung
             nach § 25 TDDDG auslösen und damit ein Cookie-Banner erzwingen. -->
""",
    "en": """        <!-- Plain profile link: the icon is inline in the document, nothing is loaded from Meta
             when the page opens. No embed and no follow button — those would require consent
             under § 25 TDDDG and thus a cookie banner. -->
""",
}

JS = open(os.path.join(HERE, "shell", "site.js"), encoding="utf-8").read()
CF_BEACON = ('<!-- Cloudflare Web Analytics --><script type=\'module\' '
             'src=\'https://static.cloudflareinsights.com/beacon.min.js\' '
             'data-cf-beacon=\'{"token": "7b45f2b83d574c8987ad43343d41f3c4"}\'></script>'
             '<!-- End Cloudflare Web Analytics -->')


# Modul-Glyphen (Inline-SVG, kein externer Request). Aus index.html gezogen, damit
# Handbuchkopf und Modulkachel garantiert dasselbe Symbol zeigen.
GLYPHS = {
    "grades": '<svg viewBox="0 0 24 24"><path d="M9 4H7a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="3.2" rx="1.1"/></svg>',
    "calendar": '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>',
    "planning": '<svg viewBox="0 0 24 24"><path d="M12 6.5c-1.6-1.1-4-1.7-6.5-1.7v13c2.5 0 4.9.6 6.5 1.7"/><path d="M12 6.5c1.6-1.1 4-1.7 6.5-1.7v13c-2.5 0-4.9.6-6.5 1.7"/><path d="M12 6.5v12.3"/></svg>',
    "groups": '<svg viewBox="0 0 24 24"><circle cx="9" cy="8" r="3"/><circle cx="17" cy="10" r="2.4"/><path d="M3 19c0-2.8 2.7-4.5 6-4.5s6 1.7 6 4.5M17 14.6c2.4.3 4 1.9 4 4.4"/></svg>',
    "documentation": '<svg viewBox="0 0 24 24"><path d="M7 3h7l5 5v12a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z"/><path d="M14 3v5h5"/><path d="M9 12.5h6M9 16h6M9 9h3"/></svg>',
    "tasks": '<svg viewBox="0 0 24 24"><rect x="4" y="4" width="7" height="7" rx="1.6"/><rect x="13" y="4" width="7" height="7" rx="1.6"/><rect x="4" y="13" width="7" height="7" rx="1.6"/><rect x="13" y="13" width="7" height="7" rx="1.6"/></svg>',
}

# ---------- Ableitungen aus dem Pfad ----------

def lang_of(path):
    return "en" if path.startswith("en/") else "de"


def base_of(path):
    return path.split("/")[-1]


def prefix_of(path):
    """Pfad-Präfix von dieser Seite zur Wurzel des Repos."""
    return "../" if lang_of(path) == "en" else ""


def twin_of(path):
    """Pfad zur anderssprachigen Fassung, relativ zur übergebenen Seite."""
    twin = TWIN.get(base_of(path), "index.html")
    return ("../" + twin) if lang_of(path) == "en" else ("en/" + twin)


def active_of(path):
    return ACTIVE.get(path)


# ---------- Adressen für Suchmaschinen ----------

def canonical_of(path):
    """Die eine gültige, absolute Adresse dieser Seite.

    Der Webserver liefert dieselbe Startseite unter „/" und unter „/index.html"; intern verlinken
    wir „index.html", von außen zeigt alles auf „/". Ohne canonical muss Google raten, welche der
    beiden zählt, und verteilt die Signale auf zwei Adressen. Wir nennen „/" als die gültige.
    """
    if base_of(path) == "index.html":
        return f"{SITE}/en/" if lang_of(path) == "en" else f"{SITE}/"
    return f"{SITE}/{path}"


def absolute_of(path, href):
    """Macht einen seitenrelativen Verweis absolut — „index.html#module" auf einer Seite in
    /en/ wird zu https://classtiles.de/en/#module."""
    ziel, _, anker = href.partition("#")
    voll = posixpath.normpath(posixpath.join(posixpath.dirname(path), ziel or "."))
    voll = "" if voll == "." else voll
    if posixpath.basename(voll) == "index.html":
        voll = posixpath.dirname(voll)
        voll = (voll + "/") if voll else ""
    url = f"{SITE}/{voll}"
    return f"{url}#{anker}" if anker else url


def twin_page(path):
    """Die anderssprachige Fassung als Pfad im Repo („en/privacy.html" bzw. „datenschutz.html").

    twin_of() liefert denselben Verweis seitenrelativ, für den Gebrauch im Markup.
    """
    twin = TWIN.get(base_of(path), "index.html")
    return twin if lang_of(path) == "en" else "en/" + twin


def is_paired(path):
    """Gibt es diese Seite wirklich in beiden Sprachen — oder nur einen Notausgang?

    TWIN schickt jede nur deutsche Seite (Handbücher, der ganze KI-Bereich) auf eine englische
    Hinweisseite. Als Sprachverweis wäre das falsch: hreflang gilt nur, wenn beide Seiten sich
    gegenseitig benennen, und die eine Hinweisseite kann nicht auf zwölf deutsche zurückzeigen.
    Google verwirft solche Gruppen — schlimmer, es kann die eine echte Zuordnung mitverwerfen.
    Ein Paar zählt deshalb nur, wenn der Verweis hin und zurück wieder hier ankommt.
    """
    return twin_page(twin_page(path)) == path


def breadcrumb_of(path):
    """Navigationspfad dieser Seite als Liste (Beschriftung, absolute URL).

    Die Seite selbst hängt meta_block() an — nur dort ist ihr Titel bekannt. Die Startseiten
    bekommen keinen Pfad; sie sind der Anfang.
    """
    if base_of(path) == "index.html":
        return []
    lang = lang_of(path)
    url = canonical_of(path)
    start = f"{SITE}/en/" if lang == "en" else f"{SITE}/"
    pfad = [(START_LABEL[lang], start)]
    aktiv = active_of(path)
    if aktiv:
        label = next((html.unescape(l) for h, l in NAV[lang] if h == aktiv), None)
        ziel = absolute_of(path, aktiv)
        # Zwei Fälle, in denen der Reiter kein eigener Knoten ist: Er zeigt auf einen Anker der
        # Startseite (Reiter „Module"), oder die Seite IST ihr eigener Bereich — Support,
        # Handbücher, Preise und der KI-Einstieg heben den Reiter hervor, auf dem sie selbst
        # stehen. Ohne diese Prüfung stünde der Name zweimal im Pfad.
        if label and ziel != start and ziel != url:
            pfad.append((label, ziel))
    return pfad


# ---------- Blöcke ----------

def meta_block(path, title, desc, text=""):
    """Alles im Kopf, was Suchmaschinen und Messenger lesen — plus das Seitensymbol.

    `title` und `desc` kommen so herein, wie sie in der Seite stehen (HTML-maskiert); für die
    strukturierten Daten werden sie aufgelöst. `text` ist der Quelltext der Seite und wird nur
    für die Fragen der Support-Seite gebraucht.

    Der Block lädt nichts von fremden Servern. Das Vorschaubild liegt unter assets/ und wird
    beim Seitenaufruf nicht angefordert — nur ein Messenger, in dem jemand den Link teilt,
    holt es sich. Es entsteht also kein Zugriff, dem ein Besucher zustimmen müsste.
    """
    lang = lang_of(path)
    url = canonical_of(path)
    bild = f"{SITE}/{OG_BILD[lang]}"
    zeilen = [f'<link rel="canonical" href="{url}">']

    # hreflang nur für echte Paare, und immer mit Selbstverweis: Google wertet eine Sprachgruppe
    # nur aus, wenn jede Seite darin sich selbst und alle anderen nennt.
    if is_paired(path):
        twin = twin_page(path)
        de, en = (path, twin) if lang == "de" else (twin, path)
        zeilen += [f'<link rel="alternate" hreflang="de" href="{canonical_of(de)}">',
                   f'<link rel="alternate" hreflang="en" href="{canonical_of(en)}">',
                   # Maßgeblich ist die deutsche Fassung — sie bekommt den Vorgabeplatz.
                   f'<link rel="alternate" hreflang="x-default" href="{canonical_of(de)}">']

    alt = html.escape(OG_ALT[lang], quote=True)
    zeilen += [
        f'<meta property="og:type" content="website">',
        f'<meta property="og:site_name" content="ClassTiles">',
        f'<meta property="og:locale" content="{OG_LOCALE[lang]}">',
    ]
    if is_paired(path):
        andere = "en" if lang == "de" else "de"
        zeilen.append(f'<meta property="og:locale:alternate" content="{OG_LOCALE[andere]}">')
    zeilen += [
        f'<meta property="og:title" content="{title}">',
        f'<meta property="og:description" content="{desc}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{bild}">',
        f'<meta property="og:image:width" content="{OG_BILD_GROESSE[0]}">',
        f'<meta property="og:image:height" content="{OG_BILD_GROESSE[1]}">',
        f'<meta property="og:image:alt" content="{alt}">',
        f'<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{title}">',
        f'<meta name="twitter:description" content="{desc}">',
        f'<meta name="twitter:image" content="{bild}">',
    ]

    klartext_titel = html.unescape(title)
    pfad = breadcrumb_of(path)
    if pfad:
        # Die Seite selbst schließt den Pfad ab und trägt keine eigene URL — so will es schema.org.
        pfad = pfad + [(klartext_titel.split(" — ClassTiles")[0], None)]
    zeilen.append(jsonld.block(path, lang, url, klartext_titel, html.unescape(desc),
                               bild, pfad, text))

    zeilen.append(f'<link rel="icon" type="image/png" href="{ICON}">')
    return "\n  ".join(zeilen)


def style_block():
    return "<style>" + CSS + "</style>"


def bar_block(path):
    lang = lang_of(path)
    active = active_of(path)
    tabs = "".join(
        f'<a href="{href}"{" class=\"active\"" if href == active else ""}>{label}</a>'
        for href, label in NAV[lang])
    label, code = LANG_LABEL[lang]
    tabs += (f'<a class="lang" href="{twin_of(path)}" hreflang="{code}" rel="alternate">'
             f'{label}</a>')
    ig = IG_LABEL[lang]
    p = prefix_of(path)
    tabs += (f'<a class="ig" href="{IG_URL}" target="_blank" rel="noopener noreferrer" '
             f'aria-label="{ig}" title="{ig}"><picture>'
             f'<source srcset="{p}assets/instagram-white.svg" media="(prefers-color-scheme: dark)">'
             f'<img src="{p}assets/instagram-black.svg" width="29" height="29" alt="">'
             f'</picture></a>')
    return f'''<div class="bar" id="bar">
    <div class="bar-in">
      <a class="brand" href="index.html">
        <img src="{ICON}" alt="" width="34" height="34">
        <b>ClassTiles</b>
      </a>
      <nav class="tabs">{tabs}</nav>
    </div>
  </div>'''


def footer_block(path):
    lang = lang_of(path)
    t = FOOTER_TEXT[lang]
    mods = "".join(f'<a href="{h}">{l}</a>' for h, l in MODULES[lang])
    manuals = "".join(f'<a href="{h}">{l}</a>' for h, l in MANUALS[lang])
    legal = "".join(f'<a href="{h}">{l}</a>' for h, l in LEGAL[lang])
    return f'''<footer>
    <div class="wrap fcols">
      <div>
        <h4>ClassTiles</h4>
        <p>{t["blurb"]}</p>
{IG_COMMENT[lang]}        <a class="fsocial" href="{IG_URL}" target="_blank" rel="noopener noreferrer"><span>{t["social"]}</span></a>
      </div>
      <div>
        <h4>{t["modules"]}</h4>
        {mods}
      </div>
      <div>
        <h4>{t["manuals"]}</h4>
        {manuals}
      </div>
      <div>
        <h4>{t["legal"]}</h4>
        {legal}
        <a href="mailto:classtiles@icloud.com">classtiles@icloud.com</a>
      </div>
    </div>
    <div class="wrap"><p class="fnote">{t["note"]}</p></div>
  </footer>'''


def script_block():
    return "<script>" + JS + "</script>\n" + CF_BEACON


def page(path, title, desc, body):
    """Vollständige Seite. `body` ist der Inhalt zwischen Kopfleiste und Fußzeile."""
    lang = lang_of(path)
    titel, beschreibung = html.escape(title), html.escape(desc)
    return f'''<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{titel}</title>
  <meta name="description" content="{beschreibung}">
  {meta_block(path, titel, beschreibung, body)}
  {style_block()}
</head>
<body>
  {bar_block(path)}

  <div class="wrap">
{body}
  </div>

  {footer_block(path)}
  {script_block()}
</body>
</html>
'''
