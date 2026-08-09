"""Kopfleiste, Fußzeile, CSS und Skripte der Website — an einer Stelle.

Bis Commit b3b72ac9 wurden diese Blöcke von scripts/legal-pages/build.py im App-Repo erzeugt.
Der Generator ist seither nicht mehr die Quelle (App-Store-Badges, Cloudflare, Instagram und
mehrere Rechtstext-Korrekturen existieren nur hier). Gepflegt wird ab jetzt dieses Modul:
es kennt die Shell, kennt aber bewusst keinen Seiteninhalt.
"""
import html
import os

HERE = os.path.dirname(os.path.abspath(__file__))

CSS = open(os.path.join(HERE, "shell", "site.css"), encoding="utf-8").read()
ICON = open(os.path.join(HERE, "shell", "app-icon.datauri.txt"), encoding="utf-8").read().strip()

# ---------- Navigation ----------
# (href, Beschriftung) der Kopfleiste. Heute sind das die vier Rechtstexte — Modul/Support-Tabs
# kommen erst mit Task 5. Der href ist relativ zur jeweiligen Sprachfassung: eine deutsche Seite
# liegt in der Wurzel, eine englische in /en/ — beide verlinken „ihre" Dateien ohne Präfix.
NAV = {
    "de": [("datenschutz.html", "Datenschutz"), ("impressum.html", "Impressum"),
           ("nutzungsbedingungen.html", "Nutzungsbedingungen"), ("support.html", "Support")],
    "en": [("privacy.html", "Privacy"), ("imprint.html", "Legal notice"),
           ("terms.html", "Terms of use"), ("support.html", "Support")],
}

# Welcher Navigationseintrag wird auf welcher Seite hervorgehoben — für die Kopfleiste ab Task 5
# (Modul/Support-Tabs). Bis dahin markiert bar_block() die aktive Seite direkt gegen NAV, ohne
# diese Zuordnung zu benutzen.
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
}
TWIN.update({v: k for k, v in TWIN.items() if k not in ("index.html", "support.html")})

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

FOOTER_TEXT = {
    "de": dict(
        blurb="Notenverwaltung für Lehrkräfte. Läuft lokal auf deinem Gerät — kein Nutzerkonto, "
              "kein Tracking, keine Werbung.",
        social="ClassTiles auf Instagram", modules="Module", legal="Rechtliches",
        note="Diese Seite setzt keine Cookies. Besucherzahlen werden anonym und Cookie-frei mit "
             "Cloudflare Web Analytics gemessen — Details in der Datenschutzerklärung."),
    "en": dict(
        blurb="Grade management for teachers. Runs locally on your device — no user account, "
              "no tracking, no ads.",
        social="ClassTiles on Instagram", modules="Modules", legal="Legal",
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


# ---------- Blöcke ----------

def style_block():
    return "<style>" + CSS + "</style>"


def bar_block(path):
    lang = lang_of(path)
    own = base_of(path)
    tabs = "".join(
        f'<a href="{href}"{" class=\"active\"" if href == own else ""}>{label}</a>'
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
    _, twin_code = LANG_LABEL[lang]
    twin = twin_of(path)
    return f'''<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(desc)}">
  <link rel="alternate" hreflang="{twin_code}" href="{twin}">
  <link rel="icon" type="image/png" href="{ICON}">
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
