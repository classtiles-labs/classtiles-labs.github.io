"""Strukturierte Daten (JSON-LD) für die Seiten — maschinenlesbare Aussage über das, was
ohnehin auf der Seite steht.

Der Block ist reiner Text im Kopf der Seite: er lädt nichts nach, führt nichts aus und setzt
keine Cookies. Damit bleibt der Grundsatz „kein externer Request" unberührt.

Es wird nichts behauptet, was nicht auf der Seite oder im App Store steht. Insbesondere gibt es
hier **keine** Bewertungen (`aggregateRating`) — die wären erfunden, und erfundene strukturierte
Daten sind ein Verstoß gegen Googles Richtlinien, keine Optimierung.

Aufgebaut wird ein `@graph` pro Seite:

    WebSite ─┬─ WebPage (die aktuelle Seite)
             ├─ Person  (der Anbieter laut Impressum)
             └─ BreadcrumbList (Pfad in der Navigation)

Zwei Seiten bekommen zusätzlich einen Knoten: die Startseiten eine `SoftwareApplication`, die
Support-Seiten eine `FAQPage`, deren Fragen **aus der Seite selbst gelesen** werden. So kann der
Block nicht von der sichtbaren Fassung abweichen.
"""
import html
import json
import re

# Der Anbieter laut Impressum — eine natürliche Person, keine Firma. Die Anschrift steht im
# Impressum und gehört nicht zusätzlich hierher: für die Suche trägt sie nichts bei.
ANBIETER = "Stefan Venekamp"

APP_STORE = "https://apps.apple.com/app/id6760907554"
INSTAGRAM = "https://www.instagram.com/classtiles/"
EMAIL = "classtiles@icloud.com"

# Stand der App-Store-Fassung. Preis 0, weil der Download kostenlos ist; die Vollversion ist ein
# In-App-Kauf und wird nicht als Kaufpreis der App ausgegeben.
APP = {
    "de": dict(
        name="ClassTiles — Notenverwaltung",
        beschreibung="Notenverwaltung für Lehrkräfte mit sechs Modulen auf einer Datenbank: "
                     "Noten, Kalender, Planung, Gruppen und Sitzpläne, Dokumentation, "
                     "Klassengeschäfte. Läuft lokal auf dem Gerät, ohne Nutzerkonto und ohne "
                     "Werbung.",
        kategorie="EducationalApplication"),
    "en": dict(
        name="ClassTiles — Grade Management",
        beschreibung="Grade management for teachers with six modules on one database: grades, "
                     "calendar, planning, groups and seating charts, documentation, class tasks. "
                     "Runs locally on the device, with no user account and no ads.",
        kategorie="EducationalApplication"),
}

BETRIEBSSYSTEME = ["iPadOS 26", "iOS 26", "macOS 26"]

FAQ_SEITEN = ("support.html", "en/support.html")

# <details><summary>Frage</summary><div class="answer">Antwort</div></details>
FAQ_PAAR = re.compile(r'<details>\s*<summary>(.*?)</summary>\s*'
                      r'<div class="answer">(.*?)</div>\s*</details>', re.S)


def _text(roh):
    """Sichtbarer Text eines HTML-Schnipsels — Auszeichnung raus, Entities aufgelöst."""
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', roh))).strip()


def faq_paare(text):
    """Frage-Antwort-Paare einer Support-Seite, gelesen aus deren eigenem Markup."""
    return [(_text(f), _text(a)) for f, a in FAQ_PAAR.findall(text)]


def _website(site, lang):
    return {
        "@type": "WebSite",
        "@id": f"{site}/#website",
        "name": "ClassTiles",
        "url": f"{site}/",
        "inLanguage": lang,
        "publisher": {"@id": f"{site}/#anbieter"},
    }


def _person(site):
    return {
        "@type": "Person",
        "@id": f"{site}/#anbieter",
        "name": ANBIETER,
        "url": f"{site}/impressum.html",
        "email": EMAIL,
        "sameAs": [INSTAGRAM, APP_STORE],
    }


def _breadcrumb(site, url, pfad):
    """`pfad` ist eine Liste (Beschriftung, URL-oder-None); der letzte Eintrag ist diese Seite."""
    eintraege = []
    for i, (label, ziel) in enumerate(pfad, start=1):
        eintrag = {"@type": "ListItem", "position": i, "name": label}
        if ziel:
            eintrag["item"] = ziel
        eintraege.append(eintrag)
    return {"@type": "BreadcrumbList", "@id": f"{url}#breadcrumb", "itemListElement": eintraege}


def _software(site, lang, bild):
    a = APP[lang]
    return {
        "@type": "SoftwareApplication",
        "@id": f"{site}/#app",
        "name": a["name"],
        "description": a["beschreibung"],
        "applicationCategory": a["kategorie"],
        "operatingSystem": ", ".join(BETRIEBSSYSTEME),
        "url": f"{site}/",
        "downloadUrl": APP_STORE,
        "installUrl": APP_STORE,
        "image": bild,
        "author": {"@id": f"{site}/#anbieter"},
        "publisher": {"@id": f"{site}/#anbieter"},
        # Der Download ist kostenlos; die Vollversion ist ein In-App-Kauf.
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR",
                   "availability": "https://schema.org/InStock", "url": APP_STORE},
    }


def _frage(frage, antwort):
    return {"@type": "Question", "name": frage,
            "acceptedAnswer": {"@type": "Answer", "text": antwort}}


def graph(path, lang, url, title, desc, bild, pfad, text):
    """Der vollständige `@graph` einer Seite.

    `url`   kanonische, absolute URL dieser Seite
    `bild`  absolute URL des Vorschaubilds
    `pfad`  Navigationspfad für die Brotkrumen (leer = keine)
    `text`  Quelltext der Seite; nur die Support-Seiten werden daraus gelesen
    """
    site = url.split("/", 3)[0] + "//" + url.split("/", 3)[2]
    seite = {
        "@type": "WebPage",
        "@id": url,
        "url": url,
        "name": title,
        "description": desc,
        "inLanguage": lang,
        "isPartOf": {"@id": f"{site}/#website"},
        "primaryImageOfPage": bild,
    }

    knoten = [_website(site, lang), _person(site), seite]

    if path in FAQ_SEITEN:
        paare = faq_paare(text)
        if paare:
            seite["@type"] = ["WebPage", "FAQPage"]
            seite["mainEntity"] = [_frage(f, a) for f, a in paare]

    if path in ("index.html", "en/index.html"):
        knoten.append(_software(site, lang, bild))

    if pfad:
        knoten.append(_breadcrumb(site, url, pfad))
        seite["breadcrumb"] = {"@id": f"{url}#breadcrumb"}

    return {"@context": "https://schema.org", "@graph": knoten}


def block(path, lang, url, title, desc, bild, pfad, text):
    """Der fertige <script>-Block. `</` wird maskiert, damit er den Kopf nicht vorzeitig schließt."""
    roh = json.dumps(graph(path, lang, url, title, desc, bild, pfad, text),
                     ensure_ascii=False, indent=2)
    return ('<script type="application/ld+json">\n' + roh.replace("</", "<\\/")
            + '\n  </script>')
